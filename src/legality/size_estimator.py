from src.utils.logger import get_logger

logger = get_logger("size_estimator")

KNOWN_WIDTHS_M = {
    "standard": 3.0,
    "large": 6.0,
    "billboard": 9.0,
}

FOCAL_LENGTH_PX = 1000


def estimate_size(bbox: list, depth_m: float = None) -> dict:
    x1, y1, x2, y2 = bbox
    width_px = x2 - x1
    height_px = y2 - y1

    if depth_m is None:
        depth_m = _estimate_depth(width_px)

    width_m = (width_px * depth_m) / FOCAL_LENGTH_PX
    height_m = (height_px * depth_m) / FOCAL_LENGTH_PX
    area_m2 = round(width_m * height_m, 2)

    return {
        "estimated_width_m": round(width_m, 2),
        "estimated_height_m": round(height_m, 2),
        "estimated_area_m2": area_m2,
        "estimated_depth_m": round(depth_m, 2)
    }


def _estimate_depth(width_px: int) -> float:
    ref_width_m = KNOWN_WIDTHS_M["billboard"]
    depth = (FOCAL_LENGTH_PX * ref_width_m) / max(width_px, 1)
    return round(depth, 2)