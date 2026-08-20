**Severity:** LATENT · **Lane:** H_harness · **Status:** cause found, repair landed, tree cleared; the writer that resurrects the file remains unidentified

# The two-rooms repair was blind to the third room, so it reported success while every commit in the tree stayed refused

The name was the defect. `background/staging_two_rooms_repair.py` pairs the staging root
against `done/`. There are three rooms, and `background/finding_classes.py` — the detector
whose refusal the repairer exists to clear — refuses on **all three pairings**. Its own
docstring says so, and records that it was widened to do that on 2026-08-12 after a hand
census run root-vs-`done/` declared zero while root-vs-`in_progress/` held one.

The repairer was built on **2026-08-19, after that widening**, and still knew two rooms. So
the room CLAUDE.md instructs you to park an open finding in was the one room the automatic
repair could not see.

## Observed, in one measurement, with one duplicate of each shape live at once

    $ python3 -m background.finding_classes --check
    TWO ROOMS WORKER_FINDING_EIGHT_DELETED_PAGES_..._2026-08-20.md: present in in_progress AND root
    TWO ROOMS run_complete_20260820T085957Z.md:                     present in done AND root
    check: FAIL (2 failures)

    $ python3 -c "from background import staging_two_rooms_repair as tr; print(tr.observe())"
    {'changed': True,
     'verdict': 'removed 1 redundant staging copy/copies already archived: run_complete_...'}

No `alarm` key. The repairer cleared the `done/` half, reported success, and the tree stayed
refused by the half it cannot see — while the worker loop that calls `observe()` every cycle
would have gone on reporting that same success hourly.

That is the **fail-silent** pattern from R15, sitting in the report rather than in the check.
The verdict could not distinguish *"I cleared everything"* from *"I cleared the half I can
see"*, and those two states are the ones a reader most needs told apart.

## Why this was drawn, and what it says about the draw

This tick's RUNG-1c BLOCKING draw was
`WORKER_FINDING_EIGHT_DELETED_PAGES_ARE_STILL_SERVED_TO_READERS_2026-08-20.md`, read from the
staging root. **That root copy was a resurrection.** `git hash-object` on it returns
`db6a76bcd9f33d1c7107b6ec0a6b6e3a9d03e740`, byte-identical to the pre-move blob at the parent
commit `5b1359b74`; the previous tick had moved that finding to `in_progress/` in `733b4491b`,
where the tracked copy carries a prepended correction (nine ghosts, not eight) and states the
two genuinely open sub-items. The root copy was **untracked** and 19 minutes newer.

So the highest-priority lane in the machine was dispatched by a file that no commit contains,
carrying a headline its own author had already retracted. The doorbell reads the loudest copy,
and the loudest copy is always the root's — which is exactly the contradiction the detector
refuses on, and exactly the one the repairer could not reach.

There is a symmetry worth stating: the drawn finding is about a **stale cached copy served as
if it were live, by a surface that cannot tell absence from staleness**. The draw that surfaced
it had the same shape.

## The repair, and why widening the room set does not widen what it deletes

`duplicates()` now returns one row per **pairing** involving the root copy — root-vs-`done/`
and root-vs-`in_progress/` — and `repair()` groups them back by root copy so a document in all
three rooms is removed once, not twice.

`classify()` is **unchanged**. It remains the narrow containment predicate: delete only when
the other room's copy wholly contains the root copy's text. The live instance is precisely why
that timidity is load-bearing — the parked copy has a correction *prepended*, so the root text
is **not** contained in it, `classify` returns CONFLICT, and the correct output is a shout
rather than a delete. Measured: `root content contained in in_progress? False`.

`done/`-vs-`in_progress/` is the third pairing and has no root copy to remove. Nothing there is
safely deletable, so it is reported rather than repaired — but it **must** be reported, because
the detector refuses the tree on it and silence from the repairer reads as a clean tree.

Detection and repair keep their opposite failure directions, as the module's docstring
requires: the detector stays eager, the repairer stays timid. What changed is only that they
now look at the same rooms.

## R15 — three mutations, all proven to fire

| mutation | result |
|---|---|
| `OTHER_ROOMS = (ARCHIVE_DIRNAME,)` — the named defect, restored | **5 tests red**, including the fail-silent one |
| third-pairing scan moved to *after* the repair loop | **1 test red** |
| null control: third pairing stops requiring the root copy to be absent | **1 test red** |

Restored: 21 passed.

**One of those mutations was a real defect in my own first draft, caught by the test written
for it.** `unrepairable_pairings()` keys on the *absence* of a root copy, and a successful
repair creates exactly that absence — so scanning after the loop made every all-three-rooms
repair re-report as an unrepairable pairing: a control reding on its own success case. The scan
now reads the tree as found, before anything is deleted.

Two null controls guard the widening from the opposite side: a document parked in
`in_progress/` **only** is not a duplicate (parking is the normal disposition, and if mere
presence counted the repairer would shout about every parked finding forever), and a `done/`
document plus an `in_progress/` document under *different* names is not a pairing.

`test_the_repairers_room_set_matches_the_DETECTORS` asserts the invariant that was actually
violated, against `finding_classes`' own constants, so the two cannot drift apart again
silently.

## Still open, and deliberately not claimed

**The writer that re-creates these files is still unidentified.** The module's original author
declined to name a cause they could not show, and I am not going to either. What I can report:

- **Observed.** `run_complete_20260820T085957Z.md` was removed by `observe()`, and had
  reappeared in the staging root by the time `observe()` was called again minutes later, where
  it was removed a second time. The recurrence is real and it is live.
- **Observed.** 54 files in the staging root carried an mtime of 18:34, a mass event 19 minutes
  after the `733b4491b` commit at 18:15.
- **Observed.** `process_run_complete.py` (PID 3278516) has been running for 65 minutes against
  that exact marker path.
- **Inferred, not shown.** That process is a *lead* for the resurrection, not a demonstration
  of it. `_head_checkout()` and `_refresh_checkout_to` operate on a separate checkout
  directory, and one comment says a re-render is written "into the checkout AND the tree" —
  which is suggestive and is not the same as having traced a write to these paths.

This is the weaker fix and it is still the right one to build first, for the reason the module
already gives: it holds whichever cause is real, and it holds for the next duplicate whose
cause is a third thing. The state is repaired; the writer is a separate finding.

## Tree state, measured in the tree that matters

`_class_consolidation_check` in `tools/pre_commit_test_gate.py` is FAIL-CLOSED and runs
`check()` against the tree the commit would create, so that is the tree this was measured in —
a clean extract of HEAD plus this commit's paths, not the working tree.

> **CORRECTION — this section originally claimed HEAD was red with 5 failures. It was red with
> ONE.** The other four were an artefact of my own instrument and are retracted below, along
> with the sentence in this commit's message that repeats them. The finding above is unaffected:
> nothing in the repairer's defect, the fail-silent report, or the resurrected draw rests on it.

**HEAD as committed (`733b4491b`) was red with exactly one failure:** `TWO ROOMS
run_complete_20260820T085957Z.md`, present in `done/` AND root. This commit clears it, by the
widened repairer's staged `git rm`. Verified afterwards against HEAD `24e454c09`:
**`class consolidation holds`**.

**What I got wrong, and it is the same class as the finding.** I first measured HEAD in a
`git archive | tar -x` extract, which reported four additional `STALE SEVERITY` class documents.
That extract has no `.git`, and derived severity is not the same question there — the identical
tree reports `prints BLOCKING, instances derive LATENT` in a real repo and the reverse in a bare
extract. So I rendered four class documents against a fake reading, and the gate refused the
landing twice before I reproduced its checkout properly with
`surgical_land.materialise()`. Re-rendered in a real standalone repo, **only one class document
actually changed** — `CLASS_CONTROLS_THAT_CANNOT_FAIL`, gaining this finding's member row — and
the receipt records 5 landed paths, not the 9 in the pathspec, because the other four were
byte-identical to HEAD.

A control measured in an environment that cannot answer its question returns an answer anyway.
That is the finding's own subject, arriving in my instrument instead of the machine's, and the
cost was two refused landings whose 3-line excerpt named the verdict and none of the failing
lines.

The two live duplicates are resolved by different routes, which is the point of the split. The
`done/` one was removed automatically by the repairer. The `in_progress/` one was refused by it
— correctly, since the root text is not contained in the parked copy — and resolved by hand:
the untracked root resurrection was deleted after confirming its blob survives in history at
`5b1359b74`, so nothing was lost.

One caveat stated rather than buried: the working tree's own `--check` does **not** pass, and is
not expected to. It holds 53 further untracked findings that no class document lists, and an
uncommitted change to `finding_classes.py` from another lane that excludes
`WORKER_FINDING_REPEATING_ALARM_*` from consolidation. Those are that lane's to render when it
lands. The class documents committed here are rendered by HEAD's classifier over HEAD's
population, because that is the pair the gate will actually run.
