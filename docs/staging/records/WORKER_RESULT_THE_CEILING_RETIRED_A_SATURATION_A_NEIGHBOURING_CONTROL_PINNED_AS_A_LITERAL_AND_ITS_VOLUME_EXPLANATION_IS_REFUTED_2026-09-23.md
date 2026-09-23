# The ceiling retired a saturation a neighbouring control pinned as a literal, and that control's volume explanation is refuted

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Lane 0 delivery, 2026-09-23.** Item:
`land-the-bill-stress-ceiling-first-it-is-three-paths-and-it-blocks-everything-downstream`.
Subject: `company/crm/churn_model.py`, `tests/company/crm/test_churn_model.py`,
`tests/company/crm/test_the_refuted_bill_stress_term_cannot_outgrow_its_evidence.py`, and — for
§2 onward, which is the part the item did not anticipate —
`tests/company/pricing/test_the_arm_reaches_its_own_segment.py`.

## 0. The premise, re-measured before starting

The item's premise check reported that `dce3d0eb9` is already an ancestor of `origin/main` and
warned the work might be spent. **It is not spent.** `dce3d0eb9` landed a staging record and
nothing else (`git show --stat`: one file, 129 insertions). `BILL_STRESS_MAX_RATIO` was at neither
`HEAD` nor `origin/main`. The three named paths carried the whole of the unlanded work, and the
diff on `company/crm/churn_model.py` was the ceiling and nothing else — no foreign hunks to drop.

The item's `[stale-copy]` caveat was live (HEAD 3 behind `origin/main`) but does not bite here: the
three trunk commits touch `.gitignore`, two `docs/staging/` files, and four `tools/`+`tests/tools/`
files, and `git diff HEAD..origin/main` over the three subject paths is **empty**. The contested
path the caveat named, `tools/run_value_cycle_ab.py`, is not part of this work.

## 1. The ceiling, landed as its own commit

`bill_stress = sens x max(0, prev_annual_bill / 3000 - 1)` was unbounded in consumption. Bounded
now to `BILL_STRESS_MAX_RATIO = 0.068 / 0.053 = 1.28x` (Ofgem *Consumer Impacts of Market
Conditions* wave 6, Table 56, arrears banner), expressed as an uplift on each segment's own base
rate. The reasoning, the units argument for why only the ratio crosses, and what retirement still
needs are in the constant's own comment and in
`SEAT_RESULT_THE_REFUTED_KNEE_IS_BOUNDED_TO_ITS_EVIDENCE_AND_TWO_PUBLISHERS_STILL_CALL_THE_BELIEF_FLAT_2026-09-23.md`.

Mutation sweep on the new control: five mutations, five kills, run in an isolated extract. The
first draft of leg 2 was near-vacuous and the sweep is what said so.

## 2. THE INTERCONNECTION THE ITEM DID NOT NAME, and it is the more interesting half

The ceiling **reds eight legs in `tests/company/pricing/test_the_arm_reaches_its_own_segment.py`**,
a file with no textual relationship to `bill_stress` at all. One-variable control, run rather than
reasoned about: a clean `HEAD` extract is green on that file (42 passed); the same extract plus
**only** the three subject paths reds exactly those eight.

Those legs pinned the literal `pytest.approx(1.0)`. They are the shape CLAUDE.md names — *a control
keyed to today's answer goes red when the code becomes more honest* — and that is what happened:

```
margin |  SME@3.9GWh |  I&C@3.9GWh |  RESI@3.9GWh |  RESI@4,004
   0.5 |    0.063029 |    0.063029 |     0.063029 |    0.063029
   8.0 |    0.078630 |    0.163962 |     0.063029 |    0.063029
  20.0 |    0.273418 |    0.511790 |     0.712061 |    0.335022
  80.0 |    0.967958 |    0.999316 |     1.000000 |    0.996650
```

The SME path at C_IC3's volume was flat at `1.0000` across every candidate margin. It now spans
0.063 → 0.968. **The saturation was the unbounded knee**: 3.9 GWh at £60/MWh is a £236,166
previous-year bill, and the term alone asserted 19.5 of churn uplift.

### 2a. And the file's stated MECHANISM is refuted, not just its numbers

That file's claim 1 was *"the saturation is a property of volume, not of the account being
industrial — otherwise 'use the I&C branch' is a preference rather than a correction."* Measured
under the bound, **that is false**. The SME/I&C gap at C_IC3's volume is −0.085 at a £8/MWh margin;
at a household's volume it is −0.101. Nearly the same gap. What separates the branches is the
SEGMENT LABEL, not the volume.

**The routing repair is still correct and its mechanism has changed.** An industrial account on the
SME branch is no longer handed an uninformative curve — it is handed one that materially
*understates* its price response, and an arm that underestimates churn overprices. The eight legs
are re-keyed to that property, with the superseded claim corrected beside it rather than over it.

### 2b. What is NOT re-measured, stated so it is not read as covered

The 2026-08-26 finding attributed **−£94,314 realised** on C_IC3 to the routing defect. That
attribution was taken in a world where `bill_stress` ran away, and this pass has not re-run the
A/B. **How much of that loss was the routing and how much was the runaway is now an open
question**, and it is a measurement, not a reading. It is the natural next item for this lane.

## 3. Two mutations I named were wrong, and the sweep is what said so

Reported as it came back, not as designed:

| mutation | predicted | actual |
|---|---|---|
| remove the `min(...)` ceiling | reds the re-keyed legs | **KILLED** — 8 legs, incl. both new ones |
| collapse `segments_for` to the two-valued map | reds the branch-gap leg | **did not touch it** — killed by three *pre-existing* legs instead. The leg calls both branches directly, so it is about the branches disagreeing, not the routing reaching them. The flattering reading, caught. |
| `IC_RATE_SENSITIVITY` → the SME value | reds the branch-gap leg | **fired nothing in the whole file** |
| `IC_BASE_CHURN_RATE` → `BASE_CHURN_RATE` | — | KILLED by the branch-gap leg |
| `IC_TENURE_DISCOUNT_PER_YEAR` → resi value | — | KILLED by the branch-gap leg |

I had the mechanism wrong: the branches are held apart at a renewal by `IC_BASE_CHURN_RATE` (0.20
vs 0.10) and the smaller I&C tenure discount, **not** by `IC_RATE_SENSITIVITY`.

**The silent mutation was established rather than assumed to be flattering, and it is a MISSING
TEST.** Every leg in that file compared LEVELS, and the I&C branch keeps a higher level from its
base rate alone — so `IC_RATE_SENSITIVITY`, the constant that encodes *punishes a rise harder*,
could have been retuned to the household value with the file staying green and the arm's whole
reason for routing rotting underneath it. `test_the_ic_branch_is_the_STEEPER_curve_and_not_merely_the_higher_one`
is that missing test: it asks about the SLOPE across the live margins, and the mutation now fires
(I&C rises 0.5550 against SME's 0.5779 — the branch stops being the steeper one).

## 4. Two pre-existing reds, named so they are not read as mine

Both reproduce in a clean `HEAD` extract with **no file of mine copied in**, so both belong to the
standing HEAD red register rather than to this pass:

  * `tests/company/crm/test_captive_floor_and_market_netting.py::test_every_estimate_BELOW_the_elbow_is_unchanged_because_the_calibration_was_not_touched`
    — `0.1592` against an expected `0.14`.
  * `tests/company/pricing/test_value_based_renewal.py::test_a_FLOOR_bound_choice_is_not_reached_as_the_arm_STRAINING_UPWARD`
    (exact name `..._is_not_reported_as_the_arm_STRAINING_UPWARD`) — a 200 kWh account chooses
    `100.0` and `endpoint_side` reads `ceiling` where the test expects `floor`. Worth saying why
    this one is NOT mine despite sitting next to the arm: at 200 kWh the previous-year bill is
    £50, three orders below the £3,000 knee, so `bill_stress` is `0.0` with or without the
    ceiling and the bound cannot reach this input at all.

**Coverage actually run, stated rather than implied.** In the HEAD-plus-my-four-paths extract:
`tests/company/crm/` + the two churn-origin/interface files (2,206 passed, 1 pre-existing red) and
`tests/company/pricing/` (870 passed, 2 xfailed, 1 pre-existing red, 15m10s).
`tests/simulation/test_phase24a_ic_customer.py` is **not** covered here — it exceeded the budget
twice under concurrent gate-run contention. It reads `IC_BILL_STRESS_SENSITIVITY = 0.0`, which
this pass does not touch, but that is a reading and not a run.

## 5. One accuracy correction made while landing

`bill_stress_uplift_ceiling`'s docstring claimed `tools/churn_belief_size_response.py` "asks the
model for the bound instead of carrying a second copy". It does not — it composes its deafness
clause from a per-run census, precisely because this constant was uncommitted. The docstring now
says the export is the door and not the wiring.
