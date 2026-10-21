# Datasheet

Chicago Traffic Crash Analytics, Checkpoint 4

Covers the two primary datasets: Traffic Crashes - Crashes and Traffic
Crashes - People. Both come from the City of Chicago Data Portal (Socrata),
pulled with `scripts/fetch_full_data.py`.

## Summary cards

**Traffic Crashes - Crashes**
- Rows: 222,811 (our 2023-2024 pull). Full dataset since Sept 2017 is 950K+.
- Columns: 49
- One row = one crash event
- Source: data.cityofchicago.org, dataset id `85ca-t3if`
- License: public domain / Chicago Data Portal terms of use
- Known issue: injury outcome is self/officer-reported, not verified against hospital records

**Traffic Crashes - People**
- Rows: 491,892 (our 2023-2024 pull, matches the crashes window)
- Columns: 29
- One row = one person involved in a crash
- Source: data.cityofchicago.org, dataset id `u6pd-qa9d`
- License: public domain / Chicago Data Portal terms of use
- Known issue: ~29% missing age, several columns only apply to certain person types so are mostly null

## 1. Motivation

Both datasets are published by the City of Chicago Data Portal. They come
from the Chicago Police Department's E-Crash electronic crash reporting
system, following the Illinois Department of Transportation's SR1050 crash
report form. The city publishes them as part of its open data program so
researchers, journalists, and the public can study traffic safety. Not made
for research originally, it's an administrative record of police crash
reports, repurposed for open data.

## 2. Composition

- **Crashes**: one row per crash on a Chicago street under CPD jurisdiction.
  222,811 rows in our 2023-2024 pull. Not a sample, it's every crash report
  filed in that window (as of when we pulled it). Missing data: 509-512
  rows missing injury fields, 2,222 missing lat/long, and a bunch of rare
  flag columns (work zone, dooring, etc.) are almost entirely null because
  they just don't apply to most crashes.
- **People**: one row per person involved in a crash (driver, passenger,
  pedestrian, cyclist). 491,892 rows for the same window, about 2.2 people
  per crash. Also every record filed, not a sample. Missing data: age ~29%,
  sex ~2%, and a bunch of EMS/pedestrian-specific columns that only apply
  to certain person types.
- Neither dataset includes crashes that went unreported, happened on
  private property without police response, or were outside CPD
  jurisdiction (e.g. interstates patrolled by Illinois State Police).

## 3. Collection process

Data comes from police officers (or sometimes drivers themselves, for
minor crashes) filling out the SR1050 crash report form, entered into
CPD's E-Crash system. It's not a survey or sensor feed, it's an
administrative record created as part of normal police work. People
involved in a crash didn't "consent" to being in this dataset in a
research sense, it's a legal reporting requirement. Timeframe: the full
public dataset goes back to September 2017, updated daily; we pulled
2023-01-01 through 2024-12-31.

## 4. Preprocessing

The city already does some cleaning before publishing, personally
identifiable info is stripped (no names), and the data is structured to
follow the SR1050 form's fields. We don't believe raw/pre-cleaned data is
available publicly, what's on the data portal is what we have. Our own
preprocessing on top of that is listed in the Recipe section below (type
casting, invalid value handling, etc).

## 5. Uses

Chicago's Data Portal docs mention this feeds into city traffic safety
planning (Vision Zero Chicago) and is also used by journalists, academics,
and civic tech projects for crash analysis and street safety advocacy. It
should not be used to identify or penalize specific individuals, data is
meant to be aggregate/statistical, not a surveillance tool. It also
shouldn't be read as a complete record of every crash in Chicago, see
Scope section below.

## 6. Distribution

Published on the City of Chicago Data Portal (Socrata platform), free and
public, no login required. Available as CSV download or via the Socrata
API (what we used). Terms of use: City of Chicago Data Portal terms, which
allow free reuse, see data.cityofchicago.org terms of use page. No
specific academic license like CC-BY is attached, it's a government open
data release.

## 7. Maintenance

Maintained by the City of Chicago (Chicago Police Department data feeding
into the Department of Innovation and Technology's data portal). Updated
daily as new crash reports are finalized or amended. You can check the
portal page for last-updated timestamps. We have no info on a
deprecation timeline, these are actively maintained general datasets.

## Scope

Research question: What factors predict whether a Chicago traffic crash
results in injury, and do time-of-day and weather effects persist after
controlling for road and crash characteristics?

- **Target population**: every traffic crash that occurs on a Chicago
  street.
- **Access frame**: crashes that get reported to CPD and entered into
  E-Crash, this excludes crashes that go unreported (very minor fender
  benders, private property crashes with no police called), and excludes
  crashes on roads not under CPD jurisdiction.
- **Sample**: our actual working dataset, all E-Crash records from
  2023-01-01 to 2024-12-31 as published on the data portal as of our pull
  date (October 2026).

What this means for our claims: we can say things about "crashes that got
reported to CPD in 2023-2024", not "all crashes that happened in Chicago."
Minor crashes without injury might be underreported relative to severe
ones (people are more likely to call police when someone's hurt), which
could bias our injury rate estimates upward.

## Codebook

Columns we actually use, from both tables plus anything we derived
ourselves.

| Column | Dataset | Type | Units | Meaning | Range / values | Missing code | Source |
|---|---|---|---|---|---|---|---|
| crash_record_id | crashes, people | string | - | unique crash id, join key | hash string | none (0 missing) | raw |
| crash_date | crashes, people | string, cast to datetime | timestamp | when the crash happened | 2023-01-01 to 2024-12-31 | none | raw |
| posted_speed_limit | crashes | string, cast to int | mph | posted speed limit at crash site | 0-70 (0 and >70 are bad data) | none, but 0/>70 treated as invalid | raw |
| weather_condition | crashes | string (categorical) | - | weather at crash time | CLEAR, RAIN, SNOW, UNKNOWN, etc (12 levels) | "UNKNOWN" used instead of null | raw |
| lighting_condition | crashes | string (categorical) | - | lighting at crash time | DAYLIGHT, DARKNESS, DAWN, etc (6 levels) | "UNKNOWN" used instead of null | raw |
| roadway_surface_cond | crashes | string (categorical) | - | road surface condition | DRY, WET, SNOW, ICE, UNKNOWN, etc (7 levels) | "UNKNOWN" used instead of null | raw |
| road_defect | crashes | string (categorical) | - | road defect present | NO DEFECTS, RUT/HOLES, UNKNOWN, etc (7 levels) | "UNKNOWN" used instead of null | raw |
| first_crash_type | crashes | string (categorical) | - | type of first crash event | REAR END, ANGLE, PARKED VEHICLE, etc (18 levels) | none | raw |
| crash_hour | crashes | string, cast to int | hour (0-23) | hour of day crash occurred | 0-23 | none | raw |
| crash_day_of_week | crashes | string, cast to int | day (1-7) | day of week crash occurred | 1-7 | none | raw |
| most_severe_injury | crashes | string (categorical) | - | most severe injury in the crash | NO INDICATION OF INJURY, FATAL, etc (5 levels) | 512 rows missing | raw |
| injuries_total | crashes | string, cast to float | count of people | total people injured in the crash | 0-21 | 509 rows missing | raw |
| injured | crashes | derived, boolean | - | our target variable | True/False | n/a (derived from injuries_total) | computed in eda.ipynb: `injuries_total > 0` |
| age | people | string, cast to float | years | age of person | 0-100 valid, some negative/>100 junk | ~29% missing | raw |
| sex | people | string (categorical) | - | sex of person | M, F, X, missing | ~2% missing | raw |
| injury_classification | people | string (categorical) | - | injury severity for this person | NO INDICATION OF INJURY, FATAL, etc (5 levels) | 101 rows missing | raw |
| safety_equipment | people | string (categorical) | - | safety equipment used | SAFETY BELT USED, USAGE UNKNOWN, etc (18 levels) | ~0.3% missing | raw |
| speed_num | congestion | string, cast to float | mph | average arterial segment speed | 0-50ish | none observed | raw (secondary dataset) |
| hour_num | congestion | string, cast to int | hour (0-23) | hour of the speed reading | 0-23 | none | raw (secondary dataset) |

## Recipe

Steps to go from raw API data to the dataframes used in the EDA notebook.
All code referenced below actually exists and runs, see the paths.

1. **Pull crashes**: `scripts/fetch_full_data.py`, `fetch_all()` against
   `https://data.cityofchicago.org/resource/85ca-t3if.json`, paginated with
   `$limit=50000` / `$offset`, filtered with
   `$where=crash_date >= '2023-01-01T00:00:00' AND crash_date < '2025-01-01T00:00:00'`,
   ordered by `crash_record_id`. Saved to `data/raw/crashes.parquet`.
   Result: 222,811 rows.
2. **Pull people**: same script, same window, against
   `https://data.cityofchicago.org/resource/u6pd-qa9d.json`, ordered by
   `person_id`. Saved to `data/raw/people.parquet`. Result: 491,892 rows.
3. **Pull congestion** (secondary dataset): same script, single day
   2024-06-11, against
   `https://data.cityofchicago.org/resource/4g9f-3jbs.json`. Saved to
   `data/raw/congestion.parquet`. Result: 50,000 rows.
4. **Load and type-fix**: `notebooks/eda.ipynb`, cell 2 loads the parquet
   files with `pd.read_parquet`. Numeric columns (`posted_speed_limit`,
   `injuries_total`, `crash_hour`, `age`, etc) are cast with
   `pd.to_numeric(..., errors="coerce")` as they're used, since the API
   returns everything as strings.
5. **Drop/flag invalid values**: 364 crash rows with
   `posted_speed_limit` of 0 or >70 are excluded from the speed-limit plot
   (not dropped from the dataframe itself). 24 people rows with invalid
   age (negative or >100) are flagged for exclusion in any age analysis.
6. **Derive the target variable**: `crashes["injured"] = crashes["injuries_total"].astype(float).fillna(0) > 0`,
   done in `notebooks/eda.ipynb`, Relationship 1 cell.
7. **Join crashes and people**: key is `crash_record_id`. We checked this
   join directly (see below), it's a one-to-many join, crash to its
   people. We did not actually merge the two tables into one dataframe for
   the EDA notebook, each is analyzed separately. For modeling, a left
   join from crashes to people (or an aggregation of people up to the
   crash level) would be the next step.
   - Crashes rows: 222,811. People rows: 491,892.
   - Crash ids with at least one matching person record: 222,302
   - Crash ids with no matching person record: 509 (these are exactly the
     rows missing `injuries_total`/`most_severe_injury`, so it's the same
     509 incomplete reports, not a separate issue)
   - Person rows with no matching crash record: 0 (every person record
     points to a real crash in our pull)
8. **Compare against congestion (secondary dataset)**: no row-level join,
   we aggregated both datasets to "average/rate by hour of day" and
   plotted them side by side (`notebooks/eda.ipynb`, Relationship 4). Not
   a key-based join since the two datasets cover different days and
   locations don't line up 1:1 with crash sites.

## FAIR

| | Crashes | People | Congestion (secondary) |
|---|---|---|---|
| Findable (persistent link) | [data.cityofchicago.org/.../85ca-t3if](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if) | [data.cityofchicago.org/.../u6pd-qa9d](https://data.cityofchicago.org/Transportation/Traffic-Crashes-People/u6pd-qa9d) | [data.cityofchicago.org/.../4g9f-3jbs](https://data.cityofchicago.org/Transportation/Chicago-Traffic-Tracker-Historical-Congestion-Esti/4g9f-3jbs) |
| Accessible | public Socrata API, no login/key needed | same | same |
| Version / access date | pulled October 2026, data covers 2023-01-01 to 2024-12-31 | same | pulled October 2026, data for 2024-06-11 |
| Format | JSON via API, saved locally as parquet | same | same |
| License / terms | Chicago Data Portal terms of use (free public reuse) | same | same |
| Can we redistribute our processed version? | yes, our processed/filtered data inherits the open terms of the source; we keep raw files out of the repo (`data/raw/` gitignored) and ship the fetch script instead so anyone can reproduce it | same | same |

## People and CARE considerations

These datasets describe people indirectly: drivers, passengers,
pedestrians, and cyclists involved in crashes, plus implicitly the police
officers who filed the reports. No names or direct identifiers are
included, but age, sex, and general location are, so there's some
re-identification risk at a very local/rare-crash level (a single
late-night crash on a quiet street could plausibly be linked to a known
local incident).

Representation concerns:
- Injury/crash reporting likely isn't uniform across neighborhoods,
  areas with less trust in police may underreport minor crashes, which
  would bias our "crash counts" (though probably less so for injury
  crashes specifically, since those are more likely to involve EMS
  regardless of police trust).
- Pedestrians and cyclists are a small share of all "people" rows, so our
  injury model will mostly reflect driver/passenger outcomes, not
  necessarily generalize well to pedestrian/cyclist safety specifically.
- Demographic fields (age, sex) are incomplete (~29%, ~2% missing
  respectively), and missingness might not be random. e.g. hit-and-run
  cases probably have less complete person data.

CARE lens: this isn't Indigenous data, but the same framing applies to
Chicago communities more broadly. If this analysis (or a model built on
it) were ever used operationally (e.g. to direct traffic enforcement or
infrastructure investment), it could disproportionately affect
neighborhoods that are already over-policed, since crash reports are
downstream of policing presence, not just actual crash rates. We're using
this data for a class project, not deployment, but we think it's
important to flag this as a real limitation if this kind of analysis were
ever taken further.
