# Exploratory Data Analysis

Chicago Traffic Crash Analytics - Checkpoint 3

Notebook with all the actual code/plots is here: [`notebooks/eda.ipynb`](notebooks/eda.ipynb).
This doc is basically the TL;DR of that notebook, point by point.

We're using the FULL 2023-2024 pull now, not the 50k sample from last
checkpoint (that was cutting off most of the data lol). See
`scripts/fetch_full_data.py` if you want to re-run it.

## 1. Dataset Profiles

### Traffic Crashes - Crashes

222,811 rows, 49 columns. One row = one crash.

Annoying thing: literally every column comes back as a string from the API,
even stuff that's obviously a number (`posted_speed_limit`,
`injuries_total`, `crash_hour`). Had to `pd.to_numeric()` everything before
doing anything with it. Also a bunch of columns (`lane_cnt`,
`workers_present_i`, `work_zone_type`, `dooring_i`, `work_zone_i`) are
basically all null, like 99%+, so those are pretty useless. The main fields
we care about (weather, lighting, road surface) show 0 nulls which sounds
great but it's actually because Chicago just writes "UNKNOWN" instead of
leaving it blank. more on that in anomalies. `most_severe_injury` and
`injuries_total` are missing for ~510 rows, not a big deal, just drop em.

### Traffic Crashes - People

491,892 rows, 29 columns. One row per person in a crash, so ~2.2 people per
crash on average which checks out.

`age` is missing ~29% of the time, `sex` ~2%. A bunch of the EMS/pedestrian
columns are almost entirely empty because they only apply to specific
people (like `pedpedal_*` is only for pedestrians/cyclists, so obviously
most rows don't have it). Most people are fine, "NO INDICATION OF INJURY"
is like 90% of rows. Same no-injury-heavy pattern as the crashes table.

## 2. Anomalies

| Anomaly | Rows affected | What we did |
|---|---|---|
| Everything's a string, even numbers | all rows | `pd.to_numeric(errors="coerce")` |
| Speed limit = 0 or > 70mph (obviously wrong) | 364 crash rows | dropped from the speed limit plot, will exclude/cap later |
| "UNKNOWN" used instead of actual null for weather/lighting/surface/road defect | 6.7% to 25.7% of rows depending on the column | kept it as its own category instead of dropping, might actually mean something (desk report vs on-scene report) |
| Ages that are negative or over 100 | 24 people rows | drop for anything age-related |
| Age missing | 143,700 rows (~29%) | left as null, not a big deal for the crash-level model |
| Duplicate crash IDs | 0 | checked, we're good, one row per crash |

## 3. Distributions

- **Injury severity**: super skewed toward no injury, 84% of crashes have
  zero indication of injury. So injury is the minority class, matches the
  15.8% overall injury rate we calculated later.
- **Crash hour**: not flat at all, lowest overnight (1-5am) then builds up
  to a peak around 3-5pm, makes sense with rush hour.
- **Weather**: dominated by "CLEAR" at 77%. Everything else is a long tail
  under 10% each, so raw counts for rare weather types aren't that
  meaningful on their own, gotta look at rates not counts.
- **Posted speed limit**: mostly just 30mph (74% of rows), some spikes at
  25/35/45. Median is 30, pretty tight IQR. Excluded the 364 bad values.

## 4. Relationships

### 1. Injury rate by hour of day

Plot is in the notebook, section 4.

**So what:** Injury rate dips to ~13% around midday and jumps to ~19-20%
overnight/late night, vs a 15.8% average. Kinda expected since less traffic
at night = higher speeds, but honestly didn't expect the swing to be this
big.

**What next:** Need to check if this is actually just a lighting thing in
disguise (darkness vs daylight) instead of a separate hour-of-day effect,
that's basically relationship 3 below. Also for modeling we should probably
bucket hour into day/evening/overnight instead of treating it as a straight
number since the shape isn't linear at all.

### 2. Injury rate by weather condition

**So what:** The weird/rare weather types have the highest injury rates,
blowing sand/dirt (25%), fog/smoke/haze (21.6%), blowing snow/sleet/hail
(~21%), rain (19.9%), all above the 15.8% avg and above clear weather
(16.4%). But plain "SNOW" is actually below average at 14.4% which we did
not expect, maybe people just drive way slower when it's visibly snowing,
or the roads get salted/plowed more aggressively.

**What next:** Want to dig into that snow thing more, maybe cross it with
road surface condition and speed limit. Also should double check sample
size for stuff like "blowing sand" since that's probably like 10 crashes
total and the rate could just be noise.

### 3. Injury rate by lighting × weather

**So what:** Lighting shows basically the same pattern as hour of day,
"darkness, lighted road" and "dawn" have the highest rates (19.8%, 19.3%),
daylight is lowest (15.4%). Kinda surprising that LIT darkness has a higher
rate than unlit darkness, maybe lit roads are just busier/faster streets,
not actually about the lighting itself. The heatmap also shows dark+bad
weather combos (like rain at night) stacking up to the worst rates, so
these things aren't totally independent of each other.

**What next:** This is basically the whole point of our research question
. time of day, lighting, and weather all seem tangled up together, so we
need a model that controls for all of them at once (plus road
surface/defect) to see what's actually doing the work. Plan is: simple
model with just hour+weather first, then a bigger model adding
lighting/surface/speed limit/crash type, and compare.

### 4. Arterial speed vs injury rate by hour (secondary dataset)

This one uses the Traffic Tracker Congestion data from checkpoint 2.

**So what:** Heads up, this congestion pull is only for ONE day and only
has data for hours 13-21 (not sure why it cuts off, the live feed might
just not have data outside that), so take this with a grain of salt. But
within that window, average speed goes up through the afternoon (16.6mph
at 1pm up to 18.8mph at 4pm) then drops in the evening, and injury rate
moves the opposite way over roughly the same hours. So faster/less
congested roads line up with worse crash outcomes when a crash does
happen. Makes sense directionally but it's just a correlation, not proof
of anything, and the two datasets aren't even from the same days.

**What next:** Pull a full day (or several) of congestion data to see if
this holds for the whole 24 hours, not just the afternoon/evening slice we
got. If it holds up, congestion/speed could be worth adding as another
control variable in the model.

## 5. Research questions, revisited

Original question: What factors predict whether a Chicago traffic crash
results in injury, and do time-of-day and weather effects persist after
controlling for road and crash characteristics?

Good news, this still seems totally doable with our data. A few things we
learned that'll change how we approach it:

- Injury is pretty rare overall (~16%) so we need to deal with class
  imbalance in the model, not just report plain accuracy.
- Time of day, lighting, and weather are all correlated with each other
  (same overnight pattern shows up in both hour and lighting plots),
  which is literally the confounding thing our question was asking about,
  so good, that confirms the two-model comparison approach is the right
  call.
- "UNKNOWN" isn't really missing data, it's its own category and shows up
  a lot (6-26% depending on the column), need to decide how to handle it
  intentionally instead of just dropping it.
- Traffic congestion/speed might matter too, not just road surface/defect
  like we originally said, relationship 4 hints at this but we need more
  data to be sure.

**Updated question:** What factors predict whether a Chicago traffic crash
results in injury, and do time-of-day, lighting, and weather effects
persist after controlling for road characteristics (surface, defect, speed
limit, crash type) and, if we can get better data, traffic
volume/congestion?
