"""
Step 3: site-selection scoring for a NEW compound, updated with:
- official Nawy zone supply/demand counts (competition, demand proxy)
- accessibility to Cairo
- infrastructure tailwind from the Ras El Hekma megaproject
- a NEW pricing-power dimension pulled from step 2's regression zone
  coefficients (which zone commands the highest price/sqm once unit
  type and size are controlled for - a proxy for realizable margin)
Run: python src/03_site_selection.py  (after 01_data_prep.py and 02_pricing_analysis.py)
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
PROCESSED = os.path.join(BASE, "data", "processed")
FIGURES = os.path.join(BASE, "figures")

plt.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "white",
                      "font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

compounds = pd.read_csv(os.path.join(PROCESSED, "compounds_master_clean.csv"))


def assign_zone(km, zones):
    for _, z in zones.iterrows():
        if z["km_range_start"] <= km <= z["km_range_end"]:
            return z["zone"]
    if km < 100:
        return "Alexandria Corridor (<km100)"
    return "Far West (>km250)"


zones = pd.read_csv(os.path.join(RAW, "zone_supply_demand.csv"))
compounds["zone"] = compounds["km_marker"].apply(lambda k: assign_zone(k, zones))
compounds.to_csv(os.path.join(PROCESSED, "compounds_with_zone.csv"), index=False)

# cross-check: how many compounds does our own sample cover per zone,
# vs. the officially reported Nawy compound counts (sample coverage ratio)
sample_counts = compounds["zone"].value_counts()
zones["sample_compounds_found"] = zones["zone"].map(sample_counts).fillna(0).astype(int)
zones["sample_coverage_pct"] = (zones["sample_compounds_found"] / zones["compounds_count"] * 100).round(1)
zones.to_csv(os.path.join(PROCESSED, "zone_sample_coverage.csv"), index=False)

with open(os.path.join(PROCESSED, "findings_pricing.json")) as f:
    pricing_findings = json.load(f)
zone_coefs = pricing_findings["regression"]["coefficients"]

z = zones.copy()
z["demand_per_compound"] = z["properties_available"] / z["compounds_count"]
z["competition_score"] = 1 - (z["compounds_count"] - z["compounds_count"].min()) / (
    z["compounds_count"].max() - z["compounds_count"].min())
z["demand_score"] = (z["demand_per_compound"] - z["demand_per_compound"].min()) / (
    z["demand_per_compound"].max() - z["demand_per_compound"].min())
z["accessibility_score"] = 1 - (z["dist_from_cairo_km"] - z["dist_from_cairo_km"].min()) / (
    z["dist_from_cairo_km"].max() - z["dist_from_cairo_km"].min())
tailwind_zones = {"Ras El Hekma": 1.0, "Al Dabaa": 0.6, "Sidi Heneish": 0.4}
z["infra_tailwind_score"] = z["zone"].map(tailwind_zones).fillna(0.0)

# pricing-power score: regression zone coefficient (log scale, Al Alamein
# is the omitted baseline = 0), rescaled 0-1. Higher = zone supports a
# higher price/sqm after controlling for what's actually being built there.
zone_key_map = {"Al Alamein": 0.0}
for zname in z["zone"]:
    key = f"zone_{zname}"
    if key in zone_coefs:
        zone_key_map[zname] = zone_coefs[key]
z["pricing_power_raw"] = z["zone"].map(zone_key_map).fillna(0.0)
pp_min, pp_max = z["pricing_power_raw"].min(), z["pricing_power_raw"].max()
z["pricing_power_score"] = (z["pricing_power_raw"] - pp_min) / (pp_max - pp_min) if pp_max > pp_min else 0.5

weights = {
    "competition_score": 0.25,
    "demand_score": 0.20,
    "accessibility_score": 0.15,
    "infra_tailwind_score": 0.20,
    "pricing_power_score": 0.20,
}
z["site_score"] = sum(z[k] * w for k, w in weights.items())
z = z.sort_values("site_score", ascending=False).reset_index(drop=True)
z.to_csv(os.path.join(PROCESSED, "zone_site_selection_scores.csv"), index=False)

findings = {
    "weights": weights,
    "site_selection_ranking": z[["zone", "site_score", "competition_score", "demand_score",
                                   "accessibility_score", "infra_tailwind_score",
                                   "pricing_power_score", "sample_coverage_pct"]].round(3).to_dict(orient="records"),
}

fig, ax = plt.subplots(figsize=(9.5, 5.5))
bars = ax.barh(z["zone"], z["site_score"], color="#2ca02c")
ax.invert_yaxis()
ax.set_xlabel("Composite site-selection score (0-1)")
ax.set_title("Best zones for a new North Coast compound\n(now including a regression-based pricing-power dimension)")
for b, val in zip(bars, z["site_score"]):
    ax.text(val + 0.01, b.get_y() + b.get_height() / 2, f"{val:.2f}", va="center", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(FIGURES, "site_selection_ranking.png"), dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 6))
score_cols = ["competition_score", "demand_score", "accessibility_score", "infra_tailwind_score", "pricing_power_score"]
labels = ["Competition\n(whitespace)", "Demand\nproxy", "Accessibility", "Infra\ntailwind", "Pricing\npower"]
x = np.arange(len(score_cols))
width = 0.14
for i, (_, row) in enumerate(z.iterrows()):
    ax.bar(x + i * width, row[score_cols].values.astype(float), width, label=row["zone"])
ax.set_xticks(x + width * (len(z) - 1) / 2)
ax.set_xticklabels(labels)
ax.set_ylabel("Score (0-1)")
ax.set_title("Site-selection score breakdown by zone and criterion")
ax.legend(frameon=False, fontsize=8, ncol=2)
fig.tight_layout()
fig.savefig(os.path.join(FIGURES, "site_selection_breakdown.png"), dpi=150)
plt.close(fig)

with open(os.path.join(PROCESSED, "findings_site_selection.json"), "w") as f:
    json.dump(findings, f, indent=2, default=str)

print("Step 3 complete. Top zone:", z.iloc[0]["zone"], "| score:", round(z.iloc[0]["site_score"], 3))
print("Runner-up:", z.iloc[1]["zone"], "| score:", round(z.iloc[1]["site_score"], 3))
