import networkx as nx
import pytest
from shapely.geometry import LineString

from motomap.router import (
    NoRouteFoundError,
    TRAVEL_TIME_ATTR,
    add_travel_time_to_graph,
    ucret_opsiyonlu_rota_hesapla,
)


def _build_graph_toll_is_faster():
    graph = nx.MultiDiGraph()
    for n, (x, y) in {
        1: (0.0, 0.0),
        2: (1.0, 0.0),
        3: (2.0, 0.0),
        4: (1.0, 0.8),
    }.items():
        graph.add_node(n, x=x, y=y)
    # Toll route: 1 -> 2 -> 3 (faster)
    graph.add_edge(1, 2, 0, length=1000, maxspeed=90, toll="yes")
    graph.add_edge(2, 3, 0, length=1000, maxspeed=90, toll="yes")
    # Free route: 1 -> 4 -> 3 (slower)
    graph.add_edge(1, 4, 0, length=3000, maxspeed=60, toll="no")
    graph.add_edge(4, 3, 0, length=3000, maxspeed=60, toll="no")
    return graph


def _build_graph_free_is_faster():
    graph = nx.MultiDiGraph()
    for n, (x, y) in {
        1: (0.0, 0.0),
        2: (1.0, 0.0),
        3: (2.0, 0.0),
        4: (1.0, 0.8),
    }.items():
        graph.add_node(n, x=x, y=y)
    # Toll route (slower)
    graph.add_edge(1, 2, 0, length=5000, maxspeed=50, toll="yes")
    graph.add_edge(2, 3, 0, length=5000, maxspeed=50, toll="yes")
    # Free route (faster)
    graph.add_edge(1, 4, 0, length=2000, maxspeed=60, toll="no")
    graph.add_edge(4, 3, 0, length=2000, maxspeed=60, toll="no")
    return graph


def test_add_travel_time_to_graph_sets_edge_attribute():
    graph = _build_graph_toll_is_faster()
    add_travel_time_to_graph(graph)
    data = graph.edges[1, 2, 0]
    assert TRAVEL_TIME_ATTR in data
    assert data[TRAVEL_TIME_ATTR] > 0


def test_ucretli_serbest_selects_toll_when_toll_is_faster():
    graph = _build_graph_toll_is_faster()
    result = ucret_opsiyonlu_rota_hesapla(graph, 1, 3, tercih="ucretli_serbest")

    assert result["secilen_rota"]["nodes"] == [1, 2, 3]
    assert result["secilen_rota"]["ucretli_yol_iceriyor"] is True
    assert result["alternatifler"]["ucretsiz"]["nodes"] == [1, 4, 3]


def test_ucretli_serbest_can_still_choose_free_route_when_faster():
    graph = _build_graph_free_is_faster()
    result = ucret_opsiyonlu_rota_hesapla(graph, 1, 3, tercih="ucretli_serbest")

    assert result["secilen_rota"]["nodes"] == [1, 4, 3]
    assert result["secilen_rota"]["ucretli_yol_iceriyor"] is False


def test_ucretsiz_preference_forces_non_toll_route():
    graph = _build_graph_toll_is_faster()
    result = ucret_opsiyonlu_rota_hesapla(graph, 1, 3, tercih="ucretsiz")

    assert result["secilen_rota"]["nodes"] == [1, 4, 3]
    assert result["secilen_rota"]["ucretli_yol_iceriyor"] is False


def test_ucretsiz_raises_when_no_non_toll_route_exists():
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, 0, length=1000, maxspeed=60, toll="yes")
    graph.add_edge(2, 3, 0, length=1000, maxspeed=60, toll="yes")

    with pytest.raises(NoRouteFoundError):
        ucret_opsiyonlu_rota_hesapla(graph, 1, 3, tercih="ucretsiz")


def _build_graph_for_viraj_mode():
    graph = nx.MultiDiGraph()
    for n, (x, y) in {
        1: (0.0, 0.0),
        2: (2.0, 0.0),
        3: (1.0, 0.2),
        4: (2.2, 1.0),
        5: (3.0, 0.0),
    }.items():
        graph.add_node(n, x=x, y=y)

    # Route A (straighter, slightly faster in pure time)
    graph.add_edge(
        1, 2, 0, length=1200, maxspeed=60, toll="no", grade=0.00,
        geometry=LineString([(0.0, 0.0), (2.0, 0.0)])
    )
    graph.add_edge(
        2, 5, 0, length=1200, maxspeed=60, toll="no", grade=0.00,
        geometry=LineString([(2.0, 0.0), (3.0, 0.0)])
    )

    # Route B (more curvy, can win in viraj_keyfi mode)
    graph.add_edge(
        1, 3, 0, length=1300, maxspeed=60, toll="no", grade=-0.01,
        geometry=LineString([(0.0, 0.0), (0.6, 0.0), (1.0, 0.2)])
    )
    graph.add_edge(
        3, 4, 0, length=1300, maxspeed=60, toll="no", grade=-0.01,
        geometry=LineString([(1.0, 0.2), (1.4, 0.7), (2.2, 1.0)])
    )
    graph.add_edge(
        4, 5, 0, length=400, maxspeed=60, toll="no", grade=-0.01,
        geometry=LineString([(2.2, 1.0), (2.8, 0.4), (3.0, 0.0)])
    )
    return graph


def _build_graph_for_guvenli_mode():
    graph = nx.MultiDiGraph()
    for n, (x, y) in {
        1: (0.0, 0.0),
        2: (1.0, 0.0),
        3: (1.0, 1.0),
        4: (2.0, 0.0),
    }.items():
        graph.add_node(n, x=x, y=y)

    # Risky downhill + sharp turns (shorter in raw time)
    graph.add_edge(
        1, 2, 0, length=700, maxspeed=60, toll="no", grade=-0.12,
        geometry=LineString([(0.0, 0.0), (0.5, 0.0), (0.5, 0.6)])
    )
    graph.add_edge(
        2, 4, 0, length=700, maxspeed=60, toll="no", grade=-0.12,
        geometry=LineString([(0.5, 0.6), (1.0, 0.6), (1.0, 0.0)])
    )

    # Safer route
    graph.add_edge(
        1, 3, 0, length=1200, maxspeed=60, toll="no", grade=-0.01,
        geometry=LineString([(0.0, 0.0), (0.5, 0.5), (1.0, 1.0)])
    )
    graph.add_edge(
        3, 4, 0, length=1200, maxspeed=60, toll="no", grade=-0.01,
        geometry=LineString([(1.0, 1.0), (1.6, 0.6), (2.0, 0.0)])
    )
    return graph


def test_viraj_keyfi_mode_can_choose_curvy_route():
    graph = _build_graph_for_viraj_mode()
    result = ucret_opsiyonlu_rota_hesapla(
        graph, 1, 5, tercih="ucretli_serbest", surus_modu="viraj_keyfi"
    )

    assert result["secilen_rota"]["nodes"] == [1, 3, 4, 5]
    assert result["secilen_rota"]["viraj_fun_sayisi"] > 0


def test_guvenli_mode_avoids_risky_downhill_segments():
    graph = _build_graph_for_guvenli_mode()

    standard = ucret_opsiyonlu_rota_hesapla(
        graph, 1, 4, tercih="ucretli_serbest", surus_modu="standart"
    )
    safe = ucret_opsiyonlu_rota_hesapla(
        graph, 1, 4, tercih="ucretli_serbest", surus_modu="guvenli"
    )

    assert standard["secilen_rota"]["nodes"] == [1, 2, 4]
    assert safe["secilen_rota"]["nodes"] == [1, 3, 4]
    assert safe["secilen_rota"]["yuksek_risk_segment_sayisi"] == 0


def _build_graph_for_cc_highway_restriction():
    graph = nx.MultiDiGraph()
    for n, (x, y) in {
        1: (0.0, 0.0),
        2: (1.0, 0.0),
        3: (1.0, 1.0),
        4: (2.0, 0.0),
    }.items():
        graph.add_node(n, x=x, y=y)

    # Fast motorway route
    graph.add_edge(1, 2, 0, length=900, maxspeed=120, toll="no", highway="motorway")
    graph.add_edge(2, 4, 0, length=900, maxspeed=120, toll="no", highway="motorway")

    # Slower urban route
    graph.add_edge(1, 3, 0, length=1700, maxspeed=50, toll="no", highway="secondary")
    graph.add_edge(3, 4, 0, length=1700, maxspeed=50, toll="no", highway="secondary")
    return graph


def test_low_cc_avoids_motorway_trunk_edges():
    graph = _build_graph_for_cc_highway_restriction()

    low_cc = ucret_opsiyonlu_rota_hesapla(
        graph, 1, 4, tercih="ucretli_serbest", surus_modu="standart", motor_cc=50
    )
    high_cc = ucret_opsiyonlu_rota_hesapla(
        graph, 1, 4, tercih="ucretli_serbest", surus_modu="standart", motor_cc=250
    )

    assert low_cc["secilen_rota"]["nodes"] == [1, 3, 4]
    assert high_cc["secilen_rota"]["nodes"] == [1, 2, 4]


def _build_graph_for_cc_grade_penalty():
    graph = nx.MultiDiGraph()
    for n, (x, y) in {
        1: (0.0, 0.0),
        2: (1.0, 0.1),
        3: (1.0, 0.9),
        4: (2.0, 0.0),
    }.items():
        graph.add_node(n, x=x, y=y)

    # Short but steep option
    graph.add_edge(1, 2, 0, length=1200, maxspeed=60, toll="no", grade=0.11, highway="secondary")
    graph.add_edge(2, 4, 0, length=1200, maxspeed=60, toll="no", grade=0.11, highway="secondary")

    # Longer but mild slope option
    graph.add_edge(1, 3, 0, length=1400, maxspeed=60, toll="no", grade=0.02, highway="secondary")
    graph.add_edge(3, 4, 0, length=1400, maxspeed=60, toll="no", grade=0.02, highway="secondary")
    return graph


def test_mid_cc_prefers_milder_grade_when_time_close():
    graph = _build_graph_for_cc_grade_penalty()

    no_cc = ucret_opsiyonlu_rota_hesapla(
        graph, 1, 4, tercih="ucretli_serbest", surus_modu="standart"
    )
    mid_cc = ucret_opsiyonlu_rota_hesapla(
        graph, 1, 4, tercih="ucretli_serbest", surus_modu="standart", motor_cc=150
    )

    assert no_cc["secilen_rota"]["nodes"] == [1, 2, 4]
    assert mid_cc["secilen_rota"]["nodes"] == [1, 3, 4]


def test_ucretsiz_preference_applies_in_viraj_mode():
    graph = _build_graph_toll_is_faster()
    result = ucret_opsiyonlu_rota_hesapla(
        graph,
        1,
        3,
        tercih="ucretsiz",
        surus_modu="viraj_keyfi",
    )

    assert result["secilen_rota"]["nodes"] == [1, 4, 3]
    assert result["secilen_rota"]["ucretli_yol_iceriyor"] is False


def _build_graph_for_motorway_side_shortcut():
    graph = nx.MultiDiGraph()
    for n, (x, y) in {
        1: (0.0, 0.0),
        2: (0.6, 0.0),
        3: (1.2, 0.0),
        4: (0.6, 0.4),
        5: (0.6, -0.4),
    }.items():
        graph.add_node(n, x=x, y=y)

    # Unrealistic local shortcut near motorway shoulder.
    graph.add_edge(1, 2, 0, length=180, maxspeed=50, toll="no", highway="service")
    graph.add_edge(2, 3, 0, length=180, maxspeed=50, toll="no", highway="service")

    # Main-road alternative.
    graph.add_edge(1, 4, 0, length=350, maxspeed=50, toll="no", highway="primary")
    graph.add_edge(4, 3, 0, length=350, maxspeed=50, toll="no", highway="primary")

    # Major highway touching the shortcut node.
    graph.add_edge(2, 5, 0, length=500, maxspeed=100, toll="no", highway="motorway")
    return graph


def test_standart_mode_avoids_motorway_side_shortcuts():
    graph = _build_graph_for_motorway_side_shortcut()
    result = ucret_opsiyonlu_rota_hesapla(
        graph, 1, 3, tercih="ucretli_serbest", surus_modu="standart"
    )

    assert result["secilen_rota"]["nodes"] == [1, 4, 3]
