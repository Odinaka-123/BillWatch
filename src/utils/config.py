import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_config(path: str = None) -> dict:
    config_path = Path(path) if path else ROOT / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()