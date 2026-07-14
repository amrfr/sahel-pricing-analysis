"""
Step 1: load raw sources, clean, currency-adjust to USD using the
price_recency-matched EGP/USD rate, and write a unified processed
dataset for steps 2 and 3.
Run: python src/01_data_prep.py
"""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
PROCESSED = os.path.join(BASE, "data", "processed")
os.makedirs(PROCESSED, exist_ok=True)

units = pd.read_csv(os.path.join(RAW, "unit_price_samples.csv"))
fx = pd.read_csv(os.path.join(RAW, "fx_rates.csv")).set_index("year")["egp_per_usd"]

units["price_per_sqm_egp"] = units["total_price_egp"] / units["area_sqm"]
units["egp_per_usd"] = units["price_recency"].map(fx)
units["price_per_sqm_usd"] = units["price_per_sqm_egp"] / units["egp_per_usd"]
units["total_price_usd"] = units["total_price_egp"] / units["egp_per_usd"]

units.to_csv(os.path.join(PROCESSED, "unit_price_samples_enriched.csv"), index=False)

print("Loaded", len(units), "unit-level price observations across",
      units["compound"].nunique(), "compounds and", units["zone"].nunique(), "zones.")
print("Unit type counts:")
print(units["unit_type"].value_counts().to_string())
print("Pairing confidence counts:")
print(units["pairing_confidence"].value_counts().to_string())

compounds = pd.read_csv(os.path.join(RAW, "compounds_master.csv"))
compounds.to_csv(os.path.join(PROCESSED, "compounds_master_clean.csv"), index=False)
print("\nCompounds master list:", len(compounds), "compounds (spans km",
      compounds["km_marker"].min(), "to km", compounds["km_marker"].max(), ")")

print("\nStep 1 complete.")
