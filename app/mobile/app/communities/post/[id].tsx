import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Image,
} from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius, typography, shadows } from "../../../theme";
import GlassCard from "../../../components/GlassCard";
import CommentCard from "../../../components/CommentCard";
import { useAuth } from "../../../context/AuthContext";
import { useToast } from "../../../components/Toast";

interface Author {
  id: string;
  username: string;
  avatar_url?: string;
  badge?: string;
}

interface Comment {
  id: string;
  author: Author;
  content: string;
  created_at: string;
  likes: number;
  is_liked: boolean;
  replies?: Comment[];
}

interface PostData {
  id: string;
  author: Author;
  community: {
    id: string;
    name: string;
    slug: string;
  };
  title: string;
  content: string;
  image_url?: string;
  likes: number;
  is_liked: boolean;
  comment_count: number;
  created_at: string;
  tags: string[];
}

export default function PostDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { user, token } = useAuth();
  const { showToast } = useToast();
  const scrollViewRef = useRef<ScrollView>(null);

  const [post, setPost] = useState<PostData | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [replyingTo, setReplyingTo] = useState<{ id: string; username: string } | null>(null);

  useEffect(() => {
    fetchPostAndComments();
  }, [id]);

  const fetchPostAndComments = async () => {
    try {
      // TODO: Replace with actual API calls
      setTimeout(() => {
        setPost({
          id: id || "1",
          author: {
            id: "u1",
            username: "motosever",
            avatar_url: undefined,
            badge: "Pro Rider",
          },
          community: {
            id: "c1",
            name: "İstanbul Motorcuları",
            slug: "istanbul-motorcular",
          },
          title: "Hafta sonu Bolu rotası önerileri",
          content: `Merhaba arkadaşlar! Bu hafta sonu Bolu'ya bir günlük bir tur planlamak istiyorum. Daha önce gidenler var mı? 

Şunları merak ediyorum:
- En güzel manzaralı rota hangisi?
- Yol durumu nasıl?
- Mola için önerilen yerler neler?

Teşekkürler!`,
          image_url: undefined,
          likes: 24,
          is_liked: false,
          comment_count: 8,
          created_at: "2024-01-20T14:30:00Z",
          tags: ["rota", "bolu", "hafta-sonu"],
        });

        setComments([
          {
            id: "cm1",
            author: { id: "u2", username: "karadenizrider", badge: "Expert" },
            content: "Abant gölü rotası harika! D755 üzerinden gidersen manzara muhteşem. Ama virajlara dikkat.",
            created_at: "2024-01-20T15:00:00Z",
            likes: 12,
            is_liked: true,
            replies: [
              {
                id: "cm1r1",
                author: { id: "u3", username: "rider34" },
                content: "Katılıyorum, geçen hafta gittik süperdi!",
                created_at: "2024-01-20T15:30:00Z",
                likes: 3,
                is_liked: false,
              },
            ],
          },
          {
            id: "cm2",
            author: { id: "u4", username: "touring_turkey" },
            content: "Yedigöller de alternatif olabilir. Biraz daha uzun ama kesinlikle görülmeli.",
            created_at: "2024-01-20T16:00:00Z",
            likes: 8,
            is_liked: false,
          },
          {
            id: "cm3",
            author: { id: "u5", username: "adventurerider" },
            content: "Mola için Göynük'teki tarihi konak öneririm. Kahvaltısı efsane!",
            created_at: "2024-01-20T17:00:00Z",
            likes: 5,
            is_liked: false,
          },
        ]);

        setLoading(false);
      }, 500);
    } catch (error) {
      console.error("Error fetching post:", error);
      setLoading(false);
    }
  };

  const handleLikePost = async () => {
    if (!post) return;
    try {
      setPost({
        ...post,
        is_liked: !post.is_liked,
        likes: post.is_liked ? post.likes - 1 : post.likes + 1,
      });
    } catch (error) {
      showToast({ message: "Beğeni işlemi başarısız", type: "error" });
    }
  };

  const handleLikeComment = async (commentId: string) => {
    setComments((prev) =>
      prev.map((c) => {
        if (c.id === commentId) {
          return { ...c, is_liked: !c.is_liked, likes: c.is_liked ? c.likes - 1 : c.likes + 1 };
        }
        if (c.replies) {
          return {
            ...c,
            replies: c.replies.map((r) =>
              r.id === commentId
                ? { ...r, is_liked: !r.is_liked, likes: r.is_liked ? r.likes - 1 : r.likes + 1 }
                : r
            ),
          };
        }
        return c;
      })
    );
  };

  const handleReply = (commentId: string, username: string) => {
    setReplyingTo({ id: commentId, username });
    setNewComment(`@${username} `);
  };

  const handleSubmitComment = async () => {
    if (!newComment.trim()) return;
    setSubmitting(true);

    try {
      // TODO: API call
      const newCommentObj: Comment = {
        id: `cm_${Date.now()}`,
        author: {
          id: user?.id || "me",
          username: user?.username || "Ben",
        },
        content: newComment.trim(),
        created_at: new Date().toISOString(),
        likes: 0,
        is_liked: false,
      };

      if (replyingTo) {
        setComments((prev) =>
          prev.map((c) => {
            if (c.id === replyingTo.id) {
              return { ...c, replies: [...(c.replies || []), newCommentObj] };
            }
            return c;
          })
        );
      } else {
        setComments((prev) => [...prev, newCommentObj]);
      }

      setNewComment("");
      setReplyingTo(null);
      showToast({ message: "Yorum eklendi", type: "success" });

      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    } catch (error) {
      showToast({ message: "Yorum eklenemedi", type: "error" });
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return "Az önce";
    if (diffHours < 24) return `${diffHours} saat önce`;
    if (diffDays < 7) return `${diffDays} gün önce`;
    return date.toLocaleDateString("tr-TR");
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

  if (!post) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={64} color={colors.textSecondary} />
          <Text style={styles.errorText}>Gönderi bulunamadı</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.headerButton}>
          <Ionicons name="arrow-back" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => router.push(`/communities/${post.community.slug}` as any)}
          style={styles.communityLink}
        >
          <Text style={styles.communityName}>{post.community.name}</Text>
          <Ionicons name="chevron-forward" size={16} color={colors.textSecondary} />
        </TouchableOpacity>
        <TouchableOpacity style={styles.headerButton}>
          <Ionicons name="ellipsis-vertical" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
      </View>

      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        keyboardVerticalOffset={100}
      >
        <ScrollView
          ref={scrollViewRef}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.scrollContent}
        >
          {/* Post Content */}
          <View style={styles.postContainer}>
            {/* Author Row */}
            <View style={styles.authorRow}>
              <View style={styles.avatar}>
                {post.author.avatar_url ? (
                  <Image source={{ uri: post.author.avatar_url }} style={styles.avatarImage} />
                ) : (
                  <Ionicons name="person" size={24} color={colors.textSecondary} />
                )}
              </View>
              <View style={styles.authorInfo}>
                <View style={styles.authorNameRow}>
                  <Text style={styles.authorName}>{post.author.username}</Text>
                  {post.author.badge && (
                    <View style={styles.authorBadge}>
                      <Text style={styles.authorBadgeText}>{post.author.badge}</Text>
                    </View>
                  )}
                </View>
                <Text style={styles.postDate}>{formatDate(post.created_at)}</Text>
              </View>
            </View>

            {/* Title & Content */}
            <Text style={styles.postTitle}>{post.title}</Text>
            <Text style={styles.postContent}>{post.content}</Text>

            {/* Image */}
            {post.image_url && (
              <Image source={{ uri: post.image_url }} style={styles.postImage} resizeMode="cover" />
            )}

            {/* Tags */}
            {post.tags.length > 0 && (
              <View style={styles.tagsRow}>
                {post.tags.map((tag, index) => (
                  <TouchableOpacity key={index} style={styles.tag}>
                    <Text style={styles.tagText}>#{tag}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}

            {/* Actions */}
            <View style={styles.actionsRow}>
              <TouchableOpacity style={styles.actionButton} onPress={handleLikePost}>
                <Ionicons
                  name={post.is_liked ? "heart" : "heart-outline"}
                  size={24}
                  color={post.is_liked ? colors.errorRed : colors.textSecondary}
                />
                <Text style={[styles.actionText, post.is_liked && styles.actionTextActive]}>
                  {post.likes}
                </Text>
              </TouchableOpacity>

              <View style={styles.actionButton}>
                <Ionicons name="chatbubble-outline" size={22} color={colors.textSecondary} />
                <Text style={styles.actionText}>{comments.length}</Text>
              </View>

              <TouchableOpacity style={styles.actionButton}>
                <Ionicons name="share-social-outline" size={22} color={colors.textSecondary} />
              </TouchableOpacity>

              <TouchableOpacity style={styles.actionButton}>
                <Ionicons name="bookmark-outline" size={22} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>
          </View>

          {/* Comments Section */}
          <View style={styles.commentsSection}>
            <Text style={styles.commentsTitle}>Yorumlar ({comments.length})</Text>

            {comments.map((comment) => (
              <View key={comment.id}>
                <CommentCard
                  id={comment.id}
                  author={{
                    id: comment.author.id,
                    displayName: comment.author.username,
                    avatarUrl: comment.author.avatar_url,
                  }}
                  content={comment.content}
                  createdAt={comment.created_at}
                  likesCount={comment.likes}
                  isLiked={comment.is_liked}
                  onLikePress={() => handleLikeComment(comment.id)}
                  onReplyPress={() => handleReply(comment.id, comment.author.username)}
                />

                {/* Replies */}
                {comment.replies && comment.replies.length > 0 && (
                  <View style={styles.repliesContainer}>
                    {comment.replies.map((reply) => (
                      <CommentCard
                        key={reply.id}
                        id={reply.id}
                        author={{
                          id: reply.author.id,
                          displayName: reply.author.username,
                          avatarUrl: reply.author.avatar_url,
                        }}
                        content={reply.content}
                        createdAt={reply.created_at}
                        likesCount={reply.likes}
                        isLiked={reply.is_liked}
                        onLikePress={() => handleLikeComment(reply.id)}
                        isReply
                      />
                    ))}
                  </View>
                )}
              </View>
            ))}

            {comments.length === 0 && (
              <View style={styles.noComments}>
                <Ionicons name="chatbubbles-outline" size={48} color={colors.textMuted} />
                <Text style={styles.noCommentsText}>Henüz yorum yok. İlk yorumu sen yap!</Text>
              </View>
            )}
          </View>
        </ScrollView>

        {/* Comment Input */}
        <View style={styles.commentInputContainer}>
          {replyingTo && (
            <View style={styles.replyingToBar}>
              <Text style={styles.replyingToText}>@{replyingTo.username} yanıtlanıyor</Text>
              <TouchableOpacity onPress={() => {
                setReplyingTo(null);
                setNewComment("");
              }}>
                <Ionicons name="close" size={18} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>
          )}
          <View style={styles.inputRow}>
            <TextInput
              style={styles.commentInput}
              placeholder="Yorum yaz..."
              placeholderTextColor={colors.textMuted}
              value={newComment}
              onChangeText={setNewComment}
              multiline
              maxLength={500}
            />
            <TouchableOpacity
              style={[styles.sendButton, !newComment.trim() && styles.sendButtonDisabled]}
              onPress={handleSubmitComment}
              disabled={!newComment.trim() || submitting}
            >
              {submitting ? (
                <ActivityIndicator size="small" color={colors.textPrimary} />
              ) : (
                <Ionicons name="send" size={20} color={colors.textPrimary} />
              )}
            </TouchableOpacity>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  flex: {
    flex: 1,
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
  communityLink: {
    flexDirection: "row",
    alignItems: "center",
  },
  communityName: {
    ...typography.body,
    color: colors.accentBlue,
    fontWeight: "600",
  },
  scrollContent: {
    paddingBottom: spacing.xl,
  },
  postContainer: {
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderDefault,
  },
  authorRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.surfaceGlass,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.sm,
  },
  avatarImage: {
    width: 48,
    height: 48,
    borderRadius: 24,
  },
  authorInfo: {
    flex: 1,
  },
  authorNameRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  authorName: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: "600",
  },
  authorBadge: {
    backgroundColor: colors.accentBlue + "30",
    paddingHorizontal: spacing.xs,
    paddingVertical: 2,
    borderRadius: radius.xs,
  },
  authorBadgeText: {
    ...typography.caption,
    color: colors.accentBlue,
    fontWeight: "600",
  },
  postDate: {
    ...typography.caption,
    color: colors.textMuted,
    marginTop: 2,
  },
  postTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  postContent: {
    ...typography.body,
    color: colors.textSecondary,
    lineHeight: 24,
  },
  postImage: {
    width: "100%",
    height: 200,
    borderRadius: radius.md,
    marginTop: spacing.md,
  },
  tagsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.xs,
    marginTop: spacing.md,
  },
  tag: {
    backgroundColor: colors.surfaceGlass,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
  },
  tagText: {
    ...typography.caption,
    color: colors.accentBlue,
  },
  actionsRow: {
    flexDirection: "row",
    marginTop: spacing.lg,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.borderDefault,
  },
  actionButton: {
    flexDirection: "row",
    alignItems: "center",
    marginRight: spacing.xl,
    gap: spacing.xs,
  },
  actionText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  actionTextActive: {
    color: colors.errorRed,
  },
  commentsSection: {
    padding: spacing.md,
  },
  commentsTitle: {
    ...typography.h4,
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  repliesContainer: {
    marginLeft: spacing.xl,
    borderLeftWidth: 2,
    borderLeftColor: colors.borderDefault,
    paddingLeft: spacing.sm,
  },
  noComments: {
    alignItems: "center",
    paddingVertical: spacing.xl,
  },
  noCommentsText: {
    ...typography.body,
    color: colors.textMuted,
    marginTop: spacing.sm,
    textAlign: "center",
  },
  commentInputContainer: {
    backgroundColor: colors.bgPrimary,
    borderTopWidth: 1,
    borderTopColor: colors.borderDefault,
    padding: spacing.md,
  },
  replyingToBar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: colors.surfaceGlass,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.sm,
    marginBottom: spacing.sm,
  },
  replyingToText: {
    ...typography.caption,
    color: colors.accentBlue,
  },
  inputRow: {
    flexDirection: "row",
    alignItems: "flex-end",
    gap: spacing.sm,
  },
  commentInput: {
    flex: 1,
    backgroundColor: colors.surfaceGlass,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    ...typography.body,
    color: colors.textPrimary,
    maxHeight: 100,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: radius.full,
    backgroundColor: colors.accentBlue,
    justifyContent: "center",
    alignItems: "center",
  },
  sendButtonDisabled: {
    backgroundColor: colors.surfaceGlass,
  },
});
