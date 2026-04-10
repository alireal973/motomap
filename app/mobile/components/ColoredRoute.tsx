import React, { useMemo } from "react";
import { View, Text, StyleSheet } from "react-native";
import { Polyline, Marker } from "react-native-maps";
import { colors } from "../theme";

export type RouteSegment = {
  segment_id: number;
  start_lat: number;
  start_lng: number;
  end_lat: number;
  end_lng: number;
  safety_level: "safe" | "caution" | "limited" | "dangerous";
  lane_split_suitable: boolean;
  color_hex: string;
  stroke_width: number;
  opacity: number;
};

type Props = {
  segments: RouteSegment[];
  showLaneSplitMarkers?: boolean;
  showLegend?: boolean;
  onSegmentPress?: (segment: RouteSegment) => void;
};

const SAFETY_COLORS = {
  safe: "#22C55E",
  caution: "#F59E0B",
  limited: "#F97316",
  dangerous: "#EF4444",
};

export function ColoredRoute({ segments, showLaneSplitMarkers = true, showLegend, onSegmentPress }: Props) {
  const groups = useMemo(() => {
    const result: { color: string; coords: { latitude: number; longitude: number }[]; width: number; segs: RouteSegment[] }[] = [];
    let current: (typeof result)[0] | null = null;

    for (const seg of segments) {
      const coord = { latitude: seg.start_lat, longitude: seg.start_lng };
      if (current && current.color === seg.color_hex) {
        current.coords.push(coord);
        current.segs.push(seg);
      } else {
        if (current) {
          const last = current.segs[current.segs.length - 1];
          current.coords.push({ latitude: last.end_lat, longitude: last.end_lng });
          result.push(current);
        }
        current = { color: seg.color_hex, coords: [coord], width: seg.stroke_width, segs: [seg] };
      }
    }
    if (current) {
      const last = current.segs[current.segs.length - 1];
      current.coords.push({ latitude: last.end_lat, longitude: last.end_lng });
      result.push(current);
    }
    return result;
  }, [segments]);

  const markers = useMemo(() => {
    if (!showLaneSplitMarkers) return [];
    const m: { coord: { latitude: number; longitude: number }; type: "start" | "end" }[] = [];
    let prev = false;
    for (const seg of segments) {
      if (seg.lane_split_suitable && !prev) {
        m.push({ coord: { latitude: seg.start_lat, longitude: seg.start_lng }, type: "start" });
      } else if (!seg.lane_split_suitable && prev) {
        m.push({ coord: { latitude: seg.start_lat, longitude: seg.start_lng }, type: "end" });
      }
      prev = seg.lane_split_suitable;
    }
    return m;
  }, [segments, showLaneSplitMarkers]);

  return (
    <>
      {groups.map((g, i) => (
        <Polyline
          key={`route-${i}`}
          coordinates={g.coords}
          strokeColor={g.color}
          strokeWidth={g.width}
          lineCap="round"
          lineJoin="round"
          tappable={!!onSegmentPress}
          onPress={() => onSegmentPress?.(g.segs[0])}
        />
      ))}
      {markers.map((m, i) => (
        <Marker key={`lane-${i}`} coordinate={m.coord} anchor={{ x: 0.5, y: 0.5 }}>
          <View style={[styles.marker, m.type === "start" ? styles.markerStart : styles.markerEnd]}>
            <Text style={styles.markerText}>{m.type === "start" ? "\u2702\uFE0F" : "\uD83D\uDEAB"}</Text>
          </View>
        </Marker>
      ))}
      {showLegend && <RouteLegend />}
    </>
  );
}

function RouteLegend() {
  return (
    <View style={styles.legend}>
      {(["safe", "caution", "limited", "dangerous"] as const).map((level) => (
        <View key={level} style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: SAFETY_COLORS[level] }]} />
          <Text style={styles.legendText}>
            {{ safe: "Guvenli", caution: "Dikkatli", limited: "Sinirli", dangerous: "Tehlikeli" }[level]}
          </Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  marker: { width: 26, height: 26, borderRadius: 13, justifyContent: "center", alignItems: "center" },
  markerStart: { backgroundColor: "#22C55E" },
  markerEnd: { backgroundColor: "#EF4444" },
  markerText: { fontSize: 13 },
  legend: {
    position: "absolute", bottom: 120, left: 16,
    backgroundColor: "rgba(8,28,80,0.9)", borderRadius: 12, padding: 12,
  },
  legendItem: { flexDirection: "row", alignItems: "center", marginBottom: 6 },
  legendDot: { width: 14, height: 4, borderRadius: 2, marginRight: 8 },
  legendText: { color: colors.textPrimary, fontSize: 12 },
});
