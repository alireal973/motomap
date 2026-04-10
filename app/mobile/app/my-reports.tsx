// app/mobile/app/my-reports.tsx
import { useState, useEffect, useCallback } from "react";
import {
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import ScreenHeader from "../components/ScreenHeader";
import GlassCard from "../components/GlassCard";
import EmptyState from "../components/EmptyState";
import LoadingScreen from "../components/LoadingScreen";
import { colors, spacing, radius } from "../theme";
import { useAuth } from "../context/AuthContext";
import { apiRequest } from "../utils/api";

type ReportStatus = "pending" | "verified" | "expired" | "rejected";
type ReportType = "hazard" | "accident" | "road_work" | "police" | "flood" | "other";

type Report = {
  id: string;
  type: ReportType;
  description: string;
  location_name: string;
  status: ReportStatus;
  verifications_count: number;
  created_at: string;
  expires_at?: string;
};

const REPORT_TYPE_CONFIG: Record<ReportType, { icon: keyof typeof Ionicons.glyphMap; label: string; color: string }> = {
  hazard: { icon: "warning", label: "Tehlike", color: colors.warning },
  accident: { icon: "car", label: "Kaza", color: colors.danger },
  road_work: { icon: "construct", label: "Yol Çalışması", color: colors.info },
  police: { icon: "shield", label: "Polis", color: colors.accentBlue },
  flood: { icon: "water", label: "Su Birikintisi", color: colors.accentBlue },
  other: { icon: "alert-circle", label: "Diğer", color: colors.textSecondary },
};

const STATUS_CONFIG: Record<ReportStatus, { label: string; color: string }> = {
  pending: { label: "Onay Bekliyor", color: colors.warning },
  verified: { label: "Doğrulandı", color: colors.success },
  expired: { label: "Süresi Doldu", color: colors.textTertiary },
  rejected: { label: "Reddedildi", color: colors.danger },
};

export default function MyReportsScreen() {
  const { token, isAuthenticated } = useAuth();
  const [reports, setReports] = useState<Report[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchReports = useCallback(async () => {
    if (!token) return;
    try {
      const response = await apiRequest("/api/reports/my", { token }) as { reports?: Report[] };
      setReports(response.reports || []);
    } catch {
      // Handle error
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchReports();
    } else {
      setIsLoading(false);
    }
  }, [isAuthenticated, fetchReports]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    fetchReports();
  };

  const handleReportPress = (reportId: string) => {
    router.push(`/report/${reportId}` as never);
  };

  const handleCreateReport = () => {
    router.push("/report/create" as never);
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins} dk önce`;
    if (diffHours < 24) return `${diffHours} sa önce`;
    if (diffDays < 7) return `${diffDays} gün önce`;

    return date.toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "short",
    });
  };

  const renderReportItem = ({ item }: { item: Report }) => {
    const typeConfig = REPORT_TYPE_CONFIG[item.type];
    const statusConfig = STATUS_CONFIG[item.status];

    return (
      <TouchableOpacity onPress={() => handleReportPress(item.id)} activeOpacity={0.7}>
        <GlassCard style={styles.reportCard}>
          <View style={styles.reportHeader}>
            <View style={[styles.typeIcon, { backgroundColor: `${typeConfig.color}20` }]}>
              <Ionicons name={typeConfig.icon} size={24} color={typeConfig.color} />
            </View>
            <View style={styles.reportInfo}>
              <Text style={styles.reportType}>{typeConfig.label}</Text>
              <Text style={styles.reportLocation} numberOfLines={1}>
                {item.location_name}
              </Text>
            </View>
            <View style={[styles.statusBadge, { backgroundColor: `${statusConfig.color}20` }]}>
              <Text style={[styles.statusText, { color: statusConfig.color }]}>
                {statusConfig.label}
              </Text>
            </View>
          </View>

          {item.description && (
            <Text style={styles.reportDescription} numberOfLines={2}>
              {item.description}
            </Text>
          )}

          <View style={styles.reportFooter}>
            <View style={styles.footerItem}>
              <Ionicons name="time-outline" size={14} color={colors.textTertiary} />
              <Text style={styles.footerText}>{formatDate(item.created_at)}</Text>
            </View>
            <View style={styles.footerItem}>
              <Ionicons name="checkmark-circle-outline" size={14} color={colors.textTertiary} />
              <Text style={styles.footerText}>
                {item.verifications_count} doğrulama
              </Text>
            </View>
          </View>
        </GlassCard>
      </TouchableOpacity>
    );
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return (
      <View style={styles.container}>
        <ScreenHeader title="Raporlarım" onBack={() => router.back()} />
        <EmptyState
          icon="📝"
          title="Giriş Yapın"
          description="Raporlarınızı görmek için giriş yapmanız gerekiyor."
        />
      </View>
    );
  }

  const stats = {
    total: reports.length,
    verified: reports.filter((r) => r.status === "verified").length,
    pending: reports.filter((r) => r.status === "pending").length,
  };

  return (
    <View style={styles.container}>
      <ScreenHeader title="Raporlarım" onBack={() => router.back()} />

      {/* Stats */}
      <GlassCard style={styles.statsCard}>
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{stats.total}</Text>
            <Text style={styles.statLabel}>Toplam</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: colors.success }]}>
              {stats.verified}
            </Text>
            <Text style={styles.statLabel}>Doğrulanmış</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: colors.warning }]}>
              {stats.pending}
            </Text>
            <Text style={styles.statLabel}>Bekleyen</Text>
          </View>
        </View>
      </GlassCard>

      {/* Reports List */}
      <FlatList
        data={reports}
        keyExtractor={(item) => item.id}
        renderItem={renderReportItem}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            tintColor={colors.accentBlue}
          />
        }
        ListEmptyComponent={
          <EmptyState
            icon="📋"
            title="Rapor Bulunamadı"
            description="Henüz bir rapor oluşturmadınız. Yol durumlarını bildirerek topluluğa katkıda bulunun!"
          />
        }
      />

      {/* FAB */}
      <TouchableOpacity style={styles.fab} onPress={handleCreateReport} activeOpacity={0.85}>
        <Ionicons name="add" size={28} color="#FFFFFF" />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  statsCard: {
    margin: spacing.md,
    padding: spacing.lg,
  },
  statsRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
  },
  statItem: {
    alignItems: "center",
    flex: 1,
  },
  statValue: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textTertiary,
    marginTop: spacing.xs,
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: colors.surfaceBorder,
  },
  listContent: {
    padding: spacing.md,
    paddingTop: 0,
    paddingBottom: 100,
  },
  reportCard: {
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  reportHeader: {
    flexDirection: "row",
    alignItems: "center",
  },
  typeIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: "center",
    justifyContent: "center",
  },
  reportInfo: {
    flex: 1,
    marginLeft: spacing.md,
  },
  reportType: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  reportLocation: {
    fontSize: 13,
    color: colors.textSecondary,
    marginTop: 2,
  },
  statusBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.sm,
  },
  statusText: {
    fontSize: 11,
    fontWeight: "700",
  },
  reportDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.surfaceBorder,
  },
  reportFooter: {
    flexDirection: "row",
    marginTop: spacing.md,
    gap: spacing.lg,
  },
  footerItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  footerText: {
    fontSize: 12,
    color: colors.textTertiary,
  },
  fab: {
    position: "absolute",
    bottom: spacing.xl,
    right: spacing.lg,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.accentBlue,
    alignItems: "center",
    justifyContent: "center",
    shadowColor: colors.accentBlue,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 8,
    elevation: 8,
  },
});
