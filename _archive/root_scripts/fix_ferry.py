with open('motomap/algorithm.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_forbidden = '''def is_motorcycle_forbidden(
    edge_data: Mapping[str, object],
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> bool:
    """Return `True` when the edge should be excluded from motorcycle routing."""

    highway = normalize_tag(edge_data.get("highway"))'''

new_forbidden = '''def is_motorcycle_forbidden(
    edge_data: Mapping[str, object],
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> bool:
    """Return `True` when the edge should be excluded from motorcycle routing."""

    if is_ferry_edge(edge_data):
        return True

    highway = normalize_tag(edge_data.get("highway"))'''

text = text.replace(old_forbidden, new_forbidden)

with open('motomap/algorithm.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated algorithm.py to exclude ferries")
