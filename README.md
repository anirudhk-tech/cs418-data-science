# Chicago Traffic Crash Analytics

CS 418 Group Project

## Team

- Anirudh Kuppili (anirudhk_tech)
- Karim Nashawi (KarimNashawi)

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
| Traffic Crashes - Crashes | 50,000 | 49 | 2023-01-01 to 2024-12-31 (capped at `$limit=50000`) | Chicago |
| Traffic Crashes - People | 50,000 | 28 | 2023-01-01 to 2024-12-31 (capped at `$limit=50000`) | Chicago |
| NOAA daily weather (GHCND) | 317 | 5 | 2023-01-01 to 2023-01-31 | Midway station (GHCND:USW00014819) |
| Traffic Tracker Congestion | 50,000 | 22 | 2024-06-11 to 2024-07-11 (capped at `$limit=50000`) | Chicago arterial segments |

One row in Traffic Crashes - Crashes represents a single crash event. One row
in Traffic Crashes - People represents one person involved in a crash (so
multiple rows per crash). The crashes/people/congestion pulls are capped by
`$limit=50000` and are not full history, crashes alone has 950K+ rows since
2017; the `$where` window will be widened once we scope the actual modeling
dataset. Columns we care most about in Crashes: `injuries_total`,
`most_severe_injury`, `weather_condition`, `lighting_condition`,
`roadway_surface_cond`, `road_defect`, `posted_speed_limit`, `crash_hour`,
`crash_day_of_week`, `first_crash_type`.

## Setup

```
pip install -r requirements.txt
```
