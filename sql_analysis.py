"""Load the CSV files into SQLite and run the queries in queries.sql.

Tables:
  climate  <- dataset.csv     (monthly data)
  daily    <- daily_data.csv  (daily data, created by fetch_data.py)

Run:  python sql_analysis.py
"""
import os
import re
import sqlite3

import pandas as pd


def main() -> None:
    con = sqlite3.connect(":memory:")          # temporary in-memory database

    monthly = pd.read_csv("dataset.csv")
    monthly.to_sql("climate", con, index=False)
    print(f"Loaded {len(monthly)} rows into table 'climate' (monthly)")

    has_daily = os.path.exists("daily_data.csv")
    if has_daily:
        daily = pd.read_csv("daily_data.csv")
        daily.to_sql("daily", con, index=False)
        print(f"Loaded {len(daily)} rows into table 'daily'")
    else:
        print("daily_data.csv not found, skipping daily queries (run fetch_data.py)")
    print()

    sql = open("queries.sql", encoding="utf-8").read()
    for block in re.split(r"(?m)^-- name: ", sql)[1:]:
        title, query = block.split("\n", 1)
        if not has_daily and re.search(r"\bFROM daily\b", query):
            continue
        print("=" * 70)
        print(title)
        print("=" * 70)
        print(pd.read_sql_query(query, con).to_string(index=False), "\n")
    con.close()


if __name__ == "__main__":
    main()
