import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius, typography, shadows } from "../../theme";
import GlassCard from "../../components/GlassCard";
import { useAuth } from "../../context/AuthContext";

interface ReportData {
  id: string;
  type: "hazard" | "accident" | "police" | "traffic" | "road_work" | "weather";
  title: string;
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  status: "active" | "resolved" | "expired";
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  reporter: {
    id: string;
    username: string;
  };
  confirmations: number;
  created_at: string;
  updated_at: string;
  expires_at?: string;
  images?: string[];
}

const REPORT_TYPE_CONFIG = {
  hazard: { label: "Tehlike", icon: "warning", color: "#FF9800" },
  accident: { label: "Kaza", icon: "car", color: "#F44336" },
  police: { label: "Polis", icon: "shield-checkmark", color: "#2196F3" },
  traffic: { label: "Trafik", icon: "car-outline", color: "#9C27B0" },
  road_work: { label: "Yol Çalışması", icon: "construct", color: "#FF5722" },
  weather: { label: "Hava Durumu", icon: "cloud", color: "#607D8B" },
};

const SEVERITY_CONFIG = {
  low: { label: "Düşük", color: "#4CAF50" },
  medium: { label: "Orta", color: "#FFC107" },
  high: { label: "Yüksek", color: "#FF9800" },
  critical: { label: "Kritik", color: "#F44336" },
};

const STATUS_CONFIG = {
  active: { label: "Aktif", color: "#4CAF50" },
  resolved: { label: "Çözüldü", color: "#9E9E9E" },
  expired: { label: "Süresi Doldu", color: "#607D8B" },
};

export default function ReportDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { user } = useAuth();
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState(false);
  const [hasConfirmed, setHasConfirmed] = useState(false);

  useEffect(() => {
    fetchReportDetails();
  }, [id]);

  const fetchReportDetails = async () => {
    try {
      // TODO: API call
      setTimeout(() => {
        setReport({
          id: id || "1",
          type: "hazard",
          title: "Yolda döküntü/engel var",
          description: "D100 karayolu Gebze çıkışında sağ şeritte büyük bir demir parçası var. Dikkatli geçin!",
          severity: "high",
          status: "active",
          location: {
            latitude: 40.8025,
            longitude: 29.4367,
            address: "D100 Karayolu, Gebze Çıkışı, Kocaeli",
          },
          reporter: {
            id: "u1",
            username: "rider34",
          },
          confirmations: 12,
          created_at: "2024-01-20T14:30:00Z",
          updated_at: "2024-01-20T15:45:00Z",
          expires_at: "2024-01-21T14:30:00Z",
        });
        setLoading(false);
      }, 500);
    } catch (error) {
      console.error("Error fetching report:", error);
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!report || hasConfirmed) return;
    setConfirming(true);

    try {
      // TODO: API call
      setReport({ ...report, confirmations: report.confirmations + 1 });
      setHasConfirmed(true);
    } finally {
      setConfirming(false);
    }
  };

  const handleReportResolved = async () => {
    if (!report) return;
    // TODO: API call to mark as resolved
    router.back();
  };

  const handleShowOnMap = () => {
    if (!report) return;
    router.push(`/map?lat=${report.location.latitude}&lng=${report.location.longitude}&report=${id}`);
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleString("tr-TR", {
      day: "numeric",
      month: "long",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getTimeRemaining = (expiresAt?: string): string | null => {
    if (!expiresAt) return null;
    const now = new Date();
    const expires = new Date(expiresAt);
    const diffMs = expires.getTime() - now.getTime();
    
    if (diffMs <= 0) return "Süresi doldu";
    
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) return `${hours}s ${minutes}dk kaldı`;
    return `${minutes}dk kaldı`;
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

  if (!report) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={64} color={colors.textSecondary} />
          <Text style={styles.errorText}>Rapor bulunamadı</Text>
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Text style={styles.backButtonText}>Geri Dön</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const typeConfig = REPORT_TYPE_CONFIG[report.type];
  const severityConfig = SEVERITY_CONFIG[report.severity];
  const statusConfig = STATUS_CONFIG[report.status];
  const timeRemaining = getTimeRemaining(report.expires_at);
  const isOwner = user?.id === report.reporter.id;

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.headerButton}>
          <Ionicons name="arrow-back" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Rapor Detayı</Text>
        {isOwner && (
          <TouchableOpacity style={styles.headerButton}>
            <Ionicons name="ellipsis-vertical" size={24} color={colors.textPrimary} />
          </TouchableOpacity>
        )}
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
        {/* Type & Status Badge */}
        <View style={styles.badgesRow}>
          <View style={[styles.typeBadge, { backgroundColor: typeConfig.color + "20" }]}>
            <Ionicons name={typeConfig.icon as any} size={18} color={typeConfig.color} />
            <Text style={[styles.typeBadgeText, { color: typeConfig.color }]}>
              {typeConfig.label}
            </Text>
          </View>

          <View style={[styles.statusBadge, { backgroundColor: statusConfig.color + "20" }]}>
            <View style={[styles.statusDot, { backgroundColor: statusConfig.color }]} />
            <Text style={[styles.statusBadgeText, { color: statusConfig.color }]}>
              {statusConfig.label}
            </Text>
          </View>
        </View>

        {/* Title & Severity */}
        <Text style={styles.title}>{report.title}</Text>
        <View style={[styles.severityBadge, { backgroundColor: severityConfig.color + "20" }]}>
          <Ionicons name="alert-circle" size={16} color={severityConfig.color} />
          <Text style={[styles.severityText, { color: severityConfig.color }]}>
            {severityConfig.label} Öncelik
          </Text>
        </View>

        {/* Description */}
        <GlassCard style={styles.descriptionCard}>
          <Text style={styles.description}>{report.description}</Text>
        </GlassCard>

        {/* Location */}
        <GlassCard style={styles.locationCard}>
          <View style={styles.locationHeader}>
            <Ionicons name="location" size={20} color={colors.accentBlue} />
            <Text style={styles.locationTitle}>Konum</Text>
          </View>
          <Text style={styles.locationAddress}>{report.location.address}</Text>
          <TouchableOpacity style={styles.showMapButton} onPress={handleShowOnMap}>
            <Ionicons name="map-outline" size={18} color={colors.accentBlue} />
            <Text style={styles.showMapText}>Haritada Göster</Text>
          </TouchableOpacity>
        </GlassCard>

        {/* Info Cards */}
        <View style={styles.infoRow}>
          <GlassCard style={styles.infoCard}>
            <Ionicons name="person-outline" size={24} color={colors.textSecondary} />
            <Text style={styles.infoLabel}>Bildiren</Text>
            <Text style={styles.infoValue}>{report.reporter.username}</Text>
          </GlassCard>

          <GlassCard style={styles.infoCard}>
            <Ionicons name="checkmark-circle-outline" size={24} color={colors.successGreen} />
            <Text style={styles.infoLabel}>Onay</Text>
            <Text style={styles.infoValue}>{report.confirmations}</Text>
          </GlassCard>
        </View>

        {/* Timestamps */}
        <GlassCard style={styles.timestampCard}>
          <View style={styles.timestampRow}>
            <Ionicons name="time-outline" size={18} color={colors.textSecondary} />
            <Text style={styles.timestampLabel}>Oluşturulma:</Text>
            <Text style={styles.timestampValue}>{formatDate(report.created_at)}</Text>
          </View>
          <View style={styles.timestampRow}>
            <Ionicons name="refresh-outline" size={18} color={colors.textSecondary} />
            <Text style={styles.timestampLabel}>Son güncelleme:</Text>
            <Text style={styles.timestampValue}>{formatDate(report.updated_at)}</Text>
          </View>
          {timeRemaining && (
            <View style={styles.timestampRow}>
              <Ionicons name="hourglass-outline" size={18} color={colors.warningYellow} />
              <Text style={styles.timestampLabel}>Geçerlilik:</Text>
              <Text style={[styles.timestampValue, { color: colors.warningYellow }]}>
                {timeRemaining}
              </Text>
            </View>
          )}
        </GlassCard>
      </ScrollView>

      {/* Bottom Actions */}
      {report.status === "active" && (
        <View style={styles.bottomActions}>
          {!isOwner && (
            <TouchableOpacity
              style={[styles.confirmButton, hasConfirmed && styles.confirmedButton]}
              onPress={handleConfirm}
              disabled={hasConfirmed || confirming}
            >
              {confirming ? (
                <ActivityIndicator size="small" color={colors.textPrimary} />
              ) : (
                <>
                  <Ionicons
                    name={hasConfirmed ? "checkmark-circle" : "checkmark-circle-outline"}
                    size={24}
                    color={colors.textPrimary}
                  />
                  <Text style={styles.confirmButtonText}>
                    {hasConfirmed ? "Onaylandı" : "Onayla"}
                  </Text>
                </>
              )}
            </TouchableOpacity>
          )}

          {isOwner && (
            <TouchableOpacity style={styles.resolveButton} onPress={handleReportResolved}>
              <Ionicons name="checkmark-done" size={24} color={colors.textPrimary} />
              <Text style={styles.resolveButtonText}>Çözüldü Olarak İşaretle</Text>
            </TouchableOpacity>
          )}
        </View>
      )}
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
  backButton: {
    marginTop: spacing.lg,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.sm,
    backgroundColor: colors.accentBlue,
    borderRadius: radius.md,
  },
  backButtonText: {
    ...typography.button,
    color: colors.textPrimary,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderDefault,
  },
  headerButton: {
    padding: spacing.sm,
  },
  headerTitle: {
    ...typography.h4,
    color: colors.textPrimary,
    flex: 1,
    textAlign: "center",
  },
  scrollContent: {
    padding: spacing.md,
  },
  badgesRow: {
    flexDirection: "row",
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  typeBadge: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
    gap: spacing.xs,
  },
  typeBadgeText: {
    ...typography.caption,
    fontWeight: "600",
  },
  statusBadge: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
    gap: spacing.xs,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  statusBadgeText: {
    ...typography.caption,
    fontWeight: "600",
  },
  title: {
    ...typography.h2,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  severityBadge: {
    flexDirection: "row",
    alignItems: "center",
    alignSelf: "flex-start",
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.sm,
    gap: spacing.xs,
    marginBottom: spacing.md,
  },
  severityText: {
    ...typography.caption,
    fontWeight: "600",
  },
  descriptionCard: {
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  description: {
    ...typography.body,
    color: colors.textSecondary,
    lineHeight: 24,
  },
  locationCard: {
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  locationHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  locationTitle: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: "600",
  },
  locationAddress: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  showMapButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  showMapText: {
    ...typography.bodySmall,
    color: colors.accentBlue,
  },
  infoRow: {
    flexDirection: "row",
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  infoCard: {
    flex: 1,
    padding: spacing.md,
    alignItems: "center",
  },
  infoLabel: {
    ...typography.caption,
    color: colors.textMuted,
    marginTop: spacing.xs,
  },
  infoValue: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: "600",
    marginTop: 2,
  },
  timestampCard: {
    padding: spacing.md,
  },
  timestampRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.sm,
    gap: spacing.sm,
  },
  timestampLabel: {
    ...typography.bodySmall,
    color: colors.textMuted,
  },
  timestampValue: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    flex: 1,
    textAlign: "right",
  },
  bottomActions: {
    padding: spacing.md,
    paddingBottom: spacing.lg,
    borderTopWidth: 1,
    borderTopColor: colors.borderDefault,
  },
  confirmButton: {
    flexDirection: "row",
    backgroundColor: colors.successGreen,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    justifyContent: "center",
    alignItems: "center",
    gap: spacing.sm,
  },
  confirmedButton: {
    backgroundColor: colors.surfaceGlass,
  },
  confirmButtonText: {
    ...typography.button,
    color: colors.textPrimary,
  },
  resolveButton: {
    flexDirection: "row",
    backgroundColor: colors.accentBlue,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    justifyContent: "center",
    alignItems: "center",
    gap: spacing.sm,
  },
  resolveButtonText: {
    ...typography.button,
    color: colors.textPrimary,
  },
});
