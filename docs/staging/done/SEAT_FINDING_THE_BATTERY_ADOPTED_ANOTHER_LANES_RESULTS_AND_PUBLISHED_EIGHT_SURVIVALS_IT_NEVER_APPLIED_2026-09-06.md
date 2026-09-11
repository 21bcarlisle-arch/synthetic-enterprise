**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: the battery adopted another lane's results and published eight survivals it never applied

**Measured 2026-09-06 00:47 BST, delivery seat, isolated worktree at `af958429e`, claim id
`converged-battery-next-subject`. Caught by reading the run's own output rather than its summary
line. Repaired in the same commit as the finding.**

---

## What happened, in the order it happened

`tools/ops_repo_contract_battery.py` landed at `af958429e` with a pre-registration naming eight
contracts and predicting all eight would survive all three caller suites. It was then run:

```
$ python3 -m tools.ops_repo_contract_battery --out /var/tmp/ops_repo_battery_results.json
BASELINE (no mutation, full pass, reds recorded and later deselected)
POISON (import-time raise -- proves each suite can go red for this subject at all)
  tests/background/test_delivery_lane.py: control stayed green (floor discriminates) (1.7s)
M1: all requested suites already recorded, skipping
   ... M2..M8 identically ...

SURVIVED ALL 3 CALLER SUITES: ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']
```

**That summary line is exactly the pre-registered prediction, and not one of the eight mutations
was ever applied.** The whole run took under thirty seconds and executed a single pytest pass — one
control suite that happened to be missing from the file it found.

The file it found was another lane's. A second session had run its own `ops_repo` battery minutes
earlier and written eight results to the same path. Its contracts are honest and near-identical in
spirit and different in fact — its `M3` is *"the refusal NAMES the repo it protected"*, mine is
*"the refusal carries its OWN TYPE"*; its `M7` is *"the timeout NAMES the lock file"*, mine is
*"the lock deadline is REACHABLE"*; its `M8` is *"the guard CALLS in_test_process()"*, mine is the
deadline mutation. Eight rows, eight ids, two different sets of edits.

## Why it was possible, which is the part that generalises

Two independent keys collided at once, and either alone would have been enough.

1. **`--out` defaulted to a path derived from the SUBJECT's name** —
   `/var/tmp/<name>_battery_results.json`. One subject, one filename, however many specs.
2. **The resume cache was keyed on the mutation ID.** Every spec in this family numbers its
   contracts `M1`..`M8`, because the shape was copied from the first one. So a row is looked up by
   a label that carries no information about what the row measured.

And the row's own prose does not save you: `results["mutations"].setdefault(mid, {"contract":
contract, ...})` keeps whichever contract string arrived first. The JSON on disk therefore carried
the *other lane's* description of each contract, under my ids, reported by my run.

**The instrument built to establish that a kill came from running the code published eight
survivals that no run produced.** `da7336230`'s own commit message — *"a kill is not proof the code
ran"* — was written about the null round, one level down. This is the same sentence about the
battery itself.

## Why the existing floors did not catch it

They are all inside a mutation round, and no mutation round ran.

* The **target-present-exactly-once** assertion fires when a patch is applied. Nothing was patched.
* The **`held_through_run`** check compares the subject on disk to the mutated text. No row was run,
  so no row was re-checked; the eight `held_through_run: true` values in the file were the other
  lane's.
* The **poison round** did its job perfectly and is the reason this was caught at all: it printed
  one line where it should have printed six, because five of the six suites were already recorded.
  A floor that has already run for someone else is a floor that does not run for you.
* **`NOT YET GRADED ON EVERY SUITE`** — the engine's own guard against reporting a partial run as a
  finished one — stayed silent, because by its own reckoning the run was complete.

Every one of those controls asks *did this mutation get applied and did the suites see it*. None
asks *is this file about MY mutations at all*. That is the gap: **a resume key that names the
subject but not the work is a key that cannot tell two experiments apart.**

## The repair

`tools/contract_battery.py` grows a `fingerprint(spec)`: a sha256 over the subject, the suites,
the controls, the poison and null anchors, and every mutation's **OLD and NEW text** — the ids are
included but never alone, because a renumbered mutation and a rewritten one are both different
work.

It is used twice, and the two are not redundant:

* **In the default filename.** Two specs for one subject no longer collide by default at all. This
  prevents the accident.
* **As a resume gate that FAILS CLOSED with a named reason.** A results file whose stored
  fingerprint differs is refused, exit 2, printing both fingerprints and what to do. This catches
  it when someone passes `--out` explicitly, which is what both colliding runs did.

**An absent fingerprint is refused exactly as hard as a wrong one.** A file written before this
check existed cannot say which spec scored it, and "cannot tell" is not "matches" — the same rule
the null round already applies when it stamps `grades_text: null` rather than `false`.

`tests/tools/test_a_battery_cannot_resume_another_specs_results.py` proves it, and proves it can
fail: with `if results and stored != fp:` replaced by `if False:`, the two refusal legs go red and
the five others stay green. The leg that makes that meaningful is
`test_the_partition_is_real_and_its_own_spec_still_resumes` — without it, `return 2`
unconditionally passes every test of a refusal while killing every battery in the family, and this
project has walked into that trap three times through three different doors.

## What this does not establish, and what it costs

The other lane's eight rows are not wrong — they are a real measurement of a real set of contracts,
and they say the same thing mine predicted. **That is what makes this dangerous rather than
obvious:** the false result agreed with the pre-registration to the letter. Had the two specs
disagreed, the collision would have announced itself. Agreement is the condition under which this
class is invisible, and agreement is the common case when two lanes are drawn onto one subject.

A second lane is working this same subject concurrently. Nothing in the drawn direction, the claim
store or the tree said so; it was discovered from a file mtime in `/var/tmp`. That is filed here as
an observation and not repaired — `background/delivery_lane.py` binds *landed paths*, and neither
lane had landed when they collided in a scratch directory. Whether claim binding should extend to
in-flight scratch is a decision, not a drive-by.

The contaminated evidence is preserved at `/var/tmp/ops_repo_battery_results.json` (the collision)
and `/var/tmp/ops_repo_battery.json` (the other lane's own run), both outside the tree and both
readable until `/var/tmp` is cleared.
