// app/mobile/app/(tabs)/_layout.tsx
import { Tabs } from "expo-router";
import { StyleSheet, Text, View } from "react-native";
import { colors } from "../../theme";

function TabIcon({ icon, label, focused }: { icon: string; label: string; focused: boolean }) {
  return (
    <View style={styles.tabItem}>
      <Text style={[styles.tabIcon, focused && styles.tabIconActive]}>
        {icon}
      </Text>
      <Text style={[styles.tabLabel, focused && styles.tabLabelActive]}>
        {label}
      </Text>
    </View>
  );
}

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarShowLabel: false,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon icon={"\u{1F3E0}"} label="Ana Sayfa" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="route"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon icon={"\u{1F9ED}"} label="Rota" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="map"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon icon={"\u{1F5FA}\uFE0F"} label="Harita" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="garage"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon icon={"\u{1F527}"} label="Garaj" focused={focused} />
          ),
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: colors.bgSecondary,
    borderTopWidth: 1,
    borderTopColor: colors.surfaceBorder,
    height: 70,
    paddingTop: 8,
    paddingBottom: 12,
  },
  tabItem: {
    alignItems: "center",
    gap: 3,
  },
  tabIcon: {
    fontSize: 22,
    opacity: 0.45,
  },
  tabIconActive: {
    opacity: 1,
  },
  tabLabel: {
    fontSize: 10,
    fontWeight: "600",
    color: colors.textTertiary,
    letterSpacing: 0.3,
  },
  tabLabelActive: {
    color: colors.accentBlue,
  },
});