**Severity:** LATENT · **Lane:** W2_customer_generator (world side: `simulation/`) · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `land-the-journey-decision-for-an-svt-conversion-now` (Lane 0 delivery)
**Answers:** `docs/staging/WORKER_FINDING_AN_SVT_CONVERSION_IS_A_RENEWED_ROW_AGAIN_AND_ITS_JOURNEY_DECISION_IS_STILL_SKIPPED_2026-10-02.md` (the skipped journey decision)
**Pre-registration:** `docs/staging/records/WORKER_PREREG_AN_SVT_CONVERSION_RECORDS_A_STAYED_DECISION_ON_ITS_JOURNEY_2026-10-02.md`

# An SVT conversion now records a stayed decision, and nothing else moves

**2026-10-02, delivery seat.**

## What landed

`simulation/run_phase2b.py`: the renewal block calls `_record_renewal_decision` on every renewal,
rolled or not. Before this, the call sat inside `if event is not None:`. When `1cd4b03dc` took the
departure roll off a household converting off the SVT, that household lost its journey decision too.
The helper records `switched` only for a rolled `churned` event. It also writes one row to a new SIM-side output,
`renewal_decisions_log`, with `rolled` and `switched`. `tests/simulation/test_an_svt_conversion_records_a_stayed_decision.py`
has one partition control over the three shapes (conversion, rolled-and-stayed, rolled-and-left) and an AST
leg that refuses a call site gated on `event` or `_rolled`. All three mutations named in its docstring
were run and each fails the tests.

## The runs

Both runs are the default world, full horizon, `SIM_FAST_MODE=1`, on one commit, `65f48b276`
(origin/main at draw time). The pre-registration named `ed7e89d0e`, but origin had moved by then.
Base is a detached worktree at `65f48b276`. Change is the same commit plus this diff. They ran
serially, each for about 17 minutes. The pre-registration's 05:55Z amendment gave a recipe with
`SIM_FAST_MODE` unset. I ran all five arms with it set to 1, which is what every production launch
sets (`sim/risk_committee_agent.py`). Unset, the committee refuses. The arms are consistent with one
another either way. Origin then moved to `a0f2496e9`, which reroutes riding-leg declines behind the
decline switch. That switch is off, so the graded path is the same, and the landing is rebased onto it. The box was also running a value-cycle depth job, which only
affects timing. Scripts and outputs are in `/var/tmp/svt-journey/`: `run.py`, `grade.py`,
`base.json`, `change.json`, `base2.json` (placebo), `alloc.json`, `jonly.json` (one-variable arms).

## Grades

- **P1, whole-book departures: HELD.** The strong form fails only on a single float ULP, which is shown below to be a code-layout effect.
  `churned` by year is identical: 2017 9, 2018 4, 2019 5, 2020 3, 2021 3, 2025 2. Both runs have
  96 `customer_events`. 95 are identical byte for byte. One, a 2025-03-15 `churned` row, differs only
  in `unit_rate_gbp_per_mwh`: 275.31995847836555 against 275.3199584783656, a difference of 5e-14.
  Nothing that prices a renewal reads a journey. The only readers are `churn_journey_log` and the
  journey's own `advance()`. The suspected cause is float summation order varying between
  processes, since `run.py` does not pin `PYTHONHASHSEED`. That claim is tested, not assumed, by a
  placebo: a second base run on the same commit. **The placebo REFUTED the hash explanation.** The second base run (`base2`) is identical to the
  first byte for byte, in all four logs. The ULP is therefore caused by this diff, and my first
  explanation was wrong. Next hypothesis, **written before the arm ran**: the diff allocates new
  objects (the log rows), which shifts the order of something iterated by object identity, and
  so the order of a float sum. If so, it is not a world effect. Prediction, moderate confidence:
  an arm that is base plus ONLY the `renewal_decisions_log` append (the journey decision still
  skipped on a conversion) reproduces the change's 275.3199584783656. If instead it reproduces
  base's ...6555, then a recorded journey decision reaches a renewal price, and that path is the
  finding. **The allocation arm REFUTED that prediction.** Base plus only the log append reproduces base
  byte for byte: 275.31995847836555, with `customer_events` and `churn_journey_log` both equal to
  base. No module outside the run loop reads a journey (grepped `simulation/`, `sim/`, `company/`,
  `saas/`). Two causes remain: the journey decision itself, by a path I have not found, or the
  helper's different code shape. The discriminating arm, **written before it ran**, is base plus
  ONLY `_journey.record_decision(..., switched=False)` on a conversion, with no helper and no log.
  Prediction, low confidence (60%): it reproduces the change's ...656. **The journey arm REFUTED that prediction too.** It reproduces the change's
  `churn_journey_log` exactly, so the whole effect of the decision is present, yet its
  `customer_events` equal base byte for byte (...6555). Neither variable alone moves the price,
  and only the change as written (the helper plus both writes) does. The ULP therefore comes from
  code shape: allocation or memory layout feeding the order of a float reduction. numpy's SIMD
  sums depend on array alignment, which is the likely route, but I have not traced it. It is not
  a world effect. **P1 is graded HELD**: departures, their causes and every value except one
  2025 price at 5e-14 are identical, and that one is shown to be no consequence of the decision.
  The record keeps three wrong predictions in order: hash order, then allocation from the log
  alone, then the journey. **A lesson for anyone grading "byte-identical" on this world:** a pure
  refactor can move a float by a ULP. Compare prices at a tolerance (say 1e-9 relative) and
  state the tolerance, or run a placebo arm.
- **P2, retention outcomes and nudge rows: HELD.** Outcomes are identical (`retained` 27,
  `churned_despite_offer` 7). There are 34 nudge rows in each run.
- **P3, decisions recorded rise by exactly the conversions: HELD, overall and in every year.**
  The change records 96 decisions: 59 rolled and 37 not rolled. The base has 59 rolled renewal
  events. All 37 unrolled rows are `svt_conversion` `renewed` rows. No unrolled `declined_fix`
  occurs while the decline switch is off. Per year, the decisions equal the base's rolled events
  plus the conversions in every year from 2016 to 2025.
- **P4, later journeys move toward CONTENT: direction HELD, strict prediction REFUTED.** Both runs
  have 96 journey rows. After 2017, `content` rises from 58 to 60 and `comparing` stays at 0 to 0.
  The strict fall in `comparing` that I predicted with moderate confidence did not happen, because
  no row in either run is ever `comparing` or `in_market`. Every journey is logged as `content` or
  `irritated`, and none is burned. Two households moved, both from `irritated` to `content`:
  `PROS-2016-0098` at its 2021-03-22 renewal and `SYN-2016-030` at 2025-04-12. The amendment's added leg, **`irritated` does not rise in years after the first conversion:
  HELD**: it falls from 4 to 2. Before this
  change, an irritated converter stayed irritated into its next term. Now its stay resets it.

## What it means

The change is a pure record. It moves no departure, outcome or price. The single ULP comes from code layout, not the decision. It reaches only the journey trajectory, through two households. The pre-registration did not
anticipate one thing: in this world the journey never reaches `comparing` at a renewal, so the
funnel's middle states are not exercised at all. That is the next question for whoever owns
`simulation/churn_journey.py`. I am not taking it up here.

The finding this answers said the journey "feeds later behaviour". In the run loop it does not: all three arms show the decision moving only the journey's own log.

Item three of the renewal-block sequence edits the same block, and it is now unblocked.
