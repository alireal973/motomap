// app/mobile/app/onboarding.tsx
import { useRouter } from "expo-router";
import {
  Dimensions,
  ImageBackground,
  StyleSheet,
  Text,
  View,
} from "react-native";
import AppButton from "../components/AppButton";
import GlassCard from "../components/GlassCard";
import { useApp } from "../context/AppContext";
import { colors, spacing } from "../theme";

const { width, height } = Dimensions.get("window");

export default function OnboardingScreen() {
  const router = useRouter();
  const { setUserMode } = useApp();

  const handleSelect = (mode: "work" | "hobby") => {
    setUserMode(mode);
    router.replace("/(tabs)");
  };

  return (
    <ImageBackground
      source={require("../assets/moto_bg.png")}
      style={styles.bg}
      resizeMode="cover"
    >
      <View style={styles.overlay}>
        <View style={styles.inner}>
          <View style={styles.topBar}>
            <View style={styles.globeCircle}>
              <Text style={styles.globeIcon}>{"\u{1F310}"}</Text>
            </View>
            <Text style={styles.brandText}>MOTOMAP</Text>
          </View>

          <View style={styles.heroBlock}>
            <Text style={styles.heroWhite}>{"Seni Daha \u0130yi"}</Text>
            <Text style={styles.heroBlue}>{"Tan\u0131yal\u0131m."}</Text>
            <Text style={styles.subtitle}>
              {"Uygulamay\u0131 genellikle hangi ama\u00E7la\nkullanacaks\u0131n?"}
            </Text>
          </View>

          <View style={styles.spacer} />

          <View style={styles.cardsBlock}>
            <GlassCard
              onPress={() => handleSelect("work")}
              style={styles.selectionCard}
              accessibilityLabel={"\u0130\u015F ve Kurye modu"}
            >
              <View style={styles.cardIconWrap}>
                <Text style={styles.cardIcon}>{"\u{1F4BC}"}</Text>
              </View>
              <View style={styles.cardTextBlock}>
                <Text style={styles.cardTitle}>{"\u0130\u015F / Kurye"}</Text>
                <Text style={styles.cardSub}>
                  {"H\u0131zl\u0131 teslimat ve\nverimli rotalar."}
                </Text>
              </View>
              <Text style={styles.cardArrow}>{"\u203A"}</Text>
            </GlassCard>

            <GlassCard
              onPress={() => handleSelect("hobby")}
              style={styles.selectionCard}
              accessibilityLabel={"Gezi ve Hobi modu"}
            >
              <View style={styles.cardIconWrap}>
                <Text style={styles.cardIcon}>{"\u{1F90D}"}</Text>
              </View>
              <View style={styles.cardTextBlock}>
                <Text style={styles.cardTitle}>Gezi / Hobi</Text>
                <Text style={styles.cardSub}>
                  {"Keyifli turlar ve\nvirajl\u0131 yollar."}
                </Text>
              </View>
              <Text style={styles.cardArrow}>{"\u203A"}</Text>
            </GlassCard>
          </View>

          <AppButton
            title={"GER\u0130 D\u00D6N"}
            onPress={() => router.back()}
            variant="ghost"
          />
        </View>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  bg: { flex: 1, width, height },
  overlay: { flex: 1, backgroundColor: "rgba(8, 28, 80, 0.68)" },
  inner: {
    flex: 1,
    paddingHorizontal: spacing.screenPadding,
    paddingTop: spacing.topSafeArea,
    paddingBottom: spacing.xxl,
  },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginBottom: spacing.xxl,
  },
  globeCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.accentBlue,
    alignItems: "center",
    justifyContent: "center",
  },
  globeIcon: { fontSize: 18 },
  brandText: {
    color: colors.textPrimary,
    fontSize: 17,
    fontWeight: "800",
    letterSpacing: 1,
  },
  heroBlock: { marginBottom: spacing.sm },
  heroWhite: {
    color: colors.textPrimary,
    fontSize: 46,
    fontWeight: "900",
    letterSpacing: -0.5,
    lineHeight: 52,
  },
  heroBlue: {
    color: colors.accentBlue,
    fontSize: 46,
    fontWeight: "900",
    letterSpacing: -0.5,
    lineHeight: 52,
  },
  subtitle: {
    color: colors.textSecondary,
    fontSize: 16,
    lineHeight: 24,
    marginTop: 16,
  },
  spacer: { flex: 1 },
  cardsBlock: { gap: 14, marginBottom: spacing.xl },
  selectionCard: {
    flexDirection: "row",
    alignItems: "center",
    gap: 16,
  },
  cardIconWrap: {
    width: 52,
    height: 52,
    borderRadius: 14,
    backgroundColor: "rgba(255,255,255,0.15)",
    alignItems: "center",
    justifyContent: "center",
  },
  cardIcon: { fontSize: 24 },
  cardTextBlock: { flex: 1 },
  cardTitle: {
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: "800",
    marginBottom: 4,
  },
  cardSub: { color: colors.textSecondary, fontSize: 13, lineHeight: 19 },
  cardArrow: { color: colors.textSecondary, fontSize: 24, fontWeight: "300" },
});