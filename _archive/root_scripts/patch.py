import sys

# 1. Patch api/services/route_preview.py
with open('api/services/route_preview.py', 'r', encoding='utf-8') as f:
    text = f.read()

imports_old = '''import json
import random
from copy import deepcopy
from pathlib import Path
from typing import Any'''

imports_new = '''import json
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
_GRAPH_LOCK = threading.Lock()'''

text = text.replace(imports_old, imports_new)

old_get_payload = '''    def get_route_payload(self) -> dict[str, Any]:
        base_route = deepcopy(DEMO_ROUTE)
        # Random endpoints in Istanbul'''

new_get_payload = '''    def get_route_payload(self) -> dict[str, Any]:
        global _CACHED_GRAPH, _GRAPH_LOCK
        
        if MOTOMAP_AVAILABLE:
            try:
                with _GRAPH_LOCK:
                    if _CACHED_GRAPH is None:
                        print("[MotoMap] Kadikoy grafigi ilk kez indiriliyor, lutfen bekleyin...")
                        g = motomap_graf_olustur("Kadikoy, Istanbul, Turkey")
                        g = add_travel_time_to_graph(g)
                        g = ox.utils_graph.get_largest_component(g, strongly=True)
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
        # Random endpoints in Istanbul'''

text = text.replace(old_get_payload, new_get_payload)

with open('api/services/route_preview.py', 'w', encoding='utf-8') as f:
    f.write(text)

# 2. Patch api/routes/route_preview.py
with open('api/routes/route_preview.py', 'r', encoding='utf-8') as f:
    text2 = f.read()

route_old = '''async def get_route_preview():
    svc = RoutePreviewService()
    try:
        return RoutePreviewResponse.model_validate(svc.get_route_payload())'''

route_new = '''from fastapi.concurrency import run_in_threadpool

@router.get("", response_model=RoutePreviewResponse)
async def get_route_preview():
    svc = RoutePreviewService()
    try:
        payload = await run_in_threadpool(svc.get_route_payload)
        return RoutePreviewResponse.model_validate(payload)'''

text2 = text2.replace('''@router.get("", response_model=RoutePreviewResponse)\n''' + route_old, route_new)

with open('api/routes/route_preview.py', 'w', encoding='utf-8') as f:
    f.write(text2)

print("Patch applied successfully.")
