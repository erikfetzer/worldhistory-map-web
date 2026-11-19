#!/usr/bin/env python3
"""Build events-wikidata.json: famous dated events with a location, from Wikidata.

Run by .github/workflows/events.yml (monthly, or on demand). Needs network access to query.wikidata.org.
Events are ranked by how many Wikipedia language editions have an article about them ("sitelinks"),
a simple, neutral proxy for how widely known an event is.

Output rows: [year, lon, lat, category, title, wikipediaTitle, sitelinks, qid]
"""
import json, sys, time, urllib.parse, urllib.request

ENDPOINT = "https://query.wikidata.org/sparql"
UA = "whoruled.earth events builder (https://whoruled.earth; https://github.com/erikfetzer/worldhistory-map-web)"

# category -> list of (Wikidata class, minimum sitelinks)
CLASSES = {
    "war": [("Q178561", 22), ("Q188055", 18), ("Q1261499", 18)],                      # battle, siege, naval battle
    "politics": [("Q131569", 12), ("Q625298", 12), ("Q10931", 12), ("Q124734", 14),     # treaty, peace treaty, revolution, rebellion
                 ("Q3882219", 14), ("Q45382", 18)],                                     # assassination, coup d'état
    "exploration": [("Q2401485", 10)],                                                  # expedition
    "disaster": [("Q7944", 16), ("Q7692360", 14), ("Q8070", 14), ("Q168983", 16)],      # earthquake, eruption, tsunami, great fire
}
KEEP = 2600

QUERY = """
SELECT ?e ?eLabel ?date ?coord ?pcoord ?sl ?article WHERE {
  ?e wdt:P31 wd:%(cls)s ; wikibase:sitelinks ?sl .
  FILTER(?sl >= %(min)d)
  { ?e wdt:P585 ?date } UNION { ?e wdt:P580 ?date }
  OPTIONAL { ?e wdt:P625 ?coord }
  OPTIONAL { ?e wdt:P276|wdt:P1071 ?place . ?place wdt:P625 ?pcoord }
  OPTIONAL { ?article schema:about ?e ; schema:isPartOf <https://en.wikipedia.org/> }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

def run(query, tries=4):
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:  # rate limits and timeouts: back off and retry
            print(f"  retry {i + 1}: {e}", file=sys.stderr)
            time.sleep(10 * (i + 1))
    return []

def point(wkt):
    # "Point(lon lat)"
    try:
        lon, lat = wkt[wkt.index("(") + 1: wkt.index(")")].split()
        return round(float(lon), 3), round(float(lat), 3)
    except Exception:
        return None

def year_of(dt):
    # WDQS dates follow XSD 1.1 (year 0 = 1 BCE), so shift non-positive years to historical numbering
    neg = dt.startswith("-")
    y = int(dt.lstrip("-").split("-")[0])
    if neg:
        return -y - 1
    return y if y != 0 else -1

events = {}
for cat, classes in CLASSES.items():
    for cls, mn in classes:
        rows = run(QUERY % {"cls": cls, "min": mn})
        print(f"{cat} {cls}: {len(rows)} rows", file=sys.stderr)
        for b in rows:
            qid = b["e"]["value"].rsplit("/", 1)[-1]
            label = b.get("eLabel", {}).get("value", "")
            if not label or label == qid:
                continue
            ll = point(b.get("coord", {}).get("value", "")) or point(b.get("pcoord", {}).get("value", ""))
            if not ll:
                continue
            try:
                y = year_of(b["date"]["value"])
            except Exception:
                continue
            if y < -3400 or y > 2025:
                continue
            art = b.get("article", {}).get("value", "")
            wiki = urllib.parse.unquote(art.rsplit("/wiki/", 1)[-1]).replace("_", " ") if art else ""
            sl = int(b["sl"]["value"])
            cur = events.get(qid)
            if cur is None or y < cur[0]:  # keep the earliest date if an item has several
                events[qid] = [y, ll[0], ll[1], cat, label, wiki, sl, qid]
        time.sleep(2)

rows = sorted(events.values(), key=lambda r: -r[6])[:KEEP]
rows.sort(key=lambda r: r[0])
if len(rows) < 300:
    sys.exit(f"Only {len(rows)} events came back; keeping the previous file.")
with open("events-wikidata.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))
print(f"events-wikidata.json: {len(rows)} events", file=sys.stderr)
