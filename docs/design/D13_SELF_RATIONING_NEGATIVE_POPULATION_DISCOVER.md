# DISCOVER — the self-rationing pairs need a negative population, and it cannot be borrowed

**Atom:** `D13_self_rationing_negative_population_discover` · **Stage:** DISCOVER (doc-only, no build)
**Minted:** 2026-08-09 by the `D12_detection_cell_grid_is_recall_only` build
**DISCOVER CLOSED:** 2026-08-09 · **verdict: the mint's premise is FALSE, and the two pairs are not one problem**
**Owns the debt registered against:** `couple_w2_5_c7.detection`, `couple_w2_8_c10.detection`
in `tools.couple_w2_11_d5.DETECTION_DIRECTION_CONTRACT`

---

## VERDICT (read this first)

The mint asked whether a settled-fact negative population exists for self-rationing at all, and
pre-authorised **"no second direction is publishable here"** as a legitimate finding.

**It is not the finding.** The mint's stated reason — that *"a household that is **not**
self-rationing" is a continuum the harness labels by threshold* — **is false in the code for both
pairs**. Both worlds carry a **discrete, generative** negative label. Neither needs a threshold
invented to name its must-not-flag set.

But the two pairs then diverge completely, and lumping them into one atom was the actual error:

| | **W2_8 ↔ C10** (self-rationing) | **W2_5 ↔ C7** (life events) |
|---|---|---|
| settled-fact negative? | **yes** — `label == NOT_RATIONING`, a Bernoulli onset outcome | **yes** — `income_stress == LOW` throughout the year, a state-machine value |
| denominator choice swings the rate? | **no** — 0.0000 either way | **yes — ×2.88**, the D11 shape, reproduced |
| is the second direction worth publishing? | **no — it is VACUOUS**, and publishing it would over-claim | **yes**, once the exclusion is a named R13 choice |
| why | the world contains **no hard negatives at all** | the ambiguity is real but **discrete and enumerable** |

So the register's two entries are debt for **opposite reasons**, and one atom cannot pay both.

---

## Q1. Is there a settled-fact negative for self-rationing at all? — **Yes, in both.**

**W2_8.** `simulation/self_rationing.py` draws rationing onset as a **Bernoulli** against a
budget-derived propensity (`onset = _substream(base_seed, "onset").random() < prop`) and stamps
`RationingLabel.SELF_RATIONING` / `NOT_RATIONING`. The *propensity* is continuous; the **label is
not**. "This household is not self-rationing" is exactly as settled a fact as the payment pair's
"the cash arrived" — it is a generative outcome the harness already holds as the answer key, not a
threshold the harness applies after the fact.

**W2_5.** `simulation/life_events.py` runs a discrete `income_stress` state machine over
`LOW / MODERATE / HIGH`. "This household sat at LOW income stress at both ends of the year" is a
settled state, not a cut on a continuum.

The floor (`TDCV_LOW_FLOOR_KWH`) *is* a threshold — but it selects the **truth** set
(`is_silent_hardship`), which was never in dispute. It plays no part in defining the negative.

## Q4. Three populations, not two — **stated explicitly, and the third is non-empty in both.**

Measured at the atom's own default population (`n=4000` households, seedless/deterministic):

```
W2_8 ↔ C10                       n = 4000
  must-flag   (is_silent_hardship)                    192
  NEITHER     (truly rationing, but ABOVE the floor)   56   <- flagging is NOT wrong
  must-not-flag (label == NOT_RATIONING)             3752
```

The 56 are real rationers excluded from `truth_set` only by the floor criterion. Flagging one is
**not an error** — the detector is right about them. The coupler's existing
`false_positive_rate` stat divides by `n_customers - len(truth_set)`, which sweeps all 56 into the
negatives: **the D11 denominator defect is present in `tools/couple_w2_8_c10.py` today.** It changes
no published number (see Q3) but it is the wrong set, and it should be excluded on principle rather
than because it currently costs nothing.

```
W2_5 ↔ C7                        n = 2000 customers × 10 years = 20000 instances
  must-flag   (distress event dated in that year)     1099
  NEITHER     (no event, but stress carried in)       2772   = 14.7% of the naive denominator
  must-not-flag (LOW at both ends)                   16129
```

The NEITHER set here is the mechanism the mint missed: `income_stress` is **persistent**. A job loss
in 2019 leaves the household at HIGH until an `income_recovery` event fires, and
`simulation.payment_timing` keeps mapping that stress onto LATE / DD_FAILED records for as long as it
lasts. A C7 flag in 2020 on such a household is **correct** — the household really is in distress —
but the naive denominator scores it a false positive.

## Q3. Sensitivity before commitment — **run, and it separates the two pairs decisively.**

**W2_8: no sensitivity at all, because the numerator is empty.**

```
FP rate, settled negative (label == NOT_RATIONING):  0/3752 = 0.0000
FP rate, naive (universe − truth_set):               0/3808 = 0.0000
```

The denominator choice cannot move a rate of zero. Probing why: of 3752 non-rationers, **0 have any
consumption drop at all** — `generate_self_rationing_state` returns `observed == healthy` exactly on
the not-onset branch — and **0 are flaggable under *any* of the five weather factors** the coupler
can draw. The zero is **structural, not creditable**: no drop-based detector can false-positive in
this world, because the world never presents a non-rationer with a drop. There are no house moves,
no efficiency retrofits, no vacancies, no behavioural change in a mild winter.

**W2_5: the D11 shape, reproduced, and stable under scale.**

| candidate negative | fp | denominator | rate |
|---|---|---|---|
| A — naive `universe − truth` | 3140 | 18901 | **0.1661** |
| B — exclude carried-HIGH | 2674 | 17937 | 0.1491 |
| C — require LOW at both ends | 929 | 16129 | **0.0576** |

**A → C swings the measured false-flag rate by ×2.88**, with company behaviour held literally fixed —
the same defect D11 hit (×10.5) and D12 hit (0.1031 → 0.0584). It is not a small-sample artefact;
re-run across population sizes the factor is flat:

```
  5,000 instances : 0.1752 -> 0.0626  (×2.80)
 20,000 instances : 0.1661 -> 0.0576  (×2.88)
 50,000 instances : 0.1621 -> 0.0562  (×2.89)
```

**But — and this is the finding that overturns the mint — the choice is DISCRETE, not a continuum.**
There are exactly three candidates because `income_stress` has exactly three values. This is not
"pick a threshold and hope"; it is a named, enumerable, three-way question with a measured
consequence attached to each option. That is precisely the shape that **can** face the director as a
curriculum-shaped call under R13, rather than being quietly chosen by the agent that benefits from
the atom closing.

## Q2. Does the dimension publish a false-flag rate at all? — **Different answer per pair.**

**W2_8 ↔ C10 — NO, and the reason is not the one the mint expected.** The negative population is
available and unambiguous, so the mint's stated blocker does not apply. The blocker is that the
measure would be **vacuous**: it returns 0.0000 for any detector, because the world has no
confounding drops. Publishing "false-flag rate 0.0000" would read as a precise detector and would in
fact be reporting a property of the world. That is an R12 breach in the making — a number that looks
like company performance and is not.

The honest sequencing is **world-first**: the second direction becomes publishable here only once
W2_8 emits non-rationers who *do* drop (a move, a retrofit, a vacancy, a mild-winter cut). Until
then the entry stays recall-only, with **this** as its reason — a *world* gap, not a metric gap.

**W2_5 ↔ C7 — YES, subject to one named R13 choice.** The negative is settled at option C, the
NEITHER set is definable without any threshold, and the ×2.88 consequence is measured up front
exactly as the mint demanded. What must not happen is the agent picking C because it produces the
prettiest number. The choice — *does a household carrying distress from a prior year belong in the
must-not-flag set?* — is a question about what the company is being held to, and it goes to the
director with all three rates on the table.

---

## What changes as a result

Nothing is built here; this DISCOVER answers the question and hands off. Two follow-on atoms are
minted, one per pair, because the two debts are **not the same debt**:

* **`D14_w2_8_needs_negative_drops`** (WORLD, `simulation/self_rationing.py`) — the W2_8 register
  entry stays recall-only until the world can produce a non-rationer with a consumption drop.
  This is a world-depth gap, and it is the honest blocker.
* **`D15_w2_5_false_flag_direction_r13_choice`** (HARNESS, `tools/couple_w2_5_c7.py`) — publish the
  second direction on the settled negative, with the three-way exclusion put to the director as an
  R13 curriculum call carrying the measured 0.1661 / 0.1491 / 0.0576.

**R12 note.** No number was tuned and no figure moved: every rate above is a measurement of code as
it stands today. The one defect found in shipped code — `couple_w2_8_c10.py` counting 56 real
rationers as negatives — is recorded, not silently patched, because it is `D14`'s to fix alongside
the world change and fixing it now would move nothing (0/3752 and 0/3808 are both 0.0000).

## What already protects this in the meantime

The debt cannot be quietly declared paid.
`tests/tools/test_couple_w2_11_d5.py::test_every_published_detection_dimension_declares_its_error_directions`
scores the **flag-EVERYTHING** degenerate through each register entry's own scorer: an entry
declaring itself two-directional while still handing that degenerate a perfect 0.0 **fails**. Both
self-rationing entries remain registered as recall-only with `debt_atom` pointing here, so the control
holds them honest. Confirmed still live against W2_8's settled negative: flag-everything scores a
false-flag rate of **1.0000** there, so the falsifier has teeth on the very population this DISCOVER
declined to publish.

## Reproduction

Every figure above comes from the couplers' own entry points with no modification. The two
measurements are short enough to restate in full rather than leave as an un-runnable claim:

```python
# W2_8 three-population partition (the 192 / 56 / 3752 and the two 0.0000 rates)
from tools.couple_w2_8_c10 import _draw_healthy_kwh, _has_baseline, _weather_factor
from simulation.self_rationing import generate_self_rationing_state
from company.crm.self_rationing_detector import (
    SelfRationingDetector, SelfRationingObservation)
det = SelfRationingDetector()
must_flag, neither, must_not, flagged = set(), set(), set(), set()
for i in range(4000):
    cid = f"W28C{i:06d}"
    st = generate_self_rationing_state(customer_id=cid,
        healthy_annual_kwh=_draw_healthy_kwh(cid), commodity="electricity")
    hb = _has_baseline(cid)
    obs = SelfRationingObservation(customer_id=cid, commodity=st.commodity,
        observed_annual_kwh=st.observed_annual_kwh,
        baseline_annual_kwh=(st.healthy_annual_kwh if hb else None),
        floor_kwh=st.floor_kwh, missed_payments=st.missed_payments,
        arrears_open=False, weather_normalisation_factor=_weather_factor(cid))
    if det.detect(obs).self_rationing_suspected: flagged.add(cid)
    if st.is_silent_hardship: must_flag.add(cid)
    elif st.is_self_rationing: neither.add(cid)      # real rationer, above floor
    else:                      must_not.add(cid)     # settled: not rationing
# len(flagged & must_not) / len(must_not)  -> 0/3752
# len(flagged - must_flag) / (4000 - len(must_flag)) -> 0/3808   (naive, sweeps in `neither`)

# W2_5 denominator sensitivity (the 0.1661 / 0.1491 / 0.0576)
from tools.couple_w2_5_c7 import _make_population, _monthly_payments, _DISTRESS_HARM
from simulation.life_events import generate_life_events, household_at_date
from simulation.household import IncomeStress
from company.crm.life_event_detector import LifeEventDetector, ObservationWindow
# per (customer, year): truth = a distress event dated in that year;
#   A = all non-truth;  B = A minus any instance touching HIGH;
#   C = A restricted to (LOW, LOW) at both year ends.
# Flag with LifeEventDetector().detect(ObservationWindow(...)) exactly as
# build_scenario does, then rate = |flagged & N| / |N| for each candidate N.
```
