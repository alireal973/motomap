import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import { useAuth } from "../../context/AuthContext";
import GlassCard from "../../components/GlassCard";
import AppButton from "../../components/AppButton";
import { colors, spacing, radius } from "../../theme";
import { apiRequest, API_URL } from "../../utils/api";

type Stats = {
  total_motorcycles: number;
  total_km: number;
  total_routes: number;
  member_since: string | null;
  is_premium: boolean;
};

export default function ProfileScreen() {
  const { user, token, isLoading, isAuthenticated, logout } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);

  const fetchStats = useCallback(async () => {
    if (!token) return;
    try {
      const data = await apiRequest<{ statistics: Stats }>("/api/profile", { token });
      setStats(data.statistics);
    } catch {}
  }, [token]);

  useEffect(() => {
    if (isAuthenticated) fetchStats();
  }, [isAuthenticated, fetchStats]);

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.accentBlue} />
      </View>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <View style={styles.container}>
        <View style={styles.center}>
          <Text style={styles.guestIcon}>{"\uD83D\uDC64"}</Text>
          <Text style={styles.guestTitle}>Hesabiniza Giris Yapin</Text>
          <Text style={styles.guestSub}>
            Profilinizi goruntulemek ve motosikletlerinizi yonetmek icin giris yapin
          </Text>
          <AppButton
            title="Giris Yap"
            onPress={() => router.push("/auth/login" as never)}
            style={styles.authBtn}
          />
          <TouchableOpacity onPress={() => router.push("/auth/register" as never)}>
            <Text style={styles.registerLink}>Kayit Ol</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  const initial = (user.display_name?.[0] || user.email[0]).toUpperCase();

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <LinearGradient
        colors={[colors.bgSecondary, colors.bgPrimary]}
        style={styles.header}
      >
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{initial}</Text>
        </View>
        <Text style={styles.name}>{user.display_name || "Motosikletci"}</Text>
        {user.username && <Text style={styles.username}>@{user.username}</Text>}
        {user.city && (
          <Text style={styles.location}>{user.city}{user.country ? `, ${user.country}` : ""}</Text>
        )}
      </LinearGradient>

      {stats && (
        <View style={styles.statsRow}>
          <StatBox value={stats.total_motorcycles} label="Motor" />
          <StatBox value={stats.total_km} label="km" />
          <StatBox value={stats.total_routes} label="Rota" />
        </View>
      )}

      <View style={styles.menu}>
        <MenuItem icon={"\uD83D\uDEB2"} title="Garajim" sub="Motosikletlerini yonet" onPress={() => router.push("/(tabs)/garage")} />
        <MenuItem icon={"\uD83D\uDDD3"} title="Kayitli Rotalar" sub="Favorilerine goz at" onPress={() => router.push("/saved-routes")} />
        <MenuItem icon={"\u2699\uFE0F"} title="Ayarlar" sub="Hesap ve uygulama ayarlari" onPress={() => {}} />
      </View>

      <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
        <Text style={styles.logoutText}>Cikis Yap</Text>
      </TouchableOpacity>

      <View style={{ height: 100 }} />
    </ScrollView>
  );
}

function StatBox({ value, label }: { value: number; label: string }) {
  return (
    <GlassCard style={styles.statBox}>
      <Text style={styles.statVal}>{value.toLocaleString()}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </GlassCard>
  );
}

function MenuItem({ icon, title, sub, onPress }: {
  icon: string; title: string; sub: string; onPress: () => void;
}) {
  return (
    <TouchableOpacity style={styles.menuItem} onPress={onPress} activeOpacity={0.7}>
      <Text style={styles.menuIcon}>{icon}</Text>
      <View style={styles.menuContent}>
        <Text style={styles.menuTitle}>{title}</Text>
        <Text style={styles.menuSub}>{sub}</Text>
      </View>
      <Text style={styles.menuArrow}>{"\u203A"}</Text>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  center: { flex: 1, justifyContent: "center", alignItems: "center", padding: spacing.xl },
  guestIcon: { fontSize: 64, marginBottom: spacing.md },
  guestTitle: { fontSize: 22, fontWeight: "700", color: colors.textPrimary, textAlign: "center", marginBottom: spacing.sm },
  guestSub: { fontSize: 14, color: colors.textSecondary, textAlign: "center", marginBottom: spacing.lg, paddingHorizontal: spacing.lg },
  authBtn: { width: "100%", marginBottom: spacing.md },
  registerLink: { fontSize: 14, color: colors.accentBlue, fontWeight: "600" },
  header: { alignItems: "center", paddingTop: 60, paddingBottom: spacing.xl, borderBottomLeftRadius: radius.xl, borderBottomRightRadius: radius.xl },
  avatar: { width: 88, height: 88, borderRadius: 44, backgroundColor: colors.surfaceGlass, borderWidth: 3, borderColor: colors.accentBlue, justifyContent: "center", alignItems: "center", marginBottom: spacing.md },
  avatarText: { fontSize: 36, fontWeight: "700", color: colors.textPrimary },
  name: { fontSize: 24, fontWeight: "700", color: colors.textPrimary },
  username: { fontSize: 14, color: colors.textSecondary, marginTop: 2 },
  location: { fontSize: 13, color: colors.textTertiary, marginTop: 4 },
  statsRow: { flexDirection: "row", justifyContent: "space-around", marginTop: -spacing.md, paddingHorizontal: spacing.md, marginBottom: spacing.lg },
  statBox: { alignItems: "center", padding: spacing.md, minWidth: 90 },
  statVal: { fontSize: 22, fontWeight: "700", color: colors.textPrimary },
  statLabel: { fontSize: 11, color: colors.textSecondary, marginTop: 2 },
  menu: { paddingHorizontal: spacing.md },
  menuItem: { flexDirection: "row", alignItems: "center", backgroundColor: colors.surfaceGlass, borderRadius: radius.lg, padding: spacing.md, marginBottom: spacing.sm },
  menuIcon: { fontSize: 24, marginRight: spacing.md },
  menuContent: { flex: 1 },
  menuTitle: { fontSize: 15, fontWeight: "600", color: colors.textPrimary },
  menuSub: { fontSize: 12, color: colors.textSecondary, marginTop: 2 },
  menuArrow: { fontSize: 22, color: colors.textTertiary },
  logoutBtn: { marginTop: spacing.xl, marginHorizontal: spacing.md, padding: spacing.md, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.danger, alignItems: "center" },
  logoutText: { fontSize: 15, fontWeight: "600", color: colors.danger },
});
