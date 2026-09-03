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

*Graded 2026-09-01 against the artefact the two-step publish produced, in this file, beside the
predictions. Six of eight confirmed. **The two refutations are the only parts of this exercise that
taught me anything**, and one of them found a defect in a third published feed.*

**P1 — all ten rows gain the block. CONFIRMED.** Ten rows, five populations each, six statistics
each, zero missing keys.

**P2 — one variable. REFUTED, twice over, and this is the finding.**

*First refutation — the publish is not the command I thought it was.* Running
`tools/generate_dashboard_data.py` alone **deleted 1,800 leaves**: the whole of
`customers.portfolio_event_stream`, all 200 events. Not one error, not one warning, rc=0. The
section is patched onto the already-generated file by `tools/generate_portfolio_event_stream.py`,
which `background/process_run_complete.py` calls afterwards *by design* — so **the generator that
owns the file destroys a live section of it on every standalone run, and had I published that output
the site's Event Stream would have been emptied by a routine regeneration.**

That is the third instance of one shape in one afternoon, and the other two are already written up:
`SEAT_FINDING_A_PUBLISHED_SECTION_HAS_NO_WRITER_AND_ITS_OWN_GENERATOR_DELETES_IT_2026-09-01`
(`value_arms.json`, `svt_drift_belief`, no writer at all) and this file's own subject (the artefact
lagging the code). **The difference worth recording: those two were found by accident, and this one
was found because a prediction was written down that could fail.** That is the entire argument for
pre-registration, and it paid here on its first use.

*Second refutation — a published feed is not reproducible from its own inputs.* With the patcher run
in its proper place the events came back, 0 removed — and **299 leaves inside
`portfolio_event_stream` still changed on a byte-identical input.** Measured rather than assumed:
the 200 events are **the same SET** (`only in before: 0, only in after: 0`), so it is a **pure
permutation** — an unstable tie-break reordering same-date events. Membership is intact and no
published content changed, so this is cosmetic churn and not a regression, and it is pre-existing
behaviour of that feed rather than anything this change introduced.

**But it means P2 as I wrote it could never have been confirmed by any publish**, because I asserted
leaf-level equality over an artefact that contains a non-deterministic section. That is my error,
not the artefact's, and it is worth more than the confirmation would have been: the honest form of
the prediction is *no published FIGURE moves*, which holds.

*What I named as the likely cause was wrong.* I predicted the refutation would come from the market
feeds, which are modified in the shared tree right now. **Not one market figure moved.** The
artefact is reproducible on its financial content and not on its event ordering — the opposite of
where I was looking.

*The complete list of movers, as promised — nothing else changed:*
| what moved | why |
|---|---|
| +300 leaves, all `bill_shock_by_population` | the change being graded |
| `avg_bill_shock_pct_population` × 10 | the note rewrite from `2118135e5` |
| `meta.generated_at` | the clock |
| `portfolio_event_stream`, 299 leaves | a permutation of the same 200 events (above) |

**P3 — the split reconciles. CONFIRMED, at the artefact's own precision, and my first grader said
otherwise.** It called 2021 refuted on a weighted mean of 42.2282 against a published 42.3 — a
delta of 0.072 against a tolerance of 0.06 I had picked without thinking about it. **Every cell's
`avg_pct` is published rounded to 1dp, so a weighted mean of rounded values cannot reproduce the
mixed mean to better than about 0.1 in principle.** Re-graded at the rounding the artefact actually
carries, all ten years hold, worst delta 0.0718 (2021). *This is the grader-reads-the-rounded-field
false refutation this project already has written down, made by me again.* The partition itself is
exact — counts, not means — and that is what the control asserts.

**P4 — the units trap. CONFIRMED**, all ten years: `mixed_all_population.avg_pct / 100` is the
published `avg_bill_shock_pct` within its own 2dp rounding. The fraction-under-a-`_pct`-name is
still there and is still not repaired here.

**P5 — the published subject ties to the pre-split measurement. CONFIRMED, 6,094 exactly**, the
figure `ae78afdb1` measured on this run before the publisher existed. The block is a split of the
right population.

**P6 — no unobservable published as a measured zero. CONFIRMED.** `out_of_scope` is `n=0` with null
means in all ten years — the world has no prepayment households, and the artefact says that rather
than reporting that prepayment households experience no bill shock.

**P7 — the monthly series does not move. CONFIRMED**, 4,353 leaves before and after, every value
identical.

**P8 — the control is red before and green after. CONFIRMED, and it is the leg that closes the
hole.** Against the artefact as served: **1 failed, 6 passed** — red on all ten annual years, green
on the monthly series. **The same assertion, two series, one already correct**: that is the proof it
discriminates rather than passing on everything, and it came from the real file, not a fixture.
After the publish: **7 passed.**

### What is now true that was not

`site/data/dashboard.json` — the file a reader is served — carries both series split, each cell with
its own `n`, median, max and bootstrap interval, and a mixed total that names the split it is made
of. And `tests/tools/test_the_published_artefact_carries_the_split_the_code_computes.py` is the
first control anywhere that reads the served file's shock fields, so the artefact can no longer sit
on an older clock than the code without something going red.

### Owed, and not absorbed here

1. **`portfolio_event_stream` has no control and its generator deletes it.** Same class as the
   `value_arms.json` finding; filed as its own instance rather than fixed inside a bill-shock
   commit, because a publishing defect in a different feed is not this item's scope.
2. The unstable tie-break in that feed's ordering.
3. `avg_bill_shock_pct` is still a fraction under a `_pct` name; the 32 `unknown` bills are still
   unattributed; and **the `payment` population's figure is still a bill-to-bill difference for
   households who do not pay the bill** — the director's named out-of-scope build, untouched.
