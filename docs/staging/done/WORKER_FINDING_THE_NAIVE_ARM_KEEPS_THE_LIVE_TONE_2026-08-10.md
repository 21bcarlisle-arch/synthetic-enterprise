# WORKER FINDING — the frozen-baseline NAIVE arm keeps the LIVE policy's letter tone

**Severity:** RECORDED · **Lane:** C_customer_ops
**RESOLVED 2026-08-12** — items 1 and 3 built and landed; item 2's direction measured and recorded below. See the DISPOSITION section appended at the foot of this file.

**Found:** 2026-08-10, during KNIFE3 design B5 (the collections-tone wall cut).
**Status:** FIXED 2026-08-12 (drawn as a RUNG-1c blocking finding, OPS12 clause 3).
**Class:** counterfactual contamination / `one name, two numbers`.
**Impact:** the A/B it corrupts is a published diagnostic, not a control.

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

---

# DISPOSITION — 2026-08-12

Drawn by the scheduled tick as lane `C_customer_ops`'s live BLOCKING finding. All three
"what a fix would have to settle" items are answered; two are built.

## Item 1 — thread the run's policy, or pin it deliberately: BUILT

Neither of the two options this finding named was taken. Threading the policy through the
four SIM consumers was rejected for the reason the finding gives (it re-pushes a company
decision object across the wall the B5 pass had just cleared), and waiting for the push
shape was rejected because it is not needed to get the arm's IDENTITY right.

What landed instead is a run-scoped **active policy**, read only on the company side of the
seam (`company/policy/decision_policy.py::policy_scope` / `active_policy`):

- `collections_tone_for` resolves `active_policy()` instead of a pinned `CURRENT_POLICY`.
- `tools/run_frozen_baseline.py` wraps each arm in `policy_scope(...)` as well as passing
  `policy=`, so the argument covers every field a consumer is handed and the scope covers
  the one field resolved without an argument.
- `simulation/run_phase2b.py::main` now REFUSES a `policy=` argument that disagrees with the
  active scope. This is the fail-closed half: the default scope IS `CURRENT_POLICY`, so every
  existing caller is untouched, and a future caller that swaps the policy without swapping
  the scope is stopped loudly instead of producing a plausible wrong delta.

**Nothing crossed the wall.** `collections_tone_for` still accepts no policy argument, still
does not re-export the type, and the SIM still receives one string. `tools/epistemic_wall.py`
exits 0. The B5 cut's byte-for-byte identity claim also survives: outside any scope the
resolved tone is unchanged, which
`tests/company/policy/test_policy_field_consumption.py::test_outside_any_scope_the_live_policy_still_governs`
asserts against the pre-cut expression.

**Chose the context manager over a setter deliberately.** A bare `set_active_policy()` would
leak a failed arm's policy into whatever ran next — the same defect one level out. `policy_scope`
resets in `finally`, and a test performs a raising arm to prove it.

## Item 3 — a control for the CLASS: BUILT, and it names the sibling this finding did not check

`tests/company/policy/test_policy_field_consumption.py` (12 tests). Two properties, not one
assertion about `tone_mode`:

1. **Completeness.** Every `DecisionPolicy` field is declared with how it reaches its consumer
   (`run_argument` / `active_scope` / `label`). A field added to the dataclass without a
   declaration reds the suite — which is exactly the history being closed: `tone_mode` was
   added 2026-07-10 and nothing asked how the counterfactual arm would switch it.
2. **No pinned resolution.** An AST scan of `company/ simulation/ saas/ tools/ background/`
   for a policy field resolved from a module-level constant, in BOTH shapes —
   `CURRENT_POLICY.<field>` and `tone_for(CURRENT_POLICY, ...)`. The original defect was the
   second shape, so an attribute-only scan would have missed it entirely.

`framing_mode` — the sibling the finding flagged as "a live candidate for the identical bug,
not checked here" — **was NOT contaminated**: `run_phase2b.py:1353` already calls
`framing_type_for(policy, ...)` with its own parameter. It is now covered by the scan, so a
regression to `framing_type_for(CURRENT_POLICY, ...)` reds.

**R15, proven against the real historical tree, not only a fixture.** The scan was pointed at
`git show HEAD:company/interfaces/collections_communication.py` (the pre-fix file):

    HITS: ['company/interfaces/collections_communication.py:101 passes CURRENT_POLICY to tone_for()']

Line 101 is the line this finding cited. The control names the actual defect, at the actual
line, and names nothing today. Both shapes and the completeness check also have their own
`test_mutation_*` tests that PERFORM the defect, and the runtime probe has one that re-pins the
seam and proves the behavioural half fires where the static half cannot see.

## Item 2 — whether it moves published figures, and in which direction

The finding said the sign was unknown and that this "is itself the finding". It is now measured
at the input, over the whole roster rather than a sample.

Probe: the real world-facing call site (`simulation/arrears_engine.py::_tone_for_bill`) for all
24 roster accounts x 120 billing periods = 2,880 bill-periods, through
`simulation/nudge_physics.py::tone_effectiveness_multiplier`:

| arm | firm_toned | mean on-time nudge |
|---|---|---|
| current | 1,477 / 2,880 | 1.02264 |
| naive (corrected) | 2,880 / 2,880 | 1.02638 |

**Direction: the corrected naive arm's on-time payment nudge RISES by +0.365%** → its bad debt
FALLS → its margin and EV RISE → the published `delta_ev_gbp` / `delta_net_margin_gbp`
(current minus naive) **was OVERSTATED**, and will shrink slightly on the next refresh.

**A five-customer sample gave the OPPOSITE sign.** On `C0001/C0042/C0777/C1234/C9999` the
corrected arm's mean nudge FELL (1.0135 vs 1.0547), which would have made the published delta
understated. The population reversed it. Recorded because it is this project's own catalogued
failure mode — `feedback_the_atoms_own_headline_changes_sign_with_the_population`,
`feedback_promotion_evidence_may_not_reproduce_on_the_better_population` — and because a
one-paragraph sample check was the tempting cheap answer here.

**Epistemic limit, stated rather than papered over:** this measures the tone-effectiveness
multiplier, which is an INPUT to on-time probability. It is not realised written-off GBP. The
realised change needs the actual replay, and the sign at the input does not strictly guarantee
the sign at the output. So the direction above is `observed-with-evidence` for the input and
`inferred` for the P&L consequence (R9).

**No published figure was silently corrected, and none needed re-rendering.** The delta lives
in `site/state/frozen_policy_baseline.json`, reaches `dashboard.json` via
`tools/generate_dashboard_data.py::_load_frozen_baseline` — and **nothing in `site/` renders
it**. Checked: `grep -rn "frozen_baseline" site/` returns no consumer. So R11's "verify to the
rendered value" has no rendered value to verify here, which is a fact about the artefact's
reach, not a verification I skipped.

The stale artefact has instead been **stamped with its own provenance**: it now carries an
`arm_identity` block naming `tone_resolved_from` as CONTAMINATED and listing the six fields the
arms actually differed on (`tone_mode` absent, which is the defect made legible). Refreshed
artefacts carry the honest version of the same block. An artefact lacking the key predates the
fix. The regeneration itself is a multi-minute full-decade replay x2 on a weekly staleness gate
(`should_refresh_baseline`), spawned out-of-band by `process_run_complete.py` — so it is NOT run
from this bounded tick, and the corrected delta arrives with that refresh.

## What is still owed

- The corrected `delta_ev_gbp` on the next weekly baseline refresh. Not an atom: no work is
  required, the gate fires on its own, and the artefact now says which side of the fix it is on.
- The **push** shape B5 asked for (tone stamped on an emitted bill event) remains owed and
  unaffected by this. This fix deliberately does not claim it — `collections_tone_for` is still
  a PULL, and its docstring still says so.

## Queued, not fixed here (SELF_INTERRUPT_DISCIPLINE)

`saas/reporting/annual_report.py:7713` has an invalid escape `churn\_estimate` in an f-string
(SyntaxWarning; will become an error in a future Python). Surfaced by the new AST scan, not
related to this finding, so it is recorded rather than fixed on sight.
