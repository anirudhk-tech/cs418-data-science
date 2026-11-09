"""Runs the stats behind the README's Main Findings section.
Simple, not fancy: proportion tests + one logistic regression.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
import statsmodels.formula.api as smf

plt.rcParams["figure.figsize"] = (7, 4.5)
FIGDIR = "figures"

crashes = pd.read_parquet("data/raw/crashes.parquet")

crashes["injured"] = (pd.to_numeric(crashes["injuries_total"], errors="coerce").fillna(0) > 0).astype(int)
crashes["crash_hour_num"] = pd.to_numeric(crashes["crash_hour"], errors="coerce")
crashes["speed_num"] = pd.to_numeric(crashes["posted_speed_limit"], errors="coerce")

print("=" * 60)
print("FINDING 1: overnight vs midday injury rate")
print("=" * 60)

overnight = crashes[crashes["crash_hour_num"].isin([22, 23, 0, 1, 2, 3])]
midday = crashes[crashes["crash_hour_num"].isin([10, 11, 12, 13])]

n1, n2 = overnight["injured"].sum(), midday["injured"].sum()
N1, N2 = len(overnight), len(midday)
rate1, rate2 = n1 / N1, n2 / N2

stat, pval = proportions_ztest([n1, n2], [N1, N2])
ci1 = proportion_confint(n1, N1, method="wilson")
ci2 = proportion_confint(n2, N2, method="wilson")

print(f"overnight (10pm-3am): n={N1}, injury rate={rate1:.4f}, 95% CI=({ci1[0]:.4f}, {ci1[1]:.4f})")
print(f"midday (10am-1pm): n={N2}, injury rate={rate2:.4f}, 95% CI=({ci2[0]:.4f}, {ci2[1]:.4f})")
print(f"z={stat:.2f}, p={pval:.2e}, gap={rate1-rate2:.4f}")

fig, ax = plt.subplots()
bars = ax.bar(["Midday\n(10am-1pm)", "Overnight\n(10pm-3am)"], [rate2, rate1],
              yerr=[[rate2 - ci2[0], rate1 - ci1[0]], [ci2[1] - rate2, ci1[1] - rate1]],
              capsize=8, color=["#4c72b0", "#c44e52"])
ax.set_ylabel("Share of crashes with injury")
ax.set_title("Overnight crashes are more likely to cause injury than midday ones")
plt.tight_layout()
plt.savefig(f"{FIGDIR}/finding-1-overnight-vs-midday.png", dpi=150)
plt.close()

print()
print("=" * 60)
print("FINDING 2: weather effect, baseline vs full logistic regression")
print("=" * 60)

model_df = crashes.copy()
model_df["hour_bucket"] = pd.cut(
    model_df["crash_hour_num"],
    bins=[-1, 5, 9, 15, 19, 23],
    labels=["overnight", "morning", "midday", "evening_rush", "night"],
)
model_df["is_bad_weather"] = model_df["weather_condition"].isin(
    ["RAIN", "SNOW", "FOG/SMOKE/HAZE", "SLEET/HAIL", "BLOWING SNOW",
     "FREEZING RAIN/DRIZZLE", "BLOWING SAND, SOIL, DIRT"]
)
model_df = model_df.dropna(subset=["hour_bucket", "speed_num", "lighting_condition",
                                     "roadway_surface_cond", "road_defect"])
model_df = model_df[(model_df["speed_num"] > 0) & (model_df["speed_num"] <= 70)]

baseline = smf.logit("injured ~ is_bad_weather + C(hour_bucket)", data=model_df).fit(disp=0)
full = smf.logit(
    "injured ~ is_bad_weather + C(hour_bucket) + C(lighting_condition) + "
    "C(roadway_surface_cond) + C(road_defect) + speed_num",
    data=model_df,
).fit(disp=0)

base_coef = baseline.params["is_bad_weather[T.True]"]
base_p = baseline.pvalues["is_bad_weather[T.True]"]
base_or = np.exp(base_coef)
full_coef = full.params["is_bad_weather[T.True]"]
full_p = full.pvalues["is_bad_weather[T.True]"]
full_or = np.exp(full_coef)

print(f"baseline model: bad_weather odds ratio = {base_or:.3f}, p = {base_p:.2e}")
print(f"full model: bad_weather odds ratio = {full_or:.3f}, p = {full_p:.2e}")
print(f"n = {len(model_df)}")

fig, ax = plt.subplots()
ax.bar(["Baseline\n(hour + weather only)", "Full\n(+ lighting, surface, defect, speed)"],
       [base_or, full_or], color=["#4c72b0", "#55a868"])
ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
ax.set_ylabel("Odds ratio for bad weather (vs. clear/other)")
ax.set_title("Bad weather still raises injury odds after controlling for road conditions")
plt.tight_layout()
plt.savefig(f"{FIGDIR}/finding-2-weather-odds-ratio.png", dpi=150)
plt.close()

print()
print("=" * 60)
print("FINDING 3: snow surprise, snow vs rain vs clear, with speed limit check")
print("=" * 60)

for cond in ["CLEAR", "RAIN", "SNOW"]:
    sub = crashes[crashes["weather_condition"] == cond]
    n, N = sub["injured"].sum(), len(sub)
    ci = proportion_confint(n, N, method="wilson")
    print(f"{cond}: n={N}, injury rate={n/N:.4f}, 95% CI=({ci[0]:.4f}, {ci[1]:.4f})")

print()
print("speed limit by weather condition (checking for a confound):")
print(crashes[crashes["weather_condition"].isin(["CLEAR", "RAIN", "SNOW"])]
      .groupby("weather_condition")["speed_num"].mean().round(2))

snow = crashes[crashes["weather_condition"] == "SNOW"]
clear = crashes[crashes["weather_condition"] == "CLEAR"]
stat2, pval2 = proportions_ztest([snow["injured"].sum(), clear["injured"].sum()], [len(snow), len(clear)])
print(f"snow vs clear z-test: z={stat2:.2f}, p={pval2:.2e}")

rates = crashes[crashes["weather_condition"].isin(["CLEAR", "RAIN", "SNOW"])].groupby("weather_condition")["injured"].mean()
rates = rates.reindex(["CLEAR", "RAIN", "SNOW"])
fig, ax = plt.subplots()
ax.bar(rates.index, rates.values, color=["#4c72b0", "#c44e52", "#8172b2"])
ax.set_ylabel("Share of crashes with injury")
ax.set_title("Snow crashes are less likely to cause injury than rain or clear-weather ones")
plt.tight_layout()
plt.savefig(f"{FIGDIR}/finding-3-snow-surprise.png", dpi=150)
plt.close()

print()
print("Done, figures saved to figures/")
