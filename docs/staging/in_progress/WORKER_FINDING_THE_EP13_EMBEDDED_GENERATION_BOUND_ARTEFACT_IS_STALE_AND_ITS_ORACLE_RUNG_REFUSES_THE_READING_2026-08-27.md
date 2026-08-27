**Severity:** LATENT · **Lane:** W4_the_wall · **Rank:** top of EP13, before any L3 claim

# The EP13 embedded-generation bound's artefact is stale, and its own oracle rung refuses the reading

## THIRD DEATH, 2026-08-27 14:18 UTC — it was neither branch this file predicted, and item 2 is now READ

The `setsid` relaunch (pid 1027522) was **also** gone by 14:02 UTC with a 0-byte log and the
artefact still dated 06:30 (`ps -p 1027522` empty, `ls -la` on both paths — `observed-with-evidence`).
That is the third death, so this file's own instruction was followed rather than re-decided:
check `dmesg` for OOM, and **run the module in the foreground for one year before re-queueing it.**
Both were done. Both named branches are refuted, and the foreground run answered item 2 on the way.

**NOT OOM.** `dmesg | grep -i oom-kill` returns kills only inside `ops2-peak-kill-selftest-*`
cgroup scopes — a deliberate selftest — never a scope holding an EP13 pid. And the real work's
**peak RSS is 1,217.8 MB, flat for the whole year**, against `resource_headroom.sample()`
reporting `available_mb` 13,677. This job cannot OOM this box; the sim-runner's kill history is
not its history.

**NOT "the module raising before its first write".** In the foreground it runs clean end to end.

**THE COST PREMISE WAS WRONG, AND IT IS WHY THE JOB WAS EVER DETACHED.** Measured, not estimated:

```
cache load (demand, AGWS, fuel_mix, NESO published, embedded, build_shape, coords)   10.1 s
measure_year("2019"), all five null seeds, 144-cell grid                            159.0 s
```

Six scoreable years is therefore **~16 minutes**, not multi-hour. The multi-hour part is
`sweep()` — 5 grids × 6 years, and the 24x5x5 rung is 600 cells — which is **item 3**, not item 2.
**Item 2's reading never needed a detached job at all.** "Multi-hour" was inferred from the shape
of the work (six years × five rungs × five seeds, plus a five-grid sweep) and was never timed;
that unmeasured premise is what put a 16-minute job into a launcher that keeps killing it, and
then made two deaths unreadable because an empty log is what a detached job legitimately looks like.

**A FOURTH DATA POINT ON THE LAUNCH SHAPE.** Running the six-year loop in the *foreground of a
bounded tool call* died at **exit 143 (SIGTERM)** on the 10-minute tool timeout. So: `nohup &`
inside a tick dies with the tick's session; a bare foreground run dies at the tick's own timeout;
`setsid` survives both and died anyway for a reason still unidentified. The one repair that is
certain is the **log**, and it is made: the relaunch runs under a wrapper that writes `START …
pid/pgid/sess` on entry and `END … rc=<code>` on exit, so the next reader can tell RUNNING from
DEAD without `ps` archaeology and without treating an empty file as normal.

```
setsid /tmp/ep13_regen_wrap.sh   ->  python3 -u -m tools.ep13_embedded_generation_bound
  pid 1063255 (wrapper) / 1063263 (module), launched 14:18 UTC
  PPID 382, PGID == SESS == PID 1063255 — verified after launch, not assumed
  log: docs/observability/ep13_regen_20260827.log
```

### ITEM 2 IS ANSWERED FOR 2019, AND THE OCCUPANCY HYPOTHESIS IS REFUTED

The foreground year is the same code, the same seeds and the same grid the artefact will carry,
so it is the item-2 reading a run early (`/tmp/ep13_fg_year.json`, `observed-with-evidence`):

```
2019  n=8,283 scored half hours          held-out correlation
  ceiling_2d        +0.8692     48 cells   fallback 0.0013   min cell 55
  ceiling_3d        +0.8790    144 cells   fallback 0.0580   min cell 32
  placebo_shuffled  +0.8672    144 cells   fallback 0.0270   min cell 30
  placebo_day_mean  +0.8815    144 cells   fallback 0.0717   min cell 30
  oracle_probe      +0.8677    144 cells   fallback 0.0346   min cell 32

  embedded_gain_within_day  -0.0025      oracle_headroom_within_day  -0.0139
  embedded_gain_over_cells  +0.0118
  controls: fit_bites=Y  cells_are_populations=Y  null_collapses=Y
            placebos_are_cell_matched=Y  instrument_can_see_within_day=N
```

**`cells_are_populations` now PASSES and `instrument_can_see_within_day` is still False.** At 192
cells 2019 failed occupancy (fallback share 0.085–0.126 against the 0.10 threshold); at 144 it
passes with 0.058 and a minimum used cell of 32 against `MIN_FIT_OCCUPANCY = 30`. The grid
reduction did exactly what it was designed to do — and the oracle headroom did not follow it up:
**−0.0139 at 144 cells against −0.0104 at 192.** So the reading this file was parked to obtain is
that *the occupancy problem was real, is fixed, and was not what was blinding the instrument.*
The synthetic-battery analogue (92% fallbacks → 1.1%, headroom +0.049 → +0.159) does **not**
transfer to the real series, which is precisely the risk that paragraph flagged for itself.

**The next diagnostic, stated as an observation and not yet a mechanism.** `oracle_probe` is
built from the TARGET's own within-day deviation, so it is the strongest within-day third
coordinate that can exist — and it scores below `placebo_day_mean`, the rung with that same
coordinate's within-day structure destroyed, **both held out (+0.8677 vs +0.8815) and in sample
(+0.8807 vs +0.8912)**. A probe carrying the answer cannot genuinely be beaten by the same probe
with the answer removed. That is a statement about the instrument's construction, it survives the
occupancy repair, and *it is not a resolution problem* — which means `sweep()` (item 3) is a
diagnostic of how the gain moves with cells, not a route to making the oracle rung pass.
`INFERRED`, and deliberately not repaired here: the drawn work was to read item 2, and it reads.

**What still unblocks this file:** the running job writing
`docs/observability/ep13_embedded_generation_bound.json` with `cells: 144` **and** the
`resolution_sweep` block, so items 2 and 3 can be read across all six years rather than 2019 alone.

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

~~**If the process is gone and the artefact still reads 192**, the run died with the session — just
relaunch the same command.~~ **SUPERSEDED 14:18 UTC by the third-death section at the top of this
file: two relaunches have been spent on that reading and neither death was the session.** If the
process is gone again, read `END … rc=` in the log first; if there is no `END` line the job was
killed from outside and the launcher is the subject, not the module. Do not spend a fourth
relaunch on the per-year table — it is a 16-minute foreground run and 2019 is already read above.

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
