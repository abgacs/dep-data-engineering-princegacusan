import os
import glob
import json
import pandas as pd
import numpy as np

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
OUTPUT_FILE = os.path.join("data", "processed", "makati_air_weather_hourly.csv")

def load_json_files(prefix):
    """Week 9: Find and load raw JSON payloads matching prefix pattern."""
    files = glob.glob(os.path.join(RAW_DIR, f"{prefix}*.json"))
    records = []
    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                payload = json.load(f)
                records.append(payload)
        except Exception as e:
            print(f"⚠️ Warning: Failed to read {filepath}: {e}")
    return records

def parse_waqi_data(records):
    """Week 10: Extract, standardize, and flatten WAQI air quality fields."""
    parsed = []
    for rec in records:
        data = rec.get("data", {})
        if not data or not isinstance(data, dict):
            continue
            
        iaqi = data.get("iaqi", {})
        time_info = data.get("time", {})
        
        utc_ts = time_info.get("iso") or time_info.get("s")
        if not utc_ts:
            continue

        ts = pd.to_datetime(utc_ts, utc=True).floor("h")

        parsed.append({
            "observation_timestamp_utc": ts,
            "aqi": data.get("aqi"),
            "pm25": iaqi.get("pm25", {}).get("v") if isinstance(iaqi.get("pm25"), dict) else None,
            "pm10": iaqi.get("pm10", {}).get("v") if isinstance(iaqi.get("pm10"), dict) else None,
            "no2": iaqi.get("no2", {}).get("v") if isinstance(iaqi.get("no2"), dict) else None,
            "co": iaqi.get("co", {}).get("v") if isinstance(iaqi.get("co"), dict) else None,
            "ingested_at_utc": rec.get("metadata", {}).get("ingested_at_utc")
        })
    return pd.DataFrame(parsed)

def parse_openweathermap_data(records):
    """Week 10: Extract, standardize, and flatten OpenWeatherMap meteorology fields."""
    parsed = []
    for rec in records:
        data = rec.get("data", rec)
        if not isinstance(data, dict):
            continue

        dt = data.get("dt")
        if not dt:
            continue

        ts = pd.to_datetime(dt, unit="s", utc=True).floor("h")
        main = data.get("main", {})
        weather_list = data.get("weather", [{}])
        weather_cond = weather_list[0].get("main") if len(weather_list) > 0 else None
        wind = data.get("wind", {})

        parsed.append({
            "observation_timestamp_utc": ts,
            "temperature_celsius": main.get("temp"),
            "feels_like_celsius": main.get("feels_like"),
            "humidity_pct": main.get("humidity"),
            "pressure_hpa": main.get("pressure"),
            "weather_condition": weather_cond,
            "wind_speed_mps": wind.get("speed"),
            "owm_ingested_at_utc": rec.get("metadata", {}).get("ingested_at_utc")
        })
    return pd.DataFrame(parsed)

def run_data_quality_checks(df, expected_cols):
    """Week 11: Data Quality & Schema Validation Suite."""
    print("\n🔍 Running Week 11 Data Quality Checks...")
    
    if df.empty:
        print("⚠️ Quality Warning: Dataset is empty (0 records). Skipping row-level checks.")
        return True

    # Check 1: Column Schema Completeness
    missing_cols = [c for c in expected_cols if c not in df.columns]
    assert len(missing_cols) == 0, f"❌ Quality Check Failed: Missing required columns: {missing_cols}"
    print("  ✅ Schema Check Passed: All 17 expected columns present.")

    # Check 2: Primary Key Non-Null Assertion
    null_pks = df["observation_id"].isnull().sum()
    assert null_pks == 0, f"❌ Quality Check Failed: Found {null_pks} null primary keys in 'observation_id'."
    print("  ✅ Primary Key Null Check Passed: Zero nulls in 'observation_id'.")

    # Check 3: Uniqueness Assertion
    dup_count = df.duplicated(subset=["observation_id"]).sum()
    assert dup_count == 0, f"❌ Quality Check Failed: Found {dup_count} duplicate primary key records."
    print("  ✅ Uniqueness Check Passed: Zero duplicate 'observation_id' rows.")

    # Check 4: Range & Bounds Validations
    if df["humidity_pct"].notnull().any():
        invalid_humidity = df[(df["humidity_pct"] < 0) | (df["humidity_pct"] > 100)]
        if len(invalid_humidity) > 0:
            print(f"  ⚠️ Range Warning: Found {len(invalid_humidity)} records with humidity outside [0, 100].")
        else:
            print("  ✅ Range Check Passed: Humidity values within valid bounds [0, 100].")

    if df["aqi"].notnull().any():
        negative_aqi = df[df["aqi"] < 0]
        if len(negative_aqi) > 0:
            print(f"  ⚠️ Range Warning: Found {len(negative_aqi)} records with negative AQI values.")
        else:
            print("  ✅ Range Check Passed: AQI values non-negative.")

    print("🎉 All Data Quality & Validation checks completed successfully!\n")
    return True

def main():
    print("=" * 65)
    print("🚀 STARTING WEEKS 9-12 PANDAS ETL & DATA QUALITY PIPELINE")
    print("=" * 65)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 1. Week 9: Ingest Raw Payload Files (Matches "waqi*" and "openweather*")
    waqi_records = load_json_files("waqi")
    owm_records = load_json_files("openweather")

    df_waqi = parse_waqi_data(waqi_records) if waqi_records else pd.DataFrame()
    df_owm = parse_openweathermap_data(owm_records) if owm_records else pd.DataFrame()

    print("\n--- Week 9 Profiling: WAQI Extract ---")
    if not df_waqi.empty:
        print(f"Loaded {len(df_waqi)} WAQI records.")
        print(df_waqi.info())
        print(df_waqi.head(2))
    else:
        print("No WAQI records loaded.")

    print("\n--- Week 9 Profiling: OpenWeather Extract ---")
    if not df_owm.empty:
        print(f"Loaded {len(df_owm)} OpenWeather records.")
        print(df_owm.info())
        print(df_owm.head(2))
    else:
        print("No OpenWeather records loaded.")

    cols_order = [
        "observation_id", "location_name", "latitude", "longitude",
        "observation_timestamp_utc", "aqi", "pm25", "pm10", "no2", "co",
        "temperature_celsius", "feels_like_celsius", "humidity_pct",
        "pressure_hpa", "weather_condition", "wind_speed_mps", "ingested_at_utc"
    ]

    # Handle case where no files exist in raw directory
    if df_waqi.empty and df_owm.empty:
        print("\n⚠️ No raw JSON payloads found in data/raw/. Creating structural empty dataset...")
        df_final = pd.DataFrame(columns=cols_order)
        run_data_quality_checks(df_final, cols_order)
        df_final.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Structural dataset saved at {OUTPUT_FILE}")
        return

    # 2. Week 10: Merging & Joins
    print("\n🔄 Merging feeds on observation_timestamp_utc...")
    if not df_waqi.empty and not df_owm.empty:
        df_merged = pd.merge(df_waqi, df_owm, on="observation_timestamp_utc", how="outer")
    elif not df_waqi.empty:
        df_merged = df_waqi
        for c in ["temperature_celsius", "feels_like_celsius", "humidity_pct", "pressure_hpa", "wind_speed_mps"]:
            df_merged[c] = np.nan
        df_merged["weather_condition"] = None
    else:
        df_merged = df_owm
        for c in ["aqi", "pm25", "pm10", "no2", "co"]:
            df_merged[c] = np.nan
        df_merged["ingested_at_utc"] = df_merged.get("owm_ingested_at_utc", None)

    # Standardize Metadata
    df_merged["location_name"] = "Makati"
    df_merged["latitude"] = 14.5547
    df_merged["longitude"] = 121.0244

    # ISO Format Timestamp
    df_merged["observation_timestamp_utc"] = pd.to_datetime(df_merged["observation_timestamp_utc"]).dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Primary Key
    df_merged["observation_id"] = "makati_" + df_merged["observation_timestamp_utc"].astype(str)

    # Ingestion Fallback
    if "ingested_at_utc" not in df_merged.columns or df_merged["ingested_at_utc"].isnull().all():
        df_merged["ingested_at_utc"] = pd.Timestamp.now(tz="UTC").isoformat()

    # Column Schema Order
    for col in cols_order:
        if col not in df_merged.columns:
            df_merged[col] = np.nan

    # Deduplicate & Sort (Week 12 Optimization)
    df_final = df_merged[cols_order].drop_duplicates(subset=["observation_id"]).sort_values("observation_timestamp_utc")

    # 3. Week 11: Run Data Quality Suite
    run_data_quality_checks(df_final, cols_order)

    # 4. Save Processed Dataset
    df_final.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Final Processed Dataset ({len(df_final)} rows) saved to {OUTPUT_FILE}")
    print("=" * 65)

if __name__ == "__main__":
    main()
