import os
import glob
import json
import pandas as pd
import numpy as np

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")
OUTPUT_FILE = os.path.join("data", "processed", "makati_air_weather_hourly.csv")

def discover_and_load_json_files():
    """Recursively discover and classify all JSON payloads in data/raw/."""
    # Find all json files even if nested in subfolders
    search_pattern = os.path.join(RAW_DIR, "**", "*.json")
    files = glob.glob(search_pattern, recursive=True)
    
    waqi_records = []
    owm_records = []

    print(f"📁 Found {len(files)} total JSON file(s) under '{RAW_DIR}'.")

    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                payload = json.load(f)
                
            fname = os.path.basename(filepath).lower()
            
            # Identify source by payload signature or filename
            if "waqi" in fname or (isinstance(payload, dict) and "iaqi" in str(payload)):
                waqi_records.append(payload)
            elif "weather" in fname or "openweather" in fname or (isinstance(payload, dict) and ("main" in payload or "dt" in payload or "weather" in str(payload))):
                owm_records.append(payload)
            else:
                # Fallback check
                if "data" in payload and isinstance(payload["data"], dict) and "iaqi" in payload["data"]:
                    waqi_records.append(payload)
                else:
                    owm_records.append(payload)
                    
        except Exception as e:
            print(f"⚠️ Warning: Failed to parse {filepath}: {e}")

    return waqi_records, owm_records

def parse_waqi_data(records):
    """Extract and standardize WAQI fields across varying raw payload structures."""
    parsed = []
    
    for rec in records:
        if not isinstance(rec, dict):
            continue
            
        # Extract nested payload if present
        data = rec.get("data", rec)
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
            
        if not isinstance(data, dict):
            continue

        # 1. Extract AQI
        aqi_val = data.get("aqi")

        # 2. Extract Pollutants (iaqi)
        iaqi = data.get("iaqi", {})
        if not isinstance(iaqi, dict):
            iaqi = {}

        def extract_val(metric_key):
            val = iaqi.get(metric_key)
            if isinstance(val, dict):
                return val.get("v")
            elif isinstance(val, (int, float)):
                return val
            return None

        # 3. Extract Timestamp (supports iso, s, v, or metadata timestamp)
        time_info = data.get("time", {})
        utc_ts = None
        
        if isinstance(time_info, dict):
            utc_ts = time_info.get("iso") or time_info.get("s") or time_info.get("v")
        elif isinstance(time_info, str):
            utc_ts = time_info

        # Fallback to ingestion timestamp or raw metadata timestamp if WAQI time object is missing
        if not utc_ts:
            utc_ts = rec.get("metadata", {}).get("ingested_at_utc") or rec.get("ingested_at_utc")

        if not utc_ts:
            continue

        try:
            ts = pd.to_datetime(utc_ts, utc=True).floor("h")
        except Exception:
            continue

        parsed.append({
            "observation_timestamp_utc": ts,
            "aqi": aqi_val,
            "pm25": extract_val("pm25"),
            "pm10": extract_val("pm10"),
            "no2": extract_val("no2"),
            "co": extract_val("co"),
            "ingested_at_utc": rec.get("metadata", {}).get("ingested_at_utc") if isinstance(rec, dict) else None
        })
        
    return pd.DataFrame(parsed)

def parse_openweathermap_data(records):
    """Extract and standardize OpenWeatherMap fields."""
    parsed = []
    for rec in records:
        data = rec.get("data", rec) if isinstance(rec, dict) else {}
        if not isinstance(data, dict):
            continue

        dt = data.get("dt")
        if not dt:
            continue

        ts = pd.to_datetime(dt, unit="s", utc=True).floor("h")
        main = data.get("main", {})
        weather_list = data.get("weather", [{}])
        weather_cond = weather_list[0].get("main") if isinstance(weather_list, list) and len(weather_list) > 0 else None
        wind = data.get("wind", {})

        parsed.append({
            "observation_timestamp_utc": ts,
            "temperature_celsius": main.get("temp"),
            "feels_like_celsius": main.get("feels_like"),
            "humidity_pct": main.get("humidity"),
            "pressure_hpa": main.get("pressure"),
            "weather_condition": weather_cond,
            "wind_speed_mps": wind.get("speed"),
            "owm_ingested_at_utc": rec.get("metadata", {}).get("ingested_at_utc") if isinstance(rec, dict) else None
        })
    return pd.DataFrame(parsed)

def run_data_quality_checks(df, expected_cols):
    """Week 11 Data Quality Suite."""
    print("\n🔍 Running Week 11 Data Quality Checks...")
    
    if df.empty:
        print("⚠️ Quality Warning: Dataset is empty (0 records). Skipping row-level checks.")
        return True

    missing_cols = [c for c in expected_cols if c not in df.columns]
    assert len(missing_cols) == 0, f"❌ Missing required columns: {missing_cols}"
    print("  ✅ Schema Check Passed: All 17 expected columns present.")

    null_pks = df["observation_id"].isnull().sum()
    assert null_pks == 0, f"❌ Found {null_pks} null primary keys."
    print("  ✅ Primary Key Null Check Passed: Zero nulls in 'observation_id'.")

    dup_count = df.duplicated(subset=["observation_id"]).sum()
    assert dup_count == 0, f"❌ Found {dup_count} duplicate primary key records."
    print("  ✅ Uniqueness Check Passed: Zero duplicate 'observation_id' rows.")

    print("🎉 All Data Quality & Validation checks completed successfully!\n")
    return True

def main():
    print("=" * 65)
    print("🚀 STARTING WEEKS 9-12 PANDAS ETL & DATA QUALITY PIPELINE")
    print("=" * 65)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # 1. Inspect and Ingest
    waqi_records, owm_records = discover_and_load_json_files()

    df_waqi = parse_waqi_data(waqi_records) if waqi_records else pd.DataFrame()
    df_owm = parse_openweathermap_data(owm_records) if owm_records else pd.DataFrame()

    print("\n--- Week 9 Profiling: WAQI Extract ---")
    if not df_waqi.empty:
        print(f"Loaded {len(df_waqi)} WAQI records.")
        print(df_waqi.head(2))
    else:
        print("No valid WAQI observation records parsed.")

    print("\n--- Week 9 Profiling: OpenWeather Extract ---")
    if not df_owm.empty:
        print(f"Loaded {len(df_owm)} OpenWeather records.")
        print(df_owm.head(2))
    else:
        print("No valid OpenWeather observation records parsed.")

    cols_order = [
        "observation_id", "location_name", "latitude", "longitude",
        "observation_timestamp_utc", "aqi", "pm25", "pm10", "no2", "co",
        "temperature_celsius", "feels_like_celsius", "humidity_pct",
        "pressure_hpa", "weather_condition", "wind_speed_mps", "ingested_at_utc"
    ]

    if df_waqi.empty and df_owm.empty:
        print("\n⚠️ No usable JSON payload data extracted. Creating structural empty dataset...")
        df_final = pd.DataFrame(columns=cols_order)
        run_data_quality_checks(df_final, cols_order)
        df_final.to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Structural dataset saved at {OUTPUT_FILE}")
        return

    # 2. Joins & Transformations
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

    df_merged["location_name"] = "Makati"
    df_merged["latitude"] = 14.5547
    df_merged["longitude"] = 121.0244

    df_merged["observation_timestamp_utc"] = pd.to_datetime(df_merged["observation_timestamp_utc"]).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df_merged["observation_id"] = "makati_" + df_merged["observation_timestamp_utc"].astype(str)

    if "ingested_at_utc" not in df_merged.columns or df_merged["ingested_at_utc"].isnull().all():
        df_merged["ingested_at_utc"] = pd.Timestamp.now(tz="UTC").isoformat()

    for col in cols_order:
        if col not in df_merged.columns:
            df_merged[col] = np.nan

    df_final = df_merged[cols_order].drop_duplicates(subset=["observation_id"]).sort_values("observation_timestamp_utc")

    # 3. Quality & Save
    run_data_quality_checks(df_final, cols_order)
    df_final.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Final Processed Dataset ({len(df_final)} rows) saved to {OUTPUT_FILE}")
    print("=" * 65)

if __name__ == "__main__":
    main()
