**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The publish wedge is seven days of ONE unresolved merge conflict, and the narrowing that deepens it has no ceiling

*Worker, 2026-09-17, on the shared tree. Drawn to confirm the publish gate re-grades itself now its
own suite is green; it does, and the reds were never what held it.*

BLOCKING, and the reason is named rather than assumed: `_publish_surface_collisions`' docstring
argues its case on the live state of the reconciler — *"`origin_reconcile` now closes the fork
unattended on the deadman cadence ... a disjoint commit is one it absorbs without a judgement
call"* — and that premise had **already been false for five days when the sentence was written.**
A live control whose stated justification is wrong about the live state is an untrustworthy
instrument, whatever its code does.

## What was drawn, and what is true

The item said `.publish_gate_state.json` still carried 12 blocking tests from the repaired
ledger-guard set, and predicted the remainder would attribute to the HEAD ref-lock loss
(`cannot lock ref HEAD: is at aff4b153f but expected 56d746816`).

**Both halves are spent.** Measured at the start of this turn:

* `total_red: 1`, and the one remaining blocking test is
  `test_a_behind_origin_publish_refuses_instead_of_deepening_the_fork.py::test_a_level_tree_still_publishes`,
  which runs `10 passed in 0.17s` here. **The gate DID re-grade; no red the item named is live.**
* The latest `liveness_surface_refusal` names `push_never_landed`, not a ref-lock. No ref-lock
  collision appears anywhere in the live record.
* `last_clean_publish: null`, `wedge_since: 1789011039.7` = **2026-09-10T03:30Z — seven days.**

## The cause, in one line

`origin/main` (6c1e769b4) and the shared tree's HEAD (1a69fbb23) are **forked** — 7 behind, 9
ahead, neither an ancestor of the other — and `origin_reconcile` refuses to close it because the
merge **conflicts**:

    REFUSED_CONFLICT between 1a69fbb23 and 6c1e769b4 -- 2 conflicted path(s), nothing was committed:
      tests/background/test_the_liveness_surfaces_refusals_left_only_an_orphaned_log_line.py
      tests/tools/test_the_weather_store_validator_cannot_pass_a_skipped_leg.py

That refusal is **correct and deliberate**: *"an automatic reconciler must not pick"*
(`tools/surgical_land.py`). Resolving two lanes' edits to one file is a judgement, and the module
hands it to a person. **Nobody took it for seven days.**

It is not that nothing noticed. `docs/staging/WORKER_FINDING_REPEATING_ALARM_DEADMAN_ORIGIN_FORK_2026-09-15.md`
is the [ORIGIN FORK] alarm having **fired 46 times over 101.9 hours**, on the same
`REFUSED_CONFLICT` condition with different paths, first seen 2026-09-11T01:30Z — and it escalated
itself into the draw exactly as designed. **The alarm worked; the queue it escalated into was not
drained.** So this is not a missing-instrument finding. It is a finding about what happens between
a correct refusal and a human judgement, when the thing in between has no bound.

## And what happens in between is UNBOUNDED DEEPENING

`_divergence_refusal` was narrowed on 2026-09-16: when origin's incoming paths do not collide with
the publish paths, the publish commit is created anyway. Measured here — `_commits_origin_is_ahead_by()`
= 7 and `_publish_surface_collisions(['site/data'])` = `[]`, so the narrowing fires on every cycle.

The local side of the fork is what that produces. **The same two commit shapes, twice, an hour
apart:**

| commit | time | what |
|---|---|---|
| 7c28ea31f | 02:54 | `site/data/publish_provenance.json` — verification-paused banner |
| 882ef8aad | 02:56 | `agent_status.json` + `tick_heartbeat.json` — liveness heartbeat |
| 8a7be23f0 | 03:56 | the SAME banner, same `git=761daca4c` |
| 1a69fbb23 | 03:58 | the SAME heartbeat |

Four unpushable commits out of nine. `git push` needs a fast-forward of origin's ref, and **path
disjointness has no bearing on pushability** — a commit created while origin is 7 ahead cannot be
pushed whatever it touches. The narrowing's own docstring says so and delegates the bound:

> **THE BOUND THIS DOES NOT REMOVE.** Publishing while behind still widens the fork by one commit
> per cycle, and if the reconciler stops, that grows without limit ... the deadman's [ORIGIN FORK]
> page is still the alarm that this has stopped being true.

The reconciler *had* stopped — five days before that sentence was committed. The alarm fired 46
times. Nothing stopped the growth, because **an alarm is not a ceiling.** This is the 2026-09-01
incident (`the retry is the thing that widens the fork`) recurring through a door opened on
2026-09-16, in the file whose name is that this cannot happen — and its named control,
`test_a_level_tree_still_publishes`, is green, because the control asserts the narrowing rather
than the property the filename states.

## The repair, in two parts

1. **The instance** — resolve the two conflicted paths and close the fork. Both are duplicate
   landings of the same W1_14 work by two lanes, and in **both cases origin's version strictly
   contains the local one**, verified hunk by hunk: origin's liveness fixture models
   `git merge-base --is-ancestor` explicitly with `is_ancestor` defaulting to False and a
   refusing catch-all (the local commit `a7f9abaad` did the same repair identity-only, in 8 lines);
   origin's validator suite is the local file plus `test_a_leg_NOT_ASKED_FOR_is_never_counted_as_a_pass_either`
   and one extra assertion, over a `tools/validate_weather_world.py` that is byte-identical on both
   sides. Nothing local is lost by choosing origin's bytes. *Done in this turn — see the RESULT
   beside this document.*
2. **The class** — the narrowing needs a **ceiling, not an alarm**: refuse the disjoint publish once
   the local side of the fork already holds an unpushed commit from the same publish path. One
   deepening is a bet on the cadence; the second is evidence the cadence is not running, and that
   evidence is already in the tree where the guard can read it (`git rev-list origin/main..HEAD`).
   Keyed to the property — *"never create a second unpushable copy of the same surface"* — so it
   stays true when today's fork is closed. **Not done in this turn, and it is the next piece.**

## Falsifiers

* `tests/background/test_a_behind_origin_publish_refuses_instead_of_deepening_the_fork.py` — if a
  control there asserted the *property* its filename names rather than the narrowing, the four
  commits above could not have been created. It has no leg over a fork the local side has already
  deepened once.
* The claim that disjointness does not confer pushability is settled by
  `.publish_gate_state.json:liveness_surface_refusal`, which records `push_never_landed` for
  `8a7be23f06d4ad0...` — created under the narrowing, refused by origin's ref.
