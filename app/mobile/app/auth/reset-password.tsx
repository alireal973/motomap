// app/mobile/app/auth/reset-password.tsx
import { useState } from "react";
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import GlassCard from "../../components/GlassCard";
import InputField from "../../components/InputField";
import AppButton from "../../components/AppButton";
import { colors, spacing, radius } from "../../theme";
import { apiRequest } from "../../utils/api";

export default function ResetPasswordScreen() {
  const { token } = useLocalSearchParams<{ token: string }>();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!newPassword) {
      newErrors.newPassword = "Şifre gerekli";
    } else if (newPassword.length < 8) {
      newErrors.newPassword = "Şifre en az 8 karakter olmalı";
    } else if (!/[A-Z]/.test(newPassword)) {
      newErrors.newPassword = "En az bir büyük harf içermeli";
    } else if (!/[0-9]/.test(newPassword)) {
      newErrors.newPassword = "En az bir rakam içermeli";
    }

    if (newPassword !== confirmPassword) {
      newErrors.confirmPassword = "Şifreler eşleşmiyor";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleReset = async () => {
    if (!validate()) return;

    if (!token) {
      Alert.alert("Hata", "Geçersiz veya eksik token. Lütfen bağlantıyı tekrar deneyin.");
      return;
    }

    setIsLoading(true);
    try {
      await apiRequest("/api/auth/reset-password", {
        method: "POST",
        body: {
          token,
          new_password: newPassword,
        },
      });

      setIsSuccess(true);
    } catch (error: any) {
      Alert.alert(
        "Hata",
        error.message || "Şifre sıfırlama başarısız. Token süresi dolmuş olabilir."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoToLogin = () => {
    router.replace("/auth/login" as any);
  };

  if (isSuccess) {
    return (
      <View style={styles.container}>
        <View style={styles.successContainer}>
          <View style={styles.successIcon}>
            <Ionicons name="checkmark-circle" size={64} color={colors.success} />
          </View>
          <Text style={styles.successTitle}>Şifre Değiştirildi!</Text>
          <Text style={styles.successMessage}>
            Yeni şifreniz başarıyla ayarlandı. Artık giriş yapabilirsiniz.
          </Text>
          <AppButton
            title="Giriş Yap"
            onPress={handleGoToLogin}
            style={styles.loginButton}
          />
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scroll}
          keyboardShouldPersistTaps="handled"
        >
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.iconContainer}>
              <Ionicons name="key" size={40} color={colors.accentBlue} />
            </View>
            <Text style={styles.title}>Yeni Şifre Belirle</Text>
            <Text style={styles.subtitle}>
              Hesabınız için güçlü bir şifre oluşturun.
            </Text>
          </View>

          {/* Form */}
          <GlassCard style={styles.formCard}>
            <InputField
              label="Yeni Şifre"
              placeholder="••••••••"
              value={newPassword}
              onChangeText={setNewPassword}
              secureTextEntry
              leftIcon="lock-closed-outline"
              error={errors.newPassword}
            />

            <InputField
              label="Şifre Tekrar"
              placeholder="••••••••"
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              secureTextEntry
              leftIcon="lock-closed-outline"
              error={errors.confirmPassword}
            />

            {/* Password Requirements */}
            <View style={styles.requirements}>
              <Text style={styles.requirementsTitle}>Şifre gereksinimleri:</Text>
              <PasswordRequirement
                met={newPassword.length >= 8}
                text="En az 8 karakter"
              />
              <PasswordRequirement
                met={/[A-Z]/.test(newPassword)}
                text="En az bir büyük harf"
              />
              <PasswordRequirement
                met={/[0-9]/.test(newPassword)}
                text="En az bir rakam"
              />
            </View>

            <AppButton
              title="Şifreyi Sıfırla"
              onPress={handleReset}
              loading={isLoading}
              style={styles.submitButton}
            />
          </GlassCard>

          <AppButton
            title="Giriş sayfasına dön"
            onPress={handleGoToLogin}
            variant="ghost"
          />
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

function PasswordRequirement({ met, text }: { met: boolean; text: string }) {
  return (
    <View style={styles.requirement}>
      <Ionicons
        name={met ? "checkmark-circle" : "ellipse-outline"}
        size={16}
        color={met ? colors.success : colors.textTertiary}
      />
      <Text style={[styles.requirementText, met && styles.requirementMet]}>
        {text}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  keyboardView: {
    flex: 1,
  },
  scroll: {
    flexGrow: 1,
    padding: spacing.lg,
    justifyContent: "center",
  },
  header: {
    alignItems: "center",
    marginBottom: spacing.xl,
  },
  iconContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.surfaceGlass,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: spacing.lg,
  },
  title: {
    fontSize: 28,
    fontWeight: "800",
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 24,
  },
  formCard: {
    padding: spacing.lg,
    marginBottom: spacing.lg,
  },
  requirements: {
    marginTop: spacing.sm,
    marginBottom: spacing.lg,
  },
  requirementsTitle: {
    fontSize: 13,
    color: colors.textTertiary,
    marginBottom: spacing.sm,
  },
  requirement: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    marginBottom: spacing.xs,
  },
  requirementText: {
    fontSize: 13,
    color: colors.textTertiary,
  },
  requirementMet: {
    color: colors.success,
  },
  submitButton: {
    marginTop: spacing.sm,
  },
  successContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: spacing.xl,
  },
  successIcon: {
    marginBottom: spacing.lg,
  },
  successTitle: {
    fontSize: 24,
    fontWeight: "700",
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  successMessage: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: "center",
    lineHeight: 24,
    marginBottom: spacing.xl,
  },
  loginButton: {
    minWidth: 200,
  },
});
