// app/mobile/app/_layout.tsx
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { AppProvider } from "../context/AppContext";
import { AuthProvider } from "../context/AuthContext";
import { colors } from "../theme";

export default function RootLayout() {
  return (
    <AuthProvider>
      <AppProvider>
        <StatusBar style="light" />
        <Stack
          screenOptions={{
            headerShown: false,
            contentStyle: { backgroundColor: colors.bgPrimary },
            animation: "slide_from_right",
          }}
        >
          <Stack.Screen name="index" />
          <Stack.Screen name="onboarding" />
          <Stack.Screen name="(tabs)" options={{ animation: "fade" }} />
          <Stack.Screen
            name="add-motorcycle"
            options={{ presentation: "modal", animation: "slide_from_bottom" }}
          />
          <Stack.Screen name="saved-routes" />
          <Stack.Screen name="auth/login" options={{ animation: "slide_from_bottom" }} />
          <Stack.Screen name="auth/register" options={{ animation: "slide_from_bottom" }} />
          <Stack.Screen name="report/create" options={{ presentation: "modal", animation: "slide_from_bottom" }} />
          <Stack.Screen name="achievements/index" />
          <Stack.Screen name="settings/index" />
        </Stack>
      </AppProvider>
    </AuthProvider>
  );
}