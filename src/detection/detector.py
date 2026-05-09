import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger("detector")


class BillboardDetector:
    def __init__(self, weights_path: str = None):
        self.weights = weights_path or config["model"]["weights"]
        self.confidence = config["model"]["confidence"]
        self.iou = config["model"]["iou_threshold"]
        self.img_size = config["model"]["img_size"]
        self.device = config["model"]["device"]
        self.model = self._load_model()

    def _load_model(self):
        path = Path(self.weights)
        if not path.exists():
            logger.warning(f"Weights not found at {path}, loading YOLOv8n base model.")
            return YOLO("yolov8n.pt")
        logger.info(f"Loading model from {path}")
        return YOLO(str(path))

    def detect(self, image_input) -> list[dict]:
        if isinstance(image_input, (str, Path)):
            image = cv2.imread(str(image_input))
        else:
            image = image_input

        if image is None:
            logger.error("Could not read image.")
            return []

        results = self.model.predict(
            source=image,
            conf=self.confidence,
            iou=self.iou,
            imgsz=self.img_size,
            device=self.device,
            verbose=False
        )

        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": round(box.conf[0].item(), 4),
                    "class_id": int(box.cls[0].item()),
                    "width_px": x2 - x1,
                    "height_px": y2 - y1,
                    "area_px": (x2 - x1) * (y2 - y1)
                })

        logger.info(f"Detected {len(detections)} billboard(s).")
        return detections

    def detect_with_preview(self, image_input) -> tuple[list[dict], np.ndarray]:
        if isinstance(image_input, (str, Path)):
            image = cv2.imread(str(image_input))
        else:
            image = image_input.copy()

        detections = self.detect(image)

        for d in detections:
            x1, y1, x2, y2 = [int(v) for v in d["bbox"]]
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 200, 100), 2)
            label = f"{d['confidence']:.2f}"
            cv2.putText(image, label, (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 100), 1)

        return detections, image