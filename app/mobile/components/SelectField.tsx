// app/mobile/components/SelectField.tsx
import { useState } from "react";
import {
  FlatList,
  Modal,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  ViewStyle,
  StyleProp,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";

export type SelectOption<T = string> = {
  label: string;
  value: T;
  icon?: keyof typeof Ionicons.glyphMap;
};

type Props<T = string> = {
  label?: string;
  placeholder?: string;
  options: SelectOption<T>[];
  value?: T;
  onSelect: (value: T) => void;
  error?: string;
  disabled?: boolean;
  containerStyle?: StyleProp<ViewStyle>;
  modalTitle?: string;
};

export default function SelectField<T extends string | number = string>({
  label,
  placeholder = "Seçiniz...",
  options,
  value,
  onSelect,
  error,
  disabled = false,
  containerStyle,
  modalTitle,
}: Props<T>) {
  const [isOpen, setIsOpen] = useState(false);

  const selectedOption = options.find((opt) => opt.value === value);

  const borderColor = error
    ? colors.danger
    : isOpen
      ? colors.accentBlue
      : colors.surfaceBorder;

  const handleSelect = (option: SelectOption<T>) => {
    onSelect(option.value);
    setIsOpen(false);
  };

  return (
    <View style={[styles.container, containerStyle]}>
      {label && <Text style={styles.label}>{label}</Text>}

      <TouchableOpacity
        style={[styles.selectButton, { borderColor }, disabled && styles.disabled]}
        onPress={() => !disabled && setIsOpen(true)}
        activeOpacity={0.85}
        accessibilityRole="button"
        accessibilityLabel={label || placeholder}
      >
        {selectedOption?.icon && (
          <Ionicons
            name={selectedOption.icon}
            size={20}
            color={colors.textSecondary}
            style={styles.selectedIcon}
          />
        )}
        <Text
          style={[
            styles.selectText,
            !selectedOption && styles.placeholderText,
          ]}
          numberOfLines={1}
        >
          {selectedOption?.label || placeholder}
        </Text>
        <Ionicons
          name={isOpen ? "chevron-up" : "chevron-down"}
          size={20}
          color={colors.textTertiary}
        />
      </TouchableOpacity>

      {error && (
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={14} color={colors.danger} />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      <Modal
        visible={isOpen}
        transparent
        animationType="fade"
        onRequestClose={() => setIsOpen(false)}
      >
        <TouchableOpacity
          style={styles.modalOverlay}
          activeOpacity={1}
          onPress={() => setIsOpen(false)}
        >
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{modalTitle || label || "Seçim Yapın"}</Text>
              <TouchableOpacity
                onPress={() => setIsOpen(false)}
                accessibilityLabel="Kapat"
              >
                <Ionicons name="close" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <FlatList
              data={options}
              keyExtractor={(item) => String(item.value)}
              renderItem={({ item }) => (
                <TouchableOpacity
                  style={[
                    styles.optionItem,
                    item.value === value && styles.optionItemSelected,
                  ]}
                  onPress={() => handleSelect(item)}
                  activeOpacity={0.7}
                >
                  {item.icon && (
                    <Ionicons
                      name={item.icon}
                      size={20}
                      color={item.value === value ? colors.accentBlue : colors.textSecondary}
                      style={styles.optionIcon}
                    />
                  )}
                  <Text
                    style={[
                      styles.optionText,
                      item.value === value && styles.optionTextSelected,
                    ]}
                  >
                    {item.label}
                  </Text>
                  {item.value === value && (
                    <Ionicons name="checkmark" size={20} color={colors.accentBlue} />
                  )}
                </TouchableOpacity>
              )}
              showsVerticalScrollIndicator={false}
              style={styles.optionsList}
            />
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
}

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
  selectButton: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1.5,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    minHeight: 52,
  },
  disabled: {
    opacity: 0.5,
  },
  selectedIcon: {
    marginRight: spacing.sm,
  },
  selectText: {
    flex: 1,
    color: colors.textPrimary,
    fontSize: 16,
  },
  placeholderText: {
    color: colors.textTertiary,
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
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.7)",
    justifyContent: "center",
    alignItems: "center",
    padding: spacing.lg,
  },
  modalContent: {
    backgroundColor: colors.bgSecondary,
    borderRadius: radius.lg,
    width: "100%",
    maxHeight: "70%",
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
  },
  modalHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.surfaceBorder,
  },
  modalTitle: {
    color: colors.textPrimary,
    fontSize: 18,
    fontWeight: "700",
  },
  optionsList: {
    maxHeight: 400,
  },
  optionItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderBottomWidth: 1,
    borderBottomColor: colors.surfaceBorder,
  },
  optionItemSelected: {
    backgroundColor: colors.surfaceGlass,
  },
  optionIcon: {
    marginRight: spacing.md,
  },
  optionText: {
    flex: 1,
    color: colors.textPrimary,
    fontSize: 16,
  },
  optionTextSelected: {
    color: colors.accentBlue,
    fontWeight: "600",
  },
});
