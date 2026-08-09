# WORKER FINDING — the frozen-baseline NAIVE arm keeps the LIVE policy's letter tone

**Found:** 2026-08-10, during KNIFE3 design B5 (the collections-tone wall cut).
**Status:** QUEUED, not fixed (SELF_INTERRUPT_DISCIPLINE — one hotspot per pass).
**Class:** counterfactual contamination / `one name, two numbers`.
**Severity:** the A/B it corrupts is a published diagnostic, not a control.

## The claim, and how it is evidenced

`observed-with-evidence` (R9). Read from the tree, not inferred:

- `company/policy/decision_policy.py:83` — `CURRENT_POLICY` sets `tone_mode="ab_test"`.
- `company/policy/decision_policy.py:99` — `NAIVE_POLICY` sets **no** `tone_mode`, so it
  takes the dataclass default at line 68, `"firm_toned"`. The two policies genuinely differ
  on this field.
- `tools/run_frozen_baseline.py:79` — runs the same historical window twice,
  `run_phase4c(report_end=..., policy=CURRENT_POLICY)` and again with `NAIVE_POLICY`, to
  produce the counterfactual "what the naive company would have earned".
- `simulation/arrears_engine.py::_tone_for_bill` resolves the tone against the **live**
  policy, with no policy argument threaded from the run. Post-B5 it does so via
  `company/interfaces/collections_communication.py::collections_tone_for`, which likewise
  pins `CURRENT_POLICY`.

So the naive arm runs with naive retention, naive guard and naive hedging — and with
**current** dunning tone. Its arrears letters are A/B-split when the policy it claims to be
running says they are uniformly firm.

**Pre-existing, not introduced by B5** — evidenced: the pre-cut call site was
`tone_for(CURRENT_POLICY, customer_id, period_end)`, the same pinning. B5 preserved it
deliberately and byte for byte (27,090 input combinations compared, zero mismatches) so that
a wall pass would not move a simulated payment outcome. The cut moved WHERE the tone is read
from, and changed no value.

## Why it matters

Tone feeds `payment_outcome` via `simulation/nudge_physics.py::tone_effectiveness_multiplier`,
which nudges on-time payment probability (Cabinet Office/BIT anchor: +3 to +10pp). Payment
outcomes drive written-off GBP through `compute_emergent_bad_debt`, which lands in the board
P&L's `bad_debt_gbp` and therefore `net_margin_gbp`.

The consequence is not "a number is slightly off" — it is that **the naive counterfactual is
not the naive company**. Any margin delta between the two arms is attributed to the retention/
guard/hedging changes, while one uncontrolled variable rides along inside it. If the ab_test
split happens to beat uniform firm tone, the frozen baseline **understates** what the policy
changes bought; if it loses, it overstates. Neither direction is currently measured, so the
sign is unknown — which is itself the finding.

This is the `one name, two numbers` shape from the R15 library: one artefact called "the naive
arm" whose policy identity differs between the retention path (naive) and the collections path
(current), with nothing asserting the two agree.

## What a fix would have to settle (not decided here)

1. **Thread the run's policy, or pin it deliberately.** `run_phase2b` already carries a
   `policy = policy or CURRENT_POLICY` override convention (`simulation/run_phase2b.py:824`),
   so the pattern exists — but the arrears path is reached through four consumers
   (`compute_emergent_bad_debt`, `compute_debt_recovery`, `dd_collection_book`,
   `tools/generate_billing_ledger`), and threading a policy through all four is exactly the
   kind of company-object-into-the-world plumbing the wall pass has just removed. The
   push-shaped answer (tone stamped on an emitted event, so it carries the emitting run's
   policy with it) is the same one B5 is owed and is blocked on `A_composition_lift`.
2. **Whether changing it moves published figures.** It will: the naive arm's bad debt shifts.
   `docs/reports/ANNUAL_REPORT.md` and any frozen-baseline delta quoted from it would move,
   so this needs the R14 clock discipline and a stated before/after, not a silent correction.
3. **Whether a control can catch the class.** The general defect is "a counterfactual arm
   that does not switch every field it claims to switch." A control that enumerates
   `DecisionPolicy`'s fields and asserts each is actually consumed from the RUN's policy
   rather than the live one would catch this and its siblings (`framing_mode` deserves the
   same question — not checked here, and it should be).

Item 3 is the R10-shaped version: closing this as an instance fix on `tone_mode` would leave
the class open, and `framing_mode` is a live candidate for the identical bug.

## Suggested disposition

Mint as an atom in the D/E reporting lane rather than the H_harness KNIFE lane — it is a
fidelity defect in a published counterfactual, not a wall crossing. Depends on nothing; the
cheap half (item 3's control, which would red today and name its own defect) is drawable now
and does not require deciding item 1.
