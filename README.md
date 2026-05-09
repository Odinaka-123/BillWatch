# BillWatch

Automated illegal billboard detection using YOLOv8 + OpenStreetMap. Detects, geo-tags, and flags non-compliant outdoor advertising for municipal enforcement.

## Overview

BillWatch is an end-to-end AI pipeline for detecting and classifying illegal billboards in urban environments. It combines street-view and satellite imagery with deep learning and geospatial validation to give municipalities a scalable, cost-effective enforcement tool.

Built as a primary case study for Lagos, Nigeria — adaptable globally.

## Features

- YOLOv8-based billboard detection on street-view and satellite images
- Automatic GPS tagging and size estimation via monocular depth
- Legality classification using OpenStreetMap zoning data
- Permit database with SQLite backend
- Interactive enforcement dashboard with live map (Streamlit + Folium)
- Telegram alert integration for real-time notifications
- Edge-device ready — runs on CPU, no GPU required

## Project Structure

BillWatch/
├── data/
│   ├── raw/
│   │   ├── street_view/       # Raw street-view images
│   │   └── satellite/         # Raw satellite images
│   ├── annotated/
│   │   ├── images/            # Labelled images
│   │   └── labels/            # YOLO format annotations
│   └── processed/             # Preprocessed datasets
├── models/
│   ├── weights/               # Trained .pt model files
│   └── exports/               # ONNX / exported models
├── notebooks/                 # Exploration and training notebooks
├── src/
│   ├── detection/             # YOLOv8 detector + size estimator
│   ├── legality/              # OSM checker, permit DB, classifier
│   ├── dashboard/             # Streamlit app
│   └── utils/                 # Config loader, logger
├── tests/
├── config.yaml
├── requirements.txt
└── run.py

## Quickstart

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/BillWatch.git
cd BillWatch
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
source venv/bin/activate       # macOS/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt --prefer-binary
```

**4. Run the dashboard**
```bash
python run.py
```

Open your browser at `http://localhost:8501`

## Usage

1. Upload a street-view or satellite image in the sidebar
2. Enter the GPS coordinates of the image location
3. Click **Run detection**
4. View results on the map and in the detections table
5. Add known permits via the sidebar form

## Configuration

All settings are in `config.yaml`:

```yaml
model:
  confidence: 0.45       # Detection confidence threshold
  device: cpu            # Use 'cuda' if GPU available

dashboard:
  map_center_lat: 6.5244 # Default map center (Lagos)
  map_center_lon: 3.3792

alerts:
  telegram_enabled: false
  telegram_token: ""
  telegram_chat_id: ""
```

## Data Sources

| Source | Type | Cost |
|--------|------|------|
| Mapillary | Street-view imagery | Free |
| Sentinel-2 / Copernicus | Satellite imagery | Free |
| OpenStreetMap Overpass API | Zoning / GIS data | Free |
| LASAA open data | Lagos permit records | Free |

## Model Training

Training notebooks are in `/notebooks`. The detector uses YOLOv8n as a base model, fine-tuned on a custom annotated dataset of billboard instances across Lagos and two additional metropolitan regions.

Annotation tool: [Label Studio](https://labelstud.io/) (free, self-hosted)

## Tech Stack

- **Detection** — Ultralytics YOLOv8
- **Geospatial** — OpenStreetMap Overpass API, GeoPy
- **Database** — SQLite via SQLAlchemy
- **Dashboard** — Streamlit, Folium
- **Alerts** — Telegram Bot API

## License

See [LICENSE](LICENSE) for details.

## Acknowledgements

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [Mapillary](https://www.mapillary.com/)
- [Streamlit](https://streamlit.io/)

