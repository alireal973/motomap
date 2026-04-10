// app/mobile/components/LeaderboardRow.tsx
import { StyleSheet, Text, TouchableOpacity, View, Image } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";

type TrendDirection = "up" | "down" | "same";

type LeaderboardRowProps = {
  rank: number;
  userId: string;
  displayName: string;
  avatarUrl?: string;
  points: number;
  trend?: TrendDirection;
  trendAmount?: number;
  isCurrentUser?: boolean;
  subtitle?: string;
  onPress?: () => void;
};

const RANK_COLORS: Record<number, string> = {
  1: "#FFD700", // Gold
  2: "#C0C0C0", // Silver
  3: "#CD7F32", // Bronze
};

const TREND_ICONS: Record<TrendDirection, keyof typeof Ionicons.glyphMap> = {
  up: "arrow-up",
  down: "arrow-down",
  same: "remove",
};

const TREND_COLORS: Record<TrendDirection, string> = {
  up: colors.success,
  down: colors.danger,
  same: colors.textTertiary,
};

export default function LeaderboardRow({
  rank,
  displayName,
  avatarUrl,
  points,
  trend,
  trendAmount,
  isCurrentUser = false,
  subtitle,
  onPress,
}: LeaderboardRowProps) {
  const isTopThree = rank <= 3;
  const rankColor = RANK_COLORS[rank] || colors.textTertiary;

  const formatPoints = (pts: number): string => {
    if (pts >= 1000000) return `${(pts / 1000000).toFixed(1)}M`;
    if (pts >= 1000) return `${(pts / 1000).toFixed(1)}K`;
    return pts.toLocaleString("tr-TR");
  };

  return (
    <TouchableOpacity
      style={[
        styles.container,
        isCurrentUser && styles.currentUserContainer,
        isTopThree && styles.topThreeContainer,
      ]}
      onPress={onPress}
      activeOpacity={0.7}
      disabled={!onPress}
    >
      {/* Rank */}
      <View style={styles.rankContainer}>
        {isTopThree ? (
          <View style={[styles.medalContainer, { backgroundColor: `${rankColor}20` }]}>
            <Ionicons name="trophy" size={18} color={rankColor} />
          </View>
        ) : (
          <Text style={styles.rankText}>{rank}</Text>
        )}
      </View>

      {/* Avatar */}
      {avatarUrl ? (
        <Image source={{ uri: avatarUrl }} style={styles.avatar} />
      ) : (
        <View style={[styles.avatarPlaceholder, isCurrentUser && styles.currentUserAvatar]}>
          <Text style={styles.avatarText}>
            {displayName.charAt(0).toUpperCase()}
          </Text>
        </View>
      )}

      {/* Info */}
      <View style={styles.info}>
        <Text
          style={[styles.name, isCurrentUser && styles.currentUserName]}
          numberOfLines={1}
        >
          {displayName}
          {isCurrentUser && " (Sen)"}
        </Text>
        {subtitle && (
          <Text style={styles.subtitle} numberOfLines={1}>
            {subtitle}
          </Text>
        )}
      </View>

      {/* Points & Trend */}
      <View style={styles.pointsContainer}>
        <Text style={[styles.points, isTopThree && { color: rankColor }]}>
          {formatPoints(points)}
        </Text>
        {trend && (
          <View style={styles.trendContainer}>
            <Ionicons
              name={TREND_ICONS[trend]}
              size={12}
              color={TREND_COLORS[trend]}
            />
            {trendAmount !== undefined && trendAmount > 0 && (
              <Text style={[styles.trendText, { color: TREND_COLORS[trend] }]}>
                {trendAmount}
              </Text>
            )}
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceGlass,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  currentUserContainer: {
    borderWidth: 1.5,
    borderColor: colors.accentBlue,
    backgroundColor: "rgba(61, 139, 255, 0.08)",
  },
  topThreeContainer: {
    backgroundColor: "rgba(255, 255, 255, 0.05)",
  },
  rankContainer: {
    width: 36,
    alignItems: "center",
    marginRight: spacing.sm,
  },
  medalContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: "center",
    alignItems: "center",
  },
  rankText: {
    color: colors.textTertiary,
    fontSize: 16,
    fontWeight: "700",
  },
  avatar: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: colors.surfaceGlass,
  },
  avatarPlaceholder: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: colors.bgTertiary,
    justifyContent: "center",
    alignItems: "center",
  },
  currentUserAvatar: {
    backgroundColor: colors.accentBlue,
  },
  avatarText: {
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: "700",
  },
  info: {
    flex: 1,
    marginLeft: spacing.md,
  },
  name: {
    color: colors.textPrimary,
    fontSize: 15,
    fontWeight: "600",
  },
  currentUserName: {
    color: colors.accentBlue,
  },
  subtitle: {
    color: colors.textTertiary,
    fontSize: 12,
    marginTop: 2,
  },
  pointsContainer: {
    alignItems: "flex-end",
  },
  points: {
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: "700",
  },
  trendContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 2,
    gap: 2,
  },
  trendText: {
    fontSize: 11,
    fontWeight: "600",
  },
});
