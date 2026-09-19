**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [WORKER] The 98 archive moves landed, the flow inverted exactly as predicted, and the sediment alarm had been recommending a change to the half that worked

Claim: `one-hundred-and-two-dispositioned-staging-docs-were-never-committed-out-of-the-root`.

## The count, re-measured before starting

The direction said 106 root `.md` on disk, 177 in `git ls-files`, 102 tracked root documents absent
from the working tree, re-counted at 05:30Z. At 09:12Z it was **107 on disk, 182 in `ls-files`, 98
absent**. The daemons had moved on; the class was unchanged. All **98** absent documents had a copy
in `docs/staging/done/` — none in `records/`, and none unpaired, so the whole set was a clean rename
and no part of it was a deletion wearing an archival's clothes.

The direction's own instrument reads the INDEX. That matters later.

## The prediction, written before any of it landed

Recorded in the message of `9ea5c9881`, the first batch, before the other two existed:

> `root_flow()` read filed=210, dispositioned=162, net=+48, SEDIMENT: 1 violation. All 98 root names
> are absent from the current `left` set, so once every batch lands the reading becomes filed=210,
> dispositioned=260, net=-50 and the sediment violation clears. If it does not, the sediment finding
> was never about filing volume and the remedy belongs somewhere else.

**Measured after the third batch: filed=210, dispositioned=260, net=-50, sediment 0 violations.**
Exact, on both numbers. 94 of the 98 were also *filed* inside the same 7-day window, so this was one
week's own churn and not a backlog.

## What landed

| Commit | Paths | Pairs |
|---|---|---|
| `9ea5c9881` | 20 | 10 |
| `38a8e43c1` | 88 | 44 |
| `6aa321c1b` | 88 | 44 |

Both sides of every move — the root deletion and the `done/` copy. Every stem was re-checked on disk
immediately before its landing, because the archival daemons move documents mid-turn; nothing was
skipped, so no document moved under any of the three batches. Batch 1 was deliberately small to learn
the refusals; when it gated green at rc=0 the batches went to 44, because the gate's cost is almost
all fixed rather than per-path and the only reason to split at all is to lose one cycle to a refusal
instead of the whole set.

**DONE criterion met:** `git status --porcelain docs/staging/` reports **0** uncommitted root
deletions. HEAD holds 85 root `.md`, and every one of them exists on disk.

## The refutation clause is answered NOW, structurally, and it does not need the next orientation

The direction said: *if the count is back above zero at the next orientation, the archival daemon is
committing nothing by construction and the fix belongs in the daemon.*

It will be. **Neither archiver commits, and neither ever could without being given the power to
land:** `background/staging_watcher.py` (`path.rename(dest)` at two sites) and
`background/staging_archive_policy.py` (`os.replace(src, dst)` in `_execute_move`) both move the file
and stop. Grepping either for `surgical_land`, `commit`, `tree_lock` or `subprocess` returns nothing.
So the stranding recurs by construction and waiting three hours to observe it would only have bought
the same answer later.

**But the fix does NOT belong in the daemon.** A tick that lands commits needs ten minutes and nine
gates it does not have, and giving two daemons the power to write the record autonomously is a much
larger change than the defect justifies. What was actually missing is smaller: *nothing in the tree
could tell the two causes apart*, so the alarm that did fire named the wrong one.

## The real defect: an alarm reading from git on purpose, and therefore blind on purpose

`root_flow()` reads from git rather than disk, and its docstring is explicit about why — the 89
stranded moves of 2026-09-03 would have scored as drained from a disk reading. That choice is right.
Its consequence is that a disposition which *happened* and was never committed is counted as one that
did not happen, and the net is overstated by exactly that much.

Then `sediment_violations()` took that overstated net and said:

> The remedy is not a bigger folder: it is fewer channels that file, or a disposition route for the
> ones that do.

Advice about **filing**. It was firing at +48 while 98 dispositions sat uncommitted on disk — i.e.
the queue was draining half again faster than it filled, and the alarm was recommending a change to
the half that was not broken. This is the class CLAUDE.md already names: a reconciliation's printed
cause is not evidence of the cause.

## What was built

`background/staging_rooms.py`:

* `head_root_documents()` — the root names the **committed record** holds. HEAD via `ls-tree`, never
  `ls-files`: this repository lands by plumbing, so `surgical_land` never opens the shared index, and
  after these three commits the index still listed all 98 in the root while no commit did. A reading
  taken from `ls-files` would have called the queue unchanged by the landing that had just emptied
  two thirds of it. That is the same instrument the direction used to count 182.
* `stranded_dispositions()` — two buckets, because they have opposite remedies. `archived`: absent
  from the root, copy in a sub-room → the disposition happened, the remedy is a landing. `vanished`:
  absent with no copy anywhere → not an archival at all, possible loss, and calling it progress would
  file a lost document as a discharge.
* `stranded_disposition_violations()` — fires on the **property** (does every root document the record
  holds still exist on disk), not on today's 98, so it stays green when the tree becomes more honest.
  Unreadable is its own violation and never a pass.
* `sediment_violations()` now names the held-back count in the same breath as the net, instead of
  leaving the reader to reconcile two separate violations.

Wired into `render()` and into `--check`'s exit code, so it can refuse rather than merely print.

## That it can fail

Green now, and green for the right reason. Three mutations, each run against an out-of-repo copy of
the module so no mutation was ever a shared-tree write:

| Mutation | Result |
|---|---|
| drop the `elsewhere` lookup (one bucket only) | CAUGHT — `archived` goes to `[]`, `vanished` to both, so the remedy named becomes loss instead of a landing |
| flip the absence test, so the control sees nothing | CAUGHT — reports the one document that is *fine* and misses both that are not |
| return `[]` when the record cannot be read | CAUGHT — the fail-open this repository has shipped before |

And the strongest leg, which no mutation gives: run the new control against the **pre-landing** HEAD
`11427723c` and it reports **`STRANDED ARCHIVAL: 98 document(s)`**. It fires at exactly the number,
on the exact tree, and is silent on the tree that replaced it.

The partition is controlled in one assertion — `assert got["archived"] and got["vanished"]` over a
single root holding all three states — because a guard that reports nothing passes every test written
one branch at a time. HEAD is injected rather than committed in the tests, since the branch where a
document is absent from disk is the rare one and a test that had to build a git repository to reach it
would reach it once.

## Two reds in the tree that are not mine, attributed rather than inherited

* `tests/architecture/test_static_quality_ratchet.py` — I001 census 1308 → 1307. The file that lost
  its violation is `tests/tools/test_generate_maturity_map_data.py`, which another lane has dirty in
  the working tree with its imports fixed. Outside my commit's tree; `surgical_land` gates
  HEAD-plus-my-paths, which is why all three batches gated green at rc=0.
* `tests/background/test_finding_classes.py` — 2 reds. That test file is modified in the working tree
  and `background/finding_classes.py` is clean, so it is another lane's in-flight test edit against an
  unmodified module. The same file shows 11 reds in a clean HEAD extract, which is extract locality
  (no `.git`) and not a third reading.

## What would refute this

The stranding recurring **with the new control silent**. That would mean an archiver has found a
route out of the root that leaves neither a sub-room copy nor a gap at HEAD, and the property this is
keyed to is the wrong property. The count going back above zero with the control **loud** is not a
refutation — it is the control working, and at that point the choice between teaching a daemon to
land and accepting a periodic batch is a real decision with evidence under it, which it did not have
today.
