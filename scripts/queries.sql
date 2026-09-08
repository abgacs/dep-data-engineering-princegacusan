-- =====================================================================
-- MakatiAir Insight—Analytical Business Queries
-- Target Schema: makati_air_weather_hourly
-- =====================================================================

-- ---------------------------------------------------------------------
-- Question 1: How frequently does Makati experience each air quality health tier, and what is the average PM2.5 level per tier?
-- Categorize AQI values into standard health tiers to evaluate
-- how frequently Makati experiences unhealthy conditions and track average PM2.5.
-- ---------------------------------------------------------------------
SELECT 
    CASE 
        WHEN aqi IS NULL THEN '0. Unknown / Sensor Inactive'
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
GROUP BY aqi_category
ORDER BY aqi_category;


-- ---------------------------------------------------------------------
-- Question 2: How do different weather conditions and relative humidity levels impact PM2.5 concentrations and overall AQI in Makati?
-- Measure how distinct weather conditions (e.g., Rain, Clear, Clouds)
-- and relative humidity levels impact PM2.5 and overall AQI.
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
-- Question 3: Which hours of the day experience the highest average air pollution (PM2.5 and PM10) in Makati?
-- Identify peak pollution exposure hours during the day to support
-- public health advisories and urban traffic planning.
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
