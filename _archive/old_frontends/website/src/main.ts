interface LatLng {
  lat: number;
  lng: number;
}

interface ModeStats {
  mesafe_m: number;
  sure_s: number;
  viraj_fun: number;
  viraj_tehlike: number;
  yuksek_risk: number;
  ortalama_egim: number;
  ucretli: boolean;
}

interface ModeData {
  coordinates: LatLng[];
  stats: ModeStats;
}

interface BaselineStats {
  mesafe_m?: number;
  mesafe_text?: string;
  sure_s?: number;
  sure_text?: string;
}

interface EvidenceChecks {
  baseline_route_exists: boolean;
  all_modes_exist: boolean;
  viraj_fun_ge_standard: boolean;
  guvenli_risk_le_standard: boolean;
  standart_distance_close_to_baseline: boolean;
  standart_time_close_to_baseline: boolean;
}

interface ModeComparison {
  distance_ratio_vs_baseline: number | null;
  time_ratio_vs_baseline: number | null;
  fun_delta_vs_standard: number | null;
  risk_delta_vs_standard: number | null;
}

interface CaseEvidence {
  checks: EvidenceChecks;
  score: number;
  total: number;
  verdict: "PASS" | "FAIL";
  baseline_backend: string;
  mode_comparisons: Record<string, ModeComparison>;
}

interface ComparisonCase {
  case_id: string;
  label: string;
  origin: LatLng;
  destination: LatLng;
  origin_label: string;
  destination_label: string;
  baseline_backend: string;
  baseline_route: LatLng[];
  baseline_stats: BaselineStats;
  modes: Record<string, ModeData>;
  evidence: CaseEvidence;
}

interface ComparisonSuite {
  generated_at: string;
  place: string;
  baseline_backend: string;
  summary: {
    total_cases: number;
    total_mode_routes: number;
    passed_cases: number;
    failed_cases: number;
    average_score_ratio: number | null;
  };
  cases: ComparisonCase[];
}

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string;

const MODE_META: Record<string, { label: string; strokeOpacity: number }> = {
  standart: { label: "Standart", strokeOpacity: 0.95 },
  viraj_keyfi: { label: "Viraj Keyfi", strokeOpacity: 0.92 },
  guvenli: { label: "Guvenli", strokeOpacity: 0.92 },
};

const CASE_COLORS = ["#e76f51", "#2a9d8f", "#6d597a"];

let map: google.maps.Map;
let suiteData: ComparisonSuite | null = null;
const overlays: any[] = [];

function loadGoogleMapsScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (window.google?.maps) {
      resolve();
      return;
    }

    (window as Window & { __gmCallback?: () => void }).__gmCallback = () => resolve();
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&loading=async&callback=__gmCallback`;
    script.async = true;
    script.defer = true;
    script.onerror = () => reject(new Error("Google Maps yuklenemedi"));
    document.head.appendChild(script);
  });
}

async function fetchSuiteData(): Promise<ComparisonSuite> {
  const res = await fetch("/routes/comparison_suite.json");
  if (!res.ok) throw new Error("comparison_suite.json yuklenemedi");
  return res.json();
}

function initMap(): void {
  map = new google.maps.Map(document.getElementById("map")!, {
    center: { lat: 40.978, lng: 29.048 },
    zoom: 12,
    styles: [
      { elementType: "geometry", stylers: [{ color: "#f5f0e6" }] },
      { elementType: "labels.text.fill", stylers: [{ color: "#4c4945" }] },
      { elementType: "labels.text.stroke", stylers: [{ color: "#f5f0e6" }] },
      { featureType: "road", elementType: "geometry", stylers: [{ color: "#ffffff" }] },
      { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#f4d7a4" }] },
      { featureType: "water", elementType: "geometry", stylers: [{ color: "#b7d7ea" }] },
      { featureType: "poi.park", elementType: "geometry", stylers: [{ color: "#daeac9" }] },
    ],
    mapTypeControl: false,
    streetViewControl: false,
  });
}

function clearMap(): void {
  overlays.forEach((item) => item.setMap?.(null));
  overlays.length = 0;
}

function formatDistance(meters?: number): string {
  if (typeof meters !== "number") return "—";
  if (meters >= 1000) return `${(meters / 1000).toFixed(1)} km`;
  return `${Math.round(meters)} m`;
}

function formatTime(seconds?: number): string {
  if (typeof seconds !== "number") return "—";
  const mins = Math.round(seconds / 60);
  if (mins >= 60) {
    const hours = Math.floor(mins / 60);
    const rest = mins % 60;
    return `${hours}s ${rest}dk`;
  }
  return `${mins} dk`;
}

function formatRatio(value: number | null | undefined): string {
  if (typeof value !== "number") return "—";
  return `${value.toFixed(2)}x`;
}

function midpoint(coords: LatLng[]): LatLng | null {
  if (!coords.length) return null;
  return coords[Math.floor(coords.length / 2)];
}

function addPointMarker(point: LatLng, color: string, title: string, glyph: string): void {
  const marker = new (google.maps as any).Marker({
    position: point,
    map,
    title,
    label: {
      text: glyph,
      color: "#ffffff",
      fontSize: "11px",
      fontWeight: "700",
    },
    icon: {
      path: (google.maps as any).SymbolPath.CIRCLE,
      fillColor: color,
      fillOpacity: 1,
      strokeColor: "#ffffff",
      strokeWeight: 2,
      scale: 8,
    },
  });
  overlays.push(marker);
}

function addRouteLabel(point: LatLng, text: string, color: string): void {
  const marker = new (google.maps as any).Marker({
    position: point,
    map,
    label: {
      text,
      color: "#1f2933",
      fontSize: "11px",
      fontWeight: "700",
    },
    icon: {
      path: "M 0 0",
      fillOpacity: 0,
      strokeOpacity: 0,
      scale: 1,
    },
  });
  overlays.push(marker);

  const dot = new (google.maps as any).Marker({
    position: point,
    map,
    icon: {
      path: (google.maps as any).SymbolPath.CIRCLE,
      fillColor: color,
      fillOpacity: 1,
      strokeColor: "#ffffff",
      strokeWeight: 1,
      scale: 4,
    },
  });
  overlays.push(dot);
}

function addGoogleRoute(caseIndex: number, item: ComparisonCase): void {
  const polyline = new google.maps.Polyline({
    path: item.baseline_route,
    strokeColor: "#2563eb",
    strokeWeight: 4,
    strokeOpacity: 0,
    icons: [
      {
        icon: {
          path: "M 0,-1 0,1",
          strokeOpacity: 1,
          strokeColor: "#2563eb",
          scale: 3,
        },
        offset: "0",
        repeat: "12px",
      },
    ],
    map,
  } as any);
  overlays.push(polyline);

  const mid = midpoint(item.baseline_route);
  if (mid) {
    addRouteLabel(mid, `G${caseIndex + 1}`, "#2563eb");
  }
}

function addMotoRoute(
  caseIndex: number,
  item: ComparisonCase,
  mode: string,
  modeData: ModeData,
): void {
  const color = CASE_COLORS[caseIndex % CASE_COLORS.length];
  const weight = mode === "standart" ? 6 : 5;
  const polyline = new google.maps.Polyline({
    path: modeData.coordinates,
    strokeColor: color,
    strokeWeight: weight,
    strokeOpacity: MODE_META[mode].strokeOpacity,
    map,
  });
  overlays.push(polyline);

  const mid = midpoint(modeData.coordinates);
  if (mid) {
    const suffix =
      mode === "standart" ? "S" : mode === "viraj_keyfi" ? "V" : "Gv";
    addRouteLabel(mid, `${caseIndex + 1}-${suffix}`, color);
  }
}

function fitAllRoutes(cases: ComparisonCase[]): void {
  const bounds = new (google.maps as any).LatLngBounds();
  cases.forEach((item) => {
    bounds.extend(item.origin);
    bounds.extend(item.destination);
    item.baseline_route.forEach((point) => bounds.extend(point));
    Object.values(item.modes).forEach((modeData) => {
      modeData.coordinates.forEach((point) => bounds.extend(point));
    });
  });

  if (!bounds.isEmpty()) {
    (map as any).fitBounds(bounds, 40);
  }
}

function updateSummaryHeader(): void {
  if (!suiteData) return;
  document.getElementById("suite-summary")!.textContent =
    `${suiteData.summary.total_cases} vaka, 3 Google baz rota, ${suiteData.summary.total_mode_routes} MOTOMAP rota`;
  document.getElementById("suite-proof")!.textContent =
    `${suiteData.summary.passed_cases}/${suiteData.summary.total_cases} vaka PASS`;
}

function renderLegend(): void {
  const container = document.getElementById("legend-list")!;
  container.innerHTML = "";

  const baseline = document.createElement("div");
  baseline.className = "legend-item";
  baseline.innerHTML = `
    <span class="legend-swatch dashed" style="--legend-color:#2563eb"></span>
    <span>Google baz rota: G1, G2, G3</span>
  `;
  container.appendChild(baseline);

  CASE_COLORS.forEach((color, index) => {
    const item = document.createElement("div");
    item.className = "legend-item";
    item.innerHTML = `
      <span class="legend-swatch" style="background:${color}"></span>
      <span>Rota ${index + 1} ailesi</span>
    `;
    container.appendChild(item);
  });
}

function renderCaseCards(): void {
  if (!suiteData) return;
  const container = document.getElementById("case-list")!;
  container.innerHTML = "";

  suiteData.cases.forEach((item, caseIndex) => {
    const card = document.createElement("article");
    card.className = "case-card";

    const checks = Object.entries(item.evidence.checks)
      .map(([key, value]) => `${value ? "PASS" : "FAIL"} · ${key}`)
      .join("<br>");

    const modesHtml = Object.entries(item.modes)
      .map(([mode, modeData]) => {
        const comparison = item.evidence.mode_comparisons[mode];
        return `
          <div class="mode-row-card">
            <strong>${caseIndex + 1}-${MODE_META[mode].label}</strong>
            <span>${formatDistance(modeData.stats.mesafe_m)} · ${formatTime(modeData.stats.sure_s)}</span>
            <span>Fun ${modeData.stats.viraj_fun} · Risk ${modeData.stats.yuksek_risk}</span>
            <span>Baz oran ${formatRatio(comparison.distance_ratio_vs_baseline)} / ${formatRatio(comparison.time_ratio_vs_baseline)}</span>
          </div>
        `;
      })
      .join("");

    card.innerHTML = `
      <div class="case-card-head">
        <div>
          <div class="case-kicker">Rota ${caseIndex + 1}</div>
          <h3>${item.origin_label} → ${item.destination_label}</h3>
          <p>${item.label}</p>
        </div>
        <div class="case-badge ${item.evidence.verdict === "PASS" ? "pass" : "fail"}">${item.evidence.verdict} ${item.evidence.score}/${item.evidence.total}</div>
      </div>
      <div class="case-stats">
        <div class="metric">
          <span>Google</span>
          <strong>${formatDistance(item.baseline_stats.mesafe_m)}</strong>
          <em>${formatTime(item.baseline_stats.sure_s)}</em>
        </div>
        <div class="metric">
          <span>Baslangic</span>
          <strong>${item.origin_label}</strong>
          <em>${item.destination_label}</em>
        </div>
      </div>
      <div class="mode-list">${modesHtml}</div>
      <div class="checks">${checks}</div>
    `;

    container.appendChild(card);
  });
}

function renderAllRoutes(): void {
  if (!suiteData) return;
  clearMap();

  suiteData.cases.forEach((item, caseIndex) => {
    const caseColor = CASE_COLORS[caseIndex % CASE_COLORS.length];
    addPointMarker(item.origin, caseColor, `${item.origin_label}`, `O${caseIndex + 1}`);
    addPointMarker(
      item.destination,
      caseColor,
      `${item.destination_label}`,
      `D${caseIndex + 1}`,
    );
    addGoogleRoute(caseIndex, item);
    Object.entries(item.modes).forEach(([mode, modeData]) => {
      addMotoRoute(caseIndex, item, mode, modeData);
    });
  });

  fitAllRoutes(suiteData.cases);
}

async function init(): Promise<void> {
  try {
    const [data] = await Promise.all([fetchSuiteData(), loadGoogleMapsScript()]);
    suiteData = data;

    initMap();
    updateSummaryHeader();
    renderLegend();
    renderCaseCards();
    renderAllRoutes();
    document.getElementById("loading")!.style.display = "none";
  } catch (error) {
    console.error("Baslatma hatasi:", error);
    document.getElementById("loading")!.innerHTML =
      '<span style="color:#b42318">Hata: comparison_suite.json veya Google Maps yuklenemedi.</span>';
  }
}

init();
