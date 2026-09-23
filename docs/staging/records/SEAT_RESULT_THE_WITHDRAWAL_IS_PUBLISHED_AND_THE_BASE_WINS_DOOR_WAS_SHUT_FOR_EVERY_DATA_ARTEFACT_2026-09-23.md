**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS_stale_copy_refusal`

# The withdrawal is published, and the base-wins door was shut for every data artefact

**Claim:** `publish-the-withdrawal-the-belief-leg-did-not-survive`
**Landed:** `e5e57c19a`, `0690bcd68`, `5c11201e7` — all three at `origin/main`.

## What DONE asked for, and where each part stands

| the criterion | state |
|---|---|
| the panel renders "does not survive pooling" and "does not survive a second draw" | **done** — `e5e57c19a` |
| the figures at origin rather than three commits behind it | **done** — all three commits promoted |
| the three named paths out of the stale-copy census's WOULD REVERT list | **one of three**, and the other two are refused for a stated reason |
| `last_clean_publish` inside this stretch | **NOT DONE** — still 2026-09-21 19:15, `episode_clean_publishes: 0` |

**`last_clean_publish` has not moved and I am not going to dress that up.** The four reds the gate
NAMED are repaired and mutation-proven, but the gate runs 258 blocking test files and a red it never
reached is still a red. What changed is that the wedge now has a measured cause at HEAD instead of a
`red_at_head: "not_established"`.

## 1. The withdrawal reached the page

The producer landed the withdrawal at `d533d9a93`; the published feed never did — `site/data/
value_arms.json` at HEAD was last regenerated at `943b9b4f9` and still served the pre-withdrawal
reading. **The one claim this company exists to test was answered, and the page went on serving the
answer we superseded.** Regenerated at HEAD: `the_verdict_survives_pooling` false, `the_leg_holds_
across_draws` false, both clauses in the headline sentence, both derived from the figures.

One site door red on the way, and it was mine. `test_every_figure_in_the_block_is_the_FEEDS` mutates
`belief.auc` and asserts the old figure is gone from the render. That figure used to have one home;
the withdrawal gives it three — the numeric field, `repetition.draws[].auc`, and the derived
`sentence`, which quotes the first draw's AUC back to the reader in words and which the page renders
verbatim. **A control that reds because the feed got RICHER is backwards.** Fixed by making the
mutation total rather than by dropping the assertion — see the commit.

## 2. The publisher's four reds: one refactor, four blind controls

Written up in full at `records/SEAT_RESULT_THE_PUBLISHERS_FOUR_REDS_WERE_ONE_REFACTOR_AND_EVERY_
PROPERTY_THEY_GUARD_WAS_INTACT_2026-09-23.md`. The short version: `cc5cc0032` wrapped
`generate_dashboard_json`, all four controls `inspect.getsource` the wrapper, every property they
guard is intact in the body, and **three of the four said "keyed to the property" in their own
docstrings.** A control keyed to a property of the WRONG FUNCTION is pinned after all.

## 3. `--base-wins` was shut for every data artefact, in two independent ways

The drawn item said `refresh_to_head` refuses all three feed inputs and `--base-wins` refuses them
identically, and that the door is therefore SHUT for this population. **That reading was correct
about the symptom and the door is now open for the part of the population it was built for.**

**First:** `judge_copy`'s `DATA_SUFFIXES` branch returned unconditionally on `supplies`, several
screens above the `base_wins` consultation — a `.json` path never reached the flag at all. And a
JSON leaf name carries its own VALUE, so a regenerated artefact "supplies" every leaf it holds by
construction. A stale regeneration is exactly what the flag exists to discard and was the one copy
that could never get to it. The two `ladder_churn_factors` copies carry **zero** structurally novel
keys; all 2,706 and 14,236 "supplied names" are changed values of keys the base already has.

**Second, and it would have survived fixing the first:** the Python branch gates on `judge`, whose
first line is `suffix not in READABLE -> None`, and `READABLE` is `.html/.js/.py`. **`judge` is
structurally unable to have a complaint about a `.json`** — and a field structurally unable to
answer a question agrees with every answer to it. Routing data paths to the same gate would have
restored an equally dead branch. The module's own docstring says the flag "is gated on the CLOCK
(`BASE_WINS_RULES`)"; `clock_judge` is the oracle that name refers to, and it reads all three live
files as `predates_landing_by_clock` / `predates_landing_carrying_some` where `judge` reads all
three as no complaint. The data branch now asks `clock_judge`.

Both sides of the partition were proven reachable **on the live files before any control was
written**, and three controls carry it. The admitting leg asserts the DEFAULT still refuses the same
copy, so it proves the flag moved rather than that the door was open.

`docs/observability/svt_drift_belief_grade.json` is now byte-identical to `origin/main` on the
shared tree and **CLEAR** of the census, preserved at
`refs/preserved/refresh-to-head/publish-the-withdrawal-2026-09-23` (`859e9672b`) — verified to still
carry the `years_disagreeing` block it was the only copy of. **That file is the one that mattered:
it carries the `stratification` block the pooling clause is derived from, and the publisher reads
the WORKING tree. A publish taken before this would have degraded the withdrawal to
`available: False` on the live page.**

## 4. What I deliberately did NOT do, and it is the next decision

**The two `ladder_churn_factors*.json` copies are still refused, by name, as
`predates_landing_carrying_some`.** `BASE_WINS_RULES` admits `PREDATES` and `CLOCK` and excludes
`PARTIAL`, and I did not widen it.

`PARTIAL` means the copy holds *some of the landing's distinctive lines*, so it MAY have been
written on top of it and edited. For a `.py` that is a real and load-bearing distinction — the rule
exists because one coincidental carried line once vouched a fifty-two-line revert. **For a document
where a line is a VALUE and not a statement, it is not obvious the sentence means anything at all.**
Two regenerations of the same report will share `  "alpha": 10,` whenever the figure did not move,
and that is coincidence of arithmetic, not evidence of derivation.

**That question is a judgement about what evidence means, inside a door that DISCARDS bytes, and it
should not be answered silently by the lane that happens to want the files cleared.** It is filed
rather than assumed. The measurement that would settle it: across the tree's data artefacts, what is
the distribution of carried-line share, and is it bimodal the way the `.py` population was (12 at
exactly 0, 37 at exactly 1, 17 between)? If data artefacts are NOT bimodal, `PARTIAL` is not a
usable signal for them and the rule needs a different reading for `.json` — not a widened tuple.

## 5. Two oracles disagree about the same three files, and both are live

`clock_judge` reads all three as predating their landings. **`judge` reads all three as no
complaint.** Both are called "the stale-copy control" in different places, and `refresh_to_head`'s
gate called the one that cannot see data. This is repaired at the one call site I measured. **It is
not established that this is the only place the wrong one is asked**, and `judge` is the more
commonly reached name. Worth a census of its callers against the suffixes they actually receive.
