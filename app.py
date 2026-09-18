"""
app.py -- Air & Noise Pollution Mapping Dashboard

Run locally with:
    streamlit run app.py

Reads two CSV files:
    data/air_quality.csv     -- created/updated by fetch_air_quality.py
    data/noise_readings.csv  -- primary field observations (or added via sidebar form)
"""

import csv
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Air & Noise Pollution Mapper", page_icon="🌍", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
AIR_CSV_PATH = DATA_DIR / "air_quality.csv"
NOISE_CSV_PATH = DATA_DIR / "noise_readings.csv"

AQI_BANDS = [
    (0, 50, "Good"),
    (51, 100, "Moderate"),
    (101, 150, "Unhealthy for sensitive groups"),
    (151, 200, "Unhealthy"),
    (201, 300, "Very unhealthy"),
    (301, 500, "Hazardous"),
]


def aqi_label(aqi: float) -> str:
    """Return the descriptive health category for a given AQI value."""
    if pd.isna(aqi):
        return "Unknown"
    for low, high, label in AQI_BANDS:
        if low <= aqi <= high:
            return label
    return "Hazardous (500+)" if aqi > 500 else "Unknown"


@st.cache_data(ttl=3600)
def load_air_data() -> pd.DataFrame:
    """Load air quality readings and return a cleaned DataFrame."""
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
    """Load noise level observations and return a cleaned DataFrame."""
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


def append_noise_reading(locality: str, lat: float, lon: float, decibel: float,
                         date_val: str, time_of_day: str, notes: str) -> None:
    """Append a newly submitted noise observation to the CSV."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = NOISE_CSV_PATH.exists() and NOISE_CSV_PATH.stat().st_size > 0

    with open(NOISE_CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["locality", "lat", "lon", "decibel", "date_recorded", "time_of_day", "notes"])
        writer.writerow([locality, lat, lon, decibel, date_val, time_of_day, notes])


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("⚙️ Controls & Entry")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.subheader("➕ Add Noise Observation")
    st.caption("Contribute a new primary reading from your sound meter.")

    with st.form("noise_entry_form", clear_on_submit=True):
        new_locality = st.text_input("Locality Name", placeholder="e.g. Market Signal, City Center")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            new_lat = st.number_input("Latitude", value=18.5204, format="%.4f")
        with col_c2:
            new_lon = st.number_input("Longitude", value=73.8567, format="%.4f")

        new_db = st.slider("Sound Level (dB)", min_value=30.0, max_value=120.0, value=65.0, step=0.5)
        new_time = st.selectbox("Time of Day", ["Morning", "Afternoon", "Evening", "Night"])
        new_date = st.date_input("Date Recorded", value=date.today())
        new_notes = st.text_input("Notes / Context", placeholder="e.g. Heavy commercial traffic, honking")

        submitted = st.form_submit_button("Submit Reading", use_container_width=True)
        if submitted:
            if not new_locality.strip():
                st.error("Please enter a locality name.")
            else:
                append_noise_reading(
                    new_locality.strip(),
                    new_lat,
                    new_lon,
                    new_db,
                    str(new_date),
                    new_time,
                    new_notes.strip()
                )
                st.cache_data.clear()
                st.success(f"Added reading for {new_locality}!")
                st.rerun()

    st.markdown("---")
    st.info("💡 **Tip**: Stand still for 30-60 seconds when recording noise levels with a decibel meter.")


# ---------------- Load Data ----------------
air_df = load_air_data()
noise_df = load_noise_data()

st.title("🌍 Air & Noise Pollution Mapping Dashboard")
st.caption("Locality-level environmental monitoring and comparative analysis")

if air_df.empty and noise_df.empty:
    st.warning(
        "No data available yet. Run `python fetch_air_quality.py` for air quality, "
        "or submit readings using the sidebar form to populate the dashboard."
    )
    st.stop()

# Compute latest snapshot per station
latest_air = (
    air_df.sort_values("fetched_at").groupby("locality").tail(1).copy()
    if not air_df.empty else air_df
)

# ---------------- Key Metric Cards ----------------
m1, m2, m3, m4 = st.columns(4)

total_localities = len(set(latest_air["locality"].tolist() + noise_df["locality"].tolist()))
m1.metric("Localities Monitored", total_localities)

if not latest_air.empty:
    avg_aqi = latest_air["aqi"].mean()
    m2.metric("Average AQI", f"{avg_aqi:.0f}", aqi_label(avg_aqi), delta_color="inverse")
    worst_station = latest_air.loc[latest_air["aqi"].idxmax()]
    m4.metric("Highest AQI Locality", f"{worst_station['aqi']:.0f}", worst_station["locality"], delta_color="inverse")
else:
    m2.metric("Average AQI", "—")
    m4.metric("Highest AQI Locality", "—")

if not noise_df.empty:
    avg_noise = noise_df["decibel"].mean()
    who_delta = f"{avg_noise - 55:+.1f} dB vs WHO day limit (55 dB)"
    m3.metric("Average Noise Level", f"{avg_noise:.1f} dB", who_delta, delta_color="inverse")
else:
    m3.metric("Average Noise Level", "—")

st.divider()

# ---------------- Interactive Map ----------------
st.subheader("Geographic Pollution Map")
map_choice = st.radio(
    "Select map layer:",
    ["Air Quality (AQI)", "Noise Level (dB)"],
    horizontal=True
)

if map_choice == "Air Quality (AQI)":
    if latest_air.empty:
        st.info("Run `python fetch_air_quality.py` to populate the air quality map.")
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
            zoom=10,
            height=530,
        )
        fig.update_traces(marker=dict(size=14))
        fig.update_layout(map_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
else:
    if noise_df.empty:
        st.info("Add observations via the sidebar form or `data/noise_readings.csv` to populate the noise map.")
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
            zoom=10,
            height=530,
        )
        fig.update_traces(marker=dict(size=14))
        fig.update_layout(map_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig_air, use_container_width=True)

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
        st.plotly_chart(fig_noise, use_container_width=True)

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
            title="Daily Average AQI Trends"
        )
        fig_trend.update_layout(xaxis_title="Date", yaxis_title="Average AQI")
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.caption(
            "Currently only one day of readings is available. Run `fetch_air_quality.py` "
            "across multiple days (or use the GitHub Actions automated workflow) to unlock trend analysis."
        )

st.divider()

# ---------------- Reference Guide & Standards ----------------
with st.expander("📖 Reference Standards & Health Thresholds"):
    st.markdown(
        """
### Air Quality Index (AQI) Reference (WAQI / US-EPA Standard)

| AQI Range | Category | Health Implications |
|---|---|---|
| **0 - 50** | 🟢 Good | Air quality is satisfactory, and air pollution poses little or no risk. |
| **51 - 100** | 🟡 Moderate | Acceptable air quality; some pollutants may pose moderate health concern for sensitive individuals. |
| **101 - 150** | 🟠 Unhealthy for Sensitive Groups | Members of sensitive groups may experience health effects; general public is less likely to be affected. |
| **151 - 200** | 🔴 Unhealthy | Everyone may begin to experience health effects; sensitive groups may experience more serious health effects. |
| **201 - 300** | 🟣 Very Unhealthy | Health alert: The risk of health effects is increased for everyone. |
| **301+** | 🟤 Hazardous | Health warning of emergency conditions; everyone is more likely to be affected. |

---

### Environmental Noise Levels (WHO Guidelines)

| Level (dB) | Context / Reference | Assessment |
|---|---|---|
| **~30 dB** | Quiet bedroom, soft whisper | Negligible impact |
| **~50 - 55 dB** | Recommended WHO daytime limit for outdoor residential living | Comfortable threshold |
| **~60 - 65 dB** | Normal conversation, light commercial district | Moderate annoyance |
| **~70 - 80 dB** | Heavy arterial road traffic, bus stations | Noticeable strain / stress |
| **85+ dB** | Construction, sirens, continuous heavy industrial noise | Risk of hearing impairment over extended exposure |
"""
    )

# ---------------- Raw Data & Export ----------------
with st.expander("📊 View & Export Raw Data"):
    tab1, tab2 = st.tabs(["Air Quality Data", "Noise Observations"])

    with tab1:
        st.dataframe(air_df, use_container_width=True)
        if not air_df.empty:
            csv_air = air_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Air Quality CSV", data=csv_air, file_name="air_quality_export.csv", mime="text/csv")

    with tab2:
        st.dataframe(noise_df, use_container_width=True)
        if not noise_df.empty:
            csv_noise = noise_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Noise Readings CSV", data=csv_noise, file_name="noise_readings_export.csv", mime="text/csv")
