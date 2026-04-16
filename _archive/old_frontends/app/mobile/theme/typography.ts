// app/mobile/theme/typography.ts
import { TextStyle } from "react-native";

export const typography: Record<string, TextStyle> = {
  heroLarge: { fontSize: 52, fontWeight: "900", letterSpacing: -1, lineHeight: 58 },
  heroMedium: { fontSize: 40, fontWeight: "900", letterSpacing: -0.5, lineHeight: 46 },
  h1: { fontSize: 28, fontWeight: "900", letterSpacing: 0.3 },
  h2: { fontSize: 22, fontWeight: "800", letterSpacing: 0.2 },
  h3: { fontSize: 18, fontWeight: "800", letterSpacing: 0.2 },
  body: { fontSize: 15, fontWeight: "400", lineHeight: 22 },
  bodyBold: { fontSize: 15, fontWeight: "700" },
  caption: { fontSize: 12, fontWeight: "600", letterSpacing: 0.5 },
  label: { fontSize: 11, fontWeight: "700", letterSpacing: 1.5, textTransform: "uppercase" },
  stat: { fontSize: 24, fontWeight: "800" },
} as const;