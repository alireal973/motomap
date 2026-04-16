import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius, typography, shadows } from "../../theme";
import GlassCard from "../../components/GlassCard";
import InputField from "../../components/InputField";
import SelectField from "../../components/SelectField";
import ImagePicker from "../../components/ImagePicker";
import { useAuth } from "../../context/AuthContext";
import { useToast } from "../../components/Toast";

interface MotorcycleData {
  id: string;
  brand: string;
  model: string;
  year: number;
  cc: number;
  license_plate: string;
  color: string;
  nickname?: string;
  image_url?: string;
  odometer_km: number;
  is_primary: boolean;
}

const MOTORCYCLE_BRANDS = [
  "Honda", "Yamaha", "Kawasaki", "Suzuki", "BMW", "Ducati", "KTM",
  "Harley-Davidson", "Triumph", "Aprilia", "Moto Guzzi", "Benelli",
  "CF Moto", "Royal Enfield", "Diğer"
];

const CURRENT_YEAR = new Date().getFullYear();
const YEARS = Array.from({ length: 40 }, (_, i) => CURRENT_YEAR - i);

const CC_OPTIONS = [
  "50", "125", "150", "250", "300", "400", "500", "600", "650",
  "750", "800", "900", "1000", "1100", "1200", "1300", "1400+"
];

const COLOR_OPTIONS = [
  "Siyah", "Beyaz", "Kırmızı", "Mavi", "Yeşil", "Sarı", "Turuncu",
  "Gri", "Gümüş", "Mor", "Pembe", "Kahverengi", "Çok Renkli"
];

export default function MotorcycleEditScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { token } = useAuth();
  const { showToast } = useToast();
  const isNew = id === "new";

  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  // Form state
  const [brand, setBrand] = useState("");
  const [model, setModel] = useState("");
  const [year, setYear] = useState<string>("");
  const [cc, setCc] = useState("");
  const [licensePlate, setLicensePlate] = useState("");
  const [color, setColor] = useState("");
  const [nickname, setNickname] = useState("");
  const [odometer, setOdometer] = useState("");
  const [image, setImage] = useState<string | undefined>();
  const [isPrimary, setIsPrimary] = useState(false);

  // Validation errors
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!isNew) {
      fetchMotorcycleDetails();
    }
  }, [id]);

  const fetchMotorcycleDetails = async () => {
    try {
      // TODO: API call
      setTimeout(() => {
        const moto: MotorcycleData = {
          id: id || "1",
          brand: "Yamaha",
          model: "MT-07",
          year: 2022,
          cc: 689,
          license_plate: "34 ABC 123",
          color: "Mavi",
          nickname: "Gece Kartalı",
          odometer_km: 12500,
          is_primary: true,
        };

        setBrand(moto.brand);
        setModel(moto.model);
        setYear(moto.year.toString());
        setCc(moto.cc.toString());
        setLicensePlate(moto.license_plate);
        setColor(moto.color);
        setNickname(moto.nickname || "");
        setOdometer(moto.odometer_km.toString());
        setIsPrimary(moto.is_primary);
        setImage(moto.image_url);

        setLoading(false);
      }, 500);
    } catch (error) {
      console.error("Error fetching motorcycle:", error);
      setLoading(false);
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!brand) newErrors.brand = "Marka seçiniz";
    if (!model.trim()) newErrors.model = "Model giriniz";
    if (!year) newErrors.year = "Yıl seçiniz";
    if (!cc) newErrors.cc = "Motor hacmi seçiniz";
    if (!licensePlate.trim()) newErrors.licensePlate = "Plaka giriniz";
    if (!color) newErrors.color = "Renk seçiniz";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validate()) {
      showToast({ message: "Lütfen zorunlu alanları doldurun", type: "error" });
      return;
    }

    setSaving(true);

    try {
      // TODO: API call
      const data = {
        brand,
        model: model.trim(),
        year: parseInt(year),
        cc: parseInt(cc.replace("+", "")),
        license_plate: licensePlate.trim().toUpperCase(),
        color,
        nickname: nickname.trim() || undefined,
        odometer_km: parseInt(odometer) || 0,
        is_primary: isPrimary,
        image_url: image,
      };

      console.log("Saving motorcycle:", data);

      await new Promise((resolve) => setTimeout(resolve, 1000));

      showToast({ message: isNew ? "Motosiklet eklendi!" : "Değişiklikler kaydedildi", type: "success" });
      router.back();
    } catch (error) {
      showToast({ message: "Kaydetme başarısız", type: "error" });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = () => {
    Alert.alert(
      "Motosikleti Sil",
      "Bu motosikleti silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.",
      [
        { text: "İptal", style: "cancel" },
        {
          text: "Sil",
          style: "destructive",
          onPress: async () => {
            setDeleting(true);
            try {
              // TODO: API call
              await new Promise((resolve) => setTimeout(resolve, 1000));
              showToast({ message: "Motosiklet silindi", type: "success" });
              router.back();
            } catch (error) {
              showToast({ message: "Silme başarısız", type: "error" });
            } finally {
              setDeleting(false);
            }
          },
        },
      ]
    );
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

  return (
    <SafeAreaView style={styles.container} edges={["top"]}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.headerButton}>
          <Ionicons name="close" size={24} color={colors.textPrimary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>
          {isNew ? "Yeni Motosiklet" : "Motosikleti Düzenle"}
        </Text>
        <TouchableOpacity
          onPress={handleSave}
          style={styles.headerButton}
          disabled={saving}
        >
          {saving ? (
            <ActivityIndicator size="small" color={colors.accentBlue} />
          ) : (
            <Text style={styles.saveText}>Kaydet</Text>
          )}
        </TouchableOpacity>
      </View>

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        {/* Image */}
        <View style={styles.imageSection}>
          <ImagePicker
            value={image ? { uri: image, width: 0, height: 0 } : null}
            onChange={(img) => setImage(img?.uri)}
            placeholder="Motosiklet fotoğrafı ekle"
            aspectRatio={[16, 9]}
          />
        </View>

        {/* Basic Info */}
        <Text style={styles.sectionTitle}>Temel Bilgiler</Text>
        <GlassCard style={styles.formCard}>
          <SelectField
            label="Marka *"
            value={brand}
            onSelect={setBrand}
            options={MOTORCYCLE_BRANDS.map(b => ({ label: b, value: b }))}
            placeholder="Marka seçin"
            error={errors.brand}
          />

          <InputField
            label="Model *"
            value={model}
            onChangeText={(text) => {
              setModel(text);
              if (errors.model) setErrors({ ...errors, model: "" });
            }}
            placeholder="örn: MT-07, CBR600RR"
            error={errors.model}
          />

          <View style={styles.row}>
            <View style={styles.halfField}>
              <SelectField
                label="Yıl *"
                value={year}
                onSelect={setYear}
                options={YEARS.map(y => ({ label: String(y), value: String(y) }))}
                placeholder="Yıl"
                error={errors.year}
              />
            </View>
            <View style={styles.halfField}>
              <SelectField
                label="Motor Hacmi (cc) *"
                value={cc}
                onSelect={setCc}
                options={CC_OPTIONS.map(c => ({ label: c, value: c }))}
                placeholder="cc"
                error={errors.cc}
              />
            </View>
          </View>

          <SelectField
            label="Renk *"
            value={color}
            onSelect={setColor}
            options={COLOR_OPTIONS.map(c => ({ label: c, value: c }))}
            placeholder="Renk seçin"
            error={errors.color}
          />
        </GlassCard>

        {/* Registration */}
        <Text style={styles.sectionTitle}>Kayıt Bilgileri</Text>
        <GlassCard style={styles.formCard}>
          <InputField
            label="Plaka *"
            value={licensePlate}
            onChangeText={(text) => {
              setLicensePlate(text.toUpperCase());
              if (errors.licensePlate) setErrors({ ...errors, licensePlate: "" });
            }}
            placeholder="örn: 34 ABC 123"
            autoCapitalize="characters"
            error={errors.licensePlate}
          />

          <InputField
            label="Kilometre"
            value={odometer}
            onChangeText={setOdometer}
            placeholder="örn: 12500"
            keyboardType="numeric"
            rightIcon="speedometer-outline"
          />
        </GlassCard>

        {/* Optional */}
        <Text style={styles.sectionTitle}>İsteğe Bağlı</Text>
        <GlassCard style={styles.formCard}>
          <InputField
            label="Takma Ad"
            value={nickname}
            onChangeText={setNickname}
            placeholder="örn: Gece Kartalı"
            maxLength={30}
          />

          <TouchableOpacity
            style={styles.primaryToggle}
            onPress={() => setIsPrimary(!isPrimary)}
          >
            <View style={styles.primaryInfo}>
              <Ionicons
                name={isPrimary ? "star" : "star-outline"}
                size={24}
                color={isPrimary ? "#FFD700" : colors.textSecondary}
              />
              <View>
                <Text style={styles.primaryLabel}>Birincil Motosiklet</Text>
                <Text style={styles.primaryHint}>
                  Varsayılan olarak bu motosiklet kullanılsın
                </Text>
              </View>
            </View>
            <View style={[styles.toggleSwitch, isPrimary && styles.toggleSwitchActive]}>
              <View style={[styles.toggleThumb, isPrimary && styles.toggleThumbActive]} />
            </View>
          </TouchableOpacity>
        </GlassCard>

        {/* Delete Button */}
        {!isNew && (
          <TouchableOpacity
            style={styles.deleteButton}
            onPress={handleDelete}
            disabled={deleting}
          >
            {deleting ? (
              <ActivityIndicator size="small" color={colors.errorRed} />
            ) : (
              <>
                <Ionicons name="trash-outline" size={20} color={colors.errorRed} />
                <Text style={styles.deleteButtonText}>Motosikleti Sil</Text>
              </>
            )}
          </TouchableOpacity>
        )}
      </ScrollView>
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
    minWidth: 60,
  },
  headerTitle: {
    ...typography.h4,
    color: colors.textPrimary,
    flex: 1,
    textAlign: "center",
  },
  saveText: {
    ...typography.body,
    color: colors.accentBlue,
    fontWeight: "600",
    textAlign: "right",
  },
  scrollContent: {
    padding: spacing.md,
    paddingBottom: spacing.xxl,
  },
  imageSection: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    ...typography.h4,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    marginTop: spacing.md,
  },
  formCard: {
    padding: spacing.md,
  },
  row: {
    flexDirection: "row",
    gap: spacing.md,
  },
  halfField: {
    flex: 1,
  },
  primaryToggle: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: spacing.md,
    marginTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.borderDefault,
  },
  primaryInfo: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    flex: 1,
  },
  primaryLabel: {
    ...typography.body,
    color: colors.textPrimary,
  },
  primaryHint: {
    ...typography.caption,
    color: colors.textMuted,
  },
  toggleSwitch: {
    width: 50,
    height: 28,
    borderRadius: 14,
    backgroundColor: colors.surfaceGlass,
    padding: 2,
    justifyContent: "center",
  },
  toggleSwitchActive: {
    backgroundColor: colors.accentBlue,
  },
  toggleThumb: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.textSecondary,
  },
  toggleThumbActive: {
    backgroundColor: colors.textPrimary,
    alignSelf: "flex-end",
  },
  deleteButton: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: spacing.md,
    marginTop: spacing.xl,
    gap: spacing.sm,
  },
  deleteButtonText: {
    ...typography.body,
    color: colors.errorRed,
  },
});
