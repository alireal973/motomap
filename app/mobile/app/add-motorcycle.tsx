// app/mobile/app/add-motorcycle.tsx
import { useRouter } from "expo-router";
import { useState } from "react";
import {
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import AppButton from "../components/AppButton";
import ScreenHeader from "../components/ScreenHeader";
import { useApp } from "../context/AppContext";
import { colors, spacing } from "../theme";
import { MotorcycleType } from "../types";

const TYPES: { key: MotorcycleType; label: string }[] = [
  { key: "naked", label: "Naked" },
  { key: "sport", label: "Sport" },
  { key: "touring", label: "Touring" },
  { key: "adventure", label: "Adventure" },
  { key: "scooter", label: "Scooter" },
];

export default function AddMotorcycleScreen() {
  const router = useRouter();
  const { addMotorcycle, motorcycles } = useApp();

  const [brand, setBrand] = useState("");
  const [model, setModel] = useState("");
  const [cc, setCc] = useState("");
  const [type, setType] = useState<MotorcycleType>("naked");
  const [weightKg, setWeightKg] = useState("");
  const [torqueNm, setTorqueNm] = useState("");
  const [tireType, setTireType] = useState("road");

  const canSave = brand.trim().length > 0 && model.trim().length > 0 && cc.trim().length > 0;

  const handleSave = () => {
    if (!canSave) return;
    addMotorcycle({
      id: Date.now().toString(),
      brand: brand.trim(),
      model: model.trim(),
      cc: parseInt(cc, 10) || 0,
      type,
      weight_kg: weightKg ? parseInt(weightKg, 10) : undefined,
      torque_nm: torqueNm ? parseInt(torqueNm, 10) : undefined,
      tire_type: tireType,
      isActive: motorcycles.length === 0,
    });
    router.back();
  };

  return (
    <View style={styles.container}>
      <ScreenHeader title="Motor Ekle" onBack={() => router.back()} />

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Text style={styles.label}>Marka</Text>
        <TextInput
          style={styles.input}
          placeholder={"Honda, Yamaha, BMW..."}
          placeholderTextColor={colors.textTertiary}
          value={brand}
          onChangeText={setBrand}
        />

        <Text style={styles.label}>Model</Text>
        <TextInput
          style={styles.input}
          placeholder={"CB650R, MT-07..."}
          placeholderTextColor={colors.textTertiary}
          value={model}
          onChangeText={setModel}
        />

        <Text style={styles.label}>Motor Hacmi (cc)</Text>
        <TextInput
          style={styles.input}
          placeholder="600"
          placeholderTextColor={colors.textTertiary}
          value={cc}
          onChangeText={setCc}
          keyboardType="numeric"
        />

        <Text style={styles.label}>Ağırlık (kg)</Text>
        <TextInput
          style={styles.input}
          placeholder="180"
          placeholderTextColor={colors.textTertiary}
          value={weightKg}
          onChangeText={setWeightKg}
          keyboardType="numeric"
        />

        <Text style={styles.label}>Tork (Nm)</Text>
        <TextInput
          style={styles.input}
          placeholder="64"
          placeholderTextColor={colors.textTertiary}
          value={torqueNm}
          onChangeText={setTorqueNm}
          keyboardType="numeric"
        />

        <Text style={styles.label}>Lastik Tipi</Text>
        <View style={styles.typeRow}>
          {[
            { key: "road", label: "Yol / Asfalt" },
            { key: "dual", label: "Dual-Sport" },
            { key: "offroad", label: "Offroad / Dişli" },
          ].map((t) => (
            <TouchableOpacity
              key={t.key}
              style={[styles.typeBtn, tireType === t.key && styles.typeBtnActive]}
              onPress={() => setTireType(t.key)}
              activeOpacity={0.8}
            >
              <Text style={[styles.typeBtnText, tireType === t.key && styles.typeBtnTextActive]}>
                {t.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <Text style={styles.label}>Tip</Text>
        <View style={styles.typeRow}>
          {TYPES.map((t) => (
            <TouchableOpacity
              key={t.key}
              style={[styles.typeBtn, type === t.key && styles.typeBtnActive]}
              onPress={() => setType(t.key)}
              activeOpacity={0.8}
            >
              <Text style={[styles.typeBtnText, type === t.key && styles.typeBtnTextActive]}>
                {t.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <AppButton
          title="Kaydet"
          onPress={handleSave}
          style={{ marginTop: spacing.xl, opacity: canSave ? 1 : 0.4 }}
        />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  scroll: {
    paddingHorizontal: spacing.screenPadding,
    paddingBottom: 40,
    gap: 6,
  },
  label: {
    color: colors.textSecondary,
    fontSize: 13,
    fontWeight: "700",
    letterSpacing: 0.5,
    marginTop: 18,
    marginBottom: 8,
  },
  input: {
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
    borderRadius: 14,
    paddingVertical: 14,
    paddingHorizontal: 16,
    fontSize: 15,
    color: colors.textPrimary,
  },
  typeRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  typeBtn: {
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1.5,
    borderColor: colors.surfaceBorder,
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 16,
  },
  typeBtnActive: {
    borderColor: colors.accentBlue,
    backgroundColor: "rgba(61,139,255,0.2)",
  },
  typeBtnText: {
    color: colors.textTertiary,
    fontSize: 13,
    fontWeight: "700",
  },
  typeBtnTextActive: {
    color: colors.accentBlue,
  },
});