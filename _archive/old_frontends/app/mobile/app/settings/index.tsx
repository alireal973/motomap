import { useState } from "react";
import {
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import { colors, spacing, radius } from "../../theme";
import { useAuth } from "../../context/AuthContext";
import { apiRequest } from "../../utils/api";

export default function SettingsScreen() {
  const { user, token, isAuthenticated, logout } = useAuth();
  const [notifications, setNotifications] = useState(true);
  const [darkTheme, setDarkTheme] = useState(true);
  const [distanceKm, setDistanceKm] = useState(true);

  const updateSetting = async (key: string, value: unknown) => {
    if (!token) return;
    try {
      await apiRequest("/api/profile/settings", {
        method: "PATCH",
        token,
        body: { [key]: value },
      });
    } catch {}
  };

  return (
    <View style={styles.container}>
      <ScreenHeader title="Ayarlar" />
      <ScrollView contentContainerStyle={styles.scroll}>
        {isAuthenticated && (
          <GlassCard style={styles.section}>
            <Text style={styles.sectionTitle}>Hesap</Text>
            <InfoRow label="E-posta" value={user?.email || "-"} />
            <InfoRow label="Kullanici Adi" value={user?.username ? `@${user.username}` : "Ayarlanmamis"} />
            <TouchableOpacity
              style={styles.actionRow}
              onPress={() => router.push("/auth/login" as never)}
            >
              <Text style={styles.actionText}>Sifre Degistir</Text>
              <Text style={styles.arrow}>{"\u203A"}</Text>
            </TouchableOpacity>
          </GlassCard>
        )}

        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Tercihler</Text>
          <ToggleRow
            label="Bildirimler"
            value={notifications}
            onToggle={(v) => {
              setNotifications(v);
              updateSetting("notifications_enabled", v);
            }}
          />
          <ToggleRow
            label="Karanlik Tema"
            value={darkTheme}
            onToggle={(v) => {
              setDarkTheme(v);
              updateSetting("theme", v ? "dark" : "light");
            }}
          />
          <ToggleRow
            label="Kilometre (km)"
            value={distanceKm}
            onToggle={(v) => {
              setDistanceKm(v);
              updateSetting("distance_unit", v ? "km" : "mi");
            }}
          />
        </GlassCard>

        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Hakkinda</Text>
          <InfoRow label="Versiyon" value="1.0.0" />
          <InfoRow label="Gelistirici" value="MotoMap Team" />
        </GlassCard>

        {isAuthenticated && (
          <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
            <Text style={styles.logoutText}>Cikis Yap</Text>
          </TouchableOpacity>
        )}

        {!isAuthenticated && (
          <TouchableOpacity
            style={styles.loginBtn}
            onPress={() => router.push("/auth/login" as never)}
          >
            <Text style={styles.loginText}>Giris Yap</Text>
          </TouchableOpacity>
        )}

        <View style={{ height: 100 }} />
      </ScrollView>
    </View>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

function ToggleRow({
  label,
  value,
  onToggle,
}: {
  label: string;
  value: boolean;
  onToggle: (v: boolean) => void;
}) {
  return (
    <View style={styles.toggleRow}>
      <Text style={styles.toggleLabel}>{label}</Text>
      <Switch
        value={value}
        onValueChange={onToggle}
        trackColor={{ false: colors.surfaceGlass, true: colors.accentBlue }}
        thumbColor={colors.textPrimary}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  scroll: { padding: spacing.md },
  section: { marginBottom: spacing.md, padding: spacing.md },
  sectionTitle: { fontSize: 14, fontWeight: "700", color: colors.textTertiary, marginBottom: spacing.md, textTransform: "uppercase", letterSpacing: 1 },
  infoRow: { flexDirection: "row", justifyContent: "space-between", paddingVertical: spacing.sm, borderBottomWidth: 1, borderBottomColor: colors.surfaceBorder },
  infoLabel: { fontSize: 14, color: colors.textSecondary },
  infoValue: { fontSize: 14, color: colors.textPrimary, fontWeight: "500" },
  actionRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: spacing.sm },
  actionText: { fontSize: 14, color: colors.accentBlue },
  arrow: { fontSize: 20, color: colors.textTertiary },
  toggleRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: spacing.sm, borderBottomWidth: 1, borderBottomColor: colors.surfaceBorder },
  toggleLabel: { fontSize: 14, color: colors.textPrimary },
  logoutBtn: { marginTop: spacing.md, padding: spacing.md, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.danger, alignItems: "center" },
  logoutText: { fontSize: 15, fontWeight: "600", color: colors.danger },
  loginBtn: { marginTop: spacing.md, padding: spacing.md, borderRadius: radius.lg, backgroundColor: colors.accentBlue, alignItems: "center" },
  loginText: { fontSize: 15, fontWeight: "600", color: colors.textPrimary },
});
