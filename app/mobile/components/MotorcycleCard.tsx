// app/mobile/components/MotorcycleCard.tsx
import { StyleSheet, Text, View } from "react-native";
import { colors } from "../theme";
import { Motorcycle } from "../types";
import GlassCard from "./GlassCard";

type Props = {
  motorcycle: Motorcycle;
  onPress: () => void;
};

const TYPE_ICONS: Record<string, string> = {
  naked: "\u{1F3CD}\uFE0F",
  sport: "\u{1F3CE}\uFE0F",
  touring: "\u{1F6E3}\uFE0F",
  adventure: "\u26F0\uFE0F",
  scooter: "\u{1F6F5}",
};

export default function MotorcycleCard({ motorcycle, onPress }: Props) {
  const icon = TYPE_ICONS[motorcycle.type] ?? "\u{1F3CD}\uFE0F";

  return (
    <GlassCard
      onPress={onPress}
      style={[styles.card, motorcycle.isActive && styles.activeCard]}
      accessibilityLabel={`${motorcycle.brand} ${motorcycle.model}`}
    >
      <Text style={styles.icon}>{icon}</Text>
      <View style={styles.info}>
        <Text style={styles.name}>
          {motorcycle.brand} {motorcycle.model}
        </Text>
        <Text style={styles.sub}>
          {motorcycle.cc}cc \u00B7{" "}
          {motorcycle.type.charAt(0).toUpperCase() + motorcycle.type.slice(1)}
        </Text>
      </View>
      {motorcycle.isActive && (
        <View style={styles.activeBadge}>
          <Text style={styles.activeBadgeText}>Aktif</Text>
        </View>
      )}
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
  },
  activeCard: {
    borderColor: colors.accentBlue,
    backgroundColor: "rgba(61,139,255,0.12)",
  },
  icon: { fontSize: 28 },
  info: { flex: 1 },
  name: { color: colors.textPrimary, fontSize: 16, fontWeight: "800" },
  sub: { color: colors.textTertiary, fontSize: 13, marginTop: 2 },
  activeBadge: {
    backgroundColor: colors.accentBlue,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  activeBadgeText: { color: "#fff", fontSize: 11, fontWeight: "700" },
});