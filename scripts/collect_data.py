import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import argparse
from src.utils.mapillary import collect

parser = argparse.ArgumentParser(description="Collect Lagos street imagery from Mapillary")
parser.add_argument("--token", required=True, help="Mapillary client token")
parser.add_argument("--limit", type=int, default=100, help="Number of images to download")
args = parser.parse_args()

print(f"Starting collection — {args.limit} images...")
results = collect(token=args.token, limit=args.limit)

out = Path("data/raw/street_view/metadata.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)

print(f"Done. {len(results)} images saved.")
print(f"Metadata written to {out}")