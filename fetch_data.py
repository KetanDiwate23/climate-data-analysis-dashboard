"""Download REAL climate data from the free Open-Meteo archive API
(no API key needed).

Writes two files:
  dataset.csv     monthly data (240 rows), used by the charts and dashboard
  daily_data.csv  daily data (about 7,300 rows), used for the SQL analysis

Data: Open-Meteo.com (CC BY 4.0), based on ERA5 reanalysis (Copernicus / ECMWF).

Run:  python fetch_data.py
"""
import os
import shutil
import sys

import pandas as pd
import requests

API = "https://archive-api.open-meteo.com/v1/archive"
START, END = "2020-01-01", "2024-12-31"

# One representative city per region
REGIONS = {
    "Nagpur":    (21.1458, 79.0882),
    "Kerala":    (9.9312, 76.2673),    # Kochi
    "Rajasthan": (26.9124, 75.7873),   # Jaipur
    "Punjab":    (30.9010, 75.8573),   # Ludhiana
}

DAILY = ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
         "precipitation_sum", "relative_humidity_2m_mean",
         "wind_speed_10m_mean", "surface_pressure_mean"]


def fetch_region(name: str, lat: float, lon: float):
    """Returns (daily_df, monthly_df) for one region."""
    params = {"latitude": lat, "longitude": lon,
              "start_date": START, "end_date": END,
              "daily": ",".join(DAILY), "timezone": "Asia/Kolkata"}
    r = requests.get(API, params=params, timeout=60)
    r.raise_for_status()
    d = pd.DataFrame(r.json()["daily"])
    d["time"] = pd.to_datetime(d["time"])
    d["year"], d["month"] = d["time"].dt.year, d["time"].dt.month

    # Daily table (kept as-is, with friendly column names)
    daily = d.rename(columns={
        "time": "date",
        "temperature_2m_mean": "avg_temp_c",
        "temperature_2m_max": "max_temp_c",
        "temperature_2m_min": "min_temp_c",
        "precipitation_sum": "rainfall_mm",
        "relative_humidity_2m_mean": "humidity_pct",
        "wind_speed_10m_mean": "wind_kmh",
        "surface_pressure_mean": "pressure_hpa",
    })
    daily["date"] = daily["date"].dt.strftime("%Y-%m-%d")
    daily["region"] = name

    # Daily values -> monthly values
    m = d.groupby(["year", "month"]).agg(
        avg_temp_c=("temperature_2m_mean", "mean"),
        max_temp_c=("temperature_2m_max", "max"),
        min_temp_c=("temperature_2m_min", "min"),
        rainfall_mm=("precipitation_sum", "sum"),
        humidity_pct=("relative_humidity_2m_mean", "mean"),
        wind_kmh=("wind_speed_10m_mean", "mean"),
        pressure_hpa=("surface_pressure_mean", "mean"),
    ).reset_index()
    m["region"] = name
    return daily, m


def main() -> None:
    dailies, monthlies = [], []
    for name, (lat, lon) in REGIONS.items():
        print(f"Fetching {name} ...")
        daily, monthly = fetch_region(name, lat, lon)
        dailies.append(daily)
        monthlies.append(monthly)

    # ── Monthly file (dataset.csv) ───────────────────────────
    df = pd.concat(monthlies, ignore_index=True)
    df["month_name"] = pd.to_datetime(df["month"].astype(str), format="%m").dt.strftime("%B")
    df = df[["year", "month", "month_name", "region", "avg_temp_c", "max_temp_c",
             "min_temp_c", "rainfall_mm", "humidity_pct", "wind_kmh", "pressure_hpa"]]
    df = df.round({"avg_temp_c": 1, "max_temp_c": 1, "min_temp_c": 1,
                   "rainfall_mm": 1, "humidity_pct": 0, "wind_kmh": 1,
                   "pressure_hpa": 0})

    expected = len(REGIONS) * 12 * 5
    if len(df) != expected or df.isna().any().any():
        sys.exit(f"Unexpected result: {len(df)} rows (expected {expected}), "
                 f"missing values: {int(df.isna().sum().sum())}. Not saving.")

    # ── Daily file (daily_data.csv) ──────────────────────────
    dd = pd.concat(dailies, ignore_index=True)
    dd = dd[["date", "year", "month", "region", "avg_temp_c", "max_temp_c",
             "min_temp_c", "rainfall_mm", "humidity_pct", "wind_kmh", "pressure_hpa"]]
    dd = dd.round({"avg_temp_c": 1, "max_temp_c": 1, "min_temp_c": 1,
                   "rainfall_mm": 1, "humidity_pct": 0, "wind_kmh": 1,
                   "pressure_hpa": 0})
    expected_daily = len(REGIONS) * 1827          # 2020-2024 has 1,827 days
    if len(dd) != expected_daily:
        sys.exit(f"Unexpected daily result: {len(dd)} rows (expected {expected_daily}). Not saving.")
    gaps = int(dd.isna().sum().sum())
    if gaps:
        print(f"Note: {gaps} missing daily values (left empty, SQL ignores them)")

    # ── Save ─────────────────────────────────────────────────
    if os.path.exists("dataset.csv") and not os.path.exists("dataset_sample.csv"):
        shutil.copy("dataset.csv", "dataset_sample.csv")  # keep the old sample
    df.to_csv("dataset.csv", index=False)
    dd.to_csv("daily_data.csv", index=False)
    print(f"Saved dataset.csv with {len(df)} rows")
    print(f"Saved daily_data.csv with {len(dd)} rows")


if __name__ == "__main__":
    main()
