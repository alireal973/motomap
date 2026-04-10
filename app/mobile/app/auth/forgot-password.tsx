import { useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import { apiRequest } from "../../utils/api";
import { colors, spacing, radius } from "../../theme";

export default function ForgotPasswordScreen() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!email.trim()) {
      setError("E-posta gereklidir");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await apiRequest("/api/auth/forgot-password", {
        method: "POST",
        body: { email: email.trim() },
      });
      setSent(true);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Bir hata olustu, tekrar deneyin"
      );
    } finally {
      setLoading(false);
    }
  };

  if (sent) {
    return (
      <LinearGradient
        colors={[colors.bgTertiary, colors.bgPrimary]}
        style={styles.container}
      >
        <View style={styles.center}>
          <Text style={styles.successIcon}>{"\uD83D\uDCE7"}</Text>
          <Text style={styles.successTitle}>E-posta Gonderildi</Text>
          <Text style={styles.successSub}>
            Sifre sifirlama baglantisi {email} adresine gonderildi. Gelen
            kutunuzu kontrol edin.
          </Text>
          <TouchableOpacity
            style={styles.button}
            onPress={() => router.replace("/auth/login" as never)}
          >
            <Text style={styles.buttonText}>Girise Don</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient
      colors={[colors.bgTertiary, colors.bgPrimary]}
      style={styles.container}
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.flex}
      >
        <View style={styles.center}>
          <Text style={styles.title}>Sifremi Unuttum</Text>
          <Text style={styles.subtitle}>
            E-posta adresinizi girin, size sifre sifirlama baglantisi
            gonderelim.
          </Text>

          {error && (
            <View style={styles.errorBox}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}

          <TextInput
            style={styles.input}
            placeholder="E-posta adresiniz"
            placeholderTextColor={colors.textTertiary}
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            editable={!loading}
          />

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleSubmit}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color={colors.textPrimary} />
            ) : (
              <Text style={styles.buttonText}>Sifirlama Baglantisi Gonder</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
            <Text style={styles.backText}>Geri Don</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  flex: { flex: 1 },
  center: { flex: 1, justifyContent: "center", padding: spacing.lg },
  title: {
    fontSize: 28,
    fontWeight: "800",
    color: colors.textPrimary,
    textAlign: "center",
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: "center",
    marginBottom: spacing.lg,
    paddingHorizontal: spacing.md,
  },
  errorBox: {
    backgroundColor: "rgba(239,68,68,0.12)",
    borderWidth: 1,
    borderColor: colors.danger,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  errorText: { color: colors.danger, fontSize: 14, textAlign: "center" },
  input: {
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
    borderRadius: radius.md,
    padding: spacing.md,
    fontSize: 16,
    color: colors.textPrimary,
    marginBottom: spacing.lg,
  },
  button: {
    backgroundColor: colors.accentBlue,
    borderRadius: radius.md,
    padding: spacing.md,
    alignItems: "center",
    marginBottom: spacing.md,
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { fontSize: 16, fontWeight: "700", color: colors.textPrimary },
  backBtn: { alignItems: "center", padding: spacing.md },
  backText: { fontSize: 14, color: colors.textTertiary },
  successIcon: { fontSize: 64, textAlign: "center", marginBottom: spacing.md },
  successTitle: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.textPrimary,
    textAlign: "center",
    marginBottom: spacing.sm,
  },
  successSub: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: "center",
    marginBottom: spacing.lg,
    paddingHorizontal: spacing.md,
  },
});
