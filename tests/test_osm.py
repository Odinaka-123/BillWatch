import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.legality.osm_checker import is_zone_prohibited


def test_prohibited_zone_residential():
    assert is_zone_prohibited("residential") is True


def test_prohibited_zone_park():
    assert is_zone_prohibited("park") is True


def test_non_prohibited_zone():
    assert is_zone_prohibited("commercial") is False


def test_unknown_zone():
    assert is_zone_prohibited("unknown") is False