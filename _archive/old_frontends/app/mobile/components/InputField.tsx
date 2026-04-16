// app/mobile/components/InputField.tsx
import { useState, forwardRef } from "react";
import {
  StyleSheet,
  Text,
  TextInput,
  TextInputProps,
  TouchableOpacity,
  View,
  ViewStyle,
  StyleProp,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";

type Props = TextInputProps & {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: keyof typeof Ionicons.glyphMap;
  rightIcon?: keyof typeof Ionicons.glyphMap;
  onRightIconPress?: () => void;
  containerStyle?: StyleProp<ViewStyle>;
};

const InputField = forwardRef<TextInput, Props>(
  (
    {
      label,
      error,
      hint,
      leftIcon,
      rightIcon,
      onRightIconPress,
      containerStyle,
      secureTextEntry,
      ...textInputProps
    },
    ref
  ) => {
    const [isFocused, setIsFocused] = useState(false);
    const [isPasswordVisible, setIsPasswordVisible] = useState(false);

    const isPassword = secureTextEntry !== undefined;
    const showPassword = isPassword && isPasswordVisible;

    const borderColor = error
      ? colors.danger
      : isFocused
        ? colors.accentBlue
        : colors.surfaceBorder;

    return (
      <View style={[styles.container, containerStyle]}>
        {label && <Text style={styles.label}>{label}</Text>}

        <View style={[styles.inputContainer, { borderColor }]}>
          {leftIcon && (
            <Ionicons
              name={leftIcon}
              size={20}
              color={colors.textTertiary}
              style={styles.leftIcon}
            />
          )}

          <TextInput
            ref={ref}
            style={[
              styles.input,
              leftIcon && styles.inputWithLeftIcon,
              (rightIcon || isPassword) && styles.inputWithRightIcon,
            ]}
            placeholderTextColor={colors.textTertiary}
            selectionColor={colors.accentBlue}
            secureTextEntry={isPassword && !showPassword}
            onFocus={(e) => {
              setIsFocused(true);
              textInputProps.onFocus?.(e);
            }}
            onBlur={(e) => {
              setIsFocused(false);
              textInputProps.onBlur?.(e);
            }}
            {...textInputProps}
          />

          {isPassword ? (
            <TouchableOpacity
              style={styles.rightIconTouchable}
              onPress={() => setIsPasswordVisible(!isPasswordVisible)}
              accessibilityLabel={showPassword ? "Şifreyi gizle" : "Şifreyi göster"}
            >
              <Ionicons
                name={showPassword ? "eye-off-outline" : "eye-outline"}
                size={20}
                color={colors.textTertiary}
              />
            </TouchableOpacity>
          ) : rightIcon ? (
            <TouchableOpacity
              style={styles.rightIconTouchable}
              onPress={onRightIconPress}
              disabled={!onRightIconPress}
            >
              <Ionicons name={rightIcon} size={20} color={colors.textTertiary} />
            </TouchableOpacity>
          ) : null}
        </View>

        {error && (
          <View style={styles.errorContainer}>
            <Ionicons name="alert-circle" size={14} color={colors.danger} />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {hint && !error && <Text style={styles.hintText}>{hint}</Text>}
      </View>
    );
  }
);

InputField.displayName = "InputField";
export default InputField;

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.md,
  },
  label: {
    color: colors.textSecondary,
    fontSize: 14,
    fontWeight: "600",
    marginBottom: spacing.sm,
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1.5,
    borderRadius: radius.md,
    minHeight: 52,
  },
  input: {
    flex: 1,
    color: colors.textPrimary,
    fontSize: 16,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
  },
  inputWithLeftIcon: {
    paddingLeft: spacing.xs,
  },
  inputWithRightIcon: {
    paddingRight: spacing.xs,
  },
  leftIcon: {
    marginLeft: spacing.md,
  },
  rightIconTouchable: {
    padding: spacing.md,
  },
  errorContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: spacing.xs,
  },
  errorText: {
    color: colors.danger,
    fontSize: 12,
    marginLeft: spacing.xs,
  },
  hintText: {
    color: colors.textTertiary,
    fontSize: 12,
    marginTop: spacing.xs,
  },
});
