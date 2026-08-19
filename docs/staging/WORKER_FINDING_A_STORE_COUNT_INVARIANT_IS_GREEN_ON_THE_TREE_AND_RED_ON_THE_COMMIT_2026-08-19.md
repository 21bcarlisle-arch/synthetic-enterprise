# WORKER FINDING — the store/map note-count invariant is green on the working tree and red on the commit

**Severity:** LATENT · **Lane:** H_harness
**Date:** 2026-08-19
**Raised by:** the worker tick that landed `EP1_clv_three_horizon` pass 9. Found while checking
that the pass-9 store roll was complete before committing it — not drawn, not searched for.
**Class:** MEMBER of the existing tree-vs-commit class, not a new one. Its siblings are
`WORKER_FINDING_A_LANDING_STEP_CAN_ONLY_BE_CAUGHT_BY_A_TREE_IT_DOES_NOT_CONTROL_2026-08-18.md`
and `WORKER_FINDING_A_PATHSPEC_PROTECTS_OTHER_LANES_FROM_MY_INDEX_BUT_NOT_FROM_MY_STALE_COPY_2026-08-18.md`.
Filed so the instance is on the record and the class fix has one more measured member — not so a
ninth class doc is minted.
**Status:** instance REPAIRED in the commit that carries this document. Class fix named, not taken.

Every claim below is `observed-with-evidence` unless labelled `inferred` (R9).

---

## What was measured

At HEAD `b98722cb2`, extracted to a throwaway tree with `git archive HEAD docs/design/simplifications`:

```
EP1_clv_three_horizon.yaml           7 notes
EP1_clv_three_horizon.001.yaml       1 note
                                     -------
HEAD total                           8
docs/design/maturity_map.yaml:4091   simplifications_count: 9
```

The invariant is one-line explicit: `tests/design/test_simplifications_store.py:114` — *"Each
atom's `simplifications_count` must equal its store file's note count"*. On the committed tree
that equality is **8 == 9**, which is false.

That control is GREEN, and was green this tick: `41 passed in 34.11s`, and
`python3 tools/migrate_simplifications.py --check` reports `"count_mismatches": []`.

It is green because its subject is the **working tree**, and on disk there is a third chunk,
`docs/design/simplifications/archive/EP1_clv_three_horizon.002.yaml`, which `git status` reports
as `??` — untracked. It holds exactly one note (the 2026-08-15 DISCOVER/FRAME pass, 6,337 chars,
byte-identical to entry 0 of the store file at HEAD). It is the ninth note. Nothing that is
committed contains it.

So the count the map declares is true of the disk and false of the repository.

## Why this is not a defect in the control

Stated plainly because the temptation is to file it as one. `test_the_map_count_matches_the_store`
does what it says: it reads the store and the map and compares. Both readings are correct. What it
was never asked is *which tree* — and a plain `git commit -- <pathspec>` runs the pre-commit gate
against the working tree, so a file that is not in the pathspec, and not even in the index, can
supply the value that makes the gate agree.

This is the same shape as the two sibling findings, arriving on the store surface: the guard and
the artefact it guards are read from a tree that the commit does not describe.

## Why LATENT and not BLOCKING

Not silently defaulted — the reasons, and this is the part to argue with:

* No published figure moves. `simplifications_count` is a bookkeeping scalar the store/map
  invariant reads; no board number, dashboard value or gap reading is derived from it.
* No control's verdict about *its own subject* is invalidated. The count control reports on the
  working tree accurately, and it is the only tree it was ever pointed at.
* The failure mode is a lost record, not a false one: an unlanded note is invisible, and the next
  roll would have overwritten `.002.yaml` and destroyed the 2026-08-15 pass permanently.

The last bullet is why it is filed at all rather than fixed and forgotten.

## What is NOT claimed

**INFERRED, and deliberately not asserted:** which pass left the map at 9 with only 8 landed notes.
The arithmetic is consistent with pass 8 (`b6148d907`, 2026-08-19 00:59) bumping the scalar for a
note whose chunk it never wrote, and equally consistent with a chunk written and then rewritten —
`.002.yaml`'s mtime is 2026-08-19 09:51:17, the same second as the store file's, which is pass 9's
two-file atomic write and says nothing about 00:59. Reconstructing it would need the reflog and
would change no repair. **Nobody is accused of anything and no gate is asserted to have been
bypassed:** whether the gate ran on that commit was not measured, and an unmeasured claim of a
bypassed wall is exactly the shape R9 exists to stop.

## The instance repair, in this commit

`archive/EP1_clv_three_horizon.002.yaml` is committed alongside the rolled store file, so the
would-be tree carries 7 + 1 + 1 = 9 notes against a declared 9. The 2026-08-15 record survives in
a tracked file for the first time.

## The class repair, named for when it is drawn

The population is **every control the pre-commit gate selects from a store-surface edit**, not this
one cell, and the repair is not to teach `test_the_map_count_matches_the_store` about git — that
would leave its neighbours reading the wrong tree and would be one more instance fix on a class
(R10). Two candidates, and the second is the recommendation:

1. Have the store-surface controls read `git show :<path>` (the index) rather than the working
   tree. Rejected: it only moves the subject from the working tree to the index, and a pathspec
   commit's index is not its tree either.
2. **Route store-surface commits through `python3 -m tools.surgical_land`**, which gates the tree
   the commit WOULD create. The instrument already exists and is already the standing answer to a
   dirty shared index; what is missing is that nothing makes it the only door. A control that
   refuses a store-surface change committed any other way is the mechanism, and it belongs with
   the sibling findings' repair rather than in front of it.

Sequenced AFTER the sibling class fix, deliberately: three members of one class want one door, and
building a third separate guard is how the class stops being visible as a class.
