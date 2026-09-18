"""
fetch_air_quality.py

Pulls REAL, current air-quality readings for every monitoring station
inside a bounding box (e.g. your city) from the free WAQI
(World Air Quality Index) API, and appends them to data/air_quality.csv.

Run this once to get today's snapshot, or run it once a day for a
couple of weeks so your dashboard can show a trend line over time.

--------------------------------------------------------------------
SETUP (do this before running):

1. Get a free token (just needs an email):
   https://aqicn.org/data-platform/token/

2. Either:
   a) paste it below where it says PASTE_YOUR_TOKEN_HERE, OR
   b) set it as an environment variable called WAQI_TOKEN
      (safer -- do this if you're pushing this repo to GitHub,
      so your token is never committed to the code)

3. Set BOUNDS to a box that covers your city / area of interest.
   Easiest way to find coordinates: open Google Maps, right-click
   the south-west corner of your area, copy the "lat, lon" that pops
   up, then do the same for the north-east corner.
--------------------------------------------------------------------
"""

import csv
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

WAQI_TOKEN = os.environ.get("WAQI_TOKEN", "PASTE_YOUR_TOKEN_HERE")

# (south_lat, west_lon, north_lat, east_lon)
# The example below roughly covers Pune, India -- CHANGE THIS to your city.
BOUNDS = "18.40,73.75,18.65,73.95"

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = str(BASE_DIR / "data" / "air_quality.csv")


def fetch_stations(bounds: str, token: str):
    """Ask WAQI for every station inside the bounding box."""
    url = "https://api.waqi.info/map/bounds/"
    response = requests.get(url, params={"latlng": bounds, "token": token}, timeout=15)
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "ok":
        raise RuntimeError(f"WAQI API returned an error: {payload}")

    return payload.get("data", [])


def save_to_csv(stations, path):
    """Append this run's readings to the CSV (creates it with a header the first time)."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    file_already_exists = os.path.isfile(path) and os.path.getsize(path) > 0
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_already_exists:
            writer.writerow(["locality", "lat", "lon", "aqi", "fetched_at"])

        rows_written = 0
        for station in stations:
            aqi = station.get("aqi")
            if aqi in ("-", None):
                continue  # this station didn't report a reading just now

            # Safe station extraction
            station_info = station.get("station")
            station_name = (
                station_info.get("name") if isinstance(station_info, dict) else None
            )
            lat = station.get("lat")
            lon = station.get("lon")

            if lat is None or lon is None:
                continue
            if not station_name:
                station_name = f"Station ({lat}, {lon})"

            writer.writerow([station_name, lat, lon, aqi, timestamp])
            rows_written += 1

    return rows_written


if __name__ == "__main__":
    if WAQI_TOKEN == "PASTE_YOUR_TOKEN_HERE":
        raise SystemExit(
            "You need a WAQI token first. See the setup notes at the top of this file."
        )

    print(f"Looking for stations inside bounds: {BOUNDS} ...")
    stations = fetch_stations(BOUNDS, WAQI_TOKEN)
    print(f"Found {len(stations)} station(s).")

    written = save_to_csv(stations, OUTPUT_FILE)
    print(f"Saved {written} readings to {OUTPUT_FILE}")

    if written == 0:
        print(
            "No readings were saved. Double check BOUNDS actually covers an area "
            "with monitoring stations -- try a wider box."
        )
