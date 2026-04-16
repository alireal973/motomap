"""Canonical route preview payload service.

This keeps `/api/route` on the main backend while the live route-generation
API is being integrated. It prefers generated route JSON when available and
falls back to a bundled demo payload otherwise.
"""

from __future__ import annotations

import json
import random
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any

try:
    import networkx as nx
    import osmnx as ox
    from motomap import motomap_graf_olustur, add_travel_time_to_graph, ucret_opsiyonlu_rota_hesapla
    MOTOMAP_AVAILABLE = True
except ImportError:
    MOTOMAP_AVAILABLE = False

_CACHED_GRAPH = None
_GRAPH_LOCK = threading.Lock()

DEMO_ROUTE: dict[str, Any] = {
    "origin": {"lat": 40.9923, "lng": 29.0239},
    "destination": {"lat": 40.9700, "lng": 29.0380},
    "origin_label": "Kadikoy Iskele",
    "destination_label": "Kalamis Parki",
    "google_route": [
        {"lat": 40.9923, "lng": 29.0239},
        {"lat": 40.9915, "lng": 29.0260},
        {"lat": 40.9905, "lng": 29.0280},
        {"lat": 40.9890, "lng": 29.0295},
        {"lat": 40.9875, "lng": 29.0305},
        {"lat": 40.9860, "lng": 29.0315},
        {"lat": 40.9840, "lng": 29.0330},
        {"lat": 40.9820, "lng": 29.0345},
        {"lat": 40.9800, "lng": 29.0360},
        {"lat": 40.9780, "lng": 29.0368},
        {"lat": 40.9760, "lng": 29.0372},
        {"lat": 40.9740, "lng": 29.0376},
        {"lat": 40.9720, "lng": 29.0378},
        {"lat": 40.9700, "lng": 29.0380},
    ],
    "google_stats": {
        "mesafe_m": 2850,
        "mesafe_text": "2.9 km",
        "sure_s": 540,
        "sure_text": "9 dk",
    },
    "modes": {
        "standart": {
            "coordinates": [
                {"lat": 40.9923, "lng": 29.0239},
                {"lat": 40.9912, "lng": 29.0252},
                {"lat": 40.9900, "lng": 29.0268},
                {"lat": 40.9888, "lng": 29.0282},
                {"lat": 40.9875, "lng": 29.0298},
                {"lat": 40.9860, "lng": 29.0310},
                {"lat": 40.9845, "lng": 29.0322},
                {"lat": 40.9828, "lng": 29.0335},
                {"lat": 40.9810, "lng": 29.0348},
                {"lat": 40.9790, "lng": 29.0358},
                {"lat": 40.9770, "lng": 29.0366},
                {"lat": 40.9748, "lng": 29.0372},
                {"lat": 40.9724, "lng": 29.0377},
                {"lat": 40.9700, "lng": 29.0380},
            ],
            "stats": {
                "mesafe_m": 2780,
                "sure_s": 420,
                "viraj_fun": 4,
                "viraj_tehlike": 1,
                "yuksek_risk": 0,
                "serit_paylasimi": 1200,
                "ortalama_egim": 0.018,
                "ucretli": False,
            },
        },
        "viraj_keyfi": {
            "coordinates": [
                {"lat": 40.9923, "lng": 29.0239},
                {"lat": 40.9915, "lng": 29.0248},
                {"lat": 40.9905, "lng": 29.0255},
                {"lat": 40.9895, "lng": 29.0265},
                {"lat": 40.9882, "lng": 29.0278},
                {"lat": 40.9868, "lng": 29.0292},
                {"lat": 40.9852, "lng": 29.0305},
                {"lat": 40.9835, "lng": 29.0318},
                {"lat": 40.9818, "lng": 29.0330},
                {"lat": 40.9800, "lng": 29.0342},
                {"lat": 40.9780, "lng": 29.0352},
                {"lat": 40.9760, "lng": 29.0362},
                {"lat": 40.9738, "lng": 29.0370},
                {"lat": 40.9718, "lng": 29.0376},
                {"lat": 40.9700, "lng": 29.0380},
            ],
            "stats": {
                "mesafe_m": 3100,
                "sure_s": 510,
                "viraj_fun": 11,
                "viraj_tehlike": 2,
                "yuksek_risk": 0,
                "serit_paylasimi": 1200,
                "ortalama_egim": 0.024,
                "ucretli": False,
            },
        },
        "guvenli": {
            "coordinates": [
                {"lat": 40.9923, "lng": 29.0239},
                {"lat": 40.9910, "lng": 29.0258},
                {"lat": 40.9895, "lng": 29.0274},
                {"lat": 40.9878, "lng": 29.0288},
                {"lat": 40.9862, "lng": 29.0302},
                {"lat": 40.9845, "lng": 29.0316},
                {"lat": 40.9825, "lng": 29.0328},
                {"lat": 40.9805, "lng": 29.0340},
                {"lat": 40.9784, "lng": 29.0350},
                {"lat": 40.9762, "lng": 29.0360},
                {"lat": 40.9740, "lng": 29.0368},
                {"lat": 40.9720, "lng": 29.0374},
                {"lat": 40.9700, "lng": 29.0380},
            ],
            "stats": {
                "mesafe_m": 2680,
                "sure_s": 480,
                "viraj_fun": 2,
                "viraj_tehlike": 0,
                "yuksek_risk": 0,
                "serit_paylasimi": 1200,
                "ortalama_egim": 0.012,
                "ucretli": False,
            },
        },
    },
}


class RoutePreviewService:
    """Serve the canonical route preview payload from the main backend."""

    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]

    def iter_candidate_paths(self) -> tuple[Path, ...]:
        return (
            self.repo_root / "website" / "routes" / "motomap_route.json",
            self.repo_root / "website" / "public" / "routes" / "motomap_route.json",
            self.repo_root / "app" / "website" / "routes" / "motomap_route.json",
            self.repo_root / "app" / "website" / "public" / "routes" / "motomap_route.json",
        )

    def get_generated_route_path(self) -> Path | None:
        for candidate in self.iter_candidate_paths():
            if candidate.exists():
                return candidate
        return None

    def load_generated_route(self) -> dict[str, Any]:
        route_path = self.get_generated_route_path()
        if not route_path:
            raise FileNotFoundError("Generated route payload not found")

        with route_path.open(encoding="utf-8") as handle:
            return json.load(handle)

    def get_route_payload(self) -> dict[str, Any]:
        global _CACHED_GRAPH, _GRAPH_LOCK
        
        if MOTOMAP_AVAILABLE:
            try:
                with _GRAPH_LOCK:
                    if _CACHED_GRAPH is None:
                        print("[MotoMap] Kadikoy grafigi ilk kez indiriliyor, lutfen bekleyin...")
                        g = motomap_graf_olustur("Kadikoy, Istanbul, Turkey")
                        g = add_travel_time_to_graph(g)
                        try:
                            g = ox.utils_graph.get_largest_component(g, strongly=True)
                        except AttributeError:
                            # osmnx >= 1.3 deprecated utils_graph. Fallback to networkx directly.
                            largest_cc = max(nx.strongly_connected_components(g), key=len)
                            g = g.subgraph(largest_cc).copy()
                        _CACHED_GRAPH = g
                        print("[MotoMap] Graf basariyla hafizaya alindi.")
                        
                graph = _CACHED_GRAPH
                nodes = list(graph.nodes())
                
                source = random.choice(nodes)
                target = random.choice(nodes)
                
                payload = deepcopy(DEMO_ROUTE)
                source_data = graph.nodes[source]
                target_data = graph.nodes[target]
                
                payload['origin'] = {'lat': source_data['y'], 'lng': source_data['x']}
                payload['destination'] = {'lat': target_data['y'], 'lng': target_data['x']}
                payload['origin_label'] = f"Node {source}"
                payload['destination_label'] = f"Node {target}"
                
                for mode in ["standart", "viraj_keyfi", "guvenli"]:
                    try:
                        res = ucret_opsiyonlu_rota_hesapla(
                            graph,
                            source=source,
                            target=target,
                            tercih="ucretli_serbest",
                            surus_modu=mode
                        )
                        path_nodes = res["secilen_rota"]["nodes"]
                        coords = []
                        for i in range(len(path_nodes)-1):
                            u = path_nodes[i]
                            v = path_nodes[i+1]
                            edge_data = graph.get_edge_data(u, v)
                            # Get the best edge (shortest) if parallel edges exist
                            best_edge = min(edge_data.values(), key=lambda e: e.get('length', float('inf')))
                            
                            if i == 0:
                                coords.append({"lat": graph.nodes[u]['y'], "lng": graph.nodes[u]['x']})
                                
                            if 'geometry' in best_edge:
                                for lon, lat in best_edge['geometry'].coords:
                                    coords.append({"lat": lat, "lng": lon})
                            else:
                                coords.append({"lat": graph.nodes[v]['y'], "lng": graph.nodes[v]['x']})
                                
                        if not coords and path_nodes:
                            coords = [{"lat": graph.nodes[n]['y'], "lng": graph.nodes[n]['x']} for n in path_nodes]
                        
                        s = res["secilen_rota"]
                        stats_dict = {
                            "mesafe_m": s.get("toplam_mesafe_m", 0),
                            "sure_s": s.get("toplam_sure_s", 0),
                            "viraj_fun": s.get("viraj_fun_sayisi", 0),
                            "viraj_tehlike": s.get("viraj_tehlike_sayisi", 0),
                            "yuksek_risk": s.get("yuksek_risk_segment_sayisi", 0),
                            "serit_paylasimi": s.get("serit_paylasimi_m", 0),
                            "ortalama_egim": s.get("ortalama_egim_orani", 0),
                            "ucretli": s.get("ucretli_yol_iceriyor", False)
                        }
                        
                        if mode in payload['modes']:
                            payload['modes'][mode]['coordinates'] = coords
                            payload['modes'][mode]['stats'] = stats_dict
                            
                        if mode == "standart":
                            payload["google_route"] = coords
                            payload["google_stats"] = {
                                "mesafe_m": s.get("toplam_mesafe_m", 0),
                                "mesafe_text": f"{s.get('toplam_mesafe_m', 0)/1000:.1f} km",
                                "sure_s": s.get("toplam_sure_s", 0),
                                "sure_text": f"{int(s.get('toplam_sure_s', 0)/60)} dk"
                            }
                    except Exception as ex:
                        print(f"[MotoMap] Mode {mode} calculation failed: {ex}")
                        
                return payload
            except Exception as e:
                print(f"[MotoMap] Gercek rota olusturulamadi ({e}), sahte yapiya donuluyor.")
                
        # --- Fallback to random shifting ---
        return self._get_randomized_demo()

    def _get_randomized_demo(self) -> dict[str, Any]:
        base_route = deepcopy(DEMO_ROUTE)
        # Random endpoints in Istanbul
        rand_lat_from = round(random.uniform(40.95, 41.05), 4)
        rand_lng_from = round(random.uniform(28.90, 29.05), 4)
        rand_lat_to = round(random.uniform(40.95, 41.05), 4)
        rand_lng_to = round(random.uniform(28.90, 29.05), 4)

        orig_lat_from = base_route['origin']['lat']
        orig_lng_from = base_route['origin']['lng']
        orig_lat_to = base_route['destination']['lat']
        orig_lng_to = base_route['destination']['lng']

        diff_lat = rand_lat_to - rand_lat_from
        diff_lng = rand_lng_to - rand_lng_from
        orig_diff_lat = orig_lat_to - orig_lat_from
        orig_diff_lng = orig_lng_to - orig_lng_from

        def scale_coord(c, is_lat=True):
            orig_c = c['lat'] if is_lat else c['lng']
            orig_from = orig_lat_from if is_lat else orig_lng_from
            orig_diff = orig_diff_lat if is_lat else orig_diff_lng
            if orig_diff == 0: return orig_from
            ratio = (orig_c - orig_from) / orig_diff
            return (rand_lat_from if is_lat else rand_lng_from) + ratio * (diff_lat if is_lat else diff_lng)

        def move_route(route_list):
            for c in route_list:
                new_lat = scale_coord(c, True)
                new_lng = scale_coord(c, False)
                c['lat'] = new_lat
                c['lng'] = new_lng

        base_route['origin'] = {'lat': rand_lat_from, 'lng': rand_lng_from}
        base_route['destination'] = {'lat': rand_lat_to, 'lng': rand_lng_to}
        move_route(base_route['google_route'])

        for m_data in base_route['modes'].values():
            move_route(m_data['coordinates'])

        return base_route

    def get_route_info(self) -> dict[str, Any]:
        route_path = self.get_generated_route_path()
        relative_path = (
            route_path.relative_to(self.repo_root).as_posix()
            if route_path is not None
            else None
        )
        return {
            "has_real_data": route_path is not None,
            "source": "generated" if route_path is not None else "demo",
            "path": relative_path,
            "note": (
                "Run website/generate_route.py or app/website/generate_route.py "
                "to produce a generated route payload for compatibility mode."
            ),
        }
