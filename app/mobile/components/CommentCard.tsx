// app/mobile/components/CommentCard.tsx
import { StyleSheet, Text, TouchableOpacity, View, Image } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";

type CommentAuthor = {
  id: string;
  displayName: string;
  avatarUrl?: string;
};

type CommentCardProps = {
  id: string;
  author: CommentAuthor;
  content: string;
  likesCount?: number;
  isLiked?: boolean;
  createdAt: Date | string;
  isReply?: boolean;
  repliesCount?: number;
  onLikePress?: () => void;
  onReplyPress?: () => void;
  onAuthorPress?: () => void;
  onOptionsPress?: () => void;
};

export default function CommentCard({
  author,
  content,
  likesCount = 0,
  isLiked = false,
  createdAt,
  isReply = false,
  repliesCount = 0,
  onLikePress,
  onReplyPress,
  onAuthorPress,
  onOptionsPress,
}: CommentCardProps) {
  const formatTimeAgo = (date: Date | string): string => {
    const now = new Date();
    const commentDate = typeof date === "string" ? new Date(date) : date;
    const diffMs = now.getTime() - commentDate.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return "Az önce";
    if (diffMins < 60) return `${diffMins} dk`;
    if (diffHours < 24) return `${diffHours} sa`;
    if (diffDays < 7) return `${diffDays} g`;

    return commentDate.toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "short",
    });
  };

  return (
    <View style={[styles.container, isReply && styles.replyContainer]}>
      {/* Avatar */}
      <TouchableOpacity onPress={onAuthorPress} disabled={!onAuthorPress}>
        {author.avatarUrl ? (
          <Image
            source={{ uri: author.avatarUrl }}
            style={[styles.avatar, isReply && styles.replyAvatar]}
          />
        ) : (
          <View style={[styles.avatarPlaceholder, isReply && styles.replyAvatar]}>
            <Text style={[styles.avatarText, isReply && styles.replyAvatarText]}>
              {author.displayName.charAt(0).toUpperCase()}
            </Text>
          </View>
        )}
      </TouchableOpacity>

      {/* Content */}
      <View style={styles.content}>
        <View style={styles.bubble}>
          <View style={styles.header}>
            <TouchableOpacity onPress={onAuthorPress} disabled={!onAuthorPress}>
              <Text style={styles.authorName}>{author.displayName}</Text>
            </TouchableOpacity>
            <Text style={styles.timestamp}>{formatTimeAgo(createdAt)}</Text>
          </View>
          <Text style={styles.text}>{content}</Text>
        </View>

        {/* Actions */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={onLikePress}
            activeOpacity={0.7}
          >
            <Ionicons
              name={isLiked ? "heart" : "heart-outline"}
              size={16}
              color={isLiked ? colors.danger : colors.textTertiary}
            />
            {likesCount > 0 && (
              <Text style={[styles.actionText, isLiked && styles.actionTextActive]}>
                {likesCount}
              </Text>
            )}
          </TouchableOpacity>

          {!isReply && (
            <TouchableOpacity
              style={styles.actionButton}
              onPress={onReplyPress}
              activeOpacity={0.7}
            >
              <Text style={styles.replyText}>Yanıtla</Text>
            </TouchableOpacity>
          )}

          {repliesCount > 0 && !isReply && (
            <TouchableOpacity style={styles.actionButton} onPress={onReplyPress}>
              <Text style={styles.repliesText}>
                {repliesCount} yanıt görüntüle
              </Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity
            style={styles.optionsButton}
            onPress={onOptionsPress}
            activeOpacity={0.7}
          >
            <Ionicons name="ellipsis-horizontal" size={16} color={colors.textTertiary} />
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  replyContainer: {
    paddingLeft: spacing.xxl + spacing.md,
  },
  avatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.surfaceGlass,
  },
  replyAvatar: {
    width: 28,
    height: 28,
    borderRadius: 14,
  },
  avatarPlaceholder: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.accentBlue,
    justifyContent: "center",
    alignItems: "center",
  },
  avatarText: {
    color: "#FFFFFF",
    fontSize: 14,
    fontWeight: "700",
  },
  replyAvatarText: {
    fontSize: 12,
  },
  content: {
    flex: 1,
    marginLeft: spacing.sm,
  },
  bubble: {
    backgroundColor: colors.surfaceGlass,
    borderRadius: radius.md,
    padding: spacing.sm,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.xs,
    gap: spacing.sm,
  },
  authorName: {
    color: colors.textPrimary,
    fontSize: 13,
    fontWeight: "600",
  },
  timestamp: {
    color: colors.textTertiary,
    fontSize: 11,
  },
  text: {
    color: colors.textPrimary,
    fontSize: 14,
    lineHeight: 20,
  },
  actions: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: spacing.xs,
    paddingLeft: spacing.sm,
    gap: spacing.md,
  },
  actionButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  actionText: {
    color: colors.textTertiary,
    fontSize: 12,
    fontWeight: "500",
  },
  actionTextActive: {
    color: colors.danger,
  },
  replyText: {
    color: colors.textSecondary,
    fontSize: 12,
    fontWeight: "600",
  },
  repliesText: {
    color: colors.accentBlue,
    fontSize: 12,
    fontWeight: "500",
  },
  optionsButton: {
    marginLeft: "auto",
    padding: spacing.xs,
  },
});
