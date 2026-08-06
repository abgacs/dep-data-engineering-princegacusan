# MakatiAir Insight: Urban Air Quality \& Health Correlation Engine

## Problem Statement

I want to answer: "How do traffic density patterns and micro-climate variables (temperature, humidity) correlate with hourly PM2.5 and PM10 fluctuations in Makati City, and how can this data accurately predict health-risk levels for office workers and commuters?"

## Audience

This project is for Makati City Local Government (LGU), urban planners, corporate sustainability officers in the Makati CBD, and Makati-based employees.

## KPI or Key Metric

The main metric I want to track is the Makati Air Quality Index (MAQI). A dynamic score that classifies localized health risk levels based on real-time sensor data integrated with local environmental factors.

## Likely Data Source

I will explore The WAQI (World Air Quality Index) API and the OpenWeatherMap API.
WAQI: https://waqi.info/#/c/4.333/7.871/2.3z
OpenWeatherMap: https://openweathermap.org/weathermap



## Possible Final Dashboard

The dashboard should help the audience quickly see a centralized dashboard that shows Air Quality Heatmaps for Makati, helping users identify the safest times to commute or walk within the city, while flagging High-Pollution windows for the Makati LGU.



## Data Source Notes

### Primary Source

* Name: World Air Quality Index (WAQI) API
* URL: https://aqicn.org/api/
* Format: JSON (REST API)
* Coverage: Provides real-time hourly air quality readings (PM2.5, PM10) for the Makati monitoring station (Station ID: makati)
* Why it fits the problem: This API provides the high-frequency time-series data required to correlate pollution levels with hourly environmental changes in Makati, enabling the calculation of a "Health Impact Score."
* Known limitations: Free tier rate limits (requires efficient polling); occasional downtime or "missing" hours for specific sensors in the network; data is dependent on the local sensor's maintenance status.

### Fallback Source

* Name: OpenWeatherMap API (Current Weather and Forecast)
* URL: https://openweathermap.org/api
* Format: JSON (REST API)
* Coverage: Provides meteorological parameters (temperature, humidity, atmospheric pressure, wind speed/direction) for the geographic coordinates of Makati City (14.5547° N, 121.0244° E).
* Why it could still work: It provides the critical meteorological context (e.g., wind speed and humidity) that influences air quality. Even if air quality sensor data has gaps, weather trends help explain general pollutant dispersion patterns.
* Known limitations: Data is derived from regional weather models and interpolation rather than street-level sensors; free tier has daily request limits; does not contain air quality data, only meteorological context.

### Data Ingestion Strategy

To ensure a continuous, automated flow of data without manual intervention, the ingestion architecture is designed as follows:

*   **Ingestion Architecture:** Scheduled Batch Processing.
*   **Frequency:** Hourly ingestion cadence. Since the WAQI station broadcasts hourly sensor updates and weather attributes shift incrementally, polling both endpoints once every 60 minutes optimizes API limits while keeping the engine current.
*   **Ingestion Mechanism:** A dedicated Python extraction script (`scripts/extract.py`) leverages the standard `requests` library to handle HTTP GET protocols. It securely queries both endpoints using environment variables (`.env`) for authorization tokens.
*   **Storage Target (Raw Layer):** Every successful API hit writes an immutable, timestamped file into the `data/raw/` directory (e.g., `data/raw/waqi_makati_20260718_1800.json`). Retaining the exact unedited structural response guarantees that we can rerun structural data transformations if our processing rules alter down the road.

## Milestone 2 — Data Collection & Ingestion 

### Ingestion Pipeline Overview
* **Ingestion Method:** Path A — API (Hardened with Retries)
* **Script Location:** `scripts/ingest.py`
* **Storage Location:** `data/raw/` (JSON files with immutable UTC timestamps)

### Data Sources & Metadata
1. **WAQI (World Air Quality Index) API**
   * **Source Endpoint:** `https://api.waqi.info/feed/makati/`
   * **Parameters:** `token` (authenticated via `.env`)
   * **Target:** Real-time AQI and individual pollutant readings (PM2.5, PM10, CO, NO2) for Makati.

2. **OpenWeatherMap API**
   * **Source Endpoint:** `https://api.openweathermap.org/data/2.5/weather`
   * **Parameters:** `lat=14.5547`, `lon=121.0244`, `units=metric`, `appid` (authenticated via `.env`)
   * **Target:** Meteorological contextual variables (Temperature, Humidity, Wind Speed, Pressure).

### Fault Tolerance & Security
* **Retry Strategy:** Built using `urllib3.util.Retry` attached to HTTP sessions (3 retries with exponential backoff on HTTP status codes 429, 500, 502, 503, 504).
* **Credential Protection:** API keys stored exclusively in local `.env` (ignored by `.gitignore`). Exception output automatically replaces sensitive API key strings with `********` to prevent console or log leaks.
* **Reproducibility:** Every saved raw JSON file is wrapped with an `_ingestion_metadata` header recording the source URL, fetch timestamp (UTC), and ingestion path method.

## 📖 Data Dictionary
For full details on field definitions, units, nested schema structures, and data types for all raw JSON extractions, refer to the dedicated documentation:
👉 [**Data Dictionary (`data/data_dictionary.md`)**](data/data_dictionary.md)

---

## 🚀 How to Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

2. **Set API keys in a '.env' file at the repo root:**
   ```Code snippet
   WAQI_API_KEY=your_waqi_key_here
   OPENWEATHER_API_KEY=your_openweather_key_here
   
3. **Run the ingestion script:**
   ```bash
   python scripts/ingest.py

This pulls raw air quality and weather measurements for Makati City and saves the untouched JSON responses wrapped in an '_ingestion_metadata' envelope to 'data/raw/'.
