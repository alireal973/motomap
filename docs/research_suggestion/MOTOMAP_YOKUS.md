[![Language: English Companion](https://img.shields.io/badge/Language-English-1f6feb)](MOTOMAP_YOKUS.md)
[![Source: Turkish PDF](https://img.shields.io/badge/Source-Turkish%20PDF-c92a2a)](MOTOMAP_YOKUŞ.pdf)
[![Source: Turkish Text](https://img.shields.io/badge/Source-Turkish%20Text-c92a2a)](MOTOMAP_YOKUS.txt)

# MotoMap: Topography- and Engine-Power-Aware Route Optimization

This page is the English companion for the Turkish note stored as [MOTOMAP_YOKUŞ.pdf](MOTOMAP_YOKUŞ.pdf) and [MOTOMAP_YOKUS.txt](MOTOMAP_YOKUS.txt).

**Author:** Ali Ozuysal
**Institution:** Izmir Institute of Technology
**Date:** December 11, 2025

## Abstract

This note studies how the MotoMap algorithm makes routing decisions not only from traffic data, but also from road topography and motorcycle capability. In a simulation from Besiktas to Gayrettepe in Istanbul, the algorithm rejects the short but steep climb for a `50cc` scooter and instead chooses a route that is about `40%` longer but much flatter. For a larger motorcycle, it keeps the shortest and steepest route.

## Problem Framing

Traditional navigation systems mostly behave as if every road vehicle has similar climbing ability. That assumption breaks down for:

- `50cc` scooters
- low-power electric mopeds
- other small-displacement motorcycles that struggle on grades above roughly `10%`

The note uses the Besiktas to Gayrettepe corridor as a simple but meaningful test case because it represents a real short-distance climb from sea level to higher urban elevation.

## Method

### Virtual grade injection

Instead of starting with full real elevation coverage, the note first validates the decision logic using a controlled synthetic setup:

- the shortest reference route through Barbaros Boulevard is assigned an artificial grade of `15%`
- alternate roads are assigned a mild grade of `2%`

This makes the routing decision interpretable: if the router is truly engine-aware, it should avoid the steep corridor only for weak motorcycles.

### Engine-specific speed logic

For a `50cc` bike, the note proposes:

$$
V_{50cc} =
\begin{cases}
10 \text{ km/h} & \text{if grade} > 8\% \\
50 \text{ km/h} & \text{if grade} \le 8\%
\end{cases}
$$

Meaning:

- on steep roads the scooter effectively bogs down
- the resulting travel time and fuel cost rise sharply
- the optimizer should therefore avoid that edge when a flatter alternative exists

## Results

The note reports the following simulated comparison:

| Vehicle profile | Total distance | Average grade | Routing behavior |
|---|---:|---:|---|
| Maxi motorcycle (`> 50cc`) | `2.48 km` | `15.0%` steep | chooses the shortest route |
| `50cc` scooter | `3.46 km` | `2.5%` mild | accepts a longer route to avoid the climb |

Behavioral interpretation:

- the larger motorcycle uses the direct climb because torque is assumed to be sufficient
- the `50cc` scooter is redirected through flatter streets such as the Ihlamur Valley and Yildiz area
- the route becomes longer by around `1 km`, but it better respects the physical limits of the vehicle

## Conclusion

The note claims that MotoMap can analyze:

1. topographic road difficulty
2. motorcycle engine capacity
3. route trade-offs between time and mechanical feasibility

The main point is not simply "avoid hills." It is that the same road should be weighted differently for different motorcycle classes.

## Code Artifact

The Turkish source includes a Python example built around:

- `osmnx`
- `networkx`
- `folium`

The script:

1. downloads a local road graph around the study corridor
2. injects synthetic grade values into edges
3. computes separate costs for `50cc` and larger motorcycles
4. solves the shortest path under each cost model
5. prepares the result for map visualization

## Why This Matters for MOTOMAP

This note is the clearest early rationale for MotoMap's later engine-displacement-aware routing:

- a shortest path is not always a practical path
- steep grades need vehicle-class penalties
- motorcycle routing should adapt to the rider's machine rather than assuming a generic motor vehicle
