// app/mobile/components/ChallengeCard.tsx
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";
import GlassCard from "./GlassCard";

type ChallengeStatus = "active" | "completed" | "expired" | "upcoming";

type ChallengeReward = {
  type: "xp" | "badge" | "title";
  value: number | string;
};

type ChallengeCardProps = {
  id: string;
  title: string;
  description: string;
  iconName?: keyof typeof Ionicons.glyphMap;
  progress: number; // current value
  target: number; // target value
  unit?: string;
  status: ChallengeStatus;
  rewards: ChallengeReward[];
  deadline?: Date | string;
  onPress?: () => void;
  onClaimPress?: () => void;
};

const STATUS_CONFIG: Record<ChallengeStatus, { label: string; color: string; icon: keyof typeof Ionicons.glyphMap }> = {
  active: { label: "Aktif", color: colors.accentBlue, icon: "time-outline" },
  completed: { label: "Tamamlandı", color: colors.success, icon: "checkmark-circle" },
  expired: { label: "Süresi Doldu", color: colors.danger, icon: "close-circle" },
  upcoming: { label: "Yakında", color: colors.warning, icon: "hourglass-outline" },
};

export default function ChallengeCard({
  title,
  description,
  iconName = "flag",
  progress,
  target,
  unit = "",
  status,
  rewards,
  deadline,
  onPress,
  onClaimPress,
}: ChallengeCardProps) {
  const progressPercent = Math.min((progress / target) * 100, 100);
  const isCompleted = status === "completed";
  const canClaim = isCompleted && onClaimPress;
  const config = STATUS_CONFIG[status];

  const formatDeadline = (date: Date | string): string => {
    const d = typeof date === "string" ? new Date(date) : date;
    const now = new Date();
    const diffMs = d.getTime() - now.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

    if (diffMs < 0) return "Süresi doldu";
    if (diffDays > 0) return `${diffDays} gün kaldı`;
    if (diffHours > 0) return `${diffHours} saat kaldı`;
    return "Son saatler";
  };

  const renderReward = (reward: ChallengeReward, index: number) => {
    let icon: keyof typeof Ionicons.glyphMap;
    let text: string;

    switch (reward.type) {
      case "xp":
        icon = "flash";
        text = `+${reward.value} XP`;
        break;
      case "badge":
        icon = "trophy";
        text = String(reward.value);
        break;
      case "title":
        icon = "ribbon";
        text = String(reward.value);
        break;
    }

    return (
      <View key={index} style={styles.reward}>
        <Ionicons name={icon} size={14} color={colors.warning} />
        <Text style={styles.rewardText}>{text}</Text>
      </View>
    );
  };

  return (
    <GlassCard style={styles.card} onPress={onPress}>
      {/* Header */}
      <View style={styles.header}>
        <View style={[styles.iconContainer, { backgroundColor: `${config.color}20` }]}>
          <Ionicons name={iconName} size={24} color={config.color} />
        </View>
        <View style={styles.headerInfo}>
          <Text style={styles.title} numberOfLines={1}>
            {title}
          </Text>
          <View style={styles.statusRow}>
            <Ionicons name={config.icon} size={14} color={config.color} />
            <Text style={[styles.statusText, { color: config.color }]}>
              {config.label}
            </Text>
            {deadline && status === "active" && (
              <Text style={styles.deadline}> • {formatDeadline(deadline)}</Text>
            )}
          </View>
        </View>
      </View>

      {/* Description */}
      <Text style={styles.description} numberOfLines={2}>
        {description}
      </Text>

      {/* Progress */}
      <View style={styles.progressSection}>
        <View style={styles.progressHeader}>
          <Text style={styles.progressLabel}>İlerleme</Text>
          <Text style={styles.progressValue}>
            {progress.toLocaleString("tr-TR")} / {target.toLocaleString("tr-TR")} {unit}
          </Text>
        </View>
        <View style={styles.progressBar}>
          <View
            style={[
              styles.progressFill,
              { width: `${progressPercent}%` },
              isCompleted && styles.progressFillCompleted,
            ]}
          />
        </View>
      </View>

      {/* Rewards */}
      <View style={styles.rewardsSection}>
        <Text style={styles.rewardsLabel}>Ödüller:</Text>
        <View style={styles.rewardsList}>
          {rewards.map(renderReward)}
        </View>
      </View>

      {/* Claim Button */}
      {canClaim && (
        <TouchableOpacity
          style={styles.claimButton}
          onPress={(e) => {
            e.stopPropagation?.();
            onClaimPress?.();
          }}
          activeOpacity={0.85}
        >
          <Ionicons name="gift" size={18} color="#FFFFFF" />
          <Text style={styles.claimButtonText}>Ödülü Al</Text>
        </TouchableOpacity>
      )}
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: "center",
    alignItems: "center",
  },
  headerInfo: {
    flex: 1,
    marginLeft: spacing.md,
  },
  title: {
    color: colors.textPrimary,
    fontSize: 17,
    fontWeight: "700",
  },
  statusRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: spacing.xs,
    gap: spacing.xs,
  },
  statusText: {
    fontSize: 12,
    fontWeight: "600",
  },
  deadline: {
    color: colors.textTertiary,
    fontSize: 12,
  },
  description: {
    color: colors.textSecondary,
    fontSize: 14,
    lineHeight: 20,
    marginBottom: spacing.md,
  },
  progressSection: {
    marginBottom: spacing.md,
  },
  progressHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: spacing.xs,
  },
  progressLabel: {
    color: colors.textTertiary,
    fontSize: 12,
    fontWeight: "500",
  },
  progressValue: {
    color: colors.textSecondary,
    fontSize: 12,
    fontWeight: "600",
  },
  progressBar: {
    height: 8,
    backgroundColor: colors.surfaceGlass,
    borderRadius: 4,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: colors.accentBlue,
    borderRadius: 4,
  },
  progressFillCompleted: {
    backgroundColor: colors.success,
  },
  rewardsSection: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
  },
  rewardsLabel: {
    color: colors.textTertiary,
    fontSize: 12,
  },
  rewardsList: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
  },
  reward: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(245, 158, 11, 0.1)",
    borderRadius: radius.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    gap: spacing.xs,
  },
  rewardText: {
    color: colors.warning,
    fontSize: 12,
    fontWeight: "600",
  },
  claimButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.success,
    borderRadius: radius.pill,
    paddingVertical: spacing.md,
    marginTop: spacing.md,
    gap: spacing.sm,
  },
  claimButtonText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "700",
  },
});
