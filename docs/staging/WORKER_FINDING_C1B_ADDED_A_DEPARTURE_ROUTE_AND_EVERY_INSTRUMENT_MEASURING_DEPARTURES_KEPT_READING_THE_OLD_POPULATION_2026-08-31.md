**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# C1b gave the world a second way to leave, and four instruments went on measuring the population that no longer is the book

**Found:** 2026-08-31, applying the director's validation ladder to churn
(`DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31.md`). Found by the **interconnection** question
the delivery seat now owes at every orientation — *of what landed since the last orientation, what
else assumes it, and does that assumption still hold* — and not by any control, because no control
could have.

## What happened

`067a00dfd` (C1b, 2026-08-30) added the SVT inertia departure route: an account on the standard
variable product drifts off it at a segment boundary. There is no renewal decision, deliberately —
no offer is requested and no rate is struck.

`tools/capture_departure_factors.py` builds the factor table by **wrapping
`roll_lifecycle_event`**, the renewal decision. An SVT departure never calls it. So from that commit
the captured table stopped being the book and became the *renewal-decision subset* of it, which by
the C1b author's own estimate is now the minority: *"roughly 55-58% of domestic account-days no
longer reach that roll at all."*

**Four readers take that table as their subject:**

| reader | what it now computes |
|---|---|
| `tools/fit_year_level_anchor.py` | the year level anchor, fitted on one route |
| `tools/measure_departure_level.py` | the world's departure level vs the published band, on one route |
| `tools/population_anchor._churn_by_year` | churn by year, on one route |
| C2 reason mix (`docs/reports/c2_reason_mix_interval.json`) | a cause mix that cannot contain the largest cause |

**Nothing went red.** The table still had rows and every field populated. This is the
*controls-keyed-to-a-structure-that-moved* class — the control goes **quiet**, not loud — arriving
for the fifth time, and the population floor that normally catches it did not fire because the
population was intact. It was the *scope* of the population that moved, not merely its size.

## The size of it, measured on a two-route capture taken for this finding

| | pre-C1b capture | two-route capture, 2026-08-31 |
|---|---|---|
| renewal decisions | **465** | **144** |
| SVT segment decisions | not recorded | **1,266** |
| departures by renewal | 79 | 32 |
| departures off SVT | **invisible** | **50** |
| share of departures the renewal table can see | 100% | **39%** |

**The population the year anchor is fitted on lost 69% of its rows, and the majority of departures
now happen on the route that table cannot see.** The C2 published reason mix
(`docs/reports/c2_reason_mix_interval.json`) lists bill_shock, price_position and dissatisfaction —
three of four causes — while the fourth is the largest. `departure_risks` describes it as *"the
single largest departure route in a real domestic book, because two thirds of one sits on SVT"*.

## It was named at the time, and a named comment is not a control

The C1b author wrote it down at the site, precisely:

> OWED, NAMED RATHER THAN LEFT TO BE FOUND: the readers whose subject is ALL departures —
> `tools/population_anchor._churn_by_year` and `tools/measure_departure_level` — must union these
> in, or they will report a departure LEVEL that is missing the route this commit added. Neither is
> live against this log today (both read captured artefacts), so nothing regresses on landing; both
> go stale the moment the next capture runs.

Every word of that is right. It is the strongest form the comment could take and it still did not
act. **The lesson is not "write better comments".** It is that a debt taken deliberately at a seam
needs something that fails, or a queue entry that ranks — and this had neither for a day, across a
capture, a fit and two published readings.

## And the departures were recorded without a denominator

`run_phase2b` kept `_svt_departures` — the segments where the roll **fired**. The segments where it
did not were never recorded at all. So even a reader who dutifully unioned the two lists could
compute a departure **count** on the SVT route and **no rate**, because the population it happened
in was not written down. Rung 3 of the ladder — does this route discriminate between households? —
was not merely unmeasured, it was **unmeasurable**.

## Repaired

* `run_phase2b` now appends to **`_svt_decisions`** on every SVT segment evaluated, departed or not,
  with the hazard, the roll, the outcome and the factors. Written **before** the departure branch,
  so the denominator cannot depend on the outcome and there is one write rather than an `if` and an
  `else` that must be kept in step.
* `capture_departure_factors` writes it to `<out>_svt_segment_decisions.json`. **A second file, not
  a union.** An SVT decision carries no `churn_probability`, no `sim_price_response` and no
  `sim_bill_shock_base` — there was no renewal for any of them to describe. Appending them to the
  renewal table would hand every existing reader rows of `None` and let a mean be taken across two
  populations, which is the failure this repository has paid for repeatedly.
* An empty second file **says so loudly on stderr**, because "nobody was on SVT" and "the recorder
  stopped recording" produce the identical artefact and the tool cannot tell them apart.
* `tools/measure_churn_heterogeneity.route_coverage` prints, on every run, which routes the table it
  is reading can see — and `test_the_table_states_which_departure_ROUTES_it_can_see` holds that a
  reading always names its population, so a verdict can never be quoted without it.

**Observability only. No number in the run reads `_svt_decisions`,** so the world is unchanged and
this is not an R13 baseline edit.

### The `run_phase2b` half is NOT in this commit, and why

C1b's departure roll is **another lane's uncommitted work**, live in this shared tree while its tick
runs. `_svt_decisions` sits on top of it, and `simulation/run_phase2b.py` cannot be committed by
pathspec without also landing that lane's in-flight interlock across five simulation files. Adopting
five files of someone else's active work to ship one observability list is the trade that goes
wrong.

**So it is parked in the tree, where whichever lane commits `run_phase2b.py` next carries it.** The
consequence is stated rather than hidden: **the captured artefacts in this commit are reproducible
from the tree that ran and not from this commit alone.** `capture_departure_factors` fails loudly
rather than quietly if run before C1b lands — an empty SVT file, a warning on stderr, and a rung-3
reading that then **refuses** on the population floor instead of reporting a clean AUC over 144
renewals. That refusal is the intended behaviour and is leg 4 of the control.

## What is still owed, and it is not small

1. **Re-fit the year level anchor on both routes.** It was fitted on a run where the renewal roll
   was the only way out. `departure_risks` says so itself: *"the year anchor is now OVER-FITTED"*.
   The re-capture is the first half; capture → refit → capture is the loop, and **never a widened
   band**.
2. **Union the two routes in `measure_departure_level` and `population_anchor._churn_by_year`**, on
   a declared denominator. Both are the readers C1b named.
3. **The C2 reason mix is missing its largest cause.** `svt_inertia` is described in
   `departure_risks` as *"the single largest departure route in a real domestic book, because two
   thirds of one sits on SVT"*, and the published mix contains bill_shock, dissatisfaction and
   price_position only. Any reader of that mix today is reading three of four causes as if they were
   four of four.

## Severity

**LATENT, and measured rather than inferred.** The stale readings are captured artefacts, not live
feeds: `docs/reports/c2_departure_factors.json` and the fitted anchor are files, and nothing
regenerates them on a schedule. No figure a reader can see moved on the C1b landing. What is true is
that **the next capture, fit or published mix would have been wrong and would have looked right** —
which is why this is filed rather than quietly fixed.

---

## MEASURED, 2026-08-31, after the finding landed: the band control is green on a stale artefact while its live subject is unreadable

Running `measure_departure_level`'s own comparison over the two-route capture, per renewal:

| year | published band | modelled E[depart] % | inside? |
|---|---|---|---|
| 2016 | 17.00–17.60 | 17.86 | no |
| 2017 | 13.50–14.00 | 14.29 | no |
| 2018 | 19.50–20.00 | **29.50** | no |
| 2019 | 20.70–21.30 | 20.44 | no |
| 2020 | 22.50–23.00 | **29.43** | no |
| 2021 | 17.90–18.40 | 17.19 | no |
| 2023 | 8.90–12.50 | **15.51** | no |
| 2024 | 12.50–16.10 | **22.35** | no |
| 2025 | 14.30–17.90 | **21.10** | no |

**Nine years, none inside**, and 2022 is absent entirely — the renewal book has no decisions at all
in that year, which is why the instrument's summary line prints `world E[depart] = nan%`.

`test_the_worlds_realised_departure_rate_is_inside_the_published_band` is **green**, because its
subject is `docs/reports/c2_departure_factors.json` — the pre-C1b, 465-renewal artefact.

**THE CORRECT READING IS NOT "THE WORLD IS OUT OF BAND", AND SAYING SO WOULD BE THE SAME MISTAKE
ONE LEVEL UP.** This column is a mean over *renewal decisions*, and C1b changed what a renewal
decision is a sample of: the households that sit on the standard variable product no longer reach
the roll, so the 144 that remain are a **selected** subset of the book — the ones who took a fixed
deal, i.e. the ones who demonstrably shop. A mean over shoppers is not the book's departure level
and is not comparable to a published whole-population switching rate. The denominator moved, so the
comparison the instrument makes no longer has a subject.

So the honest statement is: **the control is passing on an artefact from a world that no longer
exists, and the reading it would take from the world that does exist is not a quantity it can
compare.** Both halves have to be fixed together — union the routes AND declare the denominator —
and neither is a re-fit. **Re-fitting `YEAR_LEVEL_ANCHOR` against the numbers in the table above
would be fitting the world to a selected sub-population**, which is worse than the staleness it
would appear to cure.

This sharpens item 2 of what is owed above rather than adding to it, and it is inside the delivery
lane's current focus item.
