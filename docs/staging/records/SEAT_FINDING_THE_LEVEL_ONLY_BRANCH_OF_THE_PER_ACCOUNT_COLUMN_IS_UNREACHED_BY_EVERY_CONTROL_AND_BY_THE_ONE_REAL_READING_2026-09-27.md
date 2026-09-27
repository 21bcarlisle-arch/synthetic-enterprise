**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`
**Class:** `controls_that_cannot_fail`

# The level-only branch of the per-account column is unreached by all 24 of its controls, and was unpeopled in the one real reading too

**2026-09-27.** The per-account selection column landed at `ca80a7d0a` with 25 controls. This is
the gap those controls leave, found by grading them rather than by reading them.

## The defect

`selection_by_account` partitions every billing account into three states: settled in **both**
arms, in the **value arm only**, or in the **level arm only**. The third is the one a reader gets
backwards — it is net the value arm did not earn, so it enters the residual **negative**.

Across **every** landed fixture the level roster is a strict subset of the value roster. The single
control that names the branch, `test_an_account_settling_in_one_arm_only_is_carried_and_split_out_as_a_ROSTER_difference`,
asserts `accounts_only_in_the_level_arm == []`. So the branch is never peopled, and this is the
exact shape CLAUDE.md names: *assert the rare branch CAN be taken before asserting what it does.*

**And the real data did not cover it either.** The truncated 2016–2017 reading recorded in
`SEAT_STATUS_..._TWO_SEED_DIFF_IS_IN_FLIGHT` has `accounts in one arm only: 1 (C5_2, value arm)`.
Zero level-only accounts. A defect here would not have shown up in the only real artefact so far.

## The mutation proof

Two mutations of `selection_by_account`, each run against the 24 pre-existing controls and against
the new one:

| mutation | 24 pre-existing controls | the new control |
|---|---|---|
| `only_level = []` — level-only accounts dropped from the roster split | **24 passed** | **failed** |
| `accounts = sorted(set(value_net))` — the union is the value arm only | **24 passed** | **failed** |

The second is the serious one: the column silently drops every account the level arm settled and
the value arm did not, and the residual it publishes is short by their whole net. It does not trip
the reconciliation leg either, because the identity that leg checks against is computed from the
same two arms.

## The remedy

`test_the_roster_partition_is_reachable_in_ALL_THREE_states_at_once` — one control over the whole
partition, peopling all three states in one fixture and asserting the peopling **first**, then the
signs, then that the roster/shared split still partitions the residual when the roster half carries
both signs. Keyed to the property, not to today's book.

## The drawn item's premise was spent, and the tree was blocked on its leftovers

The drawn work (*carry a per-account selection column out of the three-arm runner*) **landed at
`ca80a7d0a`** before this invocation drew it. It was not redone.

What remained was its residue. The shared tree carried a **02:07 draft** of
`tools/run_value_cycle_ab.py` and `tests/tools/test_run_value_cycle_ab.py`, older than the 04:53
landing, and those two files were **the only thing blocking the shared checkout from
fast-forwarding 5 commits** — every lane's landing and the publish path with it.

Disposition: **the base wins on both**, deliberately, and the drafts are preserved at
`refs/preserved/stale-arm-runner-draft-20260927/{tool,tests}` plus
`refs/preserved/refresh-to-head/stale-arm-runner-draft-20260927`. Not a sweep — the evidence:

* the tests copy supplies 8 names and drops 14; the door itself graded the 8 as *"the older draft
  of the 14 it drops"*;
* the tool copy's 13 draft-only dict keys all have origin counterparts — `accounts_folded` →
  `accounts_in_the_union`, `column_total_gbp`/`published_selection_gbp`/`identity` →
  `residual_gbp`, `gross_absolute_contribution_gbp` → `gross_absolute_movement_gbp`,
  `accounts_only_the_{value,level}_arm_settled` → `roster_difference.accounts_only_in_the_*`, and
  the two `*_unavailable_because` fields → origin's **raise**, which is the stricter design;
* the draft's `renewals_priced_by_account` is a duplicate of the key origin computes through
  `_priced_terms_by_account`, which additionally ranks depth against money.

**The one property the draft had and the base did not is the three-state partition control — and
it is not discarded, it is rebuilt against the surviving API and mutation-proven above.** That is
what makes this disposition lossless rather than a base-wins that orphans work into a ref nobody
reads.

`refresh_to_head` refused the tool path on the dict-key reading and said *"establish by hand which
side is the later draft … if origin/main is, this is the refusal to override."* Established by
clock (02:07 vs 04:53) and by the mapping above; overridden by hand; recorded here.

## What is still in flight

`longjob-two-state-account-diff-20260927` (seeds 11111/88888, full window) was still running at
05:39 BST, 1h10m in against a ~2h expectation. Nothing here grades it. The four commands that read
it are in `SEAT_STATUS_THE_PER_ACCOUNT_SELECTION_COLUMN_IS_CARRIED_AND_THE_TWO_SEED_DIFF_IS_IN_FLIGHT_2026-09-27.md`,
and **P0 is graded first** — if the reproduction fails, the diff is between two worlds and the rest
is void.
