# AO12 — The 10k Scale Probe

**Atom:** `AO12_scale_probe_10k` (lane H_harness, epoch 3, dial 3)
**Source:** `docs/design/refs/ADVISOR_REVIEW_DATA_ARCHITECTURE_AND_SCALE_PROBE_2026-08-05.md` §3
**Mechanism:** `tools/scale_probe_10k.py` · **Controls:** `tests/tools/test_scale_probe_10k.py`
**Artefacts:** `docs/observability/scale_probe_10k/report.json` + `prediction_register.json`
**First full run:** 2026-08-12, git `ed2e9b764`

---

## 0. Purpose, guarantee, and why — before anything else

**Purpose.** Replace the scale ARITHMETIC with a MEASUREMENT. The director asked on 2026-08-05
whether this business scales to 10k / 100k / 1m customers. The advisor answered by
extrapolation and said so plainly in its own §5: *"Runtime memory behaviour is entirely
unmeasured — every RAM claim above is arithmetic, not observation."* This probe observes.

**Guarantee.** It finds the first seam that tears and puts a number on it, and it does that
even when the run dies — because the run dying IS the measurement. Every stage is checkpointed
to disk with an explicit flush+fsync, so a stage killed at its ceiling still reports how many
units it completed, how much it was holding, and how long it took.

**Why a probe and not a fix.** R4: diagnose before fixing. The atom's scope explicitly excludes
any fix, any database or substrate adoption, and any schema work. A storage swap is an
architecture door, not a build; these findings return to the director before any substrate
decision is taken. Nothing in this document proposes one.

**Cheap enough to repeat** is a design requirement, not a nicety — the whole probe runs in
about 20 seconds. A measurement that costs an afternoon gets run once and quoted for a year.

---

## 1. What was measured, and against what prediction

Five stages, four of them the advisor's ranked predictions plus one control:

| Stage | Advisor rank | Subject |
|---|---|---|
| `population_draw` | *(not predicted — control)* | REAL `simulation.population_draw` |
| `settlement_build` | **#1** in-run RAM at settlement build | REAL `simulation.settlement.run_settlement`, real PC1 shape, real cached Elexon SSP |
| `run_output_serialization` | **#2** run-output serialization | REAL records, real `json.dumps` |
| `site_publish` | **#3** per-customer site publish | **REPLICA** — replays the 22 real `site/data/customers/*.json` byte-shapes |
| `git_transport` | **#4** git transport of outputs | **REPLICA** subject, REAL git |

The **prediction register** is written before any stage runs, and `grade_prediction` refuses to
grade a register stamped after the first stage started. A prediction written after the fact is
not a prediction; a grader that would accept one is a control that cannot fail (R15).

**Target:** 10,000 customers × 1 year (2021), per the atom's bound of one year before any decade
attempt. **Ceiling:** `RLIMIT_AS` 3072 MB per child — bounding *virtual address space*, which is
not RSS and is never called RSS in the report. **Scratch:** `~/.cache/synthetic-enterprise/`,
real disk (ext), outside the repo and deliberately not `/tmp`, which is a tmpfs on this box.

---

## 2. Findings — 2026-08-12

### 2.1 The first seam tears at settlement build, and it is not close

`settlement_build` **died at the 3 GB address-space ceiling after 8,145,405 records — 4.6% of
the target**, having settled 465 of 10,000 customers. Measured incremental cost: **367 bytes
per settlement record**, 17,520 records per customer-year.

> **10,000 customers × 1 year needs ≈ 63.9 GB of resident memory. This box has ~8.6–13.8 GB
> available depending on what else is running. The requirement is 5–7× the budget.**

The crossover, computed from the same constants: **settlement build exhausts this box at
roughly 1,500–2,100 customers** for a single year — the range, not a point, because the
denominator is `MemAvailable` and this box is shared with live daemons and the publisher. The
stable figure is the 367 bytes per record; the customer count is that figure divided by
whatever is free at the time.

Two consequences worth stating separately from the number:
- The tear is at **one year**. The decade the real run replays is 10× this.
- It is a *working-set* tear, not an output-size tear. The list is what kills it, before
  anything is written anywhere.

### 2.2 Serialization is the same order of magnitude, and the advisor's #1/#2 ordering is UNDECIDED

`run_output_serialization` measured **411 bytes/record of RSS on top of holding the records**,
and **248 bytes/record on disk**. Projected at 10k × 1 year: **72.5 GB RSS and 43.5 GB of
JSON**.

The predicted ordering `settlement_build > run_output_serialization` is **UNDECIDED**, and that
is the correct answer rather than a shortfall: settlement build *died*, so its cost is known
only as a floor (≥ 63.9 GB), and that floor sits below serialization's measured 72.5 GB. The
probe cannot say which is larger without a box that can hold the first one. What it can say is
that **both exceed the available memory by 5–8×**, which is the finding that matters.

**Do not read the 43.5 GB against the advisor's ~2 GB-per-decade estimate — they are different
artefacts.** That estimate is for `run_output_latest.json`, which is a REDUCED projection
(`extract_report_data`). This stage serialises the RAW working set, so it prices the persist
path's *input*. The reduction's own cost is unmeasured and is recorded as such in the report.

### 2.3 The publish and transport stages are three orders of magnitude cheaper — with a caveat that dominates them

`site_publish` wrote 10,000 documents (1.85 GB) in **1.3 s**. `git_transport` added, committed
and packed them in **3.5 s**. Against a 600 s stage budget these are 0.2% and 0.6%.

**Both are lower bounds, and the transport figure especially.** The replica replays 22 distinct
documents 10,000 times, so git's delta compression saw a redundancy a real book would not have:
**1.85 GB published packed to 1.42 MB — 1,306×**. Read as a measured figure it would have
*refuted* the advisor's publish-over-transport ordering on a number biased low by three orders
of magnitude. The report declares the redundancy, and the declaration is what degrades the
stage to a floor.

For orientation, computed rather than judged: **site_publish would have to be ~3,300× its
measured cost** to displace serialization in the ranking. That is the size of the gap the
unmeasured content-computation would have to close.

### 2.4 The affordability verdict — what the dependent atom consumes

| Stage | Pressure (× budget) | Kind | Verdict |
|---|---|---|---|
| `population_draw` | 0.004 | measured | **FITS** |
| `settlement_build` | ≥ 7.4 | lower bound | **DOES_NOT_FIT** |
| `run_output_serialization` | ≥ 8.4 | lower bound | **DOES_NOT_FIT** |
| `site_publish` | ≥ 0.002 | lower bound | UNDECIDED |
| `git_transport` | ≥ 0.006 | lower bound | UNDECIDED |

`SCALE_10K_PROPOSED_TARGET` reads these from `report.json` and is forbidden from re-deriving
them. The two UNDECIDED rows are UNDECIDED because they carry declared omissions, and a stage
with an omitted component can never come back FITS — the omitted work can only add.

### 2.5 A defect in the generator, found in passing

`simulation.population_draw._poisson` is Knuth's algorithm, whose target `math.exp(-lam)`
underflows to exactly 0.0 above λ ≈ 745. Above that point the loop exits only when the running
product of uniforms denormalises to zero, after ~700 multiplications **regardless of λ** — so
**`acquisitions_per_year_lambda=10000` returns ~733 customers, silently**. Measured: λ=750 →
703, λ=10000 → 733.

The probe does **not** fix it: `population_draw.py` is world-side code outside this atom's
file_scope and its draw is a director-owned curriculum instrument (R13). It works around the
saturation by calling the shipped generator repeatedly at λ=250 with per-batch seeds and id
prefixes, and it **refuses to measure a book it did not get** — a short book with the requested
N in the denominator would understate every per-customer cost, in the reassuring direction. The
behaviour is pinned by `test_the_generator_saturates_above_745`, which fails when the generator
is fixed, so the workaround is revisited rather than left behind as cargo. Filed:
`docs/staging/WORKER_FINDING_THE_POPULATION_DRAW_SATURATES_ABOVE_LAMBDA_745_2026-08-12.md`.

---

## 3. How the probe stays honest (R15)

**Three-valued pressure.** Every stage's requirement is an interval, not a number: MEASURED
`[v,v]`, LOWER_BOUND `[v,∞)`, UNKNOWN `[0,∞)`. Comparisons decide only when the intervals do
not overlap. The fail-open shape this exists to prevent is the one where a stage that never ran
is priced at 0.0 and sorts harmlessly to the bottom — which is how "we never saw it tear"
becomes "it doesn't tear". `test_mutation_pricing_an_unmeasured_stage_at_zero_changes_the_verdict`
proves the algebra is load-bearing by showing the mutation flips the comparison.

**A death is a floor, not an unknown.** A stage killed at its ceiling demonstrably needed at
least what it was holding. That is evidence and it is used.

**A per-unit cost of exactly zero is the instrument's floor, not a finding.** The N=20
rehearsal measured 3,600 settlement records growing the resident set by 0 bytes, because a
129 MB price-cache parse had already been paid. True — and emphatically not "settlement records
are free". Any resource whose per-unit cost comes out at zero is flagged `below_resolution` and
the stage degrades to a floor.

**The baseline is a high-water mark, not a point-in-time reading.** The projected peak comes
from `os.wait4`'s `ru_maxrss`, which is a process-lifetime maximum; subtracting a point-in-time
`VmRSS` baseline charged the stage's per-unit cost with every transient spike that preceded it.
The first rehearsal duly reported 67 KB per settlement record — ~180× the true figure, all of it
the price-cache parse wearing the records' clothes. `VmHWM` fixed it.

**Anything unmeasured is declared and makes the stage a floor.** Three declared omissions today:
the content-computation cost behind `site_publish`, the replica redundancy behind
`git_transport`, and the reduction step behind `run_output_serialization`.

**Death reaches the disk.** `test_checkpoints_survive_a_sigkill` launches a real child, really
kills it, and requires the checkpoints to be there anyway — and asserts the child's self-report
is *absent*, so the test cannot pass against a stage that quietly finished. An unflushed
checkpointer passes every in-process test and loses precisely the runs this probe exists to
measure.

---

## 4. Limits — read these before quoting anything above

1. **The two replica stages measure the write, not the work.** Publishing 10k customers needs a
   10k-customer run output, and §2.1 is the reason there isn't one.
2. **`MemAvailable` moves.** Pressure ratios differ run to run on a shared box; the projected
   byte figures do not. Quote the bytes, not the ratio.
3. **One year, not a decade.** Every projection here is a single year. The decade is 10×.
4. **The AS ceiling is address space.** Peak RSS is measured separately and is always lower.
5. **The settlement subject is `run_settlement` alone.** A real run also carries billing, DD
   books, meter reads, arrears and the rest; this is a floor on the pipeline, not the pipeline.
6. **Nothing here is a recommendation.** No substrate, no schema, no fix is proposed or implied.

---

## 5. Running it

```bash
python3 -m tools.scale_probe_10k                      # the committed configuration
python3 -m tools.scale_probe_10k --customers 100      # cheap end-to-end rehearsal
python3 -m tools.scale_probe_10k --stages settlement_build --as-ceiling-mb 1024
```

The report is overwritten in place each run; the prediction register is rewritten with a fresh
`written_at` before every run, which is what keeps the grading requirement honest rather than
letting one stale register bless every future run.
