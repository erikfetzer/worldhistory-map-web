#!/usr/bin/env python3
"""Build cities.json from the Reba, Reitsma & Seto (2016) historical urban population data.

Sources (CC BY 4.0), copies kept in data-src/cities/:
  chandlerV2.csv         figshare doi:10.6084/m9.figshare.2059494  (Chandler, 2250 BCE - 1975 CE)
  modelskiAncientV2.csv  figshare doi:10.6084/m9.figshare.2059497  (Modelski, 3700 BCE - 1000 CE)
  modelskiModernV2.csv   Modelski, 2000 CE
Rows describing the same city (same name or alternate name, within ~60 km) are merged.
Cleaning: Modelski's 2000 figures (city proper) are used only where Chandler has nothing from 1950 on
(Chandler's later figures are metro areas, so mixing them makes cities appear to shrink); single-point
spikes or dips of more than 4x against both neighbours within 60 years are dropped as transcription errors;
a few rows known to be wrong are excluded (see DROP_CITIES).
Output: [[name, altName, lon, lat, [[year, population], ...]], ...] sorted by peak population.
Run from the repo root:  python3 scripts/build-cities.py
"""
import csv, io, json, math, re, unicodedata

SRC = "data-src/cities/"
FILES = ["modelskiAncientV2.csv", "chandlerV2.csv", "modelskiModernV2.csv"]

def load(path):
    raw = open(path, "rb").read()
    try:
        txt = raw.decode("utf-8")
    except UnicodeDecodeError:
        txt = raw.decode("cp1252")
    return list(csv.DictReader(io.StringIO(txt)))

def year_of(col):
    era, n = col.split("_")
    n = int(n)
    return -n if era == "BC" else n

def norm(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())

def km(a, b):
    (lo1, la1), (lo2, la2) = a, b
    p = math.pi / 180
    h = math.sin((la2 - la1) * p / 2) ** 2 + math.cos(la1 * p) * math.cos(la2 * p) * math.sin((lo2 - lo1) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))

DROP_CITIES = {"Allentown"}  # row's values belong to a much larger city (e.g. 17.6M in 1914)

cities = []
for f in FILES:
    for r in load(SRC + f):
        try:
            lon, lat = float(r["Longitude"]), float(r["Latitude"])
        except (TypeError, ValueError):
            continue
        obs = {}
        for c, v in r.items():
            if c and re.fullmatch(r"(BC|AD)_\d+", c) and (v or "").strip():
                obs[year_of(c)] = int(float(v.replace(",", "")))
        if not obs:
            continue
        name, alt = r["City"].strip(), (r["OtherName"] or "").strip()
        if name in DROP_CITIES:
            continue
        keys = {norm(name), norm(alt)} - {""}
        match = None
        for c in cities:
            if (keys & c["keys"]) and km((lon, lat), c["ll"]) < 60:
                match = c
                break
        if match and f == "modelskiModernV2.csv" and any(y >= 1950 for y in match["obs"]):
            obs = {}  # keep Chandler's metro series consistent
        if match:
            for y, p in obs.items():
                match["obs"][y] = max(p, match["obs"].get(y, 0))
            match["keys"] |= keys
            if alt and not match["alt"] and norm(alt) != norm(match["name"]):
                match["alt"] = alt
        else:
            cities.append({"name": name, "alt": alt if norm(alt) != norm(name) else "", "ll": (lon, lat), "obs": obs, "keys": keys})

def despike(obs):
    keep = list(obs)
    changed = True
    while changed:
        changed = False
        for i in range(1, len(keep) - 1):
            (y0, p0), (y1, p1), (y2, p2) = keep[i - 1], keep[i], keep[i + 1]
            if y2 - y0 <= 120 and ((p1 > 4 * p0 and p1 > 4 * p2) or (4 * p1 < p0 and 4 * p1 < p2)):
                del keep[i]; changed = True; break
    return keep

out = []
for c in cities:
    obs = despike(sorted(c["obs"].items()))
    if not obs:
        continue
    out.append([c["name"], c["alt"], round(c["ll"][0], 3), round(c["ll"][1], 3), [[y, p] for y, p in obs if p > 0]])
out.sort(key=lambda c: -max(p for _, p in c[4]))
with open("cities.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
print(f"cities.json: {len(out)} cities")
