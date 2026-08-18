# WORKER FINDING — the census guarding the belief band is blind to the population that sets the edge, and passes on every book where the declared edge is wrong

**Severity:** BLOCKING · **Lane:** D_billing_metering

**Discharged:** `tests/tools/test_couple_w2_11_d5.py::test_the_belief_edges_move_on_the_draw_size_alone`, `tests/tools/test_couple_w2_11_d5.py::test_the_invoice_span_is_the_null_control_and_does_not_move`, `tests/tools/test_couple_w2_11_d5.py::test_the_belief_axis_control_fires_on_its_own_named_defects`, `tests/tools/test_couple_w2_11_d5.py::test_pinning_the_population_hides_the_belief_draw_size_defect`, `tests/tools/test_couple_w2_11_d5.py::test_the_census_measures_the_population_that_sets_the_edge`, `tests/tools/test_couple_w2_11_d5.py::test_a_census_that_measures_only_the_invoice_span_fires`, `tests/tools/test_couple_w2_11_d5.py::test_a_book_with_invoices_and_no_failure_cannot_read_as_an_agreeing_one`, `tests/tools/test_couple_w2_11_d5.py::test_the_census_caveat_names_the_edge_setting_population`, `tools/couple_w2_11_d5.py` — landed 2026-08-18 by the RUNG-1c blocking draw on H27, all four repair conditions met: both belief entries carry a per-entry scope and a shared draw-size axis, the axis is swept over 21 books in about 2 seconds with no scorer call and its verdict plus its null control print on the default path, the census measures the failure-side population and both switches are published, and the caveat the reader meets now names which population each band belongs to. 15 new test cases across 9 functions, seven of them the parametrised mutation matrix, including the pinned-population case this document asked for by name. (Every backtick on this line is read as a PATH, so the prose carries none.)

**Left open, stated rather than implied:** the two resolution controls are still called with a hard n_customers=300 at their sole call site in main. That is the same disposition D28 took one register over — unpinning them buys a ~35-minute default run for a question the 2-second predictor axis now answers on 21 books instead of one.

**Raised:** 2026-08-18, worker tick, D30 DISCOVER pass 3 (LANE 3 idle draw). Full evidence and
the sweep tables: `docs/design/simplifications/D30_the_belief_band_is_this_books_length.yaml`,
note 3.
**Owner:** `tools/couple_w2_11_d5.py` — the `file_scope` of `H27_payment_belief_gap`
(`loop_stage: harden`) as well as of D30/D31, so this is drawable now.
**Intended rank (P-1):** top of `D_billing_metering`, immediately behind D28's landed sibling —
this is the same defect on the register next door, and one leg of it is a live fail-open.
**QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE). The draw that found it was
DISCOVER/FRAME only.

## What was observed

`DIMENSION_DRIFT_RESOLUTION["belief"]` and `["belief_population_mix"]` declare where the two
published belief figures stop resolving the company's memory:

```python
"own_saturates_below": -371,
"own_saturates_above": -308,      # tools/couple_w2_11_d5.py:4922-4923
```

Four literals across the two entries, and — unlike the detection register D28 repaired on
2026-08-18 — none of them carries a `..._scope` field. Only two scope fields exist anywhere in
the module (`collapsed_runs_scope`, `saturates_above_scope`, lines 2315 and 2386) and both are
D28's, on the detection side.

**Leg 1 — both edges are a property of the draw size.** Measured through the shipped
`measure_belief_window_resolution` over n_customers ∈ {12, 24, 40, 60, 120, 200, 300, 600,
1200} × seeds {7, 11, 23}, one book shape throughout:

| | distinct values over the sweep | declared |
|---|---|---|
| `own_saturates_above` | **6** — -333, -328, -320, -313, -309, -308 | -308 |
| `own_saturates_below` | **5** — -371, -370, -367, -355, -342 | -371 |

Twenty-five days of movement on the upper edge and twenty-nine on the lower, on the draw size
alone. The declared pair is the large-n asymptote: the failure-side band reaches [30, 92] only
from about n=600 and reads [59, 80] at n=12.

**Leg 2 — the controls that put those declarations on trial are pinned at the draw size the
declarations were authored at.** `measure_dimension_drift_resolution(n_customers=300)` and
`measure_own_drift_resolution(n_customers=300)` — hard literals at their sole call site in
`main()` (lines 12033 and 12100), whose own `--customers` defaults to 4000. This is D28's
sentence about `measure_organ_query_grid_saturation`, verbatim, one register over: the only
population these declarations could fail on is the one that produced them.

**Leg 3 — the census cross-check reads a different population from the one that sets the edge.
This is the fail-open.** `measure_scenario_constant_census` ages every record:

```python
ages = sorted((as_of - r.due_date).days for r in records)          # line 6549
```

while the edge the register declares is set by observed failures only:

```python
ages = sorted((as_of - r.due_date).days
              for r in records if r.result == "failed")            # line 6261
```

The invoice span is dense by construction — every account draws every period — and hits
[30, 92] at every n from 24 up. The failure span needs a failure to *land* on the extreme
invoice, which is a draw. So `describes_this_book` is True with **zero census violations** on
books where the failure-side edge is twenty days off the declaration:

| n | seed | invoice span | `describes_this_book` | census violations | failure-side edge | declared |
|---|---|---|---|---|---|---|
| 24 | 7 | [30, 92] | True | **0** | **-328** | -308 |
| 40 | 7 | [30, 92] | True | **0** | **-313** | -308 |
| 60 | 7 | [30, 92] | True | **0** | **-309** | -308 |
| 120 | 7 | [30, 92] | True | **0** | **-309** | -308 |
| 300 | 7 | [30, 92] | True | **0** | **-309** | -308 |

The control passes on precisely the books where the claim it guards is false — R15's fail-open
pattern, in a control this atom's own map note cites under "ALREADY LANDED" as the rule that
stops an edge rotting unnoticed.

**Null control.** Over the identical sweep the two quantities that must NOT move do not:
`predict_event_age_span_from_constants` returns {30, 92} at every point (it reads no draw), and
the census's invoice-side span is [30, 92] at every n from 24 up. The sweep moves the sample,
not the law — so the failure-side movement is a property of the realisation and not an artefact
of the perturbation.

## Why it is BLOCKING rather than LATENT

`describes_this_book` is the live switch that decides whether this scenario's band may be
quoted at all — its own comment calls it "the switch, and the caveat says so out loud when it
is False" (line 6558). It is answering True on the strength of a population whose span it
happens to share, about a band it does not measure. A reader is told the resolution claim has
been checked against the book; it has been checked against a different one.

## What a repair must show

1. The declared edges derived from the book actually scored, or carrying a `..._scope` field
   naming the draw size and seeds they were measured at — the shape D28 landed next door.
2. A population axis over the belief edges that can fail: the sweep above, run over books the
   declaration was not authored on. D28's sibling axis sweeps 25 books in ~3s with no
   `score_triad` call; the belief edges need no scorer call either, so the same economics hold.
3. The census cross-check reading the population that sets the edge, or declaring in its own
   verdict that it is checking the invoice span and not the failure span. Either is honest;
   what is not is a green verdict that reads as though it covered the edge.
4. R15 both ways, including a case that pins `n_customers` and proves the control goes green
   with the defect untouched — D28's fifth mutation case, which is what caught this class the
   first time.

## Not claimed

Nothing here touches the CAVEAT that travels with a published belief figure. `score_triad`
re-derives `belief_resolution_caveat` and the census caveat from the scored book on every call
(lines 10685-10693), so the sentence riding a live figure states that book's own headroom and
is correct at any draw size. The defect is confined to the register's literals and to the
controls over them.
