**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the publisher has published nothing in 140 hours)

# The fork was the whole wedge, the orphan floor had already been discharged, and the third cause reproduces nowhere

**2026-09-16, scheduled tick, worker seat.** The Lane 0 direction named two causes for a publisher
that had failed 30 consecutive times across six days and asked that the wedge be cleared at the
consumer, in those two causes and no further. Both premises had moved by the time they were read.
One cause was real and was the whole wedge; the other was already discharged by another lane before
this turn began.

## What each named cause turned out to be

**(2) The orphan ratchet was NOT live.** The item said the floor was frozen in a tree of 1,128
modules against this tree's 1,153, and that the baseline path was dirty in the working tree. Neither
holds. The committed floor records 1,146, the path is clean, and the measurement that decides the
gate agrees exactly:

    orphans now: 537 | baseline: 537        rc=0

The ratchet refuses on the ORPHAN SET, not on the module count, so the 1,146-vs-1,153 gap is
provenance prose and not a refusal. Nothing was owed here and nothing was done. **A re-freeze would
have been a no-op dressed as a repair** — and, taken from the shared tree as the item's own remedy
described, would have written another lane's reachability into the floor.

The 7-module gap is the difference between modules indexed (1,153) and git-tracked `.py` files
(1,146) — untracked modules in the shared tree, which is ordinary mid-turn state, not drift.

**(1) The fork was real, and it was the entire wedge.** The publisher's own scoped suite was GREEN
on every recent attempt. The refusal was never about tests:

| attempt | cause recorded | total_red | blocking_tests |
|---|---|---|---|
| 03:35 UTC | `gate_refusal` | 1 | one site/knowledge test |
| 04:31 UTC | `behind_origin` | **0** | **[]** |

By the 04:31 attempt the accusation had emptied out entirely and the cause was named plainly:
origin was 4 commits ahead, so any commit made here could only be rejected non-fast-forward.

## The two accusations that pointed at nothing

Both test-shaped causes the state file carried were false by the time they were read, and each was
false in its own way. This matters because they are what a reader starts from.

- `blocking_tests` named a site/knowledge card-copy test. It passes — standalone, at HEAD, and in
  a clean HEAD extract.
- `.last_gate_blocking_tests.json` named 35 reds in the site baseline-comparison suite, **keyed to a
  different commit than the one it was cited against**. That suite is green: 154 passed, 2 skipped.

A blocking-test record that is never rewritten when the refusing commit changes is an accusation
with no accused — the exact shape the publisher's own comments say was closed on 2026-07-29 for the
lock-skip door. It is still open on this one.

## Closing the fork, and the one judgement inside it

`origin_reconcile` refused with one conflicted path: the generated feed behind the value arms. Both
sides had moved it from the merge base, and **a side-pick would have deleted real work either way**:

| field | changed on ours | changed on theirs |
|---|---|---|
| method_skill | yes | no |
| realised | no | yes |
| book, decisions | yes | yes |

`method_skill` is the Lane 0 result filed this morning — the method verdict not being reachable on
this book. Taking origin's copy would have dropped it; taking ours would have dropped their
departure work. So the feed was not resolved by choosing: the merge was built in an isolated
worktree, the producer re-run there against the MERGED inputs, and those bytes passed back as the
resolution. The result keeps `method_skill` from our side, `realised` from theirs, and regenerates
the fields that are genuinely downstream of both.

The producer resolves its output path from its own file location, which is what made this safe: it
wrote inside the worktree and the shared tree's copy was never touched (verified by mtime).

Landed as merge `8643dda9c`, gated clean, promoted to origin, 8 paths bound to the claim. The shared
tree then fast-forwarded 5 commits after clearing the two paths the refusal named — a generated
feed reverted to its committed bytes, and a staging document that was byte-identical to the copy
origin was bringing (checked before removal; removal was lossless).

**Position now: behind=0, ahead=0**, and the publisher's own divergence refusal returns `None`.

## What actually released, and what did not

The wedge is released at the consumer: the publisher's commits reach origin again — a heartbeat
commit landed and pushed during this turn, the first to do so in days — and the failure counter
stopped advancing.

**The done-condition is NOT met and this claim is not released.** `last_clean_publish` is still
null and `episode_failures` still reads 33. Those need a run whose sim output actually CHANGES; the
runs available to this turn were byte-identical, which takes the heartbeat path by design and never
records a clean publish. That is a different condition from the wedge and it is not a defect.

One publish attempt driven by hand after the fork closed was refused by a red site card-copy test —
the same test named above. **It reproduces nowhere**: green standalone, green at HEAD, green in a
clean HEAD extract, green in the working tree. The repair for that pair has been sitting uncommitted
in the shared tree since 2026-09-10. The site lane's hook runs in the SHARED WORKING TREE, so what
it caught was another lane's mid-write state, not a property of any tree that exists. It is recorded
here rather than chased, because a cause that cannot be reproduced cannot be fixed and the honest
next step is to watch whether it recurs.

No watchdog was built over the watchdog.
