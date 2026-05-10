import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from src.detection.detector import BillboardDetector


def test_detector_loads():
    detector = BillboardDetector()
    assert detector.model is not None


def test_detect_returns_list():
    detector = BillboardDetector()
    dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
    results = detector.detect(dummy_image)
    assert isinstance(results, list)


def test_detect_with_preview_returns_tuple():
    detector = BillboardDetector()
    dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
    detections, preview = detector.detect_with_preview(dummy_image)
    assert isinstance(detections, list)
    assert isinstance(preview, np.ndarray)


def test_detection_fields():
    detector = BillboardDetector()
    dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
    results = detector.detect(dummy_image)
    for d in results:
        assert "bbox" in d
        assert "confidence" in d
        assert "area_px" in d