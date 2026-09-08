import os
import sqlite3
import pandas as pd

PROCESSED_DATA_PATH = os.path.join("data", "processed", "makati_air_weather_hourly.csv")
SQL_SCRIPT_PATH = os.path.join("scripts", "queries.sql")

def run_sql_queries():
    # 1. Check if processed data exists
    if not os.path.exists(PROCESSED_DATA_PATH):
        print(f"❌ Error: Processed data file not found at {PROCESSED_DATA_PATH}")
        print("💡 Ensure you run your Week 9/10 transformation script first to generate the processed CSV.")
        return

    # 2. Check if SQL query script exists
    if not os.path.exists(SQL_SCRIPT_PATH):
        print(f"❌ Error: SQL query file not found at {SQL_SCRIPT_PATH}")
        return

    print("📊 Loading processed dataset into in-memory SQL database...")
    df = pd.read_csv(PROCESSED_DATA_PATH)

    # 3. Connect to in-memory SQLite database
    conn = sqlite3.connect(":memory:")

    # Custom SQLite helper function for EXTRACT(HOUR FROM ...) compatibility
    conn.create_function("EXTRACT_HOUR", 1, lambda ts: int(pd.to_datetime(ts).hour) if pd.notnull(ts) else None)

    # Load DataFrame into table
    df.to_sql("makati_air_weather_hourly", conn, if_exists="replace", index=False)

    # 4. Read SQL file
    with open(SQL_SCRIPT_PATH, "r", encoding="utf-8") as f:
        sql_raw = f.read()

    # Replace EXTRACT syntax for SQLite compatibility
    sql_adapted = sql_raw.replace("EXTRACT(HOUR FROM observation_timestamp_utc)", "EXTRACT_HOUR(observation_timestamp_utc)")
    
    # Split queries by semicolon
    queries = [q.strip() for q in sql_adapted.split(";") if q.strip()]

    print(f"🚀 Found {len(queries)} SQL queries in {SQL_SCRIPT_PATH}.\n")

    # 5. Execute each query
    for idx, query in enumerate(queries, 1):
        print("=" * 65)
        print(f"  EXECUTING QUESTION {idx}")
        print("=" * 65)
        try:
            result_df = pd.read_sql_query(query, conn)
            if result_df.empty:
                print("⚠️ Query executed successfully but returned 0 rows.")
            else:
                print(result_df.to_string(index=False))
            print("\n")
        except Exception as e:
            print(f"❌ Error executing query {idx}: {e}\n")

    conn.close()

if __name__ == "__main__":
    run_sql_queries()
