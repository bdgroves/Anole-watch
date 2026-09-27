# 🦎 ANOLE-WATCH

**Adaptive radiation, one islet at a time.**

ANOLE-WATCH maps the *Anolis marmoratus* species complex across Guadeloupe's main islands and satellite islets — La Désirade, Petite Terre, Marie-Galante, Les Saintes, Îlet Kahouanne. Recent taxonomic work split what used to be one wildly variable lizard into several species, each stranded on its own patch of volcanic or limestone rock. This repo pulls the public occurrence records, pins them to the islets, and (eventually) asks what the habitat on each islet looks like from orbit.

Inspired by spotting anoles near the *Death in Paradise* filming locations — and by NatGeo's August 2026 island-evolution coverage.

**🌐 Live site: [bdgroves.github.io/Anole-watch](https://bdgroves.github.io/Anole-watch/)** · [explorer map](https://bdgroves.github.io/Anole-watch/map.html)

> Part of the GeoAI & Remote Sensing Lab · sibling of [ALPINE-WATCH](https://github.com/bdgroves/Alpine-watch)

---

## Status: 🌱 scaffold

| Piece | State |
|---|---|
| GBIF occurrence fetch (`src/fetch_occurrences.py`) | ✅ written — runs in GitHub Actions |
| Weekly auto-update workflow | ✅ wired |
| Story page (`docs/index.html`) — "Six islands, six lizards" | ✅ reads live data, falls back to a snapshot |
| Leaflet explorer map (`docs/map.html`) | ✅ basic — colors points by species |
| Quality flags: centroid-parked and off-island records flagged, shown hollow on the map, left out of counts | ✅ |
| iNaturalist | ✅ already covered: iNat research-grade observations flow into GBIF |
| Sentinel-2 land cover per islet (Earth Engine) | ⬜ later |
| Islet explainer panel ("why these rocks made new species") | ⬜ later |

## Data quality notes

- **The centroid problem.** 69 records sit exactly on 16.20 N, 61.54 W, a generic "somewhere in Guadeloupe" point that records fall back to when nobody wrote down an exact locality. They're flagged `centroid`.
- **Two islands called Terre-de-Haut.** Petite Terre's islets are Terre-de-Haut and Terre-de-Bas, the same names as the main islands of Les Saintes. Some *A. chrysops* (Petite Terre) records were placed on Les Saintes, 60 km away. Island endemics recorded outside their home island are flagged `off-island`.
- Re-apply flags without refetching: `python src/fetch_occurrences.py --reflag`

## Target taxa

| Species | Where |
|---|---|
| *Anolis marmoratus* | Basse-Terre / Grande-Terre (many subspecies) |
| *Anolis ferreus* | Marie-Galante |
| *Anolis terraealtae* | Les Saintes (Terre-de-Haut / Terre-de-Bas) |
| *Anolis kahouannensis* | Îlet à Kahouanne + Tête à l'Anglais |
| *Anolis chrysops* | Petite Terre (its islets are also named Terre-de-Haut / Terre-de-Bas) |
| *Anolis desiradei* | La Désirade |

Names follow the current split; GBIF may still file some records under *A. marmoratus* subspecies — the fetch script keeps the raw `scientificName` so we can sort that out later.

## Run it

```bash
pixi install
pixi run fetch      # writes docs/data/occurrences.geojson
pixi run serve      # http://localhost:8000
```

Turn on **GitHub Pages → Deploy from branch → `main` / `docs`** to publish the map.

## Data sources

- **GBIF** occurrence API — https://www.gbif.org/developer/occurrence
- **iNaturalist** API (planned) — https://api.inaturalist.org/v1/docs/
- **Sentinel-2 SR Harmonized** via Google Earth Engine (planned)

## Build prompt (for the next session)

> Help me build out ANOLE-WATCH. Add iNaturalist research-grade records alongside GBIF, dedupe them, and assign each record to its islet with a simple polygon layer. Then add a Sentinel-2 land-cover summary per islet (Earth Engine) and a side panel explaining why isolation on these specific islets produced separate species. Match the ALPINE-WATCH dark navy/teal style.
