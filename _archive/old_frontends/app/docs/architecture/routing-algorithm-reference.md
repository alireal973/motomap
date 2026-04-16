# Routing Algorithm Reference

This document is the maintainer-facing reference for [`motomap/algorithm.py`](../../motomap/algorithm.py), the central routing policy module used by the root package and the mirrored `app/` package.

## Purpose

The routing core is responsible for:

- normalizing noisy OSM edge attributes into predictable routing inputs
- filtering edges that are illegal or impractical for motorcycles
- converting road and ferry segments into calibrated travel-time weights
- building mode-specific costs for standard, curvy, and safe riding modes
- computing toll-permitted and toll-free alternatives
- summarizing the selected route into an API-friendly payload

The design goal is that the rest of the project depends on one routing policy surface rather than duplicating rules across loaders, validators, and API code.

## End-to-End Flow

1. Raw OSM edge tags are normalized with parsing helpers such as `safe_float`, `parse_int`, `parse_speed_kmh`, and `parse_duration_s`.
2. Missing defaults are filled with `fill_edge_defaults`.
3. Illegal motorcycle edges are screened with `is_motorcycle_forbidden` and optionally removed with `filter_motorcycle_edges`.
4. Base travel time is computed per edge with `compute_edge_travel_time`.
5. The graph receives travel-time weights through `add_travel_time_to_graph` or the cached variant `ensure_travel_time_to_graph`.
6. Riding-mode penalties and bonuses are layered by `build_mode_specific_cost` or `ensure_mode_specific_cost`.
7. A compact search structure is created by `build_route_search_index`.
8. `shortest_path` runs the indexed bidirectional Dijkstra search.
9. `summarize_route` converts the node path into route metrics.
10. `ucret_opsiyonlu_rota_hesapla` coordinates the full toll-aware routing workflow.

## Data Structures

| Type | Role |
|---|---|
| `RuntimeCalibration` | Holds runtime speed and delay coefficients loaded from environment variables. |
| `RouteSearchIndex` | Stores compact adjacency lists and best-edge lookups for repeated route queries on the same graph revision. |
| `RoutingAlgorithmProfile` | Holds the static routing policy: default speeds, excluded road classes, toll behavior, and mode coefficients. |
| `NoRouteFoundError` | Raised when the selected route preference cannot be satisfied. |

## Function Catalog

### Parsing and normalization helpers

| Function | Responsibility |
|---|---|
| `safe_float` | Converts loose scalar or list-like values into a safe `float`. |
| `parse_int` | Converts loose scalar or list-like values into a safe `int`. |
| `normalize_tag` | Normalizes a scalar tag value to lowercase text. |
| `iter_normalized_values` | Flattens list-like tag values into normalized lowercase tokens. |
| `get_highway_type` | Extracts the primary `highway` classification from edge metadata. |
| `parse_speed_kmh` | Parses `maxspeed`-style values into km/h. |
| `parse_duration_s` | Parses OSM `duration` values into seconds. |

### Cache and graph-state helpers

| Function | Responsibility |
|---|---|
| `_cache_value_token` | Converts edge metadata into stable cache-key fragments. Internal helper. |
| `_graph_cache_token` | Hashes route-relevant graph inputs so cached weights stay valid after in-place edge edits. Internal helper. |
| `compute_lanes_forward` | Derives forward lane count from total lanes and `oneway`. |
| `fill_edge_defaults` | Applies default lane, speed, and surface values and derives `lanes_forward`. |
| `runtime_calibration_from_env` | Loads and clamps runtime speed and delay overrides from environment variables. |

### Filtering and base travel-time layer

| Function | Responsibility |
|---|---|
| `is_toll_edge` | Detects whether an edge is toll-tagged. |
| `is_ferry_edge` | Detects whether an edge is a ferry segment. |
| `is_motorcycle_forbidden` | Applies the motorcycle legality and practicality filter. |
| `filter_motorcycle_edges` | Returns a graph copy containing only valid motorcycle edges. |
| `compute_edge_travel_time` | Converts one edge into calibrated travel time in seconds. |
| `add_travel_time_to_graph` | Writes travel-time weights to every edge and increments the route revision. |
| `ensure_travel_time_to_graph` | Reuses existing travel-time weights when the relevant graph inputs have not changed. |

### Mode weighting and rider constraints

| Function | Responsibility |
|---|---|
| `route_cost_attr` | Maps a riding mode to its stored route-cost edge attribute. |
| `mode_weight_attr` | Returns the active weight attribute used for routing in a given mode. |
| `to_motor_cc` | Normalizes optional engine displacement input. |
| `cc_grade_penalty` | Applies slope penalties based on engine displacement. |
| `cc_highway_penalty` | Applies highway restrictions for very small motorcycles. |
| `build_mode_specific_cost` | Builds edge weights for `standart`, `viraj_keyfi`, or `guvenli` routing. |
| `ensure_mode_specific_cost` | Reuses existing mode weights when graph inputs and rider settings are unchanged. |

### Search and route summarization

| Function | Responsibility |
|---|---|
| `best_edge_data` | Selects the cheapest matching multiedge for one route segment. |
| `build_route_search_index` | Builds the compact indexed adjacency structure used for repeated searches. |
| `_bidirectional_dijkstra` | Internal indexed shortest-path implementation. |
| `shortest_path` | Returns the cheapest node sequence for the selected constraints. |
| `summarize_route` | Aggregates time, distance, ferry, toll, and risk metrics for a node path. |
| `ucret_opsiyonlu_rota_hesapla` | Orchestrates the full toll-aware routing workflow and chooses the final route. |

## Riding Modes

| Mode | Intent | Main behavior |
|---|---|---|
| `standart` | Practical commute routing | Starts from travel time, discourages shortcut-prone service connectors near major roads, and applies engine-size penalties. |
| `viraj_keyfi` | Enjoyable curvy riding | Rewards curvature and fun-turn density while still penalizing dangerous segments. |
| `guvenli` | Risk-aware routing | Penalizes high-risk segments, downhill severity, and unsafe local road types more aggressively. |

## Cache Strategy

The routing module caches two layers:

- travel-time weights via `_motomap_travel_time_state`
- mode-specific weights via `_motomap_mode_cost_state`
- compact search indexes via `_motomap_route_index_cache`

The cache keys include route-relevant graph content, not just edge count. This matters because the code frequently mutates edge attributes in place during preprocessing and benchmarking. Without content-aware cache tokens, repeated calls could return stale routes after an edge length, speed, toll flag, or ferry duration changes.

## Public Entry Point

`ucret_opsiyonlu_rota_hesapla` is the preferred high-level API for production callers. It:

- validates toll preference and riding mode
- resolves engine displacement
- ensures base travel-time weights exist
- ensures mode-specific costs exist
- builds or reuses the route index
- computes both toll-allowed and toll-free candidates
- returns the selected route plus alternatives and profile metadata

Use lower-level helpers directly only when you are integrating custom preprocessing or testing individual policy layers.

## Extension Guidance

When extending the algorithm:

- add new routing policy constants to `RoutingAlgorithmProfile`
- keep graph mutations centralized in the algorithm module
- bump cached state only through `add_travel_time_to_graph` and `build_mode_specific_cost`
- include any new route-relevant edge attributes in `_graph_cache_token`
- add deterministic tests and randomized equivalence tests when changing search logic

## Related Files

- [`motomap/algorithm.py`](../../motomap/algorithm.py)
- [`app/motomap/algorithm.py`](../../app/motomap/algorithm.py)
- [`tests/test_algorithm.py`](../../tests/test_algorithm.py)
- [`app/tests/test_algorithm.py`](../../app/tests/test_algorithm.py)
