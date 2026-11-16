**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# An archived alarm document wedged the shared tree's fast-forward, and the reconciler could not even name it (2026-11-16)

*Delivery seat executor, drawn on `alarm-annotations-wedge-the-shared-fast-forward`, 16 Nov.*

## Premise, re-measured

The draw said its three cited commits (759fac9831, 06235c81f, 2f23ad063) were already on origin.
Those commits are the hand-cleared INSTANCES. The class was still live at origin `0857edc7c`:
`_carry_plan` refused any edit at a path origin no longer holds ("HEAD and origin must both hold
the path"). So an archiver moving ANY repeating-alarm document to `done/` while `alarm_repetition`
had uncommitted lines in it held `--ff-only` until a lane landed the shared tree's bytes by hand.

## Two defects, not one

1. **The reconciler could not name the blocker.** `_arriving_paths` used `git diff --name-only`,
   and git's default rename detection reports a move by its NEW name only. The moved document's
   old path never reached `paths_blocking_fast_forward`, so the verdict was "NOTHING local collides"
   while git's own message named the file. No class could have been asked about it.
2. **No class could carry it.** Even when named, the carried class required origin to hold the
   path.

## What changed (`background/origin_reconcile.py`)

* `_arriving_paths` diffs with `--no-renames`, so a move reports both of its paths.
* `_carry_plan` gets a MOVE leg: when HEAD holds the path, origin does not, and git's rename
  detection says origin moved it, the lane's HEAD->disk change is three-way merged onto origin's
  copy at the new path and written THERE after the fast-forward (preserved on the carried ref
  first, as before). A conflict still holds. A plain deletion still holds: there is nowhere to
  carry the lines.

Test: `tests/background/test_an_alarm_document_origin_archived_carries_its_annotations_to_done.py`.
Three mutations measured, each reds the done criterion: no move leg, no `--no-renames`, writing
back at the old path.

## What is NOT fixed, and why

The root cause is that `alarm_repetition` writes tracked files and never commits them. Making
it commit, or write to an untracked sidecar instead, changes how every alarm document reads, and
that is a bigger design question than the wedge. After this change the residue is a dirty `done/`
copy in the shared tree. That copy blocks nothing unless origin edits the same `done/` path
again, and if it does, the ordinary carried class handles it, because both trees then hold the path.

A deleted (not moved) alarm document with live annotations still holds the advance, by name.
Whoever deletes one should archive it instead.
