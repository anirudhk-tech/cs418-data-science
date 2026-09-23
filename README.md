# Chicago Traffic Crash Analytics

CS 418 Group Project

## Team

- Anirudh Kuppili (anirudhk_tech)

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

1. **NOAA hourly weather data** (Midway or O'Hare station, via NOAA
   Climate Data Online). We'd join this to crash timestamps to cross-check
   the crash report's self-reported weather field against actual recorded
   conditions (precipitation, visibility, temperature) at the time of the
   crash.
2. **[Chicago Traffic Tracker - Historical Congestion Estimates by Segment](https://data.cityofchicago.org/Transportation/Chicago-Traffic-Tracker-Historical-Congestion-Esti/4g9f-3jbs)**
   (City of Chicago Data Portal). Speed/congestion estimates by road segment.
   We'd compare this against crash locations/times to see whether traffic
   volume or congestion level is a confounder for the road-characteristic
   controls in the model.

## Data Acquisition

See `notebooks/data_acquisition.ipynb`. Basic shape, column types, and
coverage for each dataset are reported there (filled in from actually running
the notebook, not estimated).

## Setup

```
pip install -r requirements.txt
```
