import requests
import time
from pathlib import Path
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger("mapillary")

BASE_URL = "https://graph.mapillary.com"

BILLBOARD_ZONES = [
    {"name": "victoria_island", "west": 3.4106, "south": 6.4195, "east": 3.4406, "north": 6.4395},
    {"name": "lekki",           "west": 3.4700, "south": 6.4300, "east": 3.5000, "north": 6.4600},
    {"name": "ikeja",           "west": 3.3300, "south": 6.5800, "east": 3.3600, "north": 6.6100},
    {"name": "surulere",        "west": 3.3500, "south": 6.4900, "east": 3.3800, "north": 6.5200},
    {"name": "maryland",        "west": 3.3600, "south": 6.5600, "east": 3.3900, "north": 6.5900},
]

TILE_SIZE = 0.09


def make_tiles(bbox: dict, tile_size: float = TILE_SIZE) -> list:
    tiles = []
    lat = bbox["south"]
    while lat < bbox["north"]:
        lon = bbox["west"]
        while lon < bbox["east"]:
            tiles.append({
                "west":  round(lon, 6),
                "south": round(lat, 6),
                "east":  round(min(lon + tile_size, bbox["east"]), 6),
                "north": round(min(lat + tile_size, bbox["north"]), 6)
            })
            lon += tile_size
        lat += tile_size
    return tiles


def fetch_image_ids(token: str, bbox: dict = None, limit: int = 50) -> list:
    tiles = make_tiles(bbox) if bbox else [bbox]
    headers = {"Authorization": f"OAuth {token}"}
    all_images = []
    per_tile = max(1, limit // max(len(tiles), 1))

    logger.info(f"Querying {len(tiles)} tiles, ~{per_tile} images each.")

    for i, tile in enumerate(tiles):
        if len(all_images) >= limit:
            break
        url = f"{BASE_URL}/images"
        params = {
            "fields":     "id,geometry,captured_at",
            "bbox":       f"{tile['west']},{tile['south']},{tile['east']},{tile['north']}",
            "limit":      per_tile,
            "image_type": "flat"
        }
        try:
            r = requests.get(url, params=params, headers=headers, timeout=30)
            r.raise_for_status()
            data = r.json().get("data", [])
            logger.info(f"Tile {i+1}/{len(tiles)}: {len(data)} images.")
            all_images.extend(data)
            time.sleep(0.3)
        except Exception as e:
            logger.error(f"Tile {i+1} failed: {e}")
            continue

    logger.info(f"Total fetched: {len(all_images)} image IDs.")
    return all_images[:limit]


def download_image(token: str, image_id: str, out_dir: Path) -> dict | None:
    url = f"{BASE_URL}/{image_id}"
    params = {
        "fields": "id,thumb_2048_url,geometry,captured_at"
    }
    headers = {
        "Authorization": f"OAuth {token}"
    }

    try:
        r = requests.get(url, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        meta = r.json()

        img_url = meta.get("thumb_2048_url")
        if not img_url:
            return None

        img_data = requests.get(img_url, timeout=30).content
        out_path = out_dir / f"{image_id}.jpg"
        out_path.write_bytes(img_data)

        coords = meta.get("geometry", {}).get("coordinates", [None, None])
        return {
            "image_id":    image_id,
            "path":        str(out_path),
            "lon":         coords[0],
            "lat":         coords[1],
            "captured_at": meta.get("captured_at")
        }

    except Exception as e:
        logger.error(f"Failed to download {image_id}: {e}")
        return None


def collect(token: str, limit: int = 200, delay: float = 0.5) -> list:
    out_dir = Path(config["data"]["raw_street_view"])
    out_dir.mkdir(parents=True, exist_ok=True)

    per_zone = limit // len(BILLBOARD_ZONES)
    all_ids = []

    for zone in BILLBOARD_ZONES:
        logger.info(f"Fetching zone: {zone['name']}")
        ids = fetch_image_ids(token, bbox=zone, limit=per_zone)
        all_ids.extend(ids)

    if not all_ids:
        logger.warning("No images returned.")
        return []

    results = []
    for i, item in enumerate(all_ids):
        image_id = item["id"]
        logger.info(f"Downloading {i+1}/{len(all_ids)}: {image_id}")
        meta = download_image(token, image_id, out_dir)
        if meta:
            results.append(meta)
        time.sleep(delay)

    logger.info(f"Downloaded {len(results)} images to {out_dir}")
    return results