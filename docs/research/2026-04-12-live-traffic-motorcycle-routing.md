[![Language: English](https://img.shields.io/badge/Language-English-1f6feb)](2026-04-12-live-traffic-motorcycle-routing.md)

# Live Traffic and Motorcycle Routing Research Note

**Date:** 2026-04-12

## 1. Executive summary

Recent production routing systems and transport-engineering workflows do not rely on a single static speed factor. They usually combine:

1. edge-level live traffic observations such as current speed, free-flow speed, jam level, or speed categories,
2. directional capacity and volume logic for congestion,
3. context-aware penalties for maneuvers that are only valid in low-speed mixed traffic,
4. weather and incident safety modifiers,
5. explicit cache or state invalidation whenever live traffic updates arrive.

That is the pattern MotoMap now follows.

## 2. What recent sources show

### A. Live traffic feeds are edge- or segment-based, not only OD based

- **Google Routes Preferred** exposes `speedReadingIntervals` with categories such as `NORMAL`, `SLOW`, and `TRAFFIC_JAM` along the returned polyline.
- **HERE Traffic API v7** exposes real-time flow information including current speed and jam factor.
- **TomTom Orbis Traffic Flow** exposes current speed and the difference from free-flow speed in vector flow tiles.

Practical implication:

- routing should accept per-edge live traffic signals directly,
- not just a single global congestion multiplier.

### B. Congestion should still be grounded in link performance logic

FHWA guidance on dynamic traffic assignment emphasizes that dynamic traffic models are sensitive to detailed network inputs and need link-level state updates. Recent BPR research also focuses on improving the classical link function rather than abandoning link-level congestion models outright.

Practical implication:

- keep BPR-style link performance as the planning backbone,
- but allow live observations to override or blend with the model when available.

### C. Motorcycle filtering is a low-speed mixed-traffic maneuver

Recent motorcycle literature and simulation practice do not treat filtering as an unrestricted speed bonus. It depends on congestion, clearance, lateral context, and surrounding vehicle state. SUMO's `SublaneModel` exists precisely because lateral mixed-traffic behavior needs separate treatment from ordinary lane-following. The 2022 study by Promraksa et al. on lane filtering at signalized urban intersections shows that instant speed, side condition, lateral vehicle condition, and vehicle type affect lateral clearance.

Practical implication:

- filtering should activate only in congested, low-speed conditions,
- tunnels, heavy-vehicle presence, narrow lanes, and night conditions should suppress the benefit.

### D. Weather matters twice: speed and risk

For motorcycle routing, weather is not just a UI warning. It changes both expected progress and acceptable maneuver envelope. In practice, weather should:

- reduce effective speed under unsafe conditions,
- and increase route cost in safety-oriented modes.

## 3. Implementation decisions for MotoMap

### 3.1 Directional capacity from lane count

MotoMap now uses directional practical capacity when live flow is available:

$$
\left(\frac{V}{C}\right)_e = \frac{Q_e}{n_{fwd,e} \cdot c_{lane,e}}
$$

where:

- $Q_e$ = live directional volume for edge $e$,
- $n_{fwd,e}$ = forward lane count,
- $c_{lane,e}$ = per-lane practical capacity.

This turns `ROAD_CAPACITY_PER_LANE` from a documentation constant into an active routing input.

### 3.2 Blending model-based and observed live speed

MotoMap keeps BPR as the structural model and blends live speed when available:

$$
V^{*}_{car,e} = (1-\lambda_e)\,V^{BPR}_{car,e} + \lambda_e\,V^{live}_{e}
$$

where $\lambda_e \in [0,1]$ is the live-traffic confidence.

Why this matters:

- pure BPR is stable but can lag real conditions,
- pure live speed is reactive but noisy,
- blending is a practical compromise used in real systems.

### 3.3 Context-aware lane filtering

MotoMap now treats filtering as a bounded congestion maneuver:

$$
V_{moto,e} =
\min\!\left(
V^{*}_{car,e} + \Delta_{lane,e}\,m_{weather,e}\,m_{context,e},
\;V_{filter,max}
\right)
$$

with the following constraints:

- only active when congestion is present,
- only active when forward lanes $\ge 2$,
- tunnels suppress filtering,
- night conditions reduce filtering benefit,
- heavy-vehicle share reduces benefit,
- narrow lane widths reduce benefit,
- filtered speed is capped.

### 3.4 Weather-aware route cost

MotoMap now applies weather and incident penalties directly into route cost:

$$
C_{mode,e} = T_e \cdot \left[1 + \omega_{mode}(1-S_e) + \phi_{mode} I_e\right]
$$

where:

- $T_e$ = edge travel time,
- $S_e \in [0,1]$ = edge weather safety score,
- $I_e$ = incident severity,
- $\omega_{mode}$ and $\phi_{mode}$ depend on riding mode.

This allows:

- `standart` to stay pragmatic,
- `viraj_keyfi` to stay fun-oriented but not blind to weather,
- `guvenli` to penalize unsafe open-road segments much more aggressively.

### 3.5 Automatic invalidation for live traffic changes

MotoMap's cache token now includes live traffic and safety attributes such as:

- `vc_ratio`,
- live speed and live volume,
- provider speed categories,
- weather safety score,
- lane-splitting modifier,
- incident severity,
- tunnel and lane-width context.

So traffic changes now force travel-time recomputation automatically instead of requiring manual cache clearing.

## 4. Engineering trade-offs

This is still not a full microscopic simulator or city-scale DTA package. It remains a production-oriented route-cost model.

It now sits in a stronger middle ground:

- better than a static motorcycle-aware router,
- much lighter than SUMO-scale microsimulation,
- compatible with current traffic feeds from Google, HERE, or TomTom,
- and much closer to real mixed-traffic motorcycle behavior.

## 5. Practical next steps

1. Add a provider adapter that map-matches Google/HERE/TomTom traffic segments onto OSM edges.
2. Store `traffic_speed_kmh`, `traffic_volume_vph`, `traffic_confidence`, and optional `incident_severity` per edge.
3. Push weather assessments to the graph before routing when the forecast is refreshed.
4. Calibrate confidence and weather weights on real rider traces or pilot telemetry.
5. If needed later, use SUMO `SublaneModel` as an offline calibration environment instead of trying to run microsimulation in the request path.

## 6. Internet sources

1. Google Maps Platform, "Request Traffic Information on the Polyline"  
   https://developers.google.com/maps/documentation/routes_preferred/traffic_on_polylines
2. HERE, "Traffic API v7"  
   https://docs.here.com/here-traffic-api
3. TomTom Developer Portal, "Vector Flow Tiles"  
   https://developer.tomtom.com/traffic-api/documentation/tomtom-orbis-maps/traffic-flow/vector-flow-tiles
4. FHWA, "Traffic Analysis Toolbox Volume XIV: Guidebook on the Utilization of Dynamic Traffic Assignment in Modeling"  
   https://ops.fhwa.dot.gov/publications/fhwahop13015/sec6.htm
5. SUMO Documentation, "Simulation" and `SublaneModel`  
   https://sumo.dlr.de/daily/userdoc/Simulation/
6. SafeTREC, "2024 Traffic Safety Facts: Motorcycle Safety"  
   https://safetrec.berkeley.edu/2024-safetrec-traffic-safety-facts-motorcycle-safety
7. TRID record for Promraksa et al. (2022), "Lane-filtering behavior of motorcycle riders at signalized urban intersections"  
   https://trid.trb.org/View/2015883
8. TRID record for Gore et al. (2023), "Modified Bureau of Public Roads Link Function"  
   https://trid.trb.org/View/2083568
