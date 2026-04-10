import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import { colors, spacing, radius } from "../../theme";
import { apiRequest } from "../../utils/api";

type LeaderboardEntry = {
  rank: number;
  user_id: string;
  points: number;
  level: number;
  streak: number;
};

type Category = "total" | "routes" | "reports" | "community";

const CATEGORIES: { key: Category; label: string }[] = [
  { key: "total", label: "Genel" },
  { key: "routes", label: "Rotalar" },
  { key: "reports", label: "Raporlar" },
  { key: "community", label: "Topluluk" },
];

const RANK_MEDALS = ["\uD83E\uDD47", "\uD83E\uDD48", "\uD83E\uDD49"];

export default function LeaderboardScreen() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState<Category>("total");

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiRequest<LeaderboardEntry[]>(
        `/api/gamification/leaderboard?category=${category}&limit=50`,
      );
      setEntries(data);
    } catch {
      setEntries([]);
    }
    setLoading(false);
  }, [category]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <View style={styles.container}>
      <ScreenHeader title="Lider Tablosu" />
      <View style={styles.tabs}>
        {CATEGORIES.map((c) => (
          <TouchableOpacity
            key={c.key}
            style={[styles.tab, category === c.key && styles.tabActive]}
            onPress={() => setCategory(c.key)}
          >
            <Text style={[styles.tabText, category === c.key && styles.tabTextActive]}>
              {c.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      {loading ? (
        <ActivityIndicator size="large" color={colors.accentBlue} style={styles.loader} />
      ) : (
        <FlatList
          data={entries}
          keyExtractor={(e) => `${e.rank}-${e.user_id}`}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <GlassCard style={[styles.row, item.rank <= 3 && styles.rowTop]}>
              <View style={styles.rankCol}>
                <Text style={styles.rank}>
                  {item.rank <= 3 ? RANK_MEDALS[item.rank - 1] : `#${item.rank}`}
                </Text>
              </View>
              <View style={styles.infoCol}>
                <Text style={styles.userId} numberOfLines={1}>
                  {item.user_id.slice(0, 8)}...
                </Text>
                <Text style={styles.level}>Lv.{item.level}</Text>
              </View>
              <View style={styles.pointsCol}>
                <Text style={styles.points}>{item.points.toLocaleString()}</Text>
                <Text style={styles.streak}>{"\uD83D\uDD25"}{item.streak}g</Text>
              </View>
            </GlassCard>
          )}
          ListEmptyComponent={
            <Text style={styles.empty}>Henuz veri yok</Text>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  tabs: { flexDirection: "row", paddingHorizontal: spacing.md, marginBottom: spacing.sm, gap: spacing.xs },
  tab: { paddingHorizontal: spacing.md, paddingVertical: spacing.xs, borderRadius: radius.pill, backgroundColor: colors.surfaceGlass },
  tabActive: { backgroundColor: colors.accentBlue },
  tabText: { fontSize: 13, color: colors.textSecondary },
  tabTextActive: { color: colors.textPrimary, fontWeight: "600" },
  loader: { marginTop: spacing.xl },
  list: { padding: spacing.md, paddingBottom: 100 },
  row: { flexDirection: "row", alignItems: "center", padding: spacing.md, marginBottom: spacing.xs },
  rowTop: { borderWidth: 1, borderColor: colors.accentBlueGlow },
  rankCol: { width: 40, alignItems: "center" },
  rank: { fontSize: 18, fontWeight: "700", color: colors.textPrimary },
  infoCol: { flex: 1, marginLeft: spacing.sm },
  userId: { fontSize: 14, fontWeight: "600", color: colors.textPrimary },
  level: { fontSize: 11, color: colors.textTertiary, marginTop: 2 },
  pointsCol: { alignItems: "flex-end" },
  points: { fontSize: 16, fontWeight: "700", color: colors.accentBlue },
  streak: { fontSize: 11, color: colors.textTertiary, marginTop: 2 },
  empty: { fontSize: 14, color: colors.textSecondary, textAlign: "center", marginTop: spacing.xl },
});
