# [WORKER PREREGISTRATION] What splitting the shock series by population must show

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`
**Filed:** 2026-09-01, **before the change.** Every number below was measured on the published
`run_output_latest.json` (3,161 events) BEFORE any code was edited, and none was written after a result.
**Knowledge:** `docs/market_research/what_bill_shock_is.md` — the definition, established and NOT re-opened.
**Finding:** `WORKER_FINDING_THE_WORLD_KNOWS_HOW_EACH_HOUSEHOLD_PAYS_AND_BILL_SHOCK_IS_THE_ONE_ORGAN_NOT_TOLD_2026-09-01`.
**Predecessor:** `WORKER_PREREGISTRATION_WHAT_TELLING_THE_SHOCK_MEASURE_HOW_THE_HOUSEHOLD_PAYS_MUST_SHOW_2026-09-01`
(the attribution, landed `fc1c9a65c`, which moved no published number and said so).

## The defect this closes, stated exactly

The attribution landed. It reaches the **bill**. It does not reach the **event**.

`saas/reporting/annual_report.py:517` builds `shock_events` from `shocked` bills and forwards five
fields. `bill_shock_population` is not one of them. Measured on the published artefact: **3,161 of
3,161 events carry no population at all.**

So the field that decides which definition applies is computed, written onto every bill, and then
**dropped by the reducer** before it reaches any published surface. This is
`a_fail_closed_guard_can_compose_its_verdict_into_an_artefact_no_published_surface_reads` and
`the_run_reducer_forwarded_the_departure_count_and_dropped_the_population_it_came_from`, together.

## The change, in one line

The reducer forwards the population, and **`monthly_ops` stops publishing one percentage over a
mixed population.**

## The predictions

**S1 — the split of the published record, whole book.** Measured now, by resolving each event's
account through `run_phase4c_on_phase2b.simulated_payment_channel` — the same feed the run itself
uses, so this is a prediction of what the run will reproduce, not an independent estimate:

| population | definition | events | share | mean | median | max |
|---|---|---:|---:|---:|---:|---:|
| `payment` (direct debit) | the change in the amount collected | **2,238** | **70.8%** | 113.9% | 50.8% | 2593.1% |
| `bill` (standard credit) | **the bill** | **912** | 28.9% | 93.4% | 45.4% | 1305.2% |
| `out_of_scope` (prepayment) | neither | **0** | 0.0% | — | — | — |
| `unknown` (non-resi) | neither — the definitions are domestic | **11** | 0.3% | 158.1% | 150.7% | 311.5% |
| **MIXED, as published today** | | 3,161 | 100% | **108.1%** | 49.7% | 2593.1% |

This reproduces the predecessor prereg's P2 (2,238 / 912 / 11) to the event, which is the check that
the mapping is the one the other three organs already use rather than a fourth opinion.

**S2 — THE HEADLINE GETS WORSE, NOT BETTER, AND THAT IS THE POINT.** Restricting `avg_shock_pct` to
the population the arithmetic is actually valid for does **not** flatter the figure:

- worst month today (mixed): **315.6%** at 2016-08
- worst month after the split (definition B only): **465.3%** at 2017-02
- months above 200%: **12 today → 7 after**

**If the split had made every number smaller I would distrust it.** It does not. It moves the peak
*up* by 150pp, because the 2016-08 peak was never a definition-B measurement at all — see S3.

**S3 — the worst month published today has ZERO events in the population the measure is valid for.**
2016-08, the 315.6% that the live artefact serves as the worst month on record, is **100%
`payment`-population**: every one of its five events is a direct-debit household, for whom the bill
is a statement that arrives and is filed. **The headline figure of the whole series is computed
entirely from households the established definition says the bill does not shock.** Two other months
(2017-01, 2019-03) are likewise zero-`bill`.

**S4 — the empty months must publish `None`, never `0.0`.** Three months have no definition-B event.
Today an empty month publishes `avg_shock_pct: 0.0`, which reads as *measured, and no shock* — an
unobservable turned into a published zero
(`a_default_zero_parameter_turns_an_unobservable_cause_into_a_published_measured_zero`). After the
split those three months publish `None` with the count beside it. **A month that got smaller because
it went from 315.6% to `None` has not improved; it has stopped claiming something it could not
support.**

**S5 — 21 further months carry 1–4 definition-B events.** The bound landed in `8e395664e` already
covers this and is not re-done here; the split makes it load-bearing rather than decorative, because
the thin months are thinner once the population is honest.

**S6 — prepayment stays 0 and is NOT repaired here.** `PaymentChannel` has two members, so the
`out_of_scope` branch is unreachable and our book is 0% prepayment against a published ~13%. Naming
the branch is not the repair. That is item (c) and it is a **separate commit**, by instruction.

## What would refute this, stated before the run

- Any event count other than **2,238 / 912 / 0 / 11** means the reducer's mapping is not the run's
  mapping, and the fourth organ disagrees with the other three about how one household pays.
- Any movement in an individual event's `bill_shock_pct`, or in `financial.annual[].avg_bill_shock_pct`,
  refutes the claim that this is a **re-partition and not a re-computation**. No arithmetic changes.
- A definition-B peak at or below 315.6% would refute **S2**, and would mean I had quietly selected
  the flattering partition.
- Any month publishing `0.0` where it has no definition-B event refutes **S4**.

## What this commit explicitly does NOT do

1. **It does not measure definition A.** For a `payment` household the right quantity is the change
   in the amount *collected*, and the DD amount is not yet a modelled quantity — the director's own
   correction, explicitly out of scope by instruction. So the DD population's bill-to-bill difference
   is published **under its own name, labelled as not being a shock measure**, rather than either
   deleted or left masquerading as one. Deleting it would hide 70.8% of the record; leaving it named
   "shock" is the defect.
2. **It does not add or exclude prepayment on the surface.** (c), separately.
3. **It does not touch the £5 baseline floor or the bound.** Both landed and both stand.

---

## OUTCOME — scored after the change, against the predictions above

*Written after running `extract_monthly_ops` over the published artefact with the new reducer's
attribution applied. Nothing above this line was edited.*

| prediction | result |
|---|---|
| **S1** — 2,238 / 912 / 0 / 11 | **CONFIRMED to the event.** `{'payment': 2238, 'bill': 912, 'out_of_scope': 0, 'unknown': 11}` |
| **S2** — peak rises 315.6% → 465.3%, months>200% falls 12 → 7 | **CONFIRMED.** Headline max 465.3% at 2017-02; 7 months above 200% |
| **S3** — 2016-08 has zero definition-B events | **CONFIRMED.** `bill` n=0, `payment` n=5; headline now `None`, mixed was 315.6% |
| **S4** — three months publish `None`, never `0.0` | **CONFIRMED.** 2016-08, 2017-01, 2019-03 |
| **S5** — 21 further months carry 1–4 definition-B events | **CONFIRMED** (measured pre-change, unchanged by it) |
| **S6** — prepayment stays 0, not repaired here | **CONFIRMED.** `out_of_scope` n=0, published as a null with the gap named on the surface |

**Nothing was refuted.** The unflattering prediction (S2) is the one that matters: the split moved
the worst published month **up** by 150pp. Had every number fallen I would have suspected the
partition of having been chosen for its answer.

**R15 — five mutations, four red against their named test, null control green.** Applied to the
imported module object via a scratch pytest plugin and reverted, never to a file, because this is a
shared tree. **M1** folds `payment` back into the headline (the defect itself) — reds all seven.
**M2** defaults a missing population to `"bill"` — *the naive repair*, and the load-bearing one: it
is the one-line change that would have turned six unrelated reds green while silently readmitting
every unattributed event to definition B. **M3** publishes `0.0` for an empty population. **M4**
silences the definition note. **M5** is the null control and is green.

### One thing found while doing this, and not fixed here

`tests/tools/test_bill_correctness_addendum_defect4.py::test_billed_total_never_less_than_gross_
margin_for_any_real_customer_year` is **RED in the tree and not from this change**: `SYN-2016-014`
2016 billed £199.18 against a gross margin of £241.81. It reads only `site/state/billing_ledger.json`
and `site/data/customer_sample.json` — artefacts written by the 14:05 auto-process run, before these
edits — and imports none of the modules touched here. Recorded rather than repaired: different lane,
outside this pathspec, and a red nobody wrote down is how a pre-existing red becomes attributed to
whoever next commits near it.

## Where this is published, precisely

`monthly_ops` is served in `site/data/dashboard.json` and `site/data/world.json`. **No site page
renders it** — checked, no HTML or JS in `site/` reads `monthly_ops`. So the claim "the live site
publishes 315.6%" is true of the **served JSON artefact** and not of a rendered page, and this
document says so rather than letting a later reader discover the distinction and treat the whole
finding as overstated.
