# PB1 — How big the world should be, with what it costs beside it

**Atom:** `PB1_population_target_and_its_price` (lane W2_customer_generator, epoch 2, dial 3)
**Source:** `docs/staging/in_progress/DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11.md`
deliverable 1 · **Depends on:** `AO12_scale_probe_10k`
**Mechanism:** `simulation/premise_population.py` (PB1 section) · **Controls:**
`tests/simulation/test_premise_population.py`
**Price list:** `docs/observability/scale_probe_10k/report.json`, run `20260812T013154Z`

---

## 0. Purpose, guarantee, why

**Purpose.** Propose a premise-population target and put the probe's *measured* cost beside it,
so scale stops being an inherited default and becomes a number that was priced before it was
bought.

**Guarantee.** Every cost below is READ from AO12's report. Nothing here re-derives a per-unit
constant or writes one down as a literal, and no function falls back to a default when the
report is missing — it refuses. The ruling's governor is the whole point: *"if the probe says
the scale is unaffordable on current storage, that is the answer."* A pricing mechanism that
cannot return NO is not one.

**Why this is a proposal and not a raise.** The number a run actually draws is a CURRICULUM
instrument and moving it is the director's act, never a build side effect (R13). The live
callers of `draw_premise_population` are untouched;
`test_the_proposal_is_not_wired_into_the_live_draw` fails the moment one starts reading
`PROPOSED_PREMISE_POPULATION`.

---

## 1. The proposal

> **Premise-population target: 100,000.**

**Reasoning, in the order it actually ran.**

1. **The cost said yes, and it said so measured rather than extrapolated.** `population_draw` is
   the only stage in AO12's report that comes back FITS. At the proposed target it projects
   **108,713,970 bytes** by the report's own method — 1.27% of that run's budget.
2. **The extrapolation was then checked, because 100k is 10× beyond AO12's measured range.** Re-running
   AO12's own `population_draw` stage at exactly 100,000 on 2026-08-24 measured
   **106,885,120 bytes peak RSS in 6.136 s** for 100,052 premises drawn. The projection
   over-predicts the measurement by 1.7%, i.e. it is slightly conservative. AO12's projection
   method is sound at 10× its measured range, and the proposal rests on a measurement at the
   proposed N rather than on a straight line through a smaller one.
3. **It has to be much larger than the book, or the acquisition physics degenerate.** PB3 requires
   a growth curve that can be *lost*; that needs a stock the company competes for and mostly does
   not win. Against the measured book ceiling in §3, 100,000 leaves a stock:book ratio of at least
   158:1 on a single year.
4. **Why not larger.** The draw is append-only (`P0007` never changes), so raising it later is
   cheap and reversible. There is no reason to buy scale nothing consumes yet, and §3 shows the
   binding constraint is the book, not the stock.
5. **Why not smaller.** Below roughly 10× the book, acquisition stops being selective and the
   subset-of-a-population premise the ruling's wall depends on stops meaning anything.

*Orientation only, not an input to the number and not verified in this tick:* 100,000 is a small
fraction of the UK domestic meter population. This is a sample of the stock and is not a claim to
represent the market.

---

## 2. The price list, read from AO12's report

Transcribed from `docs/observability/scale_probe_10k/report.json`, run `20260812T013154Z`,
budget `8,582,946,816` bytes. Peak RSS, wall time and output size are the probe's own fields.

| Stage | Status | Peak RSS (B) | Wall (s) | Output (B) | Kind | AO12 verdict |
|---|---|---|---|---|---|---|
| `population_draw` | measured | 31,563,776 | 0.2013 | — | MEASURED | **FITS** |
| `settlement_build` | ceiling_death | 3,172,732,928 | 7.0513 | — | LOWER_BOUND | **DOES_NOT_FIT** |
| `run_output_serialization` | measured | 610,410,496 | 0.7316 | 126,214,554 | LOWER_BOUND | **DOES_NOT_FIT** |
| `site_publish` | measured | 22,913,024 | 1.3443 | 1,854,553,833 | LOWER_BOUND | UNDECIDED |
| `git_transport` | measured | 28,831,744 | 3.6336 | 1,420,425 | LOWER_BOUND | UNDECIDED |

An em-dash in Output means the stage wrote nothing, and it is stored as `None` rather than `0` —
a zero there would read as "free" and it is not the same claim.

`stage_prices()` derives the Kind column from the raw stage records by its own route, and
`test_the_transcription_reproduces_the_probes_own_affordability_map` requires it to agree with the
report's stored verdict. Two paths to one answer; a disagreement is a finding about one of them.

---

## 3. The finding: the population and the book have different price lists

This is the part the ruling's ordering invites a reader to miss.

**Drawing a premise costs ~841–860 bytes. Settling a customer for one year costs ~13.6 MB.** The
two questions are three orders of magnitude apart per head, and "how big is the world" therefore
has a completely different answer from "how big is the book".

The settlement figure adds two stages rather than taking the larger, and the reason is in AO12's
source rather than in its prose: in `tools/scale_probe_10k.py::_stage_run_output_serialization`
the baseline is taken *after* `run_settlement` has returned, so the 411 B/record is measured while
the settlement working set is still held. A single-process build-then-serialize pays both.

| | Bytes/record | Bytes/customer-year | Max customers |
|---|---|---|---|
| `settlement_build` + `run_output_serialization` | 774.87 | 13,575,644 | **≤ 632** (1 year) |
| the same, over the decade the published run replays | 774.87 | 135,756,442 | **≤ 63** |

**Every one of those numbers is a CEILING, and deliberately so.** Both inputs are floors:
`settlement_build` died at its ceiling and its own record notes the per-unit cost is *under-stated*;
`run_output_serialization` declares the reduction omitted. Floors only move up, so the affordable
book only moves down. A cost governor whose error bar points the reassuring way is not a governor.

**What is NOT claimed.** The shipped run reduces before it persists
(`saas.reporting.annual_report.extract_report_data`), and that path's cost is UNMEASURED. The
figures above price a build-then-serialize-raw shape. Fail-closed: the shipped shape's cost is
*unknown*, which is not the same as *cheaper*, and this document does not price it at zero.
AO12's Limit 5 applies on top — `run_settlement` alone is a floor on the pipeline, not the
pipeline, which also carries billing, DD books, meter reads and arrears.

---

## 4. The affordability verdict, computed

- **Premise population at 100,000 — FITS.** Measured at the proposed N, not extrapolated to it.
  Nothing blocks this target on cost.
- **The book — the governor FIRES.** On the committed measurement the settlement path holds at
  most ~632 customer-years, and at most ~63 customers across the decade the published run replays.

So the ruling's ordering survives its own cost test only in half: **the world can grow now, and
the book cannot.** PB2 is asked for an opening book "materially larger than 13 and defensible as a
plausible small supplier" — on a decade run, current storage bounds that above at ~63, which is
materially larger than 13 and nowhere near a plausible small supplier.

**That is the answer, not an obstacle to route around.** Per the ruling's Sequencing paragraph, the
queryable-projections / storage work is the prerequisite:
`docs/staging/in_progress/DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS_2026-08-10.md`. It is still an
unconsumed mint source with its own WORK THIS CREATES block, so it **cannot be a `depends_on` edge
on PB2 yet** — recording the dependency in prose here rather than minting it sideways, which would
leave that doorbell pointing at work done under another name.

---

## 5. How this stays honest (R15)

Three mutations were run against the production code, each firing its own control (2026-08-24):

| Killer pattern | Mutation applied | Control that fired |
|---|---|---|
| TAUTOLOGY | per-record constant written in the module instead of read | `test_the_price_is_read_from_the_report_and_not_written_in_this_repo` |
| FAIL-OPEN | UNKNOWN stage sails through instead of refusing | `test_mutation_an_unmeasured_stage_is_refused_rather_than_priced_at_zero` |
| FAIL-SILENT / §2.4 | a floor allowed to come back FITS | `test_a_floor_below_budget_is_undecided_and_never_fits` |

The fail-open control asserts in **both** directions: that an unmeasured stage is refused, and that
had it been priced at zero the affordable book would have come out strictly *larger*. The second
assertion is what makes the refusal load-bearing rather than decorative.

A missing, malformed or empty report raises `ScaleProbeUnavailable` rather than returning a
default, because an unavailable measurement is a FAILED measurement.

---

## 6. Limits

1. **Everything here inherits AO12's limits** — read `docs/design/SCALE_PROBE_10K.md` §4 before
   quoting any figure above, particularly Limit 2 (`MemAvailable` moves; quote bytes, not ratios).
   The 100k confirmation run saw a 9,713,487,872-byte budget against the committed run's
   8,582,946,816; the byte costs are comparable, the pressure ratios are not.
2. **The book ceiling is RSS-bound only.** Disk is not the binding constraint at these sizes and is
   not modelled here.
3. **No substrate is proposed.** Naming queryable projections as the prerequisite is not choosing a
   storage design; that remains an architecture door.
4. **This is a proposal.** No population was raised, and no live path reads the constant.
