# earhart-search

Open-source, reproducible computational research toward a ranked set of search areas for Amelia
Earhart's Lockheed Electra 10E (disappeared 2 July 1937). The project is hypothesis-neutral: crash
near Howland, continuation along the 157/337 line of position, Nikumaroro and other plausible
scenarios compete, and nothing is tuned to reach a famous location.

**Status: bootstrap.** Geometry (`coordinates.py`) and the evidence-registry schema exist. There is
no simulation and no answer yet; no historical value is asserted until its source is recorded.

## Principles
Evidence before theory · primary sources first · no silent conversion of claims to facts ·
every parameter has value/units/uncertainty/source/quality/notes · observed ≠ inferred ·
deterministic seeded simulation · provenance for all inputs. See [CLAUDE.md](CLAUDE.md).

## Layout
`src/earhart/` library · `data/` inputs (sources, raw, weather, bathymetry, search_coverage) ·
`docs/` methodology, evidence register, assumptions, hypotheses · `outputs/` generated maps/KML/reports ·
`tests/`.

## Quick start
```
uv sync --extra gis --extra viz
uv run pytest
```
Python 3.12+ (pinned via `.python-version`).

## Roadmap
1 Geometry ✅ (partial) · 2 Aircraft/fuel · 3 Navigation · 4 Monte Carlo · 5 Probability map/KML ·
6 Search coverage · 7 Computer vision (blocked on 3).

Contributions: add evidence with verbatim quotes and citations; challenge assumptions in `docs/assumptions.md`.
