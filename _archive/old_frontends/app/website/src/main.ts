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

interface GoogleStats {
  mesafe_m: number;
  mesafe_text: string;
  sure_s: number;
  sure_text: string;
}

interface RouteData {
  origin: LatLng;
  destination: LatLng;
  origin_label: string;
  destination_label: string;
  google_route: LatLng[];
  google_stats: GoogleStats;
  modes: Record<string, ModeData>;
}

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY as string;

let map: google.maps.Map;
let motomapRoute: google.maps.Polyline | null = null;
let googleRoutePolyline: google.maps.Polyline | null = null;
let routeData: RouteData | null = null;
let currentMode = "standart";

function loadGoogleMapsScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (window.google?.maps) {
      resolve();
      return;
    }

    (window as any).__gmCallback = () => resolve();
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${API_KEY}&loading=async&callback=__gmCallback`;
    script.async = true;
    script.defer = true;
    script.onerror = () => reject(new Error("Google Maps yuklenemedi"));
    document.head.appendChild(script);
  });
}

async function fetchRouteData(): Promise<RouteData> {
  const res = await fetch("/routes/motomap_route.json");
  if (!res.ok) throw new Error("motomap_route.json yuklenemedi");
  return res.json();
}

function initMap(): void {
  map = new google.maps.Map(document.getElementById("map")!, {
    center: { lat: 40.988, lng: 29.025 },
    zoom: 15,
    styles: [
      { elementType: "geometry", stylers: [{ color: "#212121" }] },
      { elementType: "labels.text.stroke", stylers: [{ color: "#212121" }] },
      { elementType: "labels.text.fill", stylers: [{ color: "#757575" }] },
      {
        featureType: "road",
        elementType: "geometry",
        stylers: [{ color: "#383838" }],
      },
      {
        featureType: "road",
        elementType: "labels.text.fill",
        stylers: [{ color: "#8a8a8a" }],
      },
      {
        featureType: "water",
        elementType: "geometry",
        stylers: [{ color: "#0e1626" }],
      },
      {
        featureType: "water",
        elementType: "labels.text.fill",
        stylers: [{ color: "#3d3d3d" }],
      },
    ],
    mapTypeControl: false,
    streetViewControl: false,
  });
}

function drawGoogleRoute(coordinates: LatLng[]): void {
  if (googleRoutePolyline) {
    googleRoutePolyline.setMap(null);
  }

  googleRoutePolyline = new google.maps.Polyline({
    path: coordinates,
    strokeColor: "#4285F4",
    strokeWeight: 5,
    strokeOpacity: 0.8,
    map,
  });
}

function drawMotomapRoute(coordinates: LatLng[]): void {
  if (motomapRoute) {
    motomapRoute.setMap(null);
  }

  motomapRoute = new google.maps.Polyline({
    path: coordinates,
    strokeColor: "#E94560",
    strokeWeight: 5,
    strokeOpacity: 0.9,
    map,
  });
}

function addEndpoints(origin: LatLng, destination: LatLng): void {
  new google.maps.Circle({
    center: origin,
    radius: 40,
    fillColor: "#22c55e",
    fillOpacity: 0.95,
    strokeColor: "#14532d",
    strokeOpacity: 1,
    strokeWeight: 2,
    map,
  });

  new google.maps.Circle({
    center: destination,
    radius: 40,
    fillColor: "#f97316",
    fillOpacity: 0.95,
    strokeColor: "#7c2d12",
    strokeOpacity: 1,
    strokeWeight: 2,
    map,
  });
}

function formatDistance(meters: number): string {
  if (meters >= 1000) return `${(meters / 1000).toFixed(1)} km`;
  return `${Math.round(meters)} m`;
}

function formatTime(seconds: number): string {
  const mins = Math.round(seconds / 60);
  if (mins >= 60) {
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    return `${h}s ${m}dk`;
  }
  return `${mins} dk`;
}

function updateGoogleStats(stats: GoogleStats): void {
  document.getElementById("loading")!.style.display = "none";
  document.getElementById("google-stats")!.style.display = "block";

  document.getElementById("g-distance")!.textContent = formatDistance(stats.mesafe_m);
  document.getElementById("g-time")!.textContent = formatTime(stats.sure_s);
}

function updateMotomapStats(stats: ModeStats): void {
  document.getElementById("stats")!.style.display = "block";
  document.getElementById("mm-distance")!.textContent = formatDistance(stats.mesafe_m);
  document.getElementById("mm-time")!.textContent = formatTime(stats.sure_s);
  document.getElementById("mm-fun")!.textContent = String(stats.viraj_fun);
  document.getElementById("mm-danger")!.textContent = String(stats.viraj_tehlike);
  document.getElementById("mm-risk")!.textContent = String(stats.yuksek_risk);
  document.getElementById("mm-grade")!.textContent = `%${(stats.ortalama_egim * 100).toFixed(1)}`;
}

function switchMode(mode: string): void {
  if (!routeData || !routeData.modes[mode]) return;
  currentMode = mode;

  document.querySelectorAll(".mode-btn").forEach((btn) => {
    btn.classList.toggle("active", (btn as HTMLElement).dataset.mode === mode);
  });

  const modeData = routeData.modes[mode];
  drawMotomapRoute(modeData.coordinates);
  updateMotomapStats(modeData.stats);
}

async function init(): Promise<void> {
  try {
    const [data] = await Promise.all([fetchRouteData(), loadGoogleMapsScript()]);
    routeData = data;

    initMap();
    addEndpoints(data.origin, data.destination);

    if (data.google_route.length > 0) {
      drawGoogleRoute(data.google_route);
    }
    if (data.google_stats) {
      updateGoogleStats(data.google_stats);
    }

    switchMode(currentMode);
    document.querySelectorAll(".mode-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const mode = (btn as HTMLElement).dataset.mode!;
        switchMode(mode);
      });
    });
  } catch (err) {
    console.error("Baslatma hatasi:", err);
    document.getElementById("loading")!.innerHTML =
      '<span style="color: #e74c3c">Hata: Rotalar yuklenemedi. Lutfen generate_route.py calistirip tekrar deneyin.</span>';
  }
}

init();
