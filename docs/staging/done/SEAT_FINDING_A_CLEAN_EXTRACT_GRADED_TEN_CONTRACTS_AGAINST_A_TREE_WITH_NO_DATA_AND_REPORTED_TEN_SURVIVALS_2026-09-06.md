**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** controls_that_cannot_fail

# FINDING: a clean extract graded ten contracts against a tree with no data, and reported ten survivals

**Measured 2026-09-06 01:20–01:35 BST, delivery seat, worktree `/var/tmp/se-gif-battery` at
`6c92cc0c7`. Claim id `convergence-sweep-subject-4-grid-intensity-feed`. Subject:
`tools/generate_grid_intensity_feed.fuel_mix`, the sweep's fourth. Pre-registration landed at
`da7336230`.**

---

## What happened

The battery was run in a fresh `git worktree add --detach` extract rather than in the shared
tree, deliberately: a battery mutates its subject in place for the length of the run, and 20
minutes of that in a tree six other lanes are committing from is how a gate reds for somebody
else. The extract is the safe room.

It returned a clean, complete, entirely worthless verdict:

```
SURVIVED ALL: ten mutations, nine suites, not one kill
POISON:       3 suites reach the subject, 6 never do, 2 controls stayed green
NULL ROUND:   all nine behaviour only
```

Three suites reached the subject under the import-time floor. The two control suites stayed
green, so the floor discriminated. The null round was clean, so no kill was textual. **Every
column the instrument prints said the measurement was sound, and none of it had run.**

## The cause

`sim/cache/` is line 3 of `.gitignore`. A `git worktree` extract contains no ignored files, so
the extract had no `elexon_fuelhh_*.json`, no demand cache, no AGWS cache — none of the data
`fuel_mix()` exists to load.

The tell was in the baseline and nobody would read it as one:

| suite | in the extract | with the cache linked |
|---|---|---|
| `tests/tools/test_grid_intensity_feed_and_explore_carbon.py` | **43 passed in 0.24s** | **43 passed in 9.12s** |
| `tests/sim/test_elexon_fuel_outturn.py` | 35 passed in 0.12s | — |

Not 43 skipped. Not 43 errors. **Forty-three passed, in a quarter of a second, thirty-eight times
faster than the same suite on the same commit with its data present.** A green baseline with the
full test count is what the battery checks for and it is exactly what it got.

## Why the poison floor could not catch it, and this is the general point

The floor is an import-time `raise`. **Whether a module can be imported does not depend on
whether its data exists.** So the floor answered honestly and the answer was irrelevant: those
three suites really do reach the subject, and in this tree not one of them could execute a line
of `fuel_mix`'s body, because the first thing that body does is open a file that is not there.

Worse, the two contracts most worth grading are the *fail-closed* ones —
`test_the_feed_REFUSES_to_publish_without_the_fuel_mix...` and its biomass twin, both written as
`with pytest.raises(FuelOutturnUnavailable): gif.fuel_mix()`. **With no cache at all, those tests
pass no matter what the mutation did.** The expected exception is raised — by the missing file,
not by the contract. A test that asserts a refusal is precisely the test that a data-less tree
cannot distinguish from its own subject working.

## The state this adds to the family

The sweep already records three:

1. **never imports it** — the poison floor catches this, and announces it as blind.
2. **imports it and never executes the contract** — the `ops_repo` state (subject 6): every caller
   patches the name in its own namespace. The floor does *not* catch this; the
   `imports_but_proves_nothing` column added afterwards does.
3. **executes it** — the good answer.

This is a fourth, and neither existing column sees it: **imports it, enters the contract, and the
contract cannot reach its inputs.** Every mutation survives. Every diagnostic reads clean. The
`imports_but_proves_nothing` column would have flagged the three reaching suites here — but it is
uncommitted in the shared tree (31 lines, `tools/contract_battery.py`), so the extract at `HEAD`
ran without it and printed nothing at all. *A repair that is live in one tree and absent from the
record is its own recurring shape, and it cost this run its only warning.*

## The repair, and it is a floor not a note

A clean extract is the right room to mutate in and the wrong room to measure in, and the
difference is the ignored files. Two things follow, and only the first is optional:

* **Link the ignored data before the run.** `ln -s <shared>/sim/cache sim/cache` in the extract.
  Done here; the re-run's numbers are in the RESULT beside this file.
* **The battery must assert its own baseline is not vacuous.** The engine already records
  `seconds` per suite in the baseline. It does not compare them to anything. A subject whose
  caller suite runs 38× faster than its own recorded history has not been graded, and the
  battery is the one thing in the tree positioned to notice. Proposed: `BatterySpec` gains an
  optional `baseline_floor_seconds` per suite, taken from the direction that named the suites
  (this subject's was given as "0.8s / 9.1s" in the drawn item — the 9.1s was the true figure and
  the extract's 0.24s would have failed the floor immediately).

**Keyed to the property, not to today's answer**: the assertion is *"this suite took the time it
takes when its data is present"*, which stays true when the contract becomes more honest and goes
red when the room changes underneath it.

## What this does NOT establish

Nothing about `fuel_mix` itself. The void run is discarded entire, not reinterpreted — a row
measured in a tree where the subject could not execute has no verdict, and reading its greens as
"unproved" would be the flattering error this whole sweep exists to stop. The graded answer is
the RESULT document beside this one, from the re-run with the cache linked and a **fresh results
file** (never a resume onto the void rows).

One result from the void run does survive, because it is cache-independent by construction: the
import-time floor's finding that **six of the eight `ep13_*` caller suites never reach the subject
at all.** They import `fuel_mix` inside a function body that the suites never call. That is
carried into the RESULT.
