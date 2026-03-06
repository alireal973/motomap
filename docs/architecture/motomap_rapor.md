[![Language: English Companion](https://img.shields.io/badge/Language-English-1f6feb)](motomap_rapor.md)
[![Source: Turkish PDF](https://img.shields.io/badge/Source-Turkish%20PDF-c92a2a)](motomap_rapor.pdf)

# MOTOMAP Report

This page is the English companion for the Turkish PDF report [motomap_rapor.pdf](motomap_rapor.pdf).

## Title and Scope

**Original title:** MOTOMAP: Motorcycle-Focused Intelligent Route Optimization Engine
**Subtitle:** Algorithm Validation, System Architecture, and Benchmark Report
**Authors:** Ali Ozuysal, Muhammet Yagcioglu
**Date:** March 5, 2026

## Abstract

MOTOMAP performs motorcycle-specific route optimization by combining lane-filtering logic, engine-displacement-aware grade penalties, and curve-risk analysis. The report states that the current benchmark achieved:

- Valhalla baseline: `18/20` full passes, or `90%`
- Google baseline: `16/20` full passes, or `80%`

## Core Mathematical Model

The routing engine minimizes a composite edge weight:

$$
W(e) = T_{moto}(e) \cdot C_{highway}(e) \cdot C_{grade}(e) \cdot C_{mode}(e)
$$

Main model components:

- `T_moto(e)`: effective motorcycle travel time
- `C_highway(e)`: legal highway-access multiplier, including infinite penalty for disallowed segments
- `C_grade(e)`: engine-size-sensitive slope penalty
- `C_mode(e)`: mode-specific multiplier for standard, twisty, or safe riding

### Lane-filtering speed model

When car speed is very low, motorcycle speed is boosted according to forward lane count. The model applies higher effective speed for roads with two or more forward lanes, which reflects the ability to filter through dense traffic.

### Engine-displacement grade penalty

The report defines tiered penalties by both absolute grade and engine class:

- `<= 50cc`: strongest penalties on steep grades and no motorway access
- `50cc < CC < 250cc`: medium grade penalties
- `>= 250cc`: mild penalties, only on the steepest grades

### Curve analysis

The curve pipeline samples the road geometry every `10 m`, computes turning angles from consecutive vectors, and classifies segments as:

- fun: `15°` to `45°`
- dangerous: `> 60°`
- hairpin: dangerous turn plus short local spacing

A segment becomes high risk when a hairpin is combined with a steep downhill grade.

## Riding Modes

The report defines three route modes:

- `standard`: minimize total motorcycle travel time
- `viraj keyfi` / twisty: reward curvature and fun-road density while still penalizing risk
- `safe`: aggressively penalize steep descents, dangerous curves, and high-risk segments

## System Architecture

The documented processing pipeline is:

1. `data_loader`
2. `elevation`
3. `osm_validator`
4. `data_cleaner`
5. `curve_risk`
6. `add_travel_time`
7. mode-specific cost builder
8. `router`

The report also documents an elevation fallback chain:

1. Google Elevation API, up to three attempts
2. OpenTopo Data API, up to three attempts
3. degrade mode with default node elevation values

## Algorithmic Complexity

The route computation loop performs:

- per-edge preprocessing
- optional curve-risk enrichment for non-standard modes
- per-edge mode-cost construction
- Dijkstra on toll-permitted and toll-free candidate graphs

The stated total complexity remains in:

$$
O(|E| + |V| \log |V|)
$$

## Benchmark Results

### Kadikoy micro benchmark

For 20 origin-destination pairs:

| Metric | Google v4 | Valhalla v1 |
|---|---:|---:|
| Full pass | `16/20 (80%)` | `18/20 (90%)` |
| Average score | `6.75 / 7` | `6.90 / 7` |
| `baseline_route_exists` failures | `0` | `0` |
| `all_modes_exist` failures | `0` | `0` |
| `modes_are_different` failures | `2` | `2` |
| `safe_risk_le_standard` failures | `0` | `0` |
| `viraj_fun_ge_standard` failures | `0` | `0` |
| `std_distance_vs_baseline` failures | `2` | `0` |
| `std_time_vs_baseline` failures | `1` | `0` |

### Deep-dive examples

The report highlights sample cases 07 and 12, where Google failed the distance ratio check but Valhalla stayed much closer to the MotoMap output. The practical takeaway is that Valhalla produced stronger baseline alignment for these evaluation pairs.

## Trade-off Table

The report summarizes the expected trade-offs by mode:

| Mode | Objective | Travel time | Distance | Fun curves | High risk |
|---|---|---|---|---|---|
| Standard | minimize travel time | lowest | short | random | medium/high |
| Twisty | maximize fun-road density | about `+40%` | about `+20%` | highest | relative |
| Safe | minimize risk and steep downhill exposure | about `+15%` | about `+10%` | low | `0` in the target test scenario |

## Test Coverage

The report lists unit tests for:

- toll-permitted versus toll-free route selection
- forced toll exclusion
- no-route conditions
- twisty-mode route preference
- safe-mode risky-edge avoidance
- low-CC motorway avoidance
- grade sensitivity by engine class
- short motorway-adjacent shortcut penalties

## Key Takeaways

- The routing model is no longer only time-based; it is motorcycle-aware.
- Safe and twisty modes are separated by explicit, testable cost functions.
- The elevation fallback chain is a deliberate resilience mechanism, not an afterthought.
- Valhalla currently looks like the stronger baseline compared with Google for this benchmark set.
