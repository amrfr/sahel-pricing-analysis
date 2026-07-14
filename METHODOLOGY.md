# Methodology & limitations

Read this before citing any number in this repo. Every design choice below was made to be defensible, not impressive — where the data is thin, this document says so.

## Dataset

59 unit-level price observations (compound, unit type, area in sqm, total price, currency, listing vintage) across 27 named compounds spanning km7 to km306 of the Alexandria–Marsa Matrouh coastal road, compiled from developer sales pages and real-estate aggregator sites (full list in `SOURCES.md`). This is a **research-compiled dataset, not a live scrape** — the build environment could not execute JavaScript-rendered search/listing pages (Aqarmap, Property Finder, and Dubizzle search results all render client-side, and browser automation was unavailable in this session), so every row was manually sourced from a page that renders as static HTML (individual compound/project pages, which most Egyptian real-estate marketing sites do render server-side).

Each row carries a `pairing_confidence` flag:
- **exact** (49 of 59 rows): the source stated a specific area and a specific matching total price for that unit.
- **low** (8 rows): the source gave a "starting price" and a separate area range, and the row pairs the minimum of each — this is standard practice for developer marketing pages but tends to **overstate** true price/sqm, since the cheapest advertised price often applies to a different (larger, less desirable) unit than the smallest advertised area.
- **estimate** (2 rows, both Modon Ras El Hekma): the source gave only an aggregate EGP/sqm range (e.g. "145,000–220,000 EGP/sqm for apartments"), and the row uses the range midpoint with an assumed representative area rather than a specific listing.

Treat `low`- and `estimate`-confidence rows as directionally useful, not precise. They are retained (rather than dropped) because excluding them would silently bias the sample toward compounds with unusually clean marketing pages, which are not randomly distributed across price tiers.

## Currency adjustment

All EGP figures are converted to USD using the year matched to each row's `price_recency` (see `data/raw/fx_rates.csv`, sourced from Ahram Online and Trading Economics): 2022 at 24.5, 2023 at 30.9, 2024 at 50.8, 2025 at an estimated 48.5 (interpolated — 2025 saw the EGP roughly stable between the March 2024 flotation level and mid-2026), 2026 at 49.95. This matters enormously here: the EGP lost about 55% of its dollar value between the 2023 and 2024/2025 vintages sampled in this dataset. Comparing raw EGP prices across vintages without this adjustment would attribute currency devaluation to real price appreciation.

## Regression: what actually drives price/sqm

`log(price_per_sqm_usd) ~ log(area_sqm) + unit_type + zone`, fit by ordinary least squares (numpy `lstsq` on the design matrix — no external ML library). n=59, R²=0.386, adjusted R²=0.301. Unit type and zone are one-hot encoded with `standalone_villa`/`twin_house` (baseline: chalet) and each named zone (baseline: Al Alamein).

This supersedes the v1 analysis's simple bivariate fit of price/sqm against area alone, which pooled budget and ultra-prime compounds together and confounded the true size effect with tier effects. The R² of 0.39 is a moderate fit for cross-sectional real-estate pricing data at this sample size — real-world listing prices carry idiosyncratic noise (specific view, exact beachfront distance, finishing level, developer brand equity) that a 6-variable model cannot capture. Read the coefficients as directionally reliable, not as a pricing calculator.

## Sweet-spot definition (zone-adjusted)

For chalets only (the largest, most liquid sub-sample, n=31): each chalet's price/sqm is expressed relative to its own zone's chalet median (`relative_price_per_sqm`), which removes the zone/tier effect before looking at the size relationship. A linear fit of this ratio against area is then used to find the smallest area at which the fitted relative price/sqm comes within 10% of its value at the largest observed chalet (204 sqm in this sample) — i.e., the point past which buying bigger stops meaningfully improving your price/sqm. This produced a materially different, larger sweet-spot estimate (~204 sqm) than the unadjusted v1 analysis (~78 sqm), because the v1 fit was distorted by small ultra-prime view units at the low end and budget compounds at the high end being compared on the same scale.

This is still a linear approximation over 31 points — a large, well-populated dataset (hundreds of matched listings per zone) would likely show a non-linear (diminishing-returns) curve rather than a straight line. Treat "~200 sqm" as "the discount visibly flattens somewhere in the 180-220 sqm range," not a precise optimum.

## Same-compound appreciation checks

Two pairs in the dataset happen to price the *same compound and unit type* at two different points in time: Marassi chalets (2023 vintage vs. a 2026-priced 144 sqm unit) and La Vista Bay East chalets (2025 vs. 2026 vintage, both 150 sqm). These are single matched-pair comparisons, not a time series — useful as a sanity check against the aggregate JLL trend, not as a robust appreciation estimate. The JLL macro figures (`data/raw/market_trend_jll.csv`) are a genuine third-party published index and are more statistically reliable than these two matched pairs; the discrepancy between them (JLL shows +218% USD for Ras El Hekma over a similar window, the matched Marassi pair shows +9.3% USD) is flagged explicitly in the README as a compositional-shift artifact worth further investigation, not resolved.

## Site-selection scoring model

A transparent weighted-sum model, not a black box — every weight lives in the `weights` dict in `src/03_site_selection.py` and can be changed:

- **Competition score (25%)**: inverse-normalized count of existing compounds per zone (Nawy-reported, authoritative for the six named zones).
- **Demand score (20%)**: available-properties-per-compound, a rough absorption proxy (also Nawy-reported).
- **Accessibility score (15%)**: inverse-normalized distance from Cairo.
- **Infrastructure tailwind (20%)**: a manually-assigned flag (1.0 Ras El Hekma, 0.6 Al Dabaa, 0.4 Sidi Heneish, 0 elsewhere) reflecting the $150bn state-backed Ras El Hekma megaproject and its geographic halo. This is a judgment call, not a measured quantity — reasonable people could weight adjacency differently.
- **Pricing power (20%, new in v2)**: derived directly from the regression's zone coefficients, rescaled 0–1. This is the one score genuinely grounded in this repo's own data rather than external reporting, and it is only as reliable as that zone's sample coverage (see below).

**Sample coverage matters.** `data/processed/zone_sample_coverage.csv` reports what fraction of each zone's officially-reported compound count is actually represented in this repo's 59-row dataset. Al Dabaa (22.7%) and Sidi Abdel Rahman (22.4%) have reasonable coverage; Ghazala Bay (0%) and Sidi Heneish (8%) do not. A pricing-power score built on zero observed listings is not a measured "low price" — it is an absence of data that defaulted to the baseline in the min-max scaling. This is called out explicitly rather than presented as a confident finding.

## What would make this materially better

In rough priority order: (1) live scraping via browser automation to get hundreds of listings per zone instead of dozens total, removing the sample-coverage gaps that currently limit the pricing-power dimension for several zones; (2) a real land-acquisition-cost input per zone, which this analysis could not source and which is likely the single biggest missing variable in the site-selection model; (3) a longer time series (quarterly indices per zone/type) to replace the two single matched-pair appreciation checks with an actual trend.
