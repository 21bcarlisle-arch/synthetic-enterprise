**Severity:** LATENT · **Lane:** H_harness

**Rank:** after the remaining census reds.

# Two live worker invocations ran the identical doorbell concurrently

`observed-with-evidence` unless marked otherwise (R9).

## What is true

At 2026-08-24 07:25 BST this session was woken with a SCHEDULED-TICK doorbell (the
`unprocessed staging -- CLASS_CONTROLS_THAT_CANNOT_FAIL...` list ending in the B4_competitor_field
self-refill draw). At the same moment, `ps aux` showed a SECOND live `claude -p
--dangerously-skip-permissions --model claude-opus-5` process (pid 1817652, started ~07:25:16,
verified via `/proc/1817652` and `ps -o etimes`) running **the exact same doorbell text**
byte-for-byte, already mid-`git commit` on `docs/design/maturity_map.yaml`,
`background/worker-tick.timer`, `background/schedule_manifest.yaml`, the retired-atom-store
migration, `site/data/simplified.json`, and running a second background job
(`SE_GROW_BOOK=1 timeout 3000 python3 ... simulation.run_phase2b`).

`docs/observability/.worker_tick.lock` correctly named pid 1817652 as the sole recorded holder —
so `background/worker_tick.py`'s lock was NOT simply absent or stale; only one spawn was recorded.
This session nonetheless existed as a second live agentic context carrying the identical prompt,
so whatever spawned it either (a) is a second scheduling path outside `worker_tick.py`'s
lock-and-spawn (this project's own systemd `worker-tick.timer`/`.path` both target the SAME
`worker-tick.service` unit and the unit file's own comment claims systemd itself provides
no-stacking by skipping a trigger while the oneshot is active — consistent with only one
`worker_tick.py`-spawned child existing), or (b) is a harness-level scheduled invocation
independent of this repo's systemd units altogether, which would explain identical content simply
because both draws hit the same `find_work()` state, not because of a lock race. `inferred`: which
of these it is — I did not find a second `claude -p` line attributable to `worker_tick.py` itself
(no matching pid in the lock file, no second `worker-tick-log.md` SPAWNED entry to check against
in this bounded window), so I could not distinguish "the systemd lock raced" from "two independent
schedulers exist" without spending real time reading `worker-tick-log.md` history and
`journalctl --user -u worker-tick.service` across the exact window — deferred rather than guessed.

## Why this matters

`background/worker_tick.py::run_tick` has a real TOCTOU window regardless of the above: it checks
`invocation_in_flight()` once at the top (`worker_tick.py:379`), then does the origin-sync +
`find_work()` draw (real I/O, non-trivial wall time), and only calls `_write_lock()` **after**
`spawn_invocation()` returns (`worker_tick.py:394-397`). Two `run_tick()` calls whose check-windows
overlap will both read the lock as free and both spawn — the second spawn's `_write_lock()` simply
overwrites the first's entry, so the lock file can show exactly one legitimate-looking holder even
when two children are alive. This is exactly the class the tick's own docstring says it prevents
("no stacking") and exactly the kind of duplication the director's 2026-08-24 console message is
asking the machine to stop doing (Monday's "spinning our wheels" belief-test) — a second full
context stream re-reading the whole repo/CLAUDE.md for work the first stream is already doing is a
direct token-budget cost with zero marginal value, on TOP of the tree-corruption risk of two
uncoordinated agentic sessions editing the same shared tree.

## What I did NOT do, and why

I did not touch any file in pid 1817652's active commit pathspec (`docs/design/maturity_map.yaml`,
`background/worker-tick.timer`, `background/schedule_manifest.yaml`, the retired-atom-store files,
`site/data/simplified.json`) — that process was mid-`git commit` when I checked, and reading it
under the "concurrent lane can revert your uncommitted work mid-tick" pattern is exactly the
scenario memory already warns about. I also did not spawn a duplicate simulation run or re-action
the same staging items pid 1817652 was already visibly acting on (the retired-atom-store commit
matches the director's console mandate to delete atoms that shouldn't exist and collapse dead
lanes — that instruction is already being discharged by the live process, so re-running it here
would be pure duplication). Per SELF_INTERRUPT_DISCIPLINE this is a QUEUE finding, not a fix-on-sight:
it does not itself block the machine (the lock file DID name a real, alive, correctly-working
holder), so a code fix belongs in the normal draw, not an emergency edit racing a live commit.

## Proposed falsifier for the next atom that works this

Make `invocation_in_flight()` + `_write_lock()` one atomic critical section (e.g. `os.open(LOCK_FILE,
O_CREAT | O_EXCL)` claimed BEFORE the draw, released/overwritten only by the same pid, with a stale
lock still reclaimed on a dead pid as today) and add a test that starts two `run_tick()` calls with
an artificially slow `_draw()` and asserts only one spawns.
