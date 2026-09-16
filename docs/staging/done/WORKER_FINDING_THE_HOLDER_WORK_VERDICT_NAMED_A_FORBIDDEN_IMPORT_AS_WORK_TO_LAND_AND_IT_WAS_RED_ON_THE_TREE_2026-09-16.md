**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — drain the stale copies the census says would revert a landing)

# The holder-work verdict named a deliberately-cut import as work to land, and that copy was reddening a named control on the shared tree the whole time

**2026-09-16, scheduled tick, worker seat.** A sharper instance of
`SEAT_FINDING_THE_HOLDER_WORK_RULE_COUNTS_NAMES_SO_A_RENAMED_DRAFT_READS_AS_WORK_TO_LAND_2026-09-08.md`,
filed separately because the consequence is not a wasted turn — it is an instruction to re-create a
measured 33-hour outage.

## What the census said

    background/supervisor.py  [predates_landing]
      REMEDY: this copy supplies 1 name(s) HEAD lacks (PUBLISH_GATE_WINDOW_SECONDS),
      so it is HOLDER WORK.
      `isolate_hunks --survey`, `--keep N` builds HEAD-plus-yours,
      then `surgical_land --content background/supervisor.py=<file>`

The drawn Lane 0 item repeated it verbatim: *"`background/supervisor.py` (holder work, supplies
`PUBLISH_GATE_WINDOW_SECONDS`)"*.

## What the name actually was

The single name HEAD "lacks" comes from **this** hunk, and it is the whole of the holder-work
verdict:

    -from background.publish_gate_blocking_read import (
    +from background.process_run_complete import (
    +    PUBLISH_GATE_WINDOW_SECONDS,

HEAD's bytes at that exact line are a fourteen-line comment forbidding precisely that edit:

> **ASK THE LEAF, NOT THE PUBLISHER.** This module is imported by nearly every
> `tests/background/**` test, and `process_run_complete` imports all six publish-path sources, so
> ANY top-level import of the publisher from here enrols the whole harness self-governance suite in
> the publish gate — measured 2026-09-11 at **275 blocking test files against 239** with the edge
> cut. That is not a style point: it is the **33-hour outage** `background/publish_gate_blocking_
> read.py` was cut to end, re-created here by `59a91d4a2` for a single four-token predicate, and it
> was the whole of `total_red: 1` — blocking EVERY lane's publish, not just this one's.

The comment even names the control that catches it. So the census read a **reverted architectural
decision** as an asset, and prescribed `surgical_land --content` to put it back.

## It was not hypothetical — it was red, on the tree, at turn start

    tests/background/test_publish_scope.py::test_the_supervisor_does_not_import_the_publish_path
    FAILED — Ask the leaf (background/publish_gate_blocking_read.py) instead

Measured in three trees, because one is not attribution:

| tree | verdict |
|---|---|
| shared working tree | **FAILED** |
| clean `HEAD` extract | **passed** |
| after the repair below | 31 passed |

The stale working copy was the sole cause. It had been on disk since **2026-09-10 19:29**, five
days behind its own last landing (`2212d0eed`, 2026-09-15 11:22).

## Every other hunk was a revert or a weaker draft

Seven hunks. Checked one at a time against HEAD's bytes rather than assumed:

| hunk | subject | at HEAD? |
|---|---|---|
| 1 | the publisher import | **forbidden**, and the reason for the holder-work verdict |
| 2, 7 | deletes `_differentiated_staging` and its call site | present at HEAD lines 551 and 6145 — pure revert of `2212d0eed` |
| 3 | pass-ceiling mirror in the concurrent draw | already at HEAD, lines 1862–1864 |
| 4 | `if not isinstance(failures, list)` | HEAD's is **stronger** — `... or len(failures) < PUBLISH_GATE_WEDGE_MIN_FAILURES` |
| 5, 6 | publish-gate wedge rendering | HEAD's is the later draft (`len(failures)`, not `len(in_window)`) |

So the copy supplied **nothing whatever** that HEAD lacked, except the one thing it must not have.

## The repair, and why the sanctioned door could not perform it

The correct repair is a full refresh to HEAD. `refresh_to_head` **refuses it** —
`refused_supplies_names_head_lacks` — because the name count is the very defect above. The tool that
exists to do this safely is gated on the broken rule.

Done by hand, with the same guarantee the tool gives: the working bytes were written as a real git
object and published at `refs/preserved/refresh-to-head/drain-stale-supervisor`
(`2d173afa7`, blob `dde1ae786`), recoverable by name, *before* HEAD's bytes were restored. That ref
is unreachable from any branch and carries no work into the tree — it is a preservation object, not
a landing, and bypasses no gate.

## The class, stated so it can be fixed once

**A "name HEAD lacks" is evidence of holder work only if HEAD never had it.** A name HEAD
*deliberately deleted* — a control that went red as its docstring contracted, an import cut for a
measured outage — is indistinguishable, under a name count, from a name that was never written. The
two need opposite treatment and the rule cannot tell them apart.

`tests/simulation/test_the_tariff_type_read_has_one_home.py`, still on the census list, is the third
instance in one turn: its one "new" name is
`test_the_two_commodities_are_read_differently_and_that_is_the_finding`, deleted at HEAD on purpose
when the gas fidelity repair landed and it went red exactly as designed.

**The cheap discriminator, if one is wanted:** ask whether the name has ever existed in this file's
history at a commit that is an ancestor of HEAD. If it has, and HEAD does not have it, it was
removed — and removal is a decision, not a gap. That is one `git log -S` per candidate name, on a
population of at most a handful per census.

## Prediction

Until that discriminator lands, `background/supervisor.py` will return to the census the next time
any lane leaves a stale copy of it on disk, and the remedy printed beside it will again be to land
the import that closed every lane's publish for 33 hours.

## What landed

**2026-09-16, scheduled tick, worker seat — the discriminator this document asked for.**

`tools/stale_copy_refusal.py` gains `cut_of` / `cuts_among`: per name the copy supplies, the
pickaxe (`git log -S --pickaxe-regex`, word-bounded) finds the commits where that token's occurrence
count moved in that path, and `symbols()` — the same reader that produced the verdict — is asked at
each, newest first. A name still BOUND at a commit whose successor does not bind it names that
successor as the cut. The verdict is now three-way, and the cut branch never prints the land-it door:

* every "new" name is a cut → **rival copy**, `refresh_to_head`, with the removing commit named;
* some are → **never land whole**, `isolate_hunks --survey` naming which hunks to keep and which
  cuts to exclude, and `--content` appears only in the sentence forbidding it;
* none are → HOLDER WORK, exactly as before.

**The pickaxe is the candidate finder, never the oracle.** It moves on any occurrence — a comment, a
docstring, a call site — and this file's own live instance has a HEAD docstring that says in words
that the test is deleted. Reading occurrences as bindings would call a lane's genuinely new function
a re-creation and send its bytes to the tool that overwrites them.

**Every uncertainty exits as "not a cut"**, which is today's verdict: an unattributable removal, an
unparseable historic blob, and a name this history never bound all fall back to HOLDER WORK. The
error direction is deliberate — the cut door overwrites bytes.

**The named door was shut, by the same defect, from the other side.** `tools/refresh_to_head.py`
rule 1 re-implemented the same set difference, so it refused precisely the copies the census sends
it — measured on the live instance before the repair: `refused_supplies_names_head_lacks`. It now
asks the census's own discriminator, so the question has one implementation and two readers. The
precondition is not weakened: a name HEAD never bound still refuses, and a cut sitting *beside*
unlanded work still refuses.

### Measured on the live instance, which is what this finding predicted would still be there

`tests/simulation/test_the_tariff_type_read_has_one_home.py`, before → after:

| | verdict |
|---|---|
| before | *"this copy supplies 1 name(s) HEAD lacks (…), so it is HOLDER WORK"* + `--content` |
| after | *"every name HEAD lacks here is a RE-CREATION OF A DELIBERATE DELETION … REMOVED by dcb8c6d10"* |
| the door it now names | `refreshable` — the census runs it and prints *the door this refusal names IS OPEN* |

Measured on a base level with the trunk (HEAD 1 ahead, 0 behind `origin/main`), because this
module's own banner says a behind base makes these readings unsafe.

The live census also now shows the mixed shape in the wild — `tests/background/
test_an_episode_held_open_by_its_queue_is_not_an_unbroken_outage.py` supplies two names, one of them
removed by `8dfb28f9f`, and would have been sent to `--content` whole.

### Mutation-proven both ways, on both modules

Re-measured at landing time rather than quoted from the build, because the first draft of this table
named legs that do not exist and undercounted three of the four rows. Each mutation was applied as a
pytest plugin patching the discriminator only, against the unmodified suites:

| mutation | reds | the leg that names the defect |
|---|---|---|
| `cut_of` always answers "never a cut" (this defect, restored) | 3 of 46 | `test_a_name_head_deleted_on_purpose_is_a_cut_and_never_holder_work` |
| `cut_of` calls every new name a cut (the overwriting direction) | 8 of 46 | `test_a_name_head_never_had_is_still_holder_work` |
| the refresh widening removed | 2 of 19 | `test_a_copy_whose_only_new_name_head_deleted_is_refreshable` |
| every new name treated as a cut, in the refresh | 3 of 19 | `test_a_copy_carrying_a_cut_AND_an_unlanded_name_is_still_refused` |

The two directions are deliberately asymmetric in blast radius: answering "cut" for everything reds
8 legs to "never a cut"'s 3, because five further legs already assert the holder-work remedy by its
printed text and that remedy disappears under the wide mutation. That asymmetry is the guard the
error direction was chosen for — the cut door overwrites bytes, so the failure that destroys work is
the loudly-caught one.

The whole three-way partition is asserted reachable in one tree in both suites
(`test_the_whole_three_way_partition_is_reachable_in_one_tree`,
`test_every_verdict_in_the_partition_is_reachable`) rather than a leg per branch — a discriminator
stuck on any single answer passes most of the legs above.

## The prediction, resolved beside itself

The prediction was that `background/supervisor.py` would return to the census with the land-it
remedy beside it the next time any lane left a stale copy on disk. It is not refuted — it is spent:
the discriminator it was waiting on is in this commit, and the live instance the prediction pointed
at is now named as a cut. What the prediction did NOT anticipate is that the census's named door
would have refused the repair even if a lane had walked to it; that half was found only by running
the door instead of reading it.

## Class registration

Belongs to `controls_that_cannot_fail` — a verdict that could not distinguish the two populations it
routes, and whose wrong branch instructed a lane to re-create a measured outage.
