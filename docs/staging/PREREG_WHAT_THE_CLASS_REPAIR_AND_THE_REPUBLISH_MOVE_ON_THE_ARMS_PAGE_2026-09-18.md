**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# Pre-registration: what the class repair and the republish move on the arms page

**Filed:** 2026-09-18, BEFORE any of the measurements below were taken
**Claim id:** `republish-the-arms-decomposition-over-one-priced-book`
**Subject:** the five controls listed in
`docs/staging/SEAT_RESULT_THE_ARMS_NOW_PRICE_ONE_BOOK_SIX_CONTROLS_REFUSE_THE_REPUBLISH_AND_THREE_WERE_ALREADY_RED_2026-09-18.md`,
the `_leg_over_its_own_family` staleness thread, and the promotion of
`docs/observability/value_cycle_ab_s1_three_arm_20260918.json` to `THREE_ARM_PATH`.

---

## The premise, re-measured before starting

- `47d3115f7` **is already an ancestor of HEAD** (`8abbe4f2d`), and HEAD is level with `origin/main`.
  The drawn item's "merge origin/main first, HEAD is one behind" clause is **SPENT**.
- The claim it made about that merge is nevertheless **verified rather than taken on its word**:
  `pytest tests/tools/test_the_renewal_funnel.py` → **24 passed**. The three legs the 09-18 result
  doc recorded as red at HEAD are green. Owed item 1 of that doc is discharged by another route.
- The duplicate-work check named `the-product-gate-census-answers-per-record-while-the-guard-refuses-per-term`.
  Read: its subject is the per-term decision population split, not the arms republish. **Genuinely
  different work on the same files** — carrying on, as the draw note licenses. Its writer (pid
  2436269, started 11:17) had not touched `tools/generate_value_arms_data.py` (mtime 09:58),
  `site/data/value_arms.json` (10:41) or the 09-18 artefact (07:57) as of 12:46.

## The state the five reds were reproduced in

Promoting the 09-18 artefact to `THREE_ARM_PATH` in this isolated worktree reproduces exactly the
five: **5 failed, 239 deselected**, at `:343`, `:563`, `:4170`, `:5682`, `:6870`.

## The diagnosis, stated before the repair

All five are one class and this file has already paid for it once. `_stamped_after` (`:4901`)
exists because **ten** controls once went red reporting the failure of the guard they name rather
than the one that fired: the live floor is dated and `THREE_ARM` is a moving pointer, so promoting a
newer run makes `_staleness_caveat` refuse first and every downstream guard's subject disappears.
Three of the five (`:343`, `:563`, `:6870`) are the controls that never got that treatment. The
other two (`:4170`, `:5682`) key a **constructed witness to which side of zero the live run happens
to sit on**, which is a property of which run is promoted.

## Predictions

**P1 — the repair is symmetric.** Each repaired control goes green on the promoted 09-18 feed AND
stays green with the promotion reverted to the 09-08 run. A repair that is green in one state only
is an accommodation of one run, which is the defect wearing the fix's clothes. *This is the
prediction that can most easily be wrong: `:4170` and `:5682` have their witnesses rebuilt relative
to the subject, and if the subject sits exactly at the boundary (`share == 0.5`, `centre == 0`) the
construction has no other side to reach for.*

**P2 — repairing the five does NOT make the gate green.** I predict at least one further red on the
regenerated feed, and name it: `test_replicating_the_rows_moves_the_null_and_not_the_answer`
(`escaped_at` is `None` where `<= 8` was expected). If the gate is green with only these five
touched, this prediction is refuted and the 09-18 result doc's ninth row was mis-attributed.

**P3 — the staleness thread changes what the page says about membership.** The two sentences at
`tools/generate_value_arms_data.py:3779` and `:3874` currently assert `single_run.gbp` "is one
member of the 18" while the same block publishes `single_run_inside_the_family: false`. With the
staleness answer threaded in as a REQUIRED parameter, I predict the rendered `error_bar.reading` on
the regenerated feed **no longer claims membership** when the family is pre-fix (09-17) and the run
is post-fix (09-18).

**P4 — the page publishes the 09-18 book and refuses a direction.** On the regenerated
`site/data/value_arms.json`: `legs_on_one_bar.available` is `False` with
`why_no_leg_is_graded` naming the re-run as owed; the headline states no direction for the selection
leg; and the reversed residual (`selection_gbp` +4,327.01 against the published −332.64) is
published **with the page saying it cannot attribute it**. Publishing a reversed residual we cannot
attribute is correct; keeping a residual we KNOW is contaminated by 65 renewals the value arm
refused is not.

**P5 — what I will NOT be able to say.** Four commits touching the value arm landed between the two
runs and the level moved 20.00 → 41.00 on its own. **I predict the regenerated feed emits no
attributed cause for the reversal**, and that I will still not be able to attribute it at the end of
this turn. The one-variable run remains owed. If the page does emit a cause, this is refuted and the
cause is a finding.

## What would refute the whole exercise

A repaired control that passes only because its assertion was weakened. Every repair below either
constructs its own precondition or asserts a biconditional; none relaxes what was being asserted,
and each is checked in both promotion states.
