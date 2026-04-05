// app/mobile/components/GlassCard.tsx
import { ReactNode } from "react";
import {
  StyleSheet,
  TouchableOpacity,
  View,
  ViewStyle, StyleProp,
} from "react-native";
import { colors } from "../theme";

type Props = {
  children: ReactNode;
  style?: StyleProp<ViewStyle>;
  onPress?: () => void;
  activeOpacity?: number;
  accessibilityLabel?: string;
};

export default function GlassCard({
  children,
  style,
  onPress,
  activeOpacity = 0.85,
  accessibilityLabel,
}: Props) {
  if (onPress) {
    return (
      <TouchableOpacity
        style={[styles.card, style]}
        onPress={onPress}
        activeOpacity={activeOpacity}
        accessibilityRole="button"
        accessibilityLabel={accessibilityLabel}
      >
        {children}
      </TouchableOpacity>
    );
  }

  return <View style={[styles.card, style]}>{children}</View>;
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
    borderRadius: 18,
    padding: 18,
  },
});