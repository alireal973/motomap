"""Long-distance benchmark tool: Istanbul region -> Antalya region.

This script benchmarks up to 10,000 O-D pairs across three routing systems:
- Google Directions API
- Valhalla /route endpoint
- MotoMap (ucret_opsiyonlu_rota_hesapla) on a cached corridor graph

Key properties:
- Resume-friendly via appendable JSONL results
- Deterministic pair generation with seed
- Pair load/save through JSON
- Configurable QPS rate-limits and retries
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

import networkx as nx
import osmnx as ox
import requests
from shapely.geometry import LineString

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError as exc:  # pragma: no cover - runtime dependency guard
    raise SystemExit(
        "Missing dependency: rich. Install with `pip install rich tqdm`."
    ) from exc

try:
    from tqdm import tqdm
except ImportError as exc:  # pragma: no cover - runtime dependency guard
    raise SystemExit(
        "Missing dependency: tqdm. Install with `pip install rich tqdm`."
    ) from exc

# Allow importing from project root when executed from website/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from motomap import GOOGLE_MAPS_API_KEY
from motomap.algorithm import add_travel_time_to_graph, ucret_opsiyonlu_rota_hesapla
from motomap.data_cleaner import clean_graph
from motomap.osm_validator import filter_motorcycle_edges
from motomap.router import NoRouteFoundError

DEFAULT_COUNT = 10_000
DEFAULT_SEED = 42
DEFAULT_VALHALLA_URL = "https://valhalla1.openstreetmap.de"
DEFAULT_GOOGLE_QPS = 8.0
DEFAULT_VALHALLA_QPS = 3.0
DEFAULT_MIN_CROW_M = 350_000.0
DEFAULT_MAX_CROW_M = 900_000.0
CPP_SAMPLER_AUTO_MIN_COUNT = 200_000
CPP_SAMPLER_CALIBRATION_MIN = 1_000
CPP_SAMPLER_CALIBRATION_MAX = 5_000

# Approximate regional bounding boxes.
ISTANBUL_REGION = {
    "north": 41.35,
    "south": 40.80,
    "east": 29.90,
    "west": 28.45,
}
ANTALYA_REGION = {
    "north": 37.20,
    "south": 36.65,
    "east": 31.10,
    "west": 30.20,
}

# Corridor padding around combined Istanbul<->Antalya regional envelope.
CORRIDOR_PAD_LAT = 0.35
CORRIDOR_PAD_LNG = 0.80

# Main-route waypoints (lat, lng) for a narrow long-distance corridor polygon.
MAIN_ROUTE_WAYPOINTS = [
    (41.0082, 28.9784),  # Istanbul
    (40.1950, 29.0600),  # Bursa
    (39.6484, 27.8826),  # Balikesir
    (39.4233, 29.9833),  # Kutahya
    (38.7638, 30.5403),  # Afyon
    (37.8746, 30.8509),  # Burdur
    (36.8969, 30.7133),  # Antalya
]

# Buffer in degrees around the route polyline. Aims to keep graph size tractable.
ROUTE_BUFFER_DEG = 0.22
MAJOR_ROAD_FILTER = (
    '["highway"~"motorway|motorway_link|trunk|trunk_link|primary|primary_link|'
    'secondary|secondary_link|tertiary|tertiary_link"]'
)
FERRY_ROUTE_FILTER = '["route"="ferry"]'

GOOGLE_DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
CPP_SAMPLER_SOURCE = (
    Path(__file__).resolve().parents[1] / "embeddings" / "od_sampler.cpp"
)
CPP_SAMPLER_EXE = Path(__file__).resolve().parents[1] / "embeddings" / "od_sampler.exe"


@dataclass(frozen=True)
class Point:
    lat: float
    lng: float

    def to_json(self) -> dict[str, float]:
        return {"lat": self.lat, "lng": self.lng}


@dataclass(frozen=True)
class ODPair:
    case_id: int
    origin: Point
    destination: Point
    crow_m: float
    origin_node: str | int | None = None
    destination_node: str | int | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "origin": self.origin.to_json(),
            "destination": self.destination.to_json(),
            "crow_m": self.crow_m,
            "origin_node": self.origin_node,
            "destination_node": self.destination_node,
        }

    @property
    def identity(self) -> tuple[float, float, float, float]:
        return (
            round(self.origin.lat, 7),
            round(self.origin.lng, 7),
            round(self.destination.lat, 7),
            round(self.destination.lng, 7),
        )


@dataclass
class QPSLimiter:
    qps: float
    _next_allowed: float = field(default=0.0, init=False)
    _min_interval_s: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        if self.qps <= 0:
            raise ValueError("QPS must be > 0.")
        self._min_interval_s = 1.0 / self.qps

    def wait(self) -> None:
        now = time.monotonic()
        if now < self._next_allowed:
            time.sleep(self._next_allowed - now)
        self._next_allowed = time.monotonic() + self._min_interval_s


class RichHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter
):
    """Keep defaults and multiline help examples."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark long-distance Istanbul->Antalya routes across Google, Valhalla, and MotoMap.",
        formatter_class=RichHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python benchmark_istanbul_antalya_10k.py --count 50 --dry-run\n"
            "  python benchmark_istanbul_antalya_10k.py --count 200 --seed 123\n"
            "  python benchmark_istanbul_antalya_10k.py --disable-google --disable-valhalla"
        ),
    )

    parser.add_argument(
        "--count", type=int, default=DEFAULT_COUNT, help="Number of O-D pairs."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random seed for pair generation.",
    )

    parser.add_argument(
        "--pairs-json",
        default="routes/istanbul_antalya_10k_pairs.json",
        help="Pairs JSON path; loads if exists, otherwise generates and saves.",
    )
    parser.add_argument(
        "--results-jsonl",
        default="routes/istanbul_antalya_10k_results.jsonl",
        help="Appendable case output JSONL file for resume support.",
    )
    parser.add_argument(
        "--summary-json",
        default="routes/istanbul_antalya_10k_summary.json",
        help="Aggregate summary JSON output path.",
    )
    parser.add_argument(
        "--graph-cache",
        default="cache/istanbul_antalya_corridor.graphml",
        help="Cached corridor graph GraphML path.",
    )

    parser.add_argument(
        "--mode",
        choices=["standart", "viraj_keyfi", "guvenli"],
        default="standart",
        help="MotoMap surus_modu.",
    )
    parser.add_argument(
        "--tercih",
        choices=["ucretli_serbest", "ucretsiz"],
        default="ucretli_serbest",
        help="MotoMap toll preference.",
    )
    parser.add_argument(
        "--motor-cc", type=float, help="MotoMap motorcycle displacement."
    )

    parser.add_argument(
        "--google-qps",
        type=float,
        default=DEFAULT_GOOGLE_QPS,
        help="Google request rate limit.",
    )
    parser.add_argument(
        "--valhalla-qps",
        type=float,
        default=DEFAULT_VALHALLA_QPS,
        help="Valhalla request rate limit.",
    )
    parser.add_argument(
        "--valhalla-url", default=DEFAULT_VALHALLA_URL, help="Valhalla base URL."
    )

    parser.add_argument(
        "--min-crow-m",
        type=float,
        default=DEFAULT_MIN_CROW_M,
        help="Minimum crow-fly distance for O-D filtering.",
    )
    parser.add_argument(
        "--max-crow-m",
        type=float,
        default=DEFAULT_MAX_CROW_M,
        help="Maximum crow-fly distance for O-D filtering.",
    )

    parser.add_argument(
        "--disable-google", action="store_true", help="Disable Google backend."
    )
    parser.add_argument(
        "--disable-valhalla", action="store_true", help="Disable Valhalla backend."
    )
    parser.add_argument(
        "--disable-motomap", action="store_true", help="Disable MotoMap backend."
    )
    parser.add_argument(
        "--disable-cpp-sampler",
        action="store_true",
        help="Disable C++ O-D pair sampler and use pure Python sampling.",
    )
    parser.add_argument(
        "--force-cpp-sampler",
        action="store_true",
        help="Force C++ O-D sampler even when auto mode would prefer Python.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare graph/pairs/resume state; skip API calls.",
    )

    args = parser.parse_args()
    if args.count <= 0:
        raise SystemExit("--count must be > 0.")
    if args.min_crow_m <= 0 or args.max_crow_m <= 0:
        raise SystemExit("--min-crow-m and --max-crow-m must be > 0.")
    if args.min_crow_m >= args.max_crow_m:
        raise SystemExit("--min-crow-m must be smaller than --max-crow-m.")
    if not args.disable_google and args.google_qps <= 0:
        raise SystemExit("--google-qps must be > 0 when Google backend is enabled.")
    if not args.disable_valhalla and args.valhalla_qps <= 0:
        raise SystemExit("--valhalla-qps must be > 0 when Valhalla backend is enabled.")
    if args.disable_google and args.disable_valhalla and args.disable_motomap:
        raise SystemExit("At least one backend must remain enabled.")
    if args.disable_cpp_sampler and args.force_cpp_sampler:
        raise SystemExit(
            "--disable-cpp-sampler and --force-cpp-sampler cannot be used together."
        )
    return args


def resolve_path(raw: str, script_dir: Path) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return script_dir / path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius_m = 6_371_000.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    return 2 * radius_m * math.asin(math.sqrt(a))


def ratio(
    numerator: float | int | None, denominator: float | int | None
) -> float | None:
    if numerator is None or denominator is None:
        return None
    denom = float(denominator)
    if denom <= 0:
        return None
    return float(numerator) / denom


def ape_pct(value: float | int | None, baseline: float | int | None) -> float | None:
    if value is None or baseline is None:
        return None
    base = float(baseline)
    if base <= 0:
        return None
    return abs(float(value) - base) * 100.0 / base


def corridor_bbox() -> tuple[float, float, float, float]:
    north = max(ISTANBUL_REGION["north"], ANTALYA_REGION["north"]) + CORRIDOR_PAD_LAT
    south = min(ISTANBUL_REGION["south"], ANTALYA_REGION["south"]) - CORRIDOR_PAD_LAT
    east = max(ISTANBUL_REGION["east"], ANTALYA_REGION["east"]) + CORRIDOR_PAD_LNG
    west = min(ISTANBUL_REGION["west"], ANTALYA_REGION["west"]) - CORRIDOR_PAD_LNG
    return north, south, east, west


def corridor_polygon():
    route_xy = [(lng, lat) for lat, lng in MAIN_ROUTE_WAYPOINTS]
    line = LineString(route_xy)
    # Expand corridor around long-distance route.
    return line.buffer(ROUTE_BUFFER_DEG, cap_style=1, join_style=1)


def corridor_chunk_bboxes() -> list[tuple[float, float, float, float]]:
    boxes: list[tuple[float, float, float, float]] = []
    points = list(MAIN_ROUTE_WAYPOINTS)
    for idx in range(len(MAIN_ROUTE_WAYPOINTS) - 1):
        lat1, lng1 = MAIN_ROUTE_WAYPOINTS[idx]
        lat2, lng2 = MAIN_ROUTE_WAYPOINTS[idx + 1]
        points.append(((lat1 + lat2) / 2.0, (lng1 + lng2) / 2.0))

    seen = set()
    for lat, lng in points:
        north = lat + ROUTE_BUFFER_DEG
        south = lat - ROUTE_BUFFER_DEG
        east = lng + ROUTE_BUFFER_DEG
        west = lng - ROUTE_BUFFER_DEG
        key = (round(north, 4), round(south, 4), round(east, 4), round(west, 4))
        if key in seen:
            continue
        seen.add(key)
        boxes.append((north, south, east, west))
    return boxes


def corridor_download_filter() -> list[str]:
    return [MAJOR_ROAD_FILTER, FERRY_ROUTE_FILTER]


def keep_largest_weak_component(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    if graph.number_of_nodes() == 0:
        return graph
    components = nx.weakly_connected_components(graph)
    largest_nodes = max(components, key=len)
    return graph.subgraph(largest_nodes).copy()


def prepare_corridor_graph(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    graph = filter_motorcycle_edges(graph)
    graph = keep_largest_weak_component(graph)
    graph = clean_graph(graph)
    graph = add_travel_time_to_graph(graph)
    graph.graph["motomap_corridor_prepared"] = "1"
    graph.graph["prepared_at_utc"] = utc_now_iso()
    return graph


def load_or_build_corridor_graph(
    graph_cache: Path, console: Console
) -> nx.MultiDiGraph:
    if graph_cache.exists():
        console.print(f"[cyan]Loading graph cache:[/cyan] {graph_cache}")
        graph = ox.load_graphml(graph_cache)
        if str(graph.graph.get("motomap_corridor_prepared", "")) == "1":
            return graph
        console.print(
            "[yellow]Cached graph found but not prepared; running prepare pipeline.[/yellow]"
        )
        graph = prepare_corridor_graph(graph)
        ox.save_graphml(graph, graph_cache)
        return graph

    graph_cache.parent.mkdir(parents=True, exist_ok=True)
    graph = None
    chunk_graphs: list[nx.MultiDiGraph] = []
    boxes = corridor_chunk_bboxes()
    console.print(
        f"[cyan]Building corridor graph from {len(boxes)} chunked bbox queries...[/cyan]"
    )

    for idx, (north, south, east, west) in enumerate(boxes, start=1):
        try:
            console.print(
                f"[cyan]Chunk {idx}/{len(boxes)}[/cyan] "
                f"(N={north:.3f}, S={south:.3f}, E={east:.3f}, W={west:.3f})"
            )
            g = ox.graph_from_bbox(
                (north, south, east, west),
                network_type="all",
                custom_filter=corridor_download_filter(),
                simplify=True,
                retain_all=True,
                truncate_by_edge=True,
            )
            if g.number_of_nodes() > 0 and g.number_of_edges() > 0:
                chunk_graphs.append(g)
        except Exception as exc:
            console.print(f"[yellow]Chunk {idx} failed:[/yellow] {exc}")

    if chunk_graphs:
        graph = chunk_graphs[0]
        for g in chunk_graphs[1:]:
            graph = nx.compose(graph, g)
    else:
        # Last-resort fallback.
        north, south, east, west = corridor_bbox()
        console.print(
            "[yellow]Chunked download failed, falling back to single bbox query.[/yellow]"
        )
        graph = ox.graph_from_bbox(
            (north, south, east, west),
            network_type="all",
            custom_filter=corridor_download_filter(),
            simplify=True,
            retain_all=True,
            truncate_by_edge=True,
        )

    graph = prepare_corridor_graph(graph)
    ox.save_graphml(graph, graph_cache)
    console.print(f"[green]Saved graph cache:[/green] {graph_cache}")
    return graph


def _node_inside_region(lat: float, lng: float, region: dict[str, float]) -> bool:
    return (
        region["south"] <= lat <= region["north"]
        and region["west"] <= lng <= region["east"]
    )


def collect_region_nodes(
    graph: nx.MultiDiGraph,
    region: dict[str, float],
) -> list[tuple[str | int, float, float]]:
    nodes: list[tuple[str | int, float, float]] = []
    for node_id, data in graph.nodes(data=True):
        lat = float(data.get("y"))
        lng = float(data.get("x"))
        if _node_inside_region(lat, lng, region):
            nodes.append((node_id, lat, lng))
    return nodes


def _should_compile_cpp_sampler() -> bool:
    if not CPP_SAMPLER_EXE.exists():
        return True
    if not CPP_SAMPLER_SOURCE.exists():
        return False
    return CPP_SAMPLER_SOURCE.stat().st_mtime > CPP_SAMPLER_EXE.stat().st_mtime


def _cpp_toolchain_env() -> dict[str, str] | None:
    """Prefer g++'s own MinGW bin first to avoid Conda DLL conflicts on Windows."""
    compiler = shutil.which("g++")
    if not compiler:
        return None
    compiler_dir = str(Path(compiler).resolve().parent)
    env = os.environ.copy()
    current_path = env.get("PATH", "")
    env["PATH"] = (
        f"{compiler_dir}{os.pathsep}{current_path}" if current_path else compiler_dir
    )
    return env


def ensure_cpp_sampler(console: Console) -> bool:
    if not CPP_SAMPLER_SOURCE.exists():
        console.print(
            f"[yellow]C++ sampler source not found:[/yellow] {CPP_SAMPLER_SOURCE}"
        )
        return False

    if not _should_compile_cpp_sampler():
        return True

    CPP_SAMPLER_EXE.parent.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which("g++") or "g++"
    compile_cmd = [
        compiler,
        "-O3",
        "-std=c++17",
        str(CPP_SAMPLER_SOURCE),
        "-o",
        str(CPP_SAMPLER_EXE),
    ]
    try:
        completed = subprocess.run(
            compile_cmd,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
            env=_cpp_toolchain_env(),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        console.print(f"[yellow]C++ sampler compile failed:[/yellow] {exc}")
        return False

    if completed.returncode != 0:
        console.print(
            "[yellow]C++ sampler compile error, using Python fallback.[/yellow]"
        )
        diagnostics = (completed.stderr or "").strip() or (
            completed.stdout or ""
        ).strip()
        if diagnostics:
            console.print(diagnostics)
        else:
            console.print(
                "[yellow]Compiler returned non-zero without diagnostics. "
                "Verify local C++ toolchain (g++/MinGW) installation.[/yellow]"
            )
        return False
    return CPP_SAMPLER_EXE.exists()


def _write_nodes_csv(path: Path, nodes: list[tuple[str | int, float, float]]) -> None:
    with path.open("w", encoding="utf-8") as file:
        for node_id, lat, lng in nodes:
            file.write(f"{node_id},{lat:.8f},{lng:.8f}\n")


def sample_pairs_cpp(
    graph: nx.MultiDiGraph,
    count: int,
    seed: int,
    min_crow_m: float,
    max_crow_m: float,
    console: Console,
) -> list[ODPair] | None:
    if not ensure_cpp_sampler(console):
        return None

    ist_nodes = collect_region_nodes(graph, ISTANBUL_REGION)
    ant_nodes = collect_region_nodes(graph, ANTALYA_REGION)
    if not ist_nodes or not ant_nodes:
        return None

    with tempfile.TemporaryDirectory(prefix="motomap_cpp_sampler_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        ist_path = tmp_path / "ist.csv"
        ant_path = tmp_path / "ant.csv"
        out_path = tmp_path / "pairs.csv"
        _write_nodes_csv(ist_path, ist_nodes)
        _write_nodes_csv(ant_path, ant_nodes)

        cmd = [
            str(CPP_SAMPLER_EXE),
            "--ist",
            str(ist_path),
            "--ant",
            str(ant_path),
            "--count",
            str(count),
            "--seed",
            str(seed),
            "--min-crow-m",
            str(min_crow_m),
            "--max-crow-m",
            str(max_crow_m),
            "--out",
            str(out_path),
        ]
        try:
            completed = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                timeout=180,
                env=_cpp_toolchain_env(),
            )
        except (OSError, subprocess.SubprocessError) as exc:
            console.print(f"[yellow]C++ sampler execution failed:[/yellow] {exc}")
            return None

        if completed.returncode != 0 or not out_path.exists():
            console.print(
                "[yellow]C++ sampler returned error, using Python sampler.[/yellow]"
            )
            if completed.stderr:
                console.print(completed.stderr.strip())
            return None

        pairs: list[ODPair] = []
        with out_path.open("r", encoding="utf-8") as file:
            for line in file:
                stripped = line.strip()
                if not stripped:
                    continue
                parts = stripped.split(",")
                if len(parts) != 8:
                    continue
                case_id = int(parts[0])
                origin_node = parts[1]
                destination_node = parts[2]
                o_lat = float(parts[3])
                o_lng = float(parts[4])
                d_lat = float(parts[5])
                d_lng = float(parts[6])
                crow_m = float(parts[7])
                pairs.append(
                    ODPair(
                        case_id=case_id,
                        origin=Point(lat=o_lat, lng=o_lng),
                        destination=Point(lat=d_lat, lng=d_lng),
                        crow_m=crow_m,
                        origin_node=origin_node,
                        destination_node=destination_node,
                    )
                )
        if len(pairs) != count:
            return None
        return pairs


def sample_pairs(
    graph: nx.MultiDiGraph,
    count: int,
    seed: int,
    min_crow_m: float,
    max_crow_m: float,
    existing: list[ODPair] | None = None,
) -> list[ODPair]:
    rng = random.Random(seed)
    existing_pairs = list(existing or [])
    seen_identities = {pair.identity for pair in existing_pairs}
    seen_nodes = {
        (str(pair.origin_node), str(pair.destination_node))
        for pair in existing_pairs
        if pair.origin_node is not None and pair.destination_node is not None
    }

    ist_nodes = collect_region_nodes(graph, ISTANBUL_REGION)
    ant_nodes = collect_region_nodes(graph, ANTALYA_REGION)
    if not ist_nodes:
        raise ValueError("No Istanbul-region nodes found in corridor graph.")
    if not ant_nodes:
        raise ValueError("No Antalya-region nodes found in corridor graph.")

    pairs = existing_pairs[:]
    max_attempts = max(20_000, count * 100)
    attempts = 0
    while len(pairs) < count and attempts < max_attempts:
        attempts += 1
        origin_node, o_lat, o_lng = rng.choice(ist_nodes)
        dest_node, d_lat, d_lng = rng.choice(ant_nodes)
        node_key = (str(origin_node), str(dest_node))
        if node_key in seen_nodes:
            continue
        crow_m = haversine_m(o_lat, o_lng, d_lat, d_lng)
        if crow_m < min_crow_m or crow_m > max_crow_m:
            continue
        pair = ODPair(
            case_id=len(pairs) + 1,
            origin=Point(lat=o_lat, lng=o_lng),
            destination=Point(lat=d_lat, lng=d_lng),
            crow_m=crow_m,
            origin_node=origin_node,
            destination_node=dest_node,
        )
        if pair.identity in seen_identities:
            continue
        pairs.append(pair)
        seen_nodes.add(node_key)
        seen_identities.add(pair.identity)

    if len(pairs) < count:
        raise ValueError(
            f"Could not generate requested pairs. Requested={count}, generated={len(pairs)}, "
            f"attempts={attempts}, ist_nodes={len(ist_nodes)}, ant_nodes={len(ant_nodes)}"
        )
    return pairs[:count]


def parse_point(data: dict[str, Any], key_prefix: str) -> Point:
    if not isinstance(data, dict):
        raise ValueError(f"{key_prefix} must be an object.")
    try:
        lat = float(data["lat"])
        lng = float(data["lng"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{key_prefix} must include numeric lat/lng.") from exc
    return Point(lat=lat, lng=lng)


def load_pairs_json(path: Path) -> list[ODPair]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    rows: Any
    if isinstance(raw, dict) and isinstance(raw.get("pairs"), list):
        rows = raw["pairs"]
    elif isinstance(raw, list):
        rows = raw
    else:
        raise ValueError("Pairs JSON must be a list or {'pairs': [...]} object.")

    pairs: list[ODPair] = []
    for idx, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"Pair row at index {idx} must be object.")
        case_id = int(row.get("case_id", idx))
        origin = parse_point(row.get("origin", {}), key_prefix=f"pairs[{idx}].origin")
        destination = parse_point(
            row.get("destination", {}), key_prefix=f"pairs[{idx}].destination"
        )
        crow_m = float(
            row.get(
                "crow_m",
                haversine_m(origin.lat, origin.lng, destination.lat, destination.lng),
            )
        )
        pairs.append(
            ODPair(
                case_id=case_id,
                origin=origin,
                destination=destination,
                crow_m=crow_m,
                origin_node=row.get("origin_node"),
                destination_node=row.get("destination_node"),
            )
        )

    pairs.sort(key=lambda pair: pair.case_id)
    reindexed: list[ODPair] = []
    for idx, pair in enumerate(pairs, start=1):
        reindexed.append(
            ODPair(
                case_id=idx,
                origin=pair.origin,
                destination=pair.destination,
                crow_m=pair.crow_m,
                origin_node=pair.origin_node,
                destination_node=pair.destination_node,
            )
        )
    return reindexed


def save_pairs_json(
    path: Path,
    pairs: list[ODPair],
    seed: int,
    min_crow_m: float,
    max_crow_m: float,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": utc_now_iso(),
        "seed": seed,
        "count": len(pairs),
        "regions": {"origin": "istanbul", "destination": "antalya"},
        "min_crow_m": min_crow_m,
        "max_crow_m": max_crow_m,
        "pairs": [pair.to_json() for pair in pairs],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def filter_pairs_by_crow(
    pairs: list[ODPair],
    min_crow_m: float,
    max_crow_m: float,
) -> tuple[list[ODPair], int]:
    filtered = [pair for pair in pairs if min_crow_m <= pair.crow_m <= max_crow_m]
    dropped = len(pairs) - len(filtered)
    reindexed: list[ODPair] = []
    for idx, pair in enumerate(filtered, start=1):
        reindexed.append(
            ODPair(
                case_id=idx,
                origin=pair.origin,
                destination=pair.destination,
                crow_m=pair.crow_m,
                origin_node=pair.origin_node,
                destination_node=pair.destination_node,
            )
        )
    return reindexed, dropped


def load_or_generate_pairs(
    graph: nx.MultiDiGraph,
    pairs_json: Path,
    count: int,
    seed: int,
    min_crow_m: float,
    max_crow_m: float,
    use_cpp_sampler: bool,
    force_cpp_sampler: bool,
    console: Console,
) -> list[ODPair]:
    if pairs_json.exists():
        console.print(f"[cyan]Loading pairs:[/cyan] {pairs_json}")
        loaded = load_pairs_json(pairs_json)
        loaded, dropped = filter_pairs_by_crow(
            loaded, min_crow_m=min_crow_m, max_crow_m=max_crow_m
        )
        if dropped:
            console.print(
                f"[yellow]Dropped {dropped} pair(s) outside crow distance filter; regenerating as needed.[/yellow]"
            )
        pairs = loaded[:count]
        if len(pairs) < count:
            pairs = sample_pairs(
                graph,
                count=count,
                seed=seed,
                min_crow_m=min_crow_m,
                max_crow_m=max_crow_m,
                existing=loaded[:count],
            )
        if len(loaded) != len(pairs):
            save_pairs_json(
                pairs_json,
                pairs,
                seed=seed,
                min_crow_m=min_crow_m,
                max_crow_m=max_crow_m,
            )
        return pairs

    console.print(f"[cyan]Generating new pairs:[/cyan] {pairs_json}")
    pairs = None
    skip_cpp_reason = ""
    should_try_cpp = use_cpp_sampler and (
        force_cpp_sampler or count >= CPP_SAMPLER_AUTO_MIN_COUNT
    )
    if use_cpp_sampler and not force_cpp_sampler and count < CPP_SAMPLER_AUTO_MIN_COUNT:
        skip_cpp_reason = "batch size below auto C++ threshold"

    if should_try_cpp and not force_cpp_sampler:
        # Measure quickly on a small sample and pick the faster sampler on this machine.
        calibration_count = min(
            CPP_SAMPLER_CALIBRATION_MAX, max(CPP_SAMPLER_CALIBRATION_MIN, count // 100)
        )
        calibration_count = min(calibration_count, count)
        py_time_s = None
        cpp_time_s = None

        py_start = time.perf_counter()
        _ = sample_pairs(
            graph,
            count=calibration_count,
            seed=seed,
            min_crow_m=min_crow_m,
            max_crow_m=max_crow_m,
            existing=None,
        )
        py_time_s = time.perf_counter() - py_start

        cpp_start = time.perf_counter()
        cpp_probe = sample_pairs_cpp(
            graph=graph,
            count=calibration_count,
            seed=seed,
            min_crow_m=min_crow_m,
            max_crow_m=max_crow_m,
            console=console,
        )
        cpp_time_s = time.perf_counter() - cpp_start

        if cpp_probe is None:
            should_try_cpp = False
            skip_cpp_reason = "C++ probe failed"
            console.print(
                "[yellow]Auto sampler:[/yellow] C++ probe failed, Python sampler selected."
            )
        else:
            should_try_cpp = cpp_time_s < py_time_s
            if not should_try_cpp:
                skip_cpp_reason = "Python probe faster on this machine"
            winner = "C++" if should_try_cpp else "Python"
            console.print(
                "[cyan]Auto sampler benchmark:[/cyan] "
                f"python={py_time_s:.4f}s, cpp={cpp_time_s:.4f}s, selected={winner}"
            )

    if use_cpp_sampler and not should_try_cpp:
        console.print(
            f"[cyan]Auto sampler:[/cyan] using Python sampler ({skip_cpp_reason or 'auto selection'}). "
            "Use --force-cpp-sampler to override."
        )

    if should_try_cpp:
        pairs = sample_pairs_cpp(
            graph=graph,
            count=count,
            seed=seed,
            min_crow_m=min_crow_m,
            max_crow_m=max_crow_m,
            console=console,
        )
        if pairs is not None:
            console.print("[green]C++ sampler used for O-D generation.[/green]")
    if pairs is None:
        pairs = sample_pairs(
            graph,
            count=count,
            seed=seed,
            min_crow_m=min_crow_m,
            max_crow_m=max_crow_m,
            existing=None,
        )
        if use_cpp_sampler:
            console.print("[yellow]Python sampler fallback used.[/yellow]")

    save_pairs_json(
        pairs_json,
        pairs,
        seed=seed,
        min_crow_m=min_crow_m,
        max_crow_m=max_crow_m,
    )
    return pairs


def load_existing_results(results_jsonl: Path) -> tuple[dict[int, dict[str, Any]], int]:
    if not results_jsonl.exists():
        return {}, 0
    case_results: dict[int, dict[str, Any]] = {}
    malformed = 0
    with results_jsonl.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                row = json.loads(stripped)
            except json.JSONDecodeError:
                malformed += 1
                continue
            case_id = row.get("case_id")
            if isinstance(case_id, int):
                case_results[case_id] = row
    return case_results, malformed


def make_backend_result(
    enabled: bool,
    success: bool,
    status: str,
    distance_m: float | None = None,
    duration_s: float | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "enabled": enabled,
        "success": success,
        "status": status,
        "distance_m": distance_m,
        "duration_s": duration_s,
        "error": error,
    }


def fetch_google_directions(
    session: requests.Session,
    limiter: QPSLimiter,
    origin: Point,
    destination: Point,
    api_key: str,
    max_retries: int = 4,
) -> dict[str, Any]:
    params = {
        "origin": f"{origin.lat},{origin.lng}",
        "destination": f"{destination.lat},{destination.lng}",
        "mode": "driving",
        "key": api_key,
    }
    retryable_statuses = {"UNKNOWN_ERROR", "OVER_QUERY_LIMIT"}

    for attempt in range(max_retries):
        limiter.wait()
        try:
            response = session.get(GOOGLE_DIRECTIONS_URL, params=params, timeout=30)
        except requests.RequestException as exc:
            if attempt == max_retries - 1:
                return make_backend_result(
                    enabled=True,
                    success=False,
                    status="REQUEST_ERROR",
                    error=str(exc),
                )
            time.sleep(min(8.0, 0.8 * (2**attempt)))
            continue

        if response.status_code == 429 or 500 <= response.status_code < 600:
            if attempt == max_retries - 1:
                return make_backend_result(
                    enabled=True,
                    success=False,
                    status=f"HTTP_{response.status_code}",
                )
            time.sleep(min(10.0, 1.0 * (attempt + 1)))
            continue

        if response.status_code >= 400:
            return make_backend_result(
                enabled=True, success=False, status=f"HTTP_{response.status_code}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            if attempt == max_retries - 1:
                return make_backend_result(
                    enabled=True,
                    success=False,
                    status="MALFORMED_RESPONSE",
                    error=str(exc),
                )
            time.sleep(0.8)
            continue

        status = str(data.get("status", "UNKNOWN"))
        if status == "OK":
            routes = data.get("routes") or []
            if not routes:
                return make_backend_result(
                    enabled=True, success=False, status="EMPTY_ROUTES"
                )
            legs = routes[0].get("legs") or []
            if not legs:
                return make_backend_result(
                    enabled=True, success=False, status="EMPTY_LEGS"
                )
            leg = legs[0]
            try:
                distance_m = float((leg.get("distance") or {}).get("value"))
                duration_s = float((leg.get("duration") or {}).get("value"))
            except (TypeError, ValueError):
                return make_backend_result(
                    enabled=True,
                    success=False,
                    status="MISSING_LEG_VALUES",
                )
            return make_backend_result(
                enabled=True,
                success=True,
                status="OK",
                distance_m=distance_m,
                duration_s=duration_s,
            )

        if status in retryable_statuses and attempt < max_retries - 1:
            time.sleep(min(10.0, 1.2 * (attempt + 1)))
            continue

        return make_backend_result(enabled=True, success=False, status=status)

    return make_backend_result(
        enabled=True, success=False, status="MAX_RETRIES_EXCEEDED"
    )


def fetch_valhalla_route(
    session: requests.Session,
    limiter: QPSLimiter,
    origin: Point,
    destination: Point,
    valhalla_url: str,
    max_retries: int = 4,
) -> dict[str, Any]:
    payload = {
        "locations": [
            {"lat": origin.lat, "lon": origin.lng},
            {"lat": destination.lat, "lon": destination.lng},
        ],
        "costing": "auto",
        "directions_options": {"units": "kilometers"},
    }
    endpoint = f"{valhalla_url.rstrip('/')}/route"

    for attempt in range(max_retries):
        limiter.wait()
        try:
            response = session.post(endpoint, json=payload, timeout=30)
        except requests.RequestException as exc:
            if attempt == max_retries - 1:
                return make_backend_result(
                    enabled=True,
                    success=False,
                    status="REQUEST_ERROR",
                    error=str(exc),
                )
            time.sleep(min(8.0, 0.8 * (2**attempt)))
            continue

        if response.status_code == 429 or 500 <= response.status_code < 600:
            if attempt == max_retries - 1:
                return make_backend_result(
                    enabled=True, success=False, status=f"HTTP_{response.status_code}"
                )
            time.sleep(min(10.0, 1.0 * (attempt + 1)))
            continue
        if response.status_code >= 400:
            return make_backend_result(
                enabled=True, success=False, status=f"HTTP_{response.status_code}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            if attempt == max_retries - 1:
                return make_backend_result(
                    enabled=True,
                    success=False,
                    status="MALFORMED_RESPONSE",
                    error=str(exc),
                )
            time.sleep(0.8)
            continue

        trip = data.get("trip")
        if not isinstance(trip, dict):
            return make_backend_result(
                enabled=True,
                success=False,
                status=str(data.get("error", data.get("status_message", "NO_TRIP"))),
            )
        if int(trip.get("status", 1)) != 0:
            return make_backend_result(
                enabled=True,
                success=False,
                status=str(trip.get("status_message", "VALHALLA_ERROR")),
            )

        summary = trip.get("summary") or {}
        length_km = summary.get("length")
        duration_s = summary.get("time")
        try:
            distance_m = float(length_km) * 1000.0
            eta_s = float(duration_s)
        except (TypeError, ValueError):
            return make_backend_result(
                enabled=True, success=False, status="MISSING_SUMMARY"
            )
        return make_backend_result(
            enabled=True,
            success=True,
            status="OK",
            distance_m=distance_m,
            duration_s=eta_s,
        )

    return make_backend_result(
        enabled=True, success=False, status="MAX_RETRIES_EXCEEDED"
    )


def run_motomap_route(
    graph: nx.MultiDiGraph,
    pair: ODPair,
    mode: str,
    tercih: str,
    motor_cc: float | None,
) -> dict[str, Any]:
    try:
        origin_node = pair.origin_node
        destination_node = pair.destination_node
        if origin_node is None:
            origin_node = ox.nearest_nodes(graph, pair.origin.lng, pair.origin.lat)
        if destination_node is None:
            destination_node = ox.nearest_nodes(
                graph, pair.destination.lng, pair.destination.lat
            )
        if origin_node == destination_node:
            return make_backend_result(
                enabled=True,
                success=False,
                status="SAME_NODE",
            )

        route = ucret_opsiyonlu_rota_hesapla(
            graph,
            source=origin_node,
            target=destination_node,
            tercih=tercih,
            surus_modu=mode,
            motor_cc=motor_cc,
        )
        selected = route["secilen_rota"]
        return make_backend_result(
            enabled=True,
            success=True,
            status="OK",
            distance_m=float(selected.get("toplam_mesafe_m")),
            duration_s=float(selected.get("toplam_sure_s")),
        )
    except NoRouteFoundError as exc:
        return make_backend_result(
            enabled=True, success=False, status="NO_ROUTE", error=str(exc)
        )
    except Exception as exc:  # pragma: no cover - defensive runtime reporting
        return make_backend_result(
            enabled=True, success=False, status="MOTOMAP_ERROR", error=str(exc)
        )


def evaluate_case(
    graph: nx.MultiDiGraph,
    pair: ODPair,
    enable_google: bool,
    enable_valhalla: bool,
    enable_motomap: bool,
    google_session: requests.Session,
    valhalla_session: requests.Session,
    google_limiter: QPSLimiter | None,
    valhalla_limiter: QPSLimiter | None,
    google_api_key: str | None,
    valhalla_url: str,
    mode: str,
    tercih: str,
    motor_cc: float | None,
) -> dict[str, Any]:
    google_result = make_backend_result(enabled=False, success=False, status="DISABLED")
    valhalla_result = make_backend_result(
        enabled=False, success=False, status="DISABLED"
    )
    motomap_result = make_backend_result(
        enabled=False, success=False, status="DISABLED"
    )

    if enable_google:
        if not google_api_key:
            google_result = make_backend_result(
                enabled=True,
                success=False,
                status="MISSING_API_KEY",
            )
        elif google_limiter is None:
            google_result = make_backend_result(
                enabled=True,
                success=False,
                status="RATE_LIMITER_MISSING",
            )
        else:
            google_result = fetch_google_directions(
                session=google_session,
                limiter=google_limiter,
                origin=pair.origin,
                destination=pair.destination,
                api_key=google_api_key,
            )

    if enable_valhalla:
        if valhalla_limiter is None:
            valhalla_result = make_backend_result(
                enabled=True,
                success=False,
                status="RATE_LIMITER_MISSING",
            )
        else:
            valhalla_result = fetch_valhalla_route(
                session=valhalla_session,
                limiter=valhalla_limiter,
                origin=pair.origin,
                destination=pair.destination,
                valhalla_url=valhalla_url,
            )

    if enable_motomap:
        motomap_result = run_motomap_route(
            graph=graph,
            pair=pair,
            mode=mode,
            tercih=tercih,
            motor_cc=motor_cc,
        )

    g_dist = google_result.get("distance_m")
    g_time = google_result.get("duration_s")
    m_dist = motomap_result.get("distance_m")
    m_time = motomap_result.get("duration_s")
    v_dist = valhalla_result.get("distance_m")
    v_time = valhalla_result.get("duration_s")

    motomap_vs_google = {
        "distance_ratio": ratio(m_dist, g_dist),
        "duration_ratio": ratio(m_time, g_time),
        "distance_ape_pct": ape_pct(m_dist, g_dist),
        "duration_ape_pct": ape_pct(m_time, g_time),
    }
    valhalla_vs_google = {
        "distance_ratio": ratio(v_dist, g_dist),
        "duration_ratio": ratio(v_time, g_time),
        "distance_ape_pct": ape_pct(v_dist, g_dist),
        "duration_ape_pct": ape_pct(v_time, g_time),
    }

    return {
        "timestamp_utc": utc_now_iso(),
        "case_id": pair.case_id,
        "origin": pair.origin.to_json(),
        "destination": pair.destination.to_json(),
        "crow_m": pair.crow_m,
        "settings": {
            "mode": mode,
            "tercih": tercih,
            "motor_cc": motor_cc,
        },
        "google": google_result,
        "valhalla": valhalla_result,
        "motomap": motomap_result,
        "comparisons": {
            "motomap_vs_google": motomap_vs_google,
            "valhalla_vs_google": valhalla_vs_google,
        },
    }


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    rank = (len(ordered) - 1) * pct
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    weight = rank - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def summarize_comparator(
    results: list[dict[str, Any]], comparator_key: str
) -> dict[str, Any]:
    ratio_dist_values: list[float] = []
    ratio_time_values: list[float] = []
    ape_dist_values: list[float] = []
    ape_time_values: list[float] = []

    for row in results:
        comparisons = row.get("comparisons", {})
        comp = comparisons.get(comparator_key, {})
        dist_ratio = comp.get("distance_ratio")
        time_ratio = comp.get("duration_ratio")
        dist_ape = comp.get("distance_ape_pct")
        time_ape = comp.get("duration_ape_pct")
        if isinstance(dist_ratio, (int, float)):
            ratio_dist_values.append(float(dist_ratio))
        if isinstance(time_ratio, (int, float)):
            ratio_time_values.append(float(time_ratio))
        if isinstance(dist_ape, (int, float)):
            ape_dist_values.append(float(dist_ape))
        if isinstance(time_ape, (int, float)):
            ape_time_values.append(float(time_ape))

    def stats(values: list[float]) -> dict[str, float | int | None]:
        if not values:
            return {
                "count": 0,
                "mean": None,
                "median": None,
                "p95": None,
                "min": None,
                "max": None,
            }
        return {
            "count": len(values),
            "mean": mean(values),
            "median": median(values),
            "p95": percentile(values, 0.95),
            "min": min(values),
            "max": max(values),
        }

    return {
        "distance_ratio": stats(ratio_dist_values),
        "duration_ratio": stats(ratio_time_values),
        "distance_ape_pct": stats(ape_dist_values),
        "duration_ape_pct": stats(ape_time_values),
    }


def summarize_backend_counts(
    results: list[dict[str, Any]], backend_key: str
) -> dict[str, int | float | None]:
    enabled = 0
    success = 0
    failure = 0
    skipped = 0
    for row in results:
        backend = row.get(backend_key, {})
        if not backend.get("enabled"):
            skipped += 1
            continue
        enabled += 1
        if backend.get("success"):
            success += 1
        else:
            failure += 1
    success_rate = (success / enabled) if enabled > 0 else None
    return {
        "enabled_cases": enabled,
        "success": success,
        "failure": failure,
        "skipped": skipped,
        "success_rate": success_rate,
    }


def format_value(value: float | int | None, ndigits: int = 4) -> str:
    if value is None:
        return "-"
    if isinstance(value, int):
        return str(value)
    return f"{value:.{ndigits}f}"


def print_runtime_summary(summary: dict[str, Any], console: Console) -> None:
    backend_counts = summary["backend_counts"]
    comp_stats = summary["comparison_stats"]

    backend_table = Table(title="Backend Success/Failure")
    backend_table.add_column("Backend")
    backend_table.add_column("Enabled")
    backend_table.add_column("Success")
    backend_table.add_column("Failure")
    backend_table.add_column("Skipped")
    backend_table.add_column("Success Rate")

    for backend_name in ("google", "valhalla", "motomap"):
        row = backend_counts[backend_name]
        backend_table.add_row(
            backend_name,
            str(row["enabled_cases"]),
            str(row["success"]),
            str(row["failure"]),
            str(row["skipped"]),
            format_value(row["success_rate"], ndigits=3),
        )
    console.print(backend_table)

    ratio_table = Table(title="Comparisons vs Google")
    ratio_table.add_column("Comparator")
    ratio_table.add_column("Dist Ratio Mean")
    ratio_table.add_column("Dist Ratio P95")
    ratio_table.add_column("Time Ratio Mean")
    ratio_table.add_column("Time Ratio P95")
    ratio_table.add_column("Dist APE% Mean")
    ratio_table.add_column("Time APE% Mean")
    ratio_table.add_column("Sample Count")

    for key, label in (
        ("motomap_vs_google", "motomap/google"),
        ("valhalla_vs_google", "valhalla/google"),
    ):
        stat = comp_stats[key]
        dist_ratio = stat["distance_ratio"]
        time_ratio = stat["duration_ratio"]
        dist_ape = stat["distance_ape_pct"]
        time_ape = stat["duration_ape_pct"]
        sample_count = (
            dist_ratio["count"] if dist_ratio["count"] else time_ratio["count"]
        )
        ratio_table.add_row(
            label,
            format_value(dist_ratio["mean"]),
            format_value(dist_ratio["p95"]),
            format_value(time_ratio["mean"]),
            format_value(time_ratio["p95"]),
            format_value(dist_ape["mean"]),
            format_value(time_ape["mean"]),
            str(sample_count),
        )
    console.print(ratio_table)


def build_summary(
    args: argparse.Namespace,
    pairs: list[ODPair],
    all_results: list[dict[str, Any]],
    pending_count: int,
    resumed_count: int,
    malformed_results_lines: int,
    graph_cache: Path,
    pairs_json: Path,
    results_jsonl: Path,
) -> dict[str, Any]:
    summary = {
        "generated_at": utc_now_iso(),
        "config": {
            "count": args.count,
            "seed": args.seed,
            "pairs_json": str(pairs_json),
            "results_jsonl": str(results_jsonl),
            "summary_json": str(args.summary_json),
            "graph_cache": str(graph_cache),
            "mode": args.mode,
            "tercih": args.tercih,
            "motor_cc": args.motor_cc,
            "google_qps": args.google_qps,
            "valhalla_qps": args.valhalla_qps,
            "valhalla_url": args.valhalla_url,
            "min_crow_m": args.min_crow_m,
            "max_crow_m": args.max_crow_m,
            "disable_google": args.disable_google,
            "disable_valhalla": args.disable_valhalla,
            "disable_motomap": args.disable_motomap,
            "disable_cpp_sampler": args.disable_cpp_sampler,
            "force_cpp_sampler": args.force_cpp_sampler,
            "dry_run": args.dry_run,
        },
        "pairs": {
            "count": len(pairs),
            "min_crow_m": min(pair.crow_m for pair in pairs) if pairs else None,
            "max_crow_m": max(pair.crow_m for pair in pairs) if pairs else None,
            "avg_crow_m": (
                (sum(pair.crow_m for pair in pairs) / len(pairs)) if pairs else None
            ),
        },
        "resume": {
            "pending_count": pending_count,
            "resumed_count": resumed_count,
            "malformed_results_lines": malformed_results_lines,
        },
        "backend_counts": {
            "google": summarize_backend_counts(all_results, "google"),
            "valhalla": summarize_backend_counts(all_results, "valhalla"),
            "motomap": summarize_backend_counts(all_results, "motomap"),
        },
        "comparison_stats": {
            "motomap_vs_google": summarize_comparator(all_results, "motomap_vs_google"),
            "valhalla_vs_google": summarize_comparator(
                all_results, "valhalla_vs_google"
            ),
        },
        "results_count": len(all_results),
    }
    return summary


def write_summary_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent

    pairs_json = resolve_path(args.pairs_json, script_dir)
    results_jsonl = resolve_path(args.results_jsonl, script_dir)
    summary_json = resolve_path(args.summary_json, script_dir)
    graph_cache = resolve_path(args.graph_cache, script_dir)

    console = Console()
    console.print(
        Panel.fit(
            (
                f"count={args.count}, seed={args.seed}\n"
                f"mode={args.mode}, tercih={args.tercih}, motor_cc={args.motor_cc}\n"
                f"google={'off' if args.disable_google else 'on'} (qps={args.google_qps}), "
                f"valhalla={'off' if args.disable_valhalla else 'on'} (qps={args.valhalla_qps}), "
                f"motomap={'off' if args.disable_motomap else 'on'}\n"
                f"crow_filter=[{args.min_crow_m:.0f}, {args.max_crow_m:.0f}] m"
            ),
            title="Istanbul -> Antalya 10k Benchmark",
        )
    )

    graph = load_or_build_corridor_graph(graph_cache, console=console)
    console.print(
        "[green]Graph ready:[/green] "
        f"{graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges"
    )

    pairs = load_or_generate_pairs(
        graph=graph,
        pairs_json=pairs_json,
        count=args.count,
        seed=args.seed,
        min_crow_m=args.min_crow_m,
        max_crow_m=args.max_crow_m,
        use_cpp_sampler=not args.disable_cpp_sampler,
        force_cpp_sampler=args.force_cpp_sampler,
        console=console,
    )
    console.print(f"[green]Pairs ready:[/green] {len(pairs)}")

    existing_results_by_case, malformed_lines = load_existing_results(results_jsonl)
    target_case_ids = {pair.case_id for pair in pairs}
    existing_results_by_case = {
        case_id: row
        for case_id, row in existing_results_by_case.items()
        if case_id in target_case_ids
    }

    pending_pairs = [
        pair for pair in pairs if pair.case_id not in existing_results_by_case
    ]
    resumed_count = len(existing_results_by_case)
    console.print(
        f"[cyan]Resume state:[/cyan] existing={resumed_count}, pending={len(pending_pairs)}, "
        f"malformed_lines={malformed_lines}"
    )

    if args.dry_run:
        summary = build_summary(
            args=args,
            pairs=pairs,
            all_results=list(existing_results_by_case.values()),
            pending_count=len(pending_pairs),
            resumed_count=resumed_count,
            malformed_results_lines=malformed_lines,
            graph_cache=graph_cache,
            pairs_json=pairs_json,
            results_jsonl=results_jsonl,
        )
        write_summary_json(summary_json, summary)
        console.print(f"[green]Dry-run summary written:[/green] {summary_json}")
        print_runtime_summary(summary, console=console)
        return

    google_enabled = not args.disable_google
    valhalla_enabled = not args.disable_valhalla
    motomap_enabled = not args.disable_motomap

    if google_enabled and not GOOGLE_MAPS_API_KEY:
        console.print(
            "[yellow]GOOGLE_MAPS_API_KEY is empty; Google backend will return MISSING_API_KEY for all cases.[/yellow]"
        )

    google_limiter = QPSLimiter(args.google_qps) if google_enabled else None
    valhalla_limiter = QPSLimiter(args.valhalla_qps) if valhalla_enabled else None
    google_session = requests.Session()
    valhalla_session = requests.Session()

    new_results_count = 0
    with tqdm(total=len(pending_pairs), desc="Benchmarking", unit="case") as progress:
        for pair in pending_pairs:
            try:
                row = evaluate_case(
                    graph=graph,
                    pair=pair,
                    enable_google=google_enabled,
                    enable_valhalla=valhalla_enabled,
                    enable_motomap=motomap_enabled,
                    google_session=google_session,
                    valhalla_session=valhalla_session,
                    google_limiter=google_limiter,
                    valhalla_limiter=valhalla_limiter,
                    google_api_key=GOOGLE_MAPS_API_KEY,
                    valhalla_url=args.valhalla_url,
                    mode=args.mode,
                    tercih=args.tercih,
                    motor_cc=args.motor_cc,
                )
            except Exception as exc:  # pragma: no cover - defensive runtime reporting
                row = {
                    "timestamp_utc": utc_now_iso(),
                    "case_id": pair.case_id,
                    "origin": pair.origin.to_json(),
                    "destination": pair.destination.to_json(),
                    "crow_m": pair.crow_m,
                    "settings": {
                        "mode": args.mode,
                        "tercih": args.tercih,
                        "motor_cc": args.motor_cc,
                    },
                    "google": make_backend_result(
                        enabled=google_enabled,
                        success=False,
                        status="CASE_ERROR",
                        error=str(exc),
                    ),
                    "valhalla": make_backend_result(
                        enabled=valhalla_enabled,
                        success=False,
                        status="CASE_ERROR",
                        error=str(exc),
                    ),
                    "motomap": make_backend_result(
                        enabled=motomap_enabled,
                        success=False,
                        status="CASE_ERROR",
                        error=str(exc),
                    ),
                    "comparisons": {
                        "motomap_vs_google": {
                            "distance_ratio": None,
                            "duration_ratio": None,
                            "distance_ape_pct": None,
                            "duration_ape_pct": None,
                        },
                        "valhalla_vs_google": {
                            "distance_ratio": None,
                            "duration_ratio": None,
                            "distance_ape_pct": None,
                            "duration_ape_pct": None,
                        },
                    },
                }
            append_jsonl(results_jsonl, row)
            existing_results_by_case[pair.case_id] = row
            new_results_count += 1
            progress.update(1)

            if progress.n % 50 == 0:
                g_ok = int(row["google"]["success"])
                v_ok = int(row["valhalla"]["success"])
                m_ok = int(row["motomap"]["success"])
                progress.set_postfix(
                    {
                        "new": new_results_count,
                        "g_ok": g_ok,
                        "v_ok": v_ok,
                        "m_ok": m_ok,
                    }
                )

    all_results = [existing_results_by_case[pair.case_id] for pair in pairs]

    summary = build_summary(
        args=args,
        pairs=pairs,
        all_results=all_results,
        pending_count=len(pending_pairs),
        resumed_count=resumed_count,
        malformed_results_lines=malformed_lines,
        graph_cache=graph_cache,
        pairs_json=pairs_json,
        results_jsonl=results_jsonl,
    )
    write_summary_json(summary_json, summary)
    console.print(f"[green]Summary written:[/green] {summary_json}")
    print_runtime_summary(summary, console=console)


if __name__ == "__main__":
    main()
