import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Marker, Callout } from "react-native-maps";
import { colors, spacing, radius } from "../theme";

export type ReportType =
  | "oil_spill" | "debris" | "pothole" | "construction"
  | "traffic_light" | "electrical"
  | "wet" | "ice" | "fog" | "sand" | "leaves"
  | "heavy_traffic" | "accident" | "police" | "road_closure"
  | "gas_station" | "moto_shop" | "parking" | "scenic" | "cafe";

export type RoadReport = {
  id: string;
  latitude: number;
  longitude: number;
  type: ReportType;
  title?: string;
  description?: string;
  severity: "low" | "medium" | "high" | "critical";
  upvote_count: number;
  downvote_count: number;
  is_verified: boolean;
  created_at: string;
};

const REPORT_ICONS: Record<ReportType, string> = {
  oil_spill: "\uD83D\uDEE2\uFE0F",
  debris: "\uD83E\uDEA8",
  pothole: "\uD83D\uDD73\uFE0F",
  construction: "\uD83D\uDEA7",
  traffic_light: "\uD83D\uDEA6",
  electrical: "\u26A1",
  wet: "\uD83D\uDCA7",
  ice: "\u2744\uFE0F",
  fog: "\uD83C\uDF2B\uFE0F",
  sand: "\uD83C\uDFDC\uFE0F",
  leaves: "\uD83C\uDF42",
  heavy_traffic: "\uD83D\uDE99",
  accident: "\uD83D\uDEA8",
  police: "\uD83D\uDC6E",
  road_closure: "\uD83D\uDED1",
  gas_station: "\u26FD",
  moto_shop: "\uD83D\uDD27",
  parking: "\uD83C\uDD7F\uFE0F",
  scenic: "\uD83D\uDCF8",
  cafe: "\u2615",
};

const TYPE_TR: Record<ReportType, string> = {
  oil_spill: "Yag Dokuntusi",
  debris: "Dokuntu/Tas",
  pothole: "Cukur",
  construction: "Insaat",
  traffic_light: "Isik Arizasi",
  electrical: "Elektrik Tehlikesi",
  wet: "Islak Yol",
  ice: "Buzlanma",
  fog: "Sis",
  sand: "Kum/Cakil",
  leaves: "Yaprak",
  heavy_traffic: "Yogun Trafik",
  accident: "Kaza",
  police: "Polis Kontrolu",
  road_closure: "Yol Kapali",
  gas_station: "Benzinlik",
  moto_shop: "Motosiklet Dukkani",
  parking: "Park Yeri",
  scenic: "Manzara",
  cafe: "Motorcu Kafesi",
};

const SEVERITY_COLORS: Record<string, string> = {
  low: colors.info,
  medium: colors.warning,
  high: "#F97316",
  critical: colors.danger,
};

function formatTimeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}dk once`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}s once`;
  return `${Math.floor(hours / 24)}g once`;
}

type Props = {
  report: RoadReport;
  onPress?: (report: RoadReport) => void;
};

export function ReportMarker({ report, onPress }: Props) {
  const icon = REPORT_ICONS[report.type] || "\u26A0\uFE0F";
  const bg = SEVERITY_COLORS[report.severity] || colors.warning;

  return (
    <Marker
      coordinate={{ latitude: report.latitude, longitude: report.longitude }}
      onPress={() => onPress?.(report)}
    >
      <View style={[styles.marker, { backgroundColor: bg }]}>
        <Text style={styles.markerIcon}>{icon}</Text>
        {report.is_verified && (
          <View style={styles.verified}>
            <Text style={styles.verifiedText}>{"\u2713"}</Text>
          </View>
        )}
      </View>
      <Callout tooltip>
        <View style={styles.callout}>
          <Text style={styles.calloutTitle}>
            {icon} {report.title || TYPE_TR[report.type] || report.type}
          </Text>
          {report.description ? (
            <Text style={styles.calloutDesc} numberOfLines={2}>
              {report.description}
            </Text>
          ) : null}
          <View style={styles.calloutRow}>
            <Text style={styles.calloutStat}>
              {"\uD83D\uDC4D"} {report.upvote_count}
            </Text>
            <Text style={styles.calloutStat}>
              {"\uD83D\uDC4E"} {report.downvote_count}
            </Text>
            <Text style={styles.calloutTime}>{formatTimeAgo(report.created_at)}</Text>
          </View>
        </View>
      </Callout>
    </Marker>
  );
}

const styles = StyleSheet.create({
  marker: {
    width: 34, height: 34, borderRadius: 17,
    justifyContent: "center", alignItems: "center",
    borderWidth: 2, borderColor: "#fff",
    shadowColor: "#000", shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3, shadowRadius: 4, elevation: 4,
  },
  markerIcon: { fontSize: 16 },
  verified: {
    position: "absolute", top: -4, right: -4,
    width: 14, height: 14, borderRadius: 7,
    backgroundColor: colors.success,
    justifyContent: "center", alignItems: "center",
  },
  verifiedText: { fontSize: 8, color: "#fff", fontWeight: "bold" },
  callout: {
    backgroundColor: colors.bgSecondary, borderRadius: radius.md,
    padding: spacing.md, minWidth: 200, maxWidth: 280,
  },
  calloutTitle: { fontSize: 14, fontWeight: "700", color: colors.textPrimary, marginBottom: 4 },
  calloutDesc: { fontSize: 13, color: colors.textSecondary, marginBottom: spacing.sm },
  calloutRow: { flexDirection: "row", alignItems: "center" },
  calloutStat: { fontSize: 12, color: colors.textSecondary, marginRight: spacing.md },
  calloutTime: { fontSize: 11, color: colors.textTertiary, marginLeft: "auto" },
});
