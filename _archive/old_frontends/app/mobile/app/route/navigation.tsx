import React, { useState, useEffect, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Dimensions,
  Alert,
  Vibration,
} from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import MapView, { Polyline, Marker, PROVIDER_GOOGLE } from "react-native-maps";
import * as Location from "expo-location";
import { colors, spacing, radius, typography, shadows } from "../../theme";
import GlassCard from "../../components/GlassCard";

const { width, height } = Dimensions.get("window");

interface NavigationStep {
  instruction: string;
  distance_m: number;
  maneuver: "straight" | "turn-left" | "turn-right" | "u-turn" | "arrive";
  coordinates: { latitude: number; longitude: number };
}

interface RoutePoint {
  latitude: number;
  longitude: number;
}

const MANEUVER_ICONS: Record<string, string> = {
  straight: "arrow-up",
  "turn-left": "arrow-back",
  "turn-right": "arrow-forward",
  "u-turn": "return-down-back",
  arrive: "flag",
};

export default function NavigationScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const mapRef = useRef<MapView>(null);
  
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [heading, setHeading] = useState(0);
  const [routePoints, setRoutePoints] = useState<RoutePoint[]>([]);
  const [steps, setSteps] = useState<NavigationStep[]>([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [distanceToNext, setDistanceToNext] = useState(0);
  const [totalDistanceRemaining, setTotalDistanceRemaining] = useState(0);
  const [etaMinutes, setEtaMinutes] = useState(0);
  const [isNavigating, setIsNavigating] = useState(true);
  const [speedKmh, setSpeedKmh] = useState(0);
  const [followUser, setFollowUser] = useState(true);

  useEffect(() => {
    initializeNavigation();
    return () => {
      // Cleanup location subscription
    };
  }, []);

  const initializeNavigation = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== "granted") {
      Alert.alert("Konum İzni", "Navigasyon için konum izni gerekli", [
        { text: "Tamam", onPress: () => router.back() },
      ]);
      return;
    }

    // Mock route data - in production, fetch from API
    const mockRoute: RoutePoint[] = [
      { latitude: 41.0370, longitude: 40.5178 },
      { latitude: 41.0250, longitude: 40.4800 },
      { latitude: 41.0050, longitude: 40.4400 },
      { latitude: 40.9900, longitude: 40.2300 },
      { latitude: 41.0015, longitude: 39.7178 },
    ];

    const mockSteps: NavigationStep[] = [
      { instruction: "Rize'den çıkış yap, batıya doğru devam et", distance_m: 5000, maneuver: "straight", coordinates: mockRoute[0] },
      { instruction: "Araklı kavşağında sola dön", distance_m: 8000, maneuver: "turn-left", coordinates: mockRoute[1] },
      { instruction: "D010 karayolunu takip et", distance_m: 25000, maneuver: "straight", coordinates: mockRoute[2] },
      { instruction: "Sürmene'den geç", distance_m: 45000, maneuver: "straight", coordinates: mockRoute[3] },
      { instruction: "Hedefe vardınız: Trabzon", distance_m: 0, maneuver: "arrive", coordinates: mockRoute[4] },
    ];

    setRoutePoints(mockRoute);
    setSteps(mockSteps);
    setTotalDistanceRemaining(156500);
    setEtaMinutes(210);
    setDistanceToNext(5000);

    // Start location tracking
    const locationSub = await Location.watchPositionAsync(
      {
        accuracy: Location.Accuracy.BestForNavigation,
        distanceInterval: 10,
        timeInterval: 1000,
      },
      (location) => {
        const { latitude, longitude, speed, heading: h } = location.coords;
        setUserLocation({ latitude, longitude });
        if (h) setHeading(h);
        if (speed) setSpeedKmh(Math.round((speed * 3.6) || 0));

        if (followUser && mapRef.current) {
          mapRef.current.animateCamera({
            center: { latitude, longitude },
            heading: h || 0,
            pitch: 45,
            zoom: 17,
          });
        }

        // Check if approaching next step
        updateNavigationProgress(latitude, longitude);
      }
    );

    return () => locationSub.remove();
  };

  const updateNavigationProgress = (lat: number, lng: number) => {
    if (steps.length === 0 || currentStepIndex >= steps.length) return;

    const nextStep = steps[currentStepIndex];
    const distance = calculateDistance(lat, lng, nextStep.coordinates.latitude, nextStep.coordinates.longitude);

    setDistanceToNext(Math.round(distance));

    // If within 50m of next step, advance
    if (distance < 50 && currentStepIndex < steps.length - 1) {
      Vibration.vibrate(200);
      setCurrentStepIndex((prev) => prev + 1);
    }

    // Check if arrived
    if (currentStepIndex === steps.length - 1 && distance < 50) {
      handleArrival();
    }
  };

  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371000; // Earth radius in meters
    const dLat = (lat2 - lat1) * (Math.PI / 180);
    const dLon = (lon2 - lon1) * (Math.PI / 180);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * (Math.PI / 180)) *
        Math.cos(lat2 * (Math.PI / 180)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  const handleArrival = () => {
    setIsNavigating(false);
    Alert.alert(
      "Hedefe Vardınız! 🎉",
      "Sürüşünüz tamamlandı. İyi yolculuklar!",
      [
        { text: "Rotayı Değerlendir", onPress: () => router.push(`/route/${id}?review=true` as any) },
        { text: "Kapat", onPress: () => router.back() },
      ]
    );
  };

  const handleExitNavigation = () => {
    Alert.alert(
      "Navigasyondan Çık",
      "Navigasyonu sonlandırmak istediğinizden emin misiniz?",
      [
        { text: "İptal", style: "cancel" },
        { text: "Çık", style: "destructive", onPress: () => router.back() },
      ]
    );
  };

  const formatDistance = (meters: number): string => {
    if (meters >= 1000) {
      return `${(meters / 1000).toFixed(1)} km`;
    }
    return `${meters} m`;
  };

  const formatETA = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}s ${mins}dk` : `${mins}dk`;
  };

  const currentStep = steps[currentStepIndex];
  const nextStep = steps[currentStepIndex + 1];

  return (
    <View style={styles.container}>
      {/* Full Screen Map */}
      <MapView
        ref={mapRef}
        style={styles.map}
        provider={PROVIDER_GOOGLE}
        initialRegion={{
          latitude: routePoints[0]?.latitude || 41.0,
          longitude: routePoints[0]?.longitude || 40.0,
          latitudeDelta: 0.05,
          longitudeDelta: 0.05,
        }}
        showsUserLocation={false}
        showsCompass={false}
        rotateEnabled={true}
        pitchEnabled={true}
      >
        {/* Route Line */}
        <Polyline
          coordinates={routePoints}
          strokeColor={colors.accentBlue}
          strokeWidth={6}
        />

        {/* Remaining route (lighter) */}
        {currentStepIndex > 0 && (
          <Polyline
            coordinates={routePoints.slice(0, currentStepIndex + 1)}
            strokeColor="rgba(61, 139, 255, 0.3)"
            strokeWidth={6}
          />
        )}

        {/* User Location Marker */}
        {userLocation && (
          <Marker coordinate={userLocation} anchor={{ x: 0.5, y: 0.5 }}>
            <View style={styles.userMarkerContainer}>
              <View style={[styles.userMarker, { transform: [{ rotate: `${heading}deg` }] }]}>
                <View style={styles.userMarkerArrow} />
              </View>
              <View style={styles.userMarkerPulse} />
            </View>
          </Marker>
        )}

        {/* Destination Marker */}
        {routePoints.length > 0 && (
          <Marker coordinate={routePoints[routePoints.length - 1]}>
            <View style={styles.destinationMarker}>
              <Ionicons name="flag" size={24} color={colors.textPrimary} />
            </View>
          </Marker>
        )}
      </MapView>

      {/* Top Navigation Card */}
      <SafeAreaView style={styles.topOverlay} edges={["top"]}>
        <GlassCard style={styles.navigationCard}>
          {currentStep && (
            <>
              <View style={styles.maneuverRow}>
                <View style={styles.maneuverIcon}>
                  <Ionicons
                    name={MANEUVER_ICONS[currentStep.maneuver] as any}
                    size={36}
                    color={colors.textPrimary}
                  />
                </View>
                <View style={styles.maneuverInfo}>
                  <Text style={styles.distanceText}>{formatDistance(distanceToNext)}</Text>
                  <Text style={styles.instructionText} numberOfLines={2}>
                    {currentStep.instruction}
                  </Text>
                </View>
              </View>

              {nextStep && (
                <View style={styles.nextStepRow}>
                  <Text style={styles.nextStepLabel}>Sonra:</Text>
                  <Ionicons
                    name={MANEUVER_ICONS[nextStep.maneuver] as any}
                    size={16}
                    color={colors.textSecondary}
                  />
                  <Text style={styles.nextStepText} numberOfLines={1}>
                    {nextStep.instruction}
                  </Text>
                </View>
              )}
            </>
          )}
        </GlassCard>
      </SafeAreaView>

      {/* Speed Indicator */}
      <View style={styles.speedContainer}>
        <GlassCard style={styles.speedCard}>
          <Text style={styles.speedValue}>{speedKmh}</Text>
          <Text style={styles.speedUnit}>km/s</Text>
        </GlassCard>
      </View>

      {/* Bottom Info Bar */}
      <SafeAreaView style={styles.bottomOverlay} edges={["bottom"]}>
        <GlassCard style={styles.bottomCard}>
          <View style={styles.bottomStats}>
            <View style={styles.bottomStat}>
              <Ionicons name="navigate-outline" size={20} color={colors.accentBlue} />
              <Text style={styles.bottomStatValue}>{formatDistance(totalDistanceRemaining)}</Text>
              <Text style={styles.bottomStatLabel}>kalan</Text>
            </View>
            <View style={styles.bottomStatDivider} />
            <View style={styles.bottomStat}>
              <Ionicons name="time-outline" size={20} color={colors.accentBlue} />
              <Text style={styles.bottomStatValue}>{formatETA(etaMinutes)}</Text>
              <Text style={styles.bottomStatLabel}>varış</Text>
            </View>
          </View>

          <View style={styles.bottomActions}>
            <TouchableOpacity
              style={[styles.actionButton, followUser && styles.actionButtonActive]}
              onPress={() => setFollowUser(!followUser)}
            >
              <Ionicons
                name={followUser ? "locate" : "locate-outline"}
                size={24}
                color={followUser ? colors.accentBlue : colors.textSecondary}
              />
            </TouchableOpacity>

            <TouchableOpacity style={styles.exitButton} onPress={handleExitNavigation}>
              <Ionicons name="close" size={24} color={colors.textPrimary} />
              <Text style={styles.exitButtonText}>Çık</Text>
            </TouchableOpacity>
          </View>
        </GlassCard>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  map: {
    ...StyleSheet.absoluteFillObject,
  },
  topOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    paddingHorizontal: spacing.md,
  },
  navigationCard: {
    padding: spacing.md,
    backgroundColor: "rgba(8, 28, 80, 0.95)",
  },
  maneuverRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  maneuverIcon: {
    width: 64,
    height: 64,
    borderRadius: radius.md,
    backgroundColor: colors.accentBlue,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.md,
  },
  maneuverInfo: {
    flex: 1,
  },
  distanceText: {
    ...typography.h2,
    color: colors.textPrimary,
    fontWeight: "700",
  },
  instructionText: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  nextStepRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: spacing.md,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.borderDefault,
    gap: spacing.xs,
  },
  nextStepLabel: {
    ...typography.caption,
    color: colors.textMuted,
  },
  nextStepText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    flex: 1,
  },
  speedContainer: {
    position: "absolute",
    left: spacing.md,
    top: "50%",
    marginTop: -40,
  },
  speedCard: {
    width: 80,
    height: 80,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "rgba(8, 28, 80, 0.9)",
  },
  speedValue: {
    ...typography.h1,
    color: colors.textPrimary,
    fontWeight: "700",
  },
  speedUnit: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  userMarkerContainer: {
    alignItems: "center",
    justifyContent: "center",
  },
  userMarker: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.accentBlue,
    justifyContent: "center",
    alignItems: "center",
    borderWidth: 3,
    borderColor: colors.textPrimary,
    ...shadows.lg,
  },
  userMarkerArrow: {
    width: 0,
    height: 0,
    borderLeftWidth: 8,
    borderRightWidth: 8,
    borderBottomWidth: 16,
    borderLeftColor: "transparent",
    borderRightColor: "transparent",
    borderBottomColor: colors.textPrimary,
    marginTop: -4,
  },
  userMarkerPulse: {
    position: "absolute",
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: "rgba(61, 139, 255, 0.2)",
  },
  destinationMarker: {
    backgroundColor: "#4CAF50",
    padding: spacing.sm,
    borderRadius: radius.full,
    borderWidth: 3,
    borderColor: colors.textPrimary,
  },
  bottomOverlay: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.md,
  },
  bottomCard: {
    padding: spacing.md,
    backgroundColor: "rgba(8, 28, 80, 0.95)",
  },
  bottomStats: {
    flexDirection: "row",
    justifyContent: "center",
    marginBottom: spacing.md,
  },
  bottomStat: {
    alignItems: "center",
    paddingHorizontal: spacing.xl,
  },
  bottomStatValue: {
    ...typography.h3,
    color: colors.textPrimary,
    marginTop: spacing.xs,
  },
  bottomStatLabel: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  bottomStatDivider: {
    width: 1,
    height: "100%",
    backgroundColor: colors.borderDefault,
  },
  bottomActions: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  actionButton: {
    width: 48,
    height: 48,
    borderRadius: radius.full,
    backgroundColor: colors.surfaceGlass,
    justifyContent: "center",
    alignItems: "center",
  },
  actionButtonActive: {
    backgroundColor: "rgba(61, 139, 255, 0.2)",
  },
  exitButton: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.errorRed,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: radius.md,
    gap: spacing.xs,
  },
  exitButtonText: {
    ...typography.button,
    color: colors.textPrimary,
  },
});
