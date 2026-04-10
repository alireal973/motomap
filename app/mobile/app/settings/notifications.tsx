// app/mobile/app/settings/notifications.tsx
import { useState, useEffect } from "react";
import {
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  View,
} from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import { colors, spacing } from "../../theme";
import { useAuth } from "../../context/AuthContext";
import { apiRequest } from "../../utils/api";

type NotificationSettings = {
  push_enabled: boolean;
  route_alerts: boolean;
  weather_alerts: boolean;
  community_updates: boolean;
  achievement_alerts: boolean;
  challenge_reminders: boolean;
  report_updates: boolean;
  email_digest: boolean;
  marketing_emails: boolean;
};

const defaultSettings: NotificationSettings = {
  push_enabled: true,
  route_alerts: true,
  weather_alerts: true,
  community_updates: true,
  achievement_alerts: true,
  challenge_reminders: true,
  report_updates: true,
  email_digest: false,
  marketing_emails: false,
};

type SettingConfig = {
  key: keyof NotificationSettings;
  label: string;
  description: string;
  icon: keyof typeof Ionicons.glyphMap;
};

const PUSH_SETTINGS: SettingConfig[] = [
  {
    key: "route_alerts",
    label: "Rota Uyarıları",
    description: "Rota üzerindeki tehlikeler ve değişiklikler",
    icon: "navigate-outline",
  },
  {
    key: "weather_alerts",
    label: "Hava Durumu Uyarıları",
    description: "Kötü hava koşulları bildirimleri",
    icon: "cloudy-outline",
  },
  {
    key: "community_updates",
    label: "Topluluk Güncellemeleri",
    description: "Yeni gönderiler ve yorumlar",
    icon: "people-outline",
  },
  {
    key: "achievement_alerts",
    label: "Başarı Bildirimleri",
    description: "Yeni rozetler ve seviye atlamaları",
    icon: "trophy-outline",
  },
  {
    key: "challenge_reminders",
    label: "Görev Hatırlatıcıları",
    description: "Aktif görevler ve son tarihler",
    icon: "flag-outline",
  },
  {
    key: "report_updates",
    label: "Rapor Güncellemeleri",
    description: "Raporlarınızdaki değişiklikler",
    icon: "document-text-outline",
  },
];

const EMAIL_SETTINGS: SettingConfig[] = [
  {
    key: "email_digest",
    label: "Haftalık Özet",
    description: "Haftalık aktivite özeti e-postası",
    icon: "mail-outline",
  },
  {
    key: "marketing_emails",
    label: "Pazarlama E-postaları",
    description: "Yenilikler ve kampanyalar",
    icon: "megaphone-outline",
  },
];

export default function NotificationSettingsScreen() {
  const { token } = useAuth();
  const [settings, setSettings] = useState<NotificationSettings>(defaultSettings);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    if (!token) return;
    try {
      const data = await apiRequest("/api/profile/notification-settings", { token }) as Partial<NotificationSettings>;
      setSettings({ ...defaultSettings, ...data });
    } catch {
      // Use defaults on error
    } finally {
      setIsLoading(false);
    }
  };

  const updateSetting = async (key: keyof NotificationSettings, value: boolean) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);

    if (!token) return;
    try {
      await apiRequest("/api/profile/notification-settings", {
        method: "PATCH",
        token,
        body: { [key]: value },
      });
    } catch {
      // Revert on error
      setSettings(settings);
    }
  };

  const renderSettingRow = (config: SettingConfig, disabled = false) => (
    <View
      key={config.key}
      style={[styles.settingRow, disabled && styles.settingRowDisabled]}
    >
      <View style={styles.settingIcon}>
        <Ionicons
          name={config.icon}
          size={22}
          color={disabled ? colors.textTertiary : colors.accentBlue}
        />
      </View>
      <View style={styles.settingInfo}>
        <Text style={[styles.settingLabel, disabled && styles.textDisabled]}>
          {config.label}
        </Text>
        <Text style={[styles.settingDescription, disabled && styles.textDisabled]}>
          {config.description}
        </Text>
      </View>
      <Switch
        value={settings[config.key]}
        onValueChange={(v) => updateSetting(config.key, v)}
        trackColor={{ false: colors.surfaceGlass, true: colors.accentBlue }}
        thumbColor={colors.textPrimary}
        disabled={disabled}
      />
    </View>
  );

  const pushDisabled = !settings.push_enabled;

  return (
    <View style={styles.container}>
      <ScreenHeader title="Bildirim Ayarları" onBack={() => router.back()} />
      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Master Switch */}
        <GlassCard style={styles.section}>
          <View style={styles.masterRow}>
            <View style={styles.masterInfo}>
              <Ionicons name="notifications" size={28} color={colors.accentBlue} />
              <View style={styles.masterText}>
                <Text style={styles.masterLabel}>Push Bildirimleri</Text>
                <Text style={styles.masterDescription}>
                  Tüm bildirimleri aç/kapat
                </Text>
              </View>
            </View>
            <Switch
              value={settings.push_enabled}
              onValueChange={(v) => updateSetting("push_enabled", v)}
              trackColor={{ false: colors.surfaceGlass, true: colors.accentBlue }}
              thumbColor={colors.textPrimary}
            />
          </View>
        </GlassCard>

        {/* Push Notification Types */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Bildirim Türleri</Text>
          {PUSH_SETTINGS.map((config) => renderSettingRow(config, pushDisabled))}
        </GlassCard>

        {/* Email Settings */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>E-posta Bildirimleri</Text>
          {EMAIL_SETTINGS.map((config) => renderSettingRow(config))}
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
  masterRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  masterInfo: {
    flexDirection: "row",
    alignItems: "center",
    flex: 1,
  },
  masterText: {
    marginLeft: spacing.md,
  },
  masterLabel: {
    fontSize: 17,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  masterDescription: {
    fontSize: 13,
    color: colors.textSecondary,
    marginTop: 2,
  },
  settingRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.surfaceBorder,
  },
  settingRowDisabled: {
    opacity: 0.5,
  },
  settingIcon: {
    width: 40,
    alignItems: "center",
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
  textDisabled: {
    color: colors.textTertiary,
  },
});
