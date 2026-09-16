**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SEAT] the heartbeat is keyed per seat, and the worktree sweeper is refused because it would enumerate checkouts

Drawn as *"give `.seat_heartbeat.json` ONE RECORD PER SEAT (keyed by session_id) and a sweeper
that enumerates `git worktree list`, then re-ask whether the redirect to the shared tree becomes
correct"*. Two of those three are delivered. The third — the worktree-enumerating sweeper — is
REFUSED on measurement, and something better replaces it.

## The premise was not spent

`5f3b83b52` is an ancestor of `origin/main`, as the draw said. It is the commit that RECORDED the
refusal this item asks to revisit; it did not do the work. Neither the keyed store nor the sweeper
existed at HEAD before this turn.

## The redirect becomes correct, and the answer is yes

The 09-16 refusal was *"the record is single-valued and the population is not"*: merging two
concurrent seats' beats onto one shared record yields the SURVIVOR's answer, so a dead seat's row
is kept warm by a live one in another tree and swept by nobody — a FAIL-SILENT worse than the
staleness it fixes.

That reasoning is about a single-valued record and is simply not about a keyed one. The store now
holds one row per session id. Two live seats are two rows. One dying leaves its own row to go cold
on its own clock, and `sweep()` walks rows rather than asking for one verdict. The redirect's
premise — that a seat is a thing on this MACHINE, like `launch_liveness`'s `systemctl --user`
unit, and not a thing in a tree — was never in dispute; only the record's shape was. Both sides
are wired, guard before redirect, same doctrine as `launch_liveness.save`.

## The worktree sweeper is REFUSED, and this is the measurement

Taken 2026-09-16 across all four linked worktrees, against `git diff HEAD`:

| tree | session | pid | age | `git diff HEAD` |
|---|---|---|---|---|
| `/var/tmp/se-floorrun-20260910` | `761ae288` | 3745366 | 16 d | **SAME as HEAD** |
| `/var/tmp/se-forkmerge-20260915b` | `761ae288` | 3745366 | 16 d | **SAME as HEAD** |
| `/var/tmp/se-lane0-merge-20260915` | `761ae288` | 3745366 | 16 d | **SAME as HEAD** |
| `/var/tmp/se-seat-executor` | `f4c65996` | 3432899 | 2 h | DIFFERS — a real beat |
| `/home/rich/synthetic-enterprise` | `132f3b1e` | live | 0 s | DIFFERS — a real beat |

**`.seat_heartbeat.json` is TRACKED, so `git worktree list` does not enumerate seats — it
enumerates CHECKOUTS.** Three of the four worktrees held a byte-identical record that no seat in
any of them ever wrote; it is what git put there. A sweeper walking worktrees would have filed
three handoffs for one session that was never in those trees, and **a phantom handoff is worse
than a missed one**, because it sends the next tick to adopt work that does not exist and to
`git checkout --` paths another lane may be holding.

`git diff HEAD` does tell a checkout from a beat — but only as a one-shot over residue. Once every
seat writes the one book, no worktree copy is ever written again and there is nothing left to
enumerate. That is the register CLAUDE.md says to delete rather than write.

**What replaces it is the `tree` field on each row**, which names the tree that seat was actually
beating in — asked of the seat, not of git's checkout table. `_uncommitted_paths` and
`_last_commit` are asked of THAT tree, and the handoff tells the reader which tree to `cd` to.

## The defect the keyed store introduces, found by mutation and not by reading

One book per machine means the shared tree's 5-minute sweep files for seats that died in linked
worktrees — whose uncommitted work is in THEIR tree. A handoff built from the sweeper's own
`PROJECT_DIR` would be confidently, plausibly wrong: real files, really held by somebody, just not
by the seat the document is about.

`_uncommitted_paths(rec.get("tree"))` → `_uncommitted_paths()` **passed the entire suite**, because
every other fixture stubs that function with a lambda that ignores its argument. Answered the
unflattering way: a missing test, not an equivalence. Two controls were written and the stub in
them DISCRIMINATES ON THE TREE.

## Pre-registration, written before the battery was run

> Collapsing the key fails the per-seat legs and not the redirect ones; unwiring either side of
> the read-modify-write fails the one-book leg alone; guarding after the redirect fails only the
> ordering leg; making the handoff ask the sweeper's tree fails only the tree-routing legs.

### The result, kept beside the prediction: 6 of 6 fired, and one fired NOTHING on the first pass

| mutation | fired | predicted |
|---|---|---|
| `key` collapsed to a constant | 11 per-seat legs, no redirect leg | ✓ |
| `sweep()` asks the population verdict | the 2 survivor-masking legs only | ✓ |
| read side unresolved | the one-book leg only | ✓ |
| write side unresolved | the one-book leg only | ✓ |
| guard after redirect | the ordering leg only | ✓ |
| handoff asks the sweeper's tree | **0 — uncontrolled** → 2 after the controls were written | ✗ then ✓ |

The sixth is the finding. It is recorded here rather than quietly fixed because "the stubs ignore
the argument the defect is in" is a shape that will recur wherever a function gains a parameter.

## The residue, handled by hand rather than by a mechanism

`/var/tmp/se-seat-executor`'s 2-hour-old `f4c65996` was the one real orphan — a seat that died in
a linked worktree and would have been swept by nobody. By the time it was adopted the seat
executor had started a **new live turn** in that worktree (`c51f65da`, 0 min), so the row that got
adopted was a LIVE seat's, not a dead one's. **It was removed again**: declaring a live seat dead
is this module's expensive error, and a phantom handoff is exactly what the paragraph above
refuses. Recorded rather than tidied away — the adoption was wrong and the correction is the
evidence the check works.

What `f4c65996` held, measured before the adoption: two files, both under `docs/staging/`, which
`_uncommitted_paths` excludes because a staged document is already in the tick's draw. So it died
holding nothing and the honest outcome is that no handoff was owed.

**During the transition, a seat in a worktree running the pre-keyed copy of the module keeps its
own book.** That is self-healing (its beats join the shared book the moment that worktree runs
HEAD's copy) and it is not dangerous, because the two-signal verdict resolves an unknown to LIVE.

## What landed

- `background/seat_continuity.py` — keyed store (`{"seats": {session_id: beat}}`), legacy flat
  record adopted as a one-row store, both sides resolved to the shared tree, `state()` split into
  a per-seat verdict and an explicit population union, `sweep()` walks rows and removes the ones
  it files, `_uncommitted_paths`/`_last_commit` take the dead seat's tree. `_clear()` deleted —
  unlinking the file would have deleted every LIVE seat's row.
- `background/live_ledger_guard.py` — `shared_tree_live_record(..., for_write=True)`. "Absent means
  do not redirect" is right for a read and FAIL-OPEN for a write: it splits the book instead of
  staling the read. Reachable, not hypothetical — the old `sweep()` unlinked the shared copy.
- `tests/background/test_seat_continuity.py` — 6 new legs; the two `note_activity` handoff legs
  re-keyed to the PROPERTY (the predecessor's state survives) rather than to the mechanism that
  used to deliver it, which the repair made unnecessary.
- `tests/background/test_a_read_modify_write_live_record_reads_and_writes_one_tree.py` — the
  heartbeat leg gains the "redirect is taken" clause and a write-guard ordering leg.

## What is still owed

`launch_liveness.save()` calls `shared_tree_live_record` WITHOUT `for_write`, so it carries the
same latent split-the-book hole this turn closed for the heartbeat. Not reachable today (the file
is tracked, so a checkout always exists) and not touched here because it is a different subject.
Named so the next reader does not have to rediscover it.
