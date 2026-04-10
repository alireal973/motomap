import { useEffect, useState } from "react";
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
import { LinearGradient } from "expo-linear-gradient";
import * as Google from "expo-auth-session/providers/google";
import * as WebBrowser from "expo-web-browser";
import { useAuth } from "../../context/AuthContext";
import { colors, spacing, radius } from "../../theme";

WebBrowser.maybeCompleteAuthSession();

const GOOGLE_CLIENT_ID = process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID ?? "";

export default function LoginScreen() {
  const { login, googleLogin } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [_request, response, promptAsync] = Google.useIdTokenAuthRequest({
    clientId: GOOGLE_CLIENT_ID,
  });

  useEffect(() => {
    if (response?.type === "success") {
      const idToken = response.params.id_token;
      if (idToken) {
        setLoading(true);
        setError(null);
        googleLogin(idToken)
          .then(() => router.replace("/(tabs)"))
          .catch((err) =>
            setError(err instanceof Error ? err.message : "Google giris basarisiz")
          )
          .finally(() => setLoading(false));
      }
    }
  }, [response, googleLogin]);

  const handleLogin = async () => {
    if (!email.trim() || !password) {
      setError("E-posta ve sifre gereklidir");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await login(email.trim(), password);
      router.replace("/(tabs)");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Giris basarisiz");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    setError(null);
    promptAsync();
  };

  return (
    <LinearGradient colors={["#0E2A5C", "#06132E"]} style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.flex}
      >
        <ScrollView
          contentContainerStyle={styles.scroll}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.header}>
            <View style={styles.logoCircle}>
              <Text style={styles.logoIcon}>{"\u{1F3CD}\uFE0F"}</Text>
            </View>
            <Text style={styles.logo}>MotoMap</Text>
            <Text style={styles.subtitle}>Hesabiniza giris yapin</Text>
          </View>

          {error && (
            <View style={styles.errorBox}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}

          <TouchableOpacity
            style={styles.googleButton}
            onPress={handleGoogleLogin}
            activeOpacity={0.85}
            disabled={loading}
          >
            <View style={styles.googleIconWrap}>
              <Text style={styles.googleG}>G</Text>
            </View>
            <Text style={styles.googleButtonText}>Google ile Devam Et</Text>
          </TouchableOpacity>

          <View style={styles.dividerRow}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>veya</Text>
            <View style={styles.dividerLine} />
          </View>

          <View style={styles.form}>
            <Text style={styles.label}>E-posta</Text>
            <TextInput
              style={styles.input}
              placeholder="ornek@email.com"
              placeholderTextColor={colors.textTertiary}
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
              editable={!loading}
            />

            <Text style={styles.label}>Sifre</Text>
            <TextInput
              style={styles.input}
              placeholder="Sifrenizi girin"
              placeholderTextColor={colors.textTertiary}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              editable={!loading}
            />

            <TouchableOpacity
              onPress={() => router.push("/auth/forgot-password" as never)}
              style={styles.forgotRow}
            >
              <Text style={styles.forgotText}>Sifremi Unuttum</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, loading && styles.buttonDisabled]}
              onPress={handleLogin}
              disabled={loading}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={[colors.accentBlue, colors.accentBlueDark]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.buttonGradient}
              >
                {loading ? (
                  <ActivityIndicator color={colors.textPrimary} />
                ) : (
                  <Text style={styles.buttonText}>Giris Yap</Text>
                )}
              </LinearGradient>
            </TouchableOpacity>
          </View>

          <View style={styles.footer}>
            <Text style={styles.footerText}>Hesabiniz yok mu? </Text>
            <TouchableOpacity onPress={() => router.replace("/auth/register" as never)}>
              <Text style={styles.footerLink}>Kayit Ol</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity
            style={styles.backButton}
            onPress={() => router.back()}
          >
            <Text style={styles.backText}>Geri Don</Text>
          </TouchableOpacity>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  flex: { flex: 1 },
  scroll: { flexGrow: 1, justifyContent: "center", padding: spacing.lg },
  header: { alignItems: "center", marginBottom: spacing.xl },
  logoCircle: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: colors.surfaceElevated,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.md,
  },
  logoIcon: { fontSize: 32 },
  logo: {
    fontSize: 32,
    fontWeight: "900",
    color: colors.textPrimary,
    letterSpacing: 1,
    marginBottom: spacing.xs,
  },
  subtitle: { fontSize: 15, color: colors.textSecondary },
  errorBox: {
    backgroundColor: "rgba(239,68,68,0.12)",
    borderWidth: 1,
    borderColor: colors.danger,
    borderRadius: radius.md,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  errorText: { color: colors.danger, fontSize: 14, textAlign: "center" },
  googleButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.googleWhite,
    borderRadius: radius.md,
    paddingVertical: 14,
    paddingHorizontal: 20,
    gap: 12,
    marginBottom: spacing.lg,
  },
  googleIconWrap: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: "#4285F4",
    alignItems: "center",
    justifyContent: "center",
  },
  googleG: { color: "#fff", fontSize: 14, fontWeight: "800" },
  googleButtonText: {
    fontSize: 15,
    fontWeight: "600",
    color: colors.googleText,
  },
  dividerRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.lg,
    gap: 12,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: colors.surfaceBorder,
  },
  dividerText: {
    fontSize: 13,
    color: colors.textTertiary,
    fontWeight: "500",
  },
  form: { marginBottom: spacing.xl },
  label: {
    fontSize: 13,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    marginTop: spacing.md,
    fontWeight: "600",
    letterSpacing: 0.3,
  },
  input: {
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
    borderRadius: radius.md,
    padding: spacing.md,
    fontSize: 16,
    color: colors.textPrimary,
  },
  forgotRow: {
    alignSelf: "flex-end",
    marginTop: spacing.sm,
    paddingVertical: 4,
  },
  forgotText: { fontSize: 13, color: colors.accentBlue, fontWeight: "600" },
  button: {
    borderRadius: radius.md,
    overflow: "hidden",
    marginTop: spacing.lg,
  },
  buttonGradient: {
    paddingVertical: 16,
    alignItems: "center",
    borderRadius: radius.md,
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { fontSize: 16, fontWeight: "700", color: colors.textPrimary },
  footer: {
    flexDirection: "row",
    justifyContent: "center",
    marginBottom: spacing.md,
  },
  footerText: { fontSize: 14, color: colors.textSecondary },
  footerLink: { fontSize: 14, color: colors.accentBlue, fontWeight: "700" },
  backButton: { alignItems: "center", padding: spacing.md },
  backText: { fontSize: 14, color: colors.textTertiary },
});
