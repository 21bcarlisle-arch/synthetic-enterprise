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

---

## SECOND MEASURED INSTANCE, 2026-08-22 — and this one reached `main`

Found by the worker tick that landed `EP6_wall_protocol_typing` pass 62, while checking the
count invariant at the commit rather than on the tree. Not drawn, not searched for. Every claim
here is `observed-with-evidence` unless labelled `inferred` (R9). The `Severity:` field above is
deliberately left as filed; what follows changes what is known about the class, not its grading.

| commit | store (archived + live) | map declares | verdict |
|---|---|---|---|
| `973aa9ac6` | 56 (51 + 5) | 56 | green |
| `87eed63cc` | 56 (51 + 5) | **57** | **red** |
| `4175424cc` | 57 (53 + 4) | 57 | green |

`87eed63cc` is `Auto-process run complete: report + LATEST.md + site/` — a routine publish commit
from `background/process_run_complete.py`. It carries a four-line `docs/design/maturity_map.yaml`
hunk (`simplifications_count: 56 -> 57`, `file_scope` 37 -> 38 entries) that **is not the
publisher's change**. It was `EP6` pass 62's.

The publisher does not sweep the map by accident. It stages it **deliberately and by name**
(`process_run_complete.py:3970`, `git add -A docs/design/maturity_map.yaml docs/design/atom_status`)
and names it again in the commit pathspec, for a stated and legitimate reason: *"Publish the
pre-gate inbox fold too ... so a reconciled map lands WITH the run it belongs to, never dangling
uncommitted."* The map reconciler folds atom_status inboxes into the map and leaves the result
uncommitted; the publisher adopts it so it does not dangle.

That is the whole defect, and it is a design consequence rather than a slip: **the publisher has
no way to tell the reconciler's fold from any other lane's uncommitted map edit.** Both are "a
modified `maturity_map.yaml` in the working tree". It adopts whatever it finds. Note the
adjacent irony — the `git add` sits inside `tree_lock()` taken *specifically* to stop another
writer's staged change being swept (the comment cites a real prior incident) — and then the
`-A` on a named path re-opens that hole for the one file this class runs through. The lock
serialises the index; it cannot make a worktree edit say who authored it.

The mechanism is the one already documented above, reproduced exactly: on disk the roll was
complete (live store trimmed to 4 rows, `archive/EP6_wall_protocol_typing.045.yaml` holding the
2 rolled rows as `??` untracked), so the gate's store-contract tests ran in the working tree and
were correctly green. The commit took the map and not the store, so the committed tree declared
57 against 56 present. Healed one commit later by `4175424cc`, which landed the store file, the
untracked chunk and the map's already-committed value together.

### What this instance adds that the first one did not

1. **The red reached `main` and was pushed.** The 2026-08-19 instance was caught before its
   commit existed. This one was not caught by anything: it was gated, committed, and pushed, and
   is still in the history.
2. **The committing lane had no store-surface intent whatsoever.** The publisher does not know
   what an atom store is, and never reads one. It claims the map for the reconciler's fold and
   adopts a half-done roll it has no way to distinguish from that fold. So the class does not
   require a seat that is reasoning about stores to get it wrong — which is what makes a
   discipline-shaped fix useless here. It also means the guard cannot live in the seat that
   edits the store: by the time the red is committed, the lane that wrote the map has moved on.
3. **It therefore measures recommendation 2 above rather than merely restating it.** That repair
   says *"the instrument already exists and is already the standing answer to a dirty shared
   index; what is missing is that nothing makes it the only door."* `process_run_complete.py`
   already knows this — its own comment at line 1349 (`WHY surgical_land AND NOT git commit`)
   names hook-bypass and the shared-tree sweep as the two reasons it uses `surgical_land`
   elsewhere — and it still reaches a store-surface file through the other door. A lane that has
   already internalised the rule, written it down, and routes around it for one path is the
   strongest available evidence that the door has to be closed by mechanism and not by knowing.

`inferred`: nothing here establishes how long the class has been firing. Two instances three days
apart, both found incidentally by a seat checking something else, is consistent with a rate well
above two — but that is not measured, and a census of `simplifications_count` against store
contents at every commit touching the map is what would measure it.
