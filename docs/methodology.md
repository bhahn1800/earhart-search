# Methodology

## Question
Given reliable evidence available at the time of the last confirmed transmission, where is the
aircraft most likely to have ended up? (Not answered at bootstrap.)

## Pipeline
1. **Evidence** (`evidence.py`, `data/sources`): sourced, typed, quality-rated records.
2. **Geometry** (`coordinates.py`): WGS84 geodesics, routes, LOP construction.
3. **Aircraft/fuel** (`aircraft.py`, `fuel.py`): parameters as distributions; unresolved where unsourced.
4. **Navigation** (`navigation.py`, `celestial.py`): DR, wind, fix, clock, LOP errors. LOP orientation
   uncertainty is separate from position uncertainty along the LOP.
5. **Monte Carlo** (`simulation.py`): ≥10⁶ trajectories, seeded `numpy.random.Generator`; each draw
   samples fuel, burn, airspeed, wind, nav error, LOP offset/angle, along-LOP position, search duration,
   crew decision. Behaviour classes: local Howland search, 337° and 157° continuation, other patterns,
   fuel exhaustion. Behavioural priors are inputs, swept for sensitivity.
6. **Probability map** (`probability.py`, `gis.py`): 50/80/95 % credible regions (highest-density);
   GeoJSON, GeoTIFF, KML/KMZ, PNG. Reference layers (Howland, Lae, LOP, historical search areas,
   Nikumaroro, modern targets) styled neutrally.
7. **Search coverage** (`search_coverage.py`): per-sweep detection probability by method (air, surface,
   sonar, expedition); posterior = prior × (1 − P(detect | searched)). "Searched" ≠ "eliminated".
8. **Computer vision** (later): ranks anomalies for human review only.

## Reproducibility
Seeded RNG; configs versioned; every parameter cites evidence ids; outputs record git hash + seed.

## Sensitivity
Report which assumptions materially move the 50/80/95 % regions (one-at-a-time and global sweeps).

## Status
Implemented: `coordinates.py`, evidence schema. All else pending.
