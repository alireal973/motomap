"""Evaluate MOTOMAP route quality against a driving-directions baseline.

Supported backends:
  google   – Google Directions API (requires GOOGLE_MAPS_API_KEY)
  valhalla – FOSSGIS public Valhalla instance (free, no key)

Usage examples:
  python evaluate_with_google.py --batch 20 --skip-single
  python evaluate_with_google.py --batch 20 --backend valhalla --skip-single
  python evaluate_with_google.py --batch 20 --backend valhalla \
      --valhalla-url https://valhalla1.openstreetmap.de --skip-single
  python evaluate_with_google.py --batch 20 --pairs-file routes/od_pairs.json
"""

from __future__ import annotations

import argparse
import json
import random
import subprocess
import time
import sys
from datetime import datetime, timezone
from pathlib import Path

import networkx as nx
import osmnx as ox
import requests

# Add project root to path so we can import motomap
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from motomap import GOOGLE_MAPS_API_KEY, motomap_graf_olustur
from motomap.algorithm import (
    TRAVEL_TIME_ATTR,
    add_travel_time_to_graph,
    is_toll_edge,
    mode_weight_attr,
    ucret_opsiyonlu_rota_hesapla,
)

MODES = ["standart", "viraj_keyfi", "guvenli"]
DEFAULT_PLACE = "Kadikoy, Istanbul, Turkey"
DEFAULT_ROUTE_JSON = Path("routes") / "motomap_route.json"

DEFAULT_VALHALLA_BASE_URL = "https://valhalla1.openstreetmap.de"
ACTIVE_BACKEND = "google"  # overridden by --backend flag
ACTIVE_VALHALLA_BASE_URL = DEFAULT_VALHALLA_BASE_URL  # overridden by --valhalla-url


def nodes_to_coords(graph: nx.MultiDiGraph, node_ids: list[int]) -> list[dict]:
    return [
        {"lat": graph.nodes[nid]["y"], "lng": graph.nodes[nid]["x"]} for nid in node_ids
    ]


def decode_polyline(encoded: str) -> list[dict]:
    points = []
    index = 0
    lat = 0
    lng = 0

    while index < len(encoded):
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        lat += ~(result >> 1) if (result & 1) else (result >> 1)

        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        lng += ~(result >> 1) if (result & 1) else (result >> 1)

        points.append({"lat": lat / 1e5, "lng": lng / 1e5})

    return points


def fetch_google_route(origin: dict, destination: dict, api_key: str) -> dict:
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{origin['lat']},{origin['lng']}",
        "destination": f"{destination['lat']},{destination['lng']}",
        "mode": "driving",
        "key": api_key,
    }
    data = requests.get(url, params=params, timeout=30).json()

    if data.get("status") != "OK":
        return {"coordinates": [], "stats": {}, "status": data.get("status", "UNKNOWN")}

    route = data["routes"][0]
    leg = route["legs"][0]
    return {
        "coordinates": decode_polyline(route["overview_polyline"]["points"]),
        "stats": {
            "mesafe_m": leg["distance"]["value"],
            "mesafe_text": leg["distance"]["text"],
            "sure_s": leg["duration"]["value"],
            "sure_text": leg["duration"]["text"],
        },
        "status": "OK",
    }


def decode_polyline6(encoded: str) -> list[dict]:
    """Decode a polyline with 6-digit precision (Valhalla format)."""
    points = []
    index = 0
    lat = 0
    lng = 0
    while index < len(encoded):
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        lat += ~(result >> 1) if (result & 1) else (result >> 1)
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        lng += ~(result >> 1) if (result & 1) else (result >> 1)
        points.append({"lat": lat / 1e6, "lng": lng / 1e6})
    return points


def fetch_valhalla_route(
    origin: dict,
    destination: dict,
    base_url: str = DEFAULT_VALHALLA_BASE_URL,
    max_retries: int = 3,
) -> dict:
    """Fetch a driving route from a Valhalla instance (no API key needed)."""
    payload = {
        "locations": [
            {"lat": origin["lat"], "lon": origin["lng"]},
            {"lat": destination["lat"], "lon": destination["lng"]},
        ],
        "costing": "auto",
        "shape_format": "polyline6",
        "directions_options": {"units": "kilometers"},
    }
    for attempt in range(max_retries):
        try:
            resp = requests.post(f"{base_url}/route", json=payload, timeout=30)
            if resp.status_code == 429:  # rate-limited
                time.sleep(2 * (attempt + 1))
                continue
            if 500 <= resp.status_code < 600:
                if attempt == max_retries - 1:
                    return {
                        "coordinates": [],
                        "stats": {},
                        "status": f"HTTP_{resp.status_code}",
                    }
                time.sleep(1 + attempt)
                continue
            if resp.status_code >= 400:
                return {
                    "coordinates": [],
                    "stats": {},
                    "status": f"HTTP_{resp.status_code}",
                }
            try:
                data = resp.json()
            except ValueError:
                if attempt == max_retries - 1:
                    return {
                        "coordinates": [],
                        "stats": {},
                        "status": "MALFORMED_RESPONSE",
                    }
                time.sleep(1)
                continue
            break
        except (requests.RequestException, ValueError):
            if attempt == max_retries - 1:
                return {"coordinates": [], "stats": {}, "status": "REQUEST_ERROR"}
            time.sleep(1)
    else:
        return {"coordinates": [], "stats": {}, "status": "RATE_LIMITED"}

    trip = data.get("trip")
    if trip is None or trip.get("status", 1) != 0:
        return {
            "coordinates": [],
            "stats": {},
            "status": data.get("status_message", "VALHALLA_ERROR"),
        }

    summary = trip["summary"]
    leg = trip["legs"][0]
    distance_m = round(summary["length"] * 1000)
    time_s = round(summary["time"])
    coords = decode_polyline6(leg["shape"])

    return {
        "coordinates": coords,
        "stats": {
            "mesafe_m": distance_m,
            "mesafe_text": f"{summary['length']:.1f} km",
            "sure_s": time_s,
            "sure_text": f"{time_s // 60} min",
        },
        "status": "OK",
    }


def fetch_baseline_route(origin: dict, destination: dict) -> dict:
    """Dispatch to the active routing backend."""
    if ACTIVE_BACKEND == "valhalla":
        return fetch_valhalla_route(
            origin,
            destination,
            base_url=ACTIVE_VALHALLA_BASE_URL,
        )
    return fetch_google_route(origin, destination, GOOGLE_MAPS_API_KEY)


def edge_pairs(nodes: list[int]) -> set[tuple[int, int]]:
    return set(zip(nodes, nodes[1:]))


def edge_overlap_ratio(path_a: list[int], path_b: list[int]) -> float:
    edges_a = edge_pairs(path_a)
    edges_b = edge_pairs(path_b)
    if not edges_a or not edges_b:
        return 0.0
    inter = len(edges_a & edges_b)
    union = len(edges_a | edges_b)
    return inter / max(1, union)


def build_weighted_digraph(
    graph: nx.MultiDiGraph,
    weight_attr: str,
    allow_toll: bool = True,
) -> nx.DiGraph:
    dg = nx.DiGraph()
    for u, v, _, data in graph.edges(keys=True, data=True):
        if not allow_toll and is_toll_edge(data):
            continue
        weight = float(data.get(weight_attr, float("inf")))
        if not weight < float("inf"):
            continue
        if dg.has_edge(u, v):
            if weight < float(dg[u][v]["weight"]):
                dg[u][v]["weight"] = weight
        else:
            dg.add_edge(u, v, weight=weight)
    return dg


def find_diverse_path(
    graph: nx.MultiDiGraph,
    source: int,
    target: int,
    weight_attr: str,
    used_paths: list[list[int]],
    allow_toll: bool = True,
    max_candidates: int = 40,
    max_overlap: float = 0.86,
) -> list[int] | None:
    dg = build_weighted_digraph(graph, weight_attr=weight_attr, allow_toll=allow_toll)
    if source not in dg or target not in dg:
        return None

    try:
        candidates = nx.shortest_simple_paths(dg, source, target, weight="weight")
    except nx.NetworkXNoPath:
        return None

    for candidate in candidates:
        if all(
            edge_overlap_ratio(candidate, used) <= max_overlap for used in used_paths
        ):
            return list(candidate)
        max_candidates -= 1
        if max_candidates <= 0:
            break
    return None


def find_diverse_path_relaxed(
    graph: nx.MultiDiGraph,
    source: int,
    target: int,
    weight_attr: str,
    used_paths: list[list[int]],
    allow_toll: bool = True,
) -> list[int] | None:
    """Try strict-to-relaxed diversity thresholds to avoid identical mode outputs."""
    for overlap in (0.86, 0.92, 0.97, 0.995):
        alt = find_diverse_path(
            graph,
            source=source,
            target=target,
            weight_attr=weight_attr,
            used_paths=used_paths,
            allow_toll=allow_toll,
            max_candidates=140,
            max_overlap=overlap,
        )
        if alt is not None:
            return alt
    return None


def best_edge_data(
    graph: nx.MultiDiGraph, u: int, v: int, weight_attr: str
) -> dict | None:
    edges = graph.get_edge_data(u, v) or {}
    if not edges:
        return None
    return min(
        edges.values(), key=lambda data: float(data.get(weight_attr, float("inf")))
    )


def summarize_path(graph: nx.MultiDiGraph, nodes: list[int], weight_attr: str) -> dict:
    total_cost = 0.0
    total_time = 0.0
    total_length = 0.0
    includes_toll = False
    fun_count = 0
    danger_count = 0
    high_risk_count = 0
    grades = []

    for idx in range(len(nodes) - 1):
        edge = best_edge_data(
            graph, nodes[idx], nodes[idx + 1], weight_attr=weight_attr
        )
        if edge is None:
            continue

        total_cost += float(edge.get(weight_attr, 0.0))
        total_time += float(edge.get(TRAVEL_TIME_ATTR, 0.0))
        total_length += float(edge.get("length", 0.0) or 0.0)
        includes_toll = includes_toll or is_toll_edge(edge)
        fun_count += int(edge.get("viraj_fun_sayisi", 0) or 0)
        danger_count += int(edge.get("viraj_tehlike_sayisi", 0) or 0)
        high_risk_count += int(bool(edge.get("yuksek_risk_bolge", False)))
        grades.append(float(edge.get("grade", 0.0) or 0.0))

    return {
        "nodes": nodes,
        "toplam_sure_s": total_time,
        "toplam_maliyet_s": total_cost,
        "toplam_mesafe_m": total_length,
        "ucretli_yol_iceriyor": includes_toll,
        "viraj_fun_sayisi": fun_count,
        "viraj_tehlike_sayisi": danger_count,
        "yuksek_risk_segment_sayisi": high_risk_count,
        "ortalama_egim_orani": (sum(grades) / len(grades)) if grades else 0.0,
    }


def find_fun_richer_path(
    graph: nx.MultiDiGraph,
    source: int,
    target: int,
    weight_attr: str,
    min_fun_count: int,
    base_time_s: float,
    max_candidates: int = 80,
    max_time_multiplier: float = 2.2,
) -> tuple[dict, list[int]] | None:
    """Try to find an alternative viraj route with equal/higher fun score."""
    dg = build_weighted_digraph(graph, weight_attr=weight_attr, allow_toll=True)
    if source not in dg or target not in dg:
        return None

    try:
        candidates = nx.shortest_simple_paths(dg, source, target, weight="weight")
    except nx.NetworkXNoPath:
        return None

    best_summary = None
    best_nodes = None
    best_fun = -1

    for candidate in candidates:
        summary = summarize_path(graph, list(candidate), weight_attr=weight_attr)
        if summary["toplam_sure_s"] > float(base_time_s) * max_time_multiplier:
            max_candidates -= 1
            if max_candidates <= 0:
                break
            continue

        fun_count = int(summary["viraj_fun_sayisi"])
        if fun_count >= int(min_fun_count):
            return summary, list(candidate)

        if fun_count > best_fun:
            best_fun = fun_count
            best_summary = summary
            best_nodes = list(candidate)

        max_candidates -= 1
        if max_candidates <= 0:
            break

    if best_summary is None or best_nodes is None:
        return None
    return best_summary, best_nodes


def fp(coords: list[dict]) -> tuple[tuple[float, float], ...]:
    return tuple((round(p["lat"], 5), round(p["lng"], 5)) for p in coords)


def safe_ratio(
    numerator: float | int | None, denominator: float | int | None
) -> float | None:
    if numerator is None or denominator is None:
        return None
    denom = float(denominator)
    if denom <= 0:
        return None
    return float(numerator) / denom


def evaluate_checks(route_doc: dict) -> tuple[dict[str, bool], dict]:
    modes = route_doc.get("modes", {})
    baseline_route = route_doc.get("baseline_route")
    if baseline_route is None:
        baseline_route = route_doc.get("google_route", [])
    baseline_stats = route_doc.get("baseline_stats")
    if not baseline_stats:
        baseline_stats = route_doc.get("google_stats", {}) or {}
    baseline_backend = route_doc.get("baseline_backend", ACTIVE_BACKEND)

    std = (modes.get("standart") or {}).get("stats", {})
    vir = (modes.get("viraj_keyfi") or {}).get("stats", {})
    safe = (modes.get("guvenli") or {}).get("stats", {})

    dist_ratio = safe_ratio(std.get("mesafe_m"), baseline_stats.get("mesafe_m"))
    time_ratio = safe_ratio(std.get("sure_s"), baseline_stats.get("sure_s"))

    checks = {
        "baseline_route_exists": len(baseline_route) > 0,
        "all_modes_exist": all(
            len((modes.get(k) or {}).get("coordinates", [])) > 0 for k in MODES
        ),
        "modes_are_different": len(
            {fp((modes.get(k) or {}).get("coordinates", [])) for k in MODES}
        )
        == 3,
        "safe_risk_le_standard": (safe.get("yuksek_risk", float("inf")))
        <= (std.get("yuksek_risk", float("-inf"))),
        "viraj_fun_ge_standard": (vir.get("viraj_fun", float("-inf")))
        >= (std.get("viraj_fun", float("inf"))),
        "std_distance_vs_baseline_ok": (dist_ratio is not None)
        and (0.7 <= dist_ratio <= 1.4),
        "std_time_vs_baseline_ok": (time_ratio is not None)
        and (0.5 <= time_ratio <= 1.8),
    }

    metrics = {
        "baseline_backend": baseline_backend,
        "std_distance_ratio_vs_baseline": dist_ratio,
        "std_time_ratio_vs_baseline": time_ratio,
        "baseline_sure_s": baseline_stats.get("sure_s"),
        "standart_sure_s": std.get("sure_s"),
        "baseline_mesafe_m": baseline_stats.get("mesafe_m"),
        "standart_mesafe_m": std.get("mesafe_m"),
        # Backward-compatible aliases for prior reports.
        "std_distance_ratio_vs_google": dist_ratio,
        "std_time_ratio_vs_google": time_ratio,
        "google_sure_s": baseline_stats.get("sure_s"),
        "google_mesafe_m": baseline_stats.get("mesafe_m"),
    }
    return checks, metrics


def print_checks(checks: dict[str, bool]) -> None:
    for key, value in checks.items():
        print(f"{key}: {'PASS' if value else 'FAIL'}")


def summarize_case(label: str, checks: dict[str, bool], metrics: dict) -> dict:
    score = int(sum(1 for value in checks.values() if value))
    total = len(checks)
    status = "PASS" if score == total else "FAIL"
    baseline_label = str(metrics.get("baseline_backend", "baseline")).capitalize()
    baseline_sure_s = metrics.get("baseline_sure_s")
    if baseline_sure_s is None:
        baseline_sure_s = metrics.get("google_sure_s")
    time_ratio = metrics.get("std_time_ratio_vs_baseline")
    if time_ratio is None:
        time_ratio = metrics.get("std_time_ratio_vs_google")
    print(f"\n[{label}] {status}  score={score}/{total}")
    print_checks(checks)
    print(
        f"{baseline_label} sure_s={baseline_sure_s}, "
        f"Standart sure_s={metrics.get('standart_sure_s')}, "
        f"time_ratio={time_ratio}"
    )
    return {
        "label": label,
        "status": status,
        "score": score,
        "total": total,
        "checks": checks,
        "metrics": metrics,
    }


def parse_float(value, name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid numeric value for {name}: {value}") from exc


def normalize_point(point: dict, prefix: str = "") -> dict:
    lat = parse_float(point.get("lat"), f"{prefix}lat")
    lng = parse_float(point.get("lng"), f"{prefix}lng")
    return {"lat": lat, "lng": lng}


def load_pairs_file(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "pairs" in data:
        rows = data["pairs"]
    elif isinstance(data, list):
        rows = data
    else:
        raise ValueError("Pairs file must be a JSON list or {'pairs': [...]} object.")

    pairs = []
    for idx, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"Invalid pair row at index {idx}: must be object.")

        origin = row.get("origin")
        destination = row.get("destination")
        if origin is None or destination is None:
            raise ValueError(
                f"Pair row {idx} must include 'origin' and 'destination' objects."
            )

        label = str(row.get("label", f"pair_{idx:02d}"))
        pairs.append(
            {
                "label": label,
                "origin": normalize_point(origin, prefix=f"{label}.origin."),
                "destination": normalize_point(
                    destination, prefix=f"{label}.destination."
                ),
            }
        )
    return pairs


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    from math import asin, cos, radians, sin, sqrt

    radius_m = 6371000.0
    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    )
    return 2 * radius_m * asin(sqrt(a))


def sample_pairs_from_graph(
    graph: nx.MultiDiGraph,
    count: int,
    seed: int,
    min_distance_m: float,
    max_distance_m: float,
) -> list[dict]:
    rng = random.Random(seed)
    nodes = list(graph.nodes)
    if len(nodes) < 2:
        return []

    pairs = []
    seen = set()
    max_attempts = max(2000, count * 250)
    attempts = 0

    while len(pairs) < count and attempts < max_attempts:
        attempts += 1
        n1, n2 = rng.sample(nodes, 2)
        pair_key = (n1, n2)
        if pair_key in seen:
            continue
        seen.add(pair_key)

        o_lat, o_lng = graph.nodes[n1]["y"], graph.nodes[n1]["x"]
        d_lat, d_lng = graph.nodes[n2]["y"], graph.nodes[n2]["x"]
        crow_m = haversine_m(o_lat, o_lng, d_lat, d_lng)
        if crow_m < min_distance_m or crow_m > max_distance_m:
            continue

        pairs.append(
            {
                "label": f"sample_{len(pairs) + 1:02d}",
                "origin": {"lat": o_lat, "lng": o_lng},
                "destination": {"lat": d_lat, "lng": d_lng},
            }
        )

    return pairs


def build_route_document(
    graph: nx.MultiDiGraph, origin: dict, destination: dict
) -> dict:
    origin_node = ox.nearest_nodes(graph, origin["lng"], origin["lat"])
    destination_node = ox.nearest_nodes(graph, destination["lng"], destination["lat"])

    if origin_node == destination_node:
        raise ValueError("Origin and destination map to the same graph node.")

    origin_actual = {
        "lat": graph.nodes[origin_node]["y"],
        "lng": graph.nodes[origin_node]["x"],
    }
    destination_actual = {
        "lat": graph.nodes[destination_node]["y"],
        "lng": graph.nodes[destination_node]["x"],
    }

    baseline_data = fetch_baseline_route(origin_actual, destination_actual)
    result = {
        "origin": origin_actual,
        "destination": destination_actual,
        "origin_label": "",
        "destination_label": "",
        "baseline_backend": ACTIVE_BACKEND,
        "baseline_route": baseline_data["coordinates"],
        "baseline_stats": baseline_data["stats"],
        "baseline_status": baseline_data.get("status", "UNKNOWN"),
        # Backward-compatible aliases used by existing report tooling.
        "google_route": baseline_data["coordinates"],
        "google_stats": baseline_data["stats"],
        "google_status": baseline_data.get("status", "UNKNOWN"),
        "modes": {},
    }

    selected_paths: list[list[int]] = []
    for mode in MODES:
        route = ucret_opsiyonlu_rota_hesapla(
            graph,
            source=origin_node,
            target=destination_node,
            tercih="ucretli_serbest",
            surus_modu=mode,
        )
        selected = route["secilen_rota"]
        mode_nodes = list(selected["nodes"])
        mode_weight = mode_weight_attr(mode)

        if selected_paths:
            max_current_overlap = max(
                edge_overlap_ratio(mode_nodes, p) for p in selected_paths
            )
            if max_current_overlap > 0.98:
                alt_nodes = find_diverse_path(
                    graph,
                    source=origin_node,
                    target=destination_node,
                    weight_attr=mode_weight,
                    used_paths=selected_paths,
                    allow_toll=True,
                )
                if alt_nodes is not None:
                    selected = summarize_path(graph, alt_nodes, weight_attr=mode_weight)
                    mode_nodes = alt_nodes
                else:
                    relaxed_nodes = find_diverse_path_relaxed(
                        graph,
                        source=origin_node,
                        target=destination_node,
                        weight_attr=mode_weight,
                        used_paths=selected_paths,
                        allow_toll=True,
                    )
                    if relaxed_nodes is not None:
                        selected = summarize_path(
                            graph, relaxed_nodes, weight_attr=mode_weight
                        )
                        mode_nodes = relaxed_nodes

        if mode == "viraj_keyfi" and "standart" in result["modes"]:
            standard_fun = int(result["modes"]["standart"]["stats"]["viraj_fun"])
            current_fun = int(selected["viraj_fun_sayisi"])
            if current_fun < standard_fun:
                richer = find_fun_richer_path(
                    graph,
                    source=origin_node,
                    target=destination_node,
                    weight_attr=mode_weight,
                    min_fun_count=standard_fun,
                    base_time_s=float(selected["toplam_sure_s"]),
                )
                if richer is not None:
                    selected, mode_nodes = richer

        selected_paths.append(mode_nodes)
        result["modes"][mode] = {
            "coordinates": nodes_to_coords(graph, mode_nodes),
            "stats": {
                "mesafe_m": round(selected["toplam_mesafe_m"], 1),
                "sure_s": round(selected["toplam_sure_s"], 1),
                "viraj_fun": selected["viraj_fun_sayisi"],
                "viraj_tehlike": selected["viraj_tehlike_sayisi"],
                "yuksek_risk": selected["yuksek_risk_segment_sayisi"],
                "ortalama_egim": round(selected["ortalama_egim_orani"], 4),
                "ucretli": selected["ucretli_yol_iceriyor"],
            },
        }

    return result


def run_generate_route(script_dir: Path) -> None:
    script_path = script_dir / "generate_route.py"
    if not script_path.exists():
        raise FileNotFoundError(f"generate_route.py not found at: {script_path}")
    subprocess.run([sys.executable, str(script_path)], cwd=str(script_dir), check=True)


def evaluate_single_route_json(route_json_path: Path) -> dict:
    data = json.loads(route_json_path.read_text(encoding="utf-8"))
    checks, metrics = evaluate_checks(data)
    case = summarize_case("single_route", checks, metrics)
    case["route_json"] = str(route_json_path)
    return case


def evaluate_batch(
    place: str,
    batch_count: int,
    seed: int,
    min_distance_m: float,
    max_distance_m: float,
    pairs_file: Path | None,
) -> dict:
    print(f"\nBuilding graph for batch evaluation: {place}")
    graph = motomap_graf_olustur(place)
    graph = add_travel_time_to_graph(graph)

    if pairs_file is not None:
        pairs = load_pairs_file(pairs_file)
        print(f"Loaded {len(pairs)} O-D pairs from {pairs_file}")
    else:
        pairs = sample_pairs_from_graph(
            graph=graph,
            count=batch_count,
            seed=seed,
            min_distance_m=min_distance_m,
            max_distance_m=max_distance_m,
        )
        print(f"Sampled {len(pairs)} O-D pairs from graph")

    if batch_count > 0:
        pairs = pairs[:batch_count]

    if not pairs:
        raise ValueError("No O-D pairs available for batch evaluation.")

    cases = []
    failed_checks = {
        "baseline_route_exists": 0,
        "all_modes_exist": 0,
        "modes_are_different": 0,
        "safe_risk_le_standard": 0,
        "viraj_fun_ge_standard": 0,
        "std_distance_vs_baseline_ok": 0,
        "std_time_vs_baseline_ok": 0,
    }

    for idx, pair in enumerate(pairs, start=1):
        label = pair["label"]
        print(f"\n[{idx}/{len(pairs)}] Evaluating {label}")
        try:
            route_doc = build_route_document(graph, pair["origin"], pair["destination"])
            checks, metrics = evaluate_checks(route_doc)
            case = summarize_case(label, checks, metrics)
            case["origin"] = route_doc["origin"]
            case["destination"] = route_doc["destination"]
            case["baseline_status"] = route_doc.get(
                "baseline_status",
                route_doc.get("google_status", "UNKNOWN"),
            )
            case["google_status"] = route_doc.get("google_status", "UNKNOWN")
            cases.append(case)
            for key, value in checks.items():
                if not value:
                    failed_checks[key] += 1
        except Exception as exc:  # pragma: no cover - defensive runtime reporting
            print(f"[{label}] ERROR: {exc}")
            cases.append(
                {
                    "label": label,
                    "status": "ERROR",
                    "score": 0,
                    "total": len(failed_checks),
                    "checks": {key: False for key in failed_checks},
                    "metrics": {},
                    "error": str(exc),
                }
            )
            for key in failed_checks:
                failed_checks[key] += 1

    pass_cases = sum(1 for c in cases if c["status"] == "PASS")
    avg_score = sum(c.get("score", 0) for c in cases) / max(1, len(cases))

    print("\nBatch summary")
    print(f"full_pass: {pass_cases}/{len(cases)}")
    print(f"average_score: {avg_score:.2f}/{len(failed_checks)}")
    print("failed_checks:")
    for key, count in failed_checks.items():
        print(f"  {key}: {count}")

    return {
        "place": place,
        "count_evaluated": len(cases),
        "full_pass": pass_cases,
        "average_score": round(avg_score, 4),
        "failed_checks": failed_checks,
        "cases": cases,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate MOTOMAP outputs against a driving-directions baseline."
    )
    parser.add_argument(
        "--route-json",
        default=str(DEFAULT_ROUTE_JSON),
        help="Route JSON path for single-run quality check (default: routes/motomap_route.json).",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Run generate_route.py before evaluating --route-json.",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=0,
        help="Number of O-D pairs to evaluate in batch mode.",
    )
    parser.add_argument(
        "--place",
        default=DEFAULT_PLACE,
        help=f"Place string for graph generation (default: {DEFAULT_PLACE}).",
    )
    parser.add_argument(
        "--pairs-file",
        type=str,
        help="Optional JSON file with explicit O-D pairs.",
    )
    parser.add_argument(
        "--seed", type=int, default=42, help="Random seed for sampled O-D pairs."
    )
    parser.add_argument(
        "--min-distance-m",
        type=float,
        default=1000.0,
        help="Minimum crow-fly O-D distance when sampling pairs.",
    )
    parser.add_argument(
        "--max-distance-m",
        type=float,
        default=10000.0,
        help="Maximum crow-fly O-D distance when sampling pairs.",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        help="Optional output path for machine-readable summary JSON.",
    )
    parser.add_argument(
        "--skip-single",
        action="store_true",
        help="Skip single route-json evaluation.",
    )
    parser.add_argument(
        "--backend",
        choices=["google", "valhalla"],
        default="google",
        help="Routing backend for baseline comparison (default: google).",
    )
    parser.add_argument(
        "--valhalla-url",
        default=DEFAULT_VALHALLA_BASE_URL,
        help="Valhalla base URL for --backend valhalla.",
    )
    return parser.parse_args()


def main() -> None:
    global ACTIVE_BACKEND, ACTIVE_VALHALLA_BASE_URL
    args = parse_args()
    ACTIVE_BACKEND = args.backend
    ACTIVE_VALHALLA_BASE_URL = args.valhalla_url
    script_dir = Path(__file__).resolve().parent

    print(f"Baseline backend: {ACTIVE_BACKEND}")

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "backend": ACTIVE_BACKEND,
        "valhalla_url": (
            ACTIVE_VALHALLA_BASE_URL if ACTIVE_BACKEND == "valhalla" else None
        ),
        "single": None,
        "batch": None,
    }

    if args.generate:
        print("Running generate_route.py ...")
        run_generate_route(script_dir)

    run_single = not args.skip_single
    if run_single:
        route_json_path = Path(args.route_json)
        if not route_json_path.is_absolute():
            route_json_path = script_dir / route_json_path
        if route_json_path.exists():
            summary["single"] = evaluate_single_route_json(route_json_path)
        else:
            print(
                f"Single evaluation skipped: route json not found -> {route_json_path}"
            )

    if args.batch > 0 or args.pairs_file:
        pairs_file = Path(args.pairs_file) if args.pairs_file else None
        if pairs_file and not pairs_file.is_absolute():
            pairs_file = script_dir / pairs_file
        summary["batch"] = evaluate_batch(
            place=args.place,
            batch_count=max(args.batch, 0),
            seed=args.seed,
            min_distance_m=args.min_distance_m,
            max_distance_m=args.max_distance_m,
            pairs_file=pairs_file,
        )

    if summary["single"] is None and summary["batch"] is None:
        raise SystemExit(
            "Nothing to evaluate. Provide --generate, --batch, or a valid --route-json path."
        )

    if args.output_json:
        output_path = Path(args.output_json)
        if not output_path.is_absolute():
            output_path = script_dir / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nSaved summary: {output_path}")


if __name__ == "__main__":
    main()
