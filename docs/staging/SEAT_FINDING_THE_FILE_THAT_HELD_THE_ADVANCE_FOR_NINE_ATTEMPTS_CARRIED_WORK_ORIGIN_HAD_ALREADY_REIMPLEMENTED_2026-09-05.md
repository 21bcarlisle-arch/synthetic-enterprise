**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** uncommitted_and_orphaned_work

# FINDING: the file that held the advance for nine attempts carried work origin had already reimplemented, and hash-inequality is what kept saying otherwise

**Measured 2026-09-05, delivery seat, from the isolated worktree `/var/tmp/se-seat-executor`,
starting at `4988ef943`. The shared tree `/home/rich/synthetic-enterprise` was on `main` at
`78a36a2b5`. Ends with the wedge closed and my own merge discarded as redundant — see
"What actually landed", which is not what this turn set out to do.**

---

## The direction's premise had expired twice over, not once

I was drawn against: *"the third lane's 58 uncommitted lines in `background/process_run_complete.py`
(worktree blob `d618e5969` …) need to land. It is the single `FF_MODIFIED` path refusing the shared
tree's fast-forward."*

Neither half was still true.

**They were not uncommitted.** `d618e5969` is `78a36a2b5:background/process_run_complete.py`
exactly — the third lane committed them at `7b3134f86`, and the shared tree's working copy was
*clean* for that path.

**The fast-forward was not held by any path.** `main` held 8 commits `origin/main` did not, and
`origin/main` held 34 `main` did not. That is divergence, which no working-tree path expresses — as
the shared tree's own `b5d596316` records discovering. A twin sweep on a diverged tree deletes files
and still does not advance.

So the work at risk was never 58 lines. It was eight commits, 25 files, +3462/−166, stranded off
origin.

---

## The load-bearing finding: hash-inequality is not evidence of unlanded work

`identical_tracked_twins` (landed on the shared tree at `aab6fb990`) asks, of each `FF_MODIFIED`
blocker, *"do these bytes equal origin's blob at this path?"* — and for `process_run_complete.py` it
answered **no** and refused. Its docstring names that file as the fifth path, which *"carried 58
lines origin has never seen, and is exactly the judgement this must not automate."*

**Origin had seen them.** origin/main's own lane had independently implemented the same repair — the
post-advance re-read of both verdicts, at *both* commit sites — and gone further:

| | shared tree (`78a36a2b5`) | origin/main (`4988ef943`) |
|---|---|---|
| advance + re-read at `git_commit_push` | yes | yes |
| advance + re-read at `_commit_and_push_paths` | yes | yes |
| `_record_liveness_surface_refusal` on the post-advance refusal | **no** | yes |
| FF_MODIFIED-vs-hot-origin cause split on the refusal | **no** | yes |

Resolving that file's one conflict hunk to origin's side reproduces origin's copy **byte for byte**:
the shared tree's side contributed nothing.

**Why the guard could not see it.** Byte-equality is the right question for a file that is
*identical* and the wrong question for a file that has been *superseded*. Both answer "not a twin",
and only one of them means a lane's real work is at stake. Nine advance attempts, zero fires, and
~6h of the publish daemon emitting HEAD's superseded refusal wording all rest on that conflation.
**A hash comparison can license the cheap half of the decision; it cannot refute the expensive half,
and this guard's docstring reads as though it had.**

The cheap repair, if anyone wants it: before reporting a non-twin `FF_MODIFIED` path as a lane's
live work, ask whether its *diff against the merge base* is already contained in origin's copy. That
is a `git merge-file` away and it is the question the guard is actually being read as answering.

---

## What actually landed, and it is not what I built

**Another lane merged the same eight commits while I was working.** `f81333756` ("merge origin/main:
thirty-five commits, nine conflicts, each side chosen by running it") put all eight on `origin/main`
mid-turn. `promote_worktree_landing` correctly refused my merge as a non-fast-forward, which is how
I found out.

I had already resolved all seven conflicted paths independently, from the same two sides, choosing
each by reading and running rather than by preferring a side — two files go one way and five the
other. **All seven of my resolutions match `origin/main` byte for byte.** That is corroboration of
the *judgement* and not of the underlying code: we worked from identical inputs, so it is two
readings agreeing, not two routes agreeing. It does mean nothing is owed on those seven paths, and
my merge commit `56c6d030b` was discarded rather than promoted, because every line of it was
already on origin.

**The wedge is closed.** The shared tree is now at `2345bb0e1`, level with `origin/main`, behind by
0, and `main` is an ancestor of `origin/main` — so a fast-forward is a fast-forward again. The
direction's stated goal was reached; it was not reached by me.

**The cost worth recording is the duplication itself.** Two lanes each spent a turn on the same
seven-conflict merge, and neither could see the other until a push refused. Nothing in the draw
looks at what another lane is *mid-merge* on, only at what is claimed and what is landed.

---

## Second defect, found by the same merge, and the one thing this turn actually ships

`78a36a2b5:background/sanity_daemon.py:364`:

```python
    except OSError as e:
        last_sent = None  # MUTANT
```

That branch is the once-per-day digest stamp's unreadable case. `last_sent = None` is precisely the
fail-open the surrounding docstring argues against at length — an unreadable stamp is *unwritable*
too, so it never advances and the director gets a repeated digest every 30-minute cycle: the
alarm-that-repeats-unactionably the function exists to prevent.

A mutation-harness edit was committed and survived every gate. It is gone from `origin/main` now,
but only *incidentally* — the merge preferred origin's copy of that file for an unrelated reason
(origin had refactored the read into `_last_digest_date()`/`_StampUnreadable`). Nothing detected it,
and the harness that writes these markers runs routinely, so the next one is a matter of when.

**Shipped:** `tests/architecture/test_a_mutation_marker_never_reaches_production_source.py`. One
scan, one shape, no register and no allowlist. The discriminator is position, not vocabulary: a
*trailing* comment on a line of code whose body opens with `MUTANT`, tokenised so a marker inside a
string literal is not a hit. `background/gap_metric.py`'s standalone prose about a named
`_MUTANT_*` fixture stays green, which is why a grep would not do.

### The control was a tautology on its first draft and the harness said so

Worth recording because it is this project's most-repeated control failure and it very nearly
shipped again. The first draft passed 5/5 and its docstring called position *"the whole
discriminator"* — but deleting the position check from `residue_markers` left **all five tests
green**. None of the honest-prose comments in the negative sample *began* with `MUTANT`, so the
body-prefix test alone excluded them and the discriminator carried no load and could not be proven
to. Fixed by adding a standalone `# MUTANT markers are written by the harness…` line — a comment
that a prefix-only reading would flag and must not. Three mutations now fire: drop the position
check (2 red), make the detector return nothing (2 red), and inject a real marker into a production
root (tree scan red, green again on removal).

---

## Correction, filed beside the claim it corrects

An earlier draft of this finding recorded a third defect: that three rows of the shared tree's
`self_clearing_alarm_dispositions.json` cite
`tests/background/test_the_jsonl_carriers_claim_was_reasoned_from_a_sibling_and_one_of_five_was_wrong.py`
as their backing control, and that no such file existed. **That was true at `78a36a2b5` and is now
false.** The test arrived on `origin/main` in the same window (`git cat-file -e` confirms it), so
the citation resolves and there is nothing to fix. The claim is struck rather than deleted: it was
measured correctly against a tree that then moved, which is the ordinary hazard of grading a
citation against one snapshot, and the next reader should know the row is sound.

---

## Pre-registration: what the advance's first real trial will show

The advance has had nine attempts and zero fires, and every refusal so far was blind to its own
cause. The tree is level right now, so there is nothing to advance and no trial to be had yet.
Registered before the next time the shared tree falls behind:

*If it is behind-and-not-ahead, the advance fires and `cleared` is non-empty. If it is behind AND
ahead, theirs' divergence guard (`b5d596316`, now on origin) refuses and NAMES divergence — which
would be the first refusal in this file's life that is correct rather than blind.* Both are readable
in the deadman log. **The second outcome is not a failure of the advance**, and recording that here,
before the fact, is the point: a refusal-that-names-divergence will otherwise be counted as a tenth
non-fire by anyone tallying the same way the first nine were tallied.
