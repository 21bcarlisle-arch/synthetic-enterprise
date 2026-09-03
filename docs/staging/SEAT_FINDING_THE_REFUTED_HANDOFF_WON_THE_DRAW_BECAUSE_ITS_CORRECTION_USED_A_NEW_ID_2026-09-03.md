**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The refuted handoff won the draw because its correction was written under a new id

**Class:** `controls_that_cannot_fail` (primary), `figures_on_a_superseded_clock` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0, claim
`land-the-live-world-undecomposed-floor-leg`
**Subject:** `background/seat_continuation.py::hand_off` — the de-duplication keyed to the id
string — and `live()`'s oldest-first ordering.

## What was found

`hand_off`'s docstring made a promise:

> Re-recording the same `work_id` REPLACES it and restamps the clock, so a session that refines
> what it is handing over **does not leave two versions competing**.

The guard behind that sentence is one line:

```python
items = [i for i in _load(path) if i.get("id") != work_id]
```

**It is keyed to the id string, so it only fires when the refinement reuses the id.** A session
that refines the same *subject* under a *new* id — the natural thing to do when the correction is a
different act — leaves exactly the two competing versions the docstring says cannot exist. And
`live()` returns them oldest first, by deliberate design ("order is the seat's order"), so the
**refuted** entry is offered **first**. Not by luck: deterministically, every tick, until it ages
out six hours later.

## It had already fired, and this tick is the evidence

| Local (BST) | Event |
|---|---|
| 15:18:37 | the undecomposed floor leg's first run succeeds and writes its artefact, untracked |
| 15:35:25 | `ensure_worktree`'s `git clean -qfd` deletes it (filed at `ff8e27ce3`) |
| ~15:45 | seat writes `land-the-live-world-undecomposed-floor-leg`: *"the file already exists at `/var/tmp/se-seat-executor/…`… the only thing standing between this and done is a `git add`"* |
| 16:07:03 | the measurement is correctly relaunched as `se-floor-all-20260903c.service`, `--out` **outside every worktree** |
| ~16:12 | seat writes the correction as a **new id**, `pick-up-the-relaunched-undecomposed-floor-leg`, which says the artefact was deleted, the re-run is in flight, and *"do NOT relaunch a third run"* |
| 16:23 | **the tick is handed the 15:45 entry.** It is told to `git add` a file deleted 48 minutes earlier |

Measured at the store, before the fix:

```
STALE  6.12h  the-baseline-was-beaten-in-a-world-that-no-longer-exists
LIVE   0.49h  land-the-live-world-undecomposed-floor-leg      <- refuted, and OLDER, so offered first
LIVE   0.30h  pick-up-the-relaunched-undecomposed-floor-leg   <- the correction, never reached
```

The 16:23 tick spent its whole orientation re-establishing what the correction sitting one entry
below it already said in full: that the file was gone, that the number was unrecoverable, and that
a second run was already 23 minutes in. **The prior seat did everything right — it diagnosed the
deletion, relaunched with the artefact outside every worktree, and wrote the correction down. The
store then handed the next tick the version it had just refuted.**

This is the "key a control to the property, not to today's answer" rule at one remove. The property
is *"this instruction has been superseded"*. The key was *"the two entries happen to share a
string"*.

## The fix, and what it deliberately does not do

`supersedes` — an explicit list of ids an entry retires. `live()` does not offer a retired entry,
so a refuted instruction stops competing with the judgement that refuted it.

**Nothing infers subject overlap.** An inferred supersession would silently bury a live
instruction, which is a worse failure than the one being fixed, and no heuristic here could tell
"this replaces that" from "these are adjacent". The seat declares it or it does not happen.

Three properties the implementation carries on purpose:

1. **Once superseded, always superseded.** `_superseded_ids` does not ask whether the *superseding*
   entry is still live. Supersession is a fact about the subject, not about the clock — and keying
   it to the clock would resurrect the refuted instruction the moment its correction aged out, *as
   the oldest live entry, i.e. first*. This is not hypothetical: `seat_executor` promotes focus
   items to continuations automatically, so a retired id can be re-stamped fresh by a derivation
   that never knew it was refuted.
2. **A retirement is never silent.** A superseded entry inside its window appears in neither
   `live()` nor `expired()`. If it printed nowhere, a supersession would read exactly like the
   store having lost a write. `superseded()` reports it, naming *which* entry retired it, and
   `--list` prints it as `RETIRED`. This store's own history is the argument: `expired()`'s
   docstring records a day spent reporting its only success as its defining failure, because of a
   join nobody had made.
3. **A self-reference is ignored, not honoured.** One mistyped id would otherwise erase the seat's
   own judgement and report the entry as retired by itself.

`expired()` also stops reporting retired entries as *"written and never taken; that is the drag"* —
a correction is not a drag.

## Controls

Five legs in `tests/background/test_seat_continuation.py`, each mutation-proven (`python3 -B`, so
no stale-`.pyc` survival):

| Leg | Mutation that makes it fire |
|---|---|
| `…_a_refinement_under_a_NEW_id_RETIRES_the_refuted_one_rather_than_LOSING_to_it` | drop the `_superseded_ids` filter from `live()` — the refuted entry returns and, being older, is drawn **first** |
| `…_a_RETIRED_entry_is_REPORTED_and_not_silently_filtered` | make `superseded()` return `[]` |
| `…_an_EXPIRED_correction_does_not_RESURRECT_the_instruction_it_retired` | key `_superseded_ids` to entries inside the window |
| `…_an_entry_naming_ITSELF_is_still_offered` | remove the `dead != item.get("id")` guard |
| `…_a_handoff_with_no_supersedes_stores_NO_such_key` | always write the key — every historical entry grows an empty field on a live ledger |

The first leg asserts the **draw**, not just `live()`: `delivery_lane.next_item` must hand the tick
the correction. `live()` being right is not the property that matters.

Verified on the live store after the fix — `next_item()` now returns
`pick-up-the-relaunched-undecomposed-floor-leg`, and `--list` prints the refuted entry as
`RETIRED … not offered`.

## What is NOT done in this tick, and why

The drawn work's steps (a)–(d) — grade `P4`/`P6`/`P7`, re-run `--decompose`, regenerate
`site/data/value_arms.json`, update the `/capabilities/` headline — **all depend on the artefact,
and the run producing it is still in flight** (`se-floor-all-20260903c.service`, started 16:07,
~2h25m expected, ETA ~18:32). This is a bounded invocation; it cannot wait for it, and re-running
a third time would spend a third ~2h25m on a number two runs have already computed.

**One correction to the drawn instruction, recorded beside it.** The doorbell says P6 and P7 "read
as confirmed already — stdev 5,923.0446 against the predicted 5,923.04±5%". That figure was read
out of the artefact `ensure_worktree` deleted. It is a quotation of a destroyed file with no
surviving primary record, so **it cannot grade a pre-registration** — grading a prediction against
a remembered number is exactly the shape the pre-registration discipline exists to refuse. P4, P6
and P7 must be graded against the run now in flight, and the continuation entry now says so.
