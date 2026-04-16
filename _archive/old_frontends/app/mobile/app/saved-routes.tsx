// app/mobile/app/saved-routes.tsx
import { useRouter } from "expo-router";
import { useState } from "react";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import EmptyState from "../components/EmptyState";
import GlassCard from "../components/GlassCard";
import ScreenHeader from "../components/ScreenHeader";
import { useApp } from "../context/AppContext";
import { colors, spacing } from "../theme";
import { formatDist, formatTime } from "../utils/format";

export default function SavedRoutesScreen() {
  const router = useRouter();
  const { savedRoutes, toggleFavorite } = useApp();
  const [filter, setFilter] = useState<"all" | "favorites">("all");

  const filtered =
    filter === "favorites"
      ? savedRoutes.filter((r) => r.isFavorite)
      : savedRoutes;

  return (
    <View style={styles.container}>
      <ScreenHeader title={"Kay\u0131tl\u0131 Rotalar"} onBack={() => router.back()} />

      <View style={styles.filterRow}>
        <TouchableOpacity
          style={[styles.filterBtn, filter === "all" && styles.filterBtnActive]}
          onPress={() => setFilter("all")}
          activeOpacity={0.8}
        >
          <Text style={[styles.filterText, filter === "all" && styles.filterTextActive]}>
            {"T\u00FCm\u00FC"}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterBtn, filter === "favorites" && styles.filterBtnActive]}
          onPress={() => setFilter("favorites")}
          activeOpacity={0.8}
        >
          <Text style={[styles.filterText, filter === "favorites" && styles.filterTextActive]}>
            Favoriler
          </Text>
        </TouchableOpacity>
      </View>

      {filtered.length === 0 ? (
        <EmptyState
          icon={"\u{1F4CD}"}
          title={"Hen\u00FCz Rota Yok"}
          description={"Navigasyonu ba\u015Flatt\u0131\u011F\u0131nda rotalar\u0131n burada g\u00F6r\u00FCnecek."}
          actionLabel={"Rota Olu\u015Ftur"}
          onAction={() => router.push("/(tabs)/route")}
        />
      ) : (
        <ScrollView contentContainerStyle={styles.list} showsVerticalScrollIndicator={false}>
          {filtered.map((route) => (
            <GlassCard key={route.id} style={styles.routeCard}>
              <View style={styles.routeHeader}>
                <View style={styles.routeDots}>
                  <View style={[styles.dot, { backgroundColor: colors.success }]} />
                  <View style={styles.routeLine} />
                  <View style={[styles.dot, { backgroundColor: colors.warning }]} />
                </View>
                <View style={styles.routeLabels}>
                  <Text style={styles.routeLabel}>{route.originLabel}</Text>
                  <Text style={styles.routeLabel}>{route.destinationLabel}</Text>
                </View>
                <TouchableOpacity
                  onPress={() => toggleFavorite(route.id)}
                  accessibilityLabel={route.isFavorite ? "Favoriden kald\u0131r" : "Favoriye ekle"}
                >
                  <Text style={styles.starIcon}>{route.isFavorite ? "\u2605" : "\u2606"}</Text>
                </TouchableOpacity>
              </View>
              <View style={styles.routeStats}>
                <View style={styles.modeBadge}>
                  <Text style={styles.modeBadgeText}>{route.mode}</Text>
                </View>
                <Text style={styles.statText}>{formatDist(route.distanceM)}</Text>
                <Text style={styles.statText}>{formatTime(route.timeS)}</Text>
              </View>
            </GlassCard>
          ))}
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  filterRow: {
    flexDirection: "row",
    gap: 8,
    paddingHorizontal: spacing.screenPadding,
    marginBottom: 16,
  },
  filterBtn: {
    paddingVertical: 8,
    paddingHorizontal: 20,
    borderRadius: 10,
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
  },
  filterBtnActive: {
    borderColor: colors.accentBlue,
    backgroundColor: "rgba(61,139,255,0.2)",
  },
  filterText: { color: colors.textTertiary, fontSize: 13, fontWeight: "700" },
  filterTextActive: { color: colors.accentBlue },
  list: {
    paddingHorizontal: spacing.screenPadding,
    paddingBottom: 40,
    gap: 12,
  },
  routeCard: { gap: 12 },
  routeHeader: { flexDirection: "row", alignItems: "center", gap: 12 },
  routeDots: { alignItems: "center", gap: 2 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  routeLine: { width: 2, height: 16, backgroundColor: colors.surfaceBorder },
  routeLabels: { flex: 1 },
  routeLabel: { color: colors.textPrimary, fontSize: 13, fontWeight: "600" },
  starIcon: { color: colors.warning, fontSize: 22 },
  routeStats: { flexDirection: "row", alignItems: "center", gap: 10 },
  modeBadge: {
    backgroundColor: "rgba(61,139,255,0.2)",
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  modeBadgeText: { color: colors.accentBlue, fontSize: 11, fontWeight: "700" },
  statText: { color: colors.textTertiary, fontSize: 12 },
});