**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The control on the repairer's room set froze today's answer, so a third room wedged every commit in the tree and the repairer reported "0 duplicate(s)"

**Found:** 2026-09-04, autonomous worker, while draining the publish wedge that had held the site
for ~4 hours with ten `run_complete_*` markers queued. Reproduced and mutation-proven, not inferred.

---

## What happened

`background/finding_classes.py` refuses **every commit in the tree** when one staged document sits
in two rooms at once. `background/staging_two_rooms_repair.py` exists solely to clear that refusal
automatically — the director's instruction on 2026-08-19 was *"four manual clears is three too
many"*.

On 2026-09-04 eight preregistrations sat in **both** `docs/staging/` and `docs/staging/records/`:

```
check: FAIL (8 failures)
TWO ROOMS SEAT_PREREGISTRATION_WHETHER_A_CONSTANT_PHI_SURVIVES_..._2026-09-04.md:
  present in records AND root — the rooms make mutually exclusive claims
```

The repairer, run against that exact tree, said:

```
0 duplicate(s) across both staging rooms.
```

A clean bill, from the one component whose entire job is to clear that refusal.

## The cause, and it is not the room

`records/` landed in `finding_classes.ROOM_DIRNAMES` on 2026-09-03. The repairer kept its **own
copy** of the room names:

```python
#: Kept in step with `finding_classes.ARCHIVE_DIRNAME` / `PARKED_DIRNAME` -- ...
ARCHIVE_DIRNAME = "done"
PARKED_DIRNAME = "in_progress"
OTHER_ROOMS = (ARCHIVE_DIRNAME, PARKED_DIRNAME)
```

"Kept in step" by hand is the defect. `duplicates()` walked two rooms; the detector refused on
three. `unrepairable_pairings()` named `done/`-vs-`in_progress/` directly and so covered one of the
three rootless pairings.

## The part worth the finding: the control was already there, and it was pinned

`tests/background/test_staging_two_rooms_repair.py::test_the_repairers_room_set_matches_the_DETECTORS`
was written for exactly this. Its docstring states the invariant correctly:

> *"A repairer knowing fewer rooms than the detector can only ever clear part of what the detector
> refuses on — which is the whole finding, so it is asserted rather than left to the next reader."*

Its assertion did not say that:

```python
assert set(tr.OTHER_ROOMS) == {finding_classes.ARCHIVE_DIRNAME, finding_classes.PARKED_DIRNAME}
```

Both sides name the two rooms **that existed the day it was written**. The right-hand side is a
frozen literal wearing the detector's attribute names, which is what made it read as a comparison
against the detector. When the detector gained a third room the property became false and the
control stayed green — and it would have stayed green for a fourth room and a fifth.

This is `key a control to the property, not to today's answer`, and the flattering disguise is the
new part: the frozen literal was spelled with the *other module's own constant names*, so it
passed review as an independent read of the detector. **A control that imports the subject's
attribute names is not thereby reading the subject.**

`finding_classes.py` had already written the lesson down, one module over, about itself:

> *"A new room is not a new room until this tuple knows about it."*

The tuple that was fixed was the detector's. The repairer's was not, and the control that should
have caught it had been pinned since before the room existed.

## Cost

Every commit in the tree refused, the publisher's included. The publish path was down ~4 hours with
ten completed runs queued behind it, so every figure established in that stretch sat in a commit no
reader ever saw. The refusal is loud and correct; the thing that could have cleared it in one
second reported a clean tree.

## Repair (landed with this finding)

* `OTHER_ROOMS = tuple(ROOM_DIRNAMES)` — **imported** from the detector, not re-declared. The
  repairer can no longer know fewer rooms than the thing it exists to satisfy, whatever room is
  added next and by whichever hand. `ImportError` is deliberately fatal: a repairer guessing at the
  room list is this defect wearing a fallback.
* `unrepairable_pairings()` derives **every pair** of non-root rooms from that tuple.
* The control now reads `set(finding_classes.ROOM_DIRNAMES)` and fails with both room sets printed.
* Two new legs drive the instance that got through: a `records/` duplicate, and a rootless
  `records/`-vs-`done/` pairing.

**R15 both ways, on `python3 -B`:**

| state | result |
|---|---|
| repaired | 23 passed |
| `OTHER_ROOMS` pinned back to `(ARCHIVE_DIRNAME, PARKED_DIRNAME)` | 3 failed — the room-set control **and** both new legs |
| `unrepairable_pairings` alone pinned to the two rooms | 1 failed — the rootless leg only |

Each mutation fires exactly the leg its docstring names.

Run against the real tree under `tree_lock`, the repaired tool removed all 8 root copies and
`finding_classes --check` went to `PASS (0 failures)`.

## What this does NOT cover

The repairer still repairs the **state**, not whatever writes the duplicate — unchanged from its
original note, and still the right order. What changed is that it can now see every room the
detector refuses on.
