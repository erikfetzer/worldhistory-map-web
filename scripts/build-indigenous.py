#!/usr/bin/env python3
"""Build indigenous.json (TopoJSON) with two layers:

  cessions  US land cessions, 1784-1894: 752 tracts from Charles C. Royce's "Indian Land Cessions in the
            United States" (1899), digitized by the USDA Forest Service with Dr. Claudio Saunt (2018).
            CC BY. https://catalog.data.gov/dataset/tribal-lands-ceded-to-the-united-states-feature-layer
  reserves  Today's reservations and reserves:
            - US Census Bureau cartographic boundaries, American Indian/Alaska Native/Native Hawaiian Areas
              (public domain). Statistical areas (OTSA, ANVSA, TDSA, SDTSA) are left out: they are not lands.
            - Natural Resources Canada, Aboriginal Lands of Canada Legislative Boundaries
              (Open Government Licence - Canada).

Run by .github/workflows/indigenous.yml; needs network access and Node (for mapshaper).
"""
import datetime, io, json, os, re, subprocess, sys, tempfile, urllib.parse, urllib.request, zipfile

UA = "whoruled.earth data builder (https://whoruled.earth; https://github.com/erikfetzer/worldhistory-map-web)"
TMP = tempfile.mkdtemp()

def get(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def mapshaper(*args):
    cmd = ["npx", "-y", "mapshaper@0.6", *args]
    print("  $", " ".join(cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)

# ---------------- cessions (ArcGIS REST, GeoJSON in WGS84, lightly generalized) ----------------
CESS = "https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_TribalCessionLands_01/MapServer/0/query"
FIELDS = ["cessnum", "schdtrb", "presdaytrb", "cessdate1", "date1link_kappler_treaty", "link_other_treaty",
          "link_federal_statute", "link_executive_order", "date1link_royce_schedule", "statecounty"]

def year_from_ms(ms):
    if ms is None:
        return None, None
    d = datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=ms)
    return d.year, d.date().isoformat()

feats, offset = [], 0
while True:
    q = {"where": "1=1", "outFields": "*", "outSR": "4326", "f": "geojson", "returnGeometry": "true",
         "maxAllowableOffset": "0.004", "geometryPrecision": "4", "resultOffset": str(offset), "resultRecordCount": "500"}
    data = json.loads(get(CESS + "?" + urllib.parse.urlencode(q)))
    batch = data.get("features", [])
    print(f"cessions: got {len(batch)} at offset {offset}", file=sys.stderr)
    for f in batch:
        raw = f.get("properties") or {}
        p = {k.split(".")[-1].lower(): v for k, v in raw.items()}
        y, iso = year_from_ms(p.get("cessdate1"))
        if not f.get("geometry") or y is None:
            continue
        link = p.get("date1link_kappler_treaty") or p.get("link_other_treaty") or p.get("link_federal_statute") \
            or p.get("link_executive_order") or ""
        feats.append({"type": "Feature", "geometry": f["geometry"], "properties": {
            "n": p.get("cessnum") or "", "t": (p.get("schdtrb") or "").strip(), "p": (p.get("presdaytrb") or "").strip(),
            "y": y, "d": iso, "l": link, "r": p.get("date1link_royce_schedule") or "", "s": (p.get("statecounty") or "")[:160]}})
    if len(batch) < 500:
        break
    offset += 500
if len(feats) < 300:
    sys.exit(f"Only {len(feats)} cessions came back; stopping so the previous file is kept.")
cess_path = os.path.join(TMP, "cessions.geojson")
json.dump({"type": "FeatureCollection", "features": feats}, open(cess_path, "w"))
print(f"cessions: {len(feats)} features", file=sys.stderr)

# ---------------- US reservations and trust lands (Census cartographic boundaries) ----------------
us_path = None
for yr in (2024, 2023):
    try:
        z = zipfile.ZipFile(io.BytesIO(get(f"https://www2.census.gov/geo/tiger/GENZ{yr}/shp/cb_{yr}_us_aiannh_500k.zip")))
        d = os.path.join(TMP, f"us{yr}"); z.extractall(d)
        shp = [os.path.join(d, n) for n in os.listdir(d) if n.endswith(".shp")][0]
        us_path = os.path.join(TMP, "us.geojson")
        mapshaper(shp, "-filter", "!/(OTSA|ANVSA|TDSA|SDTSA)$/.test(NAMELSAD)",
                  "-each", "name=NAMELSAD, src='us'", "-filter-fields", "name,src",
                  "-proj", "wgs84", "-simplify", "dp", "8%", "keep-shapes", "-o", "format=geojson", us_path)
        print(f"US reservations: {yr}", file=sys.stderr)
        break
    except Exception as e:
        print(f"US reservations {yr} failed: {e}", file=sys.stderr)

# ---------------- Canada reserves and settlement lands (NRCan) ----------------
ca_path = None
CA_BASE = "https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/geobase_al_ta/shp_eng/"
try:
    names = []
    try:
        listing = get(CA_BASE).decode("utf-8", "ignore")
        names = re.findall(r'href="([^"]+\.zip)"', listing)
    except Exception as e:
        print(f"Canada listing failed: {e}", file=sys.stderr)
    cand = [n for n in names if re.search(r"_CA_", n, re.I)] or ["AL_TA_CA_SHP_eng.zip"]
    z = zipfile.ZipFile(io.BytesIO(get(urllib.parse.urljoin(CA_BASE, cand[0]))))
    d = os.path.join(TMP, "ca"); z.extractall(d)
    shps = []
    for root, _, files in os.walk(d):
        shps += [os.path.join(root, f) for f in files if f.lower().endswith(".shp")]
    shp = max(shps, key=os.path.getsize)
    fields_dbf = shp[:-4] + ".dbf"
    ca_path = os.path.join(TMP, "ca.geojson")
    mapshaper(shp, "-each", "name=(this.properties.NAME1||this.properties.ENNAME||this.properties.NAME||this.properties.ADMIN_NAME||''), src='ca'",
              "-filter-fields", "name,src", "-proj", "wgs84", "-simplify", "dp", "8%", "keep-shapes",
              "-o", "format=geojson", ca_path)
    print(f"Canada reserves: {os.path.basename(shp)}", file=sys.stderr)
except Exception as e:
    print(f"Canada reserves failed: {e}", file=sys.stderr)

# ---------------- combine ----------------
parts = [p for p in (us_path, ca_path) if p]
res_path = os.path.join(TMP, "reserves.geojson")
if parts:
    fc = {"type": "FeatureCollection", "features": []}
    for p in parts:
        fc["features"] += json.load(open(p))["features"]
    json.dump(fc, open(res_path, "w"))
inputs = [cess_path] + ([res_path] if parts else [])
mapshaper("-i", *inputs, "combine-files", "-simplify", "dp", "60%", "keep-shapes",
          "-o", "format=topojson", "quantization=1e5", "indigenous.json")
t = json.load(open("indigenous.json"))
print("indigenous.json objects:", {k: len(v.get("geometries", [])) for k, v in t["objects"].items()}, file=sys.stderr)
