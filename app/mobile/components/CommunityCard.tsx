// app/mobile/components/CommunityCard.tsx
import { StyleSheet, Text, TouchableOpacity, View, Image } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";
import GlassCard from "./GlassCard";

type CommunityCardProps = {
  id: string;
  name: string;
  slug: string;
  description?: string;
  imageUrl?: string;
  memberCount: number;
  postCount?: number;
  isJoined?: boolean;
  onPress?: () => void;
  onJoinPress?: () => void;
};

export default function CommunityCard({
  name,
  description,
  imageUrl,
  memberCount,
  postCount,
  isJoined = false,
  onPress,
  onJoinPress,
}: CommunityCardProps) {
  const formatCount = (count: number): string => {
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
    return count.toString();
  };

  return (
    <GlassCard style={styles.card} onPress={onPress}>
      <View style={styles.content}>
        {/* Image */}
        {imageUrl ? (
          <Image source={{ uri: imageUrl }} style={styles.image} />
        ) : (
          <View style={styles.imagePlaceholder}>
            <Ionicons name="people" size={24} color={colors.textTertiary} />
          </View>
        )}

        {/* Info */}
        <View style={styles.info}>
          <Text style={styles.name} numberOfLines={1}>
            {name}
          </Text>
          {description && (
            <Text style={styles.description} numberOfLines={2}>
              {description}
            </Text>
          )}
          <View style={styles.stats}>
            <View style={styles.stat}>
              <Ionicons name="people-outline" size={14} color={colors.textTertiary} />
              <Text style={styles.statText}>{formatCount(memberCount)} üye</Text>
            </View>
            {postCount !== undefined && (
              <View style={styles.stat}>
                <Ionicons name="chatbubbles-outline" size={14} color={colors.textTertiary} />
                <Text style={styles.statText}>{formatCount(postCount)} gönderi</Text>
              </View>
            )}
          </View>
        </View>

        {/* Join Button */}
        <TouchableOpacity
          style={[styles.joinButton, isJoined && styles.joinedButton]}
          onPress={(e) => {
            e.stopPropagation?.();
            onJoinPress?.();
          }}
          activeOpacity={0.7}
        >
          {isJoined ? (
            <Ionicons name="checkmark" size={18} color={colors.success} />
          ) : (
            <Ionicons name="add" size={18} color={colors.accentBlue} />
          )}
        </TouchableOpacity>
      </View>
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  content: {
    flexDirection: "row",
    alignItems: "center",
  },
  image: {
    width: 56,
    height: 56,
    borderRadius: radius.md,
    backgroundColor: colors.surfaceGlass,
  },
  imagePlaceholder: {
    width: 56,
    height: 56,
    borderRadius: radius.md,
    backgroundColor: colors.surfaceGlass,
    justifyContent: "center",
    alignItems: "center",
  },
  info: {
    flex: 1,
    marginLeft: spacing.md,
    marginRight: spacing.sm,
  },
  name: {
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: "700",
  },
  description: {
    color: colors.textSecondary,
    fontSize: 13,
    lineHeight: 18,
    marginTop: spacing.xs,
  },
  stats: {
    flexDirection: "row",
    marginTop: spacing.sm,
    gap: spacing.md,
  },
  stat: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  statText: {
    color: colors.textTertiary,
    fontSize: 12,
  },
  joinButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1,
    borderColor: colors.accentBlue,
    justifyContent: "center",
    alignItems: "center",
  },
  joinedButton: {
    borderColor: colors.success,
    backgroundColor: "rgba(34, 197, 94, 0.1)",
  },
});
