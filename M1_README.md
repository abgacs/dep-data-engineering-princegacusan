## Data Source Notes

### Primary Source
- Name: World Air Quality Index (WAQI) API
- URL: https://aqicn.org/api/
- Format: JSON (REST API)
- Coverage: Provides real-time hourly air quality readings (PM2.5, PM10) for the Makati monitoring station (Station ID: makati)
- Why it fits the problem: This API provides the high-frequency time-series data required to correlate pollution levels with hourly environmental changes in Makati, enabling the calculation of a "Health Impact Score."
- Known limitations: Free tier rate limits (requires efficient polling); occasional downtime or "missing" hours for specific sensors in the network; data is dependent on the local sensor's maintenance status.

### Fallback Source
- Name: OpenWeatherMap API (Current Weather and Forecast)
- URL: https://openweathermap.org/api
- Format: JSON (REST API)
- Coverage: Provides meteorological parameters (temperature, humidity, atmospheric pressure, wind speed/direction) for the geographic coordinates of Makati City (14.5547° N, 121.0244° E).
- Why it could still work: It provides the critical meteorological context (e.g., wind speed and humidity) that influences air quality. Even if air quality sensor data has gaps, weather trends help explain general pollutant dispersion patterns.
- Known limitations: Data is derived from regional weather models and interpolation rather than street-level sensors; free tier has daily request limits; does not contain air quality data, only meteorological context.
