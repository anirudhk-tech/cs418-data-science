# Narrative Analysis, longer notes

Chicago Traffic Crash Analytics, Checkpoint 5

This is the extra detail behind the three findings in the README. Code for
all of it is in `notebooks/narrative.ipynb` / `scripts/narrative_analysis.py`,
same analysis either way.

## Finding 1 details: overnight vs midday

Windows picked: overnight = hours 22, 23, 0, 1, 2, 3. Midday = hours 10,
11, 12, 13. These aren't arbitrary, they came straight out of the EDA
injury-rate-by-hour plot, overnight is where the rate peaks, midday is
where it bottoms out.

Numbers: overnight n=28,925, injury rate 18.67% (Wilson 95% CI
18.22%-19.12%). Midday n=46,449, injury rate 13.82% (Wilson CI
13.51%-14.14%). Two-proportion z-test: z=17.81, p=6.34e-71.

Alternative explanations we considered:
- **Confound: fewer cars overnight, so crashes that do happen are more
  "serious" by nature** (speeding, DUI, etc) rather than overnight being
  inherently more dangerous *per crash opportunity*. We can't rule this
  out with this dataset, we don't have exposure data (miles driven, cars
  on the road) to normalize by, only crash counts.
- **Confound: lighting**. Overnight obviously overlaps a lot with
  darkness. We did check lighting condition separately and it shows the
  same pattern (darkness higher injury rate than daylight), so it's
  possible this isn't really a "time of day" effect at all, just a
  "visibility" effect wearing a time-of-day costume. We did not fully
  separate these two in a joint model for this checkpoint, that's a next
  step (planned for the final model).
- **Quirk check**: could this just be reporting bias, like overnight
  crashes without injury go unreported more often than overnight injury
  crashes? Possible, can't check with this data alone.

## Finding 2 details: weather confounded by road surface

Model setup: logistic regression, outcome is `injured` (injuries_total >
0). `is_bad_weather` is True for RAIN, SNOW, FOG/SMOKE/HAZE, SLEET/HAIL,
BLOWING SNOW, FREEZING RAIN/DRIZZLE, BLOWING SAND/SOIL/DIRT, False
otherwise (mostly CLEAR/CLOUDY). Baseline model: `injured ~ is_bad_weather
+ hour_bucket`. Full model: adds lighting condition, road surface
condition, road defect, and posted speed limit. n=222,447 after dropping
rows with missing values in any of those columns and after excluding
invalid speed limits (0 or >70mph).

Baseline: bad_weather odds ratio = 1.257, p=2.23e-40.
Full: bad_weather odds ratio = 1.049, p=0.120.

The check that explained it: crosstab of `is_bad_weather` against
`roadway_surface_cond`. When weather is bad, 83.1% of crashes are on a
wet/snow/ice surface. When weather is clear/other, only 3.6% are. That's
a huge overlap, these two columns are nearly redundant with each other.
Once the model knows the surface condition, the weather flag doesn't add
much more information, hence the odds ratio collapsing toward 1 in the
full model.

This isn't us saying "weather doesn't matter", it's that weather's effect
on injury seems to run *through* road surface, not as some separate thing.
If we only had weather and not surface condition, we would have (wrongly)
credited weather itself. With both in hand, surface condition is the more
direct variable and weather looks more like a proxy for it.

What we didn't try: an interaction term between weather and surface (e.g.
does rain on an already-wet surface do something extra), ran out of time
for this checkpoint, flagged as a next step.

## Finding 3 details: snow surprise

Rates: CLEAR n=171,691, rate 16.40% (CI 16.23%-16.58%). RAIN n=19,948,
rate 19.89% (CI 19.34%-20.45%). SNOW n=4,251, rate 14.40% (CI
13.37%-15.48%). Snow vs clear z-test: z=-3.49, p=4.84e-04.

Confound we checked and ruled out: average posted speed limit by weather
condition. CLEAR=28.56mph, RAIN=29.18mph, SNOW=28.81mph. Basically flat,
so it's not that snow crashes happen on inherently lower-speed-limit
streets.

Confounds we did NOT get to check (listed honestly so we don't overclaim):
- Actual driving speed at time of crash (we only have posted limit, not
  measured speed, drivers may slow down well below the posted limit in
  snow specifically more than they do in rain).
- Whether snow crashes cluster more on streets that get plowed/salted
  fast (city priority streets) vs rain which happens everywhere equally.
- Whether snow crashes are more likely to be low-speed fender-benders
  (sliding into a stopped car) vs rain crashes involving higher-speed
  loss of control.

We're treating this as a real, legitimate, still-open finding, not
explained away, just flagged as something we'd want more data to dig into
for the final report.

## General limitations across all three findings

- All of this is associational, we're using "raises odds of injury" /
  "injury rate is higher" language, not causal language, on purpose. None
  of these are from a randomized or natural experiment.
- Our dataset is reported crashes only (see `DATASHEET.md` Scope
  section), so all these rates are "injury rate among crashes that got
  reported", not among all crashes that actually happened.
- We used CPD's injury classification as reported in the data, not a
  medical record, so "injury" here means "officer or driver reported some
  injury," which could undercount less visible injuries (e.g. injuries
  that show up later) or overcount minor claimed injuries.
