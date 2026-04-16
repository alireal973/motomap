// app/mobile/app/(tabs)/index.tsx
import { useRouter } from "expo-router";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import GlassCard from "../../components/GlassCard";
import WeatherBadge from "../../components/WeatherBadge";
import EmptyState from "../../components/EmptyState";
import { useApp } from "../../context/AppContext";
import { colors, spacing, glowShadow } from "../../theme";

export default function DashboardScreen() {
  const router = useRouter();
  const { userMode, savedRoutes } = useApp();

  const isWork = userMode === "work";
  const greeting = isWork ? "HO\u015E GELD\u0130N, KURYE" : "HO\u015E GELD\u0130N, S\u00DCR\u00DCC\u00DC";

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <Text style={styles.greeting}>{greeting}</Text>
            <Text style={styles.headerTitle}>MOTOMAP</Text>
          </View>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>M</Text>
          </View>
        </View>

        <WeatherBadge temp="18\u00B0C" description="G\u00FCne\u015Fli" city="\u0130stanbul" />

        <TouchableOpacity
          style={styles.ctaCard}
          onPress={() => router.push("/(tabs)/route")}
          activeOpacity={0.88}
          accessibilityRole="button"
          accessibilityLabel={"Yeni rota ba\u015Flat"}
        >
          <View style={styles.ctaIconWrap}>
            <Text style={styles.ctaIconText}>{"\u25B2"}</Text>
          </View>
          <Text style={styles.ctaTitle}>{"YEN\u0130 ROTA BA\u015ELAT"}</Text>
          <Text style={styles.ctaSub}>{"Hedefini se\u00E7 ve s\u00FCr\u00FC\u015F tarz\u0131n\u0131 belirle"}</Text>
        </TouchableOpacity>

        <View style={styles.quickRow}>
          <GlassCard onPress={() => router.push("/(tabs)/garage")} style={styles.quickCard}>
            <Text style={styles.quickIcon}>{"\u{1F527}"}</Text>
            <Text style={styles.quickTitle}>Garaj</Text>
            <Text style={styles.quickSub}>{"Motor bilgileri &\nBak\u0131m"}</Text>
          </GlassCard>
          <GlassCard onPress={() => router.push("/saved-routes")} style={styles.quickCard}>
            <Text style={styles.quickIcon}>{"\u{1F4CD}"}</Text>
            <Text style={styles.quickTitle}>{"Kay\u0131tl\u0131 Rotalar"}</Text>
            <Text style={styles.quickSub}>{savedRoutes.length} rota</Text>
          </GlassCard>
        </View>

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Son Rota</Text>
          <TouchableOpacity onPress={() => router.push("/saved-routes")} activeOpacity={0.7}>
            <Text style={styles.sectionLink}>{"T\u00FCm\u00FC"}</Text>
          </TouchableOpacity>
        </View>

        {savedRoutes.length === 0 ? (
          <GlassCard style={styles.emptyCard}>
            <Text style={styles.emptyIcon}>{"\u{1F4CD}"}</Text>
            <View>
              <Text style={styles.emptyTitle}>{"Hen\u00FCz rota yok"}</Text>
              <Text style={styles.emptySub}>
                {"\u0130lk rotan\u0131 olu\u015Fturmak i\u00E7in \"Yeni Rota Ba\u015Flat\"a dokun"}
              </Text>
            </View>
          </GlassCard>
        ) : (
          <GlassCard style={styles.routePreview}>
            <View style={styles.routeDots}>
              <View style={[styles.dot, { backgroundColor: colors.success }]} />
              <View style={styles.routeLine} />
              <View style={[styles.dot, { backgroundColor: colors.warning }]} />
            </View>
            <View style={styles.routeInfo}>
              <Text style={styles.routeLabel}>
                {savedRoutes[0].originLabel} {"\u2192"} {savedRoutes[0].destinationLabel}
              </Text>
              <Text style={styles.routeSub}>{savedRoutes[0].mode}</Text>
            </View>
          </GlassCard>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  scroll: {
    paddingHorizontal: spacing.screenPadding,
    paddingTop: spacing.topSafeArea,
    paddingBottom: 40,
    gap: 16,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
  },
  headerLeft: { flex: 1 },
  greeting: {
    color: colors.textTertiary,
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 1.5,
    marginBottom: 4,
  },
  headerTitle: {
    color: colors.textPrimary,
    fontSize: 28,
    fontWeight: "900",
    letterSpacing: 0.5,
    marginTop: 2,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.accentBlue,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 4,
  },
  avatarText: { color: "#fff", fontSize: 18, fontWeight: "800" },
  ctaCard: {
    backgroundColor: colors.accentBlueDark,
    borderRadius: 22,
    paddingVertical: 32,
    paddingHorizontal: 24,
    alignItems: "center",
    ...glowShadow(colors.accentBlueDark),
  },
  ctaIconWrap: {
    width: 56,
    height: 56,
    borderRadius: 14,
    backgroundColor: "rgba(255,255,255,0.22)",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  ctaIconText: { color: "#fff", fontSize: 24, fontWeight: "900" },
  ctaTitle: {
    color: "#fff",
    fontSize: 22,
    fontWeight: "900",
    letterSpacing: 0.5,
    marginBottom: 8,
    textAlign: "center",
  },
  ctaSub: { color: "rgba(255,255,255,0.75)", fontSize: 14, textAlign: "center" },
  quickRow: { flexDirection: "row", gap: 14 },
  quickCard: { flex: 1, alignItems: "center", gap: 6 },
  quickIcon: { fontSize: 28, marginBottom: 4 },
  quickTitle: {
    color: colors.textPrimary,
    fontSize: 14,
    fontWeight: "800",
    textAlign: "center",
  },
  quickSub: {
    color: colors.textTertiary,
    fontSize: 12,
    textAlign: "center",
    lineHeight: 17,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  sectionTitle: { color: colors.textPrimary, fontSize: 18, fontWeight: "800" },
  sectionLink: { color: colors.accentBlue, fontSize: 14, fontWeight: "700" },
  emptyCard: { flexDirection: "row", alignItems: "center", gap: 12 },
  emptyIcon: { fontSize: 22 },
  emptyTitle: { color: colors.textPrimary, fontSize: 14, fontWeight: "700" },
  emptySub: { color: colors.textTertiary, fontSize: 11, marginTop: 2 },
  routePreview: { flexDirection: "row", alignItems: "center", gap: 14 },
  routeDots: { alignItems: "center", gap: 2 },
  dot: { width: 10, height: 10, borderRadius: 5 },
  routeLine: { width: 2, height: 20, backgroundColor: colors.surfaceBorder },
  routeInfo: { flex: 1 },
  routeLabel: { color: colors.textPrimary, fontSize: 14, fontWeight: "700" },
  routeSub: { color: colors.textTertiary, fontSize: 12, marginTop: 2 },
});