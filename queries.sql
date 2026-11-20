-- name: Average climate by region
SELECT region,
       ROUND(AVG(avg_temp_c), 1)  AS avg_temp_c,
       ROUND(SUM(rainfall_mm), 0) AS total_rain_mm,
       COUNT(*)                   AS months_of_data
FROM climate
GROUP BY region
ORDER BY avg_temp_c DESC;

-- name: Five hottest months on record
SELECT region, year, month_name, avg_temp_c
FROM climate
ORDER BY avg_temp_c DESC
LIMIT 5;

-- name: Rank regions by rainfall within each year (window function RANK)
SELECT year, region, ROUND(SUM(rainfall_mm), 0) AS rain_mm,
       RANK() OVER (PARTITION BY year ORDER BY SUM(rainfall_mm) DESC) AS rain_rank
FROM climate
GROUP BY year, region
ORDER BY year, rain_rank;

-- name: Nagpur 3-month rolling average temperature (window function AVG OVER)
SELECT year, month,
       avg_temp_c,
       ROUND(AVG(avg_temp_c) OVER (
           ORDER BY year, month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS rolling_3m
FROM climate
WHERE region = 'Nagpur'
ORDER BY year, month
LIMIT 12;

-- name: Nagpur year-over-year change in annual temperature (window function LAG)
WITH yearly AS (
    SELECT year, ROUND(AVG(avg_temp_c), 2) AS annual_temp
    FROM climate WHERE region = 'Nagpur' GROUP BY year
)
SELECT year, annual_temp,
       ROUND(annual_temp - LAG(annual_temp) OVER (ORDER BY year), 2) AS change_vs_prev_year
FROM yearly
ORDER BY year;

-- name: Months where Nagpur rainfall exceeded 100 mm (HAVING / filtering)
SELECT month_name, ROUND(AVG(rainfall_mm), 1) AS avg_rain_mm
FROM climate
WHERE region = 'Nagpur'
GROUP BY month, month_name
HAVING AVG(rainfall_mm) > 100
ORDER BY month;

-- name: Five hottest days on record (daily table)
SELECT date, region, max_temp_c
FROM daily
ORDER BY max_temp_c DESC
LIMIT 5;

-- name: Days with max temperature of 40 C or more, per region and year
SELECT region, year,
       SUM(CASE WHEN max_temp_c >= 40 THEN 1 ELSE 0 END) AS days_40c_plus
FROM daily
GROUP BY region, year
ORDER BY region, year;

-- name: Rainy days (2.5 mm or more) per region and year
SELECT region, year,
       SUM(CASE WHEN rainfall_mm >= 2.5 THEN 1 ELSE 0 END) AS rainy_days,
       ROUND(SUM(rainfall_mm), 0) AS total_rain_mm
FROM daily
GROUP BY region, year
ORDER BY region, year;

-- name: Longest heatwave streak per region (max temp 40 C or more, consecutive days)
-- Gaps-and-islands: dates in the same streak share the same (date - row number) value.
WITH hot AS (
    SELECT region, date,
           julianday(date) - ROW_NUMBER() OVER (PARTITION BY region ORDER BY date) AS grp
    FROM daily
    WHERE max_temp_c >= 40
),
streaks AS (
    SELECT region, MIN(date) AS start_date, MAX(date) AS end_date, COUNT(*) AS days
    FROM hot
    GROUP BY region, grp
)
SELECT region, start_date, end_date, days
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY region ORDER BY days DESC) AS rn
    FROM streaks
)
WHERE rn = 1
ORDER BY days DESC;
