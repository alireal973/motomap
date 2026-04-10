import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { colors, typography, spacing, radius } from "../theme";

type WeatherData = {
  condition: string;
  temperature_celsius: number;
  humidity_percent: number;
  wind_speed_ms: number;
  visibility_meters: number;
};

type RoadCondition = {
  surface_condition: string;
  overall_safety_score: number;
  lane_splitting_modifier: number;
  warnings: string[];
};

type Props = {
  weather: WeatherData | null;
  roadConditions: RoadCondition | null;
  isLoading?: boolean;
  compact?: boolean;
};

const WEATHER_ICONS: Record<string, string> = {
  clear: "\u2600\uFE0F", clouds: "\u2601\uFE0F", rain: "\uD83C\uDF27\uFE0F",
  drizzle: "\uD83C\uDF26\uFE0F", thunderstorm: "\u26C8\uFE0F", snow: "\u2744\uFE0F",
  mist: "\uD83C\uDF2B\uFE0F", fog: "\uD83C\uDF2B\uFE0F", haze: "\uD83C\uDF01",
};

const CONDITION_TR: Record<string, string> = {
  clear: "Acik", clouds: "Bulutlu", rain: "Yagmurlu", drizzle: "Ciseleyen",
  thunderstorm: "Firtinali", snow: "Karli", mist: "Sisli", fog: "Puslu", haze: "Dumanli",
};

function getSafetyColor(pct: number): string {
  if (pct >= 80) return colors.success;
  if (pct >= 60) return colors.warning;
  return colors.danger;
}

export function WeatherCard({ weather, roadConditions, isLoading, compact }: Props) {
  if (isLoading) {
    return (
      <View style={[styles.container, compact && styles.compact]}>
        <Text style={styles.loadingText}>Hava durumu yukleniyor...</Text>
      </View>
    );
  }
  if (!weather || !roadConditions) return null;

  const icon = WEATHER_ICONS[weather.condition] || "\uD83C\uDF21\uFE0F";
  const safetyPct = Math.round(roadConditions.overall_safety_score * 100);

  if (compact) {
    return (
      <View style={[styles.container, styles.compact]}>
        <Text style={styles.iconLg}>{icon}</Text>
        <Text style={styles.tempCompact}>{Math.round(weather.temperature_celsius)}\u00B0C</Text>
        <View style={[styles.badge, { backgroundColor: getSafetyColor(safetyPct) }]}>
          <Text style={styles.badgeText}>{safetyPct}%</Text>
        </View>
      </View>
    );
  }

  return (
    <LinearGradient
      colors={["rgba(255,255,255,0.08)", "rgba(255,255,255,0.02)"]}
      style={styles.container}
    >
      <View style={styles.header}>
        <Text style={styles.iconLg}>{icon}</Text>
        <View>
          <Text style={styles.temp}>{Math.round(weather.temperature_celsius)}\u00B0C</Text>
          <Text style={styles.condition}>{CONDITION_TR[weather.condition] || weather.condition}</Text>
        </View>
      </View>
      <View style={styles.stats}>
        <Stat icon="\uD83D\uDCA8" value={`${weather.wind_speed_ms.toFixed(1)} m/s`} label="Ruzgar" />
        <Stat icon="\uD83D\uDCA7" value={`${weather.humidity_percent}%`} label="Nem" />
        <Stat icon="\uD83D\uDC41\uFE0F" value={weather.visibility_meters >= 10000 ? ">10km" : `${(weather.visibility_meters / 1000).toFixed(1)}km`} label="Gorus" />
      </View>
      <View style={styles.safetyRow}>
        <Text style={styles.safetyLabel}>Yol Guvenligi</Text>
        <View style={styles.bar}>
          <View style={[styles.barFill, { width: `${safetyPct}%`, backgroundColor: getSafetyColor(safetyPct) }]} />
        </View>
        <Text style={styles.safetyVal}>{safetyPct}%</Text>
      </View>
      <Text style={styles.laneInfo}>
        Serit Paylasimi: {Math.round(roadConditions.lane_splitting_modifier * 100)}% uygun
      </Text>
    </LinearGradient>
  );
}

function Stat({ icon, value, label }: { icon: string; value: string; label: string }) {
  return (
    <View style={styles.statItem}>
      <Text style={{ fontSize: 18 }}>{icon}</Text>
      <Text style={styles.statVal}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { borderRadius: radius.lg, padding: spacing.md, marginBottom: spacing.md },
  compact: { flexDirection: "row", alignItems: "center", padding: spacing.sm, backgroundColor: "rgba(255,255,255,0.06)" },
  header: { flexDirection: "row", alignItems: "center", marginBottom: spacing.md },
  iconLg: { fontSize: 40, marginRight: spacing.md },
  temp: { fontSize: 28, fontWeight: "700", color: colors.textPrimary },
  tempCompact: { fontSize: 16, fontWeight: "600", color: colors.textPrimary, marginRight: spacing.sm },
  condition: { fontSize: 14, color: colors.textSecondary },
  stats: { flexDirection: "row", justifyContent: "space-around", marginBottom: spacing.md },
  statItem: { alignItems: "center" },
  statVal: { fontSize: 14, fontWeight: "600", color: colors.textPrimary },
  statLabel: { fontSize: 11, color: colors.textSecondary },
  safetyRow: { marginBottom: spacing.sm },
  safetyLabel: { fontSize: 11, color: colors.textSecondary, marginBottom: 4 },
  bar: { height: 6, backgroundColor: "rgba(255,255,255,0.15)", borderRadius: 3, overflow: "hidden" },
  barFill: { height: "100%", borderRadius: 3 },
  safetyVal: { fontSize: 14, fontWeight: "600", color: colors.textPrimary, textAlign: "right", marginTop: 2 },
  badge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 12 },
  badgeText: { fontSize: 11, fontWeight: "600", color: "#fff" },
  laneInfo: { fontSize: 13, color: colors.textPrimary, paddingTop: spacing.sm, borderTopWidth: 1, borderTopColor: "rgba(255,255,255,0.1)" },
  loadingText: { fontSize: 14, color: colors.textSecondary, textAlign: "center", padding: spacing.md },
});
