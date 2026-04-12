import logging
import os

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

NETWORK_TYPE = "drive"

# Default speed limits (km/h) per OSM highway type — Turkish road standards
DEFAULT_MAXSPEED = {
    "motorway": 120,
    "motorway_link": 80,
    "trunk": 110,
    "trunk_link": 70,
    "primary": 82,
    "primary_link": 50,
    "secondary": 70,
    "secondary_link": 50,
    "tertiary": 50,
    "tertiary_link": 30,
    "residential": 50,
    "living_street": 20,
    "unclassified": 50,
}

# Default total lane count per highway type
DEFAULT_LANES = {
    "motorway": 6,
    "motorway_link": 2,
    "trunk": 4,
    "trunk_link": 2,
    "primary": 4,
    "primary_link": 2,
    "secondary": 2,
    "secondary_link": 1,
    "tertiary": 2,
    "tertiary_link": 1,
    "residential": 2,
    "living_street": 1,
    "unclassified": 2,
}

DEFAULT_SURFACE = "asphalt"

# Free-flow speed factors by highway class (fraction of maxspeed achievable
# under light traffic).  Derived from HCM 6th edition base free-flow speed
# methodology and adapted for motorcycle dynamics.
# Motorcycles generally achieve higher percentages of posted speed than cars
# due to superior power-to-weight ratio and narrower profile.
FREE_FLOW_SPEED_FACTOR: dict[str, float] = {
    "motorway": 0.95,
    "motorway_link": 0.85,
    "trunk": 0.92,
    "trunk_link": 0.82,
    "primary": 0.85,
    "primary_link": 0.75,
    "secondary": 0.80,
    "secondary_link": 0.72,
    "tertiary": 0.75,
    "tertiary_link": 0.68,
    "residential": 0.70,
    "living_street": 0.60,
    "unclassified": 0.70,
    "service": 0.55,
}

# Surface-type speed reduction factors.  Values represent the fraction of
# free-flow speed attainable on each surface.  Based on OSRM/Valhalla
# surface penalties and motorcycle-specific handling research.
SURFACE_SPEED_FACTOR: dict[str, float] = {
    "asphalt": 1.00,
    "concrete": 0.95,
    "concrete:plates": 0.90,
    "concrete:lanes": 0.92,
    "paved": 0.95,
    "paving_stones": 0.70,
    "sett": 0.65,
    "cobblestone": 0.55,
    "metal": 0.85,
    "wood": 0.70,
    "compacted": 0.60,
    "fine_gravel": 0.55,
    "gravel": 0.45,
    "pebblestone": 0.40,
    "dirt": 0.35,
    "earth": 0.35,
    "grass": 0.25,
    "mud": 0.15,
    "sand": 0.20,
    "ground": 0.35,
    "unpaved": 0.40,
}

# Estimated intersection delay (seconds) based on the OSM highway type of
# the edge being entered.  These approximate HCM control-delay values.
# Edges on limited-access roads carry zero intersection delay.
INTERSECTION_DELAY_S: dict[str, float] = {
    "motorway": 0.0,
    "motorway_link": 0.0,
    "trunk": 0.0,
    "trunk_link": 2.0,
    "primary": 8.0,
    "primary_link": 5.0,
    "secondary": 6.0,
    "secondary_link": 4.0,
    "tertiary": 5.0,
    "tertiary_link": 3.0,
    "residential": 3.0,
    "living_street": 2.0,
    "unclassified": 3.0,
    "service": 2.0,
}

# Turkish traffic regulations: motorcycles below this CC are prohibited on
# motorways and expressways (Karayollari Trafik Yonetmeligi Madde 38).
MOTORWAY_MIN_CC = 125.0

# ---------------------------------------------------------------------------
# BPR volume-delay function parameters
# ---------------------------------------------------------------------------
# The Bureau of Public Roads (BPR) function models congestion:
#   t(V) = t_ff * [1 + alpha * (V / C) ^ beta]
# where V = traffic volume (veh/h), C = practical capacity, t_ff = free-flow
# travel time.  Standard BPR parameters from FHWA (1964) are alpha=0.15,
# beta=4.  These are overridable per road class.
#
# Reference:
#   Bureau of Public Roads (1964). Traffic Assignment Manual.
#   US Dept. of Commerce, Urban Planning Division, Washington DC.
#
#   Gore, N. & Arkatkar, S. (2022). "Modified Bureau of Public Roads Link
#   Function." Transportation Research Record, 2677(5), 966-990.
#   doi:10.1177/03611981221138511
BPR_ALPHA: dict[str, float] = {
    "motorway": 0.15,
    "motorway_link": 0.15,
    "trunk": 0.20,
    "trunk_link": 0.20,
    "primary": 0.25,
    "primary_link": 0.25,
    "secondary": 0.30,
    "secondary_link": 0.30,
    "tertiary": 0.35,
    "tertiary_link": 0.35,
    "residential": 0.40,
    "living_street": 0.50,
    "unclassified": 0.35,
    "service": 0.50,
}

BPR_BETA: dict[str, float] = {
    "motorway": 4.0,
    "motorway_link": 4.0,
    "trunk": 4.0,
    "trunk_link": 4.0,
    "primary": 4.0,
    "primary_link": 4.0,
    "secondary": 4.0,
    "secondary_link": 4.0,
    "tertiary": 4.0,
    "tertiary_link": 4.0,
    "residential": 3.0,
    "living_street": 3.0,
    "unclassified": 4.0,
    "service": 3.0,
}

# Practical per-lane capacity (vehicles/hour/lane) by road class.
# Based on HCM 6th Edition Table 12-14 and Exhibit 23-2.
ROAD_CAPACITY_PER_LANE: dict[str, int] = {
    "motorway": 2200,
    "motorway_link": 1800,
    "trunk": 2000,
    "trunk_link": 1600,
    "primary": 1000,
    "primary_link": 800,
    "secondary": 800,
    "secondary_link": 600,
    "tertiary": 600,
    "tertiary_link": 500,
    "residential": 400,
    "living_street": 200,
    "unclassified": 400,
    "service": 300,
}

# Peak-hour volume-to-capacity ratios when no real-time data is available.
# Represents typical Turkish urban peak conditions.
# Off-peak defaults to 0.0 (pure free-flow, no BPR congestion applied).
PEAK_HOUR_VC_RATIO: dict[str, float] = {
    "motorway": 0.75,
    "motorway_link": 0.70,
    "trunk": 0.80,
    "trunk_link": 0.70,
    "primary": 0.85,
    "primary_link": 0.75,
    "secondary": 0.75,
    "secondary_link": 0.65,
    "tertiary": 0.65,
    "tertiary_link": 0.55,
    "residential": 0.40,
    "living_street": 0.25,
    "unclassified": 0.45,
    "service": 0.30,
}

# Motorcycle lane-filtering speed advantage (km/h added on top of car speed)
# when traffic is congested (V/C > filtering threshold).
# Reference: UC Berkeley SafeTREC (2015) "Motorcycle Lane-splitting and
# Safety in California," and Wiley (2022) "Lane-Filtering Behavior of
# Motorcycle Riders at Signalized Urban Intersections."
LANE_FILTER_SPEED_BONUS: dict[int, float] = {
    1: 5.0,    # single lane: minimal advantage
    2: 15.0,   # two lanes: can filter between
    3: 20.0,   # three+ lanes: comfortable filtering
}
LANE_FILTER_VC_THRESHOLD = 0.60  # V/C above which lane filtering activates
LANE_FILTER_MIN_SPEED_KMH = 15.0  # minimum motorcycle speed even in gridlock

# Practical lane-filtering envelope used by the real-time model.  Recent
# mixed-traffic and safety literature supports treating lane filtering as a
# low-speed congestion maneuver rather than a general cruising-speed bonus.
LIVE_TRAFFIC_DEFAULT_CONFIDENCE = 0.65
LANE_FILTER_MAX_CAR_SPEED_KMH = 40.0
LANE_FILTER_MAX_EFFECTIVE_SPEED_KMH = 42.0
LANE_FILTER_TUNNEL_MODIFIER = 0.0
LANE_FILTER_NIGHT_MODIFIER = 0.75
LANE_FILTER_HEAVY_VEHICLE_PENALTY = 0.45
LANE_FILTER_NARROW_LANE_WIDTH_M = 3.15
LANE_FILTER_NARROW_LANE_MODIFIER = 0.72

# Weather and incident penalties used by mode-specific routing costs.
WEATHER_SPEED_FLOOR_FACTOR = 0.70
STANDART_WEATHER_PENALTY_WEIGHT = 0.30
VIRAJ_WEATHER_PENALTY_WEIGHT = 0.20
GUVENLI_WEATHER_PENALTY_WEIGHT = 0.75
STANDART_INCIDENT_PENALTY_WEIGHT = 0.35
VIRAJ_INCIDENT_PENALTY_WEIGHT = 0.20
GUVENLI_INCIDENT_PENALTY_WEIGHT = 0.85
