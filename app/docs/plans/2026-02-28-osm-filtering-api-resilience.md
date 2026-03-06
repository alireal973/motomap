[![Language: English](https://img.shields.io/badge/Language-English-1f6feb)](2026-02-28-osm-filtering-api-resilience.md)
[![Language: Turkish](https://img.shields.io/badge/Language-Turkish-c92a2a)](2026-02-28-osm-filtering-api-resilience.tr.md)

# OSM Motorcycle Filtering and API Resilience

This file is the English execution summary of the longer Turkish implementation plan preserved in [2026-02-28-osm-filtering-api-resilience.tr.md](2026-02-28-osm-filtering-api-resilience.tr.md).

## Goal

Filter out road segments that are not suitable or legal for motorcycles during OSM ingestion, and harden elevation calls with retries, fallback providers, and degrade-mode behavior.

## Architecture

- add an OSM filtering layer around `data_loader.py` and `data_cleaner.py`
- add retry, backoff, and fallback logic to `elevation.py`
- introduce `motomap.osm_validator` as the reusable filtering module

## Tech Stack

- Python 3.10+
- osmnx 2.1+
- networkx 3.0+
- retry / backoff logic
- structured logging

## Related Issues

- closed: `#3` paid or free road preference
- closed: `#4` curve option and slope handling
- historical plan references: `#5` motorcycle-rule filtering, `#6` OSM plus Google API risk analysis
- currently open via `gh`: `#12` Istanbul cross-continental test, `#13` emergency-lane handling during lane filtering

## Status Analysis

Completed foundation:

- toll and free-route preference work was already delivered
- curve and slope-related groundwork was already delivered

Remaining work in this plan:

- edge-level motorcycle validation
- pipeline integration of the validator
- elevation API resilience and degrade mode
- tag normalization and logging cleanup
- full verification and issue updates

## Mathematical Model

### Road suitability function

For each OSM edge $e$:

$$
\text{valid}(e) = \begin{cases}
0, & \text{highway}(e) \in \mathcal{F} \\
0, & \text{access}(e) = \texttt{no} \lor \text{motor vehicle}(e) = \texttt{no} \\
1, & \text{otherwise}
\end{cases}
$$

Filtered highway set:

$$
\mathcal{F} = \{\texttt{cycleway},\; \texttt{footway},\; \texttt{pedestrian},\; \texttt{path},\; \texttt{steps},\; \texttt{corridor},\; \texttt{bridleway}\}
$$

Valid graph:

$$
G' = (V, E'), \quad E' = \{e \in E \mid \text{valid}(e) = 1\}
$$

### Elevation resilience model

Retry schedule:

$$
t_{\text{wait}}(n) = \min\!\left(t_{\max},\; t_0 \cdot b^{n-1}\right)
$$

Recommended defaults:

- $t_0 = 1s$
- $b = 2$
- $t_{\max} = 30s$
- $N_{\max} = 3$

Fallback chain:

$$
\text{elevation}(v) = \begin{cases}
\text{Google}(v), & \text{if API key is valid and quota is available} \\
\text{OpenTopo}(v), & \text{if Google fails} \\
0, & \text{if all providers fail}
\end{cases}
$$

## Workstream Summary

### 1. OSM validator tests

Create synthetic-graph tests for:

- excluded edge types such as `cycleway`, `footway`, `pedestrian`, `path`, and `steps`
- `access=no` and `motor_vehicle=no`
- node attribute preservation
- expected edge counts after filtering

### 2. OSM validator implementation

Add:

- `EXCLUDED_HIGHWAY_TYPES`
- tag normalization helpers
- `filter_motorcycle_edges(graph)`

Expose it from the public package interface where appropriate.

### 3. Pipeline integration

Insert filtering into the main graph build flow after graph loading and before downstream feature engineering.

Expected effect:

- invalid road edges never reach the cost engine
- tests can assert pipeline behavior instead of isolated function behavior only

### 4. Elevation resilience tests

Cover:

- Google failure with OpenTopo fallback
- all providers failing and entering degrade mode
- numeric elevation attributes after successful enrichment

### 5. Elevation resilience implementation

Add:

- retry loops
- logging on each failed attempt
- OpenTopo fallback
- degrade mode that fills missing node elevations with `0`

### 6. Tag normalization

Verify that list-form OSM tags such as `highway=["primary","secondary"]` are normalized to a single usable string.

### 7. Logging

Add base logging configuration so retries and degraded runs are observable during tests and batch jobs.

### 8. Final verification

Run:

- targeted validator tests
- elevation resilience tests
- the full test suite
- `git status` before push

## Acceptance Checklist

- invalid motorcycle edges are removed from the routing graph
- public pipeline uses the validator
- elevation enrichment survives external API failures
- degrade mode keeps the pipeline usable rather than crashing
- tests cover validator behavior and API fallback behavior

## Detailed Original

If you need the procedural red-green-refactor sequence, exact code examples, or commit-by-commit checklist, use the Turkish original preserved here:

- [Full Turkish plan](2026-02-28-osm-filtering-api-resilience.tr.md)
