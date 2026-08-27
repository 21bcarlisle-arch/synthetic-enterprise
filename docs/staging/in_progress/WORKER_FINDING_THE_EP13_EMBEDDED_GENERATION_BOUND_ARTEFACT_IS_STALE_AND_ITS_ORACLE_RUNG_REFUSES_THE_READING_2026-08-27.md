**Severity:** LATENT · **Lane:** W4_the_wall · **Rank:** top of EP13, before any L3 claim

# The EP13 embedded-generation bound's artefact is stale, and its own oracle rung refuses the reading

## PARKED IN-PROGRESS 2026-08-27 11:26 UTC — the one owed item is RUNNING, not waiting

**Blocking sub-item: item 1 below (regenerate the artefact at the current `(12,4,3)` grid).**
It was drawn by the scheduled tick that self-refilled `EP13_adapter_carbon_intensity`
(level 2→3, `loop_stage: build`) and is **in flight now**, not queued:

```
setsid nohup python3 -m tools.ep13_embedded_generation_bound
  pid 1027522, relaunched 13:33 UTC, log: docs/observability/ep13_regen_20260827.log
```

It loads only on-disk caches (`load_cached()`), so it needs no network and cannot block on one.
The module prints nothing until it finishes — an empty log is normal, not a stall.

### FIRST LAUNCH DIED — relaunched 2026-08-27 13:33 UTC, and the fix is `setsid`, not a retry

The 11:26 launch (pid 807748) was gone by 13:33 with a **0-byte log** and the artefact still
dated 06:30 at `grid: {u: 16, v: 4, w: 3}` — all three `observed-with-evidence` (`ps -p 807748`
empty, `ls -la` on both paths, `grid` read out of the JSON). That is precisely the "process is
gone and the artefact still reads 192" branch this file wrote for itself two hours earlier, so
the instruction was followed rather than re-decided.

**Why it died, and why a plain relaunch would have died the same way.** The original command was
`nohup … &` from inside a worker-tick shell. `nohup` only detaches from SIGHUP-on-terminal-close;
it leaves the child in the *session and process group of the tick that spawned it*, so when that
session was torn down the job went with it. A multi-hour compute job launched from a **bounded**
invocation therefore cannot outlive its own launcher — the very thing it needs to do. The
relaunch uses `setsid`, which puts the job in a new session with no controlling terminal:

```
PID 1027522  PPID 382  PGID 1027522  SESS 1027522
```

`PGID == SESS == PID` and `PPID` reparented away from the tick shell is the check that it is
genuinely detached — verified after launch, not assumed. **If this file is read again and the
artefact is still stale, do NOT simply relaunch a third time: the `setsid` form has already been
tried, so a third death is a different defect** (OOM against the sim-runner's history of kills,
or the module raising before its first write) and the empty log stops being normal. Check
`dmesg -T | grep -i oom` and run the module in the foreground for one year before re-queueing it.

*Generalises past this file: this is R18's other half. R18 made waiters name their subject and
carry a deadline; this is the same failure from the launcher's side — a job whose lifetime is
shorter than the work it was launched to do looks exactly like a job still running.*

**What unblocks this file:** `docs/observability/ep13_embedded_generation_bound.json` showing
`cells: 144` instead of `192`. Until then item 1 is neither owed nor re-drawable.

**If the process is gone and the artefact still reads 192**, the run died with the session — just
relaunch the same command. Nothing is lost and nothing needs re-deciding; per the body below,
the repair was already diagnosed and made, and only the re-measurement was left undone.

**Then read the rungs in the stated order — `instrument_can_see_within_day` FIRST (items 2 and 3),
and the refusal in "What must not happen" stands until item 1 is read.** `EP13` was verified still
at `level_current: 2` during this tick, so no premature L3 claim exists.

*Note for whoever edits this atom's map entry: it sits at 11,940 B against the 12,288 B per-atom
cap (348 B of headroom, the fattest in the map), so a note written there will refuse the commit
tree-wide. Rehome the narrative instead.*

**Filed by the worker seat, 2026-08-27, while landing the uncommitted mid-work of the session
that built this instrument. QUEUED, not fixed on sight (SELF-INTERRUPT DISCIPLINE): regenerating
the artefact is a multi-hour compute job, the drawn tick's work was landing the code, and nothing
downstream reads the artefact yet.**

## Why this matters before anything else on EP13

`EP13_adapter_carbon_intensity` sits at `level_current: 2`, `level_target: 3`, `loop_stage:
build`. The instrument `tools/ep13_embedded_generation_bound.py` exists precisely to decide
whether the L3 build — wiring `sim/neso_embedded_generation.py` into the dispatch model — is
worth doing at all. **That decision cannot currently be read off the artefact on disk.** Any L3
move that cites `docs/observability/ep13_embedded_generation_bound.json` today would be citing a
measurement its own controls decline to interpret.

## Observed, with evidence

`docs/observability/ep13_embedded_generation_bound.json` (untracked, produced by an earlier
revision of the module):

```
year        2d       3d     shuf  daymean   ORACLE   gain_wd  headroom   cells
2019   +0.8718  +0.8817  +0.8702  +0.8831  +0.8727   -0.0014   -0.0104     192
2020   +0.8714  +0.8787  +0.8701  +0.8775  +0.8720   +0.0011   -0.0055     192
2021   +0.9078  +0.9190  +0.9052  +0.9133  +0.9074   +0.0057   -0.0058     192
2022   +0.8916  +0.9063  +0.8902  +0.8928  +0.8922   +0.0135   -0.0006     192
2023   +0.8072  +0.8301  +0.8014  +0.8331  +0.8109   -0.0030   -0.0223     192
2024   +0.7298  +0.7522  +0.7274  +0.8108  +0.7571   -0.0587   -0.0538     192
```

Two facts, both `observed-with-evidence`:

**1. `instrument_can_see_within_day` is False in all six years.** `oracle_headroom_within_day` is
NEGATIVE in five of six — the oracle probe, built from the target's own within-day deviation and
therefore the strongest within-day third coordinate that can exist, scores *below* the day-mean
placebo it is measured against. The module's own docstring states the consequence: *"If it shows
nothing there either, the null is about the instrument and says nothing about the hypothesis."*
So the `gain_wd` column above is not evidence that embedded generation carries no timing. It is
not evidence of anything.

**2. The artefact is stale relative to the module it came from.** It reports `cells: 192`
throughout. The module's live constants are `U_BINS, V_BINS, W_BINS = 12, 4, 3` = **144**. 192 is
`(16, 4, 3)` — the second rung of `SWEEP_GRIDS`. The grid was reduced after this run and the
artefact was never regenerated.

## Why the artefact is stale — observed, not inferred

The grid reduction was a *deliberate, measured* response to exactly the occupancy problem this
artefact shows, and the module says so in its own words at `U_BINS, V_BINS, W_BINS`:

> 16x4x3 = 192 cells was tried first and MEASURED to fail the occupancy control — 10-15% of
> scored half hours fell back to the u-marginal in four years of six, and a fallback is precisely
> where the third coordinate stops being read, so the rung that most needed the resolution was
> the one losing the signal. 12x4x3 = 144 against roughly 8,700 fit-side half hours is ~60 per
> cell.

The artefact above IS that failing run: `cells_are_populations` False in four of six years, with
`occupancy_fallback_share` between 0.085 and 0.126 against a 0.10 threshold. So the repair was
diagnosed and made, and only the re-measurement was left undone. **Nothing here needs
re-deciding — it needs re-running.**

## The corroborating evidence, from the other side

**The identical failure was reproduced and cured on the synthetic battery in this tick.**
`tests/tools/test_ep13_embedded_generation_bound.py`
was running a fixture whose date arithmetic collided (120 requested days → 112 distinct), leaving
18.7 fit-side half hours per cell against `MIN_FIT_OCCUPANCY = 30`. The result was **92% fallbacks**,
`instrument_can_see_within_day` False, and a positive control that failed — the same signature as
the table above. With real date arithmetic and a 366-day year (62 per cell, 1.1% fallbacks) the
oracle headroom went from +0.049 to **+0.159** and every control passed, with the signal and noise
worlds separating +0.189 vs +0.0004. Nothing about the instrument's logic changed.

That is a strong analogue (R4), not a proof about the real series. The real series may also be
genuinely harder than the synthetic one.

## What is owed

1. Regenerate `docs/observability/ep13_embedded_generation_bound.json` with the current `(12,4,3)`
   grid — `python3 -m tools.ep13_embedded_generation_bound`. Multi-hour: six years × five rungs ×
   five null seeds, plus the five-grid `resolution_sweep`.
2. Read `instrument_can_see_within_day` FIRST. If it is still False at 144 cells, the sweep is the
   next diagnostic, and the honest verdict is "this atom's question is not answerable at any
   resolution these caches support" — which refuses the L3 build for a *stated* reason.
3. Only then read `embedded_gain_within_day`, and only in the years where the oracle rung passes.

## What must not happen

No `level_current: 3` on `EP13_adapter_carbon_intensity` citing this artefact, and no wiring of
`sim/neso_embedded_generation.py` into the dispatch model on the strength of the `gain_wd` column,
until (1) is done. The adapter is committed and dormant on the orphan-ratchet record precisely so
that this decision stays open rather than being made by default.
