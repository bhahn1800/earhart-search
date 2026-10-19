# Assumptions & unresolved parameters

No historical value is asserted here. Each row is an *unresolved parameter* until evidence is
registered. "Sensitivity" is a prior guess at influence and must be replaced by measured sensitivity
once the Monte Carlo engine exists.

| Parameter | Type | Units | Required evidence | Expected sensitivity | Status |
|---|---|---|---|---|---|
| fuel at departure | distribution | US gal | Lae fueling records, tank capacities | High | UNRESOLVED |
| taxi/takeoff fuel | distribution | US gal | engine run-up/takeoff data | Low | UNRESOLVED |
| cruise burn rate | distribution | gal/h | in-flight logs, prior legs, Lockheed/P&W data | High | UNRESOLVED |
| true airspeed | distribution | kt | prior-leg ground speeds, power settings | High | UNRESOLVED |
| altitude profile | scenario | ft | radio statements, flight plan | Medium | UNRESOLVED |
| mixture/power changes | scenario | — | pilot statements | Medium | UNRESOLVED |
| reserve / usable-fuel floor | distribution | gal | tank unusable quantity | Medium | UNRESOLVED |
| wind field | distribution | kt, deg | reanalysis + ship reports | High | UNRESOLVED |
| dead-reckoning error | distribution | nm | Noonan's method/track record | High | UNRESOLVED |
| celestial fix error | distribution | nm | instrument, sight quality, sun elevation | High | UNRESOLVED |
| clock (chronometer) error | distribution | s | rate/watch-check records | Medium | UNRESOLVED |
| LOP orientation error | distribution | deg | observation method | Medium | UNRESOLVED |
| LOP offset (perpendicular) | distribution | nm | derived from fix error | High | UNRESOLVED |
| position along LOP | distribution | nm | DR/radio information | High | UNRESOLVED |
| true vs. magnetic "157/337" | discrete | — | variation, Noonan's practice | High | UNRESOLVED |
| search duration | scenario | min | fuel state + decision model | High | UNRESOLVED |
| crew decision/behaviour priors | configurable prior | — | none (documented, swept) | High | UNRESOLVED |

## Modelling conventions (these are choices, not claims)
- WGS84 geodesics; 1 nm = 1852 m. 1937 charts used other datums — datum shift is an uncertainty term.
- LOP *orientation* error and *position-along-LOP* uncertainty are separate parameters and never merged.
- Behavioural priors are exogenous inputs, swept in sensitivity analysis, never tuned to a target location.
