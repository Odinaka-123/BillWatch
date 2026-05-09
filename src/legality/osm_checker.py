import overpy
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger("osm_checker")

api = overpy.Overpass()

PROHIBITED_ZONES = [
    "residential",
    "conservation",
    "nature_reserve",
    "park",
    "cemetery",
    "school",
    "hospital",
]

def get_zone_at(lat: float, lon: float) -> dict:
    radius = 50
    timeout = config["legality"]["osm_timeout"]

    query = f"""
    [out:json][timeout:{timeout}];
    (
      way(around:{radius},{lat},{lon})[landuse];
      way(around:{radius},{lat},{lon})[amenity];
      way(around:{radius},{lat},{lon})[leisure];
      relation(around:{radius},{lat},{lon})[boundary];
    );
    out tags;
    """

    try:
        result = api.query(query)
        tags = {}
        for way in result.ways:
            tags.update(way.tags)
        for rel in result.relations:
            tags.update(rel.tags)

        zone_type = (
            tags.get("landuse") or
            tags.get("amenity") or
            tags.get("leisure") or
            tags.get("boundary") or
            "unknown"
        )

        return {
            "lat": lat,
            "lon": lon,
            "zone_type": zone_type,
            "tags": tags
        }

    except Exception as e:
        logger.error(f"OSM query failed for ({lat}, {lon}): {e}")
        return {"lat": lat, "lon": lon, "zone_type": "unknown", "tags": {}}


def is_zone_prohibited(zone_type: str) -> bool:
    return any(p in zone_type.lower() for p in PROHIBITED_ZONES)