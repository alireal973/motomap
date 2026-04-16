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
import { router } from "expo-router";
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
  brand_name: string | null;
  region_city: string | null;
  is_official: boolean;
};

const TYPE_ICONS: Record<string, string> = {
  brand: "\uD83C\uDFCD\uFE0F",
  style: "\uD83C\uDFC1",
  region: "\uD83D\uDCCD",
  interest: "\u2B50",
  event: "\uD83D\uDCC5",
};

const TYPE_LABELS: Record<string, string> = {
  brand: "Marka",
  style: "Stil",
  region: "Bolge",
  interest: "Ilgi",
  event: "Etkinlik",
};

type FilterKey = "all" | "brand" | "style" | "region" | "interest";

export default function CommunitiesScreen() {
  const { token } = useAuth();
  const [communities, setCommunities] = useState<Community[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<FilterKey>("all");

  const fetchCommunities = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filter !== "all") params.set("type", filter);
      if (search.trim()) params.set("search", search.trim());
      const qs = params.toString();
      const data = await apiRequest<Community[]>(`/api/communities${qs ? `?${qs}` : ""}`);
      setCommunities(data);
    } catch {
      setCommunities([]);
    } finally {
      setLoading(false);
    }
  }, [filter, search]);

  useEffect(() => {
    fetchCommunities();
  }, [fetchCommunities]);

  const handleJoin = async (slug: string) => {
    if (!token) {
      router.push("/auth/login" as never);
      return;
    }
    try {
      await apiRequest(`/api/communities/${slug}/join`, { method: "POST", token });
      fetchCommunities();
    } catch {}
  };

  const renderItem = ({ item }: { item: Community }) => (
    <GlassCard style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardIcon}>{TYPE_ICONS[item.type] || "\uD83D\uDCAC"}</Text>
        <View style={styles.cardInfo}>
          <View style={styles.nameRow}>
            <Text style={styles.cardName} numberOfLines={1}>{item.name}</Text>
            {item.is_official && <Text style={styles.officialBadge}>Resmi</Text>}
          </View>
          <Text style={styles.cardType}>{TYPE_LABELS[item.type] || item.type}</Text>
        </View>
      </View>
      {item.description && (
        <Text style={styles.cardDesc} numberOfLines={2}>{item.description}</Text>
      )}
      <View style={styles.cardFooter}>
        <Text style={styles.stat}>{item.member_count} uye</Text>
        <Text style={styles.stat}>{item.post_count} gonderi</Text>
        <TouchableOpacity style={styles.joinBtn} onPress={() => handleJoin(item.slug)}>
          <Text style={styles.joinText}>Katil</Text>
        </TouchableOpacity>
      </View>
    </GlassCard>
  );

  const FILTERS: { key: FilterKey; label: string }[] = [
    { key: "all", label: "Tumu" },
    { key: "brand", label: "Marka" },
    { key: "style", label: "Stil" },
    { key: "region", label: "Bolge" },
    { key: "interest", label: "Ilgi" },
  ];

  return (
    <View style={styles.container}>
      <ScreenHeader title="Topluluklar" />
      <TextInput
        style={styles.search}
        placeholder="Topluluk ara..."
        placeholderTextColor={colors.textTertiary}
        value={search}
        onChangeText={setSearch}
      />
      <View style={styles.filters}>
        {FILTERS.map((f) => (
          <TouchableOpacity
            key={f.key}
            style={[styles.filterBtn, filter === f.key && styles.filterActive]}
            onPress={() => setFilter(f.key)}
          >
            <Text style={[styles.filterText, filter === f.key && styles.filterTextActive]}>
              {f.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      {loading ? (
        <ActivityIndicator size="large" color={colors.accentBlue} style={styles.loader} />
      ) : (
        <FlatList
          data={communities}
          keyExtractor={(c) => c.id}
          renderItem={renderItem}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            <Text style={styles.empty}>Topluluk bulunamadi</Text>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  search: {
    backgroundColor: colors.surfaceGlass, borderWidth: 1,
    borderColor: colors.surfaceBorder, borderRadius: radius.md,
    marginHorizontal: spacing.md, padding: spacing.md,
    fontSize: 15, color: colors.textPrimary,
  },
  filters: { flexDirection: "row", paddingHorizontal: spacing.md, marginVertical: spacing.sm, gap: spacing.xs },
  filterBtn: { paddingHorizontal: spacing.md, paddingVertical: spacing.xs, borderRadius: radius.pill, backgroundColor: colors.surfaceGlass },
  filterActive: { backgroundColor: colors.accentBlue },
  filterText: { fontSize: 12, color: colors.textSecondary },
  filterTextActive: { color: colors.textPrimary, fontWeight: "600" },
  loader: { marginTop: spacing.xl },
  list: { padding: spacing.md, paddingBottom: 100 },
  card: { marginBottom: spacing.md, padding: spacing.md },
  cardHeader: { flexDirection: "row", alignItems: "center", marginBottom: spacing.sm },
  cardIcon: { fontSize: 32, marginRight: spacing.md },
  cardInfo: { flex: 1 },
  nameRow: { flexDirection: "row", alignItems: "center", gap: spacing.xs },
  cardName: { fontSize: 16, fontWeight: "700", color: colors.textPrimary, flex: 1 },
  officialBadge: { fontSize: 10, fontWeight: "700", color: colors.accentBlue, backgroundColor: colors.accentBlueGlow, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4, overflow: "hidden" },
  cardType: { fontSize: 12, color: colors.textTertiary, marginTop: 2 },
  cardDesc: { fontSize: 13, color: colors.textSecondary, marginBottom: spacing.sm },
  cardFooter: { flexDirection: "row", alignItems: "center" },
  stat: { fontSize: 12, color: colors.textTertiary, marginRight: spacing.md },
  joinBtn: { marginLeft: "auto", backgroundColor: colors.accentBlue, paddingHorizontal: spacing.md, paddingVertical: spacing.xs, borderRadius: radius.pill },
  joinText: { fontSize: 12, fontWeight: "700", color: colors.textPrimary },
  empty: { fontSize: 14, color: colors.textSecondary, textAlign: "center", marginTop: spacing.xl },
});
