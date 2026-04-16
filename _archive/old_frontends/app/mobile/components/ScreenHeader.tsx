// app/mobile/components/ScreenHeader.tsx
import { ReactNode } from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { colors, spacing, typography } from "../theme";

type Props = {
  title: string;
  onBack?: () => void;
  rightAction?: ReactNode;
};

export default function ScreenHeader({ title, onBack, rightAction }: Props) {
  return (
    <View style={styles.container}>
      {onBack ? (
        <TouchableOpacity
          style={styles.backBtn}
          onPress={onBack}
          activeOpacity={0.7}
          accessibilityRole="button"
          accessibilityLabel="Geri"
        >
          <Text style={styles.backIcon}>{"\u2039"}</Text>
        </TouchableOpacity>
      ) : (
        <View style={styles.backPlaceholder} />
      )}
      <Text style={styles.title}>{title}</Text>
      <View style={styles.rightSlot}>{rightAction}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    paddingTop: spacing.topSafeArea,
    paddingBottom: 16,
    paddingHorizontal: spacing.screenPadding,
    backgroundColor: colors.bgPrimary,
  },
  backBtn: {
    width: 40,
    height: 40,
    alignItems: "center",
    justifyContent: "center",
    marginRight: spacing.sm,
  },
  backPlaceholder: {
    width: 40,
    marginRight: spacing.sm,
  },
  backIcon: {
    fontSize: 32,
    color: colors.textSecondary,
    fontWeight: "300",
    lineHeight: 36,
  },
  title: {
    flex: 1,
    ...typography.h3,
    color: colors.textPrimary,
  },
  rightSlot: {
    width: 40,
    alignItems: "flex-end",
  },
});