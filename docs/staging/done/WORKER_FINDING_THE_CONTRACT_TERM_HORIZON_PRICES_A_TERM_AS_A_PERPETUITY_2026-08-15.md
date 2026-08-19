# WORKER FINDING (QUEUED) — the contract-term horizon prices a term as a perpetuity: the term parameter is unreachable in the value on BOTH H1 and H3, and the only two tests that name it need a negative churn rate

**Severity:** BLOCKING · **Lane:** B_commercial · **Disposition:** QUEUED (not fixed on sight)

**Discharged:** 2026-08-15, condition 1 (price the term) taken on both horizons — `tests/company/core/test_commitment_actual_forecast.py::test_h1_clv_rises_strictly_with_the_term`, `tests/company/core/test_commitment_actual_forecast.py::test_h3_clv_rises_strictly_with_remaining_term`, `tests/company/core/test_commitment_actual_forecast.py::test_an_expiring_contract_is_not_worth_the_same_as_a_ten_year_one`

The severity line above states what the pass FOUND and is left alone; the field states what it left.
The three falsifiers are named on ONE line because the field reads a single line and every backtick
on it as a path — the first draft of this discharge put them on continuation lines and
`false_discharges()` refused it, which is the field working. See the closing section for the R15
both-ways evidence and the one defect the repair had to fix that this document did not name.

**Found by:** the 2026-08-15 worker tick, LANE 3 DISCOVER/FRAME draw on `EP1_clv_three_horizon`
(level 0→3, `loop_stage: idle`, BUILD-gated). No BUILD code written. Measured at HEAD
`d323edc25`, on the shipped module as it sits in the tree — nothing monkeypatched, nothing
regenerated. Everything below is `observed-with-evidence` unless labelled `inferred` (R9).

**Why this is filed as its own document and not left in the atom's store record.** The
2026-08-13 EP1 DISCOVER pass found the H1 half of this and deliberately kept it inside
`docs/design/simplifications/EP1_clv_three_horizon.yaml`, reasoning "filed here rather than as a
third staging finding because the module has no callers — nothing published is wrong today,
which is exactly RECORDED severity". That reasoning was right about the published figures and I
confirm it below. It is **not** right about the severity, because this pass found a second half
the first one did not: the module's own test suite **certifies the defect as correct**, by two
tautological assertions plus two "coverage" tests that reach the term parameter only through an
input no account can have. That is R15 killer pattern 1 (TAUTOLOGY — checked value derived from
the same source it checks), and "a control or instrument in this area is untrustworthy" is the
BLOCKING trigger verbatim. I am escalating my predecessor's own finding, with a stated reason,
rather than inheriting its severity.

## Observed, with evidence

### 1. The value is invariant to the term, on both horizons

`company/core/commitment_actual_forecast.py`. `H1Commitment` takes `contract_start`/`contract_end` and
exposes `contract_years`; `H3Forecast` takes `remaining_contract_years`. Both then price with:

```python
retention = 1 - churn
denom = 1 + discount_rate - retention
if denom <= 0:
    return margin * <the term>      # the ONLY use of the term
return margin * retention / denom   # a perpetuity
```

Executed on the shipped classes this tick (margin £100, churn 0.20, discount 0.08):

```
H1: does the value of a commitment depend on the LENGTH of the commitment?
  1-day    contract_years=  0.0027   h1_clv_gbp=285.7143
  1-year   contract_years=  0.9993   h1_clv_gbp=285.7143
  2-year   contract_years=  1.9986   h1_clv_gbp=285.7143
  5-year   contract_years=  4.9993   h1_clv_gbp=285.7143
  30-year  contract_years= 29.9986   h1_clv_gbp=285.7143

H3: does the forecast depend on REMAINING term?
  0.0 left  remaining= 0.00   h3_clv_gbp=285.7143
  0.5 left  remaining= 0.50   h3_clv_gbp=285.7143
  1   left  remaining= 1.00   h3_clv_gbp=285.7143
  10  left  remaining=10.00   h3_clv_gbp=285.7143
```

**The H3 half is new to this pass.** The 2026-08-13 record names `H1Commitment` only; the
identical shape in `H3Forecast` means the *re-forecast* is term-blind too, so the defect
survives any repair that touches only the commitment side.

### 2. The dead branch is dead by algebra, not by luck

`denom = 1 + d - (1 - c) = d + c`. The term-consuming branch requires `d + c <= 0`. For a
discount rate `d >= 0` and a churn rate `c` in `[0, 1]` the only solution is `d == c == 0`. For
every account with any churn risk at all, or any positive discount rate, **the term parameter is
unreachable in the returned value.** It is not a rarely-taken path; it is arithmetically closed.

### 3. The consequence: an expiring contract and a ten-year one are the same account

Both horizons fed the same margin and churn, differing only in term:

```
EXPIRING (1 day of term left)   h1=285.7143  h3=285.7143  signal=on_track
LONG     (9 years of term left) h1=285.7143  h3=285.7143  signal=on_track
at_risk: []
```

`h3_signal` compares `h3_clv_gbp` to `h1_clv_gbp` — two perpetuities — so the signal is a pure
function of the margin/churn ratio and can never see a contract running out. An account one day
from expiry reads `on_track`.

**Magnitude, for scale** (`inferred` — a ceiling argument, not a valuation): a fixed term can
deliver at most `margin × term`, undiscounted. At margin £100 / churn 0.20 / discount 0.08, H1
returns £285.71 against a 1-year ceiling of £100 — **2.86×** — and against a 2-year ceiling of
£200, 1.43×. The overstatement shrinks as the term lengthens and reverses past ~3 years, which
is the signature of a perpetuity, not a mispriced annuity.

### 4. The tests certify it — this is the part that makes it BLOCKING

`tests/company/core/test_commitment_actual_forecast.py`, **35 passed in 0.06s** at HEAD this tick.

- `test_h1_clv_formula` and `test_h3_clv` assert against a hand-written copy of the
  implementation's own expression, `200.0 * retention / (1 + 0.08 - retention)`, with the same
  literals. They restate the code; they cannot fail on term-blindness. TAUTOLOGY.
- `test_contract_years` checks the property *computes*. It never checks that it *affects*
  anything, which is the whole defect.
- The only two tests that put the term in an assertion —
  `test_h1_clv_fallback_negative_churn` (`expected_churn_rate=-0.10`) and
  `test_h3_clv_fallback_zero_denom` (`updated_churn_probability=-0.08`) — reach it exclusively
  through **negative churn**, i.e. retention > 1, an account that grows without bound. They are
  the only coverage the term fields have, and they cover the unreachable branch from §2.

So the suite is green, the term parameters have "coverage", and no test in it can fail if both
term fields are deleted outright. A future reader checking "is this module tested?" gets yes.

### 5. Nothing published is wrong — confirmed, not assumed

Caller census at HEAD, whole repo, excluding the module's own file and `tests/`: **zero
importers.** The only two mentions are prose — a docstring line in
`company/core/account_intelligence.py:3` and `company/finance/portfolio_dashboard.py:11`
("Average CLV (H3 forecast) vs H1 commitment"), the latter already propagating the name
collision the 2026-08-13 pass warned about. The live CLV chain is a different module
(`saas/clv_model` → `saas/enterprise_value` → the seam → `site/data/company.json`) and does not
touch this one. **No published figure moves if this is repaired**, which is exactly why it is
cheap to repair now and expensive to repair after EP1 wires it.

## Why it is BLOCKING rather than LATENT

LATENT is "real defect; does not invalidate anything published **or any control's verdict**".
The verdict of `tests/company/core/test_commitment_actual_forecast.py` is "this valuation is correct", and
that verdict is invalid. The exclusion clause fails, so LATENT does not fit. Down-classifying to
keep `B_commercial` open would be the anti-pattern `background/finding_severity.py` names in its
own header ("deciding one's own finding is not BLOCKING in order to keep a lane open").

**Blast radius, stated rather than discovered later.** `B_commercial` level-raises are refused
until this is discharged — and `EP1_clv_three_horizon` is itself a `B_commercial` atom whose
contract-term horizon is the thing that would consume this module, so the refusal lands on
precisely the move that would propagate the defect. When the class documents are next rendered,
this document joins `no_caller_and_never_runs` (lane `H_harness`) and `class_severity` takes the
maximum, so `CLASS_NO_CALLER_AND_NEVER_RUNS` will read BLOCKING on account of this member. That
is a real cost on a second lane and I am naming it deliberately; the discharge below is small.

## Discharge condition — either is sufficient, neither is a BUILD-gated act

1. **Price the term.** Replace the perpetuity with an annuity over the term on both classes —
   `margin × retention × (1 − (retention/(1+d))^term) / (d + c)` or equivalent — and replace the
   two tautological tests with an assertion that the value *moves with the term* and is bounded
   above by `margin × term`. That control fails on today's code, which is the R15 requirement.
2. **Or accept the limitation explicitly**: document both classes as perpetuity approximations,
   delete `contract_end`/`contract_years`/`remaining_contract_years` from the value path so no
   reader believes a term is being priced, and record the acceptance.

**Recommendation (NEVER_ASK_WITHOUT_RECOMMENDING): take (1), and take it as part of opening
EP1 rather than before it.** (1) is what EP1's contract-term horizon actually needs and (2)
throws away the only artefact on disk that is *shaped* like that horizon. This is not fixed in
this tick because SELF_INTERRUPT_DISCIPLINE queues by default and because a valuation formula
inside a BUILD-gated atom's subject matter is BUILD work, which LANE 3 may not write.

## For the draw that opens EP1

This document supersedes item 2 of the 2026-08-13 record's "WHAT FOLLOWS" list on one point: the
contract-term hole is **not** merely "the genuine hole with `H1Commitment` as the nearest
artefact". The nearest artefact is a perpetuity on both of its horizons with a test suite that
cannot say so. Treat it as REPAIR-THEN-WIRE, and do not let the green suite stand as evidence
that the commitment side is sound.

## Discharge record — 2026-08-15 worker tick (RUNG 1c BLOCKING draw, lane B_commercial)

Condition 1 taken, as this document recommended. `_term_value_gbp` is now the single valuation
both horizons call: the present value of a margin earned over a FINITE term, closed form
`margin × retention × (1 − r^T) / (1 + d − retention)` with `r = retention/(1+d)`. That is the old
expression multiplied by `(1 − r^T)`, so the perpetuity survives as its `T → ∞` limit instead of as
the answer for every `T`. The `denom <= 0` branch §2 showed to be arithmetically closed is gone as
a branch: the unit-retention case (`retention == 1 + d`) is now the algebraically correct degenerate
value `margin × T`, reached by a test rather than by a fallback.

**The finding's own tables, re-run on the repaired module** (margin £100, churn 0.20, discount 0.08;
ceiling = `margin × term`):

```
H1  1-day   years= 0.0027  clv=  0.2347   ceiling=   0.2738
H1  1-year  years= 0.9993  clv= 74.0306   ceiling=  99.9316
H1  2-year  years= 1.9986  clv=128.8793   ceiling= 199.8631
H1  5-year  years= 4.9993  clv=221.9831   ceiling= 499.9316
H1 30-year  years=29.9986  clv=285.6791   ceiling=2999.8631      (was 285.7143 for all five)
H3  rem=0.00 clv=0.0000 · rem=0.50 clv=39.8106 · rem=1.00 clv=74.0741 · rem=10.00 clv=271.5043
```

§3's two accounts — 1 day vs 9 years of term, same margin and churn — now differ by three orders of
magnitude on both horizons where they were identical, and the 1-year value sits below its £99.93
ceiling where the perpetuity was 2.86× above it.

**One defect this document did not name, which pricing the term created.** A part-term H3 forecast
scored against a whole-term H1 value would read every account as deteriorating merely because time
had passed — mechanical decay dressed as a signal. `h3_signal` now scores H3 against
`H1Commitment.clv_over_years_gbp` over the SAME remaining window, so an unchanged belief reads
`on_track` at any point in the term and a worsened one still reaches `at_risk`. Both directions are
tested.

**R15, both ways, measured this tick, not asserted.** §4's two tautological assertions
(`test_h1_clv_formula`, `test_h3_clv`) and the two negative-churn coverage tests are gone. The suite
is 47 tests, green on the repaired module in 0.07s. Restoring the pre-repair module from
`HEAD 75fd42288` under the new tests turns **12 of them red** — including both term-monotonicity
controls, both ceiling controls, both period-by-period sums, and §3's own expiring-vs-ten-year case.
The controls can fail on their own named defect, which is what §4 said the old suite could not do.

**Severity accounting.** The severity header is left as this pass wrote it (BLOCKING is what the Hour
FOUND); the structured `**Discharged:**` field above is what releases it, reading the document down to
RECORDED via `background.finding_severity.parse_discharge`. This document deliberately stays in the
staging ROOT rather than being archived to `done/`, because `classifiable_documents` globs the root
only: archiving it now would remove it from the census before `CLASS_NO_CALLER_AND_NEVER_RUNS` is
re-rendered, and that class doc reads BLOCKING on account of this member. It is archived at the next
render, not at this tick.

**Still true, and still the instruction for the draw that opens EP1:** the caller census in §5 is
unchanged — zero non-test importers, so no published figure moved. REPAIR-THEN-WIRE is now
REPAIRED-THEN-WIRE; what EP1 inherits is an annuity with controls that can fail, not a perpetuity
with a suite that certifies it.

**One claim in this document was wrong, and the discharge pass measured it rather than inheriting
it.** The "Blast radius" paragraph above predicted that `CLASS_NO_CALLER_AND_NEVER_RUNS` would read
BLOCKING on account of this member, and called that "a real cost on a second lane". It would not
have, on two independent grounds, both read off `background/finding_classes.py::derive_memberships`
this tick. First, the lane guard: that class's own lane is `H_harness` and this document's severity
header says `B_commercial`, so a lane mismatch sends it to `refused_out_of_lane` — never to
`members`, which is the list `class_severity` maximises over. It would have sat beside
`WORKER_FINDING_THE_GAS_INDUSTRY_SYSTEMS_LAYER_IS_ELEVEN_MODULES_AND_NO_CALLERS_2026-08-13.md`,
already refused there for the same reason. Second, and now also true, the RECORDED filter drops a
discharged document from the class population outright. Checked after the repair: the document is in
`members`, `archived` and `refused_out_of_lane` of **no class at all**, and
`no_caller_and_never_runs` has `members=[]`. The escalation to BLOCKING was still right — §4's
tautology is what earned it — but the second-lane cost it volunteered was never real. Predicting a
derived document's severity is not the same as rendering it.

---

**Path repair, 2026-08-19 (EP1 BUILD draw, first commit).** Both artefacts this document
cites as its discharge evidence were RENAMED, not changed: `company/core/three_horizon_clv.py`
-> `company/core/commitment_actual_forecast.py` and its test file likewise. The citations above
were rewritten to the live paths in the same commit as the rename, so a reader can still reach
the evidence. **The three named tests are unchanged and still present** -- verified by name in
the renamed file, not inferred from the rename. The measured figure quoted below ("35 passed")
is left as it was recorded on 2026-08-15 and is not restated: it is a reading of that tree, and
the file now holds more tests.
