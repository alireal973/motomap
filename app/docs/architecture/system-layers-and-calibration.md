[![Language: English](https://img.shields.io/badge/Language-English-1f6feb)](system-layers-and-calibration.md)
[![Language: Turkish](https://img.shields.io/badge/Language-Turkish-c92a2a)](system-layers-and-calibration.tr.md)

# MotoMap System Layers

This document summarizes MotoMap's end-to-end technical layers and the calibration and evaluation feedback loop in one place.

## 1. High-level layered architecture

```mermaid
flowchart TB
    subgraph L0[Layer 0 - External Data Sources]
        OSM[OpenStreetMap road network]
        ELEV[Google Elevation API / OpenTopo]
        TRAFFIC[Live traffic source]
        OBS[GPS traces / benchmark data]
    end

    subgraph L1[Layer 1 - Ingestion and Resilience]
        DL[data_loader.py\nload_graph]
        OV[osm_validator.py\nfilter_motorcycle_edges]
        EL[elevation.py\nadd_elevation + fallback]
    end

    subgraph L2[Layer 2 - Feature Engineering]
        GR[elevation.py\nadd_grade]
        CL[data_cleaner.py\nclean_graph]
        CR[curve_risk.py\ncurve + risk metrics]
    end

    subgraph L3[Layer 3 - Cost and Routing Core]
        TT[router.py\nadd_travel_time_to_graph]
        MW[router.py\nmode-specific weight]
        RT[router.py\nucret_opsiyonlu_rota_hesapla]
    end

    subgraph L4[Layer 4 - Orchestration and Delivery]
        PUB[motomap.__init__.py\nmotomap_graf_olustur]
        API[REST API / service layer]
        APP[Web / mobile client]
        OUT[Script outputs\nmap/pdf/png/npz]
    end

    subgraph L5[Layer 5 - Evaluation and Calibration]
        MET[Metric computation\nETA, risk, route delta]
        EVA[Evaluation sets\nmode/baseline comparison]
        TUNE[Parameter tuning\nspeed factor, delay, penalties]
    end

    OSM --> DL
    ELEV --> EL
    TRAFFIC --> TT
    OBS --> EVA

    DL --> OV --> EL --> GR --> CL --> CR
    CL --> TT
    CR --> MW
    TT --> MW --> RT

    RT --> API --> APP
    RT --> OUT
    RT --> MET --> EVA --> TUNE --> TT
    TUNE --> MW

    PUB --> DL
    PUB --> OV
    PUB --> EL
    PUB --> GR
    PUB --> CL
```

## 2. Layer-by-layer purpose

| Layer | What it does | Why it matters | Main components |
|---|---|---|---|
| 0. External data | Supplies roads, elevation, traffic, and observations. | Routing quality depends on real-world inputs. | OSM, Google/OpenTopo, traffic feeds, GPS traces |
| 1. Ingestion | Loads the graph, removes motorcycle-invalid edges, adds resilient elevation fallback. | Dirty or incomplete inputs become routing defects quickly. | `data_loader.py`, `osm_validator.py`, `elevation.py` |
| 2. Feature engineering | Computes grade, fills lanes/speed/surface, derives curve and risk metrics. | Raw OSM tags are not enough to explain rider cost. | `add_grade`, `clean_graph`, `add_curve_and_risk_metrics` |
| 3. Routing core | Builds time-based costs plus mode-specific weights and toll/free choices. | Converts rider intent into numeric optimization. | `router.py` |
| 4. Delivery | Orchestrates the pipeline and exposes results to APIs, apps, and artifacts. | Bridges the routing engine with actual product surfaces. | `motomap_graf_olustur`, service layer, output scripts |
| 5. Evaluation | Measures KPIs, compares baselines, and tunes parameters. | Prevents regressions and aligns the model with real behavior. | metrics, eval scripts, tuning loops |

## 3. Calibration and evaluation loop

```mermaid
flowchart LR
    A[1. Prepare scenarios and observations\nOD set + GPS / baseline] -->
    B[2. Generate routes with current parameters\nstandard / safe / twisty]

    B --> C[3. Compute metrics\nETA MAE/MAPE, risk score, route similarity]
    C --> D{4. Do the acceptance thresholds pass?}

    D -- Yes --> E[5. Freeze parameter set\nrelease + documentation]
    D -- No --> F[6. Update parameters\nMOTOMAP_SPEED_FACTOR\nMOTOMAP_SEGMENT_DELAY_S\nroad / curve / grade penalties]

    F --> G[7. Run regression tests\nunit + scenario eval]
    G --> B

    E --> H[8. Monitor production\nlatency, pass-rate, mode separation]
    H --> A
```

Notes:

- This is a continuous quality loop, not a one-off exercise.
- `speed_factor` and `segment_delay` are the first levers to tune when ETA drift appears.

## 4. Short glossary

| Term | Short explanation |
|---|---|
| OD (Origin-Destination) | A start and destination pair. |
| Edge | A directed road connection in the graph. |
| Grade | Road slope ratio. Positive for climbs, negative for descents. |
| Curvature | How twisty a road is. |
| Baseline | A reference system or route result used for comparison. |
| Calibration | Adjusting parameters against observations. |
| Evaluation | Measuring performance with explicit metrics. |
| KPI | A tracked quality indicator. |
