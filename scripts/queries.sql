-- =====================================================================
-- MakatiAir Insight — Analytical Business Queries
-- Schema: makati_air_weather_hourly
-- =====================================================================

-- ---------------------------------------------------------------------
-- Question 1: Air Quality Severity Distribution
-- Business Need: Categorize air quality levels into standard health tiers 
-- to evaluate how often Makati experiences unhealthy conditions and monitor 
-- average PM2.5 levels per tier.
-- ---------------------------------------------------------------------
SELECT 
    CASE 
        WHEN aqi <= 50 THEN '1. Good (0-50)'
        WHEN aqi <= 100 THEN '2. Moderate (51-100)'
        WHEN aqi <= 150 THEN '3. Unhealthy for Sensitive Groups (101-150)'
        WHEN aqi <= 200 THEN '4. Unhealthy (151-200)'
        ELSE '5. Very Unhealthy / Hazardous (201+)'
    END AS aqi_category,
    COUNT(*) AS total_hours,
    ROUND(AVG(pm25), 2) AS avg_pm25_ugm3,
    ROUND(AVG(temperature_celsius), 1) AS avg_temp_celsius
FROM makati_air_weather_hourly
WHERE aqi IS NOT NULL
GROUP BY 1
ORDER BY 1;


-- ---------------------------------------------------------------------
-- Question 2: Environmental Correlation (Weather vs Air Quality)
-- Business Need: Determine how weather conditions (Clear, Rain, Clouds) 
-- and relative humidity levels impact particulate matter (PM2.5) concentrations.
-- ---------------------------------------------------------------------
SELECT 
    weather_condition,
    COUNT(*) AS total_observations,
    ROUND(AVG(humidity_pct), 1) AS avg_humidity_pct,
    ROUND(AVG(aqi), 1) AS avg_aqi,
    ROUND(AVG(pm25), 2) AS avg_pm25_ugm3,
    ROUND(MAX(pm25), 2) AS peak_pm25_ugm3
FROM makati_air_weather_hourly
WHERE weather_condition IS NOT NULL
GROUP BY weather_condition
HAVING COUNT(*) >= 1
ORDER BY avg_pm25_ugm3 DESC;


-- ---------------------------------------------------------------------
-- Question 3: Diurnal Pollution Trends (Hour of Day Analysis)
-- Business Need: Identify peak pollution exposure hours throughout the day 
-- to support public health advisories and urban traffic planning.
-- ---------------------------------------------------------------------
SELECT 
    EXTRACT(HOUR FROM observation_timestamp_utc) AS hour_of_day_utc,
    COUNT(*) AS total_records,
    ROUND(AVG(aqi), 1) AS avg_aqi,
    ROUND(AVG(pm25), 2) AS avg_pm25,
    ROUND(AVG(pm10), 2) AS avg_pm10,
    ROUND(AVG(wind_speed_mps), 2) AS avg_wind_speed_mps
FROM makati_air_weather_hourly
WHERE observation_timestamp_utc IS NOT NULL
GROUP BY hour_of_day_utc
ORDER BY hour_of_day_utc ASC;
