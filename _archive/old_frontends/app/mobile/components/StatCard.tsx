// app/mobile/components/StatCard.tsx
import { StyleSheet, Text, View } from "react-native";
import { colors } from "../theme";

type Props = {
  label: string;
  value: string;
  icon: string;
  color: string;
};

export default function StatCard({ label, value, icon, color }: Props) {
  return (
    <View style={styles.card}>
      <Text style={styles.icon}>{icon}</Text>
      <Text style={[styles.value, { color }]}>{value}</Text>
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: "47%",
    backgroundColor: "rgba(61,139,255,0.1)",
    borderWidth: 1,
    borderColor: "rgba(61,139,255,0.25)",
    borderRadius: 16,
    padding: 14,
    alignItems: "center",
    gap: 4,
  },
  icon: { fontSize: 22, marginBottom: 2 },
  value: { fontSize: 24, fontWeight: "800" },
  label: {
    color: colors.textTertiary,
    fontSize: 11,
    textAlign: "center",
    letterSpacing: 0.5,
  },
});