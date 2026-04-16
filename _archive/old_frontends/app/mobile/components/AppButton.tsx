// app/mobile/components/AppButton.tsx
import {
  ActivityIndicator,
  StyleSheet,
  Text,
  TouchableOpacity,
  ViewStyle, StyleProp,
} from "react-native";
import { colors, radius, glowShadow } from "../theme";

type Variant = "primary" | "secondary" | "ghost";

type Props = {
  title: string;
  onPress: () => void;
  variant?: Variant;
  loading?: boolean;
  style?: StyleProp<ViewStyle>;
  accessibilityLabel?: string;
};

export default function AppButton({
  title,
  onPress,
  variant = "primary",
  loading = false,
  style,
  accessibilityLabel,
}: Props) {
  const variantStyle = variantStyles[variant];
  const textColor =
    variant === "primary"
      ? "#FFFFFF"
      : variant === "secondary"
        ? colors.textSecondary
        : colors.textTertiary;

  return (
    <TouchableOpacity
      style={[styles.base, variantStyle, style]}
      onPress={onPress}
      activeOpacity={0.85}
      disabled={loading}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel ?? title}
    >
      {loading ? (
        <ActivityIndicator color={textColor} />
      ) : (
        <Text style={[styles.text, { color: textColor }]}>{title}</Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    alignItems: "center",
    justifyContent: "center",
    minHeight: 48,
  },
  text: {
    fontSize: 16,
    fontWeight: "800",
    letterSpacing: 1,
  },
});

const variantStyles: Record<Variant, ViewStyle> = {
  primary: {
    backgroundColor: colors.accentBlue,
    borderRadius: radius.pill,
    paddingVertical: 18,
    paddingHorizontal: 32,
    ...glowShadow(colors.accentBlue),
  },
  secondary: {
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1.5,
    borderColor: colors.surfaceBorder,
    borderRadius: radius.md,
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  ghost: {
    backgroundColor: "transparent",
    paddingVertical: 12,
  },
};