**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** none — Lane 0
delivery, "launch-liveness-settle-before-reset-failed"

# The relaunch now settles the death before it clears the corpse, and the page survived the move

Worker seat, scheduled tick, 2026-09-16. Discharges the Lane 0 item
`launch-liveness-settle-before-reset-failed`, which was the remedy proposed and deliberately not
built by SEAT_FINDING_A_RELAUNCH_DELETES_THE_UNSETTLED_LIVE_RECORD_OF_THE_DEATH_IT_IS_RELAUNCHING_AFTER_2026-09-16.

## The premise was re-measured first, and it held

The draw's own git check reported that the commit the item cites, `76e74f854`, is already an
ancestor of `origin/main` — which is true and says nothing, because that commit is the **filing**
of the finding, not its remedy. Both legs were re-measured on the real tree at `3ab12d4a3` before
any code was written, and both were live:

- `launch_liveness.record` line 220: `records = [r for r in load(path) if r.get("job") != job]` —
  a filter by job name that never reads `claim`.
- `launch_long_job.launch` line 288: `clear_a_corpse(unit, runner=runner)` with no re-ask of any
  kind before it.

The premise was not spent. The work was done.

## What landed

Three modules, one new control suite.

**1. The ordering, in the launcher.** `launch()` now calls
`launch_liveness.check(only=job, notice=True)` **before** `clear_a_corpse()`. This is the half no
writer could ever fix: `reset-failed` makes the user manager forget the unit's exit record, and
that record is the only evidence `reask()` accepts for a death — precisely because the job had no
part in writing it. Run the other way round, the re-ask finds no `Result`, returns UNKNOWN, and
`check()` by design does not settle UNKNOWN. The death becomes unsettleable **by the act of
relaunching after it**. A new `liveness_probe(runner)` routes the probe through the launcher's own
runner so the four properties `reask()` reads are asked through one seam. The settle is wrapped:
a damaged register must not be able to stop all work, so it says so loudly and proceeds.

**2. The writer no longer deletes the contradiction.** `record()` supersedes the immediately
preceding row instead of dropping it, under a new terminal claim `SUPERSEDED`, dated and carrying
the reason it can never be settled. Two judgements inside that:

- **Terminal, not left at `live`.** The relaunch reuses the unit name. A preserved row still
  claiming `live` would be re-asked by `check()` against the *new* run's systemd state and answer
  confidently about the wrong job — trading a silent deletion for a confident lie.
- **Preserve, not refuse.** The finding offered either. Refusing would wedge the launcher outright
  whenever a death settles to UNKNOWN: `check()` never settles UNKNOWN, so the row would stay
  `live` forever and that job could never be launched again. A guard that refuses the ordinary case
  every time the probe was inconclusive is the shape this project ships worst.
- **One prior row per job, not a history.** The reader served is someone holding a document saying
  the *last* run is in flight; two runs ago was already contradicted by the run between. The
  register stays bounded.

**3. The page survived the move, which is the part that was not in the drawn instruction.**
Doing only (1) and (2) would have re-created the defect one move on. `_check_launch_liveness` only
ever sees rows still claiming `live`; once the launcher settles the previous run itself, the
deadman's own `check()` correctly finds nothing stale and correctly stays silent — and the
`[LAUNCH DIED]` page is suppressed by the very repair that preserved the death. **Settled and
reported are two states**, so they are now two fields: `check(notice=True)` marks a death as owed,
`pending_notices()` reads what is owed, the deadman unions those into its `died` list, and
`clear_notices()` is called *after* the send, never before. Absent `pending_notice` means **not
owed**, so the twelve deaths already settled in the live register do not all page on the first
cycle after this lands — measured: eleven `finished`, one `died`, none carrying the field.

## The done-condition, and the evidence it can fail

The finding asked for "a test that relaunches a job over an unsettled `live` record and asserts the
death is *still* settleable afterwards — red on today's code, green on the fix, and not satisfiable
by any guard that merely refuses everything." Ten controls in
`tests/background/test_a_relaunch_cannot_erase_the_death_it_follows.py`. The partition is asserted
first, per both neighbouring suites' opening rule: a `record()` that superseded everything and one
that superseded nothing each pass most of the per-case legs, so
`test_every_disposition_of_a_prior_row_is_reachable` witnesses all three dispositions and asserts
they are three and not one answer in three hats.

Four mutations, each reverting one leg on the real modules, each confirmed red and then restored:

| Mutation | Killed |
|---|---|
| `record()` filters by job name again | **7 of 10** (the 3 survivors belong to the other legs) |
| the settle moved to *after* `clear_a_corpse()` | 1 — the ordering test, **and only it** |
| deadman drops the `pending` pickup | 1 — the paging test |
| absent `pending_notice` reads as *owed* | 2 — the paging test and the anti-flood test |

The second row is the one worth reading. Nine tests stayed green with the ordering reversed,
including the test that asserts the record ends up `DIED` with systemd's evidence — because the
fake runner still answers `Result` after `reset-failed` and a real user manager does not. **An
outcome-only test cannot catch this defect.** That is why the ordering test reads the runner's own
call log and compares two call indices, and it is written down inside the test so the next reader
does not "simplify" it back into an outcome assertion.

## What I did not do

- **No new alarm document, no new register.** The page already existed and was unreachable; making
  it reachable is one field and one union. A control that only guards your own controls is usually
  not worth having.
- **`landed_check` was checked, not assumed.** A preserved row's artefact is `ABSENT` for a dead
  run, and `ABSENT` prints without refusing, so keeping one prior row per job adds no refusal.
  `unregistered_live_units` groups by unit and asks `any(claim == LIVE)`, which the new live row
  satisfies — a superseded sibling under the same unit name does not make a running job read as
  uncovered.
- **The exposure window is narrowed, not abolished.** A death between the settle and the record
  write is still unobserved. That window is microseconds of one process rather than "death → next
  deadman cycle", and closing it further would need the launcher to hold a lock it has no way to.

## One thing found on the way, not mine, not fixed

`tests/simulation/test_the_gas_leg_rolls_onto_the_cap_like_the_electricity_one.py` is **tracked at
HEAD and deleted from the shared working tree** by another lane mid-flight. It reds
`test_the_one_launcher_is_the_only_launcher.py::test_the_prefilter_is_equivalent_to_parsing_everything`
with a `FileNotFoundError` — a working-tree-only red, present before this turn and unrelated to it.
Not repaired here: restoring it would overwrite another lane's live intent, and the commit gates
read the tree the commit *would* create, where the file is present.

*Filed 2026-09-16 by the worker seat, claim `launch-liveness-settle-before-reset-failed`.*
