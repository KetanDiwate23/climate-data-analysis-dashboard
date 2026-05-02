
#  Climate Data Analysis & Visualization System
#  Author  : [Ketan Diwate]
#  Dataset : India Meteorological Network — Nagpur & Regions
#  Tools   : Python | Pandas | NumPy | Matplotlib | Seaborn


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")

# ── Output folder ────────────────────────────────────────────
os.makedirs("charts", exist_ok=True)

# ── Global style ─────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0a0e1a",
    "axes.facecolor":   "#111827",
    "axes.edgecolor":   "#1e3054",
    "axes.labelcolor":  "#94a3b8",
    "axes.titlecolor":  "#e2e8f0",
    "axes.titlesize":   13,
    "axes.labelsize":   10,
    "xtick.color":      "#64748b",
    "ytick.color":      "#64748b",
    "xtick.labelsize":  9,
    "ytick.labelsize":  9,
    "grid.color":       "#1e3054",
    "grid.linestyle":   "--",
    "grid.alpha":       0.6,
    "text.color":       "#e2e8f0",
    "legend.facecolor": "#111827",
    "legend.edgecolor": "#1e3054",
    "legend.fontsize":  9,
    "font.family":      "monospace",
})

ACCENT_BLUE   = "#00d4ff"
ACCENT_GREEN  = "#4ade80"
ACCENT_AMBER  = "#f59e0b"
ACCENT_PINK   = "#f472b6"
ACCENT_RED    = "#dc2626"
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]


# ════════════════════════════════════════════════════════════
#  1. LOAD & VALIDATE DATA
# ════════════════════════════════════════════════════════════
def load_data(filepath: str = "dataset.csv") -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()
    df["month_name"] = pd.Categorical(df["month_name"], categories=MONTHS, ordered=True)
    print(f"✔  Loaded {len(df)} records | Regions: {df['region'].unique().tolist()}")
    print(f"   Years : {sorted(df['year'].unique().tolist())}")
    print(f"   Cols  : {df.columns.tolist()}\n")
    return df


# ════════════════════════════════════════════════════════════
#  2. STATISTICAL SUMMARY
# ════════════════════════════════════════════════════════════
def statistical_summary(df: pd.DataFrame) -> None:
    nagpur = df[df["region"] == "Nagpur"]

    print("=" * 55)
    print("  CLIMATE STATISTICAL SUMMARY — NAGPUR (2020–2024)")
    print("=" * 55)

    stats = nagpur.groupby("month_name", observed=True).agg(
        Mean_Temp   = ("avg_temp_c",   "mean"),
        Std_Temp    = ("avg_temp_c",   "std"),
        Max_Temp    = ("max_temp_c",   "max"),
        Min_Temp    = ("min_temp_c",   "min"),
        Total_Rain  = ("rainfall_mm",  "sum"),
        Avg_Rain    = ("rainfall_mm",  "mean"),
        Avg_Humidity= ("humidity_pct", "mean"),
    ).round(2)

    print(stats.to_string())

    # Z-score anomaly detection
    nagpur_2024 = nagpur[nagpur["year"] == 2024].copy().sort_values("month")
    baseline    = nagpur[nagpur["year"] < 2024]
    base_mean   = baseline.groupby("month")["avg_temp_c"].mean()
    base_std    = baseline.groupby("month")["avg_temp_c"].std()

    nagpur_2024 = nagpur_2024.set_index("month")
    nagpur_2024["anomaly_z"] = (
        (nagpur_2024["avg_temp_c"] - base_mean) / base_std
    ).round(2)
    nagpur_2024.index = [MONTHS[m-1] for m in nagpur_2024.index]

    print("\n  TEMPERATURE ANOMALY — 2024 vs 2020–2023 Baseline (Z-Score)")
    print("-" * 55)
    print(nagpur_2024[["avg_temp_c","anomaly_z"]].rename(
        columns={"avg_temp_c":"Temp(°C)","anomaly_z":"Z-Score"}).to_string())
    print(f"\n  Annual Mean Temp  : {nagpur_2024['avg_temp_c'].mean():.1f}°C")
    print(f"  Annual Rainfall   : {nagpur_2024['rainfall_mm'].sum():.0f} mm")
    print(f"  Max Temp Recorded : {nagpur_2024['max_temp_c'].max():.1f}°C")
    print(f"  Min Temp Recorded : {nagpur_2024['min_temp_c'].min():.1f}°C")
    print("=" * 55 + "\n")


# ════════════════════════════════════════════════════════════
#  3. CHART 1 — Temperature Trend (line + range band)
# ════════════════════════════════════════════════════════════
def chart_temperature_trend(df: pd.DataFrame) -> None:
    nagpur = df[df["region"] == "Nagpur"]
    yearly = nagpur.groupby(["year","month"], observed=True).agg(
        avg=("avg_temp_c","mean"),
        hi =("max_temp_c","mean"),
        lo =("min_temp_c","mean"),
    ).reset_index()

    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor("#0a0e1a")

    colors = [ACCENT_BLUE, ACCENT_GREEN, ACCENT_AMBER, ACCENT_PINK, "#a78bfa"]
    years  = sorted(nagpur["year"].unique())

    for i, yr in enumerate(years):
        yd = yearly[yearly["year"] == yr].sort_values("month")
        lw = 2.5 if yr == 2024 else 1.2
        ls = "-"  if yr == 2024 else "--"
        ax.plot(yd["month"], yd["avg"], color=colors[i], lw=lw, ls=ls,
                label=str(yr), zorder=3)
        if yr == 2024:
            ax.fill_between(yd["month"], yd["lo"], yd["hi"],
                            color=ACCENT_BLUE, alpha=0.10, zorder=1)

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MONTHS)
    ax.set_xlabel("Month")
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("MONTHLY TEMPERATURE TREND — NAGPUR (2020–2024)\n"
                 "Shaded band = 2024 Max/Min range", pad=12)
    ax.legend(loc="upper right", ncol=5)
    ax.grid(True, axis="y")

    plt.tight_layout()
    plt.savefig("charts/01_temperature_trend.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("✔  Saved: charts/01_temperature_trend.png")


# ════════════════════════════════════════════════════════════
#  4. CHART 2 — Rainfall vs Historical Average (bar + line)
# ════════════════════════════════════════════════════════════
def chart_rainfall_comparison(df: pd.DataFrame) -> None:
    nagpur   = df[df["region"] == "Nagpur"]
    hist_avg = nagpur[nagpur["year"] < 2024].groupby("month", observed=True)["rainfall_mm"].mean()
    curr     = nagpur[nagpur["year"] == 2024].sort_values("month")

    fig, ax = plt.subplots(figsize=(13, 5))
    fig.patch.set_facecolor("#0a0e1a")

    x = np.arange(1, 13)
    bars = ax.bar(x, curr["rainfall_mm"].values, color=ACCENT_GREEN,
                  alpha=0.70, width=0.6, label="2024 Actual", zorder=2)
    ax.plot(x, hist_avg.values, color=ACCENT_PINK, lw=2.2,
            linestyle="--", marker="o", markersize=4,
            label="2020–2023 Avg", zorder=3)

    # Annotate deficit / surplus
    for xi, (actual, avg) in enumerate(zip(curr["rainfall_mm"].values, hist_avg.values), start=1):
        diff = actual - avg
        color = ACCENT_AMBER if diff < 0 else ACCENT_GREEN
        ax.annotate(f"{diff:+.0f}", xy=(xi, max(actual, avg) + 8),
                    ha="center", fontsize=7.5, color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS)
    ax.set_ylabel("Rainfall (mm)")
    ax.set_title("MONTHLY RAINFALL — 2024 ACTUAL vs HISTORICAL AVERAGE\n"
                 "Annotations show mm surplus (+) / deficit (−)", pad=12)
    ax.legend()
    ax.grid(True, axis="y")

    plt.tight_layout()
    plt.savefig("charts/02_rainfall_comparison.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("✔  Saved: charts/02_rainfall_comparison.png")


# ════════════════════════════════════════════════════════════
#  5. CHART 3 — Temperature Anomaly Heatmap (10 year × 12 month)
# ════════════════════════════════════════════════════════════
def chart_anomaly_heatmap(df: pd.DataFrame) -> None:
    nagpur   = df[df["region"] == "Nagpur"]
    baseline = nagpur.groupby("month")["avg_temp_c"].mean()
    pivot    = nagpur.pivot_table(index="year", columns="month", values="avg_temp_c")
    anomaly  = pivot.subtract(baseline, axis=1)

    fig, ax = plt.subplots(figsize=(13, 5))
    fig.patch.set_facecolor("#0a0e1a")

    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(anomaly, ax=ax, cmap=cmap, center=0,
                linewidths=0.5, linecolor="#0a0e1a",
                annot=True, fmt=".1f", annot_kws={"size": 8, "color": "#e2e8f0"},
                cbar_kws={"label": "Temp Anomaly (°C)", "shrink": 0.8})

    ax.set_xticklabels(MONTHS, rotation=0)
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    ax.set_title("TEMPERATURE ANOMALY HEATMAP\n"
                 "Deviation from monthly baseline mean (°C)", pad=12)

    plt.tight_layout()
    plt.savefig("charts/03_anomaly_heatmap.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("✔  Saved: charts/03_anomaly_heatmap.png")


# ════════════════════════════════════════════════════════════
#  6. CHART 4 — Regional Climate Comparison (multi-panel)
# ════════════════════════════════════════════════════════════
def chart_regional_comparison(df: pd.DataFrame) -> None:
    df_2024  = df[df["year"] == 2024]
    regions  = df_2024["region"].unique()
    pal      = [ACCENT_BLUE, ACCENT_GREEN, ACCENT_AMBER, ACCENT_PINK]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor("#0a0e1a")

    # ─ Panel A: Temperature ────────────────────────
    ax = axes[0]
    for i, region in enumerate(regions):
        rd = df_2024[df_2024["region"] == region].sort_values("month")
        ax.plot(rd["month"], rd["avg_temp_c"], color=pal[i % len(pal)],
                lw=2, marker="o", markersize=3, label=region)

    ax.set_xticks(range(1, 13)); ax.set_xticklabels(MONTHS, fontsize=8)
    ax.set_ylabel("Temperature (°C)")
    ax.set_title("REGIONAL TEMPERATURE PROFILE — 2024", pad=10)
    ax.legend(fontsize=8); ax.grid(True, axis="y")

    # ─ Panel B: Rainfall ───────────────────────────
    ax = axes[1]
    region_totals = df_2024.groupby("region")["rainfall_mm"].sum().sort_values(ascending=True)
    bars = ax.barh(region_totals.index, region_totals.values,
                   color=[pal[i % len(pal)] for i in range(len(region_totals))],
                   alpha=0.8, height=0.6)
    for bar, val in zip(bars, region_totals.values):
        ax.text(val + 30, bar.get_y() + bar.get_height() / 2,
                f"{val:.0f} mm", va="center", fontsize=9, color="#e2e8f0")

    ax.set_xlabel("Annual Rainfall (mm)")
    ax.set_title("ANNUAL RAINFALL BY REGION — 2024", pad=10)
    ax.grid(True, axis="x")

    plt.tight_layout()
    plt.savefig("charts/04_regional_comparison.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("✔  Saved: charts/04_regional_comparison.png")


# ════════════════════════════════════════════════════════════
#  7. CHART 5 — Seasonal Dashboard (4-panel summary)
# ════════════════════════════════════════════════════════════
def chart_seasonal_dashboard(df: pd.DataFrame) -> None:
    nagpur = df[(df["region"] == "Nagpur") & (df["year"] == 2024)].sort_values("month")

    fig = plt.figure(figsize=(14, 9))
    fig.patch.set_facecolor("#0a0e1a")
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.38, wspace=0.32)

    # ─ Panel A: Temp Max / Mean / Min ──────────────
    ax1 = fig.add_subplot(gs[0, 0])
    x   = np.arange(12)
    ax1.bar(x - 0.25, nagpur["max_temp_c"], 0.25, color=ACCENT_RED,    alpha=0.8, label="Max")
    ax1.bar(x,        nagpur["avg_temp_c"], 0.25, color=ACCENT_AMBER,  alpha=0.8, label="Mean")
    ax1.bar(x + 0.25, nagpur["min_temp_c"], 0.25, color=ACCENT_BLUE,   alpha=0.8, label="Min")
    ax1.set_xticks(x); ax1.set_xticklabels(MONTHS, fontsize=7.5)
    ax1.set_ylabel("°C"); ax1.set_title("TEMPERATURE RANGE", pad=8)
    ax1.legend(fontsize=7); ax1.grid(True, axis="y")

    # ─ Panel B: Humidity & Wind ────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ln1 = ax2.plot(x, nagpur["humidity_pct"], color=ACCENT_GREEN,  lw=2, marker="o",
                   markersize=3, label="Humidity (%)")
    ax2b = ax2.twinx()
    ax2b.tick_params(colors="#64748b")
    ln2 = ax2b.plot(x, nagpur["wind_kmh"], color=ACCENT_PINK, lw=2,
                    linestyle="--", marker="s", markersize=3, label="Wind (km/h)")
    ax2.set_xticks(x); ax2.set_xticklabels(MONTHS, fontsize=7.5)
    ax2.set_ylabel("Humidity (%)"); ax2b.set_ylabel("Wind (km/h)")
    ax2.set_title("HUMIDITY & WIND SPEED", pad=8)
    lns = ln1 + ln2
    ax2.legend(lns, [l.get_label() for l in lns], fontsize=7)
    ax2.grid(True, axis="y")

    # ─ Panel C: Rainfall monthly ───────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    bar_colors = [ACCENT_BLUE if v < 50 else ACCENT_GREEN if v < 200 else ACCENT_AMBER
                  for v in nagpur["rainfall_mm"]]
    ax3.bar(x, nagpur["rainfall_mm"], color=bar_colors, alpha=0.85, width=0.7)
    ax3.set_xticks(x); ax3.set_xticklabels(MONTHS, fontsize=7.5)
    ax3.set_ylabel("Rainfall (mm)"); ax3.set_title("MONTHLY RAINFALL", pad=8)
    patches = [mpatches.Patch(color=ACCENT_BLUE,  label="Dry <50mm"),
               mpatches.Patch(color=ACCENT_GREEN, label="Moderate <200mm"),
               mpatches.Patch(color=ACCENT_AMBER, label="Heavy ≥200mm")]
    ax3.legend(handles=patches, fontsize=7)
    ax3.grid(True, axis="y")

    # ─ Panel D: Pressure ───────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.fill_between(x, nagpur["pressure_hpa"], alpha=0.15, color=ACCENT_PINK)
    ax4.plot(x, nagpur["pressure_hpa"], color=ACCENT_PINK, lw=2, marker="D",
             markersize=3)
    ax4.set_xticks(x); ax4.set_xticklabels(MONTHS, fontsize=7.5)
    ax4.set_ylabel("Pressure (hPa)"); ax4.set_title("ATMOSPHERIC PRESSURE", pad=8)
    ax4.grid(True, axis="y")

    fig.suptitle("SEASONAL CLIMATE DASHBOARD — NAGPUR 2024",
                 fontsize=14, color=ACCENT_BLUE, y=1.01,
                 fontfamily="monospace", fontweight="bold")

    plt.savefig("charts/05_seasonal_dashboard.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("✔  Saved: charts/05_seasonal_dashboard.png")


# ════════════════════════════════════════════════════════════
#  8. CHART 6 — Correlation Heatmap
# ════════════════════════════════════════════════════════════
def chart_correlation_matrix(df: pd.DataFrame) -> None:
    nagpur = df[df["region"] == "Nagpur"]
    cols   = ["avg_temp_c","max_temp_c","min_temp_c",
              "rainfall_mm","humidity_pct","wind_kmh","pressure_hpa"]
    corr   = nagpur[cols].corr()

    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor("#0a0e1a")

    mask = np.triu(np.ones_like(corr, dtype=bool))
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(corr, ax=ax, mask=mask, cmap=cmap, center=0,
                annot=True, fmt=".2f", annot_kws={"size": 9},
                linewidths=0.5, linecolor="#0a0e1a",
                cbar_kws={"shrink": 0.8})

    ax.set_title("CLIMATE VARIABLE CORRELATION MATRIX\n"
                 "Pearson r — Nagpur 2020–2024", pad=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")

    plt.tight_layout()
    plt.savefig("charts/06_correlation_matrix.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("✔  Saved: charts/06_correlation_matrix.png")


# ════════════════════════════════════════════════════════════
#  9. CHART 7 — Rolling 3-Month Temperature Average
# ════════════════════════════════════════════════════════════
def chart_rolling_average(df: pd.DataFrame) -> None:
    nagpur = df[df["region"] == "Nagpur"].sort_values(["year","month"])
    nagpur = nagpur.copy()
    nagpur["rolling_temp"] = nagpur["avg_temp_c"].rolling(window=3, min_periods=1).mean()
    nagpur["index"] = range(len(nagpur))

    fig, ax = plt.subplots(figsize=(14, 5))
    fig.patch.set_facecolor("#0a0e1a")

    ax.plot(nagpur["index"], nagpur["avg_temp_c"], color=ACCENT_BLUE,
            lw=1.2, alpha=0.5, label="Monthly Temp")
    ax.plot(nagpur["index"], nagpur["rolling_temp"], color=ACCENT_AMBER,
            lw=2.5, label="3-Month Rolling Avg")

    # Year separators
    for yr_start in nagpur.groupby("year")["index"].min():
        ax.axvline(yr_start, color="#1e3054", lw=1.2, ls=":")

    years_pos = nagpur.groupby("year")["index"].mean()
    for yr, pos in years_pos.items():
        ax.text(pos, ax.get_ylim()[0] - 1, str(yr),
                ha="center", fontsize=8, color="#64748b")

    ax.set_ylabel("Temperature (°C)")
    ax.set_title("TEMPERATURE TREND WITH 3-MONTH ROLLING AVERAGE — 2020–2024", pad=12)
    ax.legend(); ax.grid(True, axis="y")
    ax.set_xticks([])

    plt.tight_layout()
    plt.savefig("charts/07_rolling_average.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    print("✔  Saved: charts/07_rolling_average.png")


# ════════════════════════════════════════════════════════════
#  MAIN RUNNER
# ════════════════════════════════════════════════════════════
def main():
    print("\n" + "═" * 55)
    print("  CLIMATE DATA ANALYSIS & VISUALIZATION SYSTEM")
    print("  India Meteorological Network — Python Pipeline")
    print("═" * 55 + "\n")

    df = load_data("dataset.csv")
    statistical_summary(df)

    print("Generating charts...\n")
    chart_temperature_trend(df)
    chart_rainfall_comparison(df)
    chart_anomaly_heatmap(df)
    chart_regional_comparison(df)
    chart_seasonal_dashboard(df)
    chart_correlation_matrix(df)
    chart_rolling_average(df)

    print("\n" + "═" * 55)
    print("  ✔  All 7 charts saved to /charts/")
    print("═" * 55 + "\n")


if __name__ == "__main__":
    main()
