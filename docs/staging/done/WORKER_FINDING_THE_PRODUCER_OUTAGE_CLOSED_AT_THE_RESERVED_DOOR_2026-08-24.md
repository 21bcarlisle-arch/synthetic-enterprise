**Severity:** RECORDED · **Lane:** H_harness

# The producer outage closed at the reserved door: the director raised the guest to 24 GB and every process came back

**Found by:** worker tick 2026-08-24 15:16 BST, drawn on the RUNG-1d "PRODUCER SILENT
(PRIORITY ZERO)" doorbell — the fourth pass on this door today and the one that found it
already repaired by the only party who could repair it.

## Class registration

Closure record for `CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`'s producer limb. It closes,
with evidence, the three passes filed today:

- `done/WORKER_FINDING_THE_PRODUCER_IS_NOT_DEAD_IT_IS_OOM_KILLED_TWELVE_TIMES_TODAY_2026-08-24.md`
- `WORKER_FINDING_THE_PRODUCER_OOMS_BECAUSE_THE_BOOK_GREW_AND_SETTLEMENT_SCALES_WITH_IT_2026-08-24.md`
- `WORKER_FINDING_THE_PRODUCER_RUNS_THE_WORKING_TREE_SO_A_HALF_TYPED_EDIT_IS_AN_OUTAGE_2026-08-24.md`

## Observed, with evidence (R9)

**The reserved repair was taken.** The second pass named three candidate repairs and ruled two
of them reserved to the director. Repair 2 — give the guest more memory — was prepared to the
boundary a tick may reach (the third pass wrote `/mnt/c/Users/*/.wslconfig` and NTFY'd, leaving
it inert) and the director executed it:

| observation | value | source |
|---|---|---|
| `.wslconfig` | `[wsl2] memory=24GB / swap=8GB` | the file on the host, read this tick |
| guest MemTotal | **24,608,836 kB (23.5 GB)**, was 15 GB | `/proc/meminfo` |
| guest swap | 8 GB, was none | `free -m` |
| uptime at draw | **1 min** | `uptime`, 15:16:38 BST |
| unit restarted | 15:15:15 | `journalctl --user -u sim-runner.service` |

`wsl --shutdown` therefore ran at ≈15:14:33 — the journal's last line before the boot is
`Stopped sim-runner.service … Consumed 33min 19.524s … 11.5G memory peak`, i.e. the fifteenth
run was killed by the shutdown rather than by the kernel, which is the intended outcome.

**Every declared process came back.** `systemctl --user list-units` reports **13 units active,
0 failed** — supervisor, deadmans-switch, worker-seat-manager, sim-runner, publisher-side
background-worker, naive-organ, sanity-daemon, dispatcher, ntfy-responder, staging-watcher,
file-api, token-proxy, worker-tick. This is the OPS1 IaC claim under its first real test: the
box was destroyed and reconstructed from the repo alone, with no hand-restart of anything.

**The arithmetic now closes.** Runs peaked at 13.5 GB (14:41 kill, the highest of the fourteen).
Against 23.5 GB with ~2 GB of resident daemons the headroom is ~8 GB, where before it was
negative. A run started at 15:15:15 and was resident at 800 MB / 1 min 41 s when this was
written.

## What is NOT claimed

**Not "fixed" — the doorbell's own bar is a landed run output, and no run has completed since
09:07 UTC.** A run takes ~40–47 min, so the first confirmation falls at ≈15:55–16:00, after this
bounded tick ends. The falsifier is exact and cheap for the next tick to read: a new
`docs/reports/run_output_*.json` newer than `run_output_26afdac4f_20260824T090747Z.json`. If a
fifteenth OOM kill appears in `journalctl --user -u sim-runner.service` instead, the book has
outgrown 24 GB as well and repair 3 — reduce the run's footprint in code, the one candidate that
was never reserved — becomes the only remaining move.

**Repair 3 is still owed and is still the right engineering.** Raising the ceiling bought
headroom against a book that is growing on purpose: the director asked for residential growth
toward 200 accounts, and today's 6× step from 13 to 81 is what exhausted 15 GB. Settlement
memory scales with book × years against a fixed 10-year horizon, so 200 accounts will ask for
more than 24 GB on the same trajectory. `tools/settlement_footprint_probe.py` (landed this tick)
is the short-horizon closed-loop harness that pass 2 said had to exist first, because validating
the fix by running the 40-minute job is not a loop anyone can turn.

## What this tick landed

1. **The OOM door**, which had been diagnosing this outage from the working tree alone, unlanded,
   across a WSL restart that could have taken it: `background/oom_watch.py`,
   `tools/settlement_footprint_probe.py`, their three test files, and the
   `_producer_starved_active` wiring. 51 tests.
2. **CLAUDE.md's memory figure, rewritten so it cannot go stale again.** It said 32 GB (host,
   never available), then ~15 GB (correct for six hours), and is now wrong a third time. The line
   no longer states a number as doctrine: it says the binding figure is the guest's, that it
   MOVES, and points at `background.resource_headroom.sample()["total_mb"]` to read it.

## The durable lesson

A fact that three separate documents quoted as a constant changed twice in one day. Both wrong
readings were load-bearing — the 32 GB figure is why nobody sized the run against the box, and
the 15 GB figure was baked as a string literal into the supervisor's own wedge doorbell, where
it would have instructed every future tick from a number that stopped being true at 15:14. **A
machine quantity belongs in a reader, not in prose and not in a literal** — the same doctrine
`oom_watch` applies to the kill record, applied to the memory ceiling.
