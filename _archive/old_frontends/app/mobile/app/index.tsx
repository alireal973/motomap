// app/mobile/app/index.tsx
import { useRouter } from "expo-router";
import {
  Dimensions,
  Image,
  ImageBackground,
  StyleSheet,
  Text,
  View,
} from "react-native";
import AppButton from "../components/AppButton";
import GlassCard from "../components/GlassCard";
import { colors, spacing } from "../theme";

const { width, height } = Dimensions.get("window");

export default function WelcomeScreen() {
  const router = useRouter();

  return (
    <ImageBackground
      source={require("../assets/moto_bg.png")}
      style={styles.bg}
      resizeMode="cover"
    >
      <View style={styles.overlay}>
        <View style={styles.inner}>
          <View style={styles.topBar}>
            <Image
              source={require("../assets/motomap_logo_white.png")}
              style={styles.logoImg}
              resizeMode="contain"
            />
          </View>

          <View style={styles.heroBlock}>
            <Text style={styles.heroWhite}>YOLUN</Text>
            <Text style={styles.heroBlue}>RUHUNU</Text>
            <Text style={styles.heroWhite}>KE\u015EFET.</Text>
            <Text style={styles.subtitle}>
              {"Sadece en h\u0131zl\u0131 de\u011Fil, en keyifli\nrotalar i\u00E7in tasarland\u0131."}
            </Text>
          </View>

          <View style={styles.spacer} />

          <GlassCard style={styles.featureCard}>
            <View style={styles.featureIconWrap}>
              <Text style={styles.featureIconText}>{"\u26A1"}</Text>
            </View>
            <View style={styles.featureCardText}>
              <Text style={styles.featureCardTitle}>{"Ak\u0131ll\u0131 Rotalar"}</Text>
              <Text style={styles.featureCardSub}>
                {"Virajl\u0131 ve manzaral\u0131 se\u00E7enekler."}
              </Text>
            </View>
          </GlassCard>

          <AppButton
            title={"BA\u015ELAYALIM  \u203A"}
            onPress={() => router.push("/onboarding")}
            variant="primary"
            style={styles.ctaButton}
            accessibilityLabel={"Ba\u015Flayalim"}
          />
        </View>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  bg: { flex: 1, width, height },
  overlay: { flex: 1, backgroundColor: "rgba(8, 28, 80, 0.72)" },
  inner: {
    flex: 1,
    paddingHorizontal: spacing.screenPadding,
    paddingTop: spacing.topSafeArea,
    paddingBottom: spacing.xxl,
  },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.xxl,
    marginLeft: -24,
  },
  logoImg: { width: 280, height: 96 },
  heroBlock: { marginBottom: spacing.sm },
  heroWhite: {
    color: colors.textPrimary,
    fontSize: 58,
    fontWeight: "900",
    letterSpacing: -1,
    lineHeight: 62,
  },
  heroBlue: {
    color: colors.accentBlue,
    fontSize: 58,
    fontWeight: "900",
    letterSpacing: -1,
    lineHeight: 62,
  },
  subtitle: {
    color: colors.textSecondary,
    fontSize: 16,
    lineHeight: 24,
    marginTop: 18,
  },
  spacer: { flex: 1 },
  featureCard: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    marginBottom: spacing.lg,
  },
  featureIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: "rgba(61,139,255,0.35)",
    alignItems: "center",
    justifyContent: "center",
  },
  featureIconText: { fontSize: 22 },
  featureCardText: { flex: 1 },
  featureCardTitle: {
    color: colors.textPrimary,
    fontSize: 15,
    fontWeight: "700",
    marginBottom: 3,
  },
  featureCardSub: { color: colors.textSecondary, fontSize: 13 },
  ctaButton: {
    backgroundColor: "#ffffff",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 12,
    elevation: 8,
  },
});