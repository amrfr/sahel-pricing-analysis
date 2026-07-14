# Sources

## Unit-level pricing (per compound, see `data/raw/unit_price_samples.csv` for exact figures used)

- Mountain View Ras El Hekma — [Nawy blog](https://www.nawy.com/blog/95621-mountain-view-ras-el-hekma-chalets-with-exclusive-prices/amp)
- Hacienda Bay — [Sawa Helmasr](https://sawahelmasr.com/compounds/hacienda-bay/)
- June Ras El Hekma, Fouka Bay — [Property Finder blog](https://www.propertyfinder.eg/blog/en/best-compounds-in-north-coast/)
- La Vista Bay East — [Shary](https://shary.com.eg/en/projects/la-vista-bay-east-north-coast/), [GPR Property](https://gprproperty.com/en/project/la-vista-north-coast/)
- Marassi (all sub-phases: Santorini, Lea, Marina Views, Marina West, Riva Golf, Skaia, Altea, Marassi Bay) — [FlatAndVilla](https://flatandvilla.com/en/north-coast/marassi-north-coast/)
- Marassi 2026 vintage chalet — [Real Estate Egypt](https://realestate.eg/en/2864-chalet-for-sale-in-marassi-north-coast-from-144-meter)
- Telal North Coast — [FlatAndVilla](https://flatandvilla.com/en/north-coast/telal-north-coast/)
- Silversands — [FlatAndVilla](https://flatandvilla.com/en/north-coast/silversands-north-coast/)
- Solare — [HomeAndMall](https://homeandmall.com/en-eg/north-coast/solare-north-coast/)
- Gaia North Coast — [IPG Egypt](https://ipgegypt.com/en/projects/48-gaia-north-coast-ras-el-hekma)
- Seazen — Property Finder blog (see above)
- Salt North Coast — [SelectHouse](https://selecthouse.co/en/property/salt-north-coast/), [Tatweer Misr official](https://tatweermisr.com/salt)
- D-Bay — [Nawy](https://www.nawy.com/compound/452-d-bay)
- Palm Hills New Alamein — [Badya Palm Hills](https://badyapalmhills.com/apartment/new-alamein-north-coast/)
- Mazarine — [IMICEgypt](https://imicegypt.com/en/projects/mazarine-new-alamein/)
- SouthMed — [IMICEgypt](https://imicegypt.com/en/projects/south-med-egypt/)
- Almaza Bay — [CompoundGate](https://compoundgate.com/en/north-coast/almaza-bay)
- Downtown New Alamein — [Nawy](https://www.nawy.com/compound/314-downtown-new-alamein), [IPG Egypt](https://ipgegypt.com/en/projects/145-downtown-new-alamein-city-edge)
- Modon Ras El Hekma / Wadi Yemm — [EgyProperty](https://egyproperty-eg.com/modon-ras-el-hekma-wadi-yemm-prices-units-2026/)

## Geography, zones, compound list

- [Property Finder Egypt — "63 Best Compounds in North Coast Egypt"](https://www.propertyfinder.eg/blog/en/best-compounds-in-north-coast/) — km-position and legacy (~2022) starting prices for the 63-compound master list
- [Nawy — North Coast (Sahel) area page](https://www.nawy.com/area/north-coast-sahel) — zone km-range definitions, compound counts, live property-availability counts per zone, distance-from-Cairo figures

## Macro market trend

- [Daily News Egypt / JLL — "Egypt's North Coast residential prices soar 390% amid investment boom"](https://www.dailynewsegypt.com/2026/05/13/egypts-north-coast-residential-prices-soar-390-amid-investment-boom-jll/) — nominal price growth by property type and zone, 2023 to Q3 2025
- [Economy Middle East — Egypt real estate H1 2025](https://economymiddleeast.com/news/egypts-real-estate-market-booms-in-h1-2025-despite-inflation-and-rising-construction-costs/) — real-terms (inflation-adjusted) national price growth, 2023-2024
- [CNN Business — Gulf investment in Egypt's North Coast](https://www.cnn.com/2025/10/16/business/egypt-north-coast-gulf-investment-spc)
- [Ahram Online — Ras El Hekma $150bn UAE development deal](https://english.ahram.org.eg/NewsContentP/3/518263/Business/Egypt-signs-historic-multibillion-Ras-El-Hekma-Nor.aspx)
- [Sands of Wealth — average price/sqm Egypt](https://sandsofwealth.com/blogs/news/average-price-per-sqm-egypt)

## Currency (EGP/USD)

- [Al-Ahram Weekly — "Past devaluations"](https://english.ahram.org.eg/News/519335.aspx) — 2022-2024 devaluation timeline
- [Trading Economics — Egyptian Pound](https://tradingeconomics.com/egypt/currency) — current rate

## International benchmarks

- Ain Sokhna (Red Sea Egypt, domestic comparator) — [Lacosta Real Estate villages guide](https://lacosta-realestate.com/ain-sokhna-villages-guide-and-prices-2-0-2-5/), [Proplix North Coast vs. Ain Sokhna](https://www.proplix.co/en/blogs/north-coast-vs-ain-sokhna-best-egyptian-coast-to-invest-in)
- Costa del Sol, Spain — [The Olive Press — "Property prices start to soar in Costa del Sol"](https://www.theolivepress.es/spain-news/2026/03/10/property-prices-costa-del-sol/)
- Bodrum, Turkey — [Property Turkey — beachfront listings](https://www.propertyturkey.com/real_estate/beachfront/turkey)
- Dubai, UAE — [Sands of Wealth — Dubai price forecasts](https://sandsofwealth.com/blogs/news/dubai-price-forecasts), [Engel & Völkers — average price per sqft by area](https://www.engelvoelkers.com/ae/en/resources/average-price-per-square-foot-in-dubai)

## Note on scraping

Live browser-based scraping (Aqarmap, Property Finder, and Dubizzle search results, which render client-side via JavaScript) was attempted but unavailable in this build environment — the Claude in Chrome extension was not connected in this session. All figures above come from server-rendered developer/aggregator pages fetched directly, cross-referenced through web search where a single page didn't have both area and price for a unit. See `METHODOLOGY.md` for how pairing confidence is tracked per row.
