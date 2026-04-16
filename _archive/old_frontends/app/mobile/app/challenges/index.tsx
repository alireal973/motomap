// app/mobile/app/challenges/index.tsx
import { useState, useEffect, useCallback } from "react";
import {
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import ChallengeCard from "../../components/ChallengeCard";
import EmptyState from "../../components/EmptyState";
import LoadingScreen from "../../components/LoadingScreen";
import { colors, spacing, radius } from "../../theme";
import { useAuth } from "../../context/AuthContext";
import { apiRequest } from "../../utils/api";

type ChallengeStatus = "active" | "completed" | "expired" | "upcoming";

type Challenge = {
  id: string;
  title: string;
  description: string;
  icon_name: string;
  progress: number;
  target: number;
  unit: string;
  status: ChallengeStatus;
  rewards: Array<{ type: "xp" | "badge" | "title"; value: number | string }>;
  deadline?: string;
  category: string;
};

type TabKey = "active" | "completed" | "all";

const TABS: Array<{ key: TabKey; label: string }> = [
  { key: "active", label: "Aktif" },
  { key: "completed", label: "Tamamlanan" },
  { key: "all", label: "Tümü" },
];

export default function ChallengesScreen() {
  const { token, isAuthenticated } = useAuth();
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<TabKey>("active");

  const fetchChallenges = useCallback(async () => {
    if (!token) return;
    try {
      const response = await apiRequest("/api/challenges", { token });
      const data = response as { challenges?: Challenge[] };
      setChallenges(data.challenges || []);
    } catch {
      // Handle error silently
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchChallenges();
    } else {
      setIsLoading(false);
    }
  }, [isAuthenticated, fetchChallenges]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    fetchChallenges();
  };

  const handleClaimReward = async (challengeId: string) => {
    if (!token) return;
    try {
      await apiRequest(`/api/challenges/${challengeId}/claim`, {
        method: "POST",
        token,
      });
      // Refresh challenges after claiming
      fetchChallenges();
    } catch {
      // Handle error
    }
  };

  const filteredChallenges = challenges.filter((c) => {
    if (activeTab === "active") return c.status === "active" || c.status === "upcoming";
    if (activeTab === "completed") return c.status === "completed";
    return true;
  });

  const stats = {
    active: challenges.filter((c) => c.status === "active").length,
    completed: challenges.filter((c) => c.status === "completed").length,
    totalXp: challenges
      .filter((c) => c.status === "completed")
      .reduce((sum, c) => {
        const xpReward = c.rewards.find((r) => r.type === "xp");
        return sum + (typeof xpReward?.value === "number" ? xpReward.value : 0);
      }, 0),
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return (
      <View style={styles.container}>
        <ScreenHeader title="Görevler" />
        <EmptyState
          icon="🔐"
          title="Giriş Yapın"
          description="Görevlere katılmak için giriş yapmanız gerekiyor."
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScreenHeader title="Görevler" />

      {/* Stats */}
      <GlassCard style={styles.statsCard}>
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{stats.active}</Text>
            <Text style={styles.statLabel}>Aktif</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{stats.completed}</Text>
            <Text style={styles.statLabel}>Tamamlanan</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: colors.warning }]}>
              {stats.totalXp}
            </Text>
            <Text style={styles.statLabel}>Kazanılan XP</Text>
          </View>
        </View>
      </GlassCard>

      {/* Tabs */}
      <View style={styles.tabs}>
        {TABS.map((tab) => (
          <TouchableOpacity
            key={tab.key}
            style={[styles.tab, activeTab === tab.key && styles.tabActive]}
            onPress={() => setActiveTab(tab.key)}
          >
            <Text
              style={[styles.tabText, activeTab === tab.key && styles.tabTextActive]}
            >
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Challenges List */}
      <FlatList
        data={filteredChallenges}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <ChallengeCard
            id={item.id}
            title={item.title}
            description={item.description}
            iconName={item.icon_name as any}
            progress={item.progress}
            target={item.target}
            unit={item.unit}
            status={item.status}
            rewards={item.rewards}
            deadline={item.deadline}
            onClaimPress={
              item.status === "completed" ? () => handleClaimReward(item.id) : undefined
            }
          />
        )}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            tintColor={colors.accentBlue}
          />
        }
        ListEmptyComponent={
          <EmptyState
            icon="🏁"
            title="Görev Bulunamadı"
            description={
              activeTab === "completed"
                ? "Henüz tamamlanmış göreviniz yok."
                : "Şu an aktif görev bulunmuyor."
            }
          />
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  statsCard: {
    margin: spacing.md,
    padding: spacing.lg,
  },
  statsRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
  },
  statItem: {
    alignItems: "center",
    flex: 1,
  },
  statValue: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  statLabel: {
    fontSize: 12,
    color: colors.textTertiary,
    marginTop: spacing.xs,
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: colors.surfaceBorder,
  },
  tabs: {
    flexDirection: "row",
    marginHorizontal: spacing.md,
    marginBottom: spacing.md,
    backgroundColor: colors.surfaceGlass,
    borderRadius: radius.md,
    padding: spacing.xs,
  },
  tab: {
    flex: 1,
    paddingVertical: spacing.sm,
    alignItems: "center",
    borderRadius: radius.sm,
  },
  tabActive: {
    backgroundColor: colors.accentBlue,
  },
  tabText: {
    fontSize: 14,
    fontWeight: "600",
    color: colors.textSecondary,
  },
  tabTextActive: {
    color: "#FFFFFF",
  },
  listContent: {
    padding: spacing.md,
    paddingTop: 0,
  },
});
