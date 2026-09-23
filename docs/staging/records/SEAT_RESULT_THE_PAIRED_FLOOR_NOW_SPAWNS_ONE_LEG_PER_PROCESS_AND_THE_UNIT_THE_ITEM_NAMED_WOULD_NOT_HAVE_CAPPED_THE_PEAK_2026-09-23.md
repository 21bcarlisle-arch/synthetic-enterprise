**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** unminted — Lane 0 delivery

# The paired floor now spawns one leg per process — and the unit the item named would not have capped the peak

*Lane 0 delivery, 2026-09-23. Drawn item:
`the-paired-size-term-floor-needs-one-pair-per-process-before-any-seed-budget`.
Instrument and pre-registration: `7cb432d36`. Headroom guard fix: `f60c4c26c`.*

---

## The premise, re-measured before starting

Both cited commits are ancestors of `origin/main` — and that is what the item SAYS about them, not a
sign the work is spent. `7cb432d36` landed the instrument and its pre-registration; `f60c4c26c`
fixed the census that could not see it. The work the item asks for — the process split, and the run
— is in neither. **Premise live.** The named path
(`docs/staging/records/SEAT_PREREG_THE_PAIRED_SIZE_TERM_FLOOR_2026-09-23.md`) is correctly graded
`already landed`: it is read here, not rewritten.

The duplicate-work check named one other live claim, under *this very id*. There is no rival:
`.seat_work_in_hand.json` does not exist on the shared tree at all, and the only `ps` match for a
concurrent lane is this invocation's own prompt text. No disposition taken; the work was done.

## One clause of the item's motive is no longer true, and it is recorded here rather than worked around

> *"f60c4c26c fixed the guard that admitted it … so the guard now REFUSES this run correctly."*

**It does not refuse, right now.** Measured at 14:55Z, before any code was written:

```
available_mb 21,022   total_mb 24,032   running floor legs: []
floor_run_headroom_refusal(own_peak_mb=7800.0) -> None
```

The guard refused when the item was written because other legs were running. On an idle guest
21 GB comfortably holds 7.8 GB and the guard correctly admits it. So the refusal was never the
reason to split — it is a symptom that comes and goes with what else is running, and treating it as
the motive would have made the split look unnecessary the moment the guest went quiet. The real
reasons are unconditional and unchanged: **a 13.5-hour unit that writes nothing until it finishes
loses everything to one kill** (this guest has recorded 154 OOM kills), and a 7,878 MB peak is one
concurrent lane away from death whatever MemAvailable says at launch.

## The correction: the unit is the LEG, not the pair

The item asks for **one pair per process** and justifies it by saying that *"one pair per process
caps the peak at a single leg's"*. Those two clauses contradict each other, and the file's own
history says which one is right. `PAIRED_FLOOR_RUN_PEAK_MB`'s comment already records why a paired
leg costs 7,800 MB where a noise-floor leg costs 6,400:

> *a noise-floor leg runs ONE configuration per process, and a paired leg runs BOTH — blind and
> seeing — in one process … It therefore carries two worlds' retained state where the sibling
> carries one.*

A pair **is** the two configurations. One pair per process would have changed the seed count per
process and nothing about the thing that makes the peak large, capping it at exactly the 7,878 MB
that already died. **I took the goal clause over the mechanism clause and made the unit the leg.**

## What landed

`tools/size_term_paired_floor.py` — `--leg-only SEED|base --configuration blind|seeing` runs exactly
one leg in one process, writes a shard, exits. `--seeds` is now an orchestrator that spawns one
child per leg, waits, and holds no simulation state; it rebuilds the whole artefact from the pairs
it can assemble after every pair, which `run()` already did and `build_report` needed no change to
support. A leg already sharded is not re-run, so a killed family resumes instead of repeating.

`tools/run_value_cycle_ab.py` — `PAIRED_FLOOR_LEG_PEAK_MB`, and the census row for this module moved
from `--seeds` to `--leg-only`. **That move is load-bearing and is the half of this that is not
about this tool.** `--seeds` now holds tens of megabytes; leaving it in `FLOOR_LEG_SHAPES` would
price a family at its orchestrator's peak *plus* its child's — one leg charged to the guest twice,
refusing families this machine can hold, which makes the bound unmeasurable. That is the same
failure direction as the original defect, arrived at from the other side.

### The number I did not pick

A leg's peak is **not established**. Every measurement in hand comes from a process that ran both
configurations. The tempting value was the sibling's 6,400 MB, and it would have been a number
chosen because a number was wanted: the two legs run different arms over different retained books.
So `PAIRED_FLOOR_LEG_PEAK_MB` is set to the *pair's* measured 7,800 MB — knowingly an overestimate,
but the one bound the evidence does establish, since a leg is contained in the pair that ran it. It
refuses conservatively and is labelled in the source as a bound rather than a measurement. Every leg
now records its own `VmHWM` into its shard, and the artefact publishes `leg_peak_rss_mb` with
`admission_price_is_a_bound_not_a_measurement: true`, so the first completed family replaces the
bound with a measurement instead of inheriting it.

## The controls, and that each can fail

`tests/tools/test_the_paired_floor_leg_runs_alone_in_its_own_process.py` — six, every one
mutation-proven rather than asserted to be sound:

| mutation | caught by |
|---|---|
| orchestrator inlines the leg again | `..._runs_no_leg_in_its_own_process` |
| resume disabled, every leg re-run | `..._already_on_disk_is_not_run_again` |
| shards tidied away after loading | `..._dead_leg_costs_one_leg...` |
| shard key drops the configuration | `..._cannot_share_a_shard` |
| spawn flag renamed, census not told | `..._an_argv_the_headroom_census_counts` |
| census watches the orchestrator again | `..._sees_a_leg_and_does_not_see_its_orchestrator` |

The fifth is the one worth naming: it controls the **chain**, not the ends. A leg the census cannot
see neither counts itself nor is counted — the exact invisibility that admitted the run that died —
and asserting either end alone passes while the two disagree, which is how the first one got
through. The census leg is written as a partition over one population because two of its three
claims are absences, and a census that saw nothing would satisfy both.

## Pre-registration — the leg peak, written before any leg has been weighed

The prediction the item's own reasoning implies, filed before the run:

1. **A single leg's `VmHWM` will come in materially below 7,878 MB** — I predict **6,000–7,000 MB**,
   i.e. below the pair's peak by roughly the 1,478 MB the pair/noise-floor gap already attributes to
   carrying two configurations, but *above* the sibling's 6,400 MB because this leg runs a different
   arm. *Confidence: moderate.*
2. **If instead a leg comes in at or near 7,878 MB, the retention theory in
   `PAIRED_FLOOR_RUN_PEAK_MB`'s comment is wrong** — the pair's peak is then one leg's peak, the
   second configuration adds nothing resident, and the 1,478 MB gap to the noise-floor leg is the
   *arm*, not the pairing. **That is a finding, and it falsifies the sentence this split was
   reasoned from** even though the split still pays for itself on resumability alone.
3. Either way the bound is replaced by a measurement and `PAIRED_FLOOR_LEG_PEAK_MB` stops being a
   bound. **It is lowered only to what is observed, never to what would be convenient.**

## What is done, and what is not

**Done:** the split, its controls, the census correction, and the honest bound. The instrument can
now run the family in seven ~1h units that fit, where an OOM costs one leg and leaves the rest.

**Not done, and it is the larger half:** the family has not run, so the five predictions in
`SEAT_PREREG_THE_PAIRED_SIZE_TERM_FLOOR_2026-09-23.md` are still ungraded and the **£634 net-margin
move remains unfloored.** That is ~13.5 hours of wall clock and cannot fit in this turn. The run is
launched from here and handed on; the artefact accumulates after every pair, so whatever it reaches
is readable by the next session rather than lost.
