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
- Shareable year links: `#y117`, `#y-500`
- Keyboard: Space plays or pauses, ←/→ steps one year, Shift+←/→ jumps to the previous or next change

## Files

| File | What it is |
| --- | --- |
| `index.html` | The whole app (D3 + canvas rendering, loaded from cdnjs/jsDelivr) |
| `borders.json` | Cliopatria borders as TopoJSON (~16 MB, ~3.7 MB gzipped) |
| `land.json` | Natural Earth 1:50m land outline from `world-atlas` |
| `favicon.svg`, `*.png`, `manifest.webmanifest` | Favicon, app icons and the 1200×630 share card (`og.png`) |
| `scripts/og-card.html` | Renders `og.png`: serve the repo root, open it, screenshot `#card` (add `?year=` to pick a year) |
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

The land outline is Natural Earth (public domain) via the `world-atlas` npm package.

Cliopatria represents one scholarly reading of past territories. Historical borders were often fuzzy or disputed. Report data errors to the Seshat project.
