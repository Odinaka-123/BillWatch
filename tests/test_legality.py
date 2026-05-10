import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.legality.size_estimator import estimate_size
from src.legality.permit_checker import init_db, add_permit, check_permit
from datetime import datetime, timedelta, timezone


def test_size_estimator_returns_dict():
    bbox = [100, 100, 400, 300]
    result = estimate_size(bbox)
    assert "estimated_area_m2" in result
    assert "estimated_width_m" in result
    assert "estimated_height_m" in result
    assert result["estimated_area_m2"] > 0


def test_size_estimator_with_depth():
    bbox = [0, 0, 200, 100]
    result = estimate_size(bbox, depth_m=20.0)
    assert result["estimated_depth_m"] == 20.0


def test_permit_db_init():
    init_db()


def test_add_and_check_permit():
    init_db()
    add_permit(
        permit_id="TEST001",
        owner="Test Owner",
        lat=6.5244,
        lon=3.3792,
        address="Test Address, Lagos",
        area_m2=25.0,
        valid_until=datetime.now(timezone.utc) + timedelta(days=365)
    )
    result = check_permit(lat=6.5244, lon=3.3792)
    assert result["has_permit"] is True
    assert result["permit_id"] == "TEST001"


def test_check_permit_no_result():
    init_db()
    result = check_permit(lat=0.0, lon=0.0)
    assert result["has_permit"] is False