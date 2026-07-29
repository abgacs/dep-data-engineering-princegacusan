import json
import os
import sys
from datetime import datetime
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up raw data directory
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# API Configurations
WAQI_API_KEY = os.getenv("WAQI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Makati City Coordinates & Station ID
MAKATI_LAT = 14.5547
MAKATI_LON = 121.0244
WAQI_STATION = "makati"


def fetch_waqi_data() -> dict:
    """Fetches real-time air quality data for Makati from the WAQI API."""
    if not WAQI_API_KEY:
        print("[ERROR] Missing WAQI_API_KEY in environment variables.")
        return {}

    url = f"https://api.waqi.info/feed/{WAQI_STATION}/"
    params = {"token": WAQI_API_KEY}
    headers = {"Accept": "application/json"}

    print(f"[INFO] Querying WAQI API for station: '{WAQI_STATION}'...")
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        payload = response.json()

        # Check API-level status flag
        if payload.get("status") != "ok":
            print(f"[WARNING] WAQI API returned status error: {payload.get('data')}")
            return {}

        return payload

    except requests.exceptions.Timeout:
        print("[ERROR] WAQI API request timed out after 30 seconds.")
    except requests.exceptions.HTTPError as err:
        print(f"[ERROR] WAQI HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"[ERROR] WAQI connection failed: {err}")

    return {}


def fetch_openweather_data() -> dict:
    """Fetches current weather parameters for Makati from OpenWeatherMap API."""
    if not OPENWEATHER_API_KEY:
        print("[ERROR] Missing OPENWEATHER_API_KEY in environment variables.")
        return {}

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": MAKATI_LAT,
        "lon": MAKATI_LON,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",  # Use Celsius for temperature
    }
    headers = {"Accept": "application/json"}

    print(f"[INFO] Querying OpenWeatherMap API for Makati ({MAKATI_LAT}, {MAKATI_LON})...")
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        print("[ERROR] OpenWeatherMap API request timed out after 30 seconds.")
    except requests.exceptions.HTTPError as err:
        print(f"[ERROR] OpenWeatherMap HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"[ERROR] OpenWeatherMap connection failed: {err}")

    return {}


def save_raw_payload(payload: dict, source_name: str) -> None:
    """Saves raw JSON response with an immutable timestamp filename into /data/raw/."""
    if not payload:
        print(f"[SKIP] No payload returned for {source_name}. Skipping save.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = RAW_DIR / f"{source_name}_makati_{timestamp}.json"

    # Save formatted, indented raw JSON to retain exact unedited structure
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Saved raw extract to: {output_file}")


def main():
    print("--- Starting MakatiAir Data Ingestion ---")

    # 1. Fetch & Save WAQI Air Quality Payload
    waqi_payload = fetch_waqi_data()
    save_raw_payload(waqi_payload, "waqi")

    # 2. Fetch & Save OpenWeatherMap Meteorological Payload
    weather_payload = fetch_openweather_data()
    save_raw_payload(weather_payload, "openweather")

    print("--- Ingestion Complete ---")


if __name__ == "__main__":
    main()
