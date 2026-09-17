**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# The fabricated row was already gone, and the isolation the item asked for would have been inert in the tree it came from

**Filed** 2026-09-17 · worker · lane 0 delivery
**Item** `the-lane-claim-and-draw-stores-are-writable-by-any-test-process`

**Lane 0 delivery**, claim `the-lane-claim-and-draw-stores-are-writable-by-any-test-process`, drawn
2026-09-17 11:32 UTC. Direction, not an atom: no exit test was written for it, so what follows
includes the judgement of what done means.

---

## What the item asserted, and what the disk said

The item carried one factual claim about the tree and one directed remedy. They were re-measured
before anything was written, because a drawn item's every factual claim is an un-re-asked
prediction.

**Claim: "`some-id` … has `last_drawn_at` 1789628340, which is 05:39 UTC today, nineteen minutes
after I wrote the item asking for it to be removed. A test process is still writing the live draw
ledger."**

REFUTED on disk at 11:33 UTC. `docs/observability/.delivery_lane_claims.draws.json` holds 364 rows
and `some-id` is not one of them. The only other short keys in it are `A46_the_priced_menu` and
`settlement-ceiling`, both real.

Nothing in git could have told me that, and this is the part worth carrying forward: **both stores
are in `.gitignore`** (`.gitignore:34` and `:35`). `git show HEAD:…` on the draw ledger answers
*"exists on disk, but not in HEAD"*. So no commit ever carried the fabricated row, no commit removed
it, and `git log -S` over it returns nothing. A premise about these two files can only ever be
re-measured on disk — and the item's own instruction to bind the removal with `--landed` could never
have worked, because there is no path in it for a commit to touch.

**The write itself is already refused, and two repairs that landed before this turn are why.**
Measured, not inferred — `guard_live_ledger_write` called under a test process against both live
paths:

| measured from | `.delivery_lane_claims.json` | `.delivery_lane_claims.draws.json` |
|---|---|---|
| `/home/rich/synthetic-enterprise` (main) | REFUSED | REFUSED |
| `/var/tmp/se-seat-executor` (linked worktree) | REFUSED | REFUSED |

The first repair was the `_boom` fromlist fix in `test_dispatch_is_the_claim.py` — the simulated
`ImportError` matched on `name` alone, never fired, and the real `claim_dispatched` wrote `some-id`
into the live ledger on every run. The second was the shared-room widening of
`live_ledger_guard.is_live_record_path`: `PROJECT_DIR` is derived from `__file__`, so a module
imported out of a linked worktree bound `LIVE_RECORD_DIR` to *that* worktree, while
`delivery_lane.CLAIMS_FILE` resolves through `seat_continuation.shared_tree_dir()` to the shared
one — the guard was handed a shared-tree live path, found it outside its own room, and permitted it.

So the write hole the item was about is closed, and the row it names is gone. What the item asked
for is not what closed it.

## What the two tuple rows are actually for, and the membership check the item demanded

The guard REFUSES; it does not redirect. With it refusing from every tree, a test in
`tests/background/` that touches these stores incidentally now fails **on the guard** rather than on
its own subject — which is the exact class `_no_daemon_state_reaches_the_live_record` exists for and
the reason 35 daemon tests were repaired on 2026-08-31. That is what the two rows buy, and it is
worth saying plainly rather than letting the commit imply they closed the leak.

The item said to CHECK the membership test that tuple's comment names — *the live file is nobody's
subject* — "rather than assuming it, the way the `LANDING_IN_FLIGHT_FILE` comment did". Done by AST
over every `Load` of the two names in `tests/background/`, not by grep, which gives two controls
that read the constants without setting them first:

* **`test_delivery_lane::test_the_ledger_is_DERIVED_from_the_claims_store_so_a_test_never_writes_the_live_one`.**
  Its named mutation — `_ledger_path` returns `DRAW_LEDGER_FILE` directly — was APPLIED, in a clean
  HEAD extract with the two rows in force. It RED on `_ledger_path(store).parent`. The control keeps
  its grading power: both sides of its equality move together under a re-root that preserves the
  repo-relative path.
* **`test_a_claim_is_visible_from_every_worktree::test_the_resolution_is_wired_into_both_module_constants`.**
  `claims_file()` returns the module global, so the constant and the resolver's answer re-root
  together. Its own mutation — bind `CLAIMS_FILE` to `PROJECT_DIR` instead of `shared_tree_dir()` —
  was run WITH and WITHOUT the rows: **11 passed each time, identical**. The rows cost it nothing,
  because it is already the equivalence its own docstring declares it to be in a main checkout, and
  the crossing tests that do carry the property pass an explicit `project_dir` no re-root can reach.

Both measurements were made in an isolated HEAD extract. One earlier attempt at the first was made
in the shared tree and is not evidence: another lane's pre-commit gate selection was running against
the same working copy, so the mutation was reverted within ~30 seconds and the run it poisoned was
killed rather than read. **A mutation is a shared-tree write, and this tree has other lanes in it.**

## The third defect, which the item did not name

`_reroot` is ONE ROOM wide. It takes `current.resolve().relative_to(REPO_ROOT)`, and `REPO_ROOT` is
`Path(__file__).resolve().parents[2]` — the tree the conftest lives in. In a linked worktree that is
the worktree, while `CLAIMS_FILE` points at the shared tree by design. `relative_to` raises,
`_reroot` returns *"already pointed somewhere harmless"*, and the constant is left aimed at the live
record.

Measured, against the real paths:

```
MAIN   /home/rich/synthetic-enterprise   ONE ROOM -> docs/observability/.delivery_lane_claims.json
LINKED /var/tmp/se-seat-executor          ONE ROOM -> NOT REROOTED   <-- the two new rows are INERT here
                                          TWO ROOMS-> docs/observability/.delivery_lane_claims.json
```

So the isolation the item directed would have been inert in precisely the tree the `some-id` row was
written from. Five linked worktrees exist on this machine. `_reroot` now tries the shared tree as a
second room — the same question `live_ledger_guard._shared_record_dir` already had to answer for the
WRITE guard's subject, which is the tell that one room was never the right shape.

**A main-checkout run cannot tell the two versions apart**, because there `shared_tree_dir()` returns
`PROJECT_DIR` and the second room IS the first. That is stated in the code comment rather than left
for a reader to discover, and it is why the table above is the evidence and the suite is not.

## What is established and what is not

ESTABLISHED: the row is gone; the write is refused from both trees; the two rows cost neither
control its grading power, by mutation; the one-room re-root was a real hole and is closed.

NOT ESTABLISHED IN THIS TURN: a full `tests/background/` run. It was launched and is ~2 hours in this
tree; the landing did not wait for it, and the cheap gates plus the three directly-implicated suites
(59 passed) are what the commit stands on. Both live stores were byte-identical (`md5sum -c`) across
every run made during this turn, which is the property the item asked to see and is weaker than a
full pass.

## Direction this leaves

The item's instruction to bind the removal with `--landed` cannot be followed for the ledger row,
and the general shape is worth naming: **a Lane 0 item whose subject is an untracked file has no
landing to bind.** The claim mechanism grades progress by which paths a commit touched, so an item
of this class reads as unmoved however much of it is done. The commit here carries the conftest
change, which is bindable; the row removal is not, and was not this turn's work anyway.
