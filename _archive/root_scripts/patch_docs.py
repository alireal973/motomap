import sys

live_lab = """<!-- ============ LIVE LAB ============ -->
<section id="live-lab" class="sec sec-alt live-lab">
  <div class="c">
    <div class="sec-h r"><div class="sec-e">Live Data</div><h2 class="sec-t">Local <em class="em">Live View</em></h2><p class="sec-d">Real-time MotoMap route payload and live HERE traffic summaries, bridged seamlessly from Docker.</p></div>
    <div class="live-lab-shell">
      <div class="live-lab-map-card">
        <div class="live-lab-header">
          <span class="live-lab-kicker">Docker bridge</span>
          <button id="live-lab-refresh" class="btn btn-g">Refresh Live View</button>
        </div>
        <div class="live-lab-map-container">
          <div id="live-lab-map"></div>
          <div id="live-lab-map-loading" class="live-lab-map-loading">Connecting payload...</div>
        </div>
      </div>
      <div class="live-lab-panel">
        <div class="live-lab-status-row">
          <span id="live-lab-status" class="live-lab-pill is-idle">Evaluating</span>
          <span id="live-lab-api-origin" class="live-lab-api-origin">...</span>
        </div>
        
        <div class="live-lab-journey-card">
          <h3 id="live-lab-route-title" style="margin:0 0 6px 0;font-size:22px;font-weight:600;">Route Preview</h3>
          <p id="live-lab-route-copy" style="margin:0;color:var(--t2);font-size:15px;line-height:1.4;">Connecting to local graph...</p>
        </div>
        
        <div class="live-lab-traffic-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:24px 0;">
          <div class="live-lab-stat"><div class="stat-label" style="color:var(--t2);font-size:13px;margin-bottom:8px;">Average speed</div><div id="live-lab-speed" class="stat-val" style="font-size:28px;font-weight:900;font-family:var(--mono);">--</div></div>
          <div class="live-lab-stat"><div class="stat-label" style="color:var(--t2);font-size:13px;margin-bottom:8px;">Free flow</div><div id="live-lab-free-flow" class="stat-val" style="font-size:28px;font-weight:900;font-family:var(--mono);">--</div></div>
          <div class="live-lab-stat"><div class="stat-label" style="color:var(--t2);font-size:13px;margin-bottom:8px;">Congestion</div><div id="live-lab-congestion" class="stat-val" style="font-size:28px;font-weight:900;font-family:var(--mono);">--</div></div>
          <div class="live-lab-stat"><div class="stat-label" style="color:var(--t2);font-size:13px;margin-bottom:8px;">Segments</div><div id="live-lab-segments" class="stat-val" style="font-size:28px;font-weight:900;font-family:var(--mono);">--</div></div>
        </div>
        
        <div id="live-lab-traffic-banner" class="live-lab-traffic-banner" style="padding:16px;border-radius:12px;margin-bottom:24px;border-left:4px solid var(--t3);font-weight:600;font-size:15px;background:rgba(255,255,255,0.03);">Calculating traffic pressure...</div>
        
        <div id="live-lab-mode-list" class="live-lab-mode-list" style="display:flex;flex-direction:column;gap:12px;margin-bottom:24px;"></div>
        
        <div style="font-size:13px;color:var(--t3);text-align:center;">Note: Public visitors will see fallback data; live data requires the localhost Docker stack.</div>
      </div>
    </div>
  </div>
</section>

<!-- ============ CTA ============ -->"""

js_css = """
<style>
.live-lab { padding-top: 108px; padding-bottom: 72px; }
.live-lab-shell { display: grid; grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.95fr); gap: 24px; }
.live-lab-map-card, .live-lab-panel {
  background: linear-gradient(135deg, rgba(20,11,26,.8) 0%, rgba(9,5,12,.95) 100%);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 28px;
  padding: 24px;
  position: relative;
  box-shadow: 0 32px 64px -16px rgba(0,0,0,.5);
}
.live-lab-map-card::before, .live-lab-panel::before {
  content: ''; position: absolute; inset: 0; border-radius: inherit;
  background: radial-gradient(circle at top left, rgba(250,204,21,.04), transparent 50%);
  pointer-events: none;
}
.live-lab-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.live-lab-kicker { color: var(--accent); font-family: var(--mono); font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
.live-lab-map-container { position: relative; border-radius: 22px; overflow: hidden; background: #09050C; min-height: 560px; height: calc(100% - 56px); }
#live-lab-map { position: absolute; inset: 0; width: 100%; height: 100%; }
.live-lab-map-loading {
  position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
  background: rgba(0,0,0,.8); color: var(--t); padding: 8px 16px; border-radius: 20px;
  font-size: 14px; border: 1px solid rgba(255,255,255,.1); backdrop-filter: blur(10px);
  transition: opacity 0.3s, transform 0.3s; z-index: 10;
}
.live-lab-map-loading.is-hidden { opacity: 0; transform: translate(-50%, -6px); pointer-events: none; }

.live-lab-status-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.live-lab-pill { padding: 6px 14px; border-radius: 12px; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.live-lab-pill.is-idle { background: rgba(250,204,21,.15); color: #FDE047; border: 1px solid rgba(250,204,21,.3); }
.live-lab-pill.is-live { background: rgba(134,239,172,.15); color: #86EFAC; border: 1px solid rgba(134,239,172,.3); }
.live-lab-pill.is-error { background: rgba(249,115,22,.15); color: #F97316; border: 1px solid rgba(249,115,22,.3); }
.live-lab-api-origin { font-family: var(--mono); font-size: 13px; color: var(--t3); }

.live-lab-stat { background: rgba(0,0,0,.3); padding: 16px; border-radius: 16px; border: 1px solid rgba(255,255,255,.04); }
.live-lab-mode-card { background: rgba(0,0,0,.3); border-radius: 16px; padding: 16px; border: 1px solid rgba(255,255,255,.04); display: flex; flex-direction: column; gap: 12px; }
.live-lab-mode-card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 14px; }
.live-lab-mode-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.live-lab-mode-stat { display: flex; justify-content: space-between; font-size: 13px; }
.live-lab-mode-stat span { color: var(--t2); }
.live-lab-mode-stat strong { font-family: var(--mono); color: var(--t); }

@media(max-width: 1120px) { .live-lab-shell { grid-template-columns: 1fr; } .live-lab-map-container { min-height: 480px; } }
@media(max-width: 720px) { .live-lab { padding-top: 64px; padding-bottom: 64px; } .live-lab-map-card, .live-lab-panel { padding: 16px; border-radius: 20px; } .live-lab-map-container { min-height: 380px; } }
</style>

<script>
(function() {
  let map, mapLoaded = false, lastData = null;
  const els = {
    refresh: document.getElementById('live-lab-refresh'),
    loading: document.getElementById('live-lab-map-loading'),
    pill: document.getElementById('live-lab-status'),
    apiLabel: document.getElementById('live-lab-api-origin'),
    title: document.getElementById('live-lab-route-title'),
    copy: document.getElementById('live-lab-route-copy'),
    speed: document.getElementById('live-lab-speed'),
    freeFlow: document.getElementById('live-lab-free-flow'),
    congestion: document.getElementById('live-lab-congestion'),
    segments: document.getElementById('live-lab-segments'),
    banner: document.getElementById('live-lab-traffic-banner'),
    modes: document.getElementById('live-lab-mode-list')
  };

  const colors = { google: '#60A5FA', standart: '#FACC15', viraj_keyfi: '#E879F9', guvenli: '#86EFAC' };

  async function getApiBase() {
    const candidates = [
      window.location.origin.includes('github.io') ? null : window.location.origin,
      'http://127.0.0.1:8008',
      'http://localhost:8008'
    ].filter(Boolean);
    
    for (const base of candidates) {
      if(base === 'null') continue;
      try {
        const res = await fetch(base + '/health', { cache: 'no-store', signal: AbortSignal.timeout(1500) });
        if (res.ok) return base;
      } catch (e) {}
    }
    return null;
  }
  
  function getFallbackData() {
    try { return JSON.parse(document.getElementById('route-preview-data').textContent); } catch(e) { return null; }
  }

  function computeBbox(payload) {
    let minLat = 90, maxLat = -90, minLng = 180, maxLng = -180, hasCoords = false;
    const checkCoords = (coords) => {
      (coords || []).forEach(c => {
        hasCoords = true;
        if(c.lat < minLat) minLat = c.lat;
        if(c.lat > maxLat) maxLat = c.lat;
        if(c.lng < minLng) minLng = c.lng;
        if(c.lng > maxLng) maxLng = c.lng;
      });
    };
    checkCoords(payload.google_route);
    if(payload.modes) Object.values(payload.modes).forEach(m => checkCoords(m.coordinates));
    
    if(!hasCoords) return "40.9,28.9,41.1,29.1";

    const latPad = Math.max((maxLat - minLat) * 0.45, 0.008);
    const lngPad = Math.max((maxLng - minLng) * 0.45, 0.012);
    
    return [Math.max(-90, minLat - latPad), Math.max(-180, minLng - lngPad), Math.min(90, maxLat + latPad), Math.min(180, maxLng + lngPad)].join(',');
  }

  async function refreshData() {
    els.loading.classList.remove('is-hidden');
    els.pill.className = 'live-lab-pill is-idle';
    els.pill.textContent = 'Connecting...';
    els.apiLabel.textContent = 'Probing...';
    els.refresh.disabled = true;

    let payload = null, traffic = null, isLive = false;
    
    const base = await getApiBase();
    if (base) {
      try {
        const res = await fetch(base + '/api/route', { cache: 'no-store' });
        if (res.ok) {
          payload = await res.json();
          isLive = true;
          try {
            const bbox = computeBbox(payload);
            const tres = await fetch(base + '/api/here/traffic/flow-summary?bbox=' + bbox, { cache: 'no-store' });
            if (tres.ok) traffic = await tres.json();
          } catch(err) {}
        }
      } catch(e) {}
    }

    if (!isLive) {
      payload = getFallbackData();
      els.apiLabel.textContent = 'Fallback Payload';
      els.pill.className = 'live-lab-pill is-error';
      els.pill.textContent = 'Docker Offline';
    } else {
      els.apiLabel.textContent = base;
      els.pill.className = 'live-lab-pill is-live';
      els.pill.textContent = 'Live Connected';
    }

    if (payload) {
      els.title.textContent = "Route Active";
      els.copy.textContent = (payload.origin_label || 'Location A') + ' to ' + (payload.destination_label || 'Location B');
      
      let cp = 0;
      if (traffic && traffic.summary) {
        els.speed.textContent = Math.round(traffic.summary.avg_speed_kmh || 0);
        els.freeFlow.textContent = Math.round(traffic.summary.avg_free_flow_speed_kmh || 0);
        cp = traffic.summary.congestion_pct || 0;
        els.congestion.textContent = cp.toFixed(1) + '%';
        els.segments.textContent = traffic.summary.segment_count || 0;
      } else {
        els.speed.textContent = '--'; els.freeFlow.textContent = '--'; els.congestion.textContent = '--'; els.segments.textContent = '--';
      }

      if(!isLive || (!traffic && isLive)) {
        els.banner.textContent = isLive ? 'Waiting for traffic pipeline...' : 'Start local Docker stack for live HERE traffic.';
        els.banner.style.borderLeftColor = 'var(--t3)';
        els.banner.style.background = 'rgba(255,255,255,0.03)';
      } else {
        els.banner.textContent = cp < 40 ? 'Traffic flows cleanly through optimal passages.' : (cp < 70 ? 'Moderate congestion. Safest routing active.' : 'Heavy traffic envelope ahead.');
        els.banner.style.borderLeftColor = cp < 40 ? 'var(--green)' : (cp < 70 ? 'var(--accent)' : 'var(--orange)');
        els.banner.style.background = cp < 40 ? 'rgba(134,239,172,0.05)' : (cp < 70 ? 'rgba(250,204,21,0.05)' : 'rgba(249,115,22,0.05)');
      }

      const formatTime = (secs) => {
        if (!secs) return '--';
        const m = Math.floor(secs / 60);
        const h = Math.floor(m / 60);
        if (h > 0) return h + 'h ' + (m%60) + 'm';
        return m + ' min';
      };

      els.modes.innerHTML = '';
      if(payload.modes) {
        ['standart', 'viraj_keyfi', 'guvenli'].forEach(key => {
          if(!payload.modes[key]) return;
          const mode = payload.modes[key];
          const st = mode.stats || {};
          const km = st.mesafe_m ? (st.mesafe_m/1000).toFixed(1) + 'km' : '--';
          const tinfo = formatTime(st.sure_s);
          const clr = colors[key];
          const name = key === 'standart' ? 'Standard Route' : (key === 'viraj_keyfi' ? 'Twist & Curve' : 'Safest Filter');
          
          els.modes.innerHTML += `
            <div class="live-lab-mode-card" style="border-left: 3px solid ${clr}">
              <div class="live-lab-mode-card-header"><span style="color: ${clr}">${name}</span><span>${km}</span></div>
              <div class="live-lab-mode-grid">
                <div class="live-lab-mode-stat"><span>Est. Duration</span><strong>${tinfo}</strong></div>
                <div class="live-lab-mode-stat"><span>Fun Score</span><strong>${st.viraj_fun || 0}</strong></div>
                <div class="live-lab-mode-stat"><span>Risk Flags</span><strong>${st.yuksek_risk || 0}</strong></div>
                <div class="live-lab-mode-stat"><span>Lane Filter</span><strong>${st.serit_paylasimi ? st.serit_paylasimi+'m' : '0m'}</strong></div>
              </div>
            </div>`;
        });
      }
      
      lastData = payload;
      if(mapLoaded && map) renderGeoJSON(payload, isLive);
    }
    
    els.refresh.disabled = false;
    setTimeout(() => els.loading.classList.add('is-hidden'), 300);
  }

  function renderGeoJSON(payload, isLive) {
    const features = [];
    if(payload.google_route) {
        features.push({
            type: 'Feature', properties: { kind: 'route', routeKey: 'google' },
            geometry: { type: 'LineString', coordinates: payload.google_route.map(c => [c.lng, c.lat]) }
        });
    }
    if(payload.modes) {
        Object.entries(payload.modes).forEach(([key, val]) => {
            if(val.coordinates && Array.isArray(val.coordinates) && val.coordinates.length > 0) {
                if (isLive) {
                  features.push({
                      type: 'Feature', properties: { kind: 'traffic' },
                      geometry: { type: 'LineString', coordinates: val.coordinates.map(c => [c.lng, c.lat]) }
                  });
                }
                features.push({
                    type: 'Feature', properties: { kind: 'route', routeKey: key },
                    geometry: { type: 'LineString', coordinates: val.coordinates.map(c => [c.lng, c.lat]) }
                });
            }
        });
    }
    ['origin', 'destination'].forEach(k => {
        if(payload[k] && payload[k].lat) {
            features.push({
                type: 'Feature', properties: { kind: 'point', isDest: k==='destination' },
                geometry: { type: 'Point', coordinates: [payload[k].lng, payload[k].lat] }
            });
        }
    });

    const src = map.getSource('live-lab-routes');
    if(src) src.setData({ type: 'FeatureCollection', features });

    let minLat=90, maxLat=-90, minLng=180, maxLng=-180;
    let hasGeom = false;
    features.forEach(f => {
        if(f.geometry && f.geometry.type === 'LineString') {
            f.geometry.coordinates.forEach(c => {
                hasGeom = true;
                if(c[1]<minLat) minLat=c[1]; if(c[1]>maxLat) maxLat=c[1];
                if(c[0]<minLng) minLng=c[0]; if(c[0]>maxLng) maxLng=c[0];
            });
        }
    });

    if(hasGeom && minLat < 90) {
        map.fitBounds([[minLng, minLat], [maxLng, maxLat]], { padding: {top:64, bottom:64, left:64, right:64}, maxZoom: 14.2 });
    }
  }

  function mountMap() {
    map = new maplibregl.Map({
      container: 'live-lab-map',
      style: 'https://tiles.openfreemap.org/styles/dark',
      center: [28.97, 41.01],
      zoom: 10,
      dragRotate: false,
      scrollZoom: false
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

    map.on('load', () => {
      map.addSource('live-lab-routes', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });

      map.addLayer({
        id: 'live-lab-traffic-halo', type: 'line', source: 'live-lab-routes',
        filter: ['==', 'kind', 'traffic'],
        paint: { 'line-color': 'rgba(250,204,21,0.25)', 'line-width': 12, 'line-blur': 6 }
      });

      map.addLayer({
        id: 'live-lab-google', type: 'line', source: 'live-lab-routes',
        filter: ['all', ['==', 'kind', 'route'], ['==', 'routeKey', 'google']],
        paint: { 'line-color': colors.google, 'line-width': 4, 'line-dasharray': [2, 2] }
      });

      map.addLayer({
        id: 'live-lab-route-lines', type: 'line', source: 'live-lab-routes',
        filter: ['all', ['==', 'kind', 'route'], ['!=', 'routeKey', 'google']],
        paint: {
          'line-color': ['match', ['get', 'routeKey'], 'standart', colors.standart, 'viraj_keyfi', colors.viraj_keyfi, 'guvenli', colors.guvenli, '#fff'],
          'line-width': 4
        }
      });

      map.addLayer({
        id: 'live-lab-points', type: 'circle', source: 'live-lab-routes',
        filter: ['==', 'kind', 'point'],
        paint: {
          'circle-radius': 8,
          'circle-color': ['case', ['get', 'isDest'], '#EF4444', '#3B82F6'],
          'circle-stroke-width': 2,
          'circle-stroke-color': '#fff'
        }
      });

      mapLoaded = true;
      if (lastData) renderGeoJSON(lastData, document.getElementById('live-lab-status').className.includes('live'));
    });
  }

  els.refresh.addEventListener('click', refreshData);
  
  let iv = setInterval(refreshData, 60000);
  document.addEventListener("visibilitychange", () => {
      if(document.visibilityState === 'visible') { refreshData(); clearInterval(iv); iv = setInterval(refreshData, 60000); }
  });

  if (typeof maplibregl !== 'undefined') mountMap();
  else window.addEventListener('load', mountMap);

  refreshData();
})();
</script>
"""

with open('docs/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

if "<!-- ============ LIVE LAB ============ -->" not in content:
    content = content.replace("<!-- ============ CTA ============ -->", live_lab)

if '<li><a href="#live-lab">Live Map</a></li>' not in content:
    content = content.replace('<li><a href="#features">Features</a></li>', '<li><a href="#features">Features</a></li>\n        <li><a href="#live-lab">Live Map</a></li>')

if ".live-lab {" not in content:
    content = content.replace("</body>", js_css + "\n</body>")

with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("HTML updated successfully.")
