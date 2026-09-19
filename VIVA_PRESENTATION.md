# VIVA VOCE PRESENTATION SCRIPT & DECK STRUCTURE

## Locality-Level Air and Noise Pollution Mapping Dashboard
* **Document Type**: Oral Examination Deck Outline, Slide Script & Viva Preparation Guide
* **Domain**: Environmental Informatics, Data Science, Geographic Information Systems (GIS)
* **Student Name / Author**: Manav Singh
* **Repository**: [https://github.com/manavssingh/Pollution-Mapper](https://github.com/manavssingh/Pollution-Mapper)

---

## SLIDE-BY-SLIDE PRESENTATION STRUCTURE

### SLIDE 1: TITLE SLIDE
* **Slide Title**: Locality-Level Air and Noise Pollution Mapping and Surveillance Dashboard
* **Subtitle**: An Autonomous, Serverless GIS Platform for Multi-Pollutant Environmental Monitoring
* **Candidate Details**: Name, Roll Number, Department / Faculty Guidance
* **What to Say (Script)**:
  > *"Respected external examiner and faculty members, good morning. Today, I am presenting my field project entitled 'Locality-Level Air and Noise Pollution Mapping and Surveillance Dashboard'. This project bridges the gap between public atmospheric monitoring and local acoustic surveillance through an interactive, serverless web platform."*

---

### SLIDE 2: THE PROBLEM & MOTIVATION
* **Key Bullet Points**:
  * Traditional government monitoring stations are macroscopic ($10+\text{ km}$ apart) and fail to capture street-level exposure.
  * Lack of open public APIs for real-time street-level acoustic noise due to privacy laws and hardware costs.
  * Environmental data platforms isolate air quality from acoustic noise, ignoring their common vehicular traffic origin.
* **Visual**: Side-by-side comparison of a regional CPCB monitoring station vs a congested urban street canyon.
* **What to Say (Script)**:
  > *"In most cities today, environmental data comes from a handful of centralized government monitoring towers. While these give regional averages, they create massive spatial blindspots: exposure in a congested transit corridor is drastically worse than in an adjacent residential park just 500 meters away. Furthermore, there is virtually no public internet API for street noise. Our motivation was to create a unified platform that maps both pollutants at locality-level resolution without requiring expensive hardware servers."*

---

### SLIDE 3: PROJECT OBJECTIVES
* **Key Bullet Points**:
  1. Build an interactive GIS web application to visualize hyper-local air and acoustic indices.
  2. Implement a hybrid primary and secondary data collection model.
  3. Provide on-demand global city search with automatic geocoding.
  4. Build an autonomous, zero-maintenance data pipeline via GitHub Actions.
  5. Conduct statistical correlation analysis between decibel noise levels and AQI.
* **What to Say (Script)**:
  > *"To solve these challenges, we set five clear engineering objectives: First, develop an interactive web dashboard using Streamlit and Plotly. Second, employ a hybrid data methodology combining automated APIs with physical decibel meter field readings. Third, enable on-demand geocoding for any global city. Fourth, automate daily data collection using cloud CI/CD pipelines. And fifth, statistically evaluate whether noisy corridors also suffer from worse air pollution."*

---

### SLIDE 4: THE HYBRID DATA METHODOLOGY (KEY INNOVATION)
* **Key Bullet Points**:
  * **Secondary Data**: Automated ingestion of AQI, $PM_{2.5}$, and $PM_{10}$ from WAQI and Open-Meteo REST APIs.
  * **Primary Field Data**: Empirical decibel ($L_{\text{Aeq}}$) measurements recorded using calibrated mobile sound meters across distinct urban zones.
  * **Modeled Urban Baselines**: Diurnal WHO urban traffic models for global searched cities without field sensors.
  * **Data Integrity**: Transparent tagging of records (*Verified Field Measurement* vs. *Estimated Urban Model*).
* **Visual**: Methodology flowchart illustrating the three data streams.
* **What to Say (Script)**:
  > *"Our primary research innovation lies in our hybrid data methodology. Since free real-time noise APIs do not exist worldwide, we took a pragmatic approach: air quality is pulled automatically from monitoring APIs, while noise data was collected on-site by visiting real localities with sound-level meters. For cities searched globally where field surveys are pending, our system applies a diurnal acoustic model based on WHO traffic patterns, while maintaining transparent labeling."*

---

### SLIDE 5: FIELD VISIT & ON-SITE MEASUREMENTS
* **Key Bullet Points**:
  * 6 Representative Land-Use Zones Surveyed across the Pune Metropolitan Corridor:
    * **Shivajinagar Bus Terminal**: $82.4\text{ dB}$, $\text{AQI } 92$ ($+27.4\text{ dB}$ over WHO limit)
    * **Laxmi Road Market**: $78.0\text{ dB}$, $\text{AQI } 88$ (Commercial street canyon)
    * **Pashan Nature Trail**: $45.2\text{ dB}$, $\text{AQI } 48$ (Ecological green buffer)
    * **Katraj Residential**: $49.5\text{ dB}$, $\text{AQI } 58$ (Compliant residential zone)
    * **Hadapsar Freight Bypass**: $85.1\text{ dB}$, $\text{AQI } 124$ (Heavy commercial transport)
    * **Bhosari Industrial Estate**: $88.0\text{ dB}$, $\text{AQI } 155$ (Severe industrial strain)
* **Visual**: Table of field measurement sites with photos of decibel meter readings.
* **What to Say (Script)**:
  > *"Here are the empirical findings from our field visits. We surveyed six diverse land-use categories: transit hubs, commercial markets, green buffers, residential colonies, freight corridors, and industrial zones. The highest acoustic noise was recorded in industrial and freight hubs reaching up to 88 decibels, which exceeds WHO daytime safety guidelines by over 30 decibels. Conversely, our natural park benchmark showed that dense vegetation buffers reduce acoustic strain to 45 decibels."*

---

### SLIDE 6: STAKEHOLDER FIELD INTERACTIONS
* **Key Bullet Points**:
  * Surveyed 15 on-site stakeholders using a structured 10-question questionnaire.
  * **Traffic Constables**: Chronic auditory fatigue and dry cough; identified horn honking as the primary stressor.
  * **Shopkeepers & Vendors**: Significant vocal strain from shouting over street noise; particulate soot depositing on goods.
  * **Pedestrians**: Unanimously favored physical green buffers and strict anti-honking enforcement.
* **Visual**: Bar graph showing perceived noise sources (Horn Honking 60%, Heavy Engines 25%, Machinery 15%).
* **What to Say (Script)**:
  > *"Beyond quantitative sensor measurements, we conducted on-site qualitative interviews with traffic police, street vendors, and pedestrians. Traffic officers exposed to 8-hour shifts reported chronic headaches and vocal fatigue, identifying unnecessary horn honking as the primary culprit. These interactions confirmed that environmental noise is an acute, daily occupational health hazard."*

---

### SLIDE 7: SYSTEM ARCHITECTURE & GIT-BACKED STORAGE
* **Key Bullet Points**:
  * Zero-cost, serverless cloud architecture.
  * Git-backed data persistence: CSV storage integrated into the code repository.
  * Reactive caching with `@st.cache_data` preventing redundant network queries.
  * Deployed on Streamlit Community Cloud with continuous deployment from GitHub.
* **Visual**: System Architecture Diagram (Client $\rightarrow$ Streamlit Engine $\rightarrow$ APIs $\rightarrow$ Git Database).
* **What to Say (Script)**:
  > *"This slide highlights the technical architecture. We eliminated traditional expensive database servers by engineering a Git-backed data architecture. Streamlit serves as the reactive presentation layer, while data persists directly in Git-versioned CSV files. Whenever new readings are recorded, Streamlit's caching layer is invalidated and the interface hot-reloads seamlessly."*

---

### SLIDE 8: AUTONOMOUS CI/CD PIPELINE (GITHUB ACTIONS)
* **Key Bullet Points**:
  * `.github/workflows/fetch_data.yml` executes on a daily cron timer (`0 6 * * *` UTC).
  * Automated cloud runner boots, runs `fetch_air_quality.py`, and checks for station updates.
  * Uses GitHub Secrets vault (`WAQI_TOKEN`) for zero credential exposure.
  * `stefanzweifel/git-auto-commit-action` auto-commits new readings to the repository.
  * Verified live execution: Run #35406795872 passed with 100% success status (`success`).
* **Visual**: Screenshot of GitHub Actions workflow run with green success checkmark.
* **What to Say (Script)**:
  > *"To ensure the dashboard stays alive without manual intervention, we built an automated CI/CD data pipeline using GitHub Actions. Every day at 6:00 AM UTC, an autonomous cloud runner boots up, securely retrieves our WAQI API token from GitHub Secrets, pulls fresh station data, and commits the updated dataset back to GitHub. The live application automatically reflects this new data without anyone having to open a terminal."*

---

### SLIDE 9: INTERACTIVE GEOGRAPHIC GIS MAPPING
* **Key Bullet Points**:
  * Plotly MapLibre integration over OpenStreetMap vector tiles.
  * Three selectable map layers:
    1. **Combined Layer**: Displays dual-metric popups (AQI + Decibels + Verification Tag).
    2. **Air Quality Layer**: Continuous color-coded particulate scale (0 to 350).
    3. **Noise Level Layer**: Continuous decibel scale (30 to 95 dB).
* **Visual**: Full screenshot of the interactive map displaying colored circular markers with tooltip.
* **What to Say (Script)**:
  > *"This is our live interactive map. Users can toggle between three distinct layers: Air Quality, Noise Levels, or a Combined Multi-Pollutant Layer. Hovering over any marker reveals the exact locality, current AQI, decibel level, and data verification tier, visually represented using a continuous Red-to-Green health spectrum."*

---

### SLIDE 10: DYNAMIC CITY SEARCH & AUTO-FOCUS
* **Key Bullet Points**:
  * Global on-demand geocoding using OpenStreetMap Nominatim.
  * Instant worldwide real-time AQI fetching via Open-Meteo.
  * Automatic companion urban noise baseline calculation.
  * Camera auto-focus: Instantly re-centers and zooms the map to street-level resolution (zoom 13).
  * In-app primary observation form allowing crowd-sourced sound meter data entry.
* **Visual**: Search bar interface showing a searched city (e.g. London / Delhi) with the auto-focused map.
* **What to Say (Script)**:
  > *"The platform is not restricted to our surveyed city. Using our global search engine, anyone can search any city in the world—like Delhi, Mumbai, London, or Tokyo. The platform resolves the coordinates, pulls live atmospheric data, estimates the current urban acoustic baseline, centers the map, and personalizes the top metric cards on the fly."*

---

### SLIDE 11: ENVIRONMENTAL CORRELATION ANALYSIS (AQI VS. NOISE)
* **Key Bullet Points**:
  * Interactive scatter plot plotting Sound Level ($X$-axis, dB) against Air Quality ($Y$-axis, AQI).
  * Real-time computation of the **Pearson Correlation Coefficient ($r$)**.
  * **Empirical Result**: Positive correlation ($r > +0.65$) confirming that vehicular traffic corridors are joint hotspots of acoustic strain and particulate matter.
* **Visual**: Plotly scatter plot showing the upward trend between Decibels and AQI.
* **What to Say (Script)**:
  > *"One of our primary research questions was: Do noisy localities also suffer from worse air pollution? By merging our co-located records, our engine calculates the Pearson correlation coefficient. Across our surveyed transit and commercial nodes, we observed a strong positive correlation ($r > +0.65$). This confirms that vehicular density acts as a unified source for both acoustic and airborne particulate hazards."*

---

### SLIDE 12: KEY LEARNINGS & RECOMMENDATIONS
* **Key Learnings**:
  * Mobile crowd-sourcing offers a viable, low-cost solution for micro-environmental monitoring.
  * Natural vegetation can attenuate urban sound by up to $30\text{ dB}$ and trap airborne particulate matter.
  * CI/CD automation enables continuous academic data collection at zero server cost.
* **Policy Recommendations**:
  1. Mandate physical green vegetative noise barriers along arterial flyovers.
  2. Implement automated acoustic camera fines for illegal pressure-horn usage.
  3. Establish pedestrian-only low-emission zones in heritage market corridors.
* **What to Say (Script)**:
  > *"Our key learnings demonstrate that low-cost mobile sensing paired with cloud automation can democratize environmental surveillance. Based on our findings, we recommend three concrete urban planning interventions: deploying dense vegetative barriers along transit corridors, installing automated acoustic cameras to fine horn abuse, and establishing pedestrian-only retail zones during peak shopping hours."*

---

### SLIDE 13: CONCLUSION & FUTURE SCOPE
* **Conclusion**: Successfully engineered a live, serverless, locality-level multi-pollutant surveillance dashboard.
* **Future Scope**:
  * Deploying low-cost IoT microcontroller nodes (ESP32 + PMS5003 laser sensor + MAX4466 microphone).
  * Developing LSTM recurrent neural networks to predict next-day pollution peaks based on weather forecasts.
  * Creating a Progressive Web App (PWA) with direct Web Audio microphone sampling.
* **What to Say (Script)**:
  > *"In conclusion, Pollution-Mapper demonstrates that modern web frameworks, public APIs, and field crowd-sourcing can bridge the environmental data gap. In future work, we plan to interface low-cost ESP32 IoT hardware sensing nodes and build predictive machine learning models to forecast environmental peaks. Thank you, and I am now open to your questions."*

---

## ANTICIPATED VIVA VOCE QUESTIONS & MODEL ANSWERS

### Q1: Why didn't you use a public API for noise data?
* **Model Answer**:
  > *"Sir/Madam, unlike air quality, there are virtually no open public internet APIs for street-level acoustic noise worldwide. This is due to strict audio privacy regulations—since public microphones can inadvertently record private human conversations—and the high cost of municipal sensor deployment. Therefore, primary field data collection using sound level meters was the most authentic, scientifically sound method."*

### Q2: How accurate are smartphone decibel meters compared to laboratory sound level meters?
* **Model Answer**:
  > *"Smartphone microphones are uncalibrated for laboratory precision, but studies by the National Institute for Occupational Safety and Health (NIOSH) confirm that when configured with standard A-weighting (dBA) and slow response times, mobile decibel apps achieve an accuracy within $\pm 2\text{ dB}$ of Class 2 sound level meters. For urban locality-level screening and relative comparisons, this provides sufficient fidelity."*

### Q3: How does your daily automation work without a backend server?
* **Model Answer**:
  > *"We utilize GitHub Actions as a serverless cron runner. A YAML workflow file scheduled for 06:00 UTC spins up a temporary virtual Ubuntu machine, securely injects our WAQI API token from GitHub Secrets, executes `fetch_air_quality.py`, appends new station readings to our CSV file, and commits the changes back to GitHub. This achieves zero-maintenance, zero-cost data automation."*

### Q4: What is the significance of the Pearson correlation coefficient in your project?
* **Model Answer**:
  > *"The Pearson correlation coefficient ($r$) statistically quantifies the linear relationship between sound pressure level in decibels and the Air Quality Index. In our field study, an $r$-value greater than $+0.65$ proved that arterial traffic corridors generate a joint environmental penalty, validating that traffic reduction measures simultaneously alleviate both acoustic stress and particulate pollution."*
