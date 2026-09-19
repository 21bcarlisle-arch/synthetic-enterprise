**Severity:** BLOCKING · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:**
W1_14_weather_cells_for_household_heat_load

# RESULT: the same nine paths were stranded by the same step on two consecutive nights, and the document generalising that failure was written between them

Delivery seat, 2026-09-17. Claim `land-the-per-cell-weather-store-and-wire-its-reader`.
Pre-registration: `docs/staging/records/SEAT_PREREG_THE_WEATHER_STORE_LANDING_IS_ALREADY_RUNNING_IN_ANOTHER_LANE_2026-09-17.md`,
written at 04:06 before any measurement below and before the other lane's process had exited, and
landed in 6e02d6442 rather than in this commit.

## 1. THE PREMISE WAS NOT SPENT, AND P1 WAS REFUTED

The draw's own premise check said both cited commits were already ancestors of `origin/main`, which
is true and is not the question — they are the *machinery*, and the item was about the *artefact*.
What I found instead, three minutes into the turn, was **PID 1092137: another lane running
`tools.surgical_land` on the shared tree, started 03:43, carrying the exact path list of my item.**

I predicted (P1) that it would land and that the wiring half of my item was therefore spent. **P1
is refuted.** The process ran 32 minutes and exited at 04:15 having produced **no commit anywhere**:

    git log --oneline -4 origin/main        -> unmoved at 6c1e769b4
    git ls-tree -r origin/main -- sim/weather_world/   -> empty
    shared tree HEAD                        -> 1a69fbb23, a liveness heartbeat, not the work
    git log --all --grep="per-cell weather store is wired"  -> nothing
    the worker's own claude process (842191) -> DEAD

Nine paths were left as working-tree bytes on the shared disk, including the WORKER_RESULT document
asserting the work was done.

## 2. THE GENERALISABLE ONE, WHICH ALREADY EXISTED AND DID NOT WORK

This is the **second consecutive night** that these same paths were stranded at the same step. The
turn of 2026-09-17 00:xx filed
`SEAT_RESULT_THE_STRANDED_WEATHER_MACHINERY_WAS_ONE_LAND_SHORT_...`, whose closing section says, of
these exact files:

> **`surgical_land` is not the last step of the work; it is the step that makes the work exist.**
> Everything before it is a description of a tree nobody else has.

That was written **twelve hours before the recurrence, about the same paths, in the same lane.** The
lesson was correct, it was recorded prominently, and it did not prevent anything. **A retrospective
that names a failure mode is not a control over it** — which is this project's own rule about
building the smallest mechanism that can fail, applied to itself and failing.

The difference between the two nights is instructive rather than exculpatory: night one was a lane
that *never ran* the landing step; night two was a lane that *ran it and died inside it*. A rule
aimed at "remember to land" only addresses the first. **The mechanism worth having asks the tree,
not the author:** whether uncommitted work older than some interval exists on paths a claim is bound
to. That is a finding filed here, not built in this turn, and it is deliberately not a new register
— a one-leg check on the existing stranding alarm is the cheaper shape, and the alarm
`WORKER_FINDING_REPEATING_ALARM_...` machinery already runs.

## 3. WHAT I RE-MEASURED RATHER THAN ADOPTED, AND THE NUMBERS

Every figure in a stranded commit message is its own author's claim about a tree nobody else has, so
none were taken on trust.

| claim, from the dead lane's message | my measurement | verdict |
|---|---|---|
| 52 of 221 cells hold temperature only | 52 of 221, counted from the gzip directly **and** independently by `validate_weather_world` (189,956 rows with no wind/cloud/precip) | **P3 CONFIRMED** |
| the fabric suite is green | 82 passed, on **this** base | confirmed, and see below |
| the store is complete and consistent | 221 cells, 221 regimes, 807,313 rows, 2016-01-01..2025-12-31 no gaps, temperature centred on zero (worst \|mean\| 0.00000 C) | confirmed |

The green mattered because **it had to be re-measured on a different base**: the shared tree's HEAD
(`1a69fbb23`) and `origin/main` (`6c1e769b4`) are **diverged — neither is an ancestor of the other**.
A green measured over there was not evidence about here, and this is the memory-rule that a green in
the shared worktree measures several lanes rather than your change.

## 4. THE PATH I REFUSED TO CARRY, AND HOW IT WAS FINDABLE

`tools/weather_cell_drivers.py` is modified on the shared disk and its working copy adds the
`longitude` line `book_cells()` cannot run without. **That line is already at `origin/main`** — it
landed in `f0af86639`. The shared tree's HEAD is simply *behind* on that file, so its working diff
is a re-application, not holder work.

The tell was mechanical and worth keeping: of the seven tracked paths, I asked which differ between
the two HEADs. **Six are byte-identical at both heads — which is what made taking their bytes
safe — and exactly one differs. That one was the one not to take.** This is the cheap version of the
stale-versus-holder question, available before reading a single diff.

## 5. THE ITEM'S REMEDY WAS WRONG AND THE GATE IS WHAT SAID SO — P6 CONFIRMED

The drawn item directed: *"removing all three rows from `docs/design/orphan_baseline.json` in that
same commit"*. **The tree says one row, not three.** `sim.weather_world` is now reachable and its row
is removed; `tools.build_weather_world` and `tools.validate_weather_world` **keep** theirs, because
both remain CLI entry points nothing imports and this ratchet does not count test files as
entrypoints. Removing them asserts a reachability the tree does not have.

**A drawn item's remedy is an un-re-asked prediction exactly like every other factual claim it
makes**, and the dead lane had independently reached the same conclusion — which is corroboration,
not authority, and I checked it against `orphan_ratchet` rather than against their agreement.

### The provenance field the ratchet caught, which neither of us would have seen by reading

The baseline arrived reading `module_count: 1154`. My tree has **1150**. `freeze()` writes that field
from the tree it ran in, and it ran in the shared tree, which carries four modules this one does not.
The ratchet's own report says this in as many words, including the part that matters:

> A disagreement is either ordinary drift since the last freeze, or a `freeze()` output from ANOTHER
> tree — an older checkout, an isolated worktree — pasted in, in which case the orphan list beside it
> is that tree's reachability and the rows it omits are that tree's, not this one's.

**The orphan LIST needed no change — `orphans now: 539 | baseline: 539` is the evidence it was
computed over the same reachability — so only the note was wrong**, and I set it to 1150 rather than
re-freezing, because a re-freeze would have recomputed the list from a tree carrying other lanes'
uncommitted modules. This is the shape worth keeping: **a field that is a note and never a refusal
still carried the one piece of information that distinguished "drift" from "another tree's answer".**

## 6. WHAT LANDED

Commit 6e02d6442, promoted to `origin/main` from 6c1e769b4, 11 paths bound to the claim. The store
exists in a ref for the first time: the per-cell artefact, the `WeatherWorldSource` wiring in the
settlement path and the settlement-gap tool, the writer's docstring correction, the orphan row, and
the 82-control suite.

## 7. WHAT IS STILL OWED, AND IT FAILS CLOSED

**52 of 221 cells carry temperature only.** Open-Meteo rate-limited the ERA5 pass. `available()`
REFUSES those cells rather than answering with a NaN, so no premise settles on a sky with three
missing columns — it costs coverage, not correctness, and the validator prints the FAIL on its face.
The resume was launched in this turn and its outcome is recorded in §8 below rather than predicted
here.

The per-property pull the director refused — tools/pull\_book\_weather.py, written here without
backticks because a backticked path in a findings document is read by `landed_manifest_check` as a
claim that the path is in the tree, and the whole point of this sentence is that it is not — **is
already gone from the shared disk**. Only a stale `__pycache__` .pyc remains, which imports nothing.
The item's note that it is "still untracked on the shared disk" was true when written and is spent.
