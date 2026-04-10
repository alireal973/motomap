// app/mobile/components/DatePicker.tsx
import { useState } from "react";
import {
  Modal,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  ViewStyle,
  StyleProp,
  ScrollView,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";

const MONTHS_TR = [
  "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
  "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
];

const DAYS_TR = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"];

type Props = {
  label?: string;
  value?: Date;
  onChange: (date: Date) => void;
  placeholder?: string;
  error?: string;
  minDate?: Date;
  maxDate?: Date;
  containerStyle?: StyleProp<ViewStyle>;
};

export default function DatePicker({
  label,
  value,
  onChange,
  placeholder = "Tarih seçiniz...",
  error,
  minDate,
  maxDate,
  containerStyle,
}: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [viewDate, setViewDate] = useState(value || new Date());

  const borderColor = error
    ? colors.danger
    : isOpen
      ? colors.accentBlue
      : colors.surfaceBorder;

  const formatDate = (date: Date): string => {
    const day = date.getDate();
    const month = MONTHS_TR[date.getMonth()];
    const year = date.getFullYear();
    return `${day} ${month} ${year}`;
  };

  const getDaysInMonth = (year: number, month: number): number => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (year: number, month: number): number => {
    const day = new Date(year, month, 1).getDay();
    // Convert Sunday=0 to Monday=0 format
    return day === 0 ? 6 : day - 1;
  };

  const handlePrevMonth = () => {
    setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setViewDate(new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 1));
  };

  const handleSelectDay = (day: number) => {
    const selectedDate = new Date(viewDate.getFullYear(), viewDate.getMonth(), day);
    onChange(selectedDate);
    setIsOpen(false);
  };

  const isDateDisabled = (day: number): boolean => {
    const date = new Date(viewDate.getFullYear(), viewDate.getMonth(), day);
    if (minDate && date < minDate) return true;
    if (maxDate && date > maxDate) return true;
    return false;
  };

  const isSelectedDay = (day: number): boolean => {
    if (!value) return false;
    return (
      value.getDate() === day &&
      value.getMonth() === viewDate.getMonth() &&
      value.getFullYear() === viewDate.getFullYear()
    );
  };

  const isToday = (day: number): boolean => {
    const today = new Date();
    return (
      today.getDate() === day &&
      today.getMonth() === viewDate.getMonth() &&
      today.getFullYear() === viewDate.getFullYear()
    );
  };

  const renderCalendar = () => {
    const year = viewDate.getFullYear();
    const month = viewDate.getMonth();
    const daysInMonth = getDaysInMonth(year, month);
    const firstDay = getFirstDayOfMonth(year, month);

    const days: (number | null)[] = [];

    // Empty slots before first day
    for (let i = 0; i < firstDay; i++) {
      days.push(null);
    }

    // Days of month
    for (let d = 1; d <= daysInMonth; d++) {
      days.push(d);
    }

    // Fill remaining slots to complete last row
    while (days.length % 7 !== 0) {
      days.push(null);
    }

    return (
      <View style={styles.calendarGrid}>
        {/* Day headers */}
        {DAYS_TR.map((day) => (
          <View key={day} style={styles.dayHeader}>
            <Text style={styles.dayHeaderText}>{day}</Text>
          </View>
        ))}

        {/* Day cells */}
        {days.map((day, index) => {
          if (day === null) {
            return <View key={`empty-${index}`} style={styles.dayCell} />;
          }

          const disabled = isDateDisabled(day);
          const selected = isSelectedDay(day);
          const today = isToday(day);

          return (
            <TouchableOpacity
              key={day}
              style={[
                styles.dayCell,
                selected && styles.dayCellSelected,
                today && !selected && styles.dayCellToday,
              ]}
              onPress={() => !disabled && handleSelectDay(day)}
              disabled={disabled}
              activeOpacity={0.7}
            >
              <Text
                style={[
                  styles.dayText,
                  selected && styles.dayTextSelected,
                  disabled && styles.dayTextDisabled,
                ]}
              >
                {day}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    );
  };

  return (
    <View style={[styles.container, containerStyle]}>
      {label && <Text style={styles.label}>{label}</Text>}

      <TouchableOpacity
        style={[styles.selectButton, { borderColor }]}
        onPress={() => setIsOpen(true)}
        activeOpacity={0.85}
        accessibilityRole="button"
        accessibilityLabel={label || placeholder}
      >
        <Ionicons
          name="calendar-outline"
          size={20}
          color={colors.textTertiary}
          style={styles.icon}
        />
        <Text style={[styles.selectText, !value && styles.placeholderText]}>
          {value ? formatDate(value) : placeholder}
        </Text>
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
          <View style={styles.modalContent} onStartShouldSetResponder={() => true}>
            {/* Header */}
            <View style={styles.modalHeader}>
              <TouchableOpacity onPress={handlePrevMonth} style={styles.navButton}>
                <Ionicons name="chevron-back" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
              <Text style={styles.monthYearText}>
                {MONTHS_TR[viewDate.getMonth()]} {viewDate.getFullYear()}
              </Text>
              <TouchableOpacity onPress={handleNextMonth} style={styles.navButton}>
                <Ionicons name="chevron-forward" size={24} color={colors.textSecondary} />
              </TouchableOpacity>
            </View>

            {/* Calendar */}
            <ScrollView showsVerticalScrollIndicator={false}>
              {renderCalendar()}
            </ScrollView>

            {/* Footer */}
            <View style={styles.modalFooter}>
              <TouchableOpacity
                style={styles.todayButton}
                onPress={() => {
                  const today = new Date();
                  setViewDate(today);
                  onChange(today);
                  setIsOpen(false);
                }}
              >
                <Text style={styles.todayButtonText}>Bugün</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setIsOpen(false)}
              >
                <Text style={styles.closeButtonText}>Kapat</Text>
              </TouchableOpacity>
            </View>
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
  icon: {
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
    maxWidth: 360,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
    padding: spacing.lg,
  },
  modalHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: spacing.lg,
  },
  navButton: {
    padding: spacing.sm,
  },
  monthYearText: {
    color: colors.textPrimary,
    fontSize: 18,
    fontWeight: "700",
  },
  calendarGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
  },
  dayHeader: {
    width: "14.28%",
    alignItems: "center",
    paddingVertical: spacing.sm,
  },
  dayHeaderText: {
    color: colors.textTertiary,
    fontSize: 12,
    fontWeight: "600",
  },
  dayCell: {
    width: "14.28%",
    aspectRatio: 1,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: radius.sm,
  },
  dayCellSelected: {
    backgroundColor: colors.accentBlue,
  },
  dayCellToday: {
    borderWidth: 1,
    borderColor: colors.accentBlue,
  },
  dayText: {
    color: colors.textPrimary,
    fontSize: 14,
    fontWeight: "500",
  },
  dayTextSelected: {
    color: "#FFFFFF",
    fontWeight: "700",
  },
  dayTextDisabled: {
    color: colors.textTertiary,
    opacity: 0.4,
  },
  modalFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: spacing.lg,
    paddingTop: spacing.md,
    borderTopWidth: 1,
    borderTopColor: colors.surfaceBorder,
  },
  todayButton: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  todayButtonText: {
    color: colors.accentBlue,
    fontSize: 14,
    fontWeight: "600",
  },
  closeButton: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  closeButtonText: {
    color: colors.textSecondary,
    fontSize: 14,
    fontWeight: "600",
  },
});
