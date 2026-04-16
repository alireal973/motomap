// app/mobile/components/MapLegend.tsx
import { StyleSheet, Text, TouchableOpacity, View, Animated } from "react-native";
import { useState, useRef, useEffect } from "react";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";

type SafetyLevel = {
  color: string;
  label: string;
  description: string;
};

type MapLegendProps = {
  isVisible?: boolean;
  onToggle?: () => void;
  position?: "bottom-left" | "bottom-right" | "top-left" | "top-right";
};

const SAFETY_LEVELS: SafetyLevel[] = [
  {
    color: "#22C55E", // green
    label: "Güvenli",
    description: "İdeal sürüş koşulları",
  },
  {
    color: "#F59E0B", // yellow
    label: "Dikkatli",
    description: "Hafif risk faktörleri mevcut",
  },
  {
    color: "#FF8C00", // orange
    label: "Uyarı",
    description: "Zorlu koşullar, dikkat gerekli",
  },
  {
    color: "#EF4444", // red
    label: "Tehlike",
    description: "Yüksek risk, çok dikkatli olun",
  },
];

const REPORT_TYPES = [
  { icon: "warning" as const, color: colors.warning, label: "Tehlike" },
  { icon: "construct" as const, color: colors.info, label: "Yol Çalışması" },
  { icon: "water" as const, color: colors.accentBlue, label: "Su Birikintisi" },
  { icon: "alert-circle" as const, color: colors.danger, label: "Kaza" },
];

export default function MapLegend({
  isVisible = false,
  onToggle,
  position = "bottom-left",
}: MapLegendProps) {
  const [expanded, setExpanded] = useState(isVisible);
  const heightAnim = useRef(new Animated.Value(isVisible ? 1 : 0)).current;

  useEffect(() => {
    Animated.timing(heightAnim, {
      toValue: expanded ? 1 : 0,
      duration: 250,
      useNativeDriver: false,
    }).start();
  }, [expanded]);

  const positionStyle = {
    "bottom-left": { bottom: spacing.xxl, left: spacing.md },
    "bottom-right": { bottom: spacing.xxl, right: spacing.md },
    "top-left": { top: spacing.xxl, left: spacing.md },
    "top-right": { top: spacing.xxl, right: spacing.md },
  }[position];

  const handleToggle = () => {
    setExpanded(!expanded);
    onToggle?.();
  };

  return (
    <View style={[styles.container, positionStyle]}>
      {/* Toggle Button */}
      <TouchableOpacity
        style={styles.toggleButton}
        onPress={handleToggle}
        activeOpacity={0.7}
      >
        <Ionicons
          name="color-palette-outline"
          size={20}
          color={colors.textPrimary}
        />
        <Text style={styles.toggleText}>Harita Açıklaması</Text>
        <Ionicons
          name={expanded ? "chevron-down" : "chevron-up"}
          size={18}
          color={colors.textTertiary}
        />
      </TouchableOpacity>

      {/* Expanded Content */}
      <Animated.View
        style={[
          styles.content,
          {
            maxHeight: heightAnim.interpolate({
              inputRange: [0, 1],
              outputRange: [0, 400],
            }),
            opacity: heightAnim,
          },
        ]}
      >
        {/* Safety Colors */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Güvenlik Seviyeleri</Text>
          {SAFETY_LEVELS.map((level, index) => (
            <View key={index} style={styles.legendItem}>
              <View style={[styles.colorLine, { backgroundColor: level.color }]} />
              <View style={styles.legendInfo}>
                <Text style={styles.legendLabel}>{level.label}</Text>
                <Text style={styles.legendDescription}>{level.description}</Text>
              </View>
            </View>
          ))}
        </View>

        {/* Report Markers */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Rapor İşaretleri</Text>
          <View style={styles.markersGrid}>
            {REPORT_TYPES.map((type, index) => (
              <View key={index} style={styles.markerItem}>
                <View style={[styles.markerIcon, { backgroundColor: `${type.color}20` }]}>
                  <Ionicons name={type.icon} size={16} color={type.color} />
                </View>
                <Text style={styles.markerLabel}>{type.label}</Text>
              </View>
            ))}
          </View>
        </View>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    maxWidth: 280,
    zIndex: 100,
  },
  toggleButton: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.bgSecondary,
    borderRadius: radius.md,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    gap: spacing.sm,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
  },
  toggleText: {
    flex: 1,
    color: colors.textPrimary,
    fontSize: 13,
    fontWeight: "600",
  },
  content: {
    backgroundColor: colors.bgSecondary,
    borderRadius: radius.md,
    marginTop: spacing.sm,
    overflow: "hidden",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
  },
  section: {
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.surfaceBorder,
  },
  sectionTitle: {
    color: colors.textSecondary,
    fontSize: 11,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.5,
    marginBottom: spacing.sm,
  },
  legendItem: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.sm,
  },
  colorLine: {
    width: 24,
    height: 4,
    borderRadius: 2,
    marginRight: spacing.sm,
  },
  legendInfo: {
    flex: 1,
  },
  legendLabel: {
    color: colors.textPrimary,
    fontSize: 13,
    fontWeight: "600",
  },
  legendDescription: {
    color: colors.textTertiary,
    fontSize: 11,
    marginTop: 1,
  },
  markersGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
  },
  markerItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    width: "48%",
  },
  markerIcon: {
    width: 24,
    height: 24,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
  },
  markerLabel: {
    color: colors.textSecondary,
    fontSize: 12,
  },
});
