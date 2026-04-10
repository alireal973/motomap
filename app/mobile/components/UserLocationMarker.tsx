// app/mobile/components/UserLocationMarker.tsx
import { useEffect, useRef } from "react";
import { StyleSheet, View, Animated, Easing } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../theme";

type UserLocationMarkerProps = {
  heading?: number; // Device heading in degrees (0-360)
  accuracy?: number; // GPS accuracy in meters
  isMoving?: boolean;
};

export default function UserLocationMarker({
  heading,
  accuracy = 10,
  isMoving = false,
}: UserLocationMarkerProps) {
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const opacityAnim = useRef(new Animated.Value(0.6)).current;

  useEffect(() => {
    // Pulse animation for the outer ring
    const pulseAnimation = Animated.loop(
      Animated.sequence([
        Animated.parallel([
          Animated.timing(pulseAnim, {
            toValue: 1.8,
            duration: 1500,
            easing: Easing.out(Easing.ease),
            useNativeDriver: true,
          }),
          Animated.timing(opacityAnim, {
            toValue: 0,
            duration: 1500,
            easing: Easing.out(Easing.ease),
            useNativeDriver: true,
          }),
        ]),
        Animated.parallel([
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 0,
            useNativeDriver: true,
          }),
          Animated.timing(opacityAnim, {
            toValue: 0.6,
            duration: 0,
            useNativeDriver: true,
          }),
        ]),
      ])
    );

    pulseAnimation.start();

    return () => pulseAnimation.stop();
  }, []);

  // Calculate accuracy ring size (capped at reasonable values)
  const accuracySize = Math.min(Math.max(accuracy * 2, 40), 120);

  return (
    <View style={styles.container}>
      {/* Accuracy circle */}
      <View
        style={[
          styles.accuracyRing,
          {
            width: accuracySize,
            height: accuracySize,
            borderRadius: accuracySize / 2,
          },
        ]}
      />

      {/* Pulse ring */}
      <Animated.View
        style={[
          styles.pulseRing,
          {
            transform: [{ scale: pulseAnim }],
            opacity: opacityAnim,
          },
        ]}
      />

      {/* Main marker */}
      <View style={styles.markerOuter}>
        <View style={styles.markerInner}>
          {isMoving && (
            <View style={styles.movingIndicator} />
          )}
        </View>
      </View>

      {/* Heading indicator (arrow) */}
      {heading !== undefined && (
        <View
          style={[
            styles.headingContainer,
            { transform: [{ rotate: `${heading}deg` }] },
          ]}
        >
          <View style={styles.headingArrow}>
            <Ionicons name="navigate" size={20} color={colors.accentBlue} />
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: 120,
    height: 120,
    alignItems: "center",
    justifyContent: "center",
  },
  accuracyRing: {
    position: "absolute",
    backgroundColor: "rgba(61, 139, 255, 0.15)",
    borderWidth: 1,
    borderColor: "rgba(61, 139, 255, 0.3)",
  },
  pulseRing: {
    position: "absolute",
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.accentBlue,
  },
  markerOuter: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: "#FFFFFF",
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  markerInner: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: colors.accentBlue,
    alignItems: "center",
    justifyContent: "center",
  },
  movingIndicator: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: "#FFFFFF",
  },
  headingContainer: {
    position: "absolute",
    width: 60,
    height: 60,
    alignItems: "center",
    justifyContent: "flex-start",
  },
  headingArrow: {
    marginTop: -8,
  },
});
