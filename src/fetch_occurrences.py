"""Fetch Anolis occurrence records for Guadeloupe from GBIF → GeoJSON.

Writes docs/data/occurrences.geojson for the Leaflet map.
"""
from __future__ import annotations

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

GBIF = "https://api.gbif.org/v1"
OUT = Path(__file__).resolve().parents[1] / "docs" / "data" / "occurrences.geojson"

# Island species first, catch-all A. marmoratus LAST: a record filed under an old
# subspecies name (e.g. A. marmoratus desiradei) can match both taxa, and dedup keeps
# the first hit — so the specific islet species should win.
TAXA = [
    "Anolis ferreus",
    "Anolis terraealtae",
    "Anolis kahouannensis",
    "Anolis chrysops",
    "Anolis desiradei",
    "Anolis marmoratus",
]

# Guadeloupe archipelago bounding box (lon/lat), incl. Marie-Galante, Les Saintes, La Désirade
BBOX_WKT = "POLYGON((-61.90 15.80,-60.95 15.80,-60.95 16.55,-61.90 16.55,-61.90 15.80))"
PAGE = 300
MAX_PER_TAXON = 5000

# ── Quality flags ────────────────────────────────────────────────────────────
# Records are flagged, never deleted, so the map can show what was set aside.
# 1. "centroid": GBIF records with no real locality often get parked on the
#    Guadeloupe centroid near Pointe-à-Pitre (16.20 N, 61.54 W).
# 2. "off-island": each islet species is endemic to one place. A record far
#    from home is a georeferencing error, e.g. Petite Terre and Les Saintes
#    BOTH have islands named Terre-de-Haut and Terre-de-Bas, and some
#    A. chrysops (Petite Terre) records were placed on Les Saintes.
CENTROID = (16.20, -61.54)
HOME = {  # species: (lat, lon, radius_km)
    "Anolis ferreus":       (15.94, -61.27, 15),   # Marie-Galante
    "Anolis terraealtae":   (15.865, -61.60, 8),   # Les Saintes
    "Anolis desiradei":     (16.315, -61.05, 8),   # La Désirade
    "Anolis chrysops":      (16.175, -61.115, 3),  # Îles de la Petite Terre
    "Anolis kahouannensis": (16.38, -61.765, 5),   # Îlet à Kahouanne + Tête à l'Anglais
}


def km_between(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return 111.2 * math.hypot(lat1 - lat2, (lon1 - lon2) * math.cos(math.radians((lat1 + lat2) / 2)))


def qa_flag(taxon: str, lat: float, lon: float) -> str | None:
    if abs(lat - CENTROID[0]) < 0.006 and abs(lon - CENTROID[1]) < 0.006:
        return "centroid"
    if taxon in HOME:
        hlat, hlon, r = HOME[taxon]
        if km_between(lat, lon, hlat, hlon) > r:
            return "off-island"
    return None


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
            "qa": qa_flag(query_name, rec["decimalLatitude"], rec["decimalLongitude"]),
        },
    }


def write(features: list[dict]) -> None:
    flagged = {}
    for f in features:
        if f["properties"].get("qa"):
            flagged[f["properties"]["qa"]] = flagged.get(f["properties"]["qa"], 0) + 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "type": "FeatureCollection",
        "metadata": {"source": "GBIF", "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "flagged": flagged},
        "features": features,
    }))
    print(f"✓ wrote {len(features)} features, flagged {flagged} → {OUT.relative_to(OUT.parents[2])}")


def reflag() -> None:
    """Re-apply quality flags to the existing file without refetching."""
    gj = json.loads(OUT.read_text())
    for f in gj["features"]:
        lon, lat = f["geometry"]["coordinates"]
        f["properties"]["qa"] = qa_flag(f["properties"]["taxon"], lat, lon)
    write(gj["features"])


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

    write(features)


if __name__ == "__main__":
    reflag() if "--reflag" in sys.argv else main()
