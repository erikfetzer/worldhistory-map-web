# World History Map

An interactive map of the world's political borders from 3400 BCE to 2024 CE. Pick a year, zoom in, click a territory for details, or play the borders changing over any span of time.

It's a static site with no build step: `index.html` plus two data files. Deploy it to Vercel (or any static host) as-is.

## Features

- Year slider across 5,400 years, with a sparkline showing how many polities exist at each point
- Playback at 1 to 250 years per second, or "Each change" mode that jumps from one border change to the next
- Preset play ranges (Classical world, Medieval, Modern…) or a custom range, with optional looping
- Pan and zoom (scroll, drag, pinch), hover names, and click for details with Wikipedia/Wikidata links
- Search for a polity to jump to its time and zoom to it
- Optional dashed outlines for alliances and overlordships
- "Today's borders" toggle: overlays modern country outlines and names on any year, plus US states and Canadian provinces
- **Who ruled here?** Right-click (or long-press, or use the button) on any spot to see every power that held it from 3400 BCE to today, as a timeline and a clickable list
- **Daily quiz:** five rounds a day (one per era), same questions for everyone that day, with a streak counter and a shareable score grid. Results stay in the visitor's browser
- **Guided tours:** captioned stories that move the map and the timeline (Rome, Alexander, the Mongols, the scramble for Africa, World War I)
- **Famous journeys:** follow Marco Polo, Ibn Battuta, Magellan and Elcano, Lewis and Clark, Darwin on the Beagle and Albert Einstein stop by stop, with the route drawn on the map and who ruled each place when they arrived
- **Rise and fall:** the details card graphs each polity's territory over its whole life (click the graph to jump), and **Largest empires** ranks the top 10 by area for the current year, updating live during playback
- **Compare years:** a draggable divider shows one year on the left and another on the right, over the same view
- **Share and record:** links keep the year, the view, the selected polity and the compare year (`#y1250x80p09l47p09z2p98sMongol-Empire`); **Record clip** turns the play range into an MP4 or WebM video with the year burned in, ready to download or share
- **Cities:** about 1,700 historical cities appear and grow with the year (3700 BCE to today); more appear as you zoom in. Period names for well-known renamings (Byzantium → Constantinople → Istanbul, Edo, Leningrad…). Hover for a population estimate; click a city to see who ruled it
- **Seas & lakes:** about 90 hand-placed names for oceans, seas, gulfs, bays and large lakes; oceans show at world view, smaller waters appear as you zoom in. Names change with the period (Mare Nostrum, Pontus Euxinus, German Ocean, Gulf of Siam…). Lakes are drawn in their own blue from Natural Earth 50m lakes (`lakes.json`, public domain). Toggle with "Seas & lakes".
- **Events:** about 230 hand-picked headline events plus ~1,800 famous battles, treaties, revolutions, expeditions and disasters from Wikidata. Pins (a shape and colour per type) fade in and out around their year, more appear as you zoom, a ticker names events as playback passes them, and each opens a card with the story. Filter by type
- **Native lands:** a "Native lands (US cessions)" toggle shows the 700+ tracts the United States acquired from Native nations between 1784 and 1894 (Royce's maps, digitized by the USDA Forest Service), each fading out at its treaty date, with tribe names, present-day nations and links to the treaty texts. Today's reservations, trust lands and First Nations reserves appear with "Today's borders"
- **Rulers and events:** the details card loads a Wikipedia summary plus capital, rulers and key events from Wikidata, live in the visitor's browser, with the capital and numbered event pins on the map
- Shareable links (old `#y117` / `#y-500` links still work)
- Keyboard: Space plays or pauses, ←/→ steps one year, Shift+←/→ jumps to the previous or next change

## Files

| File | What it is |
| --- | --- |
| `index.html` | The whole app (D3 + canvas rendering, loaded from cdnjs/jsDelivr) |
| `borders.json` | Cliopatria borders as TopoJSON (~16 MB, ~3.7 MB gzipped) |
| `land.json` | Natural Earth 1:50m land outline from `world-atlas` |
| `countries.json` | Natural Earth 1:50m country borders from `world-atlas`, for the "Today's borders" overlay (loaded only when toggled on) |
| `favicon.svg`, `*.png`, `manifest.webmanifest` | Favicon, app icons and the 1200×630 share card (`og.png`) |
| `scripts/og-card.html` | Renders `og.png`: serve the repo root, open it, screenshot `#card` (add `?year=` to pick a year) |
| `events.json` | Hand-picked headline events (written in `data-src/events-curated.py`) |
| `events-wikidata.json` | Famous events from Wikidata, refreshed monthly by `.github/workflows/events.yml` running `scripts/build-events-wikidata.py` |
| `admin1.json` | US states and Canadian provinces (Natural Earth 1:50m, public domain), part of the "Today's borders" overlay |
| `indigenous.json` | US land cessions 1784–1894 (USDA Forest Service, CC BY), US reservations and trust lands (US Census, public domain), Canadian reserves and settlement lands (NRCan, OGL-Canada). Built quarterly by `.github/workflows/indigenous.yml` running `scripts/build-indigenous.py` |
| `cities.json` | Merged historical city populations (built by `scripts/build-cities.py` from `data-src/cities/`) |
| `scripts/build-data.sh` | Rebuilds `borders.json` and `land.json` from the sources |

## Run locally

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

## Data and credit

Borders come from **Cliopatria** (Seshat Global History Databank), v0.21, licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/):
Bennett, J.S. et al. "Cliopatria – A geospatial database of world-wide political entities from 3400BCE to 2024CE." *Scientific Data* 12, 247 (2025). https://doi.org/10.1038/s41597-025-04516-9
Source: https://github.com/Seshat-Global-History-Databank/cliopatria

Changes made: converted to TopoJSON, coordinates quantized, attributes trimmed to Name, FromYear, ToYear, Area, Type, Wikipedia, Wikidata and MemberOf.

Cities come from **Reba, Reitsma & Seto (2016)**, "Spatializing 6,000 years of global urbanization from 3700 BC to AD 2000", *Scientific Data* 3, 160034, https://doi.org/10.1038/sdata.2016.34, licensed CC BY 4.0 (Chandler data: doi:10.6084/m9.figshare.2059494; Modelski data: doi:10.6084/m9.figshare.2059497). Copies of the CSVs are in `data-src/cities/`. Changes made: the three tables are merged by city, Modelski's 2000 figures are used only where Chandler has no figures from 1950 on, single-point spikes of more than 4x are dropped as transcription errors, and the Allentown row is excluded.

The land outline and today's country borders are Natural Earth (public domain) via the `world-atlas` npm package.

Cliopatria represents one scholarly reading of past territories. Historical borders were often fuzzy or disputed. Report data errors to the Seshat project.
