// app/mobile/components/ModeSelector.tsx
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { colors } from "../theme";
import { RidingModeInfo } from "../types";

type Props = {
  modes: RidingModeInfo[];
  activeMode: string;
  onSelect: (key: string) => void;
};

export default function ModeSelector({ modes, activeMode, onSelect }: Props) {
  return (
    <View style={styles.row}>
      {modes.map((m) => {
        const isActive = activeMode === m.key;
        return (
          <TouchableOpacity
            key={m.key}
            style={[styles.btn, isActive && styles.btnActive]}
            onPress={() => onSelect(m.key)}
            activeOpacity={0.8}
            accessibilityRole="button"
            accessibilityLabel={m.label}
          >
            <Text style={styles.icon}>{m.icon}</Text>
            <Text style={[styles.text, isActive && styles.textActive]}>
              {m.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: "row", gap: 8 },
  btn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 5,
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: colors.surfaceBorder,
    backgroundColor: colors.surfaceGlass,
  },
  btnActive: {
    borderColor: colors.accentBlue,
    backgroundColor: "rgba(61,139,255,0.2)",
  },
  icon: { fontSize: 14 },
  text: { color: colors.textTertiary, fontSize: 12, fontWeight: "700" },
  textActive: { color: colors.accentBlue },
});