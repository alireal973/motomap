// app/mobile/app/settings/privacy.tsx
import { useState, useEffect } from "react";
import {
  Alert,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import SelectField from "../../components/SelectField";
import { colors, spacing, radius } from "../../theme";
import { useAuth } from "../../context/AuthContext";
import { apiRequest } from "../../utils/api";

type PrivacySettings = {
  profile_visibility: "public" | "friends" | "private";
  show_on_leaderboard: boolean;
  share_ride_history: boolean;
  location_sharing: "always" | "while_riding" | "never";
  analytics_enabled: boolean;
  crash_reports_enabled: boolean;
};

const defaultSettings: PrivacySettings = {
  profile_visibility: "public",
  show_on_leaderboard: true,
  share_ride_history: true,
  location_sharing: "while_riding",
  analytics_enabled: true,
  crash_reports_enabled: true,
};

const VISIBILITY_OPTIONS = [
  { value: "public" as const, label: "Herkese Açık", icon: "globe-outline" as const },
  { value: "friends" as const, label: "Sadece Arkadaşlar", icon: "people-outline" as const },
  { value: "private" as const, label: "Gizli", icon: "lock-closed-outline" as const },
];

const LOCATION_OPTIONS = [
  { value: "always" as const, label: "Her Zaman", icon: "location" as const },
  { value: "while_riding" as const, label: "Sürüş Sırasında", icon: "navigate" as const },
  { value: "never" as const, label: "Asla", icon: "close-circle-outline" as const },
];

export default function PrivacySettingsScreen() {
  const { token } = useAuth();
  const [settings, setSettings] = useState<PrivacySettings>(defaultSettings);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    if (!token) return;
    try {
      const data = await apiRequest("/api/profile/privacy-settings", { token }) as Partial<PrivacySettings>;
      setSettings({ ...defaultSettings, ...data });
    } catch {
      // Use defaults
    } finally {
      setIsLoading(false);
    }
  };

  const updateSetting = async <K extends keyof PrivacySettings>(
    key: K,
    value: PrivacySettings[K]
  ) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);

    if (!token) return;
    try {
      await apiRequest("/api/profile/privacy-settings", {
        method: "PATCH",
        token,
        body: { [key]: value },
      });
    } catch {
      setSettings(settings);
    }
  };

  const handleDownloadData = () => {
    Alert.alert(
      "Verilerimi İndir",
      "Tüm kişisel verilerinizi içeren bir dosya hazırlanacak. Bu işlem birkaç dakika sürebilir.",
      [
        { text: "İptal", style: "cancel" },
        {
          text: "İndir",
          onPress: async () => {
            try {
              await apiRequest("/api/profile/download-data", {
                method: "POST",
                token,
              });
              Alert.alert(
                "İstek Alındı",
                "Verileriniz hazırlandığında e-posta ile bilgilendirileceksiniz."
              );
            } catch (error: any) {
              Alert.alert("Hata", error.message || "İstek gönderilemedi.");
            }
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <ScreenHeader title="Gizlilik Ayarları" onBack={() => router.back()} />
      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Profile Visibility */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Profil Görünürlüğü</Text>
          <SelectField
            label="Kim profilimi görebilir?"
            options={VISIBILITY_OPTIONS}
            value={settings.profile_visibility}
            onSelect={(v) => updateSetting("profile_visibility", v)}
          />

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Liderlik Tablosunda Göster</Text>
              <Text style={styles.settingDescription}>
                Adınız ve puanınız herkese görünür olur
              </Text>
            </View>
            <Switch
              value={settings.show_on_leaderboard}
              onValueChange={(v) => updateSetting("show_on_leaderboard", v)}
              trackColor={{ false: colors.surfaceGlass, true: colors.accentBlue }}
              thumbColor={colors.textPrimary}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Sürüş Geçmişini Paylaş</Text>
              <Text style={styles.settingDescription}>
                Arkadaşlarınız rotalarınızı görebilir
              </Text>
            </View>
            <Switch
              value={settings.share_ride_history}
              onValueChange={(v) => updateSetting("share_ride_history", v)}
              trackColor={{ false: colors.surfaceGlass, true: colors.accentBlue }}
              thumbColor={colors.textPrimary}
            />
          </View>
        </GlassCard>

        {/* Location Settings */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Konum Ayarları</Text>
          <SelectField
            label="Konum Paylaşımı"
            options={LOCATION_OPTIONS}
            value={settings.location_sharing}
            onSelect={(v) => updateSetting("location_sharing", v)}
          />
          <Text style={styles.locationHint}>
            <Ionicons name="information-circle-outline" size={14} color={colors.textTertiary} />
            {" "}Konum bilginiz güvenli rotalar ve hava durumu için kullanılır.
          </Text>
        </GlassCard>

        {/* Data & Analytics */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Veri ve Analitik</Text>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Kullanım Analitiği</Text>
              <Text style={styles.settingDescription}>
                Uygulamayı geliştirmemize yardımcı olun
              </Text>
            </View>
            <Switch
              value={settings.analytics_enabled}
              onValueChange={(v) => updateSetting("analytics_enabled", v)}
              trackColor={{ false: colors.surfaceGlass, true: colors.accentBlue }}
              thumbColor={colors.textPrimary}
            />
          </View>

          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Hata Raporları</Text>
              <Text style={styles.settingDescription}>
                Otomatik hata raporları gönder
              </Text>
            </View>
            <Switch
              value={settings.crash_reports_enabled}
              onValueChange={(v) => updateSetting("crash_reports_enabled", v)}
              trackColor={{ false: colors.surfaceGlass, true: colors.accentBlue }}
              thumbColor={colors.textPrimary}
            />
          </View>
        </GlassCard>

        {/* Data Export */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Verilerim</Text>
          <Text style={styles.dataDescription}>
            KVKK kapsamında tüm kişisel verilerinizi indirebilirsiniz.
          </Text>
          <TouchableOpacity style={styles.downloadButton} onPress={handleDownloadData}>
            <Ionicons name="download-outline" size={20} color={colors.accentBlue} />
            <Text style={styles.downloadButtonText}>Verilerimi İndir</Text>
          </TouchableOpacity>
        </GlassCard>

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
  settingRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.surfaceBorder,
  },
  settingInfo: {
    flex: 1,
    marginRight: spacing.md,
  },
  settingLabel: {
    fontSize: 15,
    fontWeight: "600",
    color: colors.textPrimary,
  },
  settingDescription: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 2,
  },
  locationHint: {
    fontSize: 12,
    color: colors.textTertiary,
    marginTop: spacing.md,
    lineHeight: 18,
  },
  dataDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.lg,
  },
  downloadButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.accentBlue,
    gap: spacing.sm,
  },
  downloadButtonText: {
    fontSize: 15,
    fontWeight: "600",
    color: colors.accentBlue,
  },
});
