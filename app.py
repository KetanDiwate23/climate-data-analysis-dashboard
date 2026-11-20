"""Interactive climate dashboard.

Run:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

st.set_page_config(page_title="Climate Dashboard", layout="wide")
st.title("Climate Data Analysis Dashboard")


@st.cache_data
def load() -> pd.DataFrame:
    df = pd.read_csv("dataset.csv")
    df["month_name"] = df["month"].astype(int).map(lambda m: MONTHS[m - 1])
    return df


df = load()

# ── Sidebar filters ──────────────────────────────────────────
regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()),
                                 default=sorted(df["region"].unique()))
years = sorted(df["year"].unique())
yr_lo, yr_hi = st.sidebar.select_slider("Years", options=years,
                                        value=(years[0], years[-1]))
metric = st.sidebar.selectbox("Metric", ["avg_temp_c", "rainfall_mm",
                                         "humidity_pct", "wind_kmh", "pressure_hpa"])

f = df[df["region"].isin(regions) & df["year"].between(yr_lo, yr_hi)]
if f.empty:
    st.warning("No data for this selection. Pick at least one region.")
    st.stop()

# ── KPI row ──────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg temperature (C)", f"{f['avg_temp_c'].mean():.1f}")
c2.metric("Hottest month (C)", f"{f['max_temp_c'].max():.1f}")
c3.metric("Total rainfall (mm)", f"{f['rainfall_mm'].sum():,.0f}")
c4.metric("Records", len(f))

# ── Charts ───────────────────────────────────────────────────
left, right = st.columns(2)
with left:
    st.subheader(f"{metric} by month")
    # "01 Jan", "02 Feb", ... so the chart sorts the months in calendar order
    pivot = (f.groupby(["month", "region"])[metric].mean().unstack("region")
               .rename(index=lambda m: f"{m:02d} {MONTHS[m - 1]}"))
    st.line_chart(pivot)
with right:
    st.subheader(f"Average {metric} by region")
    st.bar_chart(f.groupby("region")[metric].mean())

st.subheader("Correlation between variables")
cols = ["avg_temp_c", "rainfall_mm", "humidity_pct", "wind_kmh", "pressure_hpa"]
st.dataframe(f[cols].corr().style.format("{:.2f}").background_gradient(cmap="coolwarm", vmin=-1, vmax=1))

with st.expander("Data explorer"):
    st.dataframe(f.drop(columns=["month_name"]))

st.caption("Data: Open-Meteo.com (CC BY 4.0), based on ERA5 reanalysis (Copernicus / ECMWF). "
           "One representative city per region: Nagpur, Kochi (Kerala), Jaipur (Rajasthan), "
           "Ludhiana (Punjab).")