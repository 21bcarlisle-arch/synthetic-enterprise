**Severity:** LATENT · **Lane:** H_harness

# The producer is not dead and its runs are not failing — the kernel OOM killer has killed it twelve times today

**Found by:** worker tick 2026-08-24 13:25–13:50 BST, drawn on the RUNG-1d "PRODUCER SILENT
self-refill (PRIORITY ZERO)" doorbell.
**Not repaired here.** The repair is a memory decision (host allocation or the run's own
footprint), not a code edit a tick can land, and one of the two candidate repairs is the
director's. What this pass did is replace the doorbell's diagnosis with the real one, because
the doorbell's prescribed repair — restart it — is what has already happened twelve times.

## What the doorbell claimed, and what is actually true

The doorbell asserted three things. The first is true; the second and third are false, and the
third is the one that matters:

| doorbell claim | verdict | evidence |
|---|---|---|
| no run output written for 3.1h | **TRUE** | newest is `run_output_26afdac4f_20260824T090747Z.json`, 09:07 UTC |
| the producer's own state says `failed` | **TRUE** | `.sim_producer_state.json` → `"last_result": "failed"` |
| "this is not a run failing, it is runs NOT happening" | **FALSE** | runs are happening continuously; each is killed before it can finish |

The producer process was alive throughout, and a healthy run was in flight while the doorbell
was being drawn.

## Observed, with evidence (R9)

**The kill is an OOM kill, and it is not new.** `journalctl --user -u sim-runner.service`:

```
Aug 24 13:07:14 sim-runner.service: The kernel OOM killer killed some processes in this unit.
Aug 24 13:07:14 sim-runner.service: Failed with result 'oom-kill'.
Aug 24 13:07:14 sim-runner.service: Consumed 30min 54.833s CPU time over 31min 32.309s wall
                                    clock time, 10.7G memory peak.
Aug 24 13:07:19 sim-runner.service: Scheduled restart job, restart counter is at 12.
```

Twelve OOM kills on 2026-08-24, peaks 3.6G–11.8G. Twenty-two since 2026-08-19, clustered
Aug 20 (8), Aug 21 (2), Aug 24 (12) — Aug 22 and Aug 23 were clean, and both days published
normally. This is chronic and intermittent, and today it crossed into total starvation.

**The box is 15 GB, not the 32 GB `CLAUDE.md` records.** `free -g` → `total 15`. The 32 GB in
the technical-environment section is the Windows *host*; the WSL2 VM the company actually runs
in gets roughly half by default. Every memory judgement made against the 32 GB figure has been
made against a number that was never available to this process.

**The arithmetic is simply short.** With the resident daemons taking ~2 GB (`supervisor.py`
0.8 G, two `claude` sessions 0.6 G, `naive_organ` + `background_worker` 0.2 G), a run that peaks
at 9–12 GB does not fit in 15 GB. `MemoryMax` and `MemoryHigh` on the unit are both `infinity`,
so nothing throttles the run before the kernel kills it outright.

**The footprint grew before the kills started.** Runs completing before 07:00 UTC took ~290 s and
wrote 4117 KB; from 07:11 they took ~630–690 s and wrote 6543 KB. The sustained OOM run begins
at 09:18, immediately after that step change. The book is growing, and the run holds the whole
settlement series in memory — 5.2 M settlement periods in the run observed here.

**Why the state file says `failed` rather than `killed`.** An OOM kill takes the child down
without a Python-level exception, so the producer records only the last run that failed *with a
return code*. That was a genuinely different and now-resolved fault (below). The state file is
therefore reporting a 7-second-old code error as the standing condition while the actual
condition — a 30-minute run being killed at 10.7 G — leaves no trace in it at all. **No control
watches the OOM door**; the RUNG-1d rung infers producer health from artefact age plus this state
file, and both inputs are consistent with "dead producer", which is why it prescribed a restart.

## The 12:07 `ValueError` was a separate, transient, already-resolved fault

Worth recording so it is not conflated with the above, and so nobody re-repairs it:

```
ValueError: drawn household 'PSTK-2021-0401' handed to customer 'SYN-2021-001' — one home, one id
```

This was a **half-landed working tree**, not a defect in any commit. The uncommitted PB2 work
splits the premise id (`PSTK-*`) from the customer id (`SYN-*`); `make_household`'s "one home,
one id" guard then fires unless `live_drawn_households` relabels the household to its customer
id. At 12:07 the split was in the tree and the relabel was not. By 12:12 the relabel had been
written and the next run cleared the guard in flight.

Both endpoints are self-consistent — HEAD has neither the split nor the relabel (`STOCK_ID_PREFIX`
does not exist at HEAD; `live_drawn_households` there is a bare `{cid: premise.household}`), and
the current tree has both. Only the five-minute window between them was broken. **The producer
runs the working tree, so any lane's partially-written multi-file edit is a production outage for
as long as it takes to finish typing.** That is the durable point, and it is a member of the
uncommitted-work class rather than of anything in `simulation/`.

## What it cost

The live site has been stale since 09:07 UTC. Nothing published is *wrong* — every figure still
carries the clock it was computed at (R14) — so no control's verdict is invalidated and this is
LATENT rather than BLOCKING. What is lost is four hours of freshness, and the fact that the
freshness alarm that exists pointed at the wrong door.

## Recommended, in priority order

1. **Raise the WSL2 memory allocation** — `memory=24GB` in `%UserProfile%\.wslconfig` on the
   Windows host, then `wsl --shutdown`. This is the one repair that addresses the cause rather
   than the symptom, and the headroom it buys is what the 32 GB figure in `CLAUDE.md` has been
   implicitly promising all along. **It is the director's**: it is a host-config change outside
   the repo, and the restart takes every session on this machine down with it, including the
   worker seat. Recommended, not taken.
2. **Correct the 32 GB figure in `CLAUDE.md`** to name both numbers (32 GB host / 15 GB WSL2
   guest), so the next memory judgement is made against the number that binds.
3. **Give the OOM door a control.** The producer's health is currently inferred from artefact age
   and a state file that an OOM kill cannot write to. A rung that reads `journalctl`'s
   `oom-kill` result for the unit would have named this in one line, and would not have
   prescribed a restart. R15: it must be mutation-tested against a synthetic OOM record.
4. **Set `MemoryHigh` on the unit** below `MemoryMax` so the run is throttled and reclaimed
   before it is killed. This converts a lost 30-minute run into a slow one. Cheapest of the four,
   and the least valuable — it treats the symptom, and against a 9–12 GB peak in a 15 GB box it
   will mostly buy swap thrash. Listed for completeness, not recommended on its own.

## Status at the end of this tick

The run started 12:12 UTC survived past the 7 s guard failure and past the point earlier runs
were killed, reaching sim-year 2023-08 at 8.9 G resident with ~3 G available. Whether it
completes is a coin toss on the same memory arithmetic; it was still progressing when this was
written. **No restart was issued** — a thirteenth restart is not a repair, and the twelve
preceding it are the evidence.
