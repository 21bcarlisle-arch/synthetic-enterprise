# WORKER FINDING — the ageing dimension's resolution is the harness's calendar

**Date:** 2026-08-10 · **Found by:** worker tick running Expert Hour #8 on `H27_payment_belief_gap` (2→3)
**Mints:** `D25_ageing_resolution_is_the_harness_calendar` (the reshape, L0)
**Verdict:** **HELD AT L2.** Eight Hours, eight defects, and this is again the tick that changed the instrument.
**R12:** nothing was tuned. Every published figure is bit-identical before and after — n=600 seed 7:
ageing `0.06847916348907757`, detection `0.012100259291270527`, latency `2.132353`, belief `0.1337579617834395`.

## Why the Hour ran here

Hour #7 left three leads in order. The first was *"the other grid readings — whether `ageing`/`belief`
are as_of-quantised is a measurement nobody has taken"*. It is the defect, in a sharper form than the
lead guessed: the ageing dimension's grid is not made of dates at all.

## The finding — the headline cannot see a week of over-ageing (observed, R9)

`ageing`'s headline is **buckets of ordinal displacement**, so a dating error is visible only where it
carries an invoice **across** a 30/60/90 boundary. And every truly-overdue invoice in this scenario is
30, 51 or 72 days overdue at `as_of` — three distances, and all three are arithmetic over harness
constants:

```
AS_OF_BUFFER_DAYS + PERIOD_SPACING_DAYS * i   for i in range(N_PERIODS)   ==   {30, 51, 72}
```

Measured against a **new declared counterfactual company** — `organ_terms_drift_days`, the supplier
holding the wrong payment terms on every account, so it dates every debt `k` days out; the world and
the truth-side bucket rule (`_ageing_bucket`, atom D21) are untouched, so every movement under it is
the company's dating moving. n=300, **bit-identical on seeds 7 / 11 / 23**:

| company drift | what the company believes | ageing headline (seed 7 / 11 / 23) |
|---|---|---|
| `0` (shipped) | dates every debt right | 0.078649 / 0.146341 / 0.078706 |
| **−1 … −8 d** | **every debt 1–8 days OLDER** | **0.078649 / 0.146341 / 0.078706** — unchanged |
| −9 d | every debt 9 days older | 0.231463 / 0.314688 / 0.212320 |
| **+1 d … +12 d** | every debt 1–12 days younger | **0.226343 / 0.288139 / 0.253083 — one number** |
| +13 d | every debt 13 days younger | 0.378304 / 0.392306 / 0.403526 |

Two things, and the second is as bad as the first:

- **An 8-day blind band, in the direction that sends the letter.** A supplier over-ageing every debt by
  a working week is bit-identical to one dating every debt perfectly. Over-ageing is the direction that
  posts an early dunning letter to a customer who does not owe it yet.
- **A 12-day collapse the other way.** A company 1 day out and one 12 days out publish one figure, so a
  movement in this headline cannot be read as days at all.

The asymmetry — 1 day visible one way, 9 the other — is an accident of where three due dates fell.

**It is a blindness, not a dead probe.** The counterfactual company is genuinely different while the
ageing headline sits still: the DETECTION dimension of the same instrument moves on every one of the
drifts ageing cannot see. That assertion is in the test, so a future inert drift parameter cannot pass
this off as "no defect".

### Why it survived seven Hours and D23's own register

D23 (Hour #7) named this exact class — *a reading taken on a grid of the harness's own making is
quantised to that grid, and the resolution is a property of the harness, not of the company being
graded* — and closed it with `ORGAN_QUERY_GRID`, **keyed to the two readings off the reconciliation
candidate-date grid**. The ageing dimension's grid is not made of dates: it is where the population
SITS relative to the bucket boundaries. Nothing reached it.

That is the **fourth escape of a register's own keying** in this one instrument: D19 out of the
detection scorers, D22 out of the rate-shaped dimensions, D23's own register out of the non-date grids.

## The class control (R10 — the class, not the instance)

`DIMENSION_DRIFT_RESOLUTION`, with the keying removed:

- **keyset DERIVED** from what `score_triad` actually publishes — a published dimension with no entry
  **RAISES**, and so does an entry for a dimension nobody publishes (an unreachable entry reads exactly
  like a clean one);
- each entry is re-scored **through that dimension's own shipped scorer** (R15 independence) against the
  declared counterfactual, on every seed — the claims are structural, so a band holding on one seed and
  not another is refused;
- the counterfactual is a **declared `score_triad` parameter**, not a test monkeypatch (the D20 rule).

**Three states, differential on purpose** — a register whose entries all land on one side is a blanket
claim wearing a register's clothes:

| dimension | state | measured |
|---|---|---|
| `ageing` | on-path, **BLIND** | blind to −8…−1, collapse (+1, +12) — **the defect**, owes D25 |
| `detection` | on-path, **BLIND** | blind to +1, sees −1 |
| `detection_latency` | on-path, **SIGHTED** | sees every drift both ways (D23's daily grid) |
| `belief` | **OFF path** | organ counts failure EVENTS, never the ledger's dating |
| `belief_population_mix` | **OFF path** | same organ, same reason |

**The differential is the evidence.** The same one-day company error is seen by exactly one of
`ageing`/`detection` in *each* direction — ageing sees +1 and is blind to −1, detection the reverse.
That localises the defect to the population's **placement** rather than to one formula, and it forbids
reading either headline as covering the other's blind side (the D16 rule: aligned denominators are
still different questions).

**The off-path state is checked, not believed.** That exemption shape is what hid D21 for five Hours,
so an off-path entry must NAME a probe that does move the dimension and the sweep must MEASURE it
(both belief dimensions: their own indiscriminate degenerate, via `HEADLINE_DIRECTION_COVERAGE`) — plus
a source assertion that `_arrears_risk_belief` really does not read the ledger's dating.

### Caught by the control on its own first draft

With only "declared-invisible must be unmoved" and "declared-visible must move", **under-stating the
band passed silently**: drop `-1` from the ageing band and every declaration still held, while
`ageing_resolution_caveat` — which *interpolates* that band — went on publishing a narrower blind spot
than the instrument has. A caveat that can only shrink is the decay this register exists to stop. The
band must now be **exact**: any measured-unmoved drift not declared is a violation.

### R15, both ways

- **Eight register mutations fire by name**: understated band; overstated sight; a collapse checked
  against readings nobody took; a collapse that is really an invisibility; an unowned hole; a rotted
  off-path claim; a probe-less exemption; an all-blind register.
- A dropped or invented dimension **RAISES** rather than passing.
- An inert counterfactual (a runner ignoring the drift) trips the **vacuity guard** — the fail-silent
  shape this instrument has now produced six times, twice inside the control written to close the one
  before.
- **SOURCE mutation**: dropping the drift inside `score_triad` fires **four** tests, the first of which
  names the register. File restored and verified md5-identical (`9c6cbb34ee413e3872c49e2285cb634a`).

## What was NOT done, and why

The population is untouched. Giving the ageing dimension invoices at distances that can resolve a
dating error moves every published ageing figure on this pair, and R12 forbids reshaping a measure
because its value looks wrong — the value is fine; what was missing is what it can resolve. That is
atom **D25**, minted at L0.

## Why still L2

Eight consecutive Hours, eight defects, none predicted by the Hour before it, and the arrival rate is
not falling. Hour #4's stated-in-advance criterion — **two consecutive clean Hours** — has still not
been approached, and this is again the tick that changed the instrument.

**Hour #9 leads, in order:**
1. `belief` and `belief_population_mix` are OFF this drift's path, so their smallest visible company
   error is still unmeasured — **no counterfactual organ knob for the arrears-severity belief exists in
   this harness at all**, which is a hole in the same shape as the one this Hour closed.
2. The pinned generated value Hour #7 left: `assert c["n_recon_detected_undated"] == 0`.
3. Whether the other dimensions' normalisation notes have the same gap between what they DENY and what
   they ESTABLISH.

## Evidence

- `tools/couple_w2_11_d5.py` — `organ_terms_drift_days`, `DIMENSION_DRIFT_RESOLUTION`,
  `measure_dimension_drift_resolution`, `check_dimension_drift_resolution`,
  `ageing_resolution_caveat`, and the control printed in the CLI (a control living only in the tests is
  one the reader about to quote an ageing displacement never meets).
- `tests/tools/test_couple_w2_11_d5.py` — 12 new tests, **271 green** (was 244).
- **153 green** across every sibling coupled-pair suite (`test_couple_cohort`, `test_couple_fabric`,
  `test_couple_supply_start`, `test_couple_w2_4_c6`, `test_couple_w2_5_c7`,
  `test_d6_ageing_metric_shape`, `test_generate_proof_coupled_gaps`, `test_live_payment_triad`,
  `test_gap_ledger_reconciler`).
