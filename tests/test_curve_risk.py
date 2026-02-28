import networkx as nx
from shapely.geometry import LineString

from motomap.curve_risk import (
    add_curve_and_risk_metrics,
    analyze_linestring_curvature,
)


def test_analyze_linestring_curvature_detects_fun_turns():
    line = LineString(
        [
            (0.0, 0.0),
            (1.0, 0.0),
            (2.0, 0.58),
            (3.0, 1.15),
        ]
    )
    metrics = analyze_linestring_curvature(line, length_m=35.0, interpolation_step_m=10.0)
    assert metrics["fun_count"] > 0
    assert metrics["curvature_score"] > 0


def test_analyze_linestring_curvature_detects_danger_and_hairpin():
    line = LineString(
        [
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (2.0, 1.0),
        ]
    )
    metrics = analyze_linestring_curvature(line, length_m=15.0, interpolation_step_m=5.0)
    assert metrics["danger_count"] > 0
    assert metrics["hairpin_count"] > 0


def test_add_curve_and_risk_metrics_marks_high_risk_downhill_hairpin():
    graph = nx.MultiDiGraph()
    graph.add_node(1, x=0.0, y=0.0)
    graph.add_node(2, x=1.0, y=1.0)
    graph.add_edge(
        1,
        2,
        0,
        length=12.0,
        grade=-0.10,
        geometry=LineString([(0.0, 0.0), (0.9, 0.0), (0.9, 0.9)]),
    )

    add_curve_and_risk_metrics(graph, interpolation_step_m=5.0)
    data = graph.edges[1, 2, 0]
    assert data["viraj_tehlike_sayisi"] > 0
    assert data["viraj_hairpin_sayisi"] > 0
    assert data["yuksek_risk_bolge"] is True
