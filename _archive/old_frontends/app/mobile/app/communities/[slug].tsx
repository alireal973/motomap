import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import { colors, spacing, radius } from "../../theme";
import { apiRequest } from "../../utils/api";
import { useAuth } from "../../context/AuthContext";

type Community = {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  type: string;
  member_count: number;
  post_count: number;
};

type Post = {
  id: string;
  author_id: string;
  type: string;
  title: string | null;
  content: string;
  like_count: number;
  comment_count: number;
  is_pinned: boolean;
  created_at: string;
};

const POST_ICONS: Record<string, string> = {
  discussion: "\uD83D\uDCAC",
  question: "\u2753",
  help_request: "\uD83C\uDD98",
  help_offer: "\uD83E\uDD1D",
  ride_invite: "\uD83C\uDFCD\uFE0F",
  event: "\uD83D\uDCC5",
  photo: "\uD83D\uDCF8",
  route_share: "\uD83D\uDDFA\uFE0F",
};

export default function CommunityDetailScreen() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
  const { token } = useAuth();
  const [community, setCommunity] = useState<Community | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [newPost, setNewPost] = useState("");
  const [posting, setPosting] = useState(false);

  const fetchData = useCallback(async () => {
    if (!slug) return;
    setLoading(true);
    try {
      const [c, p] = await Promise.all([
        apiRequest<Community>(`/api/communities/${slug}`),
        apiRequest<Post[]>(`/api/communities/${slug}/posts`),
      ]);
      setCommunity(c);
      setPosts(p);
    } catch {}
    setLoading(false);
  }, [slug]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handlePost = async () => {
    if (!newPost.trim() || !token || !slug) return;
    setPosting(true);
    try {
      await apiRequest(`/api/communities/${slug}/posts`, {
        method: "POST",
        token,
        body: { content: newPost.trim(), type: "discussion" },
      });
      setNewPost("");
      fetchData();
    } catch {}
    setPosting(false);
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ScreenHeader title="Topluluk" />
        <ActivityIndicator size="large" color={colors.accentBlue} style={styles.loader} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScreenHeader title={community?.name || "Topluluk"} />
      <FlatList
        data={posts}
        keyExtractor={(p) => p.id}
        contentContainerStyle={styles.list}
        ListHeaderComponent={
          community ? (
            <View style={styles.header}>
              {community.description && (
                <Text style={styles.desc}>{community.description}</Text>
              )}
              <View style={styles.metaRow}>
                <Text style={styles.meta}>{community.member_count} uye</Text>
                <Text style={styles.meta}>{community.post_count} gonderi</Text>
              </View>

              {token && (
                <View style={styles.composer}>
                  <TextInput
                    style={styles.input}
                    placeholder="Bir seyler yazin..."
                    placeholderTextColor={colors.textTertiary}
                    value={newPost}
                    onChangeText={setNewPost}
                    multiline
                    maxLength={5000}
                  />
                  <TouchableOpacity
                    style={[styles.postBtn, (!newPost.trim() || posting) && styles.postBtnDisabled]}
                    onPress={handlePost}
                    disabled={!newPost.trim() || posting}
                  >
                    <Text style={styles.postBtnText}>{posting ? "..." : "Paylas"}</Text>
                  </TouchableOpacity>
                </View>
              )}
            </View>
          ) : null
        }
        renderItem={({ item }) => (
          <GlassCard style={styles.postCard}>
            <View style={styles.postHeader}>
              <Text style={styles.postIcon}>{POST_ICONS[item.type] || "\uD83D\uDCAC"}</Text>
              {item.is_pinned && <Text style={styles.pinBadge}>Sabit</Text>}
              {item.title && <Text style={styles.postTitle} numberOfLines={1}>{item.title}</Text>}
            </View>
            <Text style={styles.postContent} numberOfLines={4}>{item.content}</Text>
            <View style={styles.postFooter}>
              <Text style={styles.postStat}>{"\uD83D\uDC4D"} {item.like_count}</Text>
              <Text style={styles.postStat}>{"\uD83D\uDCAC"} {item.comment_count}</Text>
              <Text style={styles.postTime}>{formatTime(item.created_at)}</Text>
            </View>
          </GlassCard>
        )}
        ListEmptyComponent={
          <Text style={styles.empty}>Henuz gonderi yok. Ilk gonderiyi siz yazin!</Text>
        }
      />
    </View>
  );
}

function formatTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}dk`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}s`;
  return `${Math.floor(hours / 24)}g`;
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  loader: { marginTop: spacing.xl },
  list: { padding: spacing.md, paddingBottom: 100 },
  header: { marginBottom: spacing.md },
  desc: { fontSize: 14, color: colors.textSecondary, marginBottom: spacing.sm },
  metaRow: { flexDirection: "row", gap: spacing.md, marginBottom: spacing.md },
  meta: { fontSize: 13, color: colors.textTertiary },
  composer: { marginBottom: spacing.md },
  input: {
    backgroundColor: colors.surfaceGlass, borderWidth: 1,
    borderColor: colors.surfaceBorder, borderRadius: radius.md,
    padding: spacing.md, fontSize: 14, color: colors.textPrimary,
    minHeight: 60, textAlignVertical: "top", marginBottom: spacing.xs,
  },
  postBtn: { backgroundColor: colors.accentBlue, borderRadius: radius.pill, paddingVertical: spacing.sm, paddingHorizontal: spacing.lg, alignSelf: "flex-end" },
  postBtnDisabled: { opacity: 0.5 },
  postBtnText: { fontSize: 13, fontWeight: "700", color: colors.textPrimary },
  postCard: { marginBottom: spacing.sm, padding: spacing.md },
  postHeader: { flexDirection: "row", alignItems: "center", marginBottom: spacing.xs, gap: spacing.xs },
  postIcon: { fontSize: 18 },
  pinBadge: { fontSize: 10, fontWeight: "700", color: colors.warning, backgroundColor: "rgba(245,158,11,0.15)", paddingHorizontal: 6, paddingVertical: 1, borderRadius: 4, overflow: "hidden" },
  postTitle: { fontSize: 14, fontWeight: "700", color: colors.textPrimary, flex: 1 },
  postContent: { fontSize: 14, color: colors.textSecondary, lineHeight: 20, marginBottom: spacing.sm },
  postFooter: { flexDirection: "row", alignItems: "center" },
  postStat: { fontSize: 12, color: colors.textTertiary, marginRight: spacing.md },
  postTime: { fontSize: 11, color: colors.textTertiary, marginLeft: "auto" },
  empty: { fontSize: 14, color: colors.textSecondary, textAlign: "center", marginTop: spacing.xl },
});
