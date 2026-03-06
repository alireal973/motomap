[![Language: English Companion](https://img.shields.io/badge/Language-English-1f6feb)](motomap_yokus_ve_viraj_Algoritmasi.md)
[![Source: Turkish PDF](https://img.shields.io/badge/Source-Turkish%20PDF-c92a2a)](motomap_yokus_ve_viraj_Algoritmasi.pdf)
[![Source: Turkish Text](https://img.shields.io/badge/Source-Turkish%20Text-c92a2a)](../issue_4/issue4.txt)

# Route, Curve, and Risk Analysis for Motorcyclists

This page is the English companion for the Turkish research note stored as [motomap_yokus_ve_viraj_Algoritmasi.pdf](motomap_yokus_ve_viraj_Algoritmasi.pdf) and the extracted text copy [../issue_4/issue4.txt](../issue_4/issue4.txt).

## Core Idea

The note argues that a "pleasant" motorcycle route and a "safe" motorcycle route are not the same thing:

- pleasant routes tend to include rhythmic, flowing curves
- safe routes depend on curve radius, visibility, and grade
- the routing engine should not optimize only distance or time; it should include an explicit safety factor

## 1. Dangerous Curve Analysis

For each road segment, the note proposes using three consecutive points `(A, B, C)` and fitting the implied circle through them. The radius of that circle is used as the main curvature signal.

Key rule:

- curves with radius `R < 15-20 m` should usually be treated as narrow or sharp turns

Suggested implementation:

- compute Menger curvature from sampled route geometry
- also track rapid bearing change, because a change larger than `60°` within about `10 m` can indicate a hairpin turn

## 2. Cost-Function Integration

The curve signal should be injected directly into the route cost used by Dijkstra or A*.

### Fun-route mode

Instead of minimizing shortest distance, the router should reward a higher curvature score:

$$
\text{Cost} = \frac{\text{Distance}}{1 + \text{Curve Factor}}
$$

### Safety mode

If the rider prioritizes safety, or if conditions are wet, very sharp turns should receive a strong penalty so the router actively avoids them.

## 3. Grade and Visibility with DEM Integration

The note highlights combined risk instead of single-factor risk. A curve is especially dangerous when:

- the turn radius is small
- the segment is on a steep downhill

The proposed combined hazard condition is:

$$
(R < 20 m) \land (\text{grade} < -8\%)
$$

When both conditions are true, the route segment should be flagged as high risk.

## 4. Data Preparation and Interpolation

Raw user-drawn routes often contain irregularly spaced coordinates, which makes curve analysis unstable. The note recommends resampling the geometry at a constant spacing such as:

- every `5 m`, or
- every `10 m`

Reasoning:

- if points are too sparse, sharp turns are missed
- if points are too dense, GPS noise can make straight roads look curvy

Suggested tool:

- Shapely `interpolate`

## 5. Vector-Angle Method for Fast Online Analysis

For real-time analysis, the note recommends replacing heavier circle-based geometry with vector math.

Given three consecutive points:

$$
\vec V_1 = P_2 - P_1, \qquad \vec V_2 = P_3 - P_2
$$

The angle between these vectors measures how abruptly the road direction changes.

Classification:

- fun curve: `15° < theta < 45°`
- danger zone: `theta > 60°`
- hairpin candidate: danger angle reached over a short local distance such as `20 m`

## 6. Proposed Vectorized Python Workflow

The note includes a NumPy-based function that:

1. resamples the route every `10 m`
2. builds consecutive vectors
3. normalizes them
4. computes turning angles with cosine similarity
5. classifies danger zones and fun zones

That approach is explicitly designed for interactive use instead of offline-only analysis.

## 7. UI and Performance Guidance

Recommended product behavior:

- render dangerous turns in red
- render pleasant curved sections in yellow or orange
- show a short summary card such as "This route contains 12 fun curves and 2 high-risk areas."
- while the user is drawing, analyze only the latest sliding window instead of recomputing the entire route after every new point

## 8. DEM Data Sources

The note lists the common external elevation sources for slope-aware route analysis:

1. SRTM
2. Copernicus GLO-30
3. ASTER GDEM

Slope is computed from elevation difference over segment distance:

$$
\text{Road Grade (\%)} = \frac{\Delta h}{\text{Distance}} \times 100
$$

## Practical Takeaway

This research note is effectively the design rationale for MotoMap's later `curve_risk` and grade-aware safety logic:

- sample geometry consistently
- treat sharp downhill curves as compound hazards
- reward flowing curves in fun mode
- penalize severe curvature in safe mode
- keep the analysis incremental enough for an interactive route-drawing UI
