// app/mobile/components/WeatherBadge.tsx
import { StyleSheet, Text, View } from "react-native";
import { colors } from "../theme";
import GlassCard from "./GlassCard";

type Props = {
  temp: string;
  description: string;
  city: string;
};

export default function WeatherBadge({ temp, description, city }: Props) {
  return (
    <GlassCard style={styles.card}>
      <View style={styles.left}>
        <Text style={styles.weatherIcon}>{"\u{1F324}"}</Text>
        <View>
          <Text style={styles.temp}>
            {temp} {description}
          </Text>
          <Text style={styles.sub}>{"S\u00FCr\u00FC\u015F i\u00E7in ideal hava"}</Text>
        </View>
      </View>
      <Text style={styles.city}>{city}</Text>
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 14,
    paddingHorizontal: 18,
  },
  left: { flexDirection: "row", alignItems: "center", gap: 12 },
  weatherIcon: { fontSize: 26 },
  temp: { color: colors.textPrimary, fontSize: 15, fontWeight: "700" },
  sub: { color: colors.textTertiary, fontSize: 12, marginTop: 2 },
  city: { color: colors.textPrimary, fontSize: 15, fontWeight: "700" },
});