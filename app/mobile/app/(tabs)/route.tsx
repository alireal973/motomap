// app/mobile/app/(tabs)/route.tsx
import { useRouter } from "expo-router";
import { useState } from "react";
import {
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import AppButton from "../../components/AppButton";
import GlassCard from "../../components/GlassCard";
import ScreenHeader from "../../components/ScreenHeader";
import { colors, spacing } from "../../theme";

type ModeOption = {
  key: string;
  icon: string;
  title: string;
  description: string;
  time: string;
  distance: string;
  badge?: string;
  badgeColor?: string;
};

const MODES: ModeOption[] = [
  {
    key: "standart",
    icon: "\u26A1",
    title: "En H\u0131zl\u0131",
    description: "Otoban ve ana yollar\u0131 kullanarak\nen k\u0131sa s\u00FCrede var.",
    time: "45 dk",
    distance: "32 km",
  },
  {
    key: "viraj_keyfi",
    icon: "\u2715",
    title: "Virajl\u0131 Yollar",
    description: "S\u00FCr\u00FC\u015F keyfini maksimize eden,\nbol virajl\u0131 alternatif rota.",
    time: "1s 15dk",
    distance: "48 km",
    badge: "\u00D6nerilen",
    badgeColor: colors.accentBlue,
  },
  {
    key: "guvenli",
    icon: "\u25B3",
    title: "Macera / Arazi",
    description: "Toprak yollar ve orman i\u00E7i\nmanzaral\u0131 zorlu rota.",
    time: "1s 40dk",
    distance: "41 km",
    badge: "Toprak Yol Uyar\u0131s\u0131",
    badgeColor: colors.warning,
  },
];

export default function RouteSelectionScreen() {
  const router = useRouter();
  const [destination, setDestination] = useState("");
  const [selectedMode, setSelectedMode] = useState("viraj_keyfi");

  return (
    <View style={styles.container}>
      <ScreenHeader title="Rota Se\u00E7imi" />

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <GlassCard style={styles.locationCard}>
          <View style={styles.locationRow}>
            <View style={[styles.locationDot, { backgroundColor: colors.success }]} />
            <View style={styles.locationTextBlock}>
              <Text style={styles.locationLabel}>Nereden</Text>
              <Text style={styles.locationValue}>Mevcut Konum</Text>
            </View>
          </View>
          <View style={styles.locationDivider} />
          <View style={styles.locationRow}>
            <View style={[styles.locationDot, { backgroundColor: colors.warning }]} />
            <View style={styles.locationTextBlock}>
              <Text style={styles.locationLabel}>Nereye</Text>
              <TextInput
                style={styles.locationInput}
                placeholder="Hedef ara..."
                placeholderTextColor={colors.textTertiary}
                value={destination}
                onChangeText={setDestination}
              />
            </View>
          </View>
        </GlassCard>

        <Text style={styles.sectionTitle}>{"S\u00FCr\u00FC\u015F Tarz\u0131n\u0131 Se\u00E7"}</Text>

        {MODES.map((m) => {
          const isActive = selectedMode === m.key;
          return (
            <GlassCard
              key={m.key}
              onPress={() => setSelectedMode(m.key)}
              style={[styles.modeCard, isActive && styles.modeCardActive]}
              accessibilityLabel={m.title}
            >
              <View
                style={[
                  styles.modeIconWrap,
                  isActive && styles.modeIconWrapActive,
                ]}
              >
                <Text style={styles.modeIcon}>{m.icon}</Text>
              </View>
              <View style={styles.modeTextBlock}>
                <View style={styles.modeTopRow}>
                  <Text style={[styles.modeTitle, isActive && styles.modeTitleActive]}>
                    {m.title}
                  </Text>
                  <Text style={[styles.modeTime, isActive && styles.modeTimeActive]}>
                    {m.time}
                  </Text>
                </View>
                <Text style={[styles.modeDesc, isActive && styles.modeDescActive]}>
                  {m.description}
                </Text>
                <View style={styles.modeTagRow}>
                  {m.badge && (
                    <View style={[styles.badge, { backgroundColor: m.badgeColor }]}>
                      <Text style={styles.badgeText}>{m.badge}</Text>
                    </View>
                  )}
                  <View style={styles.distTag}>
                    <Text style={styles.distTagText}>{m.distance}</Text>
                  </View>
                </View>
              </View>
            </GlassCard>
          );
        })}

        <AppButton
          title={"Rotay\u0131 Hesapla"}
          onPress={() => router.push("/(tabs)/map")}
          style={{ marginTop: spacing.md }}
          accessibilityLabel={"Rotay\u0131 hesapla"}
        />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  scroll: { paddingHorizontal: spacing.screenPadding, paddingBottom: 40, gap: 14 },
  locationCard: { paddingVertical: 4, paddingHorizontal: 18 },
  locationRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 14,
    gap: 14,
  },
  locationDot: { width: 12, height: 12, borderRadius: 6 },
  locationTextBlock: { flex: 1 },
  locationLabel: {
    fontSize: 11,
    color: colors.textTertiary,
    fontWeight: "600",
    letterSpacing: 0.3,
    marginBottom: 2,
  },
  locationValue: { fontSize: 15, fontWeight: "700", color: colors.textPrimary },
  locationInput: {
    fontSize: 15,
    fontWeight: "400",
    color: colors.textPrimary,
    padding: 0,
  },
  locationDivider: {
    height: 1,
    backgroundColor: colors.surfaceBorder,
    marginLeft: 26,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: colors.textPrimary,
    marginBottom: 4,
    marginTop: 6,
  },
  modeCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 16,
  },
  modeCardActive: {
    borderColor: colors.accentBlue,
    backgroundColor: "rgba(61,139,255,0.12)",
  },
  modeIconWrap: {
    width: 48,
    height: 48,
    borderRadius: 14,
    backgroundColor: "rgba(255,255,255,0.08)",
    alignItems: "center",
    justifyContent: "center",
  },
  modeIconWrapActive: { backgroundColor: colors.accentBlue },
  modeIcon: { fontSize: 20, color: colors.textPrimary },
  modeTextBlock: { flex: 1, gap: 4 },
  modeTopRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  modeTitle: { fontSize: 15, fontWeight: "800", color: colors.textSecondary },
  modeTitleActive: { color: colors.textPrimary },
  modeTime: { fontSize: 14, fontWeight: "700", color: colors.textTertiary },
  modeTimeActive: { color: colors.textPrimary },
  modeDesc: { fontSize: 13, color: colors.textTertiary, lineHeight: 19 },
  modeDescActive: { color: colors.textSecondary },
  modeTagRow: { flexDirection: "row", gap: 8, marginTop: 6, flexWrap: "wrap" },
  badge: { borderRadius: 8, paddingHorizontal: 10, paddingVertical: 4 },
  badgeText: { fontSize: 12, fontWeight: "700", color: "#fff" },
  distTag: {
    backgroundColor: "rgba(255,255,255,0.12)",
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  distTagText: { fontSize: 12, fontWeight: "600", color: colors.textSecondary },
});