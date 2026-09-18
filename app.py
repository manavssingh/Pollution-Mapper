"""
app.py -- Air & Noise Pollution Mapping Dashboard

Run locally with:
    streamlit run app.py

Reads and dynamically updates two CSV files:
    data/air_quality.csv     -- air quality observations (automated & live search)
    data/noise_readings.csv  -- primary field observations (or added via form)
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
            # Create a clean concise name (e.g. "Connaught Place, New Delhi")
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


def append_air_reading(locality: str, lat: float, lon: float, aqi: float) -> None:
    """Append a fetched air quality observation to data/air_quality.csv."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = AIR_CSV_PATH.exists() and AIR_CSV_PATH.stat().st_size > 0
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with open(AIR_CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["locality", "lat", "lon", "aqi", "fetched_at"])
        writer.writerow([locality, lat, lon, int(round(aqi)), now_iso])


def append_noise_reading(locality: str, lat: float, lon: float, decibel: float,
                         date_val: str, time_of_day: str, notes: str) -> None:
    """Append a new noise observation to data/noise_readings.csv."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = NOISE_CSV_PATH.exists() and NOISE_CSV_PATH.stat().st_size > 0

    with open(NOISE_CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["locality", "lat", "lon", "decibel", "date_recorded", "time_of_day", "notes"])
        writer.writerow([locality, lat, lon, decibel, date_val, time_of_day, notes])


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


# ---------------- State Management ----------------
if "map_center" not in st.session_state:
    st.session_state.map_center = None
if "map_zoom" not in st.session_state:
    st.session_state.map_zoom = None
if "last_searched" not in st.session_state:
    st.session_state.last_searched = ""
if "sidebar_lat" not in st.session_state:
    st.session_state.sidebar_lat = 18.5204
if "sidebar_lon" not in st.session_state:
    st.session_state.sidebar_lon = 73.8567
if "sidebar_locality" not in st.session_state:
    st.session_state.sidebar_locality = ""

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("⚙️ Controls & Entry")

    if st.button("🔄 Refresh Data", width="stretch"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.subheader("➕ Add Noise Observation")
    st.caption("Contribute a primary decibel reading for any locality.")

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
        form_notes = st.text_input("Notes / Context", placeholder="e.g. Heavy traffic, construction near road")

        submitted = st.form_submit_button("Submit Reading", width="stretch")
        if submitted:
            if not form_locality.strip():
                st.error("Please enter a locality name.")
            else:
                append_noise_reading(
                    form_locality.strip(),
                    form_lat,
                    form_lon,
                    form_db,
                    str(form_date),
                    form_time,
                    form_notes.strip()
                )
                st.cache_data.clear()
                st.session_state.map_center = {"lat": form_lat, "lon": form_lon}
                st.session_state.map_zoom = 12
                st.success(f"Added noise reading for {form_locality}!")
                st.rerun()

    st.markdown("---")
    st.info("💡 **Tip**: Stand still for 30–60 seconds when recording noise levels with a decibel meter.")


# ---------------- Header & Live Search ----------------
st.title("🌍 Air & Noise Pollution Mapping Dashboard")
st.caption("Locality-level environmental monitoring, global search, and comparative analysis")

# ---------------- Global City/Locality Search Bar ----------------
search_container = st.container()
with search_container:
    col_s1, col_s2 = st.columns([4, 1])
    with col_s1:
        search_query = st.text_input(
            "🔍 Search ANY City or Locality in the World to Map It:",
            placeholder="Type any city or area (e.g. Delhi, Mumbai, Bengaluru, New York, London, Tokyo, Paris)...",
            label_visibility="visible"
        )
    with col_s2:
        st.write("")  # align with input
        st.write("")
        search_btn = st.button("Search & Map", width="stretch")

    if search_btn and search_query.strip():
        with st.spinner(f"Finding and fetching live data for '{search_query}'..."):
            lat, lon, resolved_name = geocode_location(search_query)
            if lat is not None and lon is not None:
                aqi, pm25, pm10 = fetch_live_aqi(lat, lon)
                if aqi is not None:
                    append_air_reading(resolved_name, lat, lon, aqi)
                    st.cache_data.clear()
                    st.session_state.map_center = {"lat": lat, "lon": lon}
                    st.session_state.map_zoom = 12
                    st.session_state.last_searched = resolved_name
                    st.session_state.sidebar_lat = lat
                    st.session_state.sidebar_lon = lon
                    st.session_state.sidebar_locality = resolved_name

                    pm_info = f" | PM2.5: {pm25} µg/m³ | PM10: {pm10} µg/m³" if pm25 is not None else ""
                    st.success(
                        f"📍 Located **{resolved_name}** ({lat:.4f}, {lon:.4f})! "
                        f"Current AQI: **{int(round(aqi))}** ({aqi_label(aqi)}){pm_info}. "
                        "The map has been centered on this area."
                    )
                    st.rerun()
                else:
                    st.session_state.map_center = {"lat": lat, "lon": lon}
                    st.session_state.map_zoom = 12
                    st.session_state.sidebar_lat = lat
                    st.session_state.sidebar_lon = lon
                    st.session_state.sidebar_locality = resolved_name
                    st.warning(f"Located {resolved_name}, but live AQI data was unavailable. Map centered on coordinates.")
                    st.rerun()
            else:
                st.error(f"Could not find coordinates for '{search_query}'. Please check the spelling or try a larger nearby city.")

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

# ---------------- Key Metric Cards ----------------
m1, m2, m3, m4 = st.columns(4)

total_localities = len(set(latest_air["locality"].tolist() + noise_df["locality"].tolist()))
m1.metric("Total Localities", total_localities)

if not latest_air.empty:
    avg_aqi = latest_air["aqi"].mean()
    m2.metric("Average AQI", f"{avg_aqi:.0f}", aqi_label(avg_aqi), delta_color="inverse")
    worst_station = latest_air.loc[latest_air["aqi"].idxmax()]
    m4.metric("Highest AQI Hotspot", f"{worst_station['aqi']:.0f}", worst_station["locality"], delta_color="inverse")
else:
    m2.metric("Average AQI", "—")
    m4.metric("Highest AQI Hotspot", "—")

if not noise_df.empty:
    avg_noise = noise_df["decibel"].mean()
    who_delta = f"{avg_noise - 55:+.1f} dB vs WHO limit (55 dB)"
    m3.metric("Average Noise Level", f"{avg_noise:.1f} dB", who_delta, delta_color="inverse")
else:
    m3.metric("Average Noise Level", "—")

st.divider()

# ---------------- Interactive Map Controls ----------------
st.subheader("Interactive Geographic Map")

col_m1, col_m2 = st.columns([2, 3])
with col_m1:
    map_choice = st.radio(
        "Layer to Display:",
        ["Air Quality (AQI)", "Noise Level (dB)"],
        horizontal=True
    )

with col_m2:
    # Build list of unique localities to allow quick jump
    all_places = sorted(list(set(latest_air["locality"].tolist() + noise_df["locality"].tolist())))
    focus_options = ["All Localities (Auto-fit)"] + all_places
    selected_focus = st.selectbox("📍 Jump Map To Locality:", focus_options, index=0)

    if selected_focus != "All Localities (Auto-fit)":
        # Find coordinates of selected locality
        row_air = latest_air[latest_air["locality"] == selected_focus]
        row_noise = noise_df[noise_df["locality"] == selected_focus]
        if not row_air.empty:
            target_lat = float(row_air.iloc[0]["lat"])
            target_lon = float(row_air.iloc[0]["lon"])
            st.session_state.map_center = {"lat": target_lat, "lon": target_lon}
            st.session_state.map_zoom = 12
        elif not row_noise.empty:
            target_lat = float(row_noise.iloc[0]["lat"])
            target_lon = float(row_noise.iloc[0]["lon"])
            st.session_state.map_center = {"lat": target_lat, "lon": target_lon}
            st.session_state.map_zoom = 12

# ---------------- Render Map ----------------
if map_choice == "Air Quality (AQI)":
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
        fig.update_traces(marker=dict(size=14, opacity=0.85))

        layout_kwargs = {
            "map_style": "open-street-map",
            "margin": dict(l=0, r=0, t=0, b=0),
        }
        if st.session_state.map_center:
            layout_kwargs["map_center"] = st.session_state.map_center
            layout_kwargs["map_zoom"] = st.session_state.map_zoom or 11
        else:
            layout_kwargs["map_zoom"] = 10

        fig.update_layout(**layout_kwargs)
        st.plotly_chart(fig, width="stretch")
else:
    if noise_df.empty:
        st.info("No noise readings recorded yet. Submit one using the sidebar form!")
    else:
        fig = px.scatter_map(
            noise_df,
            lat="lat",
            lon="lon",
            color="decibel",
            hover_name="locality",
            hover_data={"decibel": True, "time_of_day": True, "notes": True, "lat": False, "lon": False},
            color_continuous_scale="RdYlGn_r",
            range_color=(30, 95),
            height=540,
        )
        fig.update_traces(marker=dict(size=14, opacity=0.85))

        layout_kwargs = {
            "map_style": "open-street-map",
            "margin": dict(l=0, r=0, t=0, b=0),
        }
        if st.session_state.map_center:
            layout_kwargs["map_center"] = st.session_state.map_center
            layout_kwargs["map_zoom"] = st.session_state.map_zoom or 11
        else:
            layout_kwargs["map_zoom"] = 10

        fig.update_layout(**layout_kwargs)
        st.plotly_chart(fig, width="stretch")

st.divider()

# ---------------- Comparative Charts ----------------
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
    if noise_df.empty:
        st.info("No noise data yet.")
    else:
        avg_noise_df = noise_df.groupby("locality", as_index=False)["decibel"].mean()
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
    tab1, tab2 = st.tabs(["Air Quality Records", "Noise Level Records"])

    with tab1:
        st.dataframe(air_df, width="stretch")
        if not air_df.empty:
            csv_air = air_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Air Quality CSV", data=csv_air, file_name="air_quality_data.csv", mime="text/csv")

    with tab2:
        st.dataframe(noise_df, width="stretch")
        if not noise_df.empty:
            csv_noise = noise_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Noise Readings CSV", data=csv_noise, file_name="noise_readings_data.csv", mime="text/csv")
