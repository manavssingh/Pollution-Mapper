# Air & Noise Pollution Mapping Dashboard

A locality-level air and noise pollution map + dashboard, built with Python
and Streamlit, deployable for free with no server management.

## The approach (and why)

The brief asks you to *collect* locality-level observations, not just
display someone else's dataset. There's no good free public API for
real-time noise data, so this project uses two different, complementary
data collection strategies -- which is a good story for your report/viva:

- **Air quality** -> pulled from the free WAQI (World Air Quality Index)
  API, which aggregates 11,000+ real monitoring stations worldwide.
- **Noise** -> genuinely collected by you, using a free decibel-meter app
  on your phone, at several localities of your choice. This is your own
  primary data collection.

Both get plotted on one interactive map and dashboard.

## Project structure

```
pollution-mapper/
├── app.py                      # the Streamlit dashboard (run this)
├── fetch_air_quality.py        # pulls real air quality data
├── requirements.txt
├── data/
│   ├── air_quality.csv         # created when you run fetch_air_quality.py
│   └── noise_readings.csv      # you fill this in by hand (template included)
└── .github/workflows/fetch_data.yml   # optional: automate daily fetching
```

## 1. Set up locally

1. Install Python 3.10+ if you don't have it, then in the project folder:
   ```
   pip install -r requirements.txt
   ```
2. Get a free WAQI token (just needs an email): https://aqicn.org/data-platform/token/
3. Open `fetch_air_quality.py` and:
   - Paste your token where it says `PASTE_YOUR_TOKEN_HERE`
   - Change `BOUNDS` to a box around your own city (instructions are in the
     file's comments -- use Google Maps to find the corner coordinates)
4. Run it:
   ```
   python fetch_air_quality.py
   ```
   This creates `data/air_quality.csv` with real readings from every
   station in your area.

## 2. Collect noise readings (your own data)

1. Install a free decibel meter app: "Sound Meter" or "Decibel X" (Android/iPhone).
2. Visit 6-10 localities that make a good comparison -- e.g. a main road,
   a market, a residential street, a park, near a school, at different
   times of day.
3. At each spot, stand still for ~30-60 seconds and note the average
   reading.
4. Open `data/noise_readings.csv` and replace the two EXAMPLE rows with
   your real readings. Get lat/lon for each spot by long-pressing the
   location in Google Maps.

## 3. Run the dashboard locally

```
streamlit run app.py
```

It opens in your browser at `localhost:8501`. You should see the map and
charts populate from your two CSV files.

## 4. Put the code on GitHub

If you've never used git, the easiest way:
1. Create a free account at github.com, click **New repository**.
2. On the empty repo page, click **uploading an existing file** and drag
   in every file/folder from `pollution-mapper/`.
3. Commit.

(If you do know git: `git init`, `git add .`, `git commit -m "initial"`,
then create the repo on GitHub and follow its `git remote add origin ...`
/ `git push` instructions.)

## 5. Deploy for free (Streamlit Community Cloud)

1. Go to https://streamlit.io/cloud and sign in with your GitHub account.
2. Click **New app**, pick your repo, branch `main`, and file `app.py`.
3. Click **Deploy**. It builds for a minute or two and gives you a public
   URL you can put in your report and share with your evaluators.

Important: the deployed app only *reads* the CSV files already committed
to your repo -- it never needs your WAQI token, so there's nothing extra
to configure on Streamlit Cloud. Whenever you push new commits (e.g. an
updated `air_quality.csv`), the live app updates automatically within a
minute or two.

## 6. (Optional, but impressive) Automate daily data collection

`.github/workflows/fetch_data.yml` runs `fetch_air_quality.py`
automatically every day and commits the new readings, so your trend chart
fills in on its own without you re-running anything.

To turn it on:
1. In your GitHub repo, go to **Settings -> Secrets and variables ->
   Actions -> New repository secret**.
2. Name it `WAQI_TOKEN`, paste your token as the value.
3. That's it -- check the **Actions** tab tomorrow to see it run (or
   trigger it manually with the "Run workflow" button).

## Ideas to make it stronger (if you have time)

- Add a "submit a noise reading" form inside `app.py` using
  `st.form` -- lets classmates/friends contribute readings too.
- Add a scatter plot of noise vs. AQI to see if noisy localities also
  tend to be more polluted (a real, original insight for your report).
- Show PM2.5 specifically (WAQI's `/feed/` endpoint returns pollutant
  breakdowns, not just the composite AQI).
- Compare weekday vs weekend, or morning vs evening.

## Troubleshooting

- **"No module named streamlit"** -> re-run `pip install -r requirements.txt`.
- **fetch script says 0 stations found** -> your `BOUNDS` box is probably
  too small or in the wrong place; double-check the coordinates.
- **Map is blank on Streamlit Cloud** -> make sure `data/air_quality.csv`
  and `data/noise_readings.csv` were actually committed to GitHub (check
  the repo in your browser).

## Data source

Air quality data: [World Air Quality Index project](https://waqi.info)
(aggregated from government and research monitoring stations globally).
