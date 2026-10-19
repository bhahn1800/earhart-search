# Evidence register

The machine-readable registry is `data/sources/evidence.jsonl` (schema: `src/earhart/evidence.py`).
It is **empty at bootstrap**. This page tracks research targets and their verification status.

Source types: `PRIMARY` (original logs, telegrams, flight documents, ship deck logs, contemporary
official reports) · `CONTEMPORARY_SECONDARY` (1937 press, later official summaries by participants) ·
`MODERN_ANALYSIS` (post-hoc research, including advocacy/research organisations — **not** treated as
authoritative) · `SPECULATIVE`.
Source quality 1–5: 1 unreliable … 5 verified original document inspected by a human.

## Research targets (all UNVERIFIED — none may become a model constant yet)

| Target | Needed to pin down | Status |
|---|---|---|
| Lae departure | time + clock/zone, runway, takeoff fuel | UNVERIFIED |
| Fuel load at Lae (~1,100 US gal claimed) | original fueling record; usable vs. total; oil | UNVERIFIED |
| Howland Island position | surveyed lat/lon, datum, 1937 chart errors | UNVERIFIED |
| Itasca position(s) and times | deck log, smoke-signal timing | UNVERIFIED |
| "200 miles out" message | exact wording, time (GCT), logged by whom | UNVERIFIED |
| "must be on you but cannot see you" | exact wording, time, signal strength | UNVERIFIED |
| Altitude (~1,000 ft) | exact wording, time | UNVERIFIED |
| "gas is running low" | exact wording, time | UNVERIFIED |
| Final "157 337" LOP transmission | exact wording, time, true/magnetic, which line | UNVERIFIED |
| Electra 10E performance / R-1340 | manual figures, Earhart's aircraft modifications | UNVERIFIED |
| Weather / winds 1–2 July 1937 | synoptic data, ship obs, reanalysis (e.g. 20CR) uncertainty | UNVERIFIED |
| Itasca radio logs | scanned originals, transcription differences | UNVERIFIED |
| Navy/Coast Guard search tracks | orders, track charts, altitudes, visibility | UNVERIFIED |

## Adding a record
1. Locate the source; record title, URL/archive reference, and verbatim `original_text`.
2. Fill `observation` (what it says) separately from `interpretation` (what it might mean).
3. Give `time_system`; never convert times silently.
4. Positioned records must state `uncertainty.horizontal_nm`.
5. Leave `verified: false` until a human has compared the record to the cited source.
