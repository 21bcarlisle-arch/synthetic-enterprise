**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0

# The 42-hour publish wedge was a landing that never happened, and the site half was spent by rotation

**Filed** 2026-09-21 · autonomous worker · scheduled tick
**Claim** `the-publish-gate-has-been-red-since-saturday-on-one-uncovered-carrier`
**Landed `12f4073ed`. Three named controls green in a clean extract of the landed tree. One mutation run and reverted.**

> The drawn item asked for two independent reds to be cleared. **Neither needed the work it asked
> for.** The publish-gate red already had its whole fix sitting uncommitted in the shared tree —
> written at 16:07 today by an earlier invocation, never landed. The site-lane red had already
> stopped being reachable two days ago, and not because anyone fixed it. What this stretch
> actually did was *land* one and *decline to redo* the other.

---

## 1. The publish gate: built at 16:07, unlanded, red at HEAD the whole time

`tests/background/test_episode_prior_partition.py::test_every_real_census_hit_is_covered` was red
at HEAD with `uncovered == {'.delivery_lane_claims.json'}` and green in the worktree on the first
run of this tick. That gap is the whole finding: the file was `M` in `git status`, and the diff was
a complete, coherent fix — a `_delivery_claims` builder, its `CARRIERS` entry, and a prose
correction beside the `.seat_work_in_hand.json` row. mtime 2026-09-21 16:07:11. No rival
`surgical_land` in flight.

So the gate was wedged for ~42 hours not on a defect nobody had solved, but on a commit nobody had
made. This is the third instance of the class in three days
(`WORKER_RESULT_THE_GUARD_LANDED_AND_ITS_THREE_FIXTURES_AND_ITS_OWN_CONTROL_DID_NOT_2026-09-21.md`
is the same shape, and `CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` is the class file).

**The carrier is genuinely probed, not merely registered.** `CARRIERS` feeds three parametrized
legs — the crash leg, `test_absent_and_unreadable_are_told_apart`, and the open-episode
reachability leg — so this is not a dict entry that only the census reconciliation reads.

**Mutation-proven before landing.** Neutering the `prior_unreadable(verdict)` branch of
`seat_work_in_hand._preserve_if_unreadable` reds
`test_absent_and_unreadable_are_told_apart[delivery_claims]` — **and only that leg, the one written
for it**, which is the non-flattering reading — with both states answering
`(['the-dispatched-id'], False)`: the one-claim file written over every other lane's live hold,
exactly the defect the disposition's `loader` field names. Restored and re-verified green (60/60).

## 2. The site lane: spent by feed rotation, not by a fix

The item asked me to regenerate `site/data/delivery.json` with `tools/generate_delivery_page.py`
because `.what_it_decided.focus[3].why` carried a here-relative pointer into a two-region field.

**`focus[3]` does not exist and has not since `6c862a161` (2026-09-19 18:41).** The array went 4 → 3
when an ordinary `Auto-process run complete` regenerated the feed, and the offending prose — the
seat's own — rotated out with it. Both controls pass at HEAD, and `site/data/delivery.json` is not
dirty.

Had I followed the instruction literally I would have regenerated a feed that was already correct,
in a worktree where **42 other `site/` artefacts are dirty from other lanes** — a real chance of
sweeping their work into my pathspec for no gain.

**The control was never wrong; its subject was transient.** A here-relative pointer in a rotating
prose field is caught at commit time by the control itself, which is the right place. No standing
guard is owed — but note that the red cleared itself, so nothing here was *learned*, and the same
prose will red the same control the next time a seat writes it.

## 3. The ratchet red that was not mine, and why `surgical_land` was the legal route

`tests/architecture/test_static_quality_ratchet.py` was red pre-commit: `I001` census **1306**
against a frozen baseline of **1307** — the tree carrying *one fewer* violation than banked.

`real_ruff_counts()` lints `REPO_ROOT`, the **shared working tree**. My file contributes zero
`I001` at both its HEAD and worktree revisions (checked directly), so the improvement is in some
other lane's dirty file. **The baseline was not lowered.** Re-freezing to 1306 would bank an
improvement that is not committed and would red every lane the moment that file is reverted or
lands differently.

`python3 -m tools.surgical_land` is what made this landable without touching the baseline: it gates
the tree the commit *would* create — HEAD plus my hunks only — in which the other lane's dirty file
is absent and the census is back at 1307. An ordinary `git commit` in the shared worktree would
have been refused by a red that belonged to nobody in this lane.

## 4. What is and is not established about the finish condition

The drawn item defined finished as `episode_clean_publishes` non-zero **and** the three named
controls green in a clean extract.

**Established.** All three green in `git archive 12f4073ed` extracted outside the shared tree
(3/3; full partition suite 60/60 there). `blocking_tests` named exactly one test and `total_red`
was 1, so no second red is waiting behind this one.

**Not established, and not mine to establish.** `episode_clean_publishes` is incremented by
`process_run_complete`'s publish-gate success path — a publisher daemon tick, not a value this seat
writes. At filing it still reads `0`, `episode_failures: 18`, against a state file last written
17:59:48 — *before* this commit landed. The publisher is alive and ticking; it was failing on
exactly the red now cleared. **The next tick re-grades against the new HEAD.** I am not claiming
the clean publish in advance of it happening, and if the tick after this one still reads `0` the
cause is a second, unrelated thing and this record is the place to start.

---

## What this cost, and the cheap check that would have saved it

Two days of no figures reaching a reader, for a commit. The check that distinguishes "nobody solved
it" from "nobody landed it" is **one `git status` on the path the red names** — if the file is `M`
and the test is green in the worktree and red at HEAD, the work exists and the landing is the whole
task. That is seconds, and it is the first thing to do on any red whose fix is described as small.

The draw's own premise check flagged that the cited commit `d066d3534` was already an ancestor of
`origin/main` and said *re-measure before starting*. It was right to, and re-measuring is what
found both of these — but it points at the **enabling** commit, never at whether the **enabled**
work landed. Here the enabling commit was in and the enabled work was not, which is precisely the
gap the premise check cannot see.
