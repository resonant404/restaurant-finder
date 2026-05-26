#!/usr/bin/env python3
"""Search the Stay Cool London API for air-conditioned venues.

Usage:
    staycool_search.py [options]

Options (all optional, combine freely):
    --q TEXT          Search by name, area, or postcode
    --area AREA       Exact area name (e.g. Soho, Shoreditch)
    --category CAT    restaurant | pub | cafe | bar | takeaway
    --ac STATUSES     Comma-separated: confirmed,likely,unlikely (default: confirmed,likely)
    --lat LAT         User latitude for proximity sort
    --lng LNG         User longitude for proximity sort
    --radius MILES    Max distance in miles (requires --lat/--lng)
    --limit N         Max results (default 20, max 200)

Emits JSON to stdout. Stdlib-only — no pip install, no venv.

Stay Cool London (staycool.lol) provides AC status for 38,000+ London venues
sourced from EPC energy certificates, chain verification, and building data.
"""
import json
import sys
import urllib.error
import urllib.request
import urllib.parse

API_BASE = "https://staycool.lol/api/venues"
TIMEOUT_SECONDS = 10


def parse_args(argv):
    args = {}
    i = 1
    while i < len(argv):
        if argv[i].startswith("--") and i + 1 < len(argv):
            args[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            i += 1
    return args


def search(params):
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v})
    url = f"{API_BASE}?{query}" if query else API_BASE
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "detail": e.read().decode("utf-8", errors="replace")}
    except urllib.error.URLError as e:
        return {"error": "network", "detail": str(e.reason)}


def main(argv):
    args = parse_args(argv)

    params = {}
    if args.get("q"):
        params["q"] = args["q"]
    if args.get("area"):
        params["area"] = args["area"]
    if args.get("category"):
        params["category"] = args["category"]
    params["ac"] = args.get("ac", "confirmed,likely")
    if args.get("lat"):
        params["lat"] = args["lat"]
    if args.get("lng"):
        params["lng"] = args["lng"]
    if args.get("radius"):
        params["radius"] = args["radius"]
    params["limit"] = args.get("limit", "20")

    result = search(params)
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
