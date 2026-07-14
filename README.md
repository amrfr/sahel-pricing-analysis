# Sahel (North Coast Egypt) Property Pricing & Site-Selection Analysis

A data-driven answer to three questions a developer or investor would actually ask before writing a cheque on Egypt's North Coast ("El Sahel"): what does the real price/sqm landscape look like, what's the size "sweet spot" per unit type, and where should a new compound be built — benchmarked against comparable coastal resort markets worldwide.

**v2 of this analysis** roughly triples the underlying dataset (21 → 59 unit-level observations across 27 compounds), replaces the earlier bivariate "sweet spot" fit with a proper multiple regression that controls for zone and unit type, adds currency-adjusted (USD) pricing so nominal EGP appreciation isn't confused with currency devaluation, and adds an international benchmark comparison against Ain Sokhna, Costa del Sol, Bodrum, and Dubai. See `METHODOLOGY.md` for full technical detail and `SOURCES.md` for the complete source list.

## Executive summary

**Price tiers are enormous, and driven by location + product type far more than by size.** Chalets range $297–$3,604/sqm (currency-adjusted), twin houses $310–$4,124/sqm, standalone villas $751–$8,247/sqm. A multiple regression controlling for zone and unit type (n=59, R²=0.39) finds unit size explains relatively little: a 1% larger chalet is associated with only a 0.13% *lower* price/sqm, holding location and type fixed — location tier and product type dominate.

**Al Dabaa and Sidi Heneish command roughly 2.5x the price/sqm of Al Alamein and Sidi Abdel Rahman**, controlling for what's actually being built there — a materially different picture than simply averaging listed prices by zone, which is distorted by which unit types happen to be sampled in each zone.

**The chalet "sweet spot" is larger than earlier assumed.** Controlling for zone (comparing each chalet's price/sqm to its own zone's median), the size discount keeps improving out to roughly 200 sqm before flattening — pointing to spacious 2–3BR chalets (180–220 sqm) as the value sweet spot, not the smaller units a naive pooled analysis suggested.

**Currency-adjusting matters — a lot.** The North Coast's headline "+390% nominal price growth 2023–Q3 2025" (JLL) partly reflects the EGP's ~55% devaluation over the same window, not just demand. Even after adjusting for FX, Ras El Hekma's dollar-denominated price/sqm still roughly tripled (JLL-reported $1,413 → $4,490/sqm). But a matched same-unit-type comparison within this dataset (Marassi chalets, 2023 vintage vs. 2026 vintage) shows a much more modest +9.3% real USD gain — a reminder that aggregate market indices can overstate true asset-level appreciation because the *mix* of what's launching shifts upmarket over time.

**Internationally, Sahel spans two very different markets in one coastline.** Mass-market Sahel chalets ($297–$1,200/sqm) are dramatically cheaper than Bodrum (~$1,900–2,400/sqm) or Costa del Sol (~$3,900–4,750/sqm) — a currency-driven bargain. But ultra-prime Sahel beachfront (La Vista Bay, Silversands, Modon Ras El Hekma: $3,000–$8,000+/sqm) now prices *at or above* Costa del Sol and approaches Dubai's citywide average — the top tier has decoupled from the devaluation discount and is pricing as a genuine international luxury product.

**Best zone for a new compound, updated: Al Dabaa** (site score 0.75 of 1.0), ahead of Ghazala Bay (0.55) and Sidi Heneish (0.49). Adding a pricing-power dimension (derived from the regression) to the original competition/demand/accessibility/infrastructure model changed the ranking: Al Dabaa combines real whitespace (22 existing compounds against strong per-compound absorption), the second-highest infrastructure tailwind from the Ras El Hekma halo, and — now confirmed independently by the regression — the highest realizable price/sqm of any zone in the dataset. Ghazala Bay remains attractive on competition/demand grounds but its pricing-power score is **not meaningfully estimated** (0% sample coverage — no priced listings in this dataset fall there), so treat that ranking as provisional pending better data.

## Repo structure

```
sahel-pricing-analysis/
├── data/
│   ├── raw/                              # sourced input data (see SOURCES.md)
│   │   ├── unit_price_samples.csv         # 59 unit-level price/sqm observations
│   │   ├── compounds_master.csv           # 76 compounds with coastal km position
│   │   ├── zone_supply_demand.csv            # 6 named zones: supply, demand, distance
│   │   ├── fx_rates.csv                      # EGP/USD by year, for currency adjustment
│   │   ├── international_benchmarks.csv   # Ain Sokhna / Bodrum / Costa del Sol / Dubai
│   │   └── market_trend_jll.csv              # JLL-reported North Coast macro price trend
│   └── processed/                        # analysis outputs (generated)
├── figures/                              # charts (generated)
├── src/
│   ├── 01_data_prep.py                   # load, clean, currency-adjust
│   ├── 02b_pricing_analysis.py           # regression, sweet spot, benchmarks
│   └── 03_site_selection.py              # zone scoring model
├── METHODOLOGY.md                        # full methodology & limitations
├── SOURCES.md                            # complete source list
├── requirements.txt
└── README.md
```

## Reproduce it

```bash
pip install -r requirements.txt
python src/01_data_prep.py
python src/02b_pricing_analysis.py
python src/03_site_selection.py
```

Every file in `data/processed/` and `figures/` is regenerated from `data/raw/` — nothing downstream is hand-edited. This was verified end-to-end from a clean `git clone` before packaging.

## Key charts

- `figures/regression_coefficients.png` — what actually moves price/sqm once size, type and zone are controlled for
- `figures/sweet_spot_zone_adjusted.png` — the zone-adjusted chalet size sweet spot
- `figures/international_benchmarks.png` — Sahel's price tiers against Ain Sokhna, Bodrum, Costa del Sol, Dubai
- `figures/site_selection_ranking.png` — the updated six-zone composite site score
- `figures/site_selection_breakdown.png` — score breakdown by zone and criterion

## License

MIT — see `LICENSE`.
