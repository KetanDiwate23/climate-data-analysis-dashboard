# 🛰️ Climate Data Analysis & Visualization System

> Analyzed large-scale environmental datasets using Python to identify weather trends, seasonal variations, and regional patterns through statistical modeling and graphical dashboards.

---

## 📌 Project Overview

This project is a **satellite-inspired climate data analysis pipeline** built with Python. It processes multi-year meteorological data from the India Meteorological Network and generates a suite of visualizations covering temperature trends, rainfall patterns, anomaly detection, and region-wise climate comparisons.

**Designed for:** Aerospace / Research / Data Engineering portfolios  
**Domain:** Environmental Data Science | Meteorology | Statistical Modeling

---

## 📁 Project Structure

```
climate-data-analysis-dashboard/
│
├── dataset.csv            ← Multi-region climate dataset (2020–2024)
├── climate_analysis.py    ← Main analysis & visualization pipeline
├── requirements.txt       ← Python dependencies
├── README.md              ← Project documentation
└── charts/                ← Auto-generated chart outputs (PNG)
    ├── 01_temperature_trend.png
    ├── 02_rainfall_comparison.png
    ├── 03_anomaly_heatmap.png
    ├── 04_regional_comparison.png
    ├── 05_seasonal_dashboard.png
    ├── 06_correlation_matrix.png
    └── 07_rolling_average.png
```

---

## 📊 Charts Generated

| # | Chart | Description |
|---|-------|-------------|
| 1 | Temperature Trend | Year-on-year monthly temp comparison (2020–2024) with max/min shaded band |
| 2 | Rainfall Comparison | 2024 actual rainfall vs. 4-year historical average with deficit/surplus annotation |
| 3 | Anomaly Heatmap | 10×12 grid heatmap of temperature anomalies (deviation from baseline mean) |
| 4 | Regional Comparison | Side-by-side multi-region temp profiles and annual rainfall ranking |
| 5 | Seasonal Dashboard | 4-panel summary: temp range, humidity & wind, rainfall intensity, pressure |
| 6 | Correlation Matrix | Pearson correlation heatmap across all climate variables |
| 7 | Rolling Average | 3-month rolling temperature average across the full 5-year dataset |

---

## 🗃️ Dataset

**File:** `dataset.csv`  
**Records:** ~192 rows (monthly data)  
**Regions:** Nagpur, Kerala, Rajasthan, Punjab  
**Years:** 2020 – 2024  

| Column | Unit | Description |
|--------|------|-------------|
| `year` | — | Calendar year |
| `month` | 1–12 | Month number |
| `month_name` | — | Month abbreviation |
| `region` | — | Indian state/city |
| `avg_temp_c` | °C | Monthly average temperature |
| `max_temp_c` | °C | Monthly maximum temperature |
| `min_temp_c` | °C | Monthly minimum temperature |
| `rainfall_mm` | mm | Total monthly rainfall |
| `humidity_pct` | % | Average relative humidity |
| `wind_kmh` | km/h | Average wind speed |
| `pressure_hpa` | hPa | Average atmospheric pressure |

> **Data source:** Modeled after India Meteorological Department (IMD) station records and NOAA ERA5 reanalysis data.

---

## ⚙️ Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/your-username/climate-data-analysis-dashboard.git
cd climate-data-analysis-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the analysis
```bash
python climate_analysis.py
```

All 7 charts will be saved to the `charts/` folder automatically.

---

## 🔬 Statistical Methods Used

| Technique | Application |
|-----------|-------------|
| **Z-Score Anomaly Detection** | Identifying months with abnormal temperatures vs. baseline |
| **Rolling Mean (3-month window)** | Smoothing short-term fluctuations to reveal long-term trends |
| **Pearson Correlation** | Measuring relationships between climate variables |
| **Grouped Aggregation** | Monthly/annual statistics by region and year |
| **Pivot Tables** | Restructuring data for heatmap visualization |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| `Python 3.10+` | Core language |
| `Pandas` | Data loading, cleaning, groupby aggregation |
| `NumPy` | Numerical operations, z-score calculation |
| `Matplotlib` | All chart rendering and layout |
| `Seaborn` | Heatmaps and statistical visualization |

---

## 🔧 Extend This Project

Ideas to expand:
- [ ] Add real-time data fetch from [Open-Meteo API](https://open-meteo.com/) (free, no key needed)
- [ ] Add more Indian cities (Mumbai, Chennai, Delhi, Kolkata)
- [ ] Export summary statistics to a PDF report
- [ ] Add a Streamlit web dashboard for interactive exploration
- [ ] Train a simple ML model (Linear Regression / LSTM) to forecast temperature

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👤 Author

**[Your Name]**  
B.Tech — [Your Branch], [Your College]  
[LinkedIn](https://linkedin.com/in/your-profile) · [GitHub](https://github.com/your-username)

---

*Resume Line: "Developed a Climate Data Analysis and Visualization System in Python using Pandas, NumPy, and Matplotlib to process 5-year meteorological datasets, identify temperature anomalies using z-score statistical modeling, and generate multi-panel graphical dashboards for regional climate comparison."*
