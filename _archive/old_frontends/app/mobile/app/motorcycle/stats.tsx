import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  ActivityIndicator,
} from "react-native";
import { router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius, typography, shadows } from "../../theme";
import GlassCard from "../../components/GlassCard";
import { useAuth } from "../../context/AuthContext";

const { width } = Dimensions.get("window");

interface MotorcycleStats {
  motorcycle: {
    id: string;
    brand: string;
    model: string;
    year: number;
    nickname?: string;
    image_url?: string;
  };
  total_distance_km: number;
  total_rides: number;
  total_duration_hours: number;
  avg_speed_kmh: number;
  max_speed_kmh: number;
  avg_ride_distance_km: number;
  longest_ride_km: number;
  favorite_route?: {
    id: string;
    name: string;
    times_ridden: number;
  };
  monthly_stats: Array<{
    month: string;
    distance_km: number;
    rides: number;
  }>;
  achievements: Array<{
    id: string;
    name: string;
    icon: string;
    earned_at: string;
  }>;
}

export default function MotorcycleStatsScreen() {
  const { token } = useAuth();
  const [stats, setStats] = useState<MotorcycleStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<"week" | "month" | "year" | "all">("month");

  useEffect(() => {
    fetchStats();
  }, [selectedPeriod]);

  const fetchStats = async () => {
    try {
      // TODO: API call with period filter
      setTimeout(() => {
        setStats({
          motorcycle: {
            id: "1",
            brand: "Yamaha",
            model: "MT-07",
            year: 2022,
            nickname: "Gece Kartalı",
          },
          total_distance_km: 12500,
          total_rides: 156,
          total_duration_hours: 245,
          avg_speed_kmh: 51,
          max_speed_kmh: 178,
          avg_ride_distance_km: 80.1,
          longest_ride_km: 456,
          favorite_route: {
            id: "r1",
            name: "Belgrad Ormanı Turu",
            times_ridden: 23,
          },
          monthly_stats: [
            { month: "Oca", distance_km: 450, rides: 8 },
            { month: "Şub", distance_km: 380, rides: 6 },
            { month: "Mar", distance_km: 720, rides: 12 },
            { month: "Nis", distance_km: 890, rides: 15 },
            { month: "May", distance_km: 1100, rides: 18 },
            { month: "Haz", distance_km: 1450, rides: 22 },
          ],
          achievements: [
            { id: "a1", name: "İlk 1000 km", icon: "trophy", earned_at: "2023-06-15" },
            { id: "a2", name: "Gece Gezgini", icon: "moon", earned_at: "2023-07-20" },
            { id: "a3", name: "10.000 km Kulübü", icon: "ribbon", earned_at: "2024-01-10" },
          ],
        });
        setLoading(false);
      }, 500);
    } catch (error) {
      console.error("Error fetching stats:", error);
      setLoading(false);
    }
  };

  const formatNumber = (num: number): string => {
    return num.toLocaleString("tr-TR");
  };

  const getMaxMonthlyDistance = (): number => {
    if (!stats) return 1;
    return Math.max(...stats.monthly_stats.map((m) => m.distance_km));
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.accentBlue} />
        </View>
      </SafeAreaView>
    );
  }

  if (!stats) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Ionicons name="analytics-outline" size={64} color={colors.textSecondary} />
          <Text style={styles.errorText}>İstatistikler yüklenemedi</Text>
        </View>
      </SafeAreaView>
    );
  }

  const maxDistance = getMaxMonthlyDistance();

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.headerButton}>
          <Ionicons name="arrow-back" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>
            {stats.motorcycle.nickname || `${stats.motorcycle.brand} ${stats.motorcycle.model}`}
          </Text>
          <Text style={styles.headerSubtitle}>İstatistikler</Text>
        </View>
        <TouchableOpacity
          onPress={() => router.push(`/motorcycle/${stats.motorcycle.id}` as any)}
          style={styles.headerButton}
        >
          <Ionicons name="create-outline" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
      </View>

      {/* Period Selector */}
      <View style={styles.periodSelector}>
        {(["week", "month", "year", "all"] as const).map((period) => (
          <TouchableOpacity
            key={period}
            style={[styles.periodButton, selectedPeriod === period && styles.periodButtonActive]}
            onPress={() => setSelectedPeriod(period)}
          >
            <Text
              style={[styles.periodText, selectedPeriod === period && styles.periodTextActive]}
            >
              {period === "week" ? "Hafta" : period === "month" ? "Ay" : period === "year" ? "Yıl" : "Tümü"}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        {/* Main Stats Grid */}
        <View style={styles.statsGrid}>
          <GlassCard style={styles.statCard}>
            <Ionicons name="speedometer-outline" size={28} color={colors.accentBlue} />
            <Text style={styles.statValue}>{formatNumber(stats.total_distance_km)}</Text>
            <Text style={styles.statLabel}>Toplam km</Text>
          </GlassCard>

          <GlassCard style={styles.statCard}>
            <Ionicons name="bicycle-outline" size={28} color={colors.accentBlue} />
            <Text style={styles.statValue}>{stats.total_rides}</Text>
            <Text style={styles.statLabel}>Sürüş</Text>
          </GlassCard>

          <GlassCard style={styles.statCard}>
            <Ionicons name="time-outline" size={28} color={colors.accentBlue} />
            <Text style={styles.statValue}>{stats.total_duration_hours}</Text>
            <Text style={styles.statLabel}>Saat</Text>
          </GlassCard>

          <GlassCard style={styles.statCard}>
            <Ionicons name="flash-outline" size={28} color={colors.accentBlue} />
            <Text style={styles.statValue}>{stats.avg_speed_kmh}</Text>
            <Text style={styles.statLabel}>Ort. km/s</Text>
          </GlassCard>
        </View>

        {/* Speed Stats */}
        <Text style={styles.sectionTitle}>Hız İstatistikleri</Text>
        <GlassCard style={styles.speedCard}>
          <View style={styles.speedRow}>
            <View style={styles.speedItem}>
              <Ionicons name="trending-up" size={24} color="#4CAF50" />
              <Text style={styles.speedValue}>{stats.max_speed_kmh} km/s</Text>
              <Text style={styles.speedLabel}>Maksimum Hız</Text>
            </View>
            <View style={styles.speedDivider} />
            <View style={styles.speedItem}>
              <Ionicons name="analytics" size={24} color={colors.accentBlue} />
              <Text style={styles.speedValue}>{stats.avg_speed_kmh} km/s</Text>
              <Text style={styles.speedLabel}>Ortalama Hız</Text>
            </View>
          </View>
        </GlassCard>

        {/* Distance Stats */}
        <Text style={styles.sectionTitle}>Mesafe İstatistikleri</Text>
        <GlassCard style={styles.distanceCard}>
          <View style={styles.distanceRow}>
            <View style={styles.distanceItem}>
              <Text style={styles.distanceValue}>{stats.avg_ride_distance_km.toFixed(1)} km</Text>
              <Text style={styles.distanceLabel}>Ort. Sürüş Mesafesi</Text>
            </View>
            <View style={styles.distanceItem}>
              <Text style={styles.distanceValue}>{formatNumber(stats.longest_ride_km)} km</Text>
              <Text style={styles.distanceLabel}>En Uzun Sürüş</Text>
            </View>
          </View>
        </GlassCard>

        {/* Favorite Route */}
        {stats.favorite_route && (
          <>
            <Text style={styles.sectionTitle}>Favori Rota</Text>
            <TouchableOpacity onPress={() => router.push(`/route/${stats.favorite_route?.id}` as any)}>
              <GlassCard style={styles.favoriteRouteCard}>
                <View style={styles.favoriteRouteInfo}>
                  <Ionicons name="heart" size={24} color={colors.errorRed} />
                  <View style={styles.favoriteRouteText}>
                    <Text style={styles.favoriteRouteName}>{stats.favorite_route.name}</Text>
                    <Text style={styles.favoriteRouteCount}>
                      {stats.favorite_route.times_ridden} kez kullanıldı
                    </Text>
                  </View>
                </View>
                <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
              </GlassCard>
            </TouchableOpacity>
          </>
        )}

        {/* Monthly Chart */}
        <Text style={styles.sectionTitle}>Aylık Mesafe</Text>
        <GlassCard style={styles.chartCard}>
          <View style={styles.chartContainer}>
            {stats.monthly_stats.map((month, index) => (
              <View key={index} style={styles.chartBar}>
                <View
                  style={[
                    styles.chartBarFill,
                    { height: `${(month.distance_km / maxDistance) * 100}%` },
                  ]}
                />
                <Text style={styles.chartBarLabel}>{month.month}</Text>
              </View>
            ))}
          </View>
          <View style={styles.chartLegend}>
            <Text style={styles.chartLegendText}>
              Son 6 ay • Toplam: {formatNumber(stats.monthly_stats.reduce((sum, m) => sum + m.distance_km, 0))} km
            </Text>
          </View>
        </GlassCard>

        {/* Achievements */}
        <Text style={styles.sectionTitle}>Başarılar</Text>
        <View style={styles.achievementsRow}>
          {stats.achievements.map((achievement) => (
            <GlassCard key={achievement.id} style={styles.achievementCard}>
              <View style={styles.achievementIcon}>
                <Ionicons name={achievement.icon as any} size={28} color="#FFD700" />
              </View>
              <Text style={styles.achievementName} numberOfLines={2}>
                {achievement.name}
              </Text>
            </GlassCard>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  errorContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: spacing.xl,
  },
  errorText: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.md,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderDefault,
  },
  headerButton: {
    padding: spacing.sm,
  },
  headerCenter: {
    flex: 1,
    alignItems: "center",
  },
  headerTitle: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: "600",
  },
  headerSubtitle: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  periodSelector: {
    flexDirection: "row",
    padding: spacing.md,
    gap: spacing.sm,
  },
  periodButton: {
    flex: 1,
    paddingVertical: spacing.sm,
    alignItems: "center",
    backgroundColor: colors.surfaceGlass,
    borderRadius: radius.md,
  },
  periodButtonActive: {
    backgroundColor: colors.accentBlue,
  },
  periodText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  periodTextActive: {
    color: colors.textPrimary,
    fontWeight: "600",
  },
  scrollContent: {
    padding: spacing.md,
    paddingBottom: spacing.xxl,
  },
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
    marginBottom: spacing.lg,
  },
  statCard: {
    width: (width - spacing.md * 2 - spacing.sm * 2) / 2 - spacing.sm / 2,
    padding: spacing.md,
    alignItems: "center",
  },
  statValue: {
    ...typography.h2,
    color: colors.textPrimary,
    marginTop: spacing.sm,
  },
  statLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  sectionTitle: {
    ...typography.h4,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    marginTop: spacing.md,
  },
  speedCard: {
    padding: spacing.md,
  },
  speedRow: {
    flexDirection: "row",
  },
  speedItem: {
    flex: 1,
    alignItems: "center",
  },
  speedDivider: {
    width: 1,
    backgroundColor: colors.borderDefault,
    marginHorizontal: spacing.md,
  },
  speedValue: {
    ...typography.h3,
    color: colors.textPrimary,
    marginTop: spacing.sm,
  },
  speedLabel: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  distanceCard: {
    padding: spacing.md,
  },
  distanceRow: {
    flexDirection: "row",
  },
  distanceItem: {
    flex: 1,
    alignItems: "center",
  },
  distanceValue: {
    ...typography.h3,
    color: colors.accentBlue,
  },
  distanceLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  favoriteRouteCard: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: spacing.md,
  },
  favoriteRouteInfo: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  favoriteRouteText: {},
  favoriteRouteName: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: "600",
  },
  favoriteRouteCount: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  chartCard: {
    padding: spacing.md,
  },
  chartContainer: {
    flexDirection: "row",
    height: 120,
    alignItems: "flex-end",
    justifyContent: "space-around",
  },
  chartBar: {
    alignItems: "center",
    width: 36,
    height: "100%",
    justifyContent: "flex-end",
  },
  chartBarFill: {
    width: 24,
    backgroundColor: colors.accentBlue,
    borderRadius: radius.xs,
    minHeight: 4,
  },
  chartBarLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  chartLegend: {
    marginTop: spacing.md,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.borderDefault,
  },
  chartLegendText: {
    ...typography.caption,
    color: colors.textMuted,
    textAlign: "center",
  },
  achievementsRow: {
    flexDirection: "row",
    gap: spacing.sm,
  },
  achievementCard: {
    flex: 1,
    padding: spacing.md,
    alignItems: "center",
  },
  achievementIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: "rgba(255, 215, 0, 0.1)",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: spacing.sm,
  },
  achievementName: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: "center",
  },
});
