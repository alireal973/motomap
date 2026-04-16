// app/mobile/components/PostCard.tsx
import { StyleSheet, Text, TouchableOpacity, View, Image } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";
import GlassCard from "./GlassCard";

type PostAuthor = {
  id: string;
  displayName: string;
  avatarUrl?: string;
};

type PostCardProps = {
  id: string;
  author: PostAuthor;
  content: string;
  imageUrl?: string;
  likesCount: number;
  commentsCount: number;
  isLiked?: boolean;
  createdAt: Date | string;
  onPress?: () => void;
  onLikePress?: () => void;
  onCommentPress?: () => void;
  onAuthorPress?: () => void;
  onSharePress?: () => void;
};

export default function PostCard({
  author,
  content,
  imageUrl,
  likesCount,
  commentsCount,
  isLiked = false,
  createdAt,
  onPress,
  onLikePress,
  onCommentPress,
  onAuthorPress,
  onSharePress,
}: PostCardProps) {
  const formatTimeAgo = (date: Date | string): string => {
    const now = new Date();
    const postDate = typeof date === "string" ? new Date(date) : date;
    const diffMs = now.getTime() - postDate.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return "Az önce";
    if (diffMins < 60) return `${diffMins} dk önce`;
    if (diffHours < 24) return `${diffHours} sa önce`;
    if (diffDays < 7) return `${diffDays} gün önce`;

    return postDate.toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "short",
    });
  };

  return (
    <GlassCard style={styles.card} onPress={onPress}>
      {/* Header */}
      <TouchableOpacity
        style={styles.header}
        onPress={onAuthorPress}
        disabled={!onAuthorPress}
        activeOpacity={0.7}
      >
        {author.avatarUrl ? (
          <Image source={{ uri: author.avatarUrl }} style={styles.avatar} />
        ) : (
          <View style={styles.avatarPlaceholder}>
            <Text style={styles.avatarText}>
              {author.displayName.charAt(0).toUpperCase()}
            </Text>
          </View>
        )}
        <View style={styles.headerInfo}>
          <Text style={styles.authorName}>{author.displayName}</Text>
          <Text style={styles.timestamp}>{formatTimeAgo(createdAt)}</Text>
        </View>
      </TouchableOpacity>

      {/* Content */}
      <Text style={styles.content} numberOfLines={5}>
        {content}
      </Text>

      {/* Image */}
      {imageUrl && (
        <Image source={{ uri: imageUrl }} style={styles.postImage} resizeMode="cover" />
      )}

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={onLikePress}
          activeOpacity={0.7}
        >
          <Ionicons
            name={isLiked ? "heart" : "heart-outline"}
            size={22}
            color={isLiked ? colors.danger : colors.textSecondary}
          />
          <Text style={[styles.actionText, isLiked && styles.actionTextActive]}>
            {likesCount > 0 ? likesCount : ""}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={onCommentPress}
          activeOpacity={0.7}
        >
          <Ionicons name="chatbubble-outline" size={20} color={colors.textSecondary} />
          <Text style={styles.actionText}>{commentsCount > 0 ? commentsCount : ""}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={onSharePress}
          activeOpacity={0.7}
        >
          <Ionicons name="share-outline" size={20} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>
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
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.surfaceGlass,
  },
  avatarPlaceholder: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.accentBlue,
    justifyContent: "center",
    alignItems: "center",
  },
  avatarText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
  },
  headerInfo: {
    marginLeft: spacing.sm,
    flex: 1,
  },
  authorName: {
    color: colors.textPrimary,
    fontSize: 15,
    fontWeight: "600",
  },
  timestamp: {
    color: colors.textTertiary,
    fontSize: 12,
    marginTop: 2,
  },
  content: {
    color: colors.textPrimary,
    fontSize: 15,
    lineHeight: 22,
    marginBottom: spacing.md,
  },
  postImage: {
    width: "100%",
    height: 200,
    borderRadius: radius.md,
    marginBottom: spacing.md,
    backgroundColor: colors.surfaceGlass,
  },
  actions: {
    flexDirection: "row",
    borderTopWidth: 1,
    borderTopColor: colors.surfaceBorder,
    paddingTop: spacing.md,
    gap: spacing.xl,
  },
  actionButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  actionText: {
    color: colors.textSecondary,
    fontSize: 14,
    fontWeight: "500",
  },
  actionTextActive: {
    color: colors.danger,
  },
});
