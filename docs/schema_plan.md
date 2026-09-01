# Processed Schema Plan — MakatiAir Insight

This document defines the storage architecture, table design, grain, primary key strategy, and target schema for the processed layer stored in `data/processed/`.

---

## 1. Storage Architecture

| Layer | Path | Format | Description |
| :--- | :--- | :--- | :--- |
| **Raw** | `data/raw/` | JSON | Raw API responses from WAQI and OpenWeatherMap wrapped in metadata envelopes. |
| **Processed** | `data/processed/` | CSV / Parquet | Cleaned, flattened, and merged tabular dataset optimized for SQL and analytical querying. |

---

## 2. Table Design & Grain

* **Processed Table / File Name:** `makati_air_weather_hourly.csv`
* **Grain:** **One row = One hourly environmental observation snapshot for Makati City.**
* **Primary Key (`observation_id`):** Deterministic string formed by combining station name and observation timestamp:  
  `makati_<observation_timestamp_utc>` (e.g., `makati_2026-09-01T23:00:00Z`).

---

## 3. Schema Definition & Target Columns

| Column Name | Data Type | Nullable | Description / Transformation |
| :--- | :--- | :--- | :--- |
| `observation_id` | String | **No** | **Primary Key.** Unique identifier for each hourly snapshot. |
| `location_name` | String | **No** | City / location monitored (`Makati`). |
| `latitude` | Float | No | Station latitude coordinate (`14.5547`). |
| `longitude` | Float | No | Station longitude coordinate (`121.0244`). |
| `observation_timestamp_utc` | Timestamp (ISO 8601) | **No** | UTC timestamp of observation snapshot. |
| `aqi` | Integer | Yes | Overall Air Quality Index score (0–500+). |
| `pm25` | Float | Yes | Fine Particulate Matter ($PM_{2.5}$) in $\mu g/m^3$. |
| `pm10` | Float | Yes | Respirable Particulate Matter ($PM_{10}$) in $\mu g/m^3$. |
| `no2` | Float | Yes | Nitrogen Dioxide concentration in ppb. |
| `co` | Float | Yes | Carbon Monoxide concentration in ppm. |
| `temperature_celsius` | Float | Yes | Ambient temperature converted to Celsius. |
| `feels_like_celsius` | Float | Yes | Perceived temperature in Celsius. |
| `humidity_pct` | Float | Yes | Relative humidity percentage (0–100%). |
| `pressure_hpa` | Float | Yes | Atmospheric pressure at sea level in hPa. |
| `weather_condition` | String | Yes | Main weather category (e.g., Clear, Rain, Clouds). |
| `wind_speed_mps` | Float | Yes | Wind speed in meters per second. |
| `ingested_at_utc` | Timestamp (ISO 8601) | **No** | Pipeline ingestion run timestamp. |

---

## 4. Relationship & Merging Logic

The raw payloads from **WAQI** and **OpenWeatherMap** are ingested independently. During transformation:
1. Timestamps are rounded to the nearest UTC hour.
2. The records are joined on `observation_timestamp_utc` to form a single, unified analytical record per hour.
