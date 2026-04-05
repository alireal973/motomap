// app/mobile/components/RouteCompareCard.tsx
import { StyleSheet, Text, View } from "react-native";
import { colors } from "../theme";
import { formatDist, formatTime } from "../utils/format";

type Props = {
  googleDistM: number;
  googleTimeS: number;
  motomapDistM: number;
  motomapTimeS: number;
};

export default function RouteCompareCard({
  googleDistM,
  googleTimeS,
  motomapDistM,
  motomapTimeS,
}: Props) {
  return (
    <View style={styles.container}>
      <CompareColumn
        label="Google"
        distance={formatDist(googleDistM)}
        time={formatTime(googleTimeS)}
        color={colors.googleBlue}
      />
      <View style={styles.divider} />
      <CompareColumn
        label="MOTOMAP"
        distance={formatDist(motomapDistM)}
        time={formatTime(motomapTimeS)}
        color={colors.accentBlue}
      />
    </View>
  );
}

function CompareColumn({
  label,
  distance,
  time,
  color,
}: {
  label: string;
  distance: string;
  time: string;
  color: string;
}) {
  return (
    <View style={styles.column}>
      <View style={[styles.dot, { backgroundColor: color }]} />
      <Text style={styles.label}>{label}</Text>
      <Text style={[styles.value, { color }]}>{distance}</Text>
      <Text style={styles.sub}>{time}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    backgroundColor: "rgba(61,139,255,0.08)",
    borderWidth: 1,
    borderColor: "rgba(61,139,255,0.2)",
    borderRadius: 18,
    padding: 16,
    alignItems: "center",
  },
  column: { flex: 1, alignItems: "center", gap: 4 },
  dot: { width: 8, height: 8, borderRadius: 4, marginBottom: 2 },
  label: {
    color: colors.textTertiary,
    fontSize: 11,
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  value: { fontSize: 22, fontWeight: "800" },
  sub: { color: colors.textSecondary, fontSize: 13 },
  divider: {
    width: 1,
    height: 50,
    backgroundColor: colors.surfaceBorder,
    marginHorizontal: 16,
  },
});