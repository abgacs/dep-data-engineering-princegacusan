# Data Dictionary — MakatiAir Insight Dataset

This document details the schema, fields, data types, and descriptions for raw JSON extractions stored in `data/raw/` and downstream processed datasets.

---

## 1. Raw Ingestion Metadata (`_ingestion_metadata`)

Every raw JSON extract produced by `scripts/ingest.py` is wrapped in a standard metadata envelope.

| Field Name | Data Type | Example Value | Description |
| :--- | :--- | :--- | :--- |
| `_ingestion_metadata.source_name` | String | `"WAQI"` or `"OpenWeatherMap"` | The identifier of the external API source. |
| `_ingestion_metadata.source_url` | String | `"https://api.waqi.info/feed/..."` | The exact API endpoint requested (with credentials masked). |
| `_ingestion_metadata.fetched_at_utc` | String (ISO 8601) | `"2026-08-07T01:00:00Z"` | UTC timestamp recording when the API request was completed. |
| `_ingestion_metadata.ingestion_path` | String | `"Path A — API Hardened with Retries"` | Pipeline ingestion strategy indicator. |

---

## 2. WAQI Air Quality Schema (`waqi_makati_*.json`)

Raw payload structure returned from the World Air Quality Index API for the Makati monitoring station.

| Field Name | Data Type | Unit / Range | Description |
| :--- | :--- | :--- | :--- |
| `status` | String | `"ok"` / `"error"` | Status of the API response payload. |
| `data.aqi` | Integer | 0 – 500+ | Overall Air Quality Index score. |
| `data.idx` | Integer | Unique ID | Station identifier in the WAQI network. |
| `data.city.name` | String | Text | Name of the monitoring station location. |
| `data.city.geo` | Array [Float] | `[Lat, Lon]` | Geographic coordinates of the monitoring station. |
| `data.iaqi.pm25.v` | Float | $\mu g/m^3$ | Fine Particulate Matter ($PM_{2.5}$) value. |
| `data.iaqi.pm10.v` | Float | $\mu g/m^3$ | Respirable Particulate Matter ($PM_{10}$) value. |
| `data.iaqi.no2.v` | Float | ppb | Nitrogen Dioxide concentration value. |
| `data.iaqi.co.v` | Float | ppm | Carbon Monoxide concentration value. |
| `data.time.iso` | String (ISO 8601) | Timestamp | Local measurement timestamp reported by the station. |

---

## 3. OpenWeatherMap Weather Schema (`openweather_makati_*.json`)

Raw payload structure returned from OpenWeatherMap Current Weather API for Makati (`14.5547, 121.0244`).

| Field Name | Data Type | Unit | Description |
| :--- | :--- | :--- | :--- |
| `coord.lat` / `coord.lon` | Float | Degrees | Latitude and Longitude of the query location. |
| `weather[0].main` | String | Text | Group of weather parameters (e.g., Rain, Clouds, Clear). |
| `weather[0].description` | String | Text | Weather condition description within the group. |
| `main.temp` | Float | Kelvin / Celsius | Ambient atmospheric temperature. |
| `main.feels_like` | Float | Kelvin / Celsius | Human perception of temperature based on humidity/wind. |
| `main.pressure` | Float | hPa | Atmospheric pressure at sea level. |
| `main.humidity` | Float | % | Relative humidity percentage. |
| `wind.speed` | Float | m/s | Wind speed. |
| `wind.deg` | Integer | Degrees | Wind direction in degrees (meteorological). |
| `dt` | Integer (Unix) | Seconds | Time of data calculation (UTC Unix epoch). |
