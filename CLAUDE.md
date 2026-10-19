# earhart-search — research principles

Goal: a reproducible probabilistic reconstruction of the final flight of Earhart and Noonan
(Lockheed Electra 10E, 2 July 1937), producing ranked lat/lon search areas. This is NOT an
effort to prove a predetermined theory. Crash-and-sink near Howland, continuation along the
157/337 LOP, Nikumaroro, and other physically plausible scenarios are competing hypotheses.

## Principles
1. Evidence before theory.
2. Primary sources outrank secondary sources.
3. Never silently convert an uncertain historical claim into a fact.
4. Every important model parameter carries: value or distribution, units, uncertainty, source,
   source quality, notes. If evidence is inadequate, create an *unresolved* parameter and document
   what evidence is needed. Do not invent performance numbers.
5. Keep observed evidence separate from inferred values.
6. Simulations are deterministic given a random seed.
7. Preserve competing hypotheses.
8. Never tune assumptions because they yield a famous proposed location.
9. Maintain provenance for every important input.
10. Flag assumptions that materially change the resulting search area (sensitivity analysis).

## Rules for working here
- Do not hard-code historical claims (positions, fuel, times, quotes) until the source is recorded
  in `data/sources/evidence.jsonl` / `docs/evidence-register.md`. Never fill gaps with guessed values.
- Modern Earhart research organisations are not authoritative; classify by source type.
- Behavioural priors (search pattern, crew decision) must be independently configurable and documented.
- "Searched" never means "eliminated": model detection probability (Phase 6).
- Maps must not visually favour any hypothesis unless the model supports it.
- Computer vision (Phase 7) is off-limits until the navigation model works; it ranks anomalies for
  human review and never asserts an anomaly is the aircraft.
- Python 3.12+, managed with `uv`. Run tests: `uv run pytest`. Source in `src/earhart/`.
- Azimuths are true unless stated; true-vs-magnetic of the historical "157/337" is unresolved.

## Hand-off
Follow the global multi-model hand-off protocol (append "Suggested next hand-off" after substantive work).
