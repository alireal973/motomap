from motomap import motomap_graf_olustur


def _edge_attr_coverage(graph, attr_name: str) -> float:
    total_edges = graph.number_of_edges()
    if total_edges == 0:
        return 0.0

    with_attr = 0
    for _, _, _, data in graph.edges(keys=True, data=True):
        if data.get(attr_name) is not None:
            with_attr += 1
    return (with_attr / total_edges) * 100


def main():
    place = "Moda, Kadikoy, Istanbul, Turkey"
    graph = motomap_graf_olustur(place)

    elevations = [
        data.get("elevation")
        for _, data in graph.nodes(data=True)
        if data.get("elevation") is not None
    ]

    print(f"Place: {place}")
    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")
    print(f"Lanes coverage: {_edge_attr_coverage(graph, 'lanes'):.2f}%")
    print(f"Maxspeed coverage: {_edge_attr_coverage(graph, 'maxspeed'):.2f}%")
    print(f"Surface coverage: {_edge_attr_coverage(graph, 'surface'):.2f}%")
    if elevations:
        print(f"Elevation min/max: {min(elevations):.2f}m / {max(elevations):.2f}m")
    else:
        print("Elevation min/max: no elevation data")


if __name__ == "__main__":
    main()
