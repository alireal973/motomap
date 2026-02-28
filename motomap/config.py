import os
from dotenv import load_dotenv

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
