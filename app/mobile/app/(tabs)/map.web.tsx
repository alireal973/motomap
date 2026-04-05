import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Dimensions,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { useRouter } from "expo-router";
import { colors, spacing } from "../../theme";
import ModeSelector from "../../components/ModeSelector";
import RouteCompareCard from "../../components/RouteCompareCard";
import StatCard from "../../components/StatCard";
import { RouteData, RIDING_MODES } from "../../types";
import { fetchRoute } from "../../utils/api";
import { formatDist, formatTime } from "../../utils/format";

const { height } = Dimensions.get("window");

export default function MapScreenWeb() {
  const router = useRouter();
  const [data, setData] = useState<RouteData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeMode, setActiveMode] = useState("standart");

  useEffect(() => {
    fetchRoute()
      .then((d) => setData(d))
      .catch((e) => setError(String(e)));
  }, []);

  const mode = data?.modes[activeMode];
  const stats = mode?.stats;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} activeOpacity={0.8}>
          <Image
            source={require("../../assets/motomap_logo_white.png")}
            style={styles.logoImg}
            resizeMode="contain"
          />
        </TouchableOpacity>
      </View>

      <View style={styles.mapPlaceholder}>
        <View style={styles.routeViz}>
          <View style={styles.originDot} />
          <View style={styles.routeLine}>
            <View style={[styles.routeSegment, { backgroundColor: colors.googleBlue, flex: 1 }]} />
            <View style={[styles.routeSegment, { backgroundColor: colors.accentBlue, flex: 1 }]} />
          </View>
          <View style={styles.destDot} />
        </View>
        {data && (
          <View style={styles.mapLabels}>
            <Text style={styles.mapLabel}>{data.origin_label}</Text>
            <Text style={styles.mapLabelDest}>{data.destination_label}</Text>
          </View>
        )}
        <Text style={styles.mapNote}>{"\ud83d\udcf1 Harita g\u00f6r\u00fcn\u00fcm\u00fc i\u00e7in Expo Go uygulamas\u0131n\u0131 kullan\u0131n"}</Text>
      </View>

      <View style={styles.panel}>
        {error ? (
          <View style={styles.centerBox}>
            <Text style={styles.errorText}>{"\u26a0\ufe0f Ba\u011flant\u0131 hatas\u0131"}</Text>
            <Text style={styles.errorSub}>{error}</Text>
          </View>
        ) : !data ? (
          <View style={styles.centerBox}>
            <ActivityIndicator color={colors.accentBlue} size="large" />
            <Text style={styles.loadingText}>Rota y\u00fckleniyor...</Text>
          </View>
        ) : (
          <ScrollView showsVerticalScrollIndicator={false}>
            <ModeSelector modes={RIDING_MODES} activeMode={activeMode} onSelect={setActiveMode} />
            <View style={{ height: 14 }} />

            <RouteCompareCard
              googleDistM={data.google_stats.mesafe_m}
              googleTimeS={data.google_stats.sure_s}
              motomapDistM={stats?.mesafe_m ?? 0}
              motomapTimeS={stats?.sure_s ?? 0}
            />
            <View style={{ height: 16 }} />

            <Text style={styles.sectionTitle}>
              {RIDING_MODES.find((m) => m.key === activeMode)?.icon}{" "}
              {RIDING_MODES.find((m) => m.key === activeMode)?.label} Modu Detaylar\u0131
            </Text>

            {stats && (
              <View style={styles.statsGrid}>
                <StatCard label="E\u011flenceli Viraj" value={String(stats.viraj_fun)} color={colors.accentBlue} icon="\ud83c\udf00" />
                <StatCard label="Tehlikeli Viraj" value={String(stats.viraj_tehlike)} color={colors.warning} icon="\u26a0\ufe0f" />
                <StatCard label="Y\u00fcksek Risk" value={String(stats.yuksek_risk)} color={colors.danger} icon="\ud83d\udd34" />
                <StatCard label="Ort. E\u011fim" value={`%${(stats.ortalama_egim * 100).toFixed(1)}`} color={colors.info} icon="\u26f0\ufe0f" />
              </View>
            )}
          </ScrollView>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  header: {
    paddingTop: 52,
    paddingHorizontal: 20,
    paddingBottom: 12,
  },
  backBtn: {
    alignSelf: "flex-start",
    backgroundColor: "rgba(8,28,80,0.88)",
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
  },
  logoImg: {
    width: 110,
    height: 38,
  },
  mapPlaceholder: {
    height: height * 0.28,
    backgroundColor: "rgba(61,139,255,0.07)",
    borderBottomWidth: 1,
    borderColor: colors.surfaceBorder,
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    paddingHorizontal: 24,
  },
  routeViz: {
    flexDirection: "row",
    alignItems: "center",
    width: "80%",
    gap: 0,
  },
  originDot: {
    width: 14,
    height: 14,
    borderRadius: 7,
    backgroundColor: colors.success,
    borderWidth: 2,
    borderColor: "#14532d",
  },
  routeLine: {
    flex: 1,
    height: 4,
    flexDirection: "row",
    gap: 0,
    marginHorizontal: 4,
  },
  routeSegment: { height: "100%" },
  destDot: {
    width: 14,
    height: 14,
    borderRadius: 7,
    backgroundColor: colors.warning,
    borderWidth: 2,
    borderColor: "#7c2d12",
  },
  mapLabels: {
    flexDirection: "row",
    justifyContent: "space-between",
    width: "80%",
  },
  mapLabel: { color: colors.success, fontSize: 11, fontWeight: "700" },
  mapLabelDest: { color: colors.warning, fontSize: 11, fontWeight: "700" },
  mapNote: { color: colors.textTertiary, fontSize: 11, textAlign: "center" },
  panel: {
    flex: 1,
    paddingHorizontal: 20,
    paddingTop: 16,
  },
  centerBox: { flex: 1, alignItems: "center", justifyContent: "center", gap: 14 },
  loadingText: { color: colors.textSecondary, fontSize: 14 },
  errorText: { color: colors.warning, fontSize: 16, fontWeight: "700" },
  errorSub: { color: colors.textTertiary, fontSize: 12, textAlign: "center" },
  sectionTitle: { color: colors.textSecondary, fontSize: 13, fontWeight: "700", marginBottom: 10 },
  statsGrid: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
});