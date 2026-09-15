# Pre-registration — the belief graded against an outcome its own price did not cause

**Filed 2026-09-10, BEFORE the run that can answer it.** Nothing on disk carries
`belief_against_control_outcomes` yet: the field landed in `1d9e0a85c` and every one of the eleven
`value_cycle_ab_s1_three_arm*.json` artefacts predates it. So the answer is not merely unread here —
it does not exist, and this file is written into that gap on purpose.

The commit that added the field filed a prediction in prose: *"the two AUCs will **not** be far
apart."* That sentence cannot refute anybody. This file turns it into bounds that can, and adds the
checks whose failure would mean the comparison is not a comparison at all.

## The run

```
python3 -m tools.run_value_cycle_ab --level-arm \
  --out docs/observability/value_cycle_ab_s1_three_arm_20260910.json
```

Same shape as the run that produced the artefact now on the canonical path
(`value_cycle_ab_s1_three_arm.json`, byte-identical to `..._20260909c.json`): full window, three
arms. No flag is being changed to make this comparison; the field is simply one the earlier pass did
not write.

## The baseline this is graded against

From `value_cycle_ab_s1_three_arm.json` (`generated_at` 2026-09-09T13:58:12Z, world
`39a192ce04c1eda8`), `belief_vs_outcome`:

| quantity | value |
|---|---|
| `discrimination_auc` | **0.6270** |
| `auc_population` | 83 retained / 40 left |
| `scored_decisions` | 123 |

## P0 — the gate on the whole exercise, checked FIRST

**The new run's `world_identity.digest` must equal `39a192ce04c1eda8`.**

If it does not, the two AUCs are from two worlds and *no* comparison below is graded. This is not a
formality: `world_identity` is the departure level the world was running at, and a page that put a
0.6270 from one world beside a figure from another would be publishing a difference that is mostly
the world. **If the digest moves, I report that and grade nothing** — the honest result is "this run
cannot answer it", not a number with an asterisk.

## P1 — the primary prediction (the commit's, made gradeable)

**|`belief_against_control_outcomes.discrimination_auc` − 0.6270| ≤ 0.10.**

Why that bound and not a tighter or looser one: on the 2026-09-09 run, 4 of the 40 departures and 12
of the 123 scored rows sit on the accounts the two arms disagreed about. A rank statistic whose
population changes outcome-label on ~10% of rows should not move more than ~0.10 unless the moved
rows are concentrated at one end of the ranking. **A swing beyond 0.10 would be telling us about the
sample, not about the belief** — and I would report it as such rather than as a finding about
inference.

## P2 — the direction

**`discrimination_auc` > 0.5.**

If the belief carries information about who leaves, it should carry it in a world where the arm's
own price rise is not part of the outcome. **A figure at or below 0.5 refutes the thesis** in the way
the block was built to allow, and it would be the more interesting result of the two.

## P3 — the risk I actually expect to bite, named before it does

**`scored_share_of_priced` ≥ 0.5.**

This is the one I am least sure of and it is not about economics. The match is an exact key —
`(customer_id, term_start)` from the value arm's log against `(customer_id, event_date)` on the
control arm's `customer_events`. Both arms run the same households in the same world, so most keys
*should* find an event. But nothing has ever exercised this join on a real pass.

**If this comes back far below 0.5, the key is the finding and the AUC is not worth quoting** — a
concordance over a small unrepresentative matched residue is exactly the shape this project keeps
paying for. In that case P1 and P2 are recorded as ungraded, not as passed or failed, and the next
item is the join, not the page.

## P4 — what does NOT move, and why that is a real prediction

**`belief_vs_outcome.discrimination_auc` stays 0.6270** and
`_grading_population_independence.outcome_moved_by_the_arms_own_price` keeps naming the same four
accounts (C5_2, PROS-2019-0024, PROS-2021-0324, SYN-2016-034).

These are computed from the value arm alone and the roster diff, neither of which the new field
touches. If they move, something other than the new field changed between the two runs and P1's
difference is not attributable — I would have two changed things and no way to assign the result,
which is the situation this project has a rule about.

## What reaches the page either way

`_independent_grading_today` already reads `available` off the artefact rather than pinning it, so
the page moves on its own when the artefact carries the field. **The population caveat stays on the
available branch regardless of the number** — the outcome becomes independent, the population does
not, and a reader who takes the second from the first draws a conclusion no run on this book
supports.

---

## GRADED, 2026-09-10 — appended after the run, and nothing above is revised

Full result:
`docs/staging/SEAT_RESULT_THE_INDEPENDENT_GRADING_EXISTS_AND_AGREES_AND_THE_ONLY_CLEAN_COMPARISON_IS_WITHIN_A_RUN_2026-09-10.md`.

| | outcome |
|---|---|
| **P0** world digest `39a192ce04c1eda8` | **HOLDS** |
| **P1** \|Δ\| ≤ 0.10 | **HOLDS** — but see below; the comparison as written is confounded |
| **P2** AUC > 0.5 | **HOLDS** — 0.6237 |
| **P3** `scored_share_of_priced` ≥ 0.5 | **HOLDS** — 0.558, the thinnest margin here |
| **P4** the untouched figures do not move | **REFUTED** |

**P4 is the one that earned its place.** `belief_vs_outcome.discrimination_auc` went 0.6270 → 0.6148
and its population 83/40 → 85/39. The disagreement set was exactly right — the same four accounts
and the same one — so the half of P4 that was about the new field held; the half that assumed a
fresh pass reproduces a figure it does not touch did not.

The tree moved between the runs (`8b846013e` → `9cf9d16ed`) and the arm's behaviour moved with it:
`priced` 214 → 215, `distinct_margins` 63 → 74. Two things differ, so the move is **not
attributable** to either alone, and I am not picking the flattering one.

**What P4 bought.** It caught that P1's stated comparison — against the *previous day's* run — was
never one-variable. The clean comparison is within a single pass: 0.6237 against 0.6148, same tree,
same book, same 215 priced decisions, differing only in which arm's outcome the belief is scored
against. That is what the page publishes. Had P4 not been filed, the cross-run figure would have
been reported as a clean result, and it is not one.

**The reasoning error, kept because it is the transferable part.** I argued P4 from *the new field
does not touch these figures* — true, and not the question. **Conceptually separate is not
invariant.** A "will not move" has to be argued from what holds the value fixed, and nothing here
did.
