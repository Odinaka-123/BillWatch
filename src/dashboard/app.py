import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from src.utils.config import config
from src.utils.logger import get_logger
from src.legality.permit_checker import init_db
from src.dashboard.auth import init_auth_db, create_user, verify_user

st.set_page_config(
    page_title="BillWatch",
    page_icon="🚨",
    layout="wide"
)

init_auth_db()
init_db()
logger = get_logger("dashboard")

# --- Auth gate ---
if "user" not in st.session_state:
    st.session_state.user = None

def show_auth():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🚨 BillWatch")
        st.caption("Municipal billboard enforcement system")
        st.divider()

        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            st.subheader("Login")
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", type="primary", use_container_width=True):
                user = verify_user(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        with tab2:
            st.subheader("Create account")
            new_user = st.text_input("Username", key="signup_user")
            new_pass = st.text_input("Password", type="password", key="signup_pass")
            new_pass2 = st.text_input("Confirm password", type="password", key="signup_pass2")
            if st.button("Sign up", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("Please fill in all fields.")
                elif new_pass != new_pass2:
                    st.error("Passwords do not match.")
                elif len(new_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    if create_user(new_user, new_pass):
                        st.success("Account created. Please log in.")
                    else:
                        st.error("Username already exists.")

if st.session_state.user is None:
    show_auth()
    st.stop()

# --- Logged in ---
st.sidebar.markdown(f"👤 **{st.session_state.user['username']}** `{st.session_state.user['role']}`")
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

if "detections" not in st.session_state:
    st.session_state.detections = []


def build_map(detections: list) -> folium.Map:
    m = folium.Map(
        location=[
            config["dashboard"]["map_center_lat"],
            config["dashboard"]["map_center_lon"]
        ],
        zoom_start=config["dashboard"]["map_zoom"],
        tiles="CartoDB positron"
    )

    for d in detections:
        color = "red" if d["is_illegal"] else "green"
        label = "ILLEGAL" if d["is_illegal"] else "COMPLIANT"
        popup_html = f"""
        <b>Status:</b> {label}<br>
        <b>Confidence:</b> {d['confidence']}<br>
        <b>Zone:</b> {d['zone']}<br>
        <b>Area:</b> {d['size']['estimated_area_m2']} m²<br>
        <b>Violations:</b> {', '.join(d['violations']) or 'None'}<br>
        <b>Permit:</b> {d['permit']['permit_id'] or 'None'}
        """
        folium.CircleMarker(
            location=[d["lat"], d["lon"]],
            radius=10,
            color=color,
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=280)
        ).add_to(m)

    return m


def metrics_row(detections: list):
    total     = len(detections)
    illegal   = sum(1 for d in detections if d["is_illegal"])
    compliant = total - illegal
    rate      = round((illegal / total * 100), 1) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total detected", total)
    c2.metric("Illegal",        illegal)
    c3.metric("Compliant",      compliant)
    c4.metric("Violation rate", f"{rate}%")


def detections_table(detections: list):
    if not detections:
        return
    rows = []
    for d in detections:
        rows.append({
            "Lat":        d["lat"],
            "Lon":        d["lon"],
            "Status":     "Illegal" if d["is_illegal"] else "Compliant",
            "Confidence": d["confidence"],
            "Zone":       d["zone"],
            "Area (m²)":  d["size"]["estimated_area_m2"],
            "Violations": ", ".join(d["violations"]) or "—",
            "Permit ID":  d["permit"]["permit_id"] or "—"
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)


st.title("BillWatch — Illegal Billboard Detection")
st.caption("Lagos, Nigeria · AI-powered enforcement dashboard")
st.divider()

with st.sidebar:
    st.header("Controls")

    uploaded = st.file_uploader(
        "Upload image",
        type=["jpg", "jpeg", "png"],
        help="Street-view or satellite image"
    )

    lat = st.number_input("Latitude",  value=6.5244, format="%.6f")
    lon = st.number_input("Longitude", value=3.3792, format="%.6f")

    run   = st.button("Run detection", type="primary", use_container_width=True)
    clear = st.button("Clear results", use_container_width=True)

    st.divider()
    st.header("Add permit")
    with st.form("permit_form"):
        pid    = st.text_input("Permit ID")
        owner  = st.text_input("Owner")
        plat   = st.number_input("Permit lat",  value=6.5244, format="%.6f")
        plon   = st.number_input("Permit lon",  value=3.3792, format="%.6f")
        addr   = st.text_input("Address")
        area   = st.number_input("Area (m²)", value=20.0)
        expiry = st.date_input("Valid until")
        submit = st.form_submit_button("Add permit")

    if submit and pid:
        from src.legality.permit_checker import add_permit
        from datetime import datetime
        add_permit(pid, owner, plat, plon, addr, area,
                   datetime.combine(expiry, datetime.min.time()))
        st.success(f"Permit {pid} added.")

if clear:
    st.session_state.detections = []

if run and uploaded:
    import cv2
    import numpy as np
    from src.detection.detector import BillboardDetector
    from src.legality.classifier import classify

    detector = BillboardDetector()

    file_bytes = np.frombuffer(uploaded.read(), np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    with st.spinner("Running detection..."):
        raw = detector.detect(image)

    if not raw:
        st.warning("No billboards detected in this image.")
    else:
        with st.spinner("Classifying legality..."):
            for d in raw:
                result = classify(d, lat, lon)
                st.session_state.detections.append(result)
        st.success(f"Found {len(raw)} billboard(s).")

st.subheader("Overview")
metrics_row(st.session_state.detections)

st.subheader("Map")
m = build_map(st.session_state.detections)
st_folium(m, width="100%", height=480)

st.subheader("Detections")
detections_table(st.session_state.detections)