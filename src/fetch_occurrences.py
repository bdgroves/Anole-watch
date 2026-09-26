"""Fetch Anolis occurrence records for Guadeloupe from GBIF → GeoJSON.

Writes docs/data/occurrences.geojson for the Leaflet map.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

GBIF = "https://api.gbif.org/v1"
OUT = Path(__file__).resolve().parents[1] / "docs" / "data" / "occurrences.geojson"

TAXA = [
    "Anolis marmoratus",
    "Anolis ferreus",
    "Anolis terraealtae",
    "Anolis kahouannensis",
    "Anolis chrysops",
    "Anolis desiradei",
]

# Guadeloupe archipelago bounding box (lon/lat), incl. Marie-Galante, Les Saintes, La Désirade
BBOX_WKT = "POLYGON((-61.90 15.80,-60.95 15.80,-60.95 16.55,-61.90 16.55,-61.90 15.80))"
PAGE = 300
MAX_PER_TAXON = 5000


def match_taxon(name: str) -> int | None:
    r = requests.get(f"{GBIF}/species/match", params={"name": name, "strict": "true"}, timeout=30)
    r.raise_for_status()
    js = r.json()
    if js.get("matchType") == "NONE":
        print(f"  ⚠ no GBIF match for {name}")
        return None
    return js.get("usageKey")


def fetch_occurrences(taxon_key: int):
    offset = 0
    while offset < MAX_PER_TAXON:
        r = requests.get(
            f"{GBIF}/occurrence/search",
            params={
                "taxonKey": taxon_key,
                "geometry": BBOX_WKT,
                "hasCoordinate": "true",
                "hasGeospatialIssue": "false",
                "limit": PAGE,
                "offset": offset,
            },
            timeout=60,
        )
        r.raise_for_status()
        js = r.json()
        yield from js.get("results", [])
        if js.get("endOfRecords", True):
            break
        offset += PAGE
        time.sleep(0.3)


def to_feature(rec: dict, query_name: str) -> dict:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [rec["decimalLongitude"], rec["decimalLatitude"]]},
        "properties": {
            "taxon": query_name,
            "scientificName": rec.get("scientificName"),
            "date": rec.get("eventDate", "")[:10] or None,
            "basis": rec.get("basisOfRecord"),
            "dataset": rec.get("datasetName") or rec.get("publisher"),
            "gbifID": rec.get("gbifID") or rec.get("key"),
        },
    }


def main() -> None:
    features, seen = [], set()
    for name in TAXA:
        key = match_taxon(name)
        if key is None:
            continue
        n = 0
        for rec in fetch_occurrences(key):
            gid = rec.get("key")
            if gid in seen:
                continue
            seen.add(gid)
            features.append(to_feature(rec, name))
            n += 1
        print(f"  {name:<24} taxonKey={key:<10} {n:>5} records")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "type": "FeatureCollection",
        "metadata": {"source": "GBIF", "updated": datetime.now(timezone.utc).isoformat(timespec="seconds")},
        "features": features,
    }))
    print(f"✓ wrote {len(features)} features → {OUT.relative_to(OUT.parents[2])}")


if __name__ == "__main__":
    main()
