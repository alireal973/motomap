import { useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import * as Location from "expo-location";
import ScreenHeader from "../../components/ScreenHeader";
import AppButton from "../../components/AppButton";
import { colors, spacing, radius } from "../../theme";
import { apiRequest } from "../../utils/api";
import { useAuth } from "../../context/AuthContext";

type ReportOption = {
  type: string;
  category: string;
  label: string;
  icon: string;
  severity: string;
};

const REPORT_OPTIONS: ReportOption[] = [
  { type: "pothole", category: "hazard", label: "Cukur", icon: "\uD83D\uDD73\uFE0F", severity: "medium" },
  { type: "oil_spill", category: "hazard", label: "Yag Dokuntusi", icon: "\uD83D\uDEE2\uFE0F", severity: "high" },
  { type: "debris", category: "hazard", label: "Dokuntu/Tas", icon: "\uD83E\uDEA8", severity: "medium" },
  { type: "construction", category: "hazard", label: "Insaat", icon: "\uD83D\uDEA7", severity: "medium" },
  { type: "wet", category: "surface", label: "Islak Yol", icon: "\uD83D\uDCA7", severity: "medium" },
  { type: "ice", category: "surface", label: "Buzlanma", icon: "\u2744\uFE0F", severity: "critical" },
  { type: "fog", category: "surface", label: "Sis", icon: "\uD83C\uDF2B\uFE0F", severity: "medium" },
  { type: "heavy_traffic", category: "traffic", label: "Yogun Trafik", icon: "\uD83D\uDE99", severity: "low" },
  { type: "accident", category: "traffic", label: "Kaza", icon: "\uD83D\uDEA8", severity: "high" },
  { type: "police", category: "traffic", label: "Polis Kontrolu", icon: "\uD83D\uDC6E", severity: "low" },
  { type: "road_closure", category: "traffic", label: "Yol Kapali", icon: "\uD83D\uDED1", severity: "critical" },
  { type: "gas_station", category: "poi", label: "Benzinlik", icon: "\u26FD", severity: "low" },
  { type: "moto_shop", category: "poi", label: "Motosiklet Dukkani", icon: "\uD83D\uDD27", severity: "low" },
  { type: "scenic", category: "poi", label: "Manzara", icon: "\uD83D\uDCF8", severity: "low" },
  { type: "cafe", category: "poi", label: "Motorcu Kafesi", icon: "\u2615", severity: "low" },
];

export default function CreateReportScreen() {
  const { token } = useAuth();
  const [selected, setSelected] = useState<ReportOption | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async () => {
    if (!selected) {
      setError("Rapor turu secin");
      return;
    }
    if (!token) {
      router.push("/auth/login" as never);
      return;
    }

    setError(null);
    setLocating(true);

    let lat: number, lng: number;
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        setError("Konum izni gereklidir");
        setLocating(false);
        return;
      }
      const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
      lat = loc.coords.latitude;
      lng = loc.coords.longitude;
    } catch {
      setError("Konum alinamadi");
      setLocating(false);
      return;
    }
    setLocating(false);
    setLoading(true);

    try {
      await apiRequest("/api/reports", {
        method: "POST",
        token,
        body: {
          latitude: lat,
          longitude: lng,
          category: selected.category,
          type: selected.type,
          severity: selected.severity,
          title: title.trim() || undefined,
          description: description.trim() || undefined,
        },
      });
      setSuccess(true);
      setTimeout(() => router.back(), 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Rapor gonderilemedi");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <View style={[styles.container, styles.center]}>
        <Text style={styles.successIcon}>{"\u2705"}</Text>
        <Text style={styles.successText}>Rapor gonderildi!</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScreenHeader title="Yol Raporu Olustur" />
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={styles.flex}
      >
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
          {error && (
            <View style={styles.errorBox}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}

          <Text style={styles.sectionTitle}>Rapor Turu</Text>
          <View style={styles.grid}>
            {REPORT_OPTIONS.map((opt) => (
              <TouchableOpacity
                key={opt.type}
                style={[styles.optionCard, selected?.type === opt.type && styles.optionSelected]}
                onPress={() => setSelected(opt)}
              >
                <Text style={styles.optionIcon}>{opt.icon}</Text>
                <Text style={styles.optionLabel}>{opt.label}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <Text style={styles.sectionTitle}>Detaylar (istege bagli)</Text>
          <TextInput
            style={styles.input}
            placeholder="Baslik"
            placeholderTextColor={colors.textTertiary}
            value={title}
            onChangeText={setTitle}
            maxLength={200}
          />
          <TextInput
            style={[styles.input, styles.textArea]}
            placeholder="Aciklama"
            placeholderTextColor={colors.textTertiary}
            value={description}
            onChangeText={setDescription}
            multiline
            numberOfLines={3}
            maxLength={2000}
          />

          <AppButton
            title={locating ? "Konum aliniyor..." : loading ? "Gonderiliyor..." : "Raporu Gonder"}
            onPress={handleSubmit}
            loading={loading || locating}
            style={styles.submitBtn}
          />
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  flex: { flex: 1 },
  center: { justifyContent: "center", alignItems: "center" },
  scroll: { padding: spacing.md, paddingBottom: 100 },
  errorBox: { backgroundColor: "rgba(239,68,68,0.15)", borderWidth: 1, borderColor: colors.danger, borderRadius: radius.md, padding: spacing.md, marginBottom: spacing.md },
  errorText: { color: colors.danger, fontSize: 14, textAlign: "center" },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: colors.textPrimary, marginBottom: spacing.sm, marginTop: spacing.md },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: spacing.sm },
  optionCard: {
    width: "30%", flexGrow: 1,
    backgroundColor: colors.surfaceGlass, borderRadius: radius.md,
    padding: spacing.sm, alignItems: "center",
    borderWidth: 2, borderColor: "transparent",
  },
  optionSelected: { borderColor: colors.accentBlue, backgroundColor: colors.accentBlueGlow },
  optionIcon: { fontSize: 26, marginBottom: 4 },
  optionLabel: { fontSize: 11, color: colors.textSecondary, textAlign: "center" },
  input: {
    backgroundColor: colors.surfaceGlass, borderWidth: 1,
    borderColor: colors.surfaceBorder, borderRadius: radius.md,
    padding: spacing.md, fontSize: 15, color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  textArea: { height: 80, textAlignVertical: "top" },
  submitBtn: { marginTop: spacing.md },
  successIcon: { fontSize: 64, marginBottom: spacing.md },
  successText: { fontSize: 20, fontWeight: "700", color: colors.success },
});
