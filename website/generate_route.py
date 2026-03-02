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
from motomap.router import (
    TRAVEL_TIME_ATTR,
    add_travel_time_to_graph,
    is_toll_edge,
    ucret_opsiyonlu_rota_hesapla,
)

# --- Configuration ---
PLACE = "Kadıköy, İstanbul, Turkey"
ORIGIN = (40.9923, 29.0239)  # Kadıköy İskele
DESTINATION = (40.9700, 29.0380)  # Kalamış Parkı
MODES = ["standart", "viraj_keyfi", "guvenli"]
OUTPUT_DIR = Path(__file__).resolve().parent / "routes"


def mode_weight_attr(mode: str) -> str:
    return {
        "standart": TRAVEL_TIME_ATTR,
        "viraj_keyfi": "route_cost_viraj_keyfi_s",
        "guvenli": "route_cost_guvenli_s",
    }[mode]


def nodes_to_coords(graph: nx.MultiDiGraph, node_ids: list) -> list[dict]:
    """Convert node IDs to [{lat, lng}, ...]."""
    return [{"lat": graph.nodes[nid]["y"], "lng": graph.nodes[nid]["x"]} for nid in node_ids]


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
        lat += (~(result >> 1) if (result & 1) else (result >> 1))

        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        lng += (~(result >> 1) if (result & 1) else (result >> 1))

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
        if all(edge_overlap_ratio(candidate, used) <= max_overlap for used in used_paths):
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


def best_edge_data(graph: nx.MultiDiGraph, u: int, v: int, weight_attr: str) -> dict | None:
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
    grades = []

    for idx in range(len(nodes) - 1):
        edge = best_edge_data(graph, nodes[idx], nodes[idx + 1], weight_attr=weight_attr)
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

    origin_actual = {"lat": graph.nodes[origin_node]["y"], "lng": graph.nodes[origin_node]["x"]}
    destination_actual = {
        "lat": graph.nodes[destination_node]["y"],
        "lng": graph.nodes[destination_node]["x"],
    }

    print(f"Baslangic: {origin_actual}")
    print(f"Varis: {destination_actual}")

    print("Google rotasi aliniyor...")
    google_data = fetch_google_route(origin_actual, destination_actual, GOOGLE_MAPS_API_KEY)
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
            max_current_overlap = max(edge_overlap_ratio(mode_nodes, p) for p in selected_paths)
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
                        selected = summarize_path(graph, relaxed_nodes, weight_attr=mode_weight)
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
        coords = nodes_to_coords(graph, mode_nodes)

        result["modes"][mode] = {
            "coordinates": coords,
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
        print(
            f"  -> {len(coords)} nokta, {selected['toplam_mesafe_m']:.0f}m, "
            f"{selected['toplam_sure_s']:.0f}s"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "motomap_route.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nRota JSON kaydedildi: {output_path}")


if __name__ == "__main__":
    main()
