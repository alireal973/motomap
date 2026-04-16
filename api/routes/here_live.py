"""HERE live traffic routes for Turkey map preview."""

from __future__ import annotations

import os
from datetime import datetime
from statistics import mean
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

load_dotenv()

router = APIRouter(prefix="/api/here", tags=["here-live"])

HERE_FLOW_URL = "https://data.traffic.hereapi.com/v7/flow"
DEFAULT_TURKEY_BBOX = "35.70,25.60,42.20,44.90"
REQUEST_TIMEOUT_S = 15.0


def _get_here_api_key() -> str:
    api_key = os.getenv("HERE_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="HERE_API_KEY is not configured in environment",
        )
    return api_key


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _compute_traffic_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    speeds: list[float] = []
    free_speeds: list[float] = []
    jam_factors: list[float] = []

    for item in results:
        current_flow = item.get("currentFlow", {})
        speed = _safe_float(current_flow.get("speed"))
        free_speed = _safe_float(current_flow.get("freeFlow"))
        jam_factor = _safe_float(current_flow.get("jamFactor"))

        if speed is not None:
            speeds.append(speed)
        if free_speed is not None:
            free_speeds.append(free_speed)
        if jam_factor is not None:
            jam_factors.append(jam_factor)

    avg_speed = mean(speeds) if speeds else 0.0
    avg_free_speed = mean(free_speeds) if free_speeds else 0.0
    avg_jam = mean(jam_factors) if jam_factors else 0.0

    # jamFactor is typically in 0..10. Convert to percentage scale for UI.
    congestion_pct = max(0.0, min(100.0, avg_jam * 10.0))

    # Speed-drop proxy for "traffic volume effect" when direct volume is absent.
    speed_drop_pct = 0.0
    if avg_free_speed > 0:
        speed_drop_pct = max(
            0.0,
            min(100.0, (1.0 - (avg_speed / avg_free_speed)) * 100.0),
        )

    return {
        "segment_count": len(results),
        "avg_speed_kmh": round(avg_speed, 2),
        "avg_free_flow_speed_kmh": round(avg_free_speed, 2),
        "avg_jam_factor": round(avg_jam, 2),
        "congestion_pct": round(congestion_pct, 2),
        "traffic_volume_proxy_pct": round(speed_drop_pct, 2),
    }


def _parse_bbox(bbox: str) -> tuple[float, float, float, float]:
    parts = [p.strip() for p in bbox.split(",")]
    if len(parts) != 4:
        raise HTTPException(status_code=400, detail="bbox must be South,West,North,East")

    try:
        south, west, north, east = (float(p) for p in parts)
    except ValueError:
        raise HTTPException(status_code=400, detail="bbox contains non-numeric values")

    if south >= north or west >= east:
        raise HTTPException(status_code=400, detail="bbox bounds are invalid")
    return south, west, north, east


async def _fetch_flow_results(
    client: httpx.AsyncClient,
    api_key: str,
    bbox_tuple: tuple[float, float, float, float],
) -> list[dict[str, Any]]:
    south, west, north, east = bbox_tuple
    # HERE API v7 requires bbox format: west,south,east,north
    here_bbox = f"{west:.6f},{south:.6f},{east:.6f},{north:.6f}"
    params = {
        "apiKey": api_key,
        "in": f"bbox:{here_bbox}",
        "locationReferencing": "shape",
    }
    response = await client.get(HERE_FLOW_URL, params=params)
    response.raise_for_status()
    payload = response.json()
    return payload.get("results", [])


def _split_bbox(bbox: tuple[float, float, float, float], grid: int = 4) -> list[tuple[float, float, float, float]]:
    south, west, north, east = bbox
    lat_step = (north - south) / grid
    lon_step = (east - west) / grid

    parts: list[tuple[float, float, float, float]] = []
    for r in range(grid):
        tile_south = south + r * lat_step
        tile_north = south + (r + 1) * lat_step
        for c in range(grid):
            tile_west = west + c * lon_step
            tile_east = west + (c + 1) * lon_step
            parts.append((tile_south, tile_west, tile_north, tile_east))
    return parts


@router.get("/traffic/flow-summary")
async def get_traffic_flow_summary(
    bbox: str = Query(
        default=DEFAULT_TURKEY_BBOX,
        description="South,West,North,East bounding box",
    ),
):
    api_key = _get_here_api_key()
    parsed_bbox = _parse_bbox(bbox)

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
            try:
                results = await _fetch_flow_results(client, api_key, parsed_bbox)
                used_tiling = False
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code != 400:
                    raise
                # Large areas can be rejected by HERE flow API; tile and aggregate.
                all_results: list[dict[str, Any]] = []
                for tile_bbox in _split_bbox(parsed_bbox, grid=4):
                    try:
                        tile_results = await _fetch_flow_results(client, api_key, tile_bbox)
                        all_results.extend(tile_results)
                    except httpx.HTTPStatusError:
                        continue
                results = all_results
                used_tiling = True
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"HERE traffic API error: {exc.response.status_code}",
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"HERE traffic request failed: {exc}")

    summary = _compute_traffic_summary(results)

    now = datetime.now()
    return {
        "timestamp_local": now.strftime("%H:%M:%S"),
        "timestamp_iso": now.isoformat(),
        "bbox": bbox,
        "used_tiling": used_tiling,
        "summary": summary,
    }


@router.get("/live-map", response_class=HTMLResponse)
async def get_live_map() -> str:
    api_key = _get_here_api_key()

    return f"""<!doctype html>
<html lang=\"tr\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>MotoMap HERE Live Traffic - Turkey</title>
  <link rel=\"stylesheet\" href=\"https://js.api.here.com/v3/3.1/mapsjs-ui.css\" />
  <style>
    :root {{
      --bg: #0a1a2f;
      --panel: rgba(9, 22, 41, 0.88);
      --text: #f7fbff;
      --muted: #9fb4c8;
      --accent: #00e0b8;
      --line: rgba(159, 180, 200, 0.28);
    }}

    html, body {{
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      font-family: "Segoe UI", "Tahoma", sans-serif;
      color: var(--text);
      background: radial-gradient(circle at 20% 20%, #14335a, #071123 55%);
    }}

    #map {{
      width: 100%;
      height: 100%;
    }}

    #panel {{
      position: absolute;
      top: 14px;
      left: 14px;
      min-width: 320px;
      max-width: 420px;
      padding: 14px 16px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: var(--panel);
      backdrop-filter: blur(8px);
      box-shadow: 0 14px 40px rgba(0, 0, 0, 0.35);
      z-index: 10;
    }}

    .title {{
      font-size: 17px;
      font-weight: 700;
      margin-bottom: 4px;
      letter-spacing: 0.2px;
    }}

    .clock {{
      font-size: 20px;
      color: var(--accent);
      margin-bottom: 10px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }}

    .meta {{
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 10px;
      line-height: 1.4;
    }}

    .stat-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}

    .stat {{
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 9px;
      background: rgba(7, 16, 30, 0.7);
    }}

    .label {{
      color: var(--muted);
      font-size: 11px;
      margin-bottom: 4px;
    }}

    .value {{
      font-size: 17px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }}

    .footnote {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 11px;
      line-height: 1.35;
    }}

    .presets {{
      display: flex;
      gap: 6px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }}

    .preset-btn {{
      background: rgba(0, 224, 184, 0.15);
      border: 1px solid rgba(0, 224, 184, 0.4);
      color: var(--accent);
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .preset-btn:hover {{
      background: rgba(0, 224, 184, 0.3);
    }}
    
    .route-section {{
      margin-top: 16px;
      border-top: 1px dashed var(--line);
      padding-top: 12px;
    }}

    .debug-box {{
      margin-top: 12px;
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid rgba(255, 60, 60, 0.3);
      border-radius: 8px;
      padding: 8px;
      font-family: monospace;
      font-size: 10px;
      color: #ff8e8e;
      white-space: pre-wrap;
      word-wrap: break-word;
      max-height: 120px;
      overflow-y: auto;
    }}
    .debug-box .log {{
      margin-bottom: 4px;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      padding-bottom: 2px;
    }}
  </style>
</head>
<body>
  <div id=\"map\"></div>
  <div id=\"panel\">
    <div class=\"title\">MotoMap - İstanbul Canlı Trafik</div>
    <div class=\"clock\" id=\"clock\">--:--:--</div>
    
    <div class=\"presets\">
      <button class=\"preset-btn\" onclick=\"goToPreset(41.0082, 28.9784, 11)\">İstanbul'a Odaklan</button>
    </div>

    <div class=\"meta\">Anlik gorunen harita alanindan trafik akisi cekiliyor.</div>

    <div class=\"stat-grid\">
      <div class=\"stat\"><div class=\"label\">Segment</div><div class=\"value\" id=\"segmentCount\">-</div></div>
      <div class=\"stat\"><div class=\"label\">Ortalama Hiz</div><div class=\"value\" id=\"avgSpeed\">-</div></div>
      <div class=\"stat\"><div class=\"label\">Serbest Akis Hiz</div><div class=\"value\" id=\"avgFreeSpeed\">-</div></div>
      <div class=\"stat\"><div class=\"label\">Jam Factor</div><div class=\"value\" id=\"jamFactor\">-</div></div>
      <div class=\"stat\"><div class=\"label\">Yogunluk %</div><div class=\"value\" id=\"congestion\">-</div></div>
      <div class=\"stat\"><div class=\"label\">Volume Proxy %</div><div class=\"value\" id=\"volumeProxy\">-</div></div>
    </div>
    
    <div class=\"route-section\">
      <div class=\"title\" style=\"font-size: 14px;\">Aktif Rota Algoritması</div>
      <div class=\"meta\" id=\"routeStatus\">Yükleniyor...</div>
      <div class=\"stat-grid\" id=\"routeStats\" style=\"display: none;\">
        <div class=\"stat\"><div class=\"label\">Orijinal Mesafe</div><div class=\"value\" id=\"routeOrigMesafe\">-</div></div>
        <div class=\"stat\"><div class=\"label\">Orijinal Süre</div><div class=\"value\" id=\"routeOrigSure\">-</div></div>
        <div class=\"stat\"><div class=\"label\">Algorit. Mesafe</div><div class=\"value\" id=\"routeAlgMesafe\">-</div></div>
        <div class=\"stat\"><div class=\"label\">Algorit. Süre</div><div class=\"value\" id=\"routeAlgSure\">-</div></div>
      </div>
    </div>

    <div class=\"footnote\" id=\"status\">Veri bekleniyor...</div>
    
    <div class=\"debug-box\" id=\"debugBox\">
      <div style=\"color: #fff\">[DEBUG] Başlatılıyor...</div>
    </div>
  </div>

  <script src=\"https://js.api.here.com/v3/3.1/mapsjs-core.js\"></script>
  <script src=\"https://js.api.here.com/v3/3.1/mapsjs-service.js\"></script>
  <script src=\"https://js.api.here.com/v3/3.1/mapsjs-ui.js\"></script>
  <script src=\"https://js.api.here.com/v3/3.1/mapsjs-mapevents.js\"></script>
  <script>
    const apiKey = "{api_key}";
    const platform = new H.service.Platform({{ apikey: apiKey }});
    const layers = platform.createDefaultLayers();

    const map = new H.Map(
      document.getElementById("map"),
      layers.vector.normal.map,
      {{
        center: {{ lat: 41.0082, lng: 28.9784 }},
        zoom: 11,
        pixelRatio: window.devicePixelRatio || 1,
      }}
    );    window.myMap = map;
    window.addEventListener("resize", () => map.getViewPort().resize());

    const mapEvents = new H.mapevents.MapEvents(map);
    new H.mapevents.Behavior(mapEvents);
    H.ui.UI.createDefault(map, layers);

    if (layers.vector.normal.traffic) {{
      map.addLayer(layers.vector.normal.traffic);
    }}

    const clockEl = document.getElementById("clock");
    const statusEl = document.getElementById("status");
    const segmentCountEl = document.getElementById("segmentCount");
    const avgSpeedEl = document.getElementById("avgSpeed");
    const avgFreeSpeedEl = document.getElementById("avgFreeSpeed");
    const jamFactorEl = document.getElementById("jamFactor");
    const congestionEl = document.getElementById("congestion");
    const volumeProxyEl = document.getElementById("volumeProxy");
    
    const routeStatusEl = document.getElementById("routeStatus");
    const routeStatsEl = document.getElementById("routeStats");
    const routeOrigMesafeEl = document.getElementById("routeOrigMesafe");
    const routeOrigSureEl = document.getElementById("routeOrigSure");
    const routeAlgMesafeEl = document.getElementById("routeAlgMesafe");
    const routeAlgSureEl = document.getElementById("routeAlgSure");

    function goToPreset(lat, lng, zoom) {{
      map.setCenter({{ lat, lng }});
      map.setZoom(zoom);
    }}

    function updateClock() {{
      const now = new Date();
      clockEl.textContent = now.toLocaleTimeString("tr-TR", {{ hour12: false }});
    }}

    function getCurrentBboxString() {{
      const lookAt = map.getViewModel().getLookAtData();
      const polygon = lookAt && lookAt.bounds ? lookAt.bounds : null;
      const bounds = polygon && typeof polygon.getBoundingBox === 'function' 
                        ? polygon.getBoundingBox() 
                        : polygon;

      if (!bounds) {{
        return "35.70,25.60,42.20,44.90";
      }}

      let south, west, north, east;
      if (typeof bounds.getBottom === "function") {{
        south = bounds.getBottom();
        west = bounds.getLeft();
        north = bounds.getTop();
        east = bounds.getRight();
      }} else {{
        south = bounds.bottom;
        west = bounds.left;
        north = bounds.top;
        east = bounds.right;
      }}

      if ([south, west, north, east].some((v) => typeof v !== "number" || Number.isNaN(v))) {{
        return "35.70,25.60,42.20,44.90";
      }}

      return `${{south}},${{west}},${{north}},${{east}}`;
    }}

    async function refreshTrafficPanel() {{
      try {{
        const bbox = encodeURIComponent(getCurrentBboxString());
        const response = await fetch(`/api/here/traffic/flow-summary?bbox=${{bbox}}`);
        if (!response.ok) {{
          throw new Error(`HTTP ${{response.status}}`);
        }}

        const data = await response.json();
        const s = data.summary;

        segmentCountEl.textContent = String(s.segment_count);
        avgSpeedEl.textContent = `${{s.avg_speed_kmh}} km/h`;
        avgFreeSpeedEl.textContent = `${{s.avg_free_flow_speed_kmh}} km/h`;
        jamFactorEl.textContent = String(s.avg_jam_factor);
        congestionEl.textContent = `${{s.congestion_pct}}%`;
        volumeProxyEl.textContent = `${{s.traffic_volume_proxy_pct}}%`;
        statusEl.textContent = `Son veri saati: ${{data.timestamp_local}}`;
      }} catch (error) {{
        statusEl.textContent = `Veri alinamadi: ${{error.message}}`;
      }}
    }}
    
    function addDebugLog(msg) {{
      const b = document.getElementById("debugBox");
      const d = new Date();
      b.innerHTML += `<div class=\"log\">[${{d.toLocaleTimeString()}}] ${{msg}}</div>`;
      b.scrollTop = b.scrollHeight;
    }}

    async function loadRouteStats() {{
      try {{
        addDebugLog("GET /api/route isteği gönderiliyor...");
        const res = await fetch(\"/api/route\");
        if (!res.ok) throw new Error(`Route API Error (HTTP ${{res.status}})`);
        const data = await res.json();
        addDebugLog(`API Yanıtı: Başarılı, mod sayısı: ${{Object.keys(data.modes || {{}}).length}}`);

        if (data.origin && data.destination) {{
          addDebugLog(`Başlangıç: ${{data.origin.lat.toFixed(4)}}, ${{data.origin.lng.toFixed(4)}}`);
          addDebugLog(`Bitiş: ${{data.destination.lat.toFixed(4)}}, ${{data.destination.lng.toFixed(4)}}`);
        }}
        
        const gStats = data.google_stats;
        let pStats = null;
        if (data.modes && data.modes.standart && data.modes.standart.stats) {{
          pStats = data.modes.standart.stats;
        }} else if (data.modes && data.modes.viraj_keyfi && data.modes.viraj_keyfi.stats) {{
           pStats = data.modes.viraj_keyfi.stats;
        }}
        
        // Handle empty/missing google_stats
        let gMesafe = \"-\";
        let gSure = \"-\";
        if (gStats && gStats.mesafe_m != null) {{
          gMesafe = `${{(gStats.mesafe_m / 1000).toFixed(1)}} km`;
        }}
        if (gStats && gStats.sure_s != null) {{
          gSure = `${{Math.round(gStats.sure_s / 60)}} dk`;
        }}
        
        if (pStats) {{
          routeStatsEl.style.display = \"grid\";
          routeStatusEl.style.display = \"none\";
          
          routeOrigMesafeEl.textContent = gMesafe;
          routeOrigSureEl.textContent = gSure;
          routeAlgMesafeEl.textContent = `${{(pStats.mesafe_m / 1000).toFixed(1)}} km`;
          routeAlgSureEl.textContent = `${{Math.round(pStats.sure_s / 60)}} dk`;

          if (data.google_route && data.google_route.length > 1) {{
            const googleLine = new H.geo.LineString();
            data.google_route.forEach((pt) => googleLine.pushPoint(pt));
            
            // Arkaya daha kalın bir çerçeve ve ana kesik çizgi atalım
            const googleOutline = new H.map.Polyline(googleLine, {{
              style: {{ lineWidth: 10, strokeColor: "rgba(0, 0, 0, 0.5)" }}
            }});
            const googlePolyline = new H.map.Polyline(googleLine, {{
              style: {{ lineWidth: 6, strokeColor: "rgba(200, 200, 200, 0.9)", lineDash: [5, 5] }}
            }});
            map.addObject(googleOutline);
            map.addObject(googlePolyline);
          }}

          let activeModeObj = data.modes.viraj_keyfi || data.modes.standart;
          if (activeModeObj && activeModeObj.coordinates && activeModeObj.coordinates.length > 1) {{
            const motoLine = new H.geo.LineString();
            activeModeObj.coordinates.forEach((pt) => motoLine.pushPoint(pt));
            
            // Fosforlu, çok kalın ve "highlight" edilmiş MotoMap rotası
            const motoOutline = new H.map.Polyline(motoLine, {{
              style: {{ lineWidth: 16, strokeColor: "rgba(0, 0, 0, 0.6)" }}
            }});
            const motoPolyline = new H.map.Polyline(motoLine, {{
              style: {{ lineWidth: 10, strokeColor: "rgba(255, 30, 30, 1)" }}
            }});
            map.addObject(motoOutline);
            map.addObject(motoPolyline);

            if (data.origin) {{
               // Daha büyük başlangıç / bitiş noktaları
               const originMarker = new H.map.Marker(data.origin);
               map.addObject(originMarker);
            }}
            if (data.destination) {{
               const destMarker = new H.map.Marker(data.destination);
               map.addObject(destMarker);
            }}

            // Haritayı rotaya odakla ve soldaki panel yüzünden biraz geri çek (padding)
            map.getViewModel().setLookAtData({{ bounds: motoPolyline.getBoundingBox() }}, true);
            setTimeout(() => map.setZoom(map.getZoom() - 0.5), 200);
          }}
        }} else {{
          routeStatusEl.textContent = \"Rota verisi (standart) bulunamadı.\";
          addDebugLog(`HATA: MotoMap mod formatı eksik!`);
        }}
        addDebugLog("Çizim işlemi tamamlandı.");
      }} catch (e) {{
        routeStatusEl.textContent = \"Bağlantı hatası.\";
        addDebugLog(`HATA: ${{e.message}}`);
      }}
    }}

    updateClock();
    setInterval(updateClock, 1000);

    refreshTrafficPanel();
    setInterval(refreshTrafficPanel, 15000);
    
    loadRouteStats();

    // Rota icin her 10 saniyede bir yeni veriyi cek:
    setInterval(() => {{
        addDebugLog("Yeniden rota cagriliyor... (10sn periyodik)");
        loadRouteStats();
    }}, 10000);

    map.addEventListener("mapviewchangeend", () => refreshTrafficPanel());
  </script>
</body>
</html>
"""