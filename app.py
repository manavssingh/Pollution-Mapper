"""
app.py -- Air & Noise Pollution Mapping Dashboard

Run locally with:
    streamlit run app.py

Reads and dynamically updates two CSV files:
    data/air_quality.csv     -- air quality observations (automated, live search & auto-geolocated)
    data/noise_readings.csv  -- noise observations (field measurements & urban baseline models)
"""

import csv
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Air & Noise Pollution Mapper", page_icon="🌍", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
AIR_CSV_PATH = DATA_DIR / "air_quality.csv"
NOISE_CSV_PATH = DATA_DIR / "noise_readings.csv"

AQI_BANDS = [
    (0, 50, "Good", "#00E400"),
    (51, 100, "Moderate", "#FFFF00"),
    (101, 150, "Unhealthy for sensitive groups", "#FF7E00"),
    (151, 200, "Unhealthy", "#FF0000"),
    (201, 300, "Very unhealthy", "#8F3F97"),
    (301, 500, "Hazardous", "#7E0023"),
]


def aqi_label(aqi: float) -> str:
    """Return the descriptive health category for a given AQI value."""
    if pd.isna(aqi):
        return "Unknown"
    for low, high, label, _ in AQI_BANDS:
        if low <= aqi <= high:
            return label
    return "Hazardous (500+)" if aqi > 500 else "Unknown"


def estimate_urban_noise(hour: int) -> float:
    """
    Estimate typical urban commercial/arterial road ambient noise (dB)
    based on diurnal traffic distribution (WHO urban acoustic guidelines).
    """
    if 7 <= hour < 11:
        return 73.5  # Morning peak traffic
    elif 11 <= hour < 17:
        return 69.5  # Afternoon commercial activity
    elif 17 <= hour < 21:
        return 74.0  # Evening rush hour
    elif 21 <= hour < 24:
        return 62.0  # Late evening tapering
    else:
        return 52.5  # Night residential baseline


def detect_client_location():
    """Detect the visitor's live city and coordinates via IP geolocation."""
    client_ip = None
    try:
        # Check Streamlit request headers if deployed on cloud
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            headers = st.context.headers
            forwarded = headers.get("X-Forwarded-For") or headers.get("x-forwarded-for")
            if forwarded:
                client_ip = forwarded.split(",")[0].strip()
    except Exception:
        pass

    try:
        url = f"http://ip-api.com/json/{client_ip}" if client_ip else "http://ip-api.com/json/"
        resp = requests.get(url, timeout=3.5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                city = data.get("city")
                lat = float(data.get("lat"))
                lon = float(data.get("lon"))
                region = data.get("regionName", "")
                country = data.get("country", "")
                full_name = f"{city}, {region}" if region else (f"{city}, {country}" if country else city)
                return city, lat, lon, full_name
    except Exception:
        pass
    return None, None, None, None


def geocode_location(query: str):
    """Find latitude, longitude, and formatted name for any city/area worldwide."""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "AirNoisePollutionMapper/1.0"}
        params = {"q": query.strip(), "format": "json", "limit": 1}
        resp = requests.get(url, params=params, headers=headers, timeout=6)
        if resp.status_code == 200 and resp.json():
            item = resp.json()[0]
            lat = float(item["lat"])
            lon = float(item["lon"])
            raw_name = item.get("display_name", query)
            parts = [p.strip() for p in raw_name.split(",")]
            short_name = ", ".join(parts[:2]) if len(parts) >= 2 else raw_name
            return lat, lon, short_name
    except Exception:
        pass
    return None, None, None


def fetch_live_aqi(lat: float, lon: float):
    """Fetch live AQI from Open-Meteo Air Quality API (free, worldwide coverage)."""
    try:
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "us_aqi,pm2_5,pm10",
        }
        resp = requests.get(url, params=params, timeout=6)
        if resp.status_code == 200:
            current = resp.json().get("current", {})
            aqi = current.get("us_aqi")
            if aqi is not None:
                return float(aqi), current.get("pm2_5"), current.get("pm10")
    except Exception:
        pass
    return None, None, None


def save_air_reading(locality: str, lat: float, lon: float, aqi: float) -> None:
    """Save or update an air quality reading to data/air_quality.csv (avoiding duplicates for today)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today_str = date.today().isoformat()
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

    records = []
    updated = False
    if AIR_CSV_PATH.exists() and AIR_CSV_PATH.stat().st_size > 0:
        with open(AIR_CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r.get("locality") == locality and r.get("fetched_at", "").startswith(today_str):
                    r["aqi"] = str(int(round(aqi)))
                    r["lat"] = f"{lat:.4f}"
                    r["lon"] = f"{lon:.4f}"
                    r["fetched_at"] = now_iso
                    updated = True
                records.append(r)

    if not updated:
        records.append({
            "locality": locality,
            "lat": f"{lat:.4f}",
            "lon": f"{lon:.4f}",
            "aqi": str(int(round(aqi))),
            "fetched_at": now_iso
        })

    with open(AIR_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["locality", "lat", "lon", "aqi", "fetched_at"])
        writer.writeheader()
        writer.writerows(records)


def save_noise_reading(locality: str, lat: float, lon: float, decibel: float,
                       date_val: str, time_of_day: str, notes: str) -> None:
    """Save or update a noise reading in data/noise_readings.csv."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    updated = False

    if NOISE_CSV_PATH.exists() and NOISE_CSV_PATH.stat().st_size > 0:
        with open(NOISE_CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r.get("locality") == locality and r.get("date_recorded") == date_val:
                    r["decibel"] = str(decibel)
                    r["lat"] = f"{lat:.4f}"
                    r["lon"] = f"{lon:.4f}"
                    r["time_of_day"] = time_of_day
                    r["notes"] = notes
                    updated = True
                records.append(r)

    if not updated:
        records.append({
            "locality": locality,
            "lat": f"{lat:.4f}",
            "lon": f"{lon:.4f}",
            "decibel": str(decibel),
            "date_recorded": date_val,
            "time_of_day": time_of_day,
            "notes": notes
        })

    with open(NOISE_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["locality", "lat", "lon", "decibel", "date_recorded", "time_of_day", "notes"])
        writer.writeheader()
        writer.writerows(records)


@st.cache_data(ttl=3600)
def load_air_data() -> pd.DataFrame:
    """Load air quality readings from CSV."""
    try:
        if not AIR_CSV_PATH.exists() or AIR_CSV_PATH.stat().st_size == 0:
            return pd.DataFrame(columns=["locality", "lat", "lon", "aqi", "fetched_at", "date", "category"])

        df = pd.read_csv(AIR_CSV_PATH)
        df["aqi"] = pd.to_numeric(df["aqi"], errors="coerce")
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
        df["fetched_at"] = pd.to_datetime(df["fetched_at"], errors="coerce")
        df = df.dropna(subset=["locality", "lat", "lon", "aqi", "fetched_at"]).copy()
        df["date"] = df["fetched_at"].dt.date
        df["category"] = df["aqi"].apply(aqi_label)
        return df
    except Exception:
        return pd.DataFrame(columns=["locality", "lat", "lon", "aqi", "fetched_at", "date", "category"])


@st.cache_data(ttl=3600)
def load_noise_data() -> pd.DataFrame:
    """Load noise level readings from CSV."""
    try:
        if not NOISE_CSV_PATH.exists() or NOISE_CSV_PATH.stat().st_size == 0:
            return pd.DataFrame(columns=["locality", "lat", "lon", "decibel", "date_recorded", "time_of_day", "notes"])

        df = pd.read_csv(NOISE_CSV_PATH)
        df["decibel"] = pd.to_numeric(df["decibel"], errors="coerce")
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
        return df.dropna(subset=["locality", "lat", "lon", "decibel"]).copy()
    except Exception:
        return pd.DataFrame(columns=["locality", "lat", "lon", "decibel", "date_recorded", "time_of_day", "notes"])


# ---------------- State Management & Automatic Geolocation ----------------
if "map_center" not in st.session_state:
    st.session_state.map_center = None
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = None
if "user_city" not in st.session_state:
    st.session_state.user_city = None
if "user_full_location" not in st.session_state:
    st.session_state.user_full_location = None
if "geo_initialized" not in st.session_state:
    st.session_state.geo_initialized = False
if "sidebar_lat" not in st.session_state:
    st.session_state.sidebar_lat = 18.5204
if "sidebar_lon" not in st.session_state:
    st.session_state.sidebar_lon = 73.8567
if "sidebar_locality" not in st.session_state:
    st.session_state.sidebar_locality = ""

# Auto-detect live user position on initial visit
if not st.session_state.geo_initialized:
    detected_city, det_lat, det_lon, det_fullname = detect_client_location()
    if detected_city and det_lat and det_lon:
        st.session_state.user_city = detected_city
        st.session_state.user_full_location = det_fullname
        st.session_state.map_center = {"lat": det_lat, "lon": det_lon}
        st.session_state.map_zoom = 12
        st.session_state.sidebar_lat = det_lat
        st.session_state.sidebar_lon = det_lon
        st.session_state.sidebar_locality = det_fullname

        # Automatically fetch and log live environmental readings for the user's city
        live_aqi, live_pm25, live_pm10 = fetch_live_aqi(det_lat, det_lon)
        if live_aqi is not None:
            cur_hr = datetime.now().hour
            cur_noise = estimate_urban_noise(cur_hr)
            time_lbl = "Morning" if 6 <= cur_hr < 12 else ("Afternoon" if 12 <= cur_hr < 17 else ("Evening" if 17 <= cur_hr < 21 else "Night"))

            save_air_reading(det_fullname, det_lat, det_lon, live_aqi)
            save_noise_reading(
                det_fullname,
                det_lat,
                det_lon,
                cur_noise,
                date.today().isoformat(),
                time_lbl,
                f"Estimated Baseline (Live Visitor Local Model, {time_lbl})"
            )
            st.cache_data.clear()

    st.session_state.geo_initialized = True

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("⚙️ Controls & Data Entry")

    if st.button("🔄 Refresh Data", width="stretch"):
        st.cache_data.clear()
        st.rerun()

    if st.button("🎯 Jump to My Live Location", width="stretch"):
        d_city, d_lat, d_lon, d_name = detect_client_location()
        if d_city and d_lat and d_lon:
            st.session_state.user_city = d_city
            st.session_state.user_full_location = d_name
            st.session_state.map_center = {"lat": d_lat, "lon": d_lon}
            st.session_state.map_zoom = 12
            st.session_state.sidebar_lat = d_lat
            st.session_state.sidebar_lon = d_lon
            st.session_state.sidebar_locality = d_name
            st.success(f"Focused on your live location: {d_name}!")
            st.rerun()

    st.markdown("---")
    st.subheader("➕ Submit Field Noise Reading")
    st.caption("Contribute a primary decibel reading from your physical sound meter.")

    with st.form("noise_entry_form", clear_on_submit=False):
        form_locality = st.text_input("Locality Name", value=st.session_state.sidebar_locality, placeholder="e.g. Connaught Place, Delhi")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            form_lat = st.number_input("Latitude", value=float(st.session_state.sidebar_lat), format="%.4f")
        with col_c2:
            form_lon = st.number_input("Longitude", value=float(st.session_state.sidebar_lon), format="%.4f")

        form_db = st.slider("Sound Level (dB)", min_value=30.0, max_value=120.0, value=68.0, step=0.5)
        form_time = st.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night"])
        form_date = st.date_input("Date Recorded", value=date.today())
        form_notes = st.text_input("Notes / Context", placeholder="e.g. Heavy commercial traffic, honking")

        submitted = st.form_submit_button("Submit Verified Field Reading", width="stretch")
        if submitted:
            if not form_locality.strip():
                st.error("Please enter a locality name.")
            else:
                note_text = form_notes.strip() if form_notes.strip() else "Verified field measurement"
                save_noise_reading(
                    form_locality.strip(),
                    form_lat,
                    form_lon,
                    form_db,
                    str(form_date),
                    form_time,
                    f"Field Measurement: {note_text}"
                )
                st.cache_data.clear()
                st.session_state.map_center = {"lat": form_lat, "lon": form_lon}
                st.session_state.map_zoom = 12
                st.success(f"Added verified reading for {form_locality}!")
                st.rerun()

    st.markdown("---")
    st.info("💡 **Methodology**: Field readings are saved as *Primary Measurements*, while unmonitored global cities use *WHO Urban Baseline Models*.")


# ---------------- Header & Geolocation Banner ----------------
st.title("🌍 Air & Noise Pollution Mapping Dashboard")
st.caption("Locality-level environmental monitoring, live auto-localization, and multi-pollutant surveillance")

if st.session_state.user_full_location:
    st.info(f"📍 **Auto-Detected Live Position**: You are viewing data focused on **{st.session_state.user_full_location}**. The map and local indicators below are centered on your area.")

# ---------------- Global City/Locality Search Bar ----------------
search_container = st.container()
with search_container:
    col_s1, col_s2 = st.columns([4, 1])
    with col_s1:
        search_query = st.text_input(
            "🔍 Search ANY City or Locality in the World (e.g. Delhi, London, Mumbai, New York, Tokyo):",
            placeholder="Type any city or neighborhood name...",
            label_visibility="visible"
        )
    with col_s2:
        st.write("")
        st.write("")
        search_btn = st.button("Search & Map Both", width="stretch")

    if search_btn and search_query.strip():
        with st.spinner(f"Geocoding and retrieving live environmental data for '{search_query}'..."):
            lat, lon, resolved_name = geocode_location(search_query)
            if lat is not None and lon is not None:
                aqi, pm25, pm10 = fetch_live_aqi(lat, lon)
                current_hour = datetime.now().hour
                est_noise = estimate_urban_noise(current_hour)
                time_label = "Morning" if 6 <= current_hour < 12 else ("Afternoon" if 12 <= current_hour < 17 else ("Evening" if 17 <= current_hour < 21 else "Night"))

                if aqi is not None:
                    save_air_reading(resolved_name, lat, lon, aqi)
                    save_noise_reading(
                        resolved_name,
                        lat,
                        lon,
                        est_noise,
                        date.today().isoformat(),
                        time_label,
                        f"Estimated Baseline (WHO Urban Traffic Model, {time_label})"
                    )

                    st.cache_data.clear()
                    st.session_state.map_center = {"lat": lat, "lon": lon}
                    st.session_state.map_zoom = 12
                    st.session_state.sidebar_lat = lat
                    st.session_state.sidebar_lon = lon
                    st.session_state.sidebar_locality = resolved_name

                    pm_info = f" | PM2.5: {pm25} µg/m³" if pm25 is not None else ""
                    st.success(
                        f"📍 Located **{resolved_name}** ({lat:.4f}, {lon:.4f})! "
                        f"Live AQI: **{int(round(aqi))}** ({aqi_label(aqi)}){pm_info} | "
                        f"Urban Noise Baseline: **{est_noise:.1f} dB**. "
                        "Mapped below!"
                    )
                    st.rerun()
                else:
                    st.session_state.map_center = {"lat": lat, "lon": lon}
                    st.session_state.map_zoom = 12
                    st.warning(f"Located {resolved_name}, but live AQI was unreachable. Map centered on coordinates.")
                    st.rerun()
            else:
                st.error(f"Could not find coordinates for '{search_query}'. Please verify spelling.")

st.divider()

# ---------------- Load Data ----------------
air_df = load_air_data()
noise_df = load_noise_data()

if air_df.empty and noise_df.empty:
    st.warning("No data available yet. Use the search bar above to map any city!")
    st.stop()

# Compute latest snapshot per locality for air
latest_air = (
    air_df.sort_values("fetched_at").groupby("locality").tail(1).copy()
    if not air_df.empty else air_df
)

# Compute latest snapshot per locality for noise
latest_noise = (
    noise_df.sort_values("date_recorded").groupby("locality").tail(1).copy()
    if not noise_df.empty else noise_df
)

# Build a Unified Combined Dataset for simultaneous mapping
combined_df = pd.merge(
    latest_air,
    latest_noise[["locality", "decibel", "time_of_day", "notes"]],
    on="locality",
    how="outer"
)

# Fill missing coordinates if locality exists in only one
for idx, row in combined_df.iterrows():
    if pd.isna(row["lat"]) or pd.isna(row["lon"]):
        match_noise = latest_noise[latest_noise["locality"] == row["locality"]]
        if not match_noise.empty:
            combined_df.at[idx, "lat"] = match_noise.iloc[0]["lat"]
            combined_df.at[idx, "lon"] = match_noise.iloc[0]["lon"]

combined_df["aqi_display"] = combined_df["aqi"].apply(lambda x: f"{int(round(x))} ({aqi_label(x)})" if pd.notna(x) else "No Air Data")
combined_df["noise_display"] = combined_df["decibel"].apply(lambda x: f"{x:.1f} dB" if pd.notna(x) else "No Noise Data")
combined_df["source_display"] = combined_df["notes"].apply(
    lambda x: "Verified Field Data" if "Field Measurement" in str(x) else ("Estimated Urban Model" if "Estimated" in str(x) else "Field Observation")
)

# ---------------- Key Metric Cards (Personalized to User Locality) ----------------
m1, m2, m3, m4 = st.columns(4)

total_localities = len(combined_df)
m1.metric("Localities Monitored", total_localities)

# Check if user's locality is available
user_air_row = latest_air[latest_air["locality"] == st.session_state.user_full_location] if st.session_state.user_full_location else pd.DataFrame()
user_noise_row = latest_noise[latest_noise["locality"] == st.session_state.user_full_location] if st.session_state.user_full_location else pd.DataFrame()

if not user_air_row.empty:
    local_aqi = user_air_row.iloc[0]["aqi"]
    m2.metric(f"Your City AQI ({st.session_state.user_city})", f"{local_aqi:.0f}", aqi_label(local_aqi), delta_color="inverse")
elif not latest_air.empty:
    avg_aqi = latest_air["aqi"].mean()
    m2.metric("Average AQI", f"{avg_aqi:.0f}", aqi_label(avg_aqi), delta_color="inverse")
else:
    m2.metric("Average AQI", "—")

if not user_noise_row.empty:
    local_noise = user_noise_row.iloc[0]["decibel"]
    who_delta = f"{local_noise - 55:+.1f} dB vs WHO limit (55 dB)"
    m3.metric(f"Your City Noise ({st.session_state.user_city})", f"{local_noise:.1f} dB", who_delta, delta_color="inverse")
elif not latest_noise.empty:
    avg_noise = latest_noise["decibel"].mean()
    who_delta = f"{avg_noise - 55:+.1f} dB vs WHO limit (55 dB)"
    m3.metric("Average Noise Level", f"{avg_noise:.1f} dB", who_delta, delta_color="inverse")
else:
    m3.metric("Average Noise Level", "—")

if not latest_air.empty:
    worst_station = latest_air.loc[latest_air["aqi"].idxmax()]
    m4.metric("Highest Pollution Hotspot", f"{worst_station['aqi']:.0f}", worst_station["locality"], delta_color="inverse")
else:
    m4.metric("Highest Pollution Hotspot", "—")

st.divider()

# ---------------- Interactive Map Controls ----------------
st.subheader("Geographic Pollution Map")

col_m1, col_m2 = st.columns([3, 2])
with col_m1:
    map_choice = st.radio(
        "Map Layer to Display:",
        ["Combined (Air & Noise)", "Air Quality (AQI)", "Noise Level (dB)"],
        horizontal=True
    )

with col_m2:
    all_places = sorted(combined_df["locality"].dropna().unique().tolist())
    default_idx = 0
    if st.session_state.user_full_location and st.session_state.user_full_location in all_places:
        focus_options = ["Your Location: " + st.session_state.user_full_location, "All Localities (Auto-fit)"] + [p for p in all_places if p != st.session_state.user_full_location]
    else:
        focus_options = ["All Localities (Auto-fit)"] + all_places

    selected_focus = st.selectbox("📍 Jump Map Focus To:", focus_options, index=0)

    if selected_focus.startswith("Your Location: "):
        clean_name = selected_focus.replace("Your Location: ", "")
        target_row = combined_df[combined_df["locality"] == clean_name]
        if not target_row.empty and pd.notna(target_row.iloc[0]["lat"]):
            st.session_state.map_center = {"lat": float(target_row.iloc[0]["lat"]), "lon": float(target_row.iloc[0]["lon"])}
            st.session_state.map_zoom = 12
    elif selected_focus != "All Localities (Auto-fit)":
        target_row = combined_df[combined_df["locality"] == selected_focus]
        if not target_row.empty and pd.notna(target_row.iloc[0]["lat"]):
            st.session_state.map_center = {"lat": float(target_row.iloc[0]["lat"]), "lon": float(target_row.iloc[0]["lon"])}
            st.session_state.map_zoom = 12

# ---------------- Render Map ----------------
layout_kwargs = {
    "map_style": "open-street-map",
    "margin": dict(l=0, r=0, t=0, b=0),
}
if st.session_state.map_center:
    layout_kwargs["map_center"] = st.session_state.map_center
    layout_kwargs["map_zoom"] = st.session_state.map_zoom or 11
else:
    layout_kwargs["map_zoom"] = 10

if map_choice == "Combined (Air & Noise)":
    fig = px.scatter_map(
        combined_df.dropna(subset=["lat", "lon"]),
        lat="lat",
        lon="lon",
        color="aqi",
        hover_name="locality",
        hover_data={
            "aqi_display": True,
            "noise_display": True,
            "source_display": True,
            "notes": True,
            "aqi": False,
            "lat": False,
            "lon": False
        },
        labels={
            "aqi_display": "Air Quality",
            "noise_display": "Noise Level",
            "source_display": "Noise Type"
        },
        color_continuous_scale="RdYlGn_r",
        range_color=(0, 350),
        height=550,
        title="Simultaneous Air & Noise Pollution Map"
    )
    fig.update_traces(marker=dict(size=16, opacity=0.88))
    fig.update_layout(**layout_kwargs)
    st.plotly_chart(fig, width="stretch")

elif map_choice == "Air Quality (AQI)":
    if latest_air.empty:
        st.info("No air quality readings available. Search for a city above to add one!")
    else:
        fig = px.scatter_map(
            latest_air,
            lat="lat",
            lon="lon",
            color="aqi",
            hover_name="locality",
            hover_data={"category": True, "aqi": True, "lat": False, "lon": False},
            color_continuous_scale="RdYlGn_r",
            range_color=(0, 350),
            height=540,
        )
        fig.update_traces(marker=dict(size=15, opacity=0.85))
        fig.update_layout(**layout_kwargs)
        st.plotly_chart(fig, width="stretch")

else:  # Noise Level
    if latest_noise.empty:
        st.info("No noise readings recorded yet. Submit one using the sidebar form!")
    else:
        fig = px.scatter_map(
            latest_noise,
            lat="lat",
            lon="lon",
            color="decibel",
            hover_name="locality",
            hover_data={"decibel": True, "time_of_day": True, "notes": True, "lat": False, "lon": False},
            color_continuous_scale="RdYlGn_r",
            range_color=(30, 95),
            height=540,
        )
        fig.update_traces(marker=dict(size=15, opacity=0.85))
        fig.update_layout(**layout_kwargs)
        st.plotly_chart(fig, width="stretch")

st.divider()

# ---------------- Comparative Bar Charts ----------------
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("AQI by Locality")
    if latest_air.empty:
        st.info("No air quality data yet.")
    else:
        fig_air = px.bar(
            latest_air.sort_values("aqi", ascending=False),
            x="locality",
            y="aqi",
            color="aqi",
            text="category",
            color_continuous_scale="RdYlGn_r",
            range_color=(0, 350),
        )
        fig_air.update_traces(textposition="outside")
        fig_air.update_layout(showlegend=False, xaxis_tickangle=-40)
        st.plotly_chart(fig_air, width="stretch")

with col_b:
    st.subheader("Noise Level by Locality (dB)")
    if latest_noise.empty:
        st.info("No noise data yet.")
    else:
        avg_noise_df = latest_noise.groupby("locality", as_index=False)["decibel"].mean()
        fig_noise = px.bar(
            avg_noise_df.sort_values("decibel", ascending=False),
            x="locality",
            y="decibel",
            color="decibel",
            color_continuous_scale="RdYlGn_r",
            range_color=(30, 95),
        )
        fig_noise.update_layout(showlegend=False, xaxis_tickangle=-40)
        st.plotly_chart(fig_noise, width="stretch")

# ---------------- Air vs Noise Correlation Analysis ----------------
merged_corr = pd.merge(latest_air[["locality", "aqi"]], latest_noise[["locality", "decibel", "notes"]], on="locality").dropna()
if len(merged_corr) >= 2:
    st.divider()
    st.subheader("🔬 Environmental Correlation: Air Quality vs. Noise Level")
    st.caption("Investigating whether areas with elevated acoustic noise also experience higher air pollution levels.")

    col_corr1, col_corr2 = st.columns([3, 2])
    with col_corr1:
        fig_scatter = px.scatter(
            merged_corr,
            x="decibel",
            y="aqi",
            text="locality",
            color="aqi",
            color_continuous_scale="RdYlGn_r",
            labels={"decibel": "Sound Level (dB)", "aqi": "Air Quality Index (AQI)"},
            title="Locality Correlation: Sound Level vs. AQI"
        )
        fig_scatter.update_traces(textposition="top center", marker=dict(size=12))
        st.plotly_chart(fig_scatter, width="stretch")

    with col_corr2:
        st.markdown("#### Research Observations")
        corr_val = merged_corr["aqi"].corr(merged_corr["decibel"])
        st.metric("Pearson Correlation Coefficient (r)", f"{corr_val:+.2f}")
        if corr_val > 0.4:
            st.info("📈 **Positive Correlation Detected**: Localities experiencing heavy vehicular traffic consistently show both increased acoustic strain and elevated particulate pollution.")
        elif corr_val < -0.4:
            st.info("📉 **Negative Correlation**: Environmental patterns deviate between commercial hubs and residential microclimates.")
        else:
            st.info("⚖️ **Moderate / Localized Variance**: Noise and air pollution vary depending on industrial zoning and open-air ventilation.")

# ---------------- Trend Analysis ----------------
if not air_df.empty:
    st.divider()
    st.subheader("AQI Trend Over Time")
    if air_df["date"].nunique() > 1:
        trend = air_df.groupby(["date", "locality"], as_index=False)["aqi"].mean()
        fig_trend = px.line(
            trend,
            x="date",
            y="aqi",
            color="locality",
            markers=True,
            title="Daily Average AQI Trends Across Monitored Areas"
        )
        fig_trend.update_layout(xaxis_title="Date", yaxis_title="Average AQI")
        st.plotly_chart(fig_trend, width="stretch")
    else:
        st.caption(
            "Currently one day of readings is available. Continue searching cities or running "
            "`fetch_air_quality.py` across different days to visualize temporal trends."
        )

st.divider()

# ---------------- Reference Standards ----------------
with st.expander("📖 Reference Standards & Health Thresholds"):
    st.markdown(
        """
### Air Quality Index (AQI) Reference (US-EPA / WAQI Scale)

| AQI Range | Category | Health Advisory |
|---|---|---|
| **0 - 50** | 🟢 Good | Air quality is satisfactory; little or no health risk. |
| **51 - 100** | 🟡 Moderate | Acceptable air quality; slight risk for sensitive individuals. |
| **101 - 150** | 🟠 Unhealthy for Sensitive Groups | Sensitive groups may experience irritation; general public less affected. |
| **151 - 200** | 🔴 Unhealthy | Everyone may begin to experience health symptoms; outdoor exertion should be limited. |
| **201 - 300** | 🟣 Very Unhealthy | Health alert: Significantly increased risk for entire population. |
| **301+** | 🟤 Hazardous | Emergency warning: General public severely affected. |

---

### Environmental Noise Standards (WHO Guidelines)

| Level (dB) | Environmental Context | Assessment |
|---|---|---|
| **~30 dB** | Quiet rural night, bedroom | Minimal impact |
| **~50 - 55 dB** | Recommended WHO daytime upper limit for residential areas | Healthy living baseline |
| **~60 - 65 dB** | Standard conversational speech, shopping street | Moderate background strain |
| **~70 - 80 dB** | Major traffic artery, bus terminal, horn honking | Elevates stress & cardiovascular risk |
| **85+ dB** | Construction, jackhammers, sirens | High risk of acoustic damage with sustained exposure |
"""
    )

# ---------------- Raw Data & Export ----------------
with st.expander("📊 View & Export Raw Data"):
    tab1, tab2, tab3 = st.tabs(["Combined View", "Air Quality Records", "Noise Level Records"])

    with tab1:
        st.dataframe(combined_df[["locality", "lat", "lon", "aqi", "category", "decibel", "source_display", "notes"]], width="stretch")

    with tab2:
        st.dataframe(air_df, width="stretch")
        if not air_df.empty:
            csv_air = air_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Air Quality CSV", data=csv_air, file_name="air_quality_data.csv", mime="text/csv")

    with tab3:
        st.dataframe(noise_df, width="stretch")
        if not noise_df.empty:
            csv_noise = noise_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Noise Readings CSV", data=csv_noise, file_name="noise_readings_data.csv", mime="text/csv")
