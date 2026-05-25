#!/usr/bin/env python3
"""Search Google Places (New) Text Search and emit JSON to stdout.

Usage:
    places_search.py "query 1" ["query 2" ...]

Reads the Google Maps Platform API key from $GOOGLE_PLACES_API_KEY, or from a
`.env` file next to this script (a single line `GOOGLE_PLACES_API_KEY=...`).

Exits with status 3 and "GOOGLE_PLACES_API_KEY not set" on stderr when no key
is configured. Callers detect this and fall back to another search backend.

Stdlib-only by design — no pip install, no venv. Ships inside the skill bundle.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"

FIELD_MASK = ",".join([
    "places.displayName",
    "places.formattedAddress",
    "places.rating",
    "places.userRatingCount",
    "places.priceLevel",
    "places.priceRange",
    "places.regularOpeningHours.openNow",
    "places.regularOpeningHours.weekdayDescriptions",
    "places.types",
    "places.primaryType",
    "places.websiteUri",
    "places.googleMapsUri",
    "places.location",
    "places.businessStatus",
    "places.editorialSummary",
])

TIMEOUT_SECONDS = 10
MAX_RESULTS = 10
MAX_PARALLEL = 5


def load_api_key():
    key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if key:
        return key.strip()
    dotenv = Path(__file__).resolve().parent / ".env"
    if dotenv.is_file():
        for line in dotenv.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == "GOOGLE_PLACES_API_KEY":
                return value.strip().strip('"').strip("'")
    return None


def search(query, api_key):
    body = json.dumps({"textQuery": query, "maxResultCount": MAX_RESULTS}).encode("utf-8")
    req = urllib.request.Request(
        PLACES_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "detail": e.read().decode("utf-8", errors="replace")}
    except urllib.error.URLError as e:
        return {"error": "network", "detail": str(e.reason)}


def main(argv):
    if len(argv) < 2:
        print('usage: places_search.py "query" ["query2" ...]', file=sys.stderr)
        return 2

    queries = argv[1:]
    api_key = load_api_key()
    if not api_key:
        print("GOOGLE_PLACES_API_KEY not set", file=sys.stderr)
        return 3

    workers = min(len(queries), MAX_PARALLEL)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda q: (q, search(q, api_key)), queries))

    json.dump({q: r for q, r in results}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
