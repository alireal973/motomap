"""Generate MOTOMAP and Google routes for the comparison website."""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import networkx as nx
import osmnx as ox
import requests

# Windows terminal fallback: avoid UnicodeEncodeError on non-UTF8 code pages.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

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

# --- Configuration ---
PLACE = "Kadıköy, İstanbul, Turkey"
ORIGIN = (40.9923, 29.0239)  # Kadıköy İskele
DESTINATION = (40.9700, 29.0380)  # Kalamış Parkı
MODES = ["standart", "viraj_keyfi", "guvenli"]
OUTPUT_DIR = Path(__file__).resolve().parent / "routes"


def nodes_to_coords(graph: nx.MultiDiGraph, node_ids: list) -> list[dict]:
    """Convert node IDs to [{lat, lng}, ...]."""
    return [
        {"lat": graph.nodes[nid]["y"], "lng": graph.nodes[nid]["x"]} for nid in node_ids
    ]


def decode_polyline(encoded: str) -> list[dict]:
    """Decode an encoded polyline."""
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
    """Fetch Google route coordinates + distance/time stats."""
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{origin['lat']},{origin['lng']}",
        "destination": f"{destination['lat']},{destination['lng']}",
        "mode": "driving",
        "key": api_key,
    }
    data = requests.get(url, params=params, timeout=30).json()

    if data.get("status") != "OK":
        print(f"  Google Directions API error: {data.get('status', 'UNKNOWN')}")
        return {"coordinates": [], "stats": {}}

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
    }


def edge_pairs(nodes: list) -> set[tuple]:
    return set(zip(nodes, nodes[1:]))


def edge_overlap_ratio(path_a: list, path_b: list) -> float:
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
    """Convert MultiDiGraph to DiGraph with min edge weight per direction."""
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
    used_paths: list[list],
    allow_toll: bool = True,
    max_candidates: int = 40,
    max_overlap: float = 0.86,
) -> list | None:
    """Find a low-cost path that is meaningfully different from existing paths."""
    dg = build_weighted_digraph(graph, weight_attr=weight_attr, allow_toll=allow_toll)
    if source not in dg or target not in dg:
        return None

    try:
        candidates = nx.shortest_simple_paths(dg, source, target, weight="weight")
    except nx.NetworkXNoPath:
        return None

    for candidate in itertools.islice(candidates, max_candidates):
        if all(
            edge_overlap_ratio(candidate, used) <= max_overlap for used in used_paths
        ):
            return candidate
    return None


def find_diverse_path_relaxed(
    graph: nx.MultiDiGraph,
    source: int,
    target: int,
    weight_attr: str,
    used_paths: list[list],
    allow_toll: bool = True,
) -> list | None:
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
        edges.values(),
        key=lambda data: float(data.get(weight_attr, float("inf"))),
    )


def summarize_path(graph: nx.MultiDiGraph, nodes: list, weight_attr: str) -> dict:
    total_cost = 0.0
    total_time = 0.0
    total_length = 0.0
    includes_toll = False
    fun_count = 0
    danger_count = 0
    high_risk_count = 0
    serit_paylasimi_m = 0.0
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
        serit_paylasimi_m += float(edge.get("serit_paylasimi_m", 0.0) or 0.0)
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
        "serit_paylasimi_m": serit_paylasimi_m,
        "ortalama_egim_orani": (sum(grades) / len(grades)) if grades else 0.0,
    }


def edge_geometry_coords(
    graph: nx.MultiDiGraph, u: int, v: int, edge_data: dict
) -> list[dict]:
    geometry = edge_data.get("geometry")
    if geometry is not None and hasattr(geometry, "coords"):
        coords = list(geometry.coords)
        if coords:
            return [{"lat": float(lat), "lng": float(lng)} for lng, lat in coords]
    return [
        {"lat": float(graph.nodes[u]["y"]), "lng": float(graph.nodes[u]["x"])},
        {"lat": float(graph.nodes[v]["y"]), "lng": float(graph.nodes[v]["x"])},
    ]


def midpoint_coord(coords: list[dict]) -> dict:
    if not coords:
        return {"lat": 0.0, "lng": 0.0}
    return coords[len(coords) // 2]


def normalize_tag_value(value, default: str) -> str:
    if isinstance(value, (list, tuple, set)):
        parts = [str(item).strip() for item in value if str(item).strip()]
    else:
        text = str(value or "").strip()
        parts = [text] if text else []
    if not parts:
        return default
    seen: list[str] = []
    for part in parts:
        cleaned = part.replace("_", " ").strip()
        if cleaned and cleaned not in seen:
            seen.append(cleaned)
    return " / ".join(seen[:2]) if seen else default


def merge_record_cluster(records: list[dict]) -> dict:
    coords: list[dict] = []
    surfaces: list[str] = []
    highways: list[str] = []
    weighted_grade = 0.0
    total_length = 0.0

    for record in records:
        segment_coords = record["coordinates"]
        if coords and segment_coords:
            if coords[-1] == segment_coords[0]:
                coords.extend(segment_coords[1:])
            else:
                coords.extend(segment_coords)
        else:
            coords.extend(segment_coords)
        surfaces.append(record["surface"])
        highways.append(record["highway"])
        length = float(record["length_m"])
        total_length += length
        weighted_grade += float(record["grade"]) * max(length, 1.0)

    return {
        "path_index": records[0]["path_index"],
        "path_index_end": records[-1].get("path_index_end", records[-1]["path_index"]),
        "coordinates": coords,
        "midpoint": midpoint_coord(coords),
        "length_m": round(total_length, 1),
        "maxspeed": max(int(record["maxspeed"]) for record in records),
        "surface": normalize_tag_value(surfaces, "unknown"),
        "lanes": max(int(record["lanes"]) for record in records),
        "highway": normalize_tag_value(highways, "unclassified"),
        "grade": round(weighted_grade / max(total_length, 1.0), 4),
        "viraj_fun": sum(int(record["viraj_fun"]) for record in records),
        "viraj_tehlike": sum(int(record["viraj_tehlike"]) for record in records),
        "hairpin": sum(int(record["hairpin"]) for record in records),
        "high_risk": any(bool(record["high_risk"]) for record in records),
        "lane_split_m": round(sum(float(record["lane_split_m"]) for record in records), 1),
    }


def build_signal_clusters(
    records: list[dict],
    signal_fn,
    bridge_limit: int = 0,
    bridge_max_length_m: float = 120.0,
) -> list[dict]:
    clusters: list[dict] = []
    active: list[dict] = []
    bridges_used = 0

    def flush() -> None:
        nonlocal active, bridges_used
        if active:
            clusters.append(merge_record_cluster(active))
        active = []
        bridges_used = 0

    for record in records:
        is_signal = bool(signal_fn(record))
        if is_signal:
            active.append(record)
            bridges_used = 0
            continue
        if active and bridges_used < bridge_limit and float(record["length_m"]) <= bridge_max_length_m:
            active.append(record)
            bridges_used += 1
            continue
        flush()

    flush()
    return clusters


def build_keyed_clusters(records: list[dict], key_fn) -> list[dict]:
    clusters: list[dict] = []
    active: list[dict] = []
    active_key: str | None = None

    def flush() -> None:
        nonlocal active, active_key
        if active:
            merged = merge_record_cluster(active)
            merged["cluster_key"] = active_key
            clusters.append(merged)
        active = []
        active_key = None

    for record in records:
        key = key_fn(record)
        if key is None:
            flush()
            continue
        if active and key == active_key:
            active.append(record)
            continue
        flush()
        active = [record]
        active_key = key

    flush()
    return clusters


def path_edge_records(
    graph: nx.MultiDiGraph, nodes: list[int], weight_attr: str
) -> list[dict]:
    records = []
    for idx in range(len(nodes) - 1):
        edge = best_edge_data(graph, nodes[idx], nodes[idx + 1], weight_attr)
        if edge is None:
            continue
        coords = edge_geometry_coords(graph, nodes[idx], nodes[idx + 1], edge)
        records.append(
            {
                "path_index": idx,
                "path_index_end": idx,
                "coordinates": coords,
                "midpoint": midpoint_coord(coords),
                "length_m": round(float(edge.get("length", 0.0) or 0.0), 1),
                "maxspeed": int(edge.get("maxspeed", 0) or 0),
                "surface": normalize_tag_value(edge.get("surface"), "unknown"),
                "lanes": int(edge.get("lanes", 0) or 0),
                "highway": normalize_tag_value(edge.get("highway"), "unclassified"),
                "grade": round(float(edge.get("grade", 0.0) or 0.0), 4),
                "viraj_fun": int(edge.get("viraj_fun_sayisi", 0) or 0),
                "viraj_tehlike": int(edge.get("viraj_tehlike_sayisi", 0) or 0),
                "hairpin": int(edge.get("viraj_hairpin_sayisi", 0) or 0),
                "high_risk": bool(edge.get("yuksek_risk_bolge", False)),
                "lane_split_m": round(float(edge.get("serit_paylasimi_m", 0.0) or 0.0), 1),
            }
        )
    return records


def segment_entry(record: dict, label: str, tone: str) -> dict:
    return {
        "label": label,
        "tone": tone,
        "coordinates": record["coordinates"],
        "midpoint": record["midpoint"],
        "length_m": record["length_m"],
        "maxspeed": record["maxspeed"],
        "surface": record["surface"],
        "lanes": record["lanes"],
        "highway": record["highway"],
        "grade": record["grade"],
        "viraj_fun": record["viraj_fun"],
        "viraj_tehlike": record["viraj_tehlike"],
        "hairpin": record["hairpin"],
        "high_risk": record["high_risk"],
        "lane_split_m": record["lane_split_m"],
    }


def top_records(records: list[dict], key_fn, limit: int = 3) -> list[dict]:
    return sorted(records, key=key_fn, reverse=True)[:limit]


def highway_family_label(highway: str) -> str:
    text = str(highway or "").lower()
    if "motorway" in text or "trunk" in text or "primary" in text:
        return "primary"
    if "secondary" in text:
        return "secondary"
    if "tertiary" in text:
        return "tertiary"
    if "residential" in text:
        return "residential"
    return "urban"


def select_showcase_records(
    records: list[dict],
    key_fn,
    limit: int = 3,
    min_length_m: float = 0.0,
    min_index_gap: int = 0,
    bucket_fn=None,
) -> list[dict]:
    candidates = [record for record in records if record["length_m"] >= min_length_m] or records
    ranked = sorted(candidates, key=key_fn, reverse=True)
    selected: list[dict] = []
    used_buckets: set[str] = set()

    for record in ranked:
        bucket = bucket_fn(record) if bucket_fn else None
        if bucket and bucket in used_buckets:
            continue
        record_start = int(record.get("path_index", 0))
        record_end = int(record.get("path_index_end", record_start))
        if min_index_gap and any(
            not (
                record_end + min_index_gap <= int(chosen.get("path_index", 0))
                or int(chosen.get("path_index_end", chosen.get("path_index", 0))) + min_index_gap <= record_start
            )
            for chosen in selected
        ):
            continue
        selected.append(record)
        if bucket:
            used_buckets.add(bucket)
        if len(selected) >= limit:
            return selected

    for record in ranked:
        if record in selected:
            continue
        selected.append(record)
        if len(selected) >= limit:
            break
    return selected


def speed_segment_label(record: dict) -> str:
    cluster_key = record.get("cluster_key")
    family = highway_family_label(record["highway"])
    if cluster_key == "sprint" or record["maxspeed"] >= 80:
        return "Primary sprint"
    if cluster_key == "connector" or record["maxspeed"] >= 60:
        return "Fast connector"
    if cluster_key == "shortcut" or family == "residential":
        return "Local shortcut"
    if family == "secondary":
        return "Secondary glide"
    return "Urban glide"


def traffic_segment_label(record: dict) -> str:
    cluster_key = record.get("cluster_key")
    if cluster_key == "bypass" or record["lane_split_m"] >= 180:
        return "Lane-share relief"
    if cluster_key == "relief":
        return "Rush release"
    if cluster_key == "rush":
        return "Rush corridor"
    if record["lanes"] >= 4:
        return "Wide-lane bypass"
    return "Pressure pocket"


def shield_segment_label(record: dict) -> str:
    cluster_key = record.get("cluster_key")
    family = highway_family_label(record["highway"])
    if cluster_key == "watch" or record["high_risk"] or record["viraj_tehlike"] > 0:
        return "Watch zone"
    if cluster_key == "neighborhood" or family == "residential":
        return "Calm neighborhood corridor"
    if cluster_key == "arterial" or family == "primary":
        return "Protected arterial link"
    return "Calm connector"


def curvature_segment_label(record: dict) -> str:
    if record["hairpin"] > 0:
        return "Hairpin sequence"
    if record["viraj_fun"] >= 5:
        return "Apex ribbon"
    if record["viraj_fun"] >= 3:
        return "Sweeper set"
    if record["viraj_tehlike"] > 0:
        return "Technical bend"
    return "Curvy section"


def elevation_segment_label(record: dict) -> str:
    cluster_key = record.get("cluster_key")
    grade = float(record["grade"])
    length_m = float(record["length_m"])
    if cluster_key == "steep-climb" or grade >= 0.05:
        return "Summit wall" if length_m >= 220 else "Steep climb"
    if cluster_key == "climb" or grade >= 0.02:
        return "Cresting climb" if length_m >= 240 else "Climb ramp"
    if cluster_key == "steep-descent" or grade <= -0.05:
        return "Brake-side descent" if length_m >= 190 else "Sharp descent"
    return "Coast-side drop" if length_m >= 240 else "Rolling descent"


def build_feature_overlays(
    graph: nx.MultiDiGraph,
    result: dict,
    selected_paths_by_mode: dict[str, list[int]],
) -> dict:
    standard_records = path_edge_records(
        graph, selected_paths_by_mode.get("standart", []), weight_attr=mode_weight_attr("standart")
    )
    curvy_records = path_edge_records(
        graph, selected_paths_by_mode.get("viraj_keyfi", []), weight_attr=mode_weight_attr("viraj_keyfi")
    )
    safe_records = path_edge_records(
        graph, selected_paths_by_mode.get("guvenli", []), weight_attr=mode_weight_attr("guvenli")
    )

    return {
        "speed": {
            "mode": "standart",
            "segments": [
                segment_entry(
                    record,
                    label=speed_segment_label(record),
                    tone="express" if record.get("cluster_key") == "sprint" or record["maxspeed"] >= 70 else "connector",
                )
                for record in select_showcase_records(
                    build_keyed_clusters(
                        standard_records,
                        key_fn=lambda item: (
                            "sprint"
                            if item["maxspeed"] >= 80 or item["lanes"] >= 4
                            else "connector"
                            if item["maxspeed"] >= 60 or highway_family_label(item["highway"]) in {"primary", "secondary"}
                            else "shortcut"
                            if highway_family_label(item["highway"]) == "residential"
                            else "urban"
                            if item["length_m"] >= 70
                            else None
                        ),
                    ) or standard_records,
                    key_fn=lambda item: item["maxspeed"] * max(item["length_m"], 1.0) + item["lanes"] * 45.0 + item["length_m"] * 0.4,
                    min_length_m=170.0,
                    min_index_gap=6,
                    bucket_fn=lambda item: str(item.get("cluster_key") or f"{highway_family_label(item['highway'])}:{item['maxspeed'] // 10}"),
                )
            ],
            "markers": [
                {"label": result["origin_label"], "kind": "origin", **result["origin"]},
                {"label": result["destination_label"], "kind": "destination", **result["destination"]},
            ],
        },
        "traffic": {
            "mode": "standart",
            "baseline_route": result.get("google_route", []),
            "segments": [
                segment_entry(
                    record,
                    label=traffic_segment_label(record),
                    tone="relief" if record.get("cluster_key") in {"bypass", "relief"} or record["lane_split_m"] >= 180 else "pressure",
                )
                for record in select_showcase_records(
                    build_keyed_clusters(
                        standard_records,
                        key_fn=lambda item: (
                            "bypass"
                            if item["lane_split_m"] >= 180 or item["lanes"] >= 4
                            else "relief"
                            if item["lane_split_m"] >= 110
                            else "rush"
                            if highway_family_label(item["highway"]) in {"primary", "secondary"}
                            else "pressure"
                            if item["length_m"] >= 80
                            else None
                        ),
                    ) or standard_records,
                    key_fn=lambda item: item["lane_split_m"] * 2.2 + item["lanes"] * 26.0 + item["length_m"] * 0.65,
                    min_length_m=170.0,
                    min_index_gap=6,
                    bucket_fn=lambda item: str(item.get("cluster_key") or highway_family_label(item["highway"])),
                )
            ],
        },
        "shield": {
            "mode": "guvenli",
            "segments": [
                segment_entry(
                    record,
                    label=shield_segment_label(record),
                    tone="watch" if record.get("cluster_key") == "watch" or record["high_risk"] or record["viraj_tehlike"] > 0 else "safe",
                )
                for record in select_showcase_records(
                    build_keyed_clusters(
                        [r for r in safe_records if not r["high_risk"] and r["viraj_tehlike"] == 0] or safe_records,
                        key_fn=lambda item: (
                            "watch"
                            if item["high_risk"] or item["viraj_tehlike"] > 0
                            else "neighborhood"
                            if highway_family_label(item["highway"]) == "residential"
                            else "arterial"
                            if highway_family_label(item["highway"]) == "primary"
                            else "connector"
                        ),
                    ) or safe_records,
                    key_fn=lambda item: item["length_m"] * 1.1 - item["viraj_tehlike"] * 80.0 + item["lanes"] * 12.0,
                    min_length_m=170.0,
                    min_index_gap=6,
                    bucket_fn=lambda item: str(item.get("cluster_key") or highway_family_label(item["highway"])),
                )
            ],
        },
        "curvature": {
            "mode": "viraj_keyfi",
            "segments": [
                segment_entry(
                    record,
                    label=curvature_segment_label(record),
                    tone="hairpin" if record["hairpin"] > 0 else "fun" if record["viraj_fun"] > 0 else "danger",
                )
                for record in select_showcase_records(
                    build_signal_clusters(
                        curvy_records,
                        signal_fn=lambda item: item["viraj_fun"] > 0 or item["viraj_tehlike"] > 0 or item["hairpin"] > 0,
                        bridge_limit=1,
                        bridge_max_length_m=145.0,
                    ) or curvy_records,
                    key_fn=lambda item: item["viraj_fun"] * 180.0 + item["viraj_tehlike"] * 140.0 + item["hairpin"] * 260.0 + item["length_m"] * 1.2,
                    min_length_m=120.0,
                    min_index_gap=6,
                    bucket_fn=lambda item: "hairpin" if item["hairpin"] > 0 else ("apex" if item["viraj_fun"] >= 5 else "sweeper"),
                )
            ],
        },
        "elevation": {
            "mode": "viraj_keyfi",
            "segments": [
                segment_entry(
                    record,
                    label=elevation_segment_label(record),
                    tone="climb" if record["grade"] >= 0 else "descent",
                )
                for record in select_showcase_records(
                    build_keyed_clusters(
                        curvy_records or standard_records,
                        key_fn=lambda item: (
                            "steep-climb"
                            if item["grade"] >= 0.05
                            else "climb"
                            if item["grade"] >= 0.02
                            else "steep-descent"
                            if item["grade"] <= -0.05
                            else "descent"
                            if item["grade"] <= -0.015
                            else None
                        ),
                    ) or (curvy_records or standard_records),
                    key_fn=lambda item: abs(item["grade"]) * max(item["length_m"], 1.0) + item["length_m"] * 0.2,
                    min_length_m=150.0,
                    min_index_gap=6,
                    bucket_fn=lambda item: str(item.get("cluster_key") or ("climb" if item["grade"] >= 0 else "descent")),
                )
            ],
        },
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
) -> tuple[dict, list] | None:
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

    for candidate in itertools.islice(candidates, max_candidates):
        summary = summarize_path(graph, candidate, weight_attr=weight_attr)
        if summary["toplam_sure_s"] > float(base_time_s) * max_time_multiplier:
            continue

        fun_count = int(summary["viraj_fun_sayisi"])
        if fun_count >= int(min_fun_count):
            return summary, list(candidate)
        if fun_count > best_fun:
            best_fun = fun_count
            best_summary = summary
            best_nodes = list(candidate)

    if best_summary is None or best_nodes is None:
        return None
    return best_summary, best_nodes


def main() -> None:
    print(f"Graf olusturuluyor: {PLACE}")
    graph = motomap_graf_olustur(PLACE)
    graph = add_travel_time_to_graph(graph)

    origin_node = ox.nearest_nodes(graph, ORIGIN[1], ORIGIN[0])
    destination_node = ox.nearest_nodes(graph, DESTINATION[1], DESTINATION[0])

    origin_actual = {
        "lat": graph.nodes[origin_node]["y"],
        "lng": graph.nodes[origin_node]["x"],
    }
    destination_actual = {
        "lat": graph.nodes[destination_node]["y"],
        "lng": graph.nodes[destination_node]["x"],
    }

    print(f"Baslangic: {origin_actual}")
    print(f"Varis: {destination_actual}")

    print("Google rotasi aliniyor...")
    google_data = fetch_google_route(
        origin_actual, destination_actual, GOOGLE_MAPS_API_KEY
    )
    print(
        f"  -> {len(google_data['coordinates'])} nokta, "
        f"{google_data['stats'].get('mesafe_text', '?')}, "
        f"{google_data['stats'].get('sure_text', '?')}"
    )

    result = {
        "origin": origin_actual,
        "destination": destination_actual,
        "origin_label": "Kadikoy Iskele",
        "destination_label": "Kalamis Parki",
        "google_route": google_data["coordinates"],
        "google_stats": google_data["stats"],
        "modes": {},
    }

    selected_paths: list[list] = []
    selected_paths_by_mode: dict[str, list] = {}

    for mode in MODES:
        print(f"Rota hesaplaniyor: {mode}")
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
                    print(
                        f"  -> Diversified fallback secildi ({len(mode_nodes)} nokta, "
                        f"overlap {max_current_overlap:.2f})"
                    )
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
                        print(
                            f"  -> Relaxed diversity fallback secildi ({len(mode_nodes)} nokta, "
                            f"overlap hedefi gevsetildi)"
                        )

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
                    print(
                        f"  -> Fun fallback secildi (viraj_fun: {current_fun} -> "
                        f"{selected['viraj_fun_sayisi']}, hedef >= {standard_fun})"
                    )

        selected_paths.append(mode_nodes)
        selected_paths_by_mode[mode] = mode_nodes
        coords = nodes_to_coords(graph, mode_nodes)

        result["modes"][mode] = {
            "coordinates": coords,
            "stats": {
                "mesafe_m": round(selected["toplam_mesafe_m"], 1),
                "sure_s": round(selected["toplam_sure_s"], 1),
                "viraj_fun": selected["viraj_fun_sayisi"],
                "viraj_tehlike": selected["viraj_tehlike_sayisi"],
                "yuksek_risk": selected["yuksek_risk_segment_sayisi"],
                "serit_paylasimi": round(selected.get("serit_paylasimi_m", 0.0), 1),
                "ortalama_egim": round(selected["ortalama_egim_orani"], 4),
                "ucretli": selected["ucretli_yol_iceriyor"],
            },
        }
        print(
            f"  -> {len(coords)} nokta, {selected['toplam_mesafe_m']:.0f}m, "
            f"{selected['toplam_sure_s']:.0f}s"
        )

    result["feature_overlays"] = build_feature_overlays(
        graph,
        result,
        selected_paths_by_mode=selected_paths_by_mode,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "motomap_route.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nRota JSON kaydedildi: {output_path}")


if __name__ == "__main__":
    main()
