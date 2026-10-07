# Chicago Traffic Crash Analytics

CS 418 Group Project

## Team

- Anirudh Kuppili (anirudhk_tech)
- Karim Nashawi (KarimNashawi)
- Kareem Muftee (k-mufti)
- Arslan Kamchybekov (ArslanKamchybekov)
- Nguyen Tuan Kiet Ho (kiet08hogit)

## Research Question

What factors predict whether a Chicago traffic crash results in injury, and do
time-of-day and weather effects persist after controlling for road and crash
characteristics (e.g. road surface, lighting condition, posted speed limit,
crash type)?

## Datasets

### Primary

1. **[Traffic Crashes - Crashes](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if)**
   (City of Chicago Data Portal). Crash-level records since September 2017,
   including injury outcome, weather condition, lighting condition, road
   surface condition, posted speed limit, and crash time/date. This is the
   core table for the injury-prediction model.
2. **[Traffic Crashes - People](https://data.cityofchicago.org/Transportation/Traffic-Crashes-People/u6pd-qa9d)**
   (City of Chicago Data Portal). Person-level records for everyone involved
   in a crash, with a finer-grained injury classification per person plus
   demographics (age, sex) and safety equipment used. Lets us build a more
   precise injury target and check whether person-level factors matter
   alongside crash-level ones.

### Secondary

1. **NOAA daily weather data (GHCND)** (Midway station, via NOAA Climate
   Data Online). We'd join this to crash dates to cross-check the crash
   report's self-reported weather field against actual recorded conditions
   (precipitation, snow, temperature) on the day of the crash.
2. **[Chicago Traffic Tracker - Historical Congestion Estimates by Segment](https://data.cityofchicago.org/Transportation/Chicago-Traffic-Tracker-Historical-Congestion-Esti/4g9f-3jbs)**
   (City of Chicago Data Portal). Speed/congestion estimates by road segment.
   We'd compare this against crash locations/times to see whether traffic
   volume or congestion level is a confounder for the road-characteristic
   controls in the model.

## Data Acquisition

See `notebooks/data_acquisition.ipynb` for the full pull (column types, head
of each dataframe, etc.). Basic shape and coverage, from actually running the
notebook:

| Dataset | Rows | Columns | Time span pulled | Geography |
|---|---|---|---|---|
| Traffic Crashes - Crashes | 222,811 | 49 | 2023-01-01 to 2024-12-31 (full window, paginated) | Chicago |
| Traffic Crashes - People | 491,892 | 29 | 2023-01-01 to 2024-12-31 (full window, paginated) | Chicago |
| NOAA daily weather (GHCND) | 317 | 5 | 2023-01-01 to 2023-01-31 | Midway station (GHCND:USW00014819) |
| Traffic Tracker Congestion | 50,000 | 22 | 2024-06-11 (single day) | Chicago arterial segments |

One row in Traffic Crashes - Crashes represents a single crash event. One row
in Traffic Crashes - People represents one person involved in a crash (so
multiple rows per crash, ~2.2 people per crash on average). The crashes and
people tables are now pulled in full for the 2023-2024 window via pagination
(`scripts/fetch_full_data.py`) rather than the 50,000-row sample from the
Checkpoint 2 pull, which undercounted ~78% of crashes and ~90% of people in
that window. Columns we care most about in Crashes: `injuries_total`,
`most_severe_injury`, `weather_condition`, `lighting_condition`,
`roadway_surface_cond`, `road_defect`, `posted_speed_limit`, `crash_hour`,
`crash_day_of_week`, `first_crash_type`.

## Exploratory Analysis

Full writeup: [`EDA.md`](EDA.md). Notebook: [`notebooks/eda.ipynb`](notebooks/eda.ipynb).

**Dataset basics:** Traffic Crashes - Crashes is 222,811 rows × 49 columns
(one row per crash); Traffic Crashes - People is 491,892 rows × 29 columns
(one row per person involved in a crash). All API columns come back as
strings and need `pd.to_numeric()` before numeric analysis.

**Revised research question:** What factors predict whether a Chicago
traffic crash results in injury, and do time-of-day, lighting, and weather
effects persist after controlling for road characteristics (surface,
defect, speed limit, crash type) and, if available, traffic
volume/congestion? (Added lighting and congestion explicitly, and class
imbalance as a modeling consideration, see `EDA.md` section 5 for why.)

**Anomalies found:**

| Anomaly | Rows affected | What we did |
|---|---|---|
| All columns typed as `str`, including numeric fields | All rows | Cast with `pd.to_numeric(errors="coerce")` |
| Invalid posted speed limit (0 or >70 mph) | 364 crash rows | Excluded from distribution plot; will exclude/cap for modeling |
| `"UNKNOWN"` as a non-null placeholder (weather/lighting/surface/road-defect) | 6.7-25.7% of rows depending on field | Kept as explicit category, treated as missing-not-at-random |
| Invalid ages (negative or >100) | 24 people rows | Will drop for age-based analysis |
| Missing age | 143,700 people rows (~29%) | Left null, not central to crash-level model |
| Duplicate crash records | 0 | Checked, none found |

**Significant findings:** Injury rate is a minority outcome overall (15.8%)
but varies meaningfully by hour (~13% midday vs. ~19-20% overnight), weather
(up to 25% in severe conditions vs. 16.4% in clear weather, with a
surprising exception where snow alone is *below* average), and lighting
(19.8% for lit darkness vs. 15.4% for daylight). These three factors look
correlated with each other, which motivates the planned baseline-vs-full
model comparison to see which effects are independent. A first pass joining
the Traffic Tracker Congestion dataset also hints that traffic
speed/volume may be a relevant additional control.

## Setup

```
pip install -r requirements.txt
```
