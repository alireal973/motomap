[![Language: English Companion](https://img.shields.io/badge/Language-English-1f6feb)](Ali_Ozuysal_Projesi.md)
[![Source: Turkish PDF](https://img.shields.io/badge/Source-Turkish%20PDF-c92a2a)](Ali_Ozuysal_Projesi.pdf)
[![Source: Turkish Text](https://img.shields.io/badge/Source-Turkish%20Text-c92a2a)](Ali_Ozuysal_Projesi.txt)

# MOTOMAP Research Proposal

This page is the English companion for the Turkish TÜBITAK 2209-A proposal stored as [Ali_Ozuysal_Projesi.pdf](Ali_Ozuysal_Projesi.pdf) and [Ali_Ozuysal_Projesi.txt](Ali_Ozuysal_Projesi.txt).

## Proposal Metadata

- **Applicant:** Ali Ozuysal
- **Advisor:** Dr. Tolga Ercan
- **Institution:** Izmir Institute of Technology
- **Program:** TÜBITAK 2209-A Undergraduate Research Projects Support Program
- **Original title:** MOTOMAP - Optimum Routing Based on Traffic Density and Spatial Risk Analysis for Motorcycle Transportation

## Executive Summary

The proposal aims to build a motorcycle-specific routing system for Istanbul that optimizes not only travel time, but also rider safety. The project starts from a gap in current navigation tools:

- mainstream navigation apps are designed around car behavior
- they do not model motorcycle-specific hazards such as poor road surfaces, dangerous narrow lanes, abrupt speed changes, local crash hotspots, or lane-filtering dynamics
- motorcycle riders are materially more exposed to injury and fatality risk than car drivers

The proposed system combines:

- traffic intensity
- road geometry
- lane count
- crash clustering
- motorcycle-specific speed behavior

into a multi-criteria route optimization model.

## Research Question and Hypothesis

**Research question:** How can real-time traffic data, road characteristics, and crash statistics be used to generate efficient and safe route recommendations for motorcycle riders?

**Hypothesis:** A routing algorithm that weights traffic density and road conditions for motorcycle use can deliver routes that are safer and faster for motorcycle riders than current general-purpose map applications.

## Scientific Contribution

The proposal argues that the literature has many traffic optimization and route-planning studies, but most are car-centered. The expected contribution is a GIS-based, motorcycle-specific decision model that jointly evaluates:

- live traffic conditions
- crash-density risk
- road structure and geometry
- travel-time optimization

The document also frames the project as aligned with smart transportation, smart cities, data analytics, and AI-based decision-support priorities.

## Objectives

The English translation of the proposal's objectives is:

1. Build a dataset from Istanbul Metropolitan Municipality open data and related sources, including road structure, traffic density, speed, lane count, and crash information.
2. Develop a novel routing algorithm that jointly optimizes time and motorcycle-specific risk. Planned inputs include traffic density, crash density, road geometry, surface, curve radius, speed profiles, and rider preferences.
3. Create a map-based interface with Folium and related GIS libraries so that routes, risk levels, and dangerous segments are understandable to users. A mobile-adaptable prototype with GPS tracking is also envisioned.
4. Validate the algorithm against existing navigation tools such as Google Maps, Yandex Maps, and IBB CepTrafik using at least 50 traffic scenarios and pilot routes in Istanbul.
5. Deliver not just a route recommender, but a broader decision-support system for route risk analysis, road classification, danger detection, and customizable path selection for motorcycle riders.

The proposal explicitly targets at least a `15%` travel-time improvement against mainstream car-oriented baselines.

## Method

### Data integration

The proposed implementation combines:

- Istanbul Metropolitan Municipality open traffic and road data
- OpenStreetMap road graphs
- `OSMnx`
- `GeoPandas`
- `NetworkX`

The data pipeline converts raw records into a spatially aligned graph enriched with:

- lane count
- average speed
- traffic density coefficient
- crash and hazard indicators

### Graph variables

The proposal defines the main variable families as:

- independent variables: distance, lane count, simulated or real traffic density, crash density, road type
- dependent variables: car travel-time function and motorcycle travel-time function

Those outputs then feed the routing cost functions.

### Smart simulation fallback

If live traffic APIs are unavailable, the proposal introduces an explicit fallback strategy:

- generate time-of-day traffic profiles
- assign road-segment speeds by congestion category
- model the lane-filtering advantage for motorcycles in slow traffic

The proposal gives a simple rule of the form:

- `motorcycle_speed = 30 km/h` if `car_speed < 20 km/h` and `lane_count >= 2`
- otherwise `motorcycle_speed = car_speed + delta_v`

### Routing

The route engine would compute separate shortest paths for cars and motorcycles using weighted graph search such as:

- Dijkstra
- A*

The proposal's logic is to minimize travel time rather than raw distance, with different weight functions for each vehicle type.

### Evaluation

Planned comparison metrics include:

- total travel time
- total distance
- route differences by congestion level
- risk scores based on crash density and other hazard indicators

The proposal also mentions statistical evaluation methods such as:

- paired t-tests for average-speed comparison
- RMSE
- MAE
- accuracy-style validation metrics

## Project Management

### Timeline

The schedule in the proposal runs from February 1, 2026 to January 31, 2027 and is structured as:

1. data collection and cleaning
2. OSM graph extraction and data integration
3. graph enrichment with traffic and travel-time functions
4. route-optimization development
5. interactive map generation and safety analysis
6. final evaluation and reporting

### Risk Management

The proposal already includes a serious fallback section. Main risks and mitigations:

- live IBB traffic API unavailable: switch to smart simulation with historical traffic profiles
- source formats change or contain missing data: use preprocessing, interpolation, and KDE-based risk estimation
- OSM data outdated in some locations: sync with local road-closure and community updates, estimate missing lane counts statistically
- Folium or OSMnx rendering problems: export HTML and keep a Leaflet/Mapbox-style backup visualization path
- NetworkX too slow on a full Istanbul graph: move to pilot-region subgraphs first, then use A* or bidirectional/hierarchical routing
- inconsistent crash data: smooth it into segment-level risk zones with KDE
- Python dependency issues: freeze package versions in a controlled environment

## Research Infrastructure

The proposal lists the Izmir Institute of Technology engineering computing lab as the primary development and testing environment.

## Expected Outputs and Impact

### Scientific and academic outputs

- a TÜBITAK final report describing the smart-simulation integration, the special motorcycle cost function, and the measured time gains
- a student-conference presentation in transportation engineering, GIS, or smart-city venues
- a case-study paper on enriching OSM graphs for lane-filtering-aware routing

### Economic, social, and technical outputs

- a working routing-engine prototype for motorcycles
- faster delivery times and better urban logistics for courier workflows
- lower fuel and operational costs through more efficient routes
- an Istanbul pilot analysis inventory comparing optimized motorcycle routes against car-oriented routes by time of day

## Bottom Line

The proposal defines MotoMap as a motorcycle-first routing and safety-analysis system, not just a motorcycle skin over a standard map. Its main value proposition is explicit: model the risks and movement patterns that car navigation products ignore, then turn those into route decisions that riders can actually use.
