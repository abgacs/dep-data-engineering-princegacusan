import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
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


def get_retry_session(retries: int = 3, backoff_factor: float = 1.0) -> requests.Session:
    """Creates a requests Session with automatic retries and exponential backoff."""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_waqi_data(session: requests.Session) -> tuple[dict, str]:
    """Fetches real-time air quality data for Makati from the WAQI API."""
    if not WAQI_API_KEY:
        print("[ERROR] Missing WAQI_API_KEY in environment variables.")
        return {}, ""

    url = f"https://api.waqi.info/feed/{WAQI_STATION}/"
    params = {"token": WAQI_API_KEY}
    headers = {"Accept": "application/json"}

    print(f"[INFO] Querying WAQI API for station: '{WAQI_STATION}'...")
    try:
        response = session.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        payload = response.json()

        if payload.get("status") != "ok":
            print(f"[WARNING] WAQI API returned status error: {payload.get('data')}")
            return {}, url

        return payload, url

    except requests.exceptions.Timeout:
        print("[ERROR] WAQI API request timed out after 30 seconds.")
    except requests.exceptions.HTTPError as err:
        safe_err = str(err).replace(WAQI_API_KEY, "********")
        print(f"[ERROR] WAQI HTTP error occurred: {safe_err}")
    except requests.exceptions.RequestException as err:
        safe_err = str(err).replace(WAQI_API_KEY, "********")
        print(f"[ERROR] WAQI connection failed: {safe_err}")

    return {}, url


def fetch_openweather_data(session: requests.Session) -> tuple[dict, str]:
    """Fetches current weather parameters for Makati from OpenWeatherMap API."""
    if not OPENWEATHER_API_KEY:
        print("[ERROR] Missing OPENWEATHER_API_KEY in environment variables.")
        return {}, ""

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": MAKATI_LAT,
        "lon": MAKATI_LON,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }
    headers = {"Accept": "application/json"}

    print(f"[INFO] Querying OpenWeatherMap API for Makati ({MAKATI_LAT}, {MAKATI_LON})...")
    try:
        response = session.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json(), url

    except requests.exceptions.Timeout:
        print("[ERROR] OpenWeatherMap API request timed out after 30 seconds.")
    except requests.exceptions.HTTPError as err:
        safe_err = str(err).replace(OPENWEATHER_API_KEY, "********")
        print(f"[ERROR] OpenWeatherMap HTTP error occurred: {safe_err}")
    except requests.exceptions.RequestException as err:
        safe_err = str(err).replace(OPENWEATHER_API_KEY, "********")
        print(f"[ERROR] OpenWeatherMap connection failed: {safe_err}")

    return {}, url


def save_raw_payload(payload: dict, source_name: str, source_url: str) -> None:
    """Saves raw JSON response with metadata header and immutable timestamp into /data/raw/."""
    if not payload:
        print(f"[SKIP] No payload returned for {source_name}. Skipping save.")
        return

    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.strftime("%Y%m%d_%H%M%S")
    
    # Wrap payload with reproducibility metadata
    envelope = {
        "_ingestion_metadata": {
            "source_name": source_name,
            "source_url": source_url,
            "fetched_at_utc": now_utc.isoformat(),
            "ingestion_path": "Path A — API (Hardened with Retries)",
        },
        "raw_response": payload,
    }

    output_file = RAW_DIR / f"{source_name}_makati_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(envelope, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Saved raw extract to: {output_file}")


def main():
    print("--- Starting MakatiAir Data Ingestion (Hardened Pipeline) ---")
    session = get_retry_session(retries=3, backoff_factor=1.0)

    # 1. Fetch & Save WAQI Air Quality Payload
    waqi_payload, waqi_url = fetch_waqi_data(session)
    save_raw_payload(waqi_payload, "waqi", waqi_url)

    # 2. Fetch & Save OpenWeatherMap Meteorological Payload
    weather_payload, owm_url = fetch_openweather_data(session)
    save_raw_payload(weather_payload, "openweather", owm_url)

    print("--- Ingestion Complete ---")


if __name__ == "__main__":
    main()