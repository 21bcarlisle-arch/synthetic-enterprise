# [WORKER PREREGISTRATION] What publishing the annual split to the served artefact must show

**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** unminted
**Filed:** 2026-09-01, **before the generator is run.** Every before-figure below was read out of
`site/data/dashboard.json` as it is served right now, at `2118135e5`.
**Knowledge:** `docs/market_research/what_bill_shock_is.md` — the definition, established and NOT
re-opened.
**Predecessors:** monthly series split at `98db658f2`, published at `318066998`, graded at
`63deb6405`. Annual series split at `2118135e5`, pre-registered at `ae78afdb1`.

## Class registration

Belongs to `figures_on_a_superseded_clock`. The served figure is on an older clock than the code
that computes it: `2118135e5` landed `bill_shock_by_population` and rewrote the note that misled,
and **neither has reached the file a reader is served.**

## Why this exists

`2118135e5` graded seven predictions and closed with *"no mean spanning both populations is
published on this surface without its two component means beside it."* **That sentence is not true
of the served artefact.** Read at HEAD:

```
$ git show HEAD:site/data/dashboard.json | ... financial.annual[-1]
HEAD annual keys: ['avg_bill_shock_pct', 'avg_bill_shock_pct_population']
has bill_shock_by_population: False
note: "every bill with a computable shock ... NOT only the bills flagged as shocks."
```

The block is absent and **the note is still the pre-`2118135e5` one** — the note that answers the
population question in the wrong dimension, which that commit itself identified as *worse than
silence*. The last publish was `318066998`, which predates the split code. The grading was computed;
it was never published.

**The drawn item's own exit condition is the test: *"if the site still serves one `avg_shock_pct`,
it has not been done."* It does. So it is not done.**

### Why nothing was red

Every control for the annual split — `tests/tools/test_the_annual_shock_mean_stops_spanning_two_populations.py`
— takes `extract_financial` as its subject and feeds it synthetic fixtures. So does the monthly
sibling. **Not one control reads `site/data/dashboard.json`.** The artefact can lack the split
entirely and the whole suite is green. That is the `controls_that_cannot_fail` sibling of this
finding, and closing it is part of the work, not a follow-up: a seam is not landed until its control
is.

## The before state, on the served artefact

`financial.annual[].avg_bill_shock_pct` — **fractions published under a `_pct` name**, one mean
spanning both populations, no `n`, no bound:

| year | published | bills_count |
|---|---:|---:|
| 2016 | 0.43 | 719 |
| 2017 | 0.36 | 1054 |
| 2018 | 0.31 | 1029 |
| 2019 | 0.43 | 1051 |
| 2020 | 0.41 | 1174 |
| 2021 | 0.42 | 1281 |
| 2022 | **0.58** | 1338 |
| 2023 | 0.47 | 1420 |
| 2024 | 0.43 | 1639 |
| 2025 | 0.46 | 860 |

Artefact digest, all 78,348 leaves: `95f203c042219d22`.
Monthly series: `shock_by_population` **is** present (published at `318066998`) — the two series are
in different states on the same file, which is the whole shape of this finding.

## The input is provably the same one

- `docs/reports/run_output_latest.json` and `docs/reports/run_output_98db658f2_20260901T155311Z.json`
  are **byte-identical**: `md5 6f34154bf6d3064fb31295e27d73b933`. That is the run behind the served
  page.
- `git log 318066998..HEAD -- tools/generate_dashboard_data.py` returns **exactly one commit**,
  `2118135e5`, whose diff is +72/−8 and is additive apart from the note rewrite.

So this is a genuine one-variable step: same input, one code delta, and the delta is the thing being
graded. **No new simulation run is involved and none should be** — a re-run would change the input
and make the diff unattributable, which is the error this file exists to avoid.

## The predictions

Filed before the generator is run. Properties only — no per-year value is predicted, because every
one of them is computable from the artefact on disk and "predicting" them would be transcription.

**P1 — all ten annual rows gain `bill_shock_by_population`,** with five keys each (`payment`,
`bill`, `out_of_scope`, `unknown`, `mixed_all_population`), each carrying `n`, `avg_pct`,
`median_pct`, `max_pct`, `ci95_low`, `ci95_high`. *Refuted if any row lacks the block or any key.*

**P2 — ONE VARIABLE: nothing else in the artefact moves.** The only leaves that may change value are
(i) the new `bill_shock_by_population` blocks, (ii) the `avg_bill_shock_pct_population` note string,
(iii) `meta.generated_at`. **A fourth mover refutes this, and I will name every one of them
whichever way it falls.**

*This is the prediction most likely to fail and I am saying so before running it, not after.* The
generator reads more than the run output: an Elexon SSP cache and the market feeds, and
`docs/market_data/price_feed.json`, `consumption_feed.json` and `grid_intensity_feed.json` are all
**modified in the shared working tree right now by another lane.** If any market-derived figure
moves, P2 is refuted and the cause is a live feed rather than this change — which is a real finding
about whether this artefact is reproducible at all, and it would be worth more than the confirmation.

**P3 — the split reconciles from the artefact alone.** For every year, the four populations' `n` sum
to `mixed_all_population.n`, and the n-weighted mean of their `avg_pct` reproduces
`mixed_all_population.avg_pct` to rounding. *Refuted if any year fails.*

**P4 — the units trap is survived.** `mixed_all_population.avg_pct / 100` equals the published
`avg_bill_shock_pct` to that field's 2dp rounding, in all ten years. **The sibling is a FRACTION
under a `_pct` name while the new block is percentages**; this is the specific way the block could be
internally consistent and still not be about the field it sits beside. *Refuted if any year
disagrees beyond rounding.*

**P5 — the published subject ties to the pre-split measurement.** The counts sum to **6,094** across
the ten years — the figure `ae78afdb1` measured on this exact run before the publisher existed.
*Refuted if not.* This is what stops the block being a correct split of the wrong subject.

**P6 — `out_of_scope` publishes `n=0` with null means in all ten years, never `0.0`.** Prepayment is
excluded by definition, and an unobservable published as a measured zero is this project's own named
defect. *Refuted by a single `0.0`.*

**P7 — the monthly series does not move.** It was published at `318066998` and no code has touched
it since. Formally a case of P2, named separately because it is the sibling series and its being
already-correct is what made the annual gap invisible.

**P8 — the new live-artefact control is RED before the regeneration and GREEN after.** It is written
and run against the artefact as it stands *first*. **If it is green before, it cannot fail and it is
worthless** — I would have shipped a control that certifies the defect it was written for. This is
the mutation proof run in the honest direction, on the real artefact rather than a fixture.

## What this closes and what it does not

**Would close:** the served artefact carries both series split, and a control exists that can see the
difference between code that computes a split and a page that publishes one.

**Does not close:** `avg_bill_shock_pct` is still a fraction under a `_pct` name; the 32 `unknown`
bills are still unattributed; and the `payment` population's figure is still a bill-to-bill
difference for households who do not pay the bill. **That last one is the director's named
out-of-scope build** — making the direct debit a modelled quantity from estimated annual consumption
— and it is the only one of the three that changes what the number *means* rather than what it is
called. It is not absorbed here.

---

## GRADING

*To be completed after the run, in this file, beside the predictions.*
