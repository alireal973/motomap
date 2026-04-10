// app/mobile/components/RouteInfoPanel.tsx
import { StyleSheet, Text, TouchableOpacity, View, ScrollView } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";
import GlassCard from "./GlassCard";
import WeatherBadge from "./WeatherBadge";

type SafetyLevel = "safe" | "caution" | "warning" | "danger";

type WeatherInfo = {
  condition: string;
  temperature: number;
  icon: string;
};

type RouteInfoPanelProps = {
  distance: number; // in km
  duration: number; // in minutes
  safetyScore?: number; // 0-100
  safetyLevel?: SafetyLevel;
  weather?: WeatherInfo;
  elevationGain?: number; // in meters
  curveCount?: number;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
  onStartNavigation?: () => void;
  onSaveRoute?: () => void;
  onShareRoute?: () => void;
};

const SAFETY_CONFIG: Record<SafetyLevel, { color: string; label: string }> = {
  safe: { color: colors.success, label: "Güvenli" },
  caution: { color: colors.warning, label: "Dikkatli Ol" },
  warning: { color: "#FF8C00", label: "Uyarı" },
  danger: { color: colors.danger, label: "Tehlikeli" },
};

export default function RouteInfoPanel({
  distance,
  duration,
  safetyScore,
  safetyLevel = "safe",
  weather,
  elevationGain,
  curveCount,
  isExpanded = false,
  onToggleExpand,
  onStartNavigation,
  onSaveRoute,
  onShareRoute,
}: RouteInfoPanelProps) {
  const formatDuration = (mins: number): string => {
    const hours = Math.floor(mins / 60);
    const minutes = mins % 60;
    if (hours === 0) return `${minutes} dk`;
    if (minutes === 0) return `${hours} sa`;
    return `${hours} sa ${minutes} dk`;
  };

  const formatDistance = (km: number): string => {
    if (km < 1) return `${Math.round(km * 1000)} m`;
    return `${km.toFixed(1)} km`;
  };

  const safetyConfig = SAFETY_CONFIG[safetyLevel];

  return (
    <GlassCard style={styles.container}>
      {/* Drag Handle */}
      <TouchableOpacity style={styles.dragHandle} onPress={onToggleExpand}>
        <View style={styles.handleBar} />
      </TouchableOpacity>

      {/* Main Stats */}
      <View style={styles.mainStats}>
        <View style={styles.statItem}>
          <Ionicons name="navigate-outline" size={20} color={colors.accentBlue} />
          <Text style={styles.statValue}>{formatDistance(distance)}</Text>
          <Text style={styles.statLabel}>Mesafe</Text>
        </View>

        <View style={styles.statDivider} />

        <View style={styles.statItem}>
          <Ionicons name="time-outline" size={20} color={colors.accentBlue} />
          <Text style={styles.statValue}>{formatDuration(duration)}</Text>
          <Text style={styles.statLabel}>Süre</Text>
        </View>

        {safetyScore !== undefined && (
          <>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Ionicons name="shield-checkmark" size={20} color={safetyConfig.color} />
              <Text style={[styles.statValue, { color: safetyConfig.color }]}>
                {safetyScore}
              </Text>
              <Text style={styles.statLabel}>{safetyConfig.label}</Text>
            </View>
          </>
        )}
      </View>

      {/* Expanded Content */}
      {isExpanded && (
        <ScrollView style={styles.expandedContent} showsVerticalScrollIndicator={false}>
          {/* Weather */}
          {weather && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Hava Durumu</Text>
              <View style={styles.weatherRow}>
                <WeatherBadge
                  temp={`${weather.temperature}°`}
                  description={weather.condition}
                  city=""
                />
              </View>
            </View>
          )}

          {/* Route Details */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Rota Detayları</Text>
            <View style={styles.detailsGrid}>
              {elevationGain !== undefined && (
                <View style={styles.detailItem}>
                  <Ionicons name="trending-up" size={18} color={colors.textSecondary} />
                  <Text style={styles.detailValue}>{elevationGain} m</Text>
                  <Text style={styles.detailLabel}>Yükseklik</Text>
                </View>
              )}
              {curveCount !== undefined && (
                <View style={styles.detailItem}>
                  <Ionicons name="git-compare" size={18} color={colors.textSecondary} />
                  <Text style={styles.detailValue}>{curveCount}</Text>
                  <Text style={styles.detailLabel}>Viraj</Text>
                </View>
              )}
            </View>
          </View>

          {/* Safety Legend */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Güvenlik Renkleri</Text>
            <View style={styles.legendRow}>
              <View style={styles.legendItem}>
                <View style={[styles.legendColor, { backgroundColor: colors.success }]} />
                <Text style={styles.legendText}>Güvenli</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendColor, { backgroundColor: colors.warning }]} />
                <Text style={styles.legendText}>Dikkatli</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendColor, { backgroundColor: "#FF8C00" }]} />
                <Text style={styles.legendText}>Uyarı</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendColor, { backgroundColor: colors.danger }]} />
                <Text style={styles.legendText}>Tehlike</Text>
              </View>
            </View>
          </View>
        </ScrollView>
      )}

      {/* Action Buttons */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={onSaveRoute}
          activeOpacity={0.7}
        >
          <Ionicons name="bookmark-outline" size={20} color={colors.textSecondary} />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.primaryButton}
          onPress={onStartNavigation}
          activeOpacity={0.85}
        >
          <Ionicons name="navigate" size={20} color="#FFFFFF" />
          <Text style={styles.primaryButtonText}>Navigasyonu Başlat</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={onShareRoute}
          activeOpacity={0.7}
        >
          <Ionicons name="share-outline" size={20} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: spacing.md,
    paddingTop: spacing.sm,
  },
  dragHandle: {
    alignItems: "center",
    paddingVertical: spacing.xs,
    marginBottom: spacing.sm,
  },
  handleBar: {
    width: 40,
    height: 4,
    backgroundColor: colors.surfaceBorder,
    borderRadius: 2,
  },
  mainStats: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    paddingVertical: spacing.sm,
  },
  statItem: {
    alignItems: "center",
    flex: 1,
  },
  statValue: {
    color: colors.textPrimary,
    fontSize: 20,
    fontWeight: "700",
    marginTop: spacing.xs,
  },
  statLabel: {
    color: colors.textTertiary,
    fontSize: 12,
    marginTop: 2,
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: colors.surfaceBorder,
  },
  expandedContent: {
    maxHeight: 250,
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.surfaceBorder,
  },
  section: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    color: colors.textSecondary,
    fontSize: 13,
    fontWeight: "600",
    marginBottom: spacing.sm,
  },
  weatherRow: {
    flexDirection: "row",
  },
  detailsGrid: {
    flexDirection: "row",
    gap: spacing.lg,
  },
  detailItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  detailValue: {
    color: colors.textPrimary,
    fontSize: 14,
    fontWeight: "600",
  },
  detailLabel: {
    color: colors.textTertiary,
    fontSize: 12,
  },
  legendRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.md,
  },
  legendItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  legendColor: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  legendText: {
    color: colors.textSecondary,
    fontSize: 12,
  },
  actions: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.surfaceBorder,
  },
  secondaryButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.surfaceGlass,
    alignItems: "center",
    justifyContent: "center",
  },
  primaryButton: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.accentBlue,
    borderRadius: radius.pill,
    paddingVertical: spacing.md,
    gap: spacing.sm,
  },
  primaryButtonText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "700",
  },
});
