# 🦎 ANOLE-WATCH

**Adaptive radiation, one islet at a time.**

ANOLE-WATCH maps the *Anolis marmoratus* species complex across Guadeloupe's main islands and satellite islets — La Désirade, Petite Terre, Marie-Galante, Les Saintes, Îlet Kahouanne. Recent taxonomic work split what used to be one wildly variable lizard into several species, each stranded on its own patch of volcanic or limestone rock. This repo pulls the public occurrence records, pins them to the islets, and (eventually) asks what the habitat on each islet looks like from orbit.

Inspired by spotting anoles near the *Death in Paradise* filming locations — and by NatGeo's August 2026 island-evolution coverage.

> Part of the GeoAI & Remote Sensing Lab · sibling of [ALPINE-WATCH](https://github.com/bdgroves/Alpine-watch)

---

## Status: 🌱 scaffold

| Piece | State |
|---|---|
| GBIF occurrence fetch (`src/fetch_occurrences.py`) | ✅ written — runs in GitHub Actions |
| Weekly auto-update workflow | ✅ wired |
| Leaflet map (`docs/index.html`) | ✅ basic — colors points by species |
| iNaturalist research-grade fetch | ⬜ next |
| Sentinel-2 land cover per islet (Earth Engine) | ⬜ later |
| Islet explainer panel ("why these rocks made new species") | ⬜ later |

## Target taxa

| Species | Where |
|---|---|
| *Anolis marmoratus* | Basse-Terre / Grande-Terre (many subspecies) |
| *Anolis ferreus* | Marie-Galante |
| *Anolis terraealtae* | Les Saintes (Terre-de-Haut / Terre-de-Bas) |
| *Anolis kahouannensis* | Îlet Kahouanne |
| *Anolis chrysops* | Petite Terre |
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
