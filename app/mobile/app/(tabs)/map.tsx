// app/mobile/app/(tabs)/map.tsx
import { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Animated,
  Dimensions,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import MapView, { Polyline, Circle, PROVIDER_DEFAULT } from "react-native-maps";
import * as Location from "expo-location";
import ModeSelector from "../../components/ModeSelector";
import RouteCompareCard from "../../components/RouteCompareCard";
import StatCard from "../../components/StatCard";
import { WeatherCard } from "../../components/WeatherCard";
import { SafetyModeToggle } from "../../components/SafetyModeToggle";
import { ReportMarker, type RoadReport } from "../../components/ReportMarker";
import { useWeather } from "../../hooks/useWeather";
import { colors, spacing } from "../../theme";
import { RouteData, RIDING_MODES, type SafetyViewMode } from "../../types";
import { fetchRoutePreview, API_URL } from "../../utils/api";
import { toMapCoords } from "../../utils/format";

const { height } = Dimensions.get("window");
const PANEL_HEIGHT = height * 0.44;

export default function MapScreen() {
  const [data, setData] = useState<RouteData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeMode, setActiveMode] = useState("standart");
  const [locationError, setLocationError] = useState<string | null>(null);
  const [userLocation, setUserLocation] = useState<Location.LocationObject | null>(null);
  const [viewMode, setViewMode] = useState<SafetyViewMode>("standard");
  const [reports, setReports] = useState<RoadReport[]>([]);
  const [showReports, setShowReports] = useState(true);
  const panelAnim = useRef(new Animated.Value(0)).current;

  const userLat = userLocation?.coords.latitude ?? null;
  const userLng = userLocation?.coords.longitude ?? null;
  const { weather, roadConditions, isLoading: weatherLoading } = useWeather(userLat, userLng);

  useEffect(() => {
    (async () => {
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status !== "granted") {
          setLocationError("Konum izni reddedildi. Canli konum haritada gorunmeyecek.");
          return;
        }
        const loc = await Location.getCurrentPositionAsync({});
        setUserLocation(loc);

        // Fetch nearby reports
        try {
          const res = await fetch(`${API_URL}/api/reports?lat=${loc.coords.latitude}&lng=${loc.coords.longitude}&radius_km=15`);
          if (res.ok) setReports(await res.json());
        } catch {}
      } catch (err) {
        console.warn("Konum alinamadi:", err);
      }
    })();

    fetchRoutePreview()
      .then((d) => {
        setData(d);
        Animated.spring(panelAnim, {
          toValue: 1,
          useNativeDriver: true,
          bounciness: 3,
        }).start();
      })
      .catch((e) => setError(String(e)));
  }, []);

  const mode = data?.modes[activeMode];
  const stats = mode?.stats;

  const centerLat = data ? (data.origin.lat + data.destination.lat) / 2 : 40.9811;
  const centerLng = data ? (data.origin.lng + data.destination.lng) / 2 : 29.031;

  const panelTranslate = panelAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [PANEL_HEIGHT, 0],
  });

  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        provider={PROVIDER_DEFAULT}
        showsUserLocation={true}
        showsMyLocationButton={true}
        initialRegion={{
          latitude: centerLat,
          longitude: centerLng,
          latitudeDelta: 0.045,
          longitudeDelta: 0.035,
        }}
      >
        {data && (
          <>
            <Polyline
              coordinates={toMapCoords(data.google_route)}
              strokeColor={colors.googleBlue}
              strokeWidth={4}
              lineDashPattern={[8, 4]}
            />
            {mode && (
              <Polyline
                coordinates={toMapCoords(mode.coordinates)}
                strokeColor={colors.accentBlue}
                strokeWidth={5}
              />
            )}
            <Circle
              center={{ latitude: data.origin.lat, longitude: data.origin.lng }}
              radius={50}
              fillColor="rgba(34,197,94,0.85)"
              strokeColor="#14532d"
              strokeWidth={2}
            />
            <Circle
              center={{ latitude: data.destination.lat, longitude: data.destination.lng }}
              radius={50}
              fillColor="rgba(249,115,22,0.85)"
              strokeColor="#7c2d12"
              strokeWidth={2}
            />
          </>
        )}
        {showReports && reports.map((r) => (
          <ReportMarker key={r.id} report={r} />
        ))}
      </MapView>

      {/* Weather compact badge */}
      {weather && (
        <View style={styles.weatherOverlay}>
          <WeatherCard weather={weather} roadConditions={roadConditions} compact />
        </View>
      )}

      {/* Safety mode + report toggle */}
      <View style={styles.controlsOverlay}>
        <SafetyModeToggle activeMode={viewMode} onModeChange={setViewMode} />
        <TouchableOpacity
          style={[styles.reportToggle, showReports && styles.reportToggleActive]}
          onPress={() => setShowReports(!showReports)}
        >
          <Text style={styles.reportToggleText}>{"\u26A0\uFE0F"}</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.logoBadge}>
        <Image
          source={require("../../assets/motomap_logo_white.png")}
          style={styles.logoImg}
          resizeMode="contain"
        />
      </TouchableOpacity>

      <Animated.View style={[styles.panel, { transform: [{ translateY: panelTranslate }] }]}>
        <View style={styles.panelHandle} />

        {error ? (
          <View style={styles.centerBox}>
            <Text style={styles.errorText}>{"\u26A0\uFE0F Ba\u011Flant\u0131 hatas\u0131"}</Text>
            <Text style={styles.errorSub}>{error}</Text>
          </View>
        ) : !data ? (
          <View style={styles.centerBox}>
            <ActivityIndicator color={colors.accentBlue} size="large" />
            <Text style={styles.loadingText}>{"Rota y\u00FCkleniyor..."}</Text>
          </View>
        ) : (
          <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
            <ModeSelector modes={RIDING_MODES} activeMode={activeMode} onSelect={setActiveMode} />

            <View style={styles.legend}>
              <View style={styles.legendItem}>
                <View style={[styles.legendDash, { backgroundColor: colors.googleBlue }]} />
                <Text style={styles.legendLabel}>Google Maps</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendDash, { backgroundColor: colors.accentBlue }]} />
                <Text style={styles.legendLabel}>MOTOMAP</Text>
              </View>
            </View>

            <RouteCompareCard
              googleDistM={data.google_stats.mesafe_m}
              googleTimeS={data.google_stats.sure_s}
              motomapDistM={stats?.mesafe_m ?? 0}
              motomapTimeS={stats?.sure_s ?? 0}
            />

            <Text style={styles.sectionTitle}>
              {RIDING_MODES.find((m) => m.key === activeMode)?.icon}{" "}
              {RIDING_MODES.find((m) => m.key === activeMode)?.label}{" Modu Detaylar\u0131"}
            </Text>

            {stats && (
              <View style={styles.statsGrid}>
                <StatCard label={"E\u011Flenceli Viraj"} value={String(stats.viraj_fun)} color={colors.accentBlue} icon={"\u{1F300}"} />
                <StatCard label={"Tehlikeli Viraj"} value={String(stats.viraj_tehlike)} color={colors.warning} icon={"\u26A0\uFE0F"} />
                <StatCard label={"Y\u00FCksek Risk"} value={String(stats.yuksek_risk)} color={colors.danger} icon={"\u{1F534}"} />
                <StatCard label={"Ort. E\u011Fim"} value={`%${(stats.ortalama_egim * 100).toFixed(1)}`} color={colors.info} icon={"\u26F0\uFE0F"} />
                <StatCard label={"\u015Eerit Payla\u015F\u0131m\u0131"} value={`${stats.serit_paylasimi} m`} color={colors.success} icon={"\u2702\uFE0F"} />
              </View>
            )}

            {/* Weather conditions */}
            {weather && roadConditions && (
              <>
                <Text style={styles.sectionTitle}>{"\uD83C\uDF24\uFE0F"} Hava Durumu</Text>
                <WeatherCard weather={weather} roadConditions={roadConditions} />
              </>
            )}
          </ScrollView>
        )}
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  map: { flex: 1 },
  logoBadge: {
    position: "absolute",
    top: 52,
    left: 16,
    backgroundColor: "rgba(8,28,80,0.88)",
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
  },
  logoImg: { width: 110, height: 38 },
  panel: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: PANEL_HEIGHT,
    backgroundColor: colors.bgPrimary,
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    paddingHorizontal: spacing.screenPadding,
    paddingTop: 10,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -6 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 24,
  },
  panelHandle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.surfaceBorder,
    alignSelf: "center",
    marginBottom: 14,
  },
  scrollContent: { paddingBottom: 8, gap: 14 },
  centerBox: { flex: 1, alignItems: "center", justifyContent: "center", gap: 14 },
  loadingText: { color: colors.textSecondary, fontSize: 14 },
  errorText: { color: colors.warning, fontSize: 16, fontWeight: "700" },
  errorSub: { color: colors.textTertiary, fontSize: 12, textAlign: "center" },
  legend: { flexDirection: "row", gap: 20 },
  legendItem: { flexDirection: "row", alignItems: "center", gap: 7 },
  legendDash: { width: 24, height: 3, borderRadius: 2 },
  legendLabel: { color: colors.textTertiary, fontSize: 12 },
  sectionTitle: {
    color: colors.textSecondary,
    fontSize: 13,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
  statsGrid: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
  weatherOverlay: {
    position: "absolute",
    top: 52,
    right: 16,
  },
  controlsOverlay: {
    position: "absolute",
    top: 100,
    left: 16,
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  reportToggle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "rgba(8,28,80,0.85)",
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
  },
  reportToggleActive: {
    backgroundColor: colors.accentBlue,
    borderColor: colors.accentBlue,
  },
  reportToggleText: { fontSize: 16 },
});
