from src.legality.osm_checker import get_zone_at, is_zone_prohibited
from src.legality.permit_checker import check_permit
from src.legality.size_estimator import estimate_size
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger("classifier")

MIN_AREA = config["legality"]["min_billboard_area_m2"]


def classify(detection: dict, lat: float, lon: float) -> dict:
    size = estimate_size(detection["bbox"])
    zone = get_zone_at(lat, lon)
    permit = check_permit(lat, lon)

    violations = []

    if size["estimated_area_m2"] < MIN_AREA:
        violations.append("below_minimum_size")

    if is_zone_prohibited(zone["zone_type"]):
        violations.append(f"prohibited_zone:{zone['zone_type']}")

    if not permit["has_permit"]:
        violations.append("no_valid_permit")

    is_illegal = len(violations) > 0

    result = {
        "lat": lat,
        "lon": lon,
        "confidence": detection["confidence"],
        "is_illegal": is_illegal,
        "violations": violations,
        "zone": zone["zone_type"],
        "permit": permit,
        "size": size,
        "bbox": detection["bbox"]
    }

    status = "ILLEGAL" if is_illegal else "COMPLIANT"
    logger.info(f"Billboard at ({lat},{lon}) → {status} | violations: {violations}")
    return result