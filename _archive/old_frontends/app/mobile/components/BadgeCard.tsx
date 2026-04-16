// app/mobile/components/BadgeCard.tsx
import { StyleSheet, Text, View, Image } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";
import GlassCard from "./GlassCard";

type BadgeRarity = "common" | "rare" | "epic" | "legendary";

type BadgeCardProps = {
  id: string;
  name: string;
  description: string;
  iconUrl?: string;
  iconName?: keyof typeof Ionicons.glyphMap;
  rarity?: BadgeRarity;
  earnedAt?: Date | string;
  progress?: number; // 0-100, if not earned yet
  onPress?: () => void;
};

const RARITY_COLORS: Record<BadgeRarity, string> = {
  common: colors.textSecondary,
  rare: colors.accentBlue,
  epic: colors.info,
  legendary: colors.warning,
};

const RARITY_LABELS: Record<BadgeRarity, string> = {
  common: "Yaygın",
  rare: "Nadir",
  epic: "Epik",
  legendary: "Efsanevi",
};

export default function BadgeCard({
  name,
  description,
  iconUrl,
  iconName = "trophy",
  rarity = "common",
  earnedAt,
  progress,
  onPress,
}: BadgeCardProps) {
  const isEarned = !!earnedAt;
  const rarityColor = RARITY_COLORS[rarity];

  const formatDate = (date: Date | string): string => {
    const d = typeof date === "string" ? new Date(date) : date;
    return d.toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  return (
    <GlassCard
      style={[styles.card, !isEarned && styles.cardLocked]}
      onPress={onPress}
    >
      {/* Badge Icon */}
      <View style={[styles.iconContainer, { borderColor: rarityColor }]}>
        {iconUrl ? (
          <Image
            source={{ uri: iconUrl }}
            style={[styles.iconImage, !isEarned && styles.iconLocked]}
          />
        ) : (
          <Ionicons
            name={iconName}
            size={32}
            color={isEarned ? rarityColor : colors.textTertiary}
          />
        )}
        {!isEarned && (
          <View style={styles.lockOverlay}>
            <Ionicons name="lock-closed" size={16} color={colors.textTertiary} />
          </View>
        )}
      </View>

      {/* Info */}
      <View style={styles.info}>
        <Text style={[styles.name, !isEarned && styles.textLocked]} numberOfLines={1}>
          {name}
        </Text>
        <Text style={[styles.description, !isEarned && styles.textLocked]} numberOfLines={2}>
          {description}
        </Text>

        {/* Rarity Badge */}
        <View style={styles.footer}>
          <View style={[styles.rarityBadge, { backgroundColor: `${rarityColor}20` }]}>
            <Text style={[styles.rarityText, { color: rarityColor }]}>
              {RARITY_LABELS[rarity]}
            </Text>
          </View>
          
          {isEarned && earnedAt && (
            <Text style={styles.earnedDate}>{formatDate(earnedAt)}</Text>
          )}
        </View>

        {/* Progress Bar (if not earned) */}
        {!isEarned && progress !== undefined && (
          <View style={styles.progressContainer}>
            <View style={styles.progressBar}>
              <View style={[styles.progressFill, { width: `${progress}%` }]} />
            </View>
            <Text style={styles.progressText}>{progress}%</Text>
          </View>
        )}
      </View>
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  cardLocked: {
    opacity: 0.7,
  },
  iconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    borderWidth: 2,
    backgroundColor: colors.surfaceGlass,
    justifyContent: "center",
    alignItems: "center",
    position: "relative",
  },
  iconImage: {
    width: 40,
    height: 40,
    borderRadius: 20,
  },
  iconLocked: {
    opacity: 0.4,
  },
  lockOverlay: {
    position: "absolute",
    bottom: -4,
    right: -4,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.bgSecondary,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 2,
    borderColor: colors.surfaceBorder,
  },
  info: {
    flex: 1,
    marginLeft: spacing.md,
    justifyContent: "center",
  },
  name: {
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: "700",
  },
  textLocked: {
    color: colors.textTertiary,
  },
  description: {
    color: colors.textSecondary,
    fontSize: 13,
    lineHeight: 18,
    marginTop: spacing.xs,
  },
  footer: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: spacing.sm,
    gap: spacing.sm,
  },
  rarityBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.sm,
  },
  rarityText: {
    fontSize: 11,
    fontWeight: "700",
    textTransform: "uppercase",
  },
  earnedDate: {
    color: colors.textTertiary,
    fontSize: 11,
  },
  progressContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: spacing.sm,
    gap: spacing.sm,
  },
  progressBar: {
    flex: 1,
    height: 6,
    backgroundColor: colors.surfaceGlass,
    borderRadius: 3,
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    backgroundColor: colors.accentBlue,
    borderRadius: 3,
  },
  progressText: {
    color: colors.textTertiary,
    fontSize: 11,
    fontWeight: "600",
    minWidth: 32,
    textAlign: "right",
  },
});
