// app/mobile/components/MapControls.tsx
import { StyleSheet, TouchableOpacity, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";

type MapLayer = "standard" | "satellite" | "terrain";

type MapControlsProps = {
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onLocateMe?: () => void;
  onCompassPress?: () => void;
  compassRotation?: number; // 0-360 degrees
  isLocating?: boolean;
  currentLayer?: MapLayer;
  onLayerChange?: (layer: MapLayer) => void;
  showLayerControl?: boolean;
};

export default function MapControls({
  onZoomIn,
  onZoomOut,
  onLocateMe,
  onCompassPress,
  compassRotation = 0,
  isLocating = false,
  currentLayer = "standard",
  onLayerChange,
  showLayerControl = true,
}: MapControlsProps) {
  const layers: { key: MapLayer; icon: keyof typeof Ionicons.glyphMap; label: string }[] = [
    { key: "standard", icon: "map-outline", label: "Standart" },
    { key: "satellite", icon: "earth-outline", label: "Uydu" },
    { key: "terrain", icon: "trail-sign-outline", label: "Arazi" },
  ];

  return (
    <View style={styles.container}>
      {/* Compass */}
      <TouchableOpacity
        style={styles.controlButton}
        onPress={onCompassPress}
        activeOpacity={0.7}
      >
        <View style={{ transform: [{ rotate: `${-compassRotation}deg` }] }}>
          <Ionicons name="compass-outline" size={24} color={colors.textPrimary} />
        </View>
      </TouchableOpacity>

      {/* Zoom Controls */}
      <View style={styles.zoomContainer}>
        <TouchableOpacity
          style={[styles.controlButton, styles.zoomButton]}
          onPress={onZoomIn}
          activeOpacity={0.7}
        >
          <Ionicons name="add" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
        <View style={styles.zoomDivider} />
        <TouchableOpacity
          style={[styles.controlButton, styles.zoomButton]}
          onPress={onZoomOut}
          activeOpacity={0.7}
        >
          <Ionicons name="remove" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
      </View>

      {/* Locate Me */}
      <TouchableOpacity
        style={[styles.controlButton, isLocating && styles.controlButtonActive]}
        onPress={onLocateMe}
        activeOpacity={0.7}
      >
        <Ionicons
          name={isLocating ? "locate" : "locate-outline"}
          size={24}
          color={isLocating ? colors.accentBlue : colors.textPrimary}
        />
      </TouchableOpacity>

      {/* Layer Control */}
      {showLayerControl && (
        <View style={styles.layerContainer}>
          {layers.map((layer) => (
            <TouchableOpacity
              key={layer.key}
              style={[
                styles.layerButton,
                currentLayer === layer.key && styles.layerButtonActive,
              ]}
              onPress={() => onLayerChange?.(layer.key)}
              activeOpacity={0.7}
            >
              <Ionicons
                name={layer.icon}
                size={18}
                color={currentLayer === layer.key ? colors.accentBlue : colors.textSecondary}
              />
            </TouchableOpacity>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    right: spacing.md,
    top: spacing.xxl + spacing.lg,
    gap: spacing.sm,
  },
  controlButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.bgSecondary,
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
  },
  controlButtonActive: {
    backgroundColor: "rgba(61, 139, 255, 0.15)",
    borderColor: colors.accentBlue,
  },
  zoomContainer: {
    backgroundColor: colors.bgSecondary,
    borderRadius: 22,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
    overflow: "hidden",
  },
  zoomButton: {
    borderRadius: 0,
    shadowOpacity: 0,
    elevation: 0,
    borderWidth: 0,
  },
  zoomDivider: {
    height: 1,
    backgroundColor: colors.surfaceBorder,
    marginHorizontal: spacing.sm,
  },
  layerContainer: {
    backgroundColor: colors.bgSecondary,
    borderRadius: radius.md,
    padding: spacing.xs,
    gap: spacing.xs,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
  },
  layerButton: {
    width: 36,
    height: 36,
    borderRadius: radius.sm,
    alignItems: "center",
    justifyContent: "center",
  },
  layerButtonActive: {
    backgroundColor: "rgba(61, 139, 255, 0.15)",
  },
});
