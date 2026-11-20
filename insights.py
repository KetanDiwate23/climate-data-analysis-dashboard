"""Auto-generates insights.md from whatever is in dataset.csv.

Every number written here is computed from the data, so the findings
always match the dataset (sample data or real data from fetch_data.py).
"""
import numpy as np
import pandas as pd

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def write_insights(df: pd.DataFrame, path: str = "insights.md") -> None:
    lines = ["# Key Findings", "",
             f"_Auto-generated from `dataset.csv` ({len(df)} rows, "
             f"{df['region'].nunique()} regions, "
             f"{int(df['year'].min())}-{int(df['year'].max())})._", ""]

    # 1. Hottest month in Nagpur
    nag = df[df["region"] == "Nagpur"]
    by_month = nag.groupby("month")["avg_temp_c"].mean()
    hot = int(by_month.idxmax())
    lines.append(f"1. **Hottest month (Nagpur):** {MONTHS[hot-1]}, averaging "
                 f"{by_month.max():.1f} C across "
                 f"{nag['year'].nunique()} years.")

    # 2. Yearly temperature trend in Nagpur (linear slope)
    yearly = nag.groupby("year")["avg_temp_c"].mean()
    if len(yearly) >= 3:
        slope = np.polyfit(yearly.index, yearly.values, 1)[0]
        direction = "warming" if slope > 0 else "cooling"
        lines.append(f"2. **Trend (Nagpur):** annual mean temperature shows a "
                     f"{direction} slope of {slope:+.2f} C per year "
                     f"({yearly.index.min()}-{yearly.index.max()}).")

    # 3. Most anomalous month: latest year vs earlier years (z-score)
    last = int(nag["year"].max())
    base = nag[nag["year"] < last]
    if base["year"].nunique() >= 2:
        mu = base.groupby("month")["avg_temp_c"].mean()
        sd = base.groupby("month")["avg_temp_c"].std().replace(0, np.nan)
        z = ((nag[nag["year"] == last].set_index("month")["avg_temp_c"] - mu) / sd).dropna()
        m = int(z.abs().idxmax())
        lines.append(f"3. **Most anomalous month ({last}, Nagpur):** {MONTHS[m-1]} "
                     f"with z-score {z[m]:+.2f} vs the {base['year'].min()}-"
                     f"{base['year'].max()} baseline.")

    # 4. Wettest vs driest region, using the latest year all regions share
    common = df.groupby("year")["region"].nunique()
    full_years = common[common == df["region"].nunique()].index
    if len(full_years):
        y = int(full_years.max())
        rain = df[df["year"] == y].groupby("region")["rainfall_mm"].sum().sort_values()
        lines.append(f"4. **Rainfall by region ({y}):** wettest is "
                     f"{rain.index[-1]} ({rain.iloc[-1]:.0f} mm), driest is "
                     f"{rain.index[0]} ({rain.iloc[0]:.0f} mm).")

    # 5. Strongest correlation between two different variables
    num = df[["avg_temp_c", "rainfall_mm", "humidity_pct", "wind_kmh", "pressure_hpa"]]
    corr = num.corr().abs().where(~np.eye(num.shape[1], dtype=bool))
    a, b = corr.stack().idxmax()
    r = num[a].corr(num[b])
    lines.append(f"5. **Strongest correlation:** {a} vs {b} (r = {r:+.2f}).")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines) + "\n")
