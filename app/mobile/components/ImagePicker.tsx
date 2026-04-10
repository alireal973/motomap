// app/mobile/components/ImagePicker.tsx
import { useState } from "react";
import {
  Alert,
  Image,
  Modal,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  ViewStyle,
  StyleProp,
  ActivityIndicator,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as ExpoImagePicker from "expo-image-picker";
import { colors, spacing, radius } from "../theme";

type ImageAsset = {
  uri: string;
  width: number;
  height: number;
  type?: "image" | "video";
  fileName?: string;
  fileSize?: number;
};

type Props = {
  label?: string;
  value?: ImageAsset | null;
  onChange: (image: ImageAsset | null) => void;
  placeholder?: string;
  error?: string;
  containerStyle?: StyleProp<ViewStyle>;
  aspectRatio?: [number, number];
  quality?: number;
  allowsEditing?: boolean;
  maxWidth?: number;
  maxHeight?: number;
};

export default function ImagePicker({
  label,
  value,
  onChange,
  placeholder = "Fotoğraf ekle",
  error,
  containerStyle,
  aspectRatio,
  quality = 0.8,
  allowsEditing = true,
  maxWidth = 1200,
  maxHeight = 1200,
}: Props) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const requestPermission = async (type: "camera" | "library"): Promise<boolean> => {
    if (type === "camera") {
      const { status } = await ExpoImagePicker.requestCameraPermissionsAsync();
      if (status !== "granted") {
        Alert.alert(
          "İzin Gerekli",
          "Kamera kullanmak için izin vermeniz gerekmektedir.",
          [{ text: "Tamam" }]
        );
        return false;
      }
    } else {
      const { status } = await ExpoImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== "granted") {
        Alert.alert(
          "İzin Gerekli",
          "Galeri erişimi için izin vermeniz gerekmektedir.",
          [{ text: "Tamam" }]
        );
        return false;
      }
    }
    return true;
  };

  const pickImage = async (source: "camera" | "library") => {
    setIsModalOpen(false);

    const hasPermission = await requestPermission(source);
    if (!hasPermission) return;

    setIsLoading(true);

    try {
      const options: ExpoImagePicker.ImagePickerOptions = {
        mediaTypes: ExpoImagePicker.MediaTypeOptions.Images,
        allowsEditing,
        aspect: aspectRatio,
        quality,
      };

      const result =
        source === "camera"
          ? await ExpoImagePicker.launchCameraAsync(options)
          : await ExpoImagePicker.launchImageLibraryAsync(options);

      if (!result.canceled && result.assets[0]) {
        const asset = result.assets[0];
        onChange({
          uri: asset.uri,
          width: asset.width,
          height: asset.height,
          type: "image",
          fileName: asset.fileName || undefined,
          fileSize: asset.fileSize || undefined,
        });
      }
    } catch (err) {
      Alert.alert("Hata", "Fotoğraf seçilirken bir hata oluştu.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemove = () => {
    Alert.alert("Fotoğrafı Kaldır", "Bu fotoğrafı kaldırmak istediğinize emin misiniz?", [
      { text: "İptal", style: "cancel" },
      {
        text: "Kaldır",
        style: "destructive",
        onPress: () => onChange(null),
      },
    ]);
  };

  const borderColor = error ? colors.danger : colors.surfaceBorder;

  return (
    <View style={[styles.container, containerStyle]}>
      {label && <Text style={styles.label}>{label}</Text>}

      {value ? (
        <View style={styles.previewContainer}>
          <Image source={{ uri: value.uri }} style={styles.preview} resizeMode="cover" />
          <View style={styles.previewOverlay}>
            <TouchableOpacity
              style={styles.previewButton}
              onPress={() => setIsModalOpen(true)}
              accessibilityLabel="Fotoğrafı değiştir"
            >
              <Ionicons name="camera" size={20} color={colors.textPrimary} />
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.previewButton, styles.removeButton]}
              onPress={handleRemove}
              accessibilityLabel="Fotoğrafı kaldır"
            >
              <Ionicons name="trash" size={20} color={colors.danger} />
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <TouchableOpacity
          style={[styles.pickerButton, { borderColor }]}
          onPress={() => setIsModalOpen(true)}
          activeOpacity={0.85}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color={colors.accentBlue} />
          ) : (
            <>
              <Ionicons name="camera-outline" size={32} color={colors.textTertiary} />
              <Text style={styles.placeholderText}>{placeholder}</Text>
            </>
          )}
        </TouchableOpacity>
      )}

      {error && (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={14} color={colors.danger} />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      <Modal
        visible={isModalOpen}
        transparent
        animationType="fade"
        onRequestClose={() => setIsModalOpen(false)}
      >
        <TouchableOpacity
          style={styles.modalOverlay}
          activeOpacity={1}
          onPress={() => setIsModalOpen(false)}
        >
          <View style={styles.modalContent} onStartShouldSetResponder={() => true}>
            <Text style={styles.modalTitle}>Fotoğraf Seç</Text>

            <TouchableOpacity
              style={styles.optionButton}
              onPress={() => pickImage("camera")}
            >
              <Ionicons name="camera" size={24} color={colors.accentBlue} />
              <Text style={styles.optionText}>Kamera ile Çek</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.optionButton}
              onPress={() => pickImage("library")}
            >
              <Ionicons name="images" size={24} color={colors.accentBlue} />
              <Text style={styles.optionText}>Galeriden Seç</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.cancelButton}
              onPress={() => setIsModalOpen(false)}
            >
              <Text style={styles.cancelText}>İptal</Text>
            </TouchableOpacity>
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.md,
  },
  label: {
    color: colors.textSecondary,
    fontSize: 14,
    fontWeight: "600",
    marginBottom: spacing.sm,
  },
  pickerButton: {
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surfaceGlass,
    borderWidth: 2,
    borderStyle: "dashed",
    borderRadius: radius.lg,
    paddingVertical: spacing.xxl,
    paddingHorizontal: spacing.lg,
    gap: spacing.sm,
  },
  placeholderText: {
    color: colors.textTertiary,
    fontSize: 14,
    fontWeight: "500",
  },
  previewContainer: {
    position: "relative",
    borderRadius: radius.lg,
    overflow: "hidden",
  },
  preview: {
    width: "100%",
    aspectRatio: 16 / 9,
    backgroundColor: colors.surfaceGlass,
  },
  previewOverlay: {
    position: "absolute",
    bottom: spacing.sm,
    right: spacing.sm,
    flexDirection: "row",
    gap: spacing.sm,
  },
  previewButton: {
    backgroundColor: "rgba(0, 0, 0, 0.6)",
    borderRadius: radius.pill,
    padding: spacing.sm,
  },
  removeButton: {
    backgroundColor: "rgba(0, 0, 0, 0.8)",
  },
  errorContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: spacing.xs,
  },
  errorText: {
    color: colors.danger,
    fontSize: 12,
    marginLeft: spacing.xs,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.7)",
    justifyContent: "flex-end",
  },
  modalContent: {
    backgroundColor: colors.bgSecondary,
    borderTopLeftRadius: radius.xl,
    borderTopRightRadius: radius.xl,
    padding: spacing.lg,
    paddingBottom: spacing.xxl,
  },
  modalTitle: {
    color: colors.textPrimary,
    fontSize: 18,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: spacing.lg,
  },
  optionButton: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceGlass,
    borderRadius: radius.md,
    padding: spacing.lg,
    marginBottom: spacing.sm,
    gap: spacing.md,
  },
  optionText: {
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: "600",
  },
  cancelButton: {
    alignItems: "center",
    padding: spacing.md,
    marginTop: spacing.sm,
  },
  cancelText: {
    color: colors.textTertiary,
    fontSize: 16,
    fontWeight: "600",
  },
});
