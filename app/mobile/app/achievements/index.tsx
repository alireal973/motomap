import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import { colors, spacing, radius } from "../../theme";
import { apiRequest } from "../../utils/api";
import { useAuth } from "../../context/AuthContext";

type Points = {
  total_points: number;
  level: number;
  current_streak_days: number;
  longest_streak_days: number;
  points_routes: number;
  points_reports: number;
  points_community: number;
  points_helping: number;
};

type Badge = {
  id: string;
  name_tr: string;
  icon: string;
  category: string;
  description_tr: string;
  requirement_type: string;
  requirement_value: number;
  points_reward: number;
};

type EarnedBadge = {
  badge_id: string;
  earned_at: string;
  name_tr: string;
  icon: string;
  category: string;
  description_tr: string;
};

const LEVEL_NAMES = ["", "Caylak", "Amatr", "Deneyimli", "Uzman", "Usta", "Efsane"];
const LEVEL_THRESHOLDS = [0, 100, 500, 1500, 5000, 15000];

export default function AchievementsScreen() {
  const { token, isAuthenticated } = useAuth();
  const [points, setPoints] = useState<Points | null>(null);
  const [allBadges, setAllBadges] = useState<Badge[]>([]);
  const [earned, setEarned] = useState<EarnedBadge[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [badgeData, ..._rest] = await Promise.all([
        apiRequest<Badge[]>("/api/gamification/badges"),
        ...(isAuthenticated && token
          ? [
              apiRequest<Points>("/api/gamification/points", { token }).then(setPoints),
              apiRequest<EarnedBadge[]>("/api/gamification/badges/my", { token }).then(setEarned),
            ]
          : []),
      ]);
      setAllBadges(badgeData);
    } catch {}
    setLoading(false);
  }, [token, isAuthenticated]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <View style={styles.container}>
        <ScreenHeader title="Basarilar" />
        <ActivityIndicator size="large" color={colors.accentBlue} style={styles.loader} />
      </View>
    );
  }

  const earnedIds = new Set(earned.map((e) => e.badge_id));
  const nextThreshold = LEVEL_THRESHOLDS[(points?.level ?? 1)] ?? 15000;
  const prevThreshold = LEVEL_THRESHOLDS[(points?.level ?? 1) - 1] ?? 0;
  const progressPct = points
    ? Math.min(1, (points.total_points - prevThreshold) / Math.max(1, nextThreshold - prevThreshold))
    : 0;

  return (
    <View style={styles.container}>
      <ScreenHeader title="Basarilar" />
      <FlatList
        data={allBadges}
        keyExtractor={(b) => b.id}
        numColumns={2}
        columnWrapperStyle={styles.badgeRow}
        contentContainerStyle={styles.list}
        ListHeaderComponent={
          points ? (
            <View style={styles.header}>
              <LinearGradient
                colors={[colors.bgTertiary, colors.bgSecondary]}
                style={styles.levelCard}
              >
                <Text style={styles.levelNum}>Lv.{points.level}</Text>
                <Text style={styles.levelName}>{LEVEL_NAMES[points.level] || ""}</Text>
                <Text style={styles.totalPts}>{points.total_points.toLocaleString()} puan</Text>
                <View style={styles.bar}>
                  <View style={[styles.barFill, { width: `${Math.round(progressPct * 100)}%` }]} />
                </View>
                <View style={styles.streakRow}>
                  <Text style={styles.streakText}>{"\uD83D\uDD25"} {points.current_streak_days} gun seri</Text>
                  <Text style={styles.streakText}>En uzun: {points.longest_streak_days}</Text>
                </View>
              </LinearGradient>

              <View style={styles.breakdown}>
                <BreakdownItem label="Rota" value={points.points_routes} />
                <BreakdownItem label="Rapor" value={points.points_reports} />
                <BreakdownItem label="Topluluk" value={points.points_community} />
                <BreakdownItem label="Yardim" value={points.points_helping} />
              </View>

              <Text style={styles.sectionTitle}>
                Rozetler ({earned.length}/{allBadges.length})
              </Text>
            </View>
          ) : null
        }
        renderItem={({ item }) => {
          const isEarned = earnedIds.has(item.id);
          return (
            <GlassCard style={[styles.badgeCard, !isEarned && styles.badgeLocked]}>
              <Text style={[styles.badgeIcon, !isEarned && styles.badgeIconLocked]}>
                {item.icon}
              </Text>
              <Text style={styles.badgeName}>{item.name_tr}</Text>
              <Text style={styles.badgeDesc} numberOfLines={2}>{item.description_tr}</Text>
              {isEarned ? (
                <Text style={styles.badgeEarned}>{"\u2713"} Kazanildi</Text>
              ) : (
                <Text style={styles.badgeReward}>+{item.points_reward} puan</Text>
              )}
            </GlassCard>
          );
        }}
        ListEmptyComponent={<Text style={styles.empty}>Rozet bulunamadi</Text>}
      />
    </View>
  );
}

function BreakdownItem({ label, value }: { label: string; value: number }) {
  return (
    <View style={styles.breakdownItem}>
      <Text style={styles.breakdownVal}>{value}</Text>
      <Text style={styles.breakdownLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  loader: { marginTop: spacing.xl },
  list: { padding: spacing.md, paddingBottom: 100 },
  header: { marginBottom: spacing.md },
  levelCard: { borderRadius: radius.lg, padding: spacing.lg, alignItems: "center", marginBottom: spacing.md },
  levelNum: { fontSize: 36, fontWeight: "800", color: colors.accentBlue },
  levelName: { fontSize: 16, fontWeight: "600", color: colors.textSecondary, marginBottom: spacing.xs },
  totalPts: { fontSize: 14, color: colors.textTertiary, marginBottom: spacing.sm },
  bar: { width: "100%", height: 6, backgroundColor: "rgba(255,255,255,0.1)", borderRadius: 3, overflow: "hidden" },
  barFill: { height: "100%", backgroundColor: colors.accentBlue, borderRadius: 3 },
  streakRow: { flexDirection: "row", justifyContent: "space-between", width: "100%", marginTop: spacing.sm },
  streakText: { fontSize: 12, color: colors.textSecondary },
  breakdown: { flexDirection: "row", justifyContent: "space-around", marginBottom: spacing.lg },
  breakdownItem: { alignItems: "center" },
  breakdownVal: { fontSize: 20, fontWeight: "700", color: colors.textPrimary },
  breakdownLabel: { fontSize: 11, color: colors.textTertiary, marginTop: 2 },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: colors.textPrimary, marginBottom: spacing.sm },
  badgeRow: { gap: spacing.sm },
  badgeCard: { flex: 1, padding: spacing.md, alignItems: "center", marginBottom: spacing.sm },
  badgeLocked: { opacity: 0.45 },
  badgeIcon: { fontSize: 36, marginBottom: spacing.xs },
  badgeIconLocked: { opacity: 0.5 },
  badgeName: { fontSize: 13, fontWeight: "700", color: colors.textPrimary, textAlign: "center" },
  badgeDesc: { fontSize: 11, color: colors.textSecondary, textAlign: "center", marginTop: 2, marginBottom: spacing.xs },
  badgeEarned: { fontSize: 11, fontWeight: "700", color: colors.success },
  badgeReward: { fontSize: 11, color: colors.textTertiary },
  empty: { fontSize: 14, color: colors.textSecondary, textAlign: "center", marginTop: spacing.xl },
});
