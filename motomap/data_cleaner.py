from motomap.config import DEFAULT_LANES, DEFAULT_MAXSPEED, DEFAULT_SURFACE


def _get_highway_type(data):
    """Extract a single highway type string from edge data.

    OSM highway can be a string or a list of strings.
    """
    highway = data.get("highway", "unclassified")
    if isinstance(highway, list):
        highway = highway[0]
    return highway


def _parse_int(value, default):
    """Parse a value to int, returning default if not possible."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    if isinstance(value, list):
        return _parse_int(value[0], default)
    return default


def _fill_lanes(data, highway):
    """Fill missing lanes with default based on highway type."""
    if "lanes" not in data or data["lanes"] is None:
        data["lanes"] = DEFAULT_LANES.get(highway, 2)
    else:
        data["lanes"] = _parse_int(data["lanes"], DEFAULT_LANES.get(highway, 2))


def _fill_maxspeed(data, highway):
    """Fill missing maxspeed with default based on highway type."""
    if "maxspeed" not in data or data["maxspeed"] is None:
        data["maxspeed"] = DEFAULT_MAXSPEED.get(highway, 50)
    else:
        data["maxspeed"] = _parse_int(data["maxspeed"], DEFAULT_MAXSPEED.get(highway, 50))


def _fill_surface(data):
    """Fill missing surface with default."""
    if "surface" not in data or data["surface"] is None:
        data["surface"] = DEFAULT_SURFACE


def _compute_lanes_forward(data):
    """Compute forward-direction lane count.

    Formula from README:
        oneway=True  -> lanes_forward = lanes
        oneway=False -> lanes_forward = max(1, lanes // 2)
    """
    lanes = data["lanes"]
    oneway = data.get("oneway", False)
    if oneway is True or oneway == "yes":
        data["lanes_forward"] = lanes
    else:
        data["lanes_forward"] = max(1, lanes // 2)


def clean_graph(G):
    """Fill missing OSM attributes and compute derived fields.

    Modifies graph edges in place and returns the graph.

    Fills:
        - lanes: total lane count (from highway type defaults)
        - maxspeed: speed limit in km/h (from highway type defaults)
        - surface: road surface type (default: asphalt)
        - lanes_forward: forward-direction lanes (from lanes + oneway)
    """
    for u, v, k, data in G.edges(keys=True, data=True):
        highway = _get_highway_type(data)
        _fill_lanes(data, highway)
        _fill_maxspeed(data, highway)
        _fill_surface(data)
        _compute_lanes_forward(data)
    return G
