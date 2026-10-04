# For the console seat: the objection probes graded the company before ba320e2d2, and the term probes did not

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-objection-and-qep-runs-measure-the-company-at-head` (Lane 0 delivery)

**2026-10-04.** This is the hand-off the delivery item asked for. Nothing was stopped, and nothing
under `/var/tmp/se-probe*`, `/var/tmp/se-objrun` or `tools/decision_probe.py` was touched. No
decision probe was running when I looked (07:35 BST). All four `obj_*` runs exited rc=0.

## Does the probe reach the path ba320e2d2 changed? Yes.

`ba320e2d2` (committed 00:20 BST) changed two things. It made `DecisionPolicy.renewal_default_belief`
default to `own_book`. It also made the clean-account price read a channel-blind churn belief, in
`value_based_renewal.py` and `discovered_price_sensitivity.py`.

- `tools/decision_probe.py::probe` wraps `runner.decide_renewal_rate` and calls it again under
  `VALUE_ARM_POLICY` and the capped and learned variants. It also imports
  `discovered_price_sensitivity.learned_correction` and `value_based_renewal.FLAT_AT_LEVEL`.
- Every `VALUE_ARM_*` policy is a `replace(CURRENT_POLICY, ...)` that does not set
  `renewal_default_belief` (`company/policy/decision_policy.py:216-227`). So each one inherits the
  new `own_book` default.
- `tools/run_value_cycle_ab.py` reaches the same path by the same route: `policy_scope(VALUE_ARM_POLICY)`
  plus `run_phase4c(policy=VALUE_ARM_POLICY)`, and it imports from `value_based_renewal` directly.

## Which runs grade which company

| runs | worktree / base | started | contains ba320e2d2 |
|---|---|---|---|
| `probe_obj_*` (objection on) | `/var/tmp/se-objrun` at `bf0d37c2f` | 2026-10-03 23:54 (`run_obj_queue.sh`) | **no** |
| `probe_term_*` (objection + cure on) | `/var/tmp/se-term2run` at `4bf859f0b` | 2026-10-04 02:30 | yes |

`se-objrun` was fast-forwarded to `5e8ebee87` at 01:25. That was after `obj_default` and
`obj_61001` had finished, and while 61002/61003 were mid-run, and Python had already loaded its
modules at start. So all four `obj` runs ran pre-flip code. The worktree's current HEAD does not
tell you which code ran.

**Consequences:**

- The objection grade in
  `records/SEAT_PREREG_THE_CHOICE_IS_HELD_DOWN_BY_A_TOO_STEEP_BELIEF_SO_LEARN_THE_SLOPE_UNDER_THE_DEFAULT_2026-10-03.md`
  ("REFUTED on 3 of 4; held on 61003") measures the **pre-flip company**: `segment_table` belief,
  with the channel-aware price. It does not answer whether the rule sits at parity with flat once
  the fidelity gap is closed, on the company at HEAD. A marker now sits beside the claim.
- The flat-in-advance grading (`191448824`) used the `term` runs. Those ran at `4bf859f0b`, which
  contains `ba320e2d2`, so that grade is **post-flip** and stands as measured.
- **A post-flip objection re-run is owed.** The `term` runs do not replace it. Against `obj` they
  changed at least three variables (the flip, the cure, and the term basis in the probe), and they
  have no objection-off partner at the same base. So no off→on difference can be attributed from them.

## Recommendation

Take the owed off/on pair on the **QEP-refit base** once that refit lands, not now. The QEP arms
retake is already re-sited at `96517e68c`, which contains `ba320e2d2`, in `/var/tmp/se-qep-arms2`.
Its three-arm leg is finished, and the three-seed floor `longjob-qep3-arms-floor` is running.
`191448824`'s own message says the refit will move every figure. A post-flip re-run on the
pre-refit world would be superseded within a day. Until then, read the `obj` table as a
pre-flip result.
