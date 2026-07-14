"""
Step 2: pricing analysis on the enriched unit-level dataset.
- price/sqm by unit type (EGP and currency-adjusted USD)
- multiple regression (numpy, log price/sqm ~ log area + unit type + zone)
  to isolate the size effect from tier/location effects
- same-compound appreciation check (Marassi, La Vista Bay East)
- international benchmark comparison
Run: python src/02_pricing_analysis.py  (after 01_data_prep.py)
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
os.makedirs(FIGURES, exist_ok=True)

plt.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "white",
                      "font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

findings = {}
units = pd.read_csv(os.path.join(PROCESSED, "unit_price_samples_enriched.csv"))

by_type_egp = units.groupby("unit_type")["price_per_sqm_egp"].agg(["count", "mean", "median", "min", "max"]).round(0)
by_type_usd = units.groupby("unit_type")["price_per_sqm_usd"].agg(["count", "mean", "median", "min", "max"]).round(0)
by_type_egp.to_csv(os.path.join(PROCESSED, "price_per_sqm_by_unit_type_egp.csv"))
by_type_usd.to_csv(os.path.join(PROCESSED, "price_per_sqm_by_unit_type_usd.csv"))
findings["price_per_sqm_egp_by_type"] = by_type_egp.to_dict(orient="index")
findings["price_per_sqm_usd_by_type"] = by_type_usd.to_dict(orient="index")

reg_df = units.copy()
reg_df["log_area"] = np.log(reg_df["area_sqm"])
reg_df["log_ppsqm"] = np.log(reg_df["price_per_sqm_usd"])

type_dummies = pd.get_dummies(reg_df["unit_type"], prefix="type", drop_first=True)
zone_dummies = pd.get_dummies(reg_df["zone"], prefix="zone", drop_first=True)
X = pd.concat([reg_df[["log_area"]], type_dummies, zone_dummies], axis=1)
feature_names = ["intercept"] + X.columns.tolist()
Xmat = np.hstack([np.ones((len(X), 1)), X.values.astype(float)])
yvec = reg_df["log_ppsqm"].values.astype(float)

beta, residuals, rank, sv = np.linalg.lstsq(Xmat, yvec, rcond=None)
y_hat = Xmat @ beta
ss_res = float(np.sum((yvec - y_hat) ** 2))
ss_tot = float(np.sum((yvec - yvec.mean()) ** 2))
r2 = 1 - ss_res / ss_tot
n, k = Xmat.shape
adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k)

coef_table = pd.Series(beta, index=feature_names).round(4)
coef_table.to_csv(os.path.join(PROCESSED, "regression_coefficients.csv"))

findings["regression"] = {
    "formula": "log(price_per_sqm_usd) ~ log(area_sqm) + unit_type + zone",
    "n_obs": int(n), "r_squared": round(float(r2), 3), "adj_r_squared": round(float(adj_r2), 3),
    "log_area_coefficient": round(float(coef_table["log_area"]), 4),
    "interpretation": "A 1%% increase in unit area is associated with a %.2f%% change in price/sqm, holding unit type and zone constant." % (coef_table["log_area"] * 100),
    "coefficients": coef_table.to_dict(),
}

plot_coefs = coef_table.drop("intercept").sort_values()
fig, ax = plt.subplots(figsize=(9, 7))
colors = ["#2ca02c" if v < 0 else "#d62728" for v in plot_coefs.values]
ax.barh(plot_coefs.index, plot_coefs.values, color=colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Regression coefficient (log price/sqm USD scale)")
ax.set_title("What actually moves price/sqm - controlling for size, type & zone (R2=%.2f, n=%d)" % (r2, n))
fig.tight_layout()
fig.savefig(os.path.join(FIGURES, "regression_coefficients.png"), dpi=150)
plt.close(fig)

chalets = units[units["unit_type"] == "chalet"].copy()
zone_median = chalets.groupby("zone")["price_per_sqm_usd"].transform("median")
chalets["relative_price_per_sqm"] = chalets["price_per_sqm_usd"] / zone_median
chalets = chalets.sort_values("area_sqm")
chalets.to_csv(os.path.join(PROCESSED, "chalets_relative_pricing.csv"), index=False)

coeffs = np.polyfit(chalets["area_sqm"], chalets["relative_price_per_sqm"], 1)
fitted_at_max = np.polyval(coeffs, chalets["area_sqm"].max())
threshold = fitted_at_max * 1.10
areas_sorted = np.linspace(chalets["area_sqm"].min(), chalets["area_sqm"].max(), 300)
fitted_vals = np.polyval(coeffs, areas_sorted)
sweet_spot_area = float(areas_sorted[np.argmax(fitted_vals <= threshold)])
findings["chalet_sweet_spot_area_sqm_zone_adjusted"] = round(sweet_spot_area, 1)
findings["chalet_relative_price_slope"] = round(float(coeffs[0]), 5)

fig, ax = plt.subplots(figsize=(9, 6))
ax.scatter(chalets["area_sqm"], chalets["relative_price_per_sqm"], s=70, alpha=0.8,
           color="#1f77b4", edgecolor="white", linewidth=0.6)
ax.plot(areas_sorted, fitted_vals, color="#1f77b4", linestyle="--", linewidth=1.5)
ax.axhline(1.0, color="gray", linewidth=0.8, linestyle=":")
ax.axvline(sweet_spot_area, color="#d62728", linewidth=1, linestyle="--",
           label="Sweet spot ~%.0f sqm" % sweet_spot_area)
ax.set_xlabel("Chalet area (sqm)")
ax.set_ylabel("Price/sqm relative to own-zone chalet median")
ax.set_title("Zone-adjusted sweet spot: size effect after controlling for location tier")
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(FIGURES, "sweet_spot_zone_adjusted.png"), dpi=150)
plt.close(fig)

appreciation_rows = []
for compound_pair, label in [
    (["Marassi Santorini", "Marassi (2BR chalet)"], "Marassi chalet, ~2023 to 2026"),
    (["La Vista Bay East"], "La Vista Bay East chalet, 2025 to 2026"),
]:
    sub = units[units["compound"].isin(compound_pair)].sort_values("price_recency")
    if len(sub) >= 2:
        first, last = sub.iloc[0], sub.iloc[-1]
        nominal_chg = (last["price_per_sqm_egp"] / first["price_per_sqm_egp"] - 1) * 100
        usd_chg = (last["price_per_sqm_usd"] / first["price_per_sqm_usd"] - 1) * 100
        appreciation_rows.append({
            "compound": label, "from_year": int(first["price_recency"]), "to_year": int(last["price_recency"]),
            "from_egp_sqm": round(float(first["price_per_sqm_egp"]), 0),
            "to_egp_sqm": round(float(last["price_per_sqm_egp"]), 0),
            "nominal_change_pct": round(float(nominal_chg), 1),
            "usd_change_pct": round(float(usd_chg), 1),
        })
appreciation_df = pd.DataFrame(appreciation_rows)
appreciation_df.to_csv(os.path.join(PROCESSED, "appreciation_check.csv"), index=False)
findings["appreciation_check"] = appreciation_rows

fx = pd.read_csv(os.path.join(RAW, "fx_rates.csv")).set_index("year")["egp_per_usd"]
reh_2023 = 43667 / fx[2023]
reh_2025 = 217768 / fx[2025]
findings["jll_ras_el_hekma_usd_check"] = {
    "2023_usd_per_sqm": round(float(reh_2023), 0),
    "q3_2025_usd_per_sqm": round(float(reh_2025), 0),
    "usd_change_pct": round(float((reh_2025 / reh_2023 - 1) * 100), 1),
    "note": "JLL-reported EGP/sqm figures converted at price_recency-matched FX; even after the EGP's ~55% devaluation over the period, dollar-denominated prices roughly tripled.",
}

bench = pd.read_csv(os.path.join(RAW, "international_benchmarks.csv"))
bench["mid_usd_sqm"] = (bench["price_per_sqm_usd_low"] + bench["price_per_sqm_usd_high"]) / 2
bench.to_csv(os.path.join(PROCESSED, "international_benchmarks_processed.csv"), index=False)

fig, ax = plt.subplots(figsize=(10, 6.5))
bench_sorted = bench.sort_values("mid_usd_sqm")
ax.barh(bench_sorted["market"] + " - " + bench_sorted["segment"],
        bench_sorted["mid_usd_sqm"], color="#9467bd")
for i, (lo, hi) in enumerate(zip(bench_sorted["price_per_sqm_usd_low"], bench_sorted["price_per_sqm_usd_high"])):
    ax.plot([lo, hi], [i, i], color="black", linewidth=1)
ax.set_xlabel("Price per sqm (USD, currency-adjusted)")
ax.set_title("Sahel vs. global coastal resort benchmarks (USD/sqm)")
fig.tight_layout()
fig.savefig(os.path.join(FIGURES, "international_benchmarks.png"), dpi=150)
plt.close(fig)

with open(os.path.join(PROCESSED, "findings_pricing.json"), "w") as f:
    json.dump(findings, f, indent=2, default=str)

print("Step 2 complete. Regression R2:", findings["regression"]["r_squared"],
      "| Sweet spot (zone-adjusted):", findings["chalet_sweet_spot_area_sqm_zone_adjusted"], "sqm")
print("Ras El Hekma USD/sqm 2023 to Q3 2025 change:", findings["jll_ras_el_hekma_usd_check"]["usd_change_pct"], "pct")
