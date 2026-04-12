import random

import networkx as nx
import pytest

from motomap.algorithm import (
    FERRY_CUSTOM_FILTER,
    TRAVEL_TIME_ATTR,
    apply_weather_assessment_to_graph,
    build_mode_specific_cost,
    build_route_search_index,
    compute_edge_travel_time,
    ensure_travel_time_to_graph,
    fill_edge_defaults,
    mode_weight_attr,
    runtime_calibration_from_env,
    shortest_path,
    summarize_route,
    ucret_opsiyonlu_rota_hesapla,
)
from motomap.weather.models import RoadConditionAssessment, RoadSurfaceCondition

HIGHWAY_TYPES = (
    "primary",
    "secondary",
    "tertiary",
    "residential",
    "service",
    "unclassified",
    "motorway",
)

MOTOR_CC_CASES = (None, 50.0, 125.0, 650.0)


def _build_simple_graph() -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, 0, highway="primary", length=500.0, maxspeed=80, toll="no")
    graph.add_edge(2, 3, 0, highway="primary", length=500.0, maxspeed=80, toll="no")
    graph.add_edge(1, 3, 0, highway="motorway", length=3_000.0, maxspeed=90, toll="yes")
    return graph


def _add_random_edge(
    graph: nx.MultiDiGraph,
    rng: random.Random,
    u: int,
    v: int,
    *,
    toll: str | None = None,
) -> None:
    if u == v:
        return
    graph.add_edge(
        u,
        v,
        length=float(rng.randint(80, 4_500)),
        maxspeed=rng.choice((30, 40, 50, 60, 70, 82, 90, 110)),
        toll=toll if toll is not None else ("yes" if rng.random() < 0.25 else "no"),
        highway=rng.choice(HIGHWAY_TYPES),
        grade=round(rng.uniform(-0.16, 0.16), 4),
    )


def _build_random_graph(case_id: int) -> tuple[nx.MultiDiGraph, float | None]:
    rng = random.Random(20260306 + case_id)
    node_count = 6 + (case_id % 5)
    graph = nx.MultiDiGraph()
    for node in range(node_count):
        graph.add_node(node, x=float(node), y=float(node % 3))

    for node in range(node_count - 1):
        _add_random_edge(graph, rng, node, node + 1, toll="no")
        if rng.random() < 0.55:
            _add_random_edge(graph, rng, node + 1, node, toll="no")
        if rng.random() < 0.35:
            _add_random_edge(graph, rng, node, node + 1)

    extra_edges = node_count * 3
    for _ in range(extra_edges):
        u = rng.randrange(node_count)
        v = rng.randrange(node_count)
        if u == v:
            continue
        _add_random_edge(graph, rng, u, v)
        if rng.random() < 0.18:
            _add_random_edge(graph, rng, u, v)

    return graph, MOTOR_CC_CASES[case_id % len(MOTOR_CC_CASES)]


def _reduce_graph(
    graph: nx.MultiDiGraph,
    weight: str,
    *,
    allow_toll: bool,
) -> nx.DiGraph:
    reduced = nx.DiGraph()
    reduced.add_nodes_from(graph.nodes)
    for u, v, _, data in graph.edges(keys=True, data=True):
        if not allow_toll and str(data.get("toll", "no")).lower() == "yes":
            continue
        edge_weight = float(data.get(weight, float("inf")))
        if edge_weight == float("inf"):
            continue
        current = reduced.get_edge_data(u, v)
        if current is None or edge_weight < float(current["weight"]):
            reduced.add_edge(u, v, weight=edge_weight)
    return reduced


def _path_cost(
    graph: nx.MultiDiGraph,
    nodes: list[int],
    weight: str,
    *,
    allow_toll: bool,
) -> float:
    total = 0.0
    for idx in range(len(nodes) - 1):
        edge_candidates = graph.get_edge_data(nodes[idx], nodes[idx + 1]) or {}
        weights = []
        for data in edge_candidates.values():
            if not allow_toll and str(data.get("toll", "no")).lower() == "yes":
                continue
            weights.append(float(data.get(weight, float("inf"))))
        total += min(weights)
    return total


def test_fill_edge_defaults_populates_routing_fields():
    edge = {"highway": "primary", "oneway": False}

    fill_edge_defaults(edge)

    assert edge["lanes"] == 4
    assert edge["maxspeed"] == 82
    assert edge["surface"] == "asphalt"
    assert edge["lanes_forward"] == 2


def test_runtime_calibration_from_env_clamps_values(monkeypatch):
    monkeypatch.setenv("MOTOMAP_SPEED_FACTOR", "9")
    monkeypatch.setenv("MOTOMAP_SEGMENT_DELAY_S", "-1")
    monkeypatch.setenv("MOTOMAP_FERRY_BOARDING_DELAY_S", "9999")

    calibration = runtime_calibration_from_env()

    assert calibration.speed_factor == 1.0
    assert calibration.segment_delay_s == 0.0
    assert calibration.ferry_boarding_delay_s == 1800.0


def test_compute_edge_travel_time_uses_ferry_fallbacks():
    edge = {"route": "ferry", "length": 1_800, "maxspeed": 18}

    travel_time_s = compute_edge_travel_time(edge)

    assert travel_time_s > 0
    assert travel_time_s >= 360.0


def test_mode_weight_attr_and_filter_constants_are_shared():
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, 0, highway="primary", length=100.0)

    assert mode_weight_attr("standart") == TRAVEL_TIME_ATTR
    assert mode_weight_attr("viraj_keyfi") == "route_cost_viraj_keyfi_s"
    assert FERRY_CUSTOM_FILTER == '["route"="ferry"]'


def test_route_search_index_is_cached_until_revision_changes():
    graph = _build_simple_graph()
    result = ucret_opsiyonlu_rota_hesapla(graph, 1, 3, tercih="ucretli_serbest")

    first_revision = graph.graph["_motomap_route_revision"]
    first_index = build_route_search_index(graph, "route_cost_standart_s")

    repeated = ucret_opsiyonlu_rota_hesapla(graph, 1, 3, tercih="ucretli_serbest")
    second_index = build_route_search_index(graph, "route_cost_standart_s")

    assert result["secilen_rota"]["nodes"] == [1, 2, 3]
    assert repeated["secilen_rota"]["nodes"] == result["secilen_rota"]["nodes"]
    assert graph.graph["_motomap_route_revision"] == first_revision
    assert second_index is first_index

    graph.edges[1, 2, 0]["length"] = 2_200.0
    result_after_change = ucret_opsiyonlu_rota_hesapla(
        graph, 1, 3, tercih="ucretli_serbest"
    )
    third_index = build_route_search_index(graph, "route_cost_standart_s")

    assert graph.graph["_motomap_route_revision"] > first_revision
    assert third_index is not first_index
    assert result_after_change["secilen_rota"]["nodes"] == [1, 3]


@pytest.mark.parametrize("case_id", range(1000))
def test_randomized_shortest_path_matches_networkx(case_id):
    graph, motor_cc = _build_random_graph(case_id)
    ucret_opsiyonlu_rota_hesapla(
        graph,
        0,
        max(graph.nodes),
        tercih="ucretli_serbest",
        surus_modu="standart",
        motor_cc=motor_cc,
    )

    weight_attr = build_mode_specific_cost(
        graph,
        surus_modu="standart",
        base_weight=TRAVEL_TIME_ATTR,
        motor_cc=motor_cc,
    )
    route_index = build_route_search_index(graph, weight_attr)

    for allow_toll in (True, False):
        reduced = _reduce_graph(graph, weight_attr, allow_toll=allow_toll)
        source = 0
        target = max(graph.nodes)

        try:
            expected_cost = nx.shortest_path_length(
                reduced,
                source,
                target,
                weight="weight",
            )
        except nx.NetworkXNoPath:
            assert (
                shortest_path(
                    graph,
                    source=source,
                    target=target,
                    weight=weight_attr,
                    allow_toll=allow_toll,
                    route_index=route_index,
                )
                is None
            ), f"case_id={case_id} allow_toll={allow_toll}"
            continue

        actual_nodes = shortest_path(
            graph,
            source=source,
            target=target,
            weight=weight_attr,
            allow_toll=allow_toll,
            route_index=route_index,
        )

        assert actual_nodes is not None, f"case_id={case_id} allow_toll={allow_toll}"
        assert actual_nodes[0] == source
        assert actual_nodes[-1] == target

        actual_cost = _path_cost(
            graph,
            actual_nodes,
            weight_attr,
            allow_toll=allow_toll,
        )
        assert actual_cost == pytest.approx(
            expected_cost,
            rel=1e-9,
            abs=1e-9,
        ), f"case_id={case_id} allow_toll={allow_toll}"

        summary = summarize_route(
            graph,
            actual_nodes,
            weight=weight_attr,
            allow_toll=allow_toll,
            route_index=route_index,
        )
        assert summary["toplam_maliyet_s"] == pytest.approx(actual_cost)
        if not allow_toll:
            assert summary["ucretli_yol_iceriyor"] is False


def test_compute_edge_travel_time_blends_live_volume_and_speed_feed():
    baseline_edge = {
        "highway": "primary",
        "length": 1_000.0,
        "maxspeed": 80,
        "lanes": 4,
        "lanes_forward": 2,
    }
    live_edge = {
        **baseline_edge,
        "traffic_volume_vph": 1_800.0,
        "traffic_speed_kmh": 18.0,
        "traffic_confidence": 1.0,
    }

    baseline = compute_edge_travel_time(baseline_edge)
    live = compute_edge_travel_time(live_edge)

    assert live > baseline


def test_tunnel_edges_suppress_lane_filtering_bonus():
    open_edge = {
        "highway": "primary",
        "length": 1_000.0,
        "maxspeed": 80,
        "lanes": 4,
        "lanes_forward": 2,
        "vc_ratio": 1.0,
        "traffic_speed_kmh": 10.0,
        "traffic_confidence": 1.0,
    }
    tunnel_edge = {**open_edge, "tunnel": "yes"}

    open_time = compute_edge_travel_time(open_edge)
    tunnel_time = compute_edge_travel_time(tunnel_edge)

    assert tunnel_time > open_time


def test_apply_weather_assessment_to_graph_penalizes_open_highways():
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, 0, highway="motorway", travel_time_s=100.0, length=1000.0)
    graph.add_edge(1, 3, 0, highway="secondary", travel_time_s=100.0, length=1000.0)

    assessment = RoadConditionAssessment(
        surface_condition=RoadSurfaceCondition.WET,
        grip_factor=0.7,
        visibility_factor=0.9,
        wind_risk_factor=0.4,
        overall_safety_score=0.55,
        lane_splitting_modifier=0.45,
        warnings=["wind"],
    )
    apply_weather_assessment_to_graph(graph, assessment)
    weight_attr = build_mode_specific_cost(
        graph,
        surus_modu="standart",
        base_weight=TRAVEL_TIME_ATTR,
    )

    assert graph.edges[1, 2, 0]["weather_overall_safety"] < graph.edges[1, 3, 0]["weather_overall_safety"]
    assert graph.edges[1, 2, 0][weight_attr] > graph.edges[1, 3, 0][weight_attr]


def test_live_traffic_changes_invalidate_cached_travel_time():
    graph = nx.MultiDiGraph()
    graph.add_edge(
        1,
        2,
        0,
        highway="primary",
        length=1_000.0,
        maxspeed=80,
        lanes=4,
        lanes_forward=2,
    )

    ensure_travel_time_to_graph(graph)
    baseline = graph.edges[1, 2, 0][TRAVEL_TIME_ATTR]

    graph.edges[1, 2, 0]["traffic_speed_kmh"] = 12.0
    graph.edges[1, 2, 0]["traffic_confidence"] = 1.0
    ensure_travel_time_to_graph(graph)
    updated = graph.edges[1, 2, 0][TRAVEL_TIME_ATTR]

    assert updated > baseline
