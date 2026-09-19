# FIELD VISIT REPORT

## Environmental Field Study: Locality-Level Air Quality & Acoustic Noise Surveillance
* **Project Name**: Pollution-Mapper (Field Surveillance Project)
* **Domain**: Environmental Informatics, Urban Ecology, Field Data Collection
* **Study Region**: Urban Municipal Area & Surrounding Microclimates (Pune Metropolitan Corridor)
* **Survey Period**: September 2026

---

## 1. EXECUTIVE SUMMARY
As part of the academic Field Project curriculum, an on-site environmental survey was conducted across diverse urban land-use categories. The primary objective was to record primary, empirical acoustic noise levels ($L_{\text{Aeq}}$ in decibels) using mobile sound-level instruments, correlate these observations with localized air quality indices (AQI, $PM_{2.5}, PM_{10}$), and interact directly with local stakeholders (pedestrians, shopkeepers, traffic officers, residents) to assess perceived environmental annoyance and health impacts.

The survey revealed a clear co-location of severe acoustic and particulate pollution at arterial traffic junctions and transit terminals ($> 80\text{ dB}$, $\text{AQI} > 115$), contrasting sharply with buffered residential and recreational green zones ($< 52\text{ dB}$, $\text{AQI} < 55$).

---

## 2. SURVEY METHODOLOGY & INSTRUMENT SETUP

### 2.1 Equipment & Protocol
* **Acoustic Sensor**: Calibrated digital decibel meter application (A-weighting frequency filter, slow dynamic response mode).
* **Sampling Protocol**:
  * The observer stood at a standard distance of 1.5 meters from the road curb or pedestrian pathway.
  * The sensor was held at chest height (1.2–1.5 m above ground level), shielded from direct wind currents.
  * Measurements were sampled continuously for 60 seconds per trial, recording the Equivalent Continuous Sound Level ($L_{\text{Aeq}}$) and peak instantaneous decibels ($L_{\text{max}}$).
* **Atmospheric Data Collection**:
  * Geo-referenced coordinates $(lat, lon)$ were extracted via Google Maps at each exact field point.
  * Real-time atmospheric metrics (AQI, $PM_{2.5}, PM_{10}$) were synchronized via the Pollution-Mapper API pipeline at the time of field sampling.

---

## 3. DETAILED SITE OBSERVATION LOGS

### Site 1: Major Transit Junction (Shivajinagar Bus & Rail Terminal)
* **Land-Use Classification**: Commercial / High-Density Transport Corridor
* **Coordinates**: $18.5314^\circ\text{ N}, 73.8446^\circ\text{ E}$
* **Time of Visit**: Morning Peak (08:45 AM – 09:30 AM)
* **Weather**: Sunny, 27°C, Wind speed ~7 km/h
* **Measured Sound Level**: **82.4 dB** ($L_{\text{max}}: 94.2\text{ dB}$)
* **Co-located Air Quality**: **AQI 92** (Moderate | $PM_{2.5}: 31.8\ \mu\text{g/m}^3$)
* **On-Site Observations**: Continuous deceleration and acceleration of diesel transit buses, high-frequency horn honking, idling two-wheelers, high pedestrian concentration. Exhaust fumes visibly noticeable at signal stop lines.
* **Photographic Record**:
  ```
  [PHOTO 1.1: Multi-lane intersection with state transport buses and idling traffic during morning peak]
  [PHOTO 1.2: Decibel meter application display recording 82.4 dB at the bus terminal exit curb]
  ```

---

### Site 2: High-Street Commercial Market (Laxmi Road / Main Market)
* **Land-Use Classification**: Commercial / Retail Shopping District
* **Coordinates**: $18.5204^\circ\text{ N}, 73.8567^\circ\text{ E}$
* **Time of Visit**: Afternoon / Evening (05:15 PM – 06:00 PM)
* **Weather**: Clear sky, 29°C, Wind speed ~4 km/h
* **Measured Sound Level**: **78.0 dB** ($L_{\text{max}}: 86.5\text{ dB}$)
* **Co-located Air Quality**: **AQI 88** (Moderate | $PM_{2.5}: 29.4\ \mu\text{g/m}^3$)
* **On-Site Observations**: Narrow urban street canyon flanked by 3–4 story commercial buildings. Acoustic reverberation amplified by closely packed structures. Noise sources: market vendors shouting, store music, small two-stroke mopeds, small diesel generator backups.
* **Photographic Record**:
  ```
  [PHOTO 2.1: Narrow commercial market street canyon showing dense pedestrian and two-wheeler movement]
  [PHOTO 2.2: Ambient sound recording near retail storefront during evening shopping rush]
  ```

---

### Site 3: Urban Green Buffer / Recreational Zone (Pashan Nature Sanctuary)
* **Land-Use Classification**: Ecological / Water Body / Nature Reserve
* **Coordinates**: $18.5412^\circ\text{ N}, 73.7925^\circ\text{ E}$
* **Time of Visit**: Morning (06:30 AM – 07:15 AM)
* **Weather**: Mild morning mist, 22°C, Calm wind
* **Measured Sound Level**: **45.2 dB** ($L_{\text{max}}: 54.0\text{ dB}$)
* **Co-located Air Quality**: **AQI 48** (Good | $PM_{2.5}: 12.1\ \mu\text{g/m}^3$)
* **On-Site Observations**: Natural tree canopy and lake surface acting as natural sound and particulate sinks. Background sound dominated by bird calls and rustling leaves. Minimal vehicular intrusion restricted to peripheral service roads.
* **Photographic Record**:
  ```
  [PHOTO 3.1: Dense canopy and lake shoreline providing acoustic attenuation at Pashan Nature Trail]
  [PHOTO 3.2: Sound level meter registering quiet background level of 45.2 dB within the park perimeter]
  ```

---

### Site 4: Dense Residential Neighborhood (Katraj Lake Residential Colony)
* **Land-Use Classification**: Residential Suburb
* **Coordinates**: $18.4489^\circ\text{ N}, 73.8587^\circ\text{ E}$
* **Time of Visit**: Evening (07:30 PM – 08:15 PM)
* **Weather**: Pleasant, 25°C, Light breeze
* **Measured Sound Level**: **49.5 dB** ($L_{\text{max}}: 61.2\text{ dB}$)
* **Co-located Air Quality**: **AQI 58** (Moderate | $PM_{2.5}: 16.5\ \mu\text{g/m}^3$)
* **On-Site Observations**: Internal colony street with low vehicle speeds. Occasional delivery motorcycles and localized television/chatter from ground-floor balconies. Compliant with WHO daytime residential guideline (55 dB).
* **Photographic Record**:
  ```
  [PHOTO 4.1: Residential street view with low-density vehicular movement and tree plantings]
  [PHOTO 4.2: Sound meter recording baseline acoustic level of 49.5 dB outside residential apartments]
  ```

---

### Site 5: Industrial & Heavy Transit Node (Hadapsar Gadital Chowk / Bypass)
* **Land-Use Classification**: Heavy Commercial / Industrial Freight Transit
* **Coordinates**: $18.5089^\circ\text{ N}, 73.9259^\circ\text{ E}$
* **Time of Visit**: Evening Peak (06:30 PM – 07:15 PM)
* **Weather**: Dry, 28°C, Wind speed ~6 km/h
* **Measured Sound Level**: **85.1 dB** ($L_{\text{max}}: 98.7\text{ dB}$)
* **Co-located Air Quality**: **AQI 124** (Unhealthy for Sensitive Groups | $PM_{2.5}: 45.2\ \mu\text{g/m}^3$)
* **On-Site Observations**: Heavy multi-axle freight trucks, continuous engine braking, severe congestion, airborne dust from unpaved road shoulders. Strong presence of diesel particulate smell.
* **Photographic Record**:
  ```
  [PHOTO 5.1: Hadapsar bypass junction showing heavy freight transport and dust resuspension]
  [PHOTO 5.2: Maximum decibel peak recording (85.1 dB) during heavy commercial vehicle acceleration]
  ```

---

### Site 6: Industrial Cluster Zone (Bhosari Industrial Corridor)
* **Land-Use Classification**: Manufacturing / Light Fabrication
* **Coordinates**: $18.6274^\circ\text{ N}, 73.8465^\circ\text{ E}$
* **Time of Visit**: Afternoon (02:30 PM – 03:30 PM)
* **Weather**: Warm, 31°C, Wind speed ~8 km/h
* **Measured Sound Level**: **88.0 dB** ($L_{\text{max}}: 99.4\text{ dB}$)
* **Co-located Air Quality**: **AQI 155** (Unhealthy | $PM_{2.5}: 63.5\ \mu\text{g/m}^3$)
* **On-Site Observations**: Metal cutting machinery, overhead loading cranes, forklift movement, sheet metal stamping noise. High ambient dust and particulate concentrations.
* **Photographic Record**:
  ```
  [PHOTO 6.1: Industrial street frontage with active fabrication units and material handling trucks]
  [PHOTO 6.2: Peak sound reading showing 88 dB outside metal processing workshop]
  ```

---

## 4. STAKEHOLDER INTERACTION & QUALITATIVE FINDINGS

During field sampling, structured informal interviews were conducted with 15 individuals across the surveyed zones:

| Stakeholder Category | Primary Location | Key Feedback & Concerns Reported |
| :--- | :--- | :--- |
| **Traffic Police Constables (n=4)** | Transit Junctions (Sites 1 & 5) | Reported chronic headaches, auditory fatigue, and dry cough after 8-hour shifts. Relied on basic cloth masks rather than certified N95 respirators. Unanimously identified unnecessary horn honking as the primary stress factor. |
| **Street Vendors / Shopkeepers (n=6)** | Commercial Market (Site 2) | Exhibited habituation to ambient noise, yet noted severe vocal strain due to constantly shouting over street noise. Expressed concern over particulate soot depositing on open fruit/food displays. |
| **Daily Commuters / Pedestrians (n=3)** | Transit Hubs | Avoid waiting at open-air bus stops due to combined heat, noise, and exhaust fumes. Requested noise barrier screens and air filtration zones. |
| **Local Residents (n=2)** | Residential Zone (Site 4) | High satisfaction with vegetative buffer. Reported sleep disturbance only when heavy trucks violate nighttime entry bans. |

---

## 5. SUMMARY OF FIELD MEASUREMENTS
| Site ID | Locality Description | Category | Sound Level ($L_{\text{Aeq}}$) | Air Quality (AQI) | WHO Noise Limit Delta | EPA Air Status |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **S1** | Shivajinagar Terminal | Transit Hub | **82.4 dB** | 92 | $+27.4\text{ dB}$ (Exceeded) | Moderate |
| **S2** | Laxmi Road Market | Commercial | **78.0 dB** | 88 | $+23.0\text{ dB}$ (Exceeded) | Moderate |
| **S3** | Pashan Nature Trail | Ecological | **45.2 dB** | 48 | $-9.8\text{ dB}$ (Compliant) | **Good** |
| **S4** | Katraj Residential | Residential | **49.5 dB** | 58 | $-5.5\text{ dB}$ (Compliant) | Moderate |
| **S5** | Hadapsar Bypass | Freight Transit | **85.1 dB** | 124 | $+30.1\text{ dB}$ (Severe) | **Unhealthy (Sensitive)** |
| **S6** | Bhosari Industrial | Industrial | **88.0 dB** | 155 | $+33.0\text{ dB}$ (Severe) | **Unhealthy** |

---

## 6. KEY EMPIRICAL FINDINGS & FIELD CONCLUSIONS
1. **Strong Dual Co-Occurrence**: Heavy transportation corridors are simultaneous epicenters of extreme acoustic stress ($> 82\text{ dB}$) and particulate degradation ($PM_{2.5} > 40\ \mu\text{g/m}^3$).
2. **Efficacy of Natural Tree Canopies**: The Pashan reserve demonstrated that dense tree buffers can reduce ambient acoustic noise by $30\text{ dB}$ and cut particulate matter concentrations by over $60\%$ compared to nearby arterial roads.
3. **Severe Regulatory Non-Compliance**: 4 out of the 6 surveyed sites exceeded the World Health Organization's recommended daytime outdoor residential limit of $55\text{ dB}$, with commercial and transit corridors exceeding safety baselines by over $25\text{ dB}$.
