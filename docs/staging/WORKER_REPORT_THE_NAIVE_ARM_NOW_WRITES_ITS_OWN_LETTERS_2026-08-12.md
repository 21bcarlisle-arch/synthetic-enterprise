# [WORKER-REPORT] the naive arm now writes its own letters — and the population reversed the sign (2026-08-12)

**Severity:** RECORDED · **Lane:** C_customer_ops
**Status:** the blocking finding is discharged and archived; one item is owed to a weekly gate,
named below. Nothing here waits on the director.

Drawn as lane `C_customer_ops`'s live BLOCKING finding (RUNG 1c, OPS12 clause 3):
`WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10`. Full disposition —
including the evidence quoted below — is at
`docs/staging/done/WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10.md`.
`C_customer_ops` now carries zero blockers (`python3 -m background.finding_severity`).

## The defect

The frozen-policy baseline replays a decade twice and publishes the margin delta as "the value
of learning". Its NAIVE arm ran naive retention, naive guard and naive hedging — and the LIVE
A/B-split dunning letter tone, because `collections_tone_for` resolved a pinned
`CURRENT_POLICY` rather than the run's. The naive counterfactual was not the naive company, and
a published delta attributed one uncontrolled variable to the policy change.

## What landed

**The fix — a run-scoped active policy, not the plumbing.** Neither option the finding named was
taken. Threading the policy through the four SIM consumers would have re-pushed a company
decision object across the wall the B5 pass had just cleared; waiting for the push shape was
unnecessary to get the arm's identity right. `company/policy/decision_policy.py` gains
`policy_scope` / `active_policy` (a context manager, so a failed arm cannot leak into the next
one — tested with a raising arm); the seam resolves the run's policy; `run_frozen_baseline`
scopes each arm; and `run_phase2b.main` **refuses** a `policy=` argument that disagrees with the
active scope, which is the fail-closed half. Nothing crossed the wall — the seam still takes no
policy argument, still re-exports no type, `tools/epistemic_wall.py` exits 0 — and outside any
scope the resolved tone is byte-for-byte what B5 preserved.

**The class control, per R10** — `tests/company/policy/test_policy_field_consumption.py`, 12
tests. Completeness (every `DecisionPolicy` field must declare how it reaches its consumer, so
the next `tone_mode` cannot arrive undeclared) plus an AST scan for a field resolved from a
module-level constant in **both** shapes — `CURRENT_POLICY.<field>` and
`tone_for(CURRENT_POLICY, ...)`. The original defect was the second shape; an attribute-only
scan would have missed it.

**R15, against the real historical tree.** The scan pointed at the pre-fix file from git:

    HITS: ['company/interfaces/collections_communication.py:101 passes CURRENT_POLICY to tone_for()']

Line 101 is the line the finding cited. It names the actual defect at the actual line, and names
nothing today.

`framing_mode` — the sibling the finding flagged and did not check — **was clean**
(`run_phase2b.py:1353` already threads its parameter). It is now inside the scan's subject.

## The finding said the sign was unknown. It is now measured — and a sample would have lied.

24 roster accounts x 120 billing periods = 2,880 bill-periods, probed at the real call site
(`arrears_engine::_tone_for_bill`) through `nudge_physics::tone_effectiveness_multiplier`:

| arm | firm_toned | mean on-time nudge |
|---|---|---|
| current | 1,477 / 2,880 | 1.02264 |
| naive (corrected) | 2,880 / 2,880 | 1.02638 |

Corrected naive on-time nudge **RISES +0.365%** → naive bad debt falls → naive margin/EV rise →
the published `delta_ev_gbp` **was OVERSTATED** and shrinks slightly on refresh.

**A five-customer sample gave the opposite sign** (naive nudge FELL, 1.0135 vs 1.0547 — which
would have made the delta understated). The population reversed it. Recorded because it is this
project's own catalogued failure mode, and because the sample was the tempting cheap answer.

Honest limit (R9): this is `observed-with-evidence` at the payment-nudge INPUT and `inferred`
for the P&L consequence. Realised written-off GBP needs the replay.

## Published figures: nothing was silently corrected, and nothing needed re-rendering

The delta reaches `dashboard.json` via `_load_frozen_baseline` — and **nothing in `site/`
renders it** (`grep -rn "frozen_baseline" site/` → no consumer). So R11 has no rendered value to
verify here; that is a fact about the artefact's reach, not a check I skipped. The stale artefact
is instead **stamped with its own provenance**: `site/state/frozen_policy_baseline.json` now
carries an `arm_identity` block naming `tone_resolved_from` as CONTAMINATED and listing the six
fields the arms actually differed on — `tone_mode` conspicuously absent, the defect made
legible. An artefact lacking the key predates the fix.

## Owed, and queued

- **Owed to a gate, not to a person:** the corrected delta arrives with the weekly baseline
  refresh (a multi-minute full-decade replay x2, `should_refresh_baseline`, spawned out-of-band
  by `process_run_complete.py`). Not run from this bounded tick; not an atom, because no work is
  required and the artefact now says which side of the fix it is on.
- B5's **push** shape (tone stamped on an emitted bill event) remains owed and untouched. This
  fix does not claim it — the seam is still a PULL and still says so.
- **Queued, not fixed** (SELF_INTERRUPT_DISCIPLINE): `saas/reporting/annual_report.py:7713` has
  an invalid escape `churn\_estimate` in an f-string (SyntaxWarning today, error in a future
  Python), surfaced by the new AST scan.
- **Queued — OPS9's exit criterion has drifted:** `background.finding_severity` now reports
  **4 UNCLASSIFIED** documents where OPS9 certified zero. Three carry a severity value off the
  vocabulary (`high`, `MEDIUM`, `HIGH` instead of `BLOCKING/LATENT/RECORDED`) and one has no
  header at all. That means the zero-unclassified criterion is measured but not *enforced* — a
  reading nothing reds on. Not this lane's finding and not fixed on sight, but it is the same
  "control that cannot fail" family OPS9 itself was about, so it should not sit unrecorded.
