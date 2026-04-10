// app/mobile/components/Toast.tsx
import { createContext, useContext, useState, useCallback, ReactNode, useEffect } from "react";
import {
  Animated,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius } from "../theme";

type ToastType = "success" | "error" | "warning" | "info";

type ToastConfig = {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
  action?: {
    label: string;
    onPress: () => void;
  };
};

type ToastContextType = {
  showToast: (config: Omit<ToastConfig, "id">) => void;
  hideToast: (id: string) => void;
};

const ToastContext = createContext<ToastContextType | null>(null);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}

const ICON_MAP: Record<ToastType, keyof typeof Ionicons.glyphMap> = {
  success: "checkmark-circle",
  error: "close-circle",
  warning: "warning",
  info: "information-circle",
};

const COLOR_MAP: Record<ToastType, string> = {
  success: colors.success,
  error: colors.danger,
  warning: colors.warning,
  info: colors.info,
};

function ToastItem({
  toast,
  onHide,
}: {
  toast: ToastConfig;
  onHide: () => void;
}) {
  const fadeAnim = useState(new Animated.Value(0))[0];
  const translateY = useState(new Animated.Value(-20))[0];

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 250,
        useNativeDriver: true,
      }),
      Animated.timing(translateY, {
        toValue: 0,
        duration: 250,
        useNativeDriver: true,
      }),
    ]).start();

    const timer = setTimeout(() => {
      handleHide();
    }, toast.duration || 4000);

    return () => clearTimeout(timer);
  }, []);

  const handleHide = () => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }),
      Animated.timing(translateY, {
        toValue: -20,
        duration: 200,
        useNativeDriver: true,
      }),
    ]).start(() => onHide());
  };

  return (
    <Animated.View
      style={[
        styles.toast,
        {
          opacity: fadeAnim,
          transform: [{ translateY }],
          borderLeftColor: COLOR_MAP[toast.type],
        },
      ]}
    >
      <Ionicons
        name={ICON_MAP[toast.type]}
        size={22}
        color={COLOR_MAP[toast.type]}
        style={styles.icon}
      />
      <Text style={styles.message} numberOfLines={2}>
        {toast.message}
      </Text>
      {toast.action && (
        <TouchableOpacity
          onPress={() => {
            toast.action?.onPress();
            handleHide();
          }}
          style={styles.actionButton}
        >
          <Text style={styles.actionText}>{toast.action.label}</Text>
        </TouchableOpacity>
      )}
      <TouchableOpacity onPress={handleHide} style={styles.closeButton}>
        <Ionicons name="close" size={18} color={colors.textTertiary} />
      </TouchableOpacity>
    </Animated.View>
  );
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastConfig[]>([]);

  const showToast = useCallback((config: Omit<ToastConfig, "id">) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { ...config, id }]);
  }, []);

  const hideToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast, hideToast }}>
      {children}
      <View style={styles.container} pointerEvents="box-none">
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onHide={() => hideToast(toast.id)} />
        ))}
      </View>
    </ToastContext.Provider>
  );
}

// Convenience hooks for specific toast types
export function useSuccessToast() {
  const { showToast } = useToast();
  return useCallback(
    (message: string, action?: ToastConfig["action"]) =>
      showToast({ message, type: "success", action }),
    [showToast]
  );
}

export function useErrorToast() {
  const { showToast } = useToast();
  return useCallback(
    (message: string, action?: ToastConfig["action"]) =>
      showToast({ message, type: "error", duration: 5000, action }),
    [showToast]
  );
}

export function useWarningToast() {
  const { showToast } = useToast();
  return useCallback(
    (message: string, action?: ToastConfig["action"]) =>
      showToast({ message, type: "warning", action }),
    [showToast]
  );
}

export function useInfoToast() {
  const { showToast } = useToast();
  return useCallback(
    (message: string, action?: ToastConfig["action"]) =>
      showToast({ message, type: "info", action }),
    [showToast]
  );
}

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    top: 60,
    left: spacing.md,
    right: spacing.md,
    zIndex: 9999,
    gap: spacing.sm,
  },
  toast: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.bgSecondary,
    borderRadius: radius.md,
    borderLeftWidth: 4,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  icon: {
    marginRight: spacing.sm,
  },
  message: {
    flex: 1,
    color: colors.textPrimary,
    fontSize: 14,
    fontWeight: "500",
  },
  actionButton: {
    marginLeft: spacing.sm,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  actionText: {
    color: colors.accentBlue,
    fontSize: 14,
    fontWeight: "700",
  },
  closeButton: {
    marginLeft: spacing.xs,
    padding: spacing.xs,
  },
});
