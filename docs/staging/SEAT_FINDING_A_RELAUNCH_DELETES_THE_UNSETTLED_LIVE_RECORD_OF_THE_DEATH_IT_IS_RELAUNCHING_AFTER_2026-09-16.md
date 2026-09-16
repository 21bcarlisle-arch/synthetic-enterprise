**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SEAT] A relaunch deletes the unsettled `live` record of the death it is relaunching after, and destroys the systemd evidence too

**Found while dispositioning `.launch_records.json`** for the self-clearing-alarm census. It is
filed separately rather than being buried in the row's `why`, because the register's two verdicts
cannot express it: `benign` is the correct answer to the question the register asks, and grading it
`real` would demand a guard that cannot fail. See
`docs/design/self_clearing_alarm_dispositions.json`, key `.launch_records.json`.

## The defect

`background/launch_liveness.py::record` removes the existing row for a job **unconditionally**:

```python
records = [r for r in load(path) if r.get("job") != job]
```

It never looks at `claim`. So this sequence loses a page:

1. Job `X` dies. Its record still reads `claim: live` — `check()` has not run yet, because
   `deadmans_switch._check_launch_liveness` runs on the deadman cycle, not on the death.
2. Somebody relaunches `X`. `launch_long_job.launch()` permits it: `name_is_held()` refuses only a
   relaunch over a unit that is **alive**, and `clear_a_corpse()` exists precisely to clear a dead
   one's name and let the launch proceed.
3. `record()` drops `X`'s stale `live` row and writes a fresh `live` one.
4. The deadman next cycles, finds nothing stale, and `clear_transition`s. The
   `[LAUNCH DIED]` `real_alarm` that `_check_launch_liveness` exists to raise never fires, and
   every document in the deleted row's `asserted_live_by` is never contradicted.

**And the evidence is destroyed on a second, independent path.** `clear_a_corpse()` runs
`systemctl --user reset-failed`, which makes systemd forget the unit's exit record. `reask()` is
documented to ask systemd FIRST *because* that verdict "survives the kill it reports" — after
`reset-failed` there is no `Result` to read, so `reask()` falls through to `UNKNOWN`, and `check()`
by design does not settle on `UNKNOWN`. So even if step 3 had preserved the row, the death would
now be unsettleable.

Both legs measured, 2026-09-16. P5 of the pre-registration
(`SEAT_PREREGISTRATION_WHAT_THE_LAUNCH_RECORDS_LOADER_AND_WRITER_WILL_DO_BEFORE_I_DISPOSITION_THE_ROW_2026-09-16.md`),
written before any of it was run:

```
=== P5: record() over an UNSETTLED live record for the same job ===
  before: [{"job": "X", ..., "launched_at": "2026-09-01T00:00:00Z",
            "asserted_live_by": ["docs/somewhere.md"], "claim": "live", ...}]
  after relaunch record(): [{"job": "X", ..., "launched_at": "2026-09-02T00:00:00Z",
            "asserted_live_by": [], "claim": "live", ...}]
  rows for job X: 1 | the old live claim survives: False
```

## Why this is the module's own founding defect, arriving by a different door

`launch_liveness.py` opens: *"THE DEFECT THIS EXISTS FOR, and it has now cost four launches of one
job."* Four launches of one job **is** four relaunches of one job name. The module was built to
make a stale in-flight claim contradictable by something other than a person checking a pid — and
the relaunch that follows a death is the single most likely event to occur inside the window where
the contradiction has not yet been written. The exposure window is exactly "death → next deadman
cycle", and a relaunch is one command.

I have not found an instance in `docs/observability/.launch_records.json`'s history where this
actually fired; its three commits do not contain a replaced `live` row. So this is LATENT, not an
incident: reachable, cheap to reach, and not yet observed.

## Why it is not graded `real` in the census

The register's `real` verdict means: an episode-start timestamp or a consecutive-failure counter
**that an alarm reads for SEVERITY**, resettable by a write that has not demonstrated the episode
ended — and its remedy is the append-or-monotonic guard in `background/episode_monotonic.py`.

Measured: no alarm reads `launched_at` or `settled_at` at all; nothing outside `launch_liveness`
and `launch_long_job` touches either field. The only severity split in the class reads `claim`, a
categorical state, and `check()`'s settling is one-way.

And the remedy would not work. Guarding `launched_at` monotonically is **vacuous here**: every
legitimate relaunch moves it forward, so the guard would refuse nothing it was installed to refuse
— a control that cannot fail, which is the thing this register exists to stop shipping.

## The remedy I would build, stated so it can be argued with before it is built

Not `episode_monotonic`. The honest shape is a **refusal at the launcher**, matching the one
already next to it: `name_is_held()` refuses a relaunch over a live *unit*; nothing refuses a
relaunch over an unsettled *claim*. So:

- `launch_long_job.launch()` re-asks (`launch_liveness.check()`) **before** `clear_a_corpse()`, so
  the prior run is settled against systemd's record while that record still exists; and
- `record()` refuses — or preserves, under a settled-history key — a row whose `claim` is still
  `live`, rather than dropping it silently.

The ordering is the substance: settling must precede `reset-failed`, or the evidence the settling
depends on is already gone. A done-condition that can fail: a test that relaunches a job over an
unsettled `live` record and asserts the death is *still* settleable afterwards — red on today's
code, green on the fix, and not satisfiable by any guard that merely refuses everything.

**Not built in this turn.** The turn's claim was the disposition row; this is the finding the row
uncovered, and inventing the fix under it would be the "short-term fix that comes undone when it
meets the rest of the system" the knowledge-first rule names. Ordering it is the next seat
decision.

*Filed 2026-09-16 by the delivery seat, claim `self-clearing-alarm-census-launch-records-disposition`.*
