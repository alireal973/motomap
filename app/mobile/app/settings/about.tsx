// app/mobile/app/settings/about.tsx
import {
  Linking,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Image,
} from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import Constants from "expo-constants";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import { colors, spacing, radius } from "../../theme";

type LinkItem = {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  url: string;
};

const LINKS: LinkItem[] = [
  {
    icon: "globe-outline",
    label: "Web Sitesi",
    url: "https://motomap.app",
  },
  {
    icon: "logo-github",
    label: "GitHub",
    url: "https://github.com/motomap",
  },
  {
    icon: "logo-twitter",
    label: "Twitter",
    url: "https://twitter.com/motomapapp",
  },
  {
    icon: "logo-instagram",
    label: "Instagram",
    url: "https://instagram.com/motomapapp",
  },
];

const LEGAL_LINKS: LinkItem[] = [
  {
    icon: "document-text-outline",
    label: "Kullanım Koşulları",
    url: "https://motomap.app/terms",
  },
  {
    icon: "shield-checkmark-outline",
    label: "Gizlilik Politikası",
    url: "https://motomap.app/privacy",
  },
  {
    icon: "code-outline",
    label: "Açık Kaynak Lisansları",
    url: "https://motomap.app/licenses",
  },
];

const CREDITS = [
  { name: "OpenStreetMap", role: "Harita verileri" },
  { name: "OpenWeatherMap", role: "Hava durumu servisi" },
  { name: "OSRM", role: "Rota hesaplama" },
  { name: "Expo", role: "React Native framework" },
];

export default function AboutScreen() {
  const appVersion = Constants.expoConfig?.version || "1.0.0";
  const buildNumber = Constants.expoConfig?.ios?.buildNumber || Constants.expoConfig?.android?.versionCode || "1";

  const handleLink = (url: string) => {
    Linking.openURL(url);
  };

  const handleEmail = () => {
    Linking.openURL("mailto:destek@motomap.app?subject=MotoMap%20Destek");
  };

  return (
    <View style={styles.container}>
      <ScreenHeader title="Hakkında" onBack={() => router.back()} />
      <ScrollView contentContainerStyle={styles.scroll}>
        {/* App Info */}
        <GlassCard style={styles.appInfo}>
          <View style={styles.logoContainer}>
            <View style={styles.logoPlaceholder}>
              <Ionicons name="bicycle" size={48} color={colors.accentBlue} />
            </View>
          </View>
          <Text style={styles.appName}>MotoMap</Text>
          <Text style={styles.appTagline}>Güvenli yolculuklar için</Text>
          <View style={styles.versionContainer}>
            <Text style={styles.versionText}>
              Versiyon {appVersion} ({buildNumber})
            </Text>
          </View>
        </GlassCard>

        {/* Description */}
        <GlassCard style={styles.section}>
          <Text style={styles.description}>
            MotoMap, motosiklet sürücüleri için özel olarak tasarlanmış bir
            navigasyon ve topluluk uygulamasıdır. Hava durumuna göre güvenlik
            değerlendirmesi, gerçek zamanlı raporlar ve sürücü topluluğu ile
            daha güvenli yolculuklar yapın.
          </Text>
        </GlassCard>

        {/* Social Links */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Bizi Takip Edin</Text>
          <View style={styles.linksGrid}>
            {LINKS.map((link) => (
              <TouchableOpacity
                key={link.label}
                style={styles.linkButton}
                onPress={() => handleLink(link.url)}
                activeOpacity={0.7}
              >
                <Ionicons name={link.icon} size={24} color={colors.accentBlue} />
                <Text style={styles.linkLabel}>{link.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </GlassCard>

        {/* Legal */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Yasal</Text>
          {LEGAL_LINKS.map((link) => (
            <TouchableOpacity
              key={link.label}
              style={styles.legalRow}
              onPress={() => handleLink(link.url)}
              activeOpacity={0.7}
            >
              <Ionicons name={link.icon} size={20} color={colors.textSecondary} />
              <Text style={styles.legalText}>{link.label}</Text>
              <Ionicons name="chevron-forward" size={18} color={colors.textTertiary} />
            </TouchableOpacity>
          ))}
        </GlassCard>

        {/* Credits */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Teşekkürler</Text>
          {CREDITS.map((credit, index) => (
            <View key={index} style={styles.creditRow}>
              <Text style={styles.creditName}>{credit.name}</Text>
              <Text style={styles.creditRole}>{credit.role}</Text>
            </View>
          ))}
        </GlassCard>

        {/* Support */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Destek</Text>
          <Text style={styles.supportText}>
            Sorularınız veya önerileriniz için bize ulaşın.
          </Text>
          <TouchableOpacity style={styles.emailButton} onPress={handleEmail}>
            <Ionicons name="mail-outline" size={20} color={colors.accentBlue} />
            <Text style={styles.emailButtonText}>destek@motomap.app</Text>
          </TouchableOpacity>
        </GlassCard>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            © 2024 MotoMap. Tüm hakları saklıdır.
          </Text>
          <Text style={styles.footerText}>
            Made with ❤️ in Türkiye
          </Text>
        </View>

        <View style={{ height: 100 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  scroll: {
    padding: spacing.md,
  },
  appInfo: {
    alignItems: "center",
    padding: spacing.xl,
    marginBottom: spacing.md,
  },
  logoContainer: {
    marginBottom: spacing.md,
  },
  logoPlaceholder: {
    width: 80,
    height: 80,
    borderRadius: 20,
    backgroundColor: colors.surfaceGlass,
    alignItems: "center",
    justifyContent: "center",
  },
  appName: {
    fontSize: 28,
    fontWeight: "800",
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  appTagline: {
    fontSize: 16,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  versionContainer: {
    backgroundColor: colors.surfaceGlass,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
  },
  versionText: {
    fontSize: 13,
    color: colors.textTertiary,
    fontWeight: "500",
  },
  section: {
    marginBottom: spacing.md,
    padding: spacing.lg,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.textTertiary,
    marginBottom: spacing.lg,
    textTransform: "uppercase",
    letterSpacing: 1,
  },
  description: {
    fontSize: 15,
    color: colors.textSecondary,
    lineHeight: 24,
  },
  linksGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.md,
  },
  linkButton: {
    alignItems: "center",
    width: "22%",
  },
  linkLabel: {
    fontSize: 11,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  legalRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.surfaceBorder,
    gap: spacing.md,
  },
  legalText: {
    flex: 1,
    fontSize: 15,
    color: colors.textPrimary,
  },
  creditRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.surfaceBorder,
  },
  creditName: {
    fontSize: 14,
    color: colors.textPrimary,
    fontWeight: "500",
  },
  creditRole: {
    fontSize: 13,
    color: colors.textTertiary,
  },
  supportText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  emailButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.accentBlue,
    gap: spacing.sm,
  },
  emailButtonText: {
    fontSize: 15,
    fontWeight: "600",
    color: colors.accentBlue,
  },
  footer: {
    alignItems: "center",
    marginTop: spacing.lg,
    gap: spacing.xs,
  },
  footerText: {
    fontSize: 12,
    color: colors.textTertiary,
  },
});
