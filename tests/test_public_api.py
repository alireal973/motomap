import networkx as nx
import motomap


def test_motomap_graf_olustur_pipeline_order(monkeypatch):
    calls = []
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, 0, highway="residential", length=100)

    def fake_load_graph(place):
        calls.append(("load_graph", place))
        return graph

    def fake_add_elevation(g, api_key=None):
        calls.append(("add_elevation", api_key))
        return g

    def fake_add_grade(g):
        calls.append(("add_grade", None))
        return g

    def fake_clean_graph(g):
        calls.append(("clean_graph", None))
        return g

    monkeypatch.setattr(motomap, "load_graph", fake_load_graph)
    monkeypatch.setattr(motomap, "add_elevation", fake_add_elevation)
    monkeypatch.setattr(motomap, "add_grade", fake_add_grade)
    monkeypatch.setattr(motomap, "clean_graph", fake_clean_graph)

    result = motomap.motomap_graf_olustur("Kadikoy, Istanbul, Turkey", api_key="test-key")

    assert result is graph
    assert calls == [
        ("load_graph", "Kadikoy, Istanbul, Turkey"),
        ("add_elevation", "test-key"),
        ("add_grade", None),
        ("clean_graph", None),
    ]


def test_motomap_graf_olustur_uses_default_api_key(monkeypatch):
    calls = []
    graph = nx.MultiDiGraph()

    monkeypatch.setattr(motomap, "GOOGLE_MAPS_API_KEY", "default-test-key")
    monkeypatch.setattr(motomap, "load_graph", lambda _place: graph)
    monkeypatch.setattr(
        motomap,
        "add_elevation",
        lambda g, api_key=None: (calls.append(api_key), g)[1],
    )
    monkeypatch.setattr(motomap, "add_grade", lambda g: g)
    monkeypatch.setattr(motomap, "clean_graph", lambda g: g)

    motomap.motomap_graf_olustur("Moda, Istanbul, Turkey")

    assert calls == ["default-test-key"]
