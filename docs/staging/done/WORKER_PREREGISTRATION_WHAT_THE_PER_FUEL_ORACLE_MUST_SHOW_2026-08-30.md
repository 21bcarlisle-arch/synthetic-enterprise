**Severity:** RECORDED · **Lane:** W4_the_wall · **Epoch:** 3 · **Atom:** `EP13_adapter_carbon_intensity`

# PREREGISTRATION — what the EP13 per-fuel oracle bound must show

**Atom:** `EP13_adapter_carbon_intensity` (lane W4_the_wall, L2 → L3, loop_stage `build`).
**Filed:** 2026-08-30, **before** the probe's output was read. The probe
(`scratch_ep13_perfuel_probe.py`) was launched, and this file was written while it was still
loading its caches. That ordering is the whole point: a prediction filed after the answer is not a
prediction.

---

## Why this measurement, and why now

EP13's ninth pass ended by naming its next hypothesis and deliberately **not** building it:

> **NEXT, named as a hypothesis and NOT built:** NESO forecasts PER FUEL where this model reduces
> everything to a residual. Elexon FUELHH half-hourly per-fuel outturn is already in `sim/cache`
> and already read for coal, biomass and the must-run block, so an oracle rung on it would bound
> that input. It would be NOT PUBLISHABLE, same class as the input ceiling, because it is NESO's
> arithmetic — its value is as a bound. Record: frame doc section 13.

Four candidate inputs have been retired by measuring their ceiling before building them (the
biomass outage model, the merit-order programme, post-hoc recalibration, embedded generation). The
peer bound then established that the target **is** reproducible — NESO's own forecast scores
0.9711 against NESO's own outturn in 2024 where the shipped reconstruction scores 0.7425 — so the
axis is not noise and L3 needs **a new input carrying within-day timing**. Per-fuel outturn is the
next candidate, and the atom's discipline is to bound it before building it.

## What the instrument is

An **oracle** rung: hold the TRUE half-hourly per-fuel generation and put it through NESO's own
published factor table, then score the resulting shape against NESO's published outturn on the same
held-out even days through the same `neso.compare_shapes`. It fits nothing, so it costs minutes
rather than the input ceiling's 85.

Plus an **ablation ladder** inside the oracle: replace one fuel's half-hourly series by that fuel's
own **day mean** — deleting only that fuel's within-day timing, nothing else — and measure what the
correlation loses. That names *which* fuel carries the timing the reconstruction is missing.

## The predictions

Numbered so each can be refuted separately. Scored on held-out even days, 2016–2024.

1. **Coverage.** `generation_over_demand` (the held GB fuels plus AGWS wind, over Elexon demand)
   lands in **0.85–0.98**, and **falls** across the window as embedded solar — invisible to FUELHH —
   grows. If it is above 1.00 or below 0.80 the denominator is wrong and no correlation below may
   be read.

2. **It is NOT NESO's arithmetic replayed.** Bit-identical share ≈ 0, and mean absolute error
   against NESO's `actual` is **20–80 gCO2/kWh** — because NESO's number carries embedded
   generation, a loss correction and per-interconnector factors that this arithmetic omits.
   *This is the load-bearing tautology guard.* If the mean absolute error comes back under ~5 g the
   oracle IS NESO's own sum and **nothing about headroom may be quoted from it**, positive or
   negative.

3. **The oracle beats the shipped baseline, and by a lot.** Oracle correlation **> 0.90 in every
   year**, and **oracle − baseline > +0.15 in 2024**, the year that has held this level for nine
   passes. Reason: the fuel mix is the physical driver of intensity, and the peer bound already
   proved the within-day axis carries recoverable signal.

4. **The advantage is within-day.** Oracle − its own day mean **> 0.10**, and the shuffled null
   collapses to within 3/√n of zero.

5. **CCGT carries the most within-day timing.** In the ablation ladder, flattening CCGT costs more
   correlation than flattening any other single fuel in **2024**; COAL is large in 2016–2019 and
   near zero by 2024; BIOMASS is the smallest of the carbon-bearing fuels throughout.

## The named risk, which is how prediction 3 could fail honestly

The oracle omits **embedded solar** and **interconnector imports**. Embedded solar is a
midday-shaped term that depresses NESO's published intensity exactly when this oracle cannot see
it, so a systematic within-day phase error is available to spoil the correlation. If prediction 3
fails while prediction 2 holds, the reading is **not** "per-fuel is uninformative" — it is "per-fuel
*without an embedded term* is uninformative", and that is a different retirement with a different
consequence for L3.

## What follows either way

- **Predictions 2–4 hold:** per-fuel outturn is the first input in five to show real headroom on
  this axis. L3's build becomes finding a *publishable proxy* for whichever fuel prediction 5 names
  — the oracle itself is not publishable, being NESO's factor table on metered truth.
- **Prediction 3 fails with 2 holding:** per-fuel is the **fifth** candidate retired by measuring
  its ceiling first, subject to the embedded-solar caveat above.
- **Prediction 2 fails:** the instrument is a tautology and reports nothing. That result gets
  written down as such, and the ablation ladder — which is a fact about the grid rather than about
  the reconstruction — is the only part that survives.

**No level move follows from any outcome here.** LAW A. This is a diagnostic; the exit axis is
unchanged and is the director's.

---

# SCORED, 2026-08-30 — four right, one wrong, one framing correction

Written after the run, against the predictions above, which were not edited. Artefact:
`docs/observability/ep13_per_fuel_oracle_bound.json`.

| year | baseline | **oracle** | oracle − baseline | oracle day-mean | gen/demand | MAE g | dominant |
|---|---|---|---|---|---|---|---|
| 2019 | 0.8819 | **0.9665** | +0.085 | 0.8268 | 0.970 | 14.7 | CCGT |
| 2020 | 0.8737 | **0.9634** | +0.090 | 0.8369 | 0.988 | 11.7 | CCGT |
| 2021 | 0.9078 | **0.9780** | +0.070 | 0.8419 | 0.964 | 16.9 | CCGT |
| 2022 | 0.8698 | **0.9823** | +0.113 | 0.8850 | 1.063 | 14.4 | CCGT |
| 2023 | 0.7973 | **0.9434** | +0.146 | 0.8602 | 0.911 | 30.3 | CCGT |
| **2024** | **0.7425** | **0.9352** | **+0.193** | 0.8185 | 0.874 | 33.1 | **CCGT** |

Ablation — correlation lost when one fuel's within-day timing is deleted:

| year | COAL | **CCGT** | OCGT | BIOMASS | WIND |
|---|---|---|---|---|---|
| 2019 | −0.0137 | **−0.0787** | +0.0001 | −0.0008 | −0.0314 |
| 2021 | −0.0106 | **−0.0766** | +0.0002 | −0.0001 | −0.0257 |
| 2023 | −0.0034 | **−0.0566** | +0.0000 | +0.0001 | −0.0000 |
| 2024 | −0.0013 | **−0.0949** | −0.0001 | −0.0003 | +0.0024 |

**1. Coverage — WRONG, and the bar was the thing that was wrong.** I predicted 0.85–0.98 and said
above that a value over 1.00 meant the denominator was broken and nothing below it could be read.
2022 came in at **1.063**. The data is right and my bar was wrong: GB was a net *exporter* in 2022,
so generation legitimately exceeded GB demand. The prediction that the ratio would *fall* across
the window held (0.970 → 0.874, embedded solar growing). The control that shipped is keyed to the
property — a sum of generation is near demand, ceiling 1.20 — and not to the range I guessed, and
`test_the_coverage_bound_admits_a_NET_EXPORT_year` pins that open at 1.063 precisely so a later
pass cannot re-tighten it into going red when the world gets more honest.

**2. Not a tautology — RIGHT.** Bit-identical share 0.000, mean absolute error 11.7–33.1 g against
NESO's outturn. I predicted 20–80 g; the true range is lower and still an order of magnitude clear
of the 2.0 g bar. This is not NESO's arithmetic replayed.

**3. Oracle beats the baseline — RIGHT, both legs.** Oracle > 0.90 in every year (0.9352–0.9823),
and 2024's margin is **+0.193**, over the predicted +0.15.

**4. The advantage is within-day — RIGHT in 2024, OVERSTATED as a general claim.** I predicted
> 0.10 and implied every year. Measured: 0.117 (2024), 0.129 (2019), 0.127 (2020), 0.136 (2021),
but 0.097 (2022) and 0.083 (2023) fall under my own bar. All six clear the shipped 0.01 materiality
margin comfortably. The null collapses everywhere (−0.009 to +0.001).

**5. CCGT — RIGHT, decisively, and this is the finding.** CCGT's ablation costs 0.052–0.095 where
coal costs 0.001–0.014 and biomass 0.0003. Coal is large early (−0.0137 in 2019) and gone by 2024
(−0.0013), as predicted. Biomass is the smallest carbon-bearing fuel throughout, as predicted.

## A framing correction to the "what follows" above, made beside the claim and not by revising it

The section above says a failure of prediction 3 would make per-fuel "the **fifth** candidate
retired by measuring its ceiling first". **That was too strong and I should not have written it.**
This instrument is *handicapped* — it has no embedded-generation term, no interconnector term and
no OIL or OTHER — so it does not bound the per-fuel input from above. It is an **attainment floor**,
not a ceiling, and a negative from it would have retired nothing. The four previous retirements
were all made on genuine ceilings and that word does not transfer. The error does not touch the
result, because the result is a positive and a floor is the right instrument for a positive: a
handicapped model that still reaches 0.9352 has proved the input carries the information.

## What this hands to L3

The atom's diagnosis since 2026-08-27 has been *L3 needs a new input carrying within-day timing*,
confirmed by the peer bound. This names it: **the within-day timing is in CCGT**, the one fuel the
shipped reconstruction never observes and instead infers from a residual. The oracle closes 84% of
the distance from the baseline to the peer bound's 0.9711 in 2024.

It also explains the decay nobody had accounted for. The baseline falls 0.88 → 0.74 across the
window while WIND's ablation cost collapses from −0.031 to ~0 and CCGT's grows to its largest.
The within-day information *migrated* into the one fuel the model cannot see — so the
reconstruction did not get worse, the grid moved the answer out of its reach.

**Still no level move.** LAW A. The build this licenses is a *publishable proxy* for within-day
CCGT dispatch; the oracle itself may never be published, and `oracle_reaches_the_published_feed`
is False by AST walk.
