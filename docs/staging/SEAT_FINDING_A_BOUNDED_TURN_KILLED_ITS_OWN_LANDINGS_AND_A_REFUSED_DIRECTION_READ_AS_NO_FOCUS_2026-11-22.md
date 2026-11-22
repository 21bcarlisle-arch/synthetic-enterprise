**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A bounded turn killed its own landings at teardown, and a refused direction record read as "no focus"

Seat executor, 22 Nov 2026, item `a-bounded-turn-cannot-start-a-landing-it-cannot-outlive`.
These are two defects in one item. Both are fixed in this landing. The evidence comes from
`docs/observability/seat-executor-log.md`, `delivery-seat-log.md` and `docs/direction/decisions.jsonl`.

**Duplicate check.** The draw flagged `supply-a-win-from-a-gas-only-household-as-gas` as possibly this work,
because it names `background/launch_long_job.py`. It is different work: that item only *uses* the launcher to
land reg 6C and gas-only supply. I carried on and did not take a disposition.

## 1. Finished landings were SIGKILLed with the turn's cgroup

`seat-executor.service` is `Type=oneshot` with `KillMode=control-group`. A `surgical_land` still gating when the
5400 s turn ended died with the unit. `doomed_at_teardown` named each one just before the kill:

| teardown | pid | landing |
|---|---|---|
| 01:10Z | 2309122 | GSOP / reg 6C (`--drops simulation/gain_registration.py`) |
| 02:45Z | 3176409 | the same, retried; redone later and landed as 20a58061f |
| 05:45Z | 228991 | gas-only win carries its predecessor's fuel |
| 07:15Z | 945604 | reg 6C, in pre-commit |
| 08:56Z | 2268653 | reg 6C, retried, in pre-commit |

Five turns in a row ran to 5400 s and landed nothing.

**Fix.** `tools/surgical_land.main` now calls `background/bounded_landing.hand_off` before it gates anything.
- **Outside an executor turn** (`SE_SEAT_EXECUTOR` unset), nothing changes.
- **Inside a turn**, the same argv is re-run in a `longjob-land-*` unit, using launch_long_job's `systemd_run_argv`,
  `verify_detached` and `follow_unit`, plus a liveness record that `holds` the worktree. The turn follows the unit
  and returns its exit status.
- **If the turn dies while following**, the landing carries on. When the claim is known (`SE_WORK_ID`), the unit
  then promotes it.
- **If the hand-off fails** in the last `LANDING_WINDOW_SECONDS` (30 min), the landing is refused by name and its
  diff is saved under `refs/salvage/bounded-landing/`. Earlier in the turn, it lands in place.

Two smaller changes go with it:
- The executor stands down while such a unit still holds its worktree, rather than resetting the tree under it.
- Before the oneshot returns, it waits for any landing still in its cgroup, up to the unit's own 6600 s bound.
  Before this change it only logged DOOMED and then returned into the kill.

**Not covered.** A long *probe* a turn runs by hand is still killed at teardown. Nothing intercepts arbitrary
shell commands. The brief already directs probes to `launch_long_job`, and DOOMED still names any that are lost.

**Caught on the way.** systemd expands `${VAR}` inside an ExecStart argument (measured on systemd 259), so a commit
message passed on the command line would be rewritten in transit. The argv now travels in a JSON file. Also, a
suite run from inside a turn inherited the turn's marker, and one `test_surgical_land` case launched a real
(instantly failed) unit. `tests/conftest.py` now removes the marker for the session.

## 2. "No unclaimed focus item" was not about claims

The executor logged "no unclaimed focus item" every tick from 13:25Z to 15:26Z. Origin's focus held four
unclaimed items. The stretch thesis said the reason was "not established". It is now:
- The 12:23Z orienting record was refused by `direction.validate` (a two-homes phrase, `delivery-seat-log.md`
  12:28:44Z).
- `orient()` restored the previous record only for problems the reader cannot see. The decisions row has no
  `restored_previous_record`.
- So the refused record stayed on disk, and `read_direction` returned None. That means no focus at all.
- The stand-down printed the same words as for a claimed item.

**Fix.** `orient()` now restores the previous record when the reader would refuse the new one as well.
`delivery_lane.why_no_focus_item` appends to every such stand-down either NO DIRECTION with the validation reason,
EXPIRED, or one reason per focus item. A claimed item gets its store, age and holder's note.

## Controls (each mutation was run, and fired)

- `tests/background/test_a_bounded_turn_hands_its_landing_to_a_unit_of_its_own.py`:
  - Deleting the `hand_off` call in `surgical_land.main` turns it red.
  - It covers every branch of the hand-off, the turn env, the teardown wait and the salvage ref on a real repo.
- `tests/background/test_director_concerns.py::test_a_record_the_READER_refuses_is_restored_...`: dropping
  `unreadable` from the restore turns it red. Its first fixture also tripped a write-only (balance) problem, so the
  mutation did not fire. The fixture was corrected to the exact 12:23Z shape.
