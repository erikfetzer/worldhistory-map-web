#!/usr/bin/env bash
# Rebuild borders.json and land.json from their sources.
# Needs: git, unzip, node/npm. Run from the repo root.
set -euo pipefail

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

git clone --depth 1 https://github.com/Seshat-Global-History-Databank/cliopatria.git "$WORK/cliopatria"
unzip -q "$WORK/cliopatria/cliopatria.geojson.zip" -d "$WORK/data"
SRC="$(ls "$WORK"/data/*.geojson | head -1)"

npx -y mapshaper@0.6 "$SRC" \
  -filter-fields Name,FromYear,ToYear,Area,Type,Wikipedia,Wikidata,MemberOf \
  -each 'Area=Math.round(Area)' \
  -o format=topojson quantization=2e5 borders.json

npm pack world-atlas@2 --pack-destination "$WORK" >/dev/null
tar -xzf "$WORK"/world-atlas-*.tgz -C "$WORK"
cp "$WORK/package/land-50m.json" land.json
cp "$WORK/package/countries-50m.json" countries.json

echo "Done: borders.json, land.json and countries.json updated."
