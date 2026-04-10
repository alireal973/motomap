// app/mobile/app/settings/account.tsx
import { useState } from "react";
import {
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import InputField from "../../components/InputField";
import AppButton from "../../components/AppButton";
import { colors, spacing, radius } from "../../theme";
import { useAuth } from "../../context/AuthContext";
import { apiRequest } from "../../utils/api";

export default function AccountSettingsScreen() {
  const { user, token, logout } = useAuth();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validatePasswordChange = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!currentPassword) {
      newErrors.currentPassword = "Mevcut şifre gerekli";
    }
    if (!newPassword) {
      newErrors.newPassword = "Yeni şifre gerekli";
    } else if (newPassword.length < 8) {
      newErrors.newPassword = "Şifre en az 8 karakter olmalı";
    }
    if (newPassword !== confirmPassword) {
      newErrors.confirmPassword = "Şifreler eşleşmiyor";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handlePasswordChange = async () => {
    if (!validatePasswordChange()) return;

    setIsLoading(true);
    try {
      await apiRequest("/api/auth/change-password", {
        method: "POST",
        token,
        body: {
          current_password: currentPassword,
          new_password: newPassword,
        },
      });

      Alert.alert("Başarılı", "Şifreniz değiştirildi.", [{ text: "Tamam" }]);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setErrors({});
    } catch (error: any) {
      Alert.alert("Hata", error.message || "Şifre değiştirilemedi.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailChange = async () => {
    if (!newEmail || !newEmail.includes("@")) {
      setErrors({ email: "Geçerli bir e-posta adresi girin" });
      return;
    }

    setIsLoading(true);
    try {
      await apiRequest("/api/auth/change-email", {
        method: "POST",
        token,
        body: { new_email: newEmail },
      });

      Alert.alert(
        "Doğrulama Gerekli",
        "Yeni e-posta adresinize bir doğrulama bağlantısı gönderdik.",
        [{ text: "Tamam" }]
      );
      setNewEmail("");
    } catch (error: any) {
      Alert.alert("Hata", error.message || "E-posta değiştirilemedi.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      "Hesabı Sil",
      "Bu işlem geri alınamaz. Tüm verileriniz silinecek. Devam etmek istediğinize emin misiniz?",
      [
        { text: "İptal", style: "cancel" },
        {
          text: "Hesabı Sil",
          style: "destructive",
          onPress: async () => {
            try {
              await apiRequest("/api/auth/delete-account", {
                method: "DELETE",
                token,
              });
              logout();
              router.replace("/");
            } catch (error: any) {
              Alert.alert("Hata", error.message || "Hesap silinemedi.");
            }
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <ScreenHeader title="Hesap Ayarları" onBack={() => router.back()} />
      <ScrollView contentContainerStyle={styles.scroll}>
        {/* Current Account Info */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Hesap Bilgileri</Text>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>E-posta</Text>
            <Text style={styles.infoValue}>{user?.email || "-"}</Text>
          </View>
          <View style={styles.infoRow}>
            <Text style={styles.infoLabel}>Kullanıcı Adı</Text>
            <Text style={styles.infoValue}>@{user?.username || "-"}</Text>
          </View>
        </GlassCard>

        {/* Change Email */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>E-posta Değiştir</Text>
          <InputField
            label="Yeni E-posta"
            placeholder="yeni@email.com"
            value={newEmail}
            onChangeText={setNewEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            leftIcon="mail-outline"
            error={errors.email}
          />
          <AppButton
            title="E-posta Değiştir"
            onPress={handleEmailChange}
            variant="secondary"
            loading={isLoading}
          />
        </GlassCard>

        {/* Change Password */}
        <GlassCard style={styles.section}>
          <Text style={styles.sectionTitle}>Şifre Değiştir</Text>
          <InputField
            label="Mevcut Şifre"
            placeholder="••••••••"
            value={currentPassword}
            onChangeText={setCurrentPassword}
            secureTextEntry
            leftIcon="lock-closed-outline"
            error={errors.currentPassword}
          />
          <InputField
            label="Yeni Şifre"
            placeholder="••••••••"
            value={newPassword}
            onChangeText={setNewPassword}
            secureTextEntry
            leftIcon="key-outline"
            error={errors.newPassword}
            hint="En az 8 karakter"
          />
          <InputField
            label="Yeni Şifre (Tekrar)"
            placeholder="••••••••"
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            secureTextEntry
            leftIcon="key-outline"
            error={errors.confirmPassword}
          />
          <AppButton
            title="Şifre Değiştir"
            onPress={handlePasswordChange}
            variant="primary"
            loading={isLoading}
          />
        </GlassCard>

        {/* Danger Zone */}
        <GlassCard style={[styles.section, styles.dangerSection]}>
          <Text style={[styles.sectionTitle, styles.dangerTitle]}>Tehlikeli Bölge</Text>
          <Text style={styles.dangerDescription}>
            Hesabınızı sildiğinizde tüm verileriniz kalıcı olarak silinecektir.
            Bu işlem geri alınamaz.
          </Text>
          <TouchableOpacity style={styles.deleteButton} onPress={handleDeleteAccount}>
            <Ionicons name="trash-outline" size={20} color={colors.danger} />
            <Text style={styles.deleteButtonText}>Hesabımı Sil</Text>
          </TouchableOpacity>
        </GlassCard>

        <View style={{ height: 100 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  scroll: {
    padding: spacing.md,
  },
  section: {
    marginBottom: spacing.md,
    padding: spacing.lg,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: colors.textTertiary,
    marginBottom: spacing.lg,
    textTransform: "uppercase",
    letterSpacing: 1,
  },
  infoRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.surfaceBorder,
  },
  infoLabel: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  infoValue: {
    fontSize: 14,
    color: colors.textPrimary,
    fontWeight: "500",
  },
  dangerSection: {
    borderWidth: 1,
    borderColor: colors.danger,
    backgroundColor: "rgba(239, 68, 68, 0.05)",
  },
  dangerTitle: {
    color: colors.danger,
  },
  dangerDescription: {
    fontSize: 13,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.lg,
  },
  deleteButton: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: spacing.md,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.danger,
    gap: spacing.sm,
  },
  deleteButtonText: {
    fontSize: 15,
    fontWeight: "600",
    color: colors.danger,
  },
});
