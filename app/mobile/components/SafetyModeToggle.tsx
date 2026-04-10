import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { colors, spacing, radius } from "../theme";

type ViewMode = "standard" | "safety" | "lane-split";

type Props = {
  activeMode: ViewMode;
  onModeChange: (mode: ViewMode) => void;
};

const MODES: { key: ViewMode; icon: string; label: string }[] = [
  { key: "standard", icon: "\uD83D\uDDFA\uFE0F", label: "Standart" },
  { key: "safety", icon: "\uD83D\uDEE1\uFE0F", label: "Guvenlik" },
  { key: "lane-split", icon: "\u2702\uFE0F", label: "Serit" },
];

export function SafetyModeToggle({ activeMode, onModeChange }: Props) {
  return (
    <View style={styles.container}>
      {MODES.map((m) => (
        <TouchableOpacity
          key={m.key}
          style={[styles.btn, activeMode === m.key && styles.btnActive]}
          onPress={() => onModeChange(m.key)}
        >
          <Text style={styles.icon}>{m.icon}</Text>
          <Text style={[styles.label, activeMode === m.key && styles.labelActive]}>{m.label}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flexDirection: "row", backgroundColor: "rgba(255,255,255,0.06)", borderRadius: radius.lg, padding: 4 },
  btn: { flexDirection: "row", alignItems: "center", paddingHorizontal: spacing.md, paddingVertical: spacing.sm, borderRadius: radius.md },
  btnActive: { backgroundColor: colors.accentBlue },
  icon: { fontSize: 14, marginRight: 4 },
  label: { fontSize: 12, color: colors.textSecondary },
  labelActive: { color: colors.textPrimary },
});
