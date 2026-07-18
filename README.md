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

