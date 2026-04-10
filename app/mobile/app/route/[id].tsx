import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
  Share,
} from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import MapView, { Polyline, Marker } from "react-native-maps";
import { colors, spacing, radius, typography, shadows } from "../../theme";
import GlassCard from "../../components/GlassCard";
import { useAuth } from "../../context/AuthContext";

const { width } = Dimensions.get("window");

interface RoutePoint {
  latitude: number;
  longitude: number;
}

interface RouteData {
  id: string;
  name: string;
  description: string;
  distance_km: number;
  duration_minutes: number;
  elevation_gain: number;
  difficulty: "easy" | "moderate" | "hard" | "expert";
  rating: number;
  rating_count: number;
  ride_count: number;
  author: {
    id: string;
    username: string;
    avatar_url?: string;
  };
  points: RoutePoint[];
  waypoints: Array<{
    name: string;
    latitude: number;
    longitude: number;
    type: "start" | "end" | "poi" | "rest" | "fuel";
  }>;
  safety_notes: string[];
  tags: string[];
  is_saved: boolean;
  created_at: string;
}

const DIFFICULTY_CONFIG = {
  easy: { label: "Kolay", color: "#4CAF50", icon: "leaf-outline" },
  moderate: { label: "Orta", color: "#FFC107", icon: "fitness-outline" },
  hard: { label: "Zor", color: "#FF9800", icon: "flame-outline" },
  expert: { label: "Uzman", color: "#F44336", icon: "skull-outline" },
};

const WAYPOINT_ICONS: Record<string, string> = {
  start: "flag",
  end: "flag-outline",
  poi: "location",
  rest: "cafe",
  fuel: "car",
};

export default function RouteDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { token } = useAuth();
  const [route, setRoute] = useState<RouteData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<"info" | "safety" | "reviews">("info");

  useEffect(() => {
    fetchRouteDetails();
  }, [id]);

  const fetchRouteDetails = async () => {
    try {
      // TODO: Replace with actual API call
      // const response = await apiRequest(`/routes/${id}`, { token });
      // setRoute(response);
      
      // Mock data for development
      setTimeout(() => {
        setRoute({
          id: id || "1",
          name: "Karadeniz Sahil Yolu",
          description: "Türkiye'nin en güzel sahil rotalarından biri. Rize'den Trabzon'a uzanan bu rota, deniz manzarası ve virajlı yollarıyla ünlüdür.",
          distance_km: 156.5,
          duration_minutes: 210,
          elevation_gain: 1250,
          difficulty: "moderate",
          rating: 4.7,
          rating_count: 234,
          ride_count: 1892,
          author: {
            id: "u1",
            username: "karadenizrider",
          },
          points: [
            { latitude: 41.0370, longitude: 40.5178 },
            { latitude: 41.0050, longitude: 40.4400 },
            { latitude: 40.9900, longitude: 40.2300 },
            { latitude: 41.0015, longitude: 39.7178 },
          ],
          waypoints: [
            { name: "Başlangıç - Rize", latitude: 41.0370, longitude: 40.5178, type: "start" },
            { name: "Araklı Mola", latitude: 41.0050, longitude: 40.4400, type: "rest" },
            { name: "Sürmene Benzinlik", latitude: 40.9900, longitude: 40.2300, type: "fuel" },
            { name: "Bitiş - Trabzon", latitude: 41.0015, longitude: 39.7178, type: "end" },
          ],
          safety_notes: [
            "Virajlarda dikkatli olun, keskin dönüşler var",
            "Yaz aylarında trafik yoğun olabilir",
            "Bazı bölgelerde GSM sinyali zayıf",
            "Yağmurlu havalarda yol kaygan",
          ],
          tags: ["sahil", "manzara", "virajlı", "karadeniz"],
          is_saved: false,
          created_at: "2024-03-15T10:00:00Z",
        });
        setLoading(false);
      }, 500);
    } catch (error) {
      console.error("Error fetching route:", error);
      setLoading(false);
    }
  };

  const handleSaveRoute = async () => {
    if (!route) return;
    setSaving(true);
    try {
      // TODO: API call to save/unsave route
      setRoute({ ...route, is_saved: !route.is_saved });
    } finally {
      setSaving(false);
    }
  };

  const handleShare = async () => {
    if (!route) return;
    try {
      await Share.share({
        title: route.name,
        message: `${route.name} rotasına göz at! MotoMap'te ${route.distance_km} km'lik bu harika rotayı keşfet.`,
      });
    } catch (error) {
      console.error("Share error:", error);
    }
  };

  const handleStartNavigation = () => {
    router.push(`/route/navigation?id=${id}` as any);
  };

  const formatDuration = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}s ${mins}dk` : `${mins}dk`;
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

  if (!route) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle-outline" size={64} color={colors.textSecondary} />
          <Text style={styles.errorText}>Rota bulunamadı</Text>
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Text style={styles.backButtonText}>Geri Dön</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const difficulty = DIFFICULTY_CONFIG[route.difficulty];

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.headerButton}>
          <Ionicons name="arrow-back" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
        <View style={styles.headerActions}>
          <TouchableOpacity onPress={handleShare} style={styles.headerButton}>
            <Ionicons name="share-outline" size={24} color={colors.textPrimary} />
          </TouchableOpacity>
          <TouchableOpacity onPress={handleSaveRoute} style={styles.headerButton} disabled={saving}>
            <Ionicons
              name={route.is_saved ? "bookmark" : "bookmark-outline"}
              size={24}
              color={route.is_saved ? colors.accentBlue : colors.textPrimary}
            />
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView showsVerticalScrollIndicator={false}>
        {/* Map Preview */}
        <View style={styles.mapContainer}>
          <MapView
            style={styles.map}
            initialRegion={{
              latitude: route.points[0]?.latitude || 41.0,
              longitude: route.points[0]?.longitude || 40.0,
              latitudeDelta: 0.5,
              longitudeDelta: 0.5,
            }}
            scrollEnabled={false}
            zoomEnabled={false}
          >
            <Polyline
              coordinates={route.points}
              strokeColor={colors.accentBlue}
              strokeWidth={4}
            />
            {route.waypoints.map((wp, index) => (
              <Marker
                key={index}
                coordinate={{ latitude: wp.latitude, longitude: wp.longitude }}
                title={wp.name}
              >
                <View style={[styles.waypointMarker, wp.type === "start" && styles.startMarker]}>
                  <Ionicons
                    name={WAYPOINT_ICONS[wp.type] as any}
                    size={16}
                    color={colors.textPrimary}
                  />
                </View>
              </Marker>
            ))}
          </MapView>
          <TouchableOpacity
            style={styles.expandMapButton}
            onPress={() => router.push(`/map?route=${id}`)}
          >
            <Ionicons name="expand-outline" size={20} color={colors.textPrimary} />
          </TouchableOpacity>
        </View>

        {/* Route Title & Stats */}
        <View style={styles.content}>
          <Text style={styles.routeName}>{route.name}</Text>
          
          <View style={styles.authorRow}>
            <Text style={styles.authorText}>
              <Ionicons name="person-outline" size={14} color={colors.textSecondary} />{" "}
              {route.author.username}
            </Text>
            <View style={[styles.difficultyBadge, { backgroundColor: difficulty.color + "30" }]}>
              <Ionicons name={difficulty.icon as any} size={14} color={difficulty.color} />
              <Text style={[styles.difficultyText, { color: difficulty.color }]}>
                {difficulty.label}
              </Text>
            </View>
          </View>

          {/* Stats Row */}
          <GlassCard style={styles.statsCard}>
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Ionicons name="navigate-outline" size={24} color={colors.accentBlue} />
                <Text style={styles.statValue}>{route.distance_km} km</Text>
                <Text style={styles.statLabel}>Mesafe</Text>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statItem}>
                <Ionicons name="time-outline" size={24} color={colors.accentBlue} />
                <Text style={styles.statValue}>{formatDuration(route.duration_minutes)}</Text>
                <Text style={styles.statLabel}>Süre</Text>
              </View>
              <View style={styles.statDivider} />
              <View style={styles.statItem}>
                <Ionicons name="trending-up-outline" size={24} color={colors.accentBlue} />
                <Text style={styles.statValue}>{route.elevation_gain}m</Text>
                <Text style={styles.statLabel}>Yükselti</Text>
              </View>
            </View>
          </GlassCard>

          {/* Rating & Rides */}
          <View style={styles.ratingRow}>
            <View style={styles.ratingItem}>
              <Ionicons name="star" size={20} color="#FFD700" />
              <Text style={styles.ratingValue}>{route.rating.toFixed(1)}</Text>
              <Text style={styles.ratingCount}>({route.rating_count})</Text>
            </View>
            <View style={styles.ratingItem}>
              <Ionicons name="bicycle-outline" size={20} color={colors.textSecondary} />
              <Text style={styles.rideCount}>{route.ride_count} sürüş</Text>
            </View>
          </View>

          {/* Tabs */}
          <View style={styles.tabsContainer}>
            {(["info", "safety", "reviews"] as const).map((tab) => (
              <TouchableOpacity
                key={tab}
                style={[styles.tab, activeTab === tab && styles.activeTab]}
                onPress={() => setActiveTab(tab)}
              >
                <Text style={[styles.tabText, activeTab === tab && styles.activeTabText]}>
                  {tab === "info" ? "Bilgi" : tab === "safety" ? "Güvenlik" : "Yorumlar"}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Tab Content */}
          {activeTab === "info" && (
            <View style={styles.tabContent}>
              <Text style={styles.sectionTitle}>Açıklama</Text>
              <Text style={styles.description}>{route.description}</Text>

              <Text style={styles.sectionTitle}>Duraklar</Text>
              {route.waypoints.map((wp, index) => (
                <View key={index} style={styles.waypointRow}>
                  <View style={styles.waypointIcon}>
                    <Ionicons
                      name={WAYPOINT_ICONS[wp.type] as any}
                      size={18}
                      color={colors.accentBlue}
                    />
                  </View>
                  <Text style={styles.waypointName}>{wp.name}</Text>
                </View>
              ))}

              <Text style={styles.sectionTitle}>Etiketler</Text>
              <View style={styles.tagsContainer}>
                {route.tags.map((tag, index) => (
                  <View key={index} style={styles.tag}>
                    <Text style={styles.tagText}>#{tag}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}

          {activeTab === "safety" && (
            <View style={styles.tabContent}>
              <Text style={styles.sectionTitle}>Güvenlik Notları</Text>
              {route.safety_notes.map((note, index) => (
                <View key={index} style={styles.safetyNote}>
                  <Ionicons name="warning-outline" size={18} color="#FFC107" />
                  <Text style={styles.safetyNoteText}>{note}</Text>
                </View>
              ))}
            </View>
          )}

          {activeTab === "reviews" && (
            <View style={styles.tabContent}>
              <Text style={styles.comingSoon}>Yorumlar yakında...</Text>
            </View>
          )}
        </View>
      </ScrollView>

      {/* Bottom Action */}
      <View style={styles.bottomAction}>
        <TouchableOpacity style={styles.startButton} onPress={handleStartNavigation}>
          <Ionicons name="navigate" size={24} color={colors.textPrimary} />
          <Text style={styles.startButtonText}>Navigasyonu Başlat</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
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
  backButton: {
    marginTop: spacing.lg,
    paddingHorizontal: spacing.xl,
    paddingVertical: spacing.sm,
    backgroundColor: colors.accentBlue,
    borderRadius: radius.md,
  },
  backButtonText: {
    ...typography.button,
    color: colors.textPrimary,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  headerButton: {
    padding: spacing.sm,
  },
  headerActions: {
    flexDirection: "row",
    gap: spacing.xs,
  },
  mapContainer: {
    height: 220,
    position: "relative",
  },
  map: {
    flex: 1,
  },
  expandMapButton: {
    position: "absolute",
    top: spacing.sm,
    right: spacing.sm,
    backgroundColor: colors.surfaceGlass,
    padding: spacing.sm,
    borderRadius: radius.sm,
  },
  waypointMarker: {
    backgroundColor: colors.surfaceCard,
    padding: spacing.xs,
    borderRadius: radius.full,
    borderWidth: 2,
    borderColor: colors.accentBlue,
  },
  startMarker: {
    backgroundColor: colors.accentBlue,
  },
  content: {
    padding: spacing.md,
  },
  routeName: {
    ...typography.h2,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  authorRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.md,
  },
  authorText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  difficultyBadge: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: radius.full,
    gap: spacing.xs,
  },
  difficultyText: {
    ...typography.caption,
    fontWeight: "600",
  },
  statsCard: {
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  statsRow: {
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
  },
  statItem: {
    alignItems: "center",
    flex: 1,
  },
  statValue: {
    ...typography.h3,
    color: colors.textPrimary,
    marginTop: spacing.xs,
  },
  statLabel: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: colors.borderDefault,
  },
  ratingRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: spacing.lg,
  },
  ratingItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.xs,
  },
  ratingValue: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: "600",
  },
  ratingCount: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  rideCount: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  tabsContainer: {
    flexDirection: "row",
    backgroundColor: colors.surfaceGlass,
    borderRadius: radius.md,
    padding: spacing.xs,
    marginBottom: spacing.md,
  },
  tab: {
    flex: 1,
    paddingVertical: spacing.sm,
    alignItems: "center",
    borderRadius: radius.sm,
  },
  activeTab: {
    backgroundColor: colors.accentBlue,
  },
  tabText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  activeTabText: {
    color: colors.textPrimary,
    fontWeight: "600",
  },
  tabContent: {
    marginTop: spacing.sm,
  },
  sectionTitle: {
    ...typography.h4,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    marginTop: spacing.md,
  },
  description: {
    ...typography.body,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  waypointRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderDefault,
  },
  waypointIcon: {
    width: 32,
    height: 32,
    borderRadius: radius.full,
    backgroundColor: colors.surfaceGlass,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.sm,
  },
  waypointName: {
    ...typography.body,
    color: colors.textPrimary,
  },
  tagsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: spacing.sm,
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
  safetyNote: {
    flexDirection: "row",
    alignItems: "flex-start",
    backgroundColor: "rgba(255, 193, 7, 0.1)",
    padding: spacing.sm,
    borderRadius: radius.sm,
    marginBottom: spacing.sm,
    gap: spacing.sm,
  },
  safetyNoteText: {
    ...typography.bodySmall,
    color: colors.textPrimary,
    flex: 1,
  },
  comingSoon: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: "center",
    paddingVertical: spacing.xl,
  },
  bottomAction: {
    padding: spacing.md,
    paddingBottom: spacing.lg,
    borderTopWidth: 1,
    borderTopColor: colors.borderDefault,
    backgroundColor: colors.bgPrimary,
  },
  startButton: {
    flexDirection: "row",
    backgroundColor: colors.accentBlue,
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    justifyContent: "center",
    alignItems: "center",
    gap: spacing.sm,
    ...shadows.md,
  },
  startButtonText: {
    ...typography.button,
    color: colors.textPrimary,
  },
});
