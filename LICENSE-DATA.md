# Data licenses

The code in this repo is MIT-licensed (see `LICENSE`). The data files below come from other sources and keep their own licenses. If you reuse them, keep the credits.

| File | Source | License |
|---|---|---|
| `borders.json` | Cliopatria v0.21, Seshat Global History Databank. Bennett, J.S. et al., "Cliopatria – A geospatial database of world-wide political entities from 3400BCE to 2024CE", *Scientific Data* 12, 247 (2025), https://doi.org/10.1038/s41597-025-04516-9. Converted to TopoJSON, coordinates quantized, attributes trimmed. | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `cities.json`, `data-src/cities/*.csv` | Reba, Reitsma & Seto (2016), "Spatializing 6,000 years of global urbanization from 3700 BC to AD 2000", *Scientific Data* 3, 160034, https://doi.org/10.1038/sdata.2016.34 (Chandler: doi:10.6084/m9.figshare.2059494; Modelski: doi:10.6084/m9.figshare.2059497). Tables merged by city; outlier spikes and the Allentown row removed. | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `land.json`, `countries.json` | Natural Earth 1:50m via the `world-atlas` package (ISC, Michael Bostock) | Public domain |
| `admin1.json`, `lakes.json` | Natural Earth 1:50m | Public domain |
| `indigenous.json` | US land cessions 1784–1894: USDA Forest Service (CC BY 4.0). US reservations and trust lands: US Census Bureau (public domain). Canadian reserves and settlement lands: Natural Resources Canada ([Open Government Licence – Canada](https://open.canada.ca/en/open-government-licence-canada)). | Mixed, as listed |
| `events-wikidata.json` | Wikidata | [CC0](https://creativecommons.org/publicdomain/zero/1.0/) |
| `events.json`, `disputed.json` | Written for this project | MIT, with the code |

Wikipedia summaries and Wikidata details shown in the map's info cards are fetched live in the visitor's browser and aren't stored in this repo. Wikipedia text is CC BY-SA 4.0; each card links to its source article.
