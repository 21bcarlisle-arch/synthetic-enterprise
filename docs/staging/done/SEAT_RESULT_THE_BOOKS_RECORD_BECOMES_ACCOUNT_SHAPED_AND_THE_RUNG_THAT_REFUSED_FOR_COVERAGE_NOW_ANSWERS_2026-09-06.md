**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** measurements_that_mirror

# RESULT: the book's record becomes account-shaped, and the rung that refused for want of coverage now answers — on a narrower question than the one that refused

**Measured 2026-09-06 BST in the shared tree. Claim
`the-companys-record-of-its-own-book-is-event-shaped-not-account-shaped`. World run
`python3 -m tools.run_phase4c_pipeline --save-json`, whose run output is
run_output_3851553ec_20260906T175529Z.json under docs/reports/ — gitignored by
.gitignore line 40 and therefore ON DISK ONLY, never landed; 2,098 account-state rows, 264 supply
points, 177 households. Instrument `python3 -m tools.r1_inference_ceiling`, artefact
r1_inference_ceiling.json under docs/observability/. Page
`python3 -m tools.generate_delivery_page`, feed delivery.json under site/data/, rendered through
site/_live_harness.mjs. Log at /tmp/acct_state_run.log.**

## What the drawn item said, and the half of it that turned out to be wrong

The item's diagnosis was right and its prediction was not, and both are worth keeping beside each
other.

**Right:** nine of eleven observables were carried by a minority of households because
`run_phase2b` only wrote them inside renewal branches. It named this a bookkeeping defect rather
than a modelling one, and it was.

**Wrong:** it predicted `dynamic_pricing_log`'s 149 was the ceiling on coverage and that fixing the
bookkeeping would give the pair rung 149 households. It gave it 164 — and **the pair rung still
refused, at 69, for the same stated reason.** The item could not have known why, because nothing in
the instrument could say it.

## What landed

`simulation/run_phase2b.py` now writes `account_state_log`: one row per (supply point, term) for
**every term the book serves** — gas legs, first terms, and indexed products that have no renewal
decision at all. It sits in the term loop's own body, above the renewal gate and above
`settled_fold.add(...)`, so the EAC estimate keeps the point-in-time blindfold the renewal estimate
has. `saas/reporting/annual_report.py::extract_report_data` forwards it; that block is opt-in and a
log it does not name is silently empty in every published run, which is the defect its own Phase-QP
note records.

Coverage, on the same book, before → after:

| observable | scope | before | after |
|---|---|---:|---:|
| `unit_rate_gbp_per_mwh` | account state | 100 | **164** |
| `company_eac_kwh` | account state | 69 | **164** |
| `svt_rate_gbp_per_mwh` | account state | 69 | **146** |
| `rate_vs_svt_pct` | account state | 69 | **146** |
| `mean_recent_margin_rate` | account state | 149 | 149 |
| `portfolio_premium_pct` | account state | 149 | 149 |
| `company_churn_estimate` | decision only | 69 | 69 |
| `resentment_score` | decision only | 69 | 69 |
| `perceived_bill_saving_gbp` | decision only | 69 | 69 |
| `expected_term_margin_gbp` | decision only | 56 | 56 |
| `discount_pct` | decision only | 35 | 35 |

The two SVT-derived fields stop at 146 and not 164 because 18 households are gas-only and
`simulation/svt_rates` publishes no gas cap. Writing the electricity cap against a gas leg's rate
would produce a spread between two commodities — a number, and not a quantity — so the gap is
recorded rather than filled.

**Four decision-only fields were deliberately NOT lifted.** `OBSERVABLE_FIELD_SCOPE` in the
instrument declares, per field, which side it is on and why: `estimate_renewal_churn` takes an old
rate *and* a new one, so it exists at a renewal and nowhere else; the journey register only advances
in a renewal window; a discount does not exist without an offer. Manufacturing values for the
accounts that never reached those decisions would have invented the coverage rather than recorded
it, and would have passed a test that only checked `company_eac_kwh` went up.

## The thing the fix made VISIBLE rather than fixed, which is the actual finding

With the book at 164 and four fields lifted, **the pair rung still refuses, at 69 households.**

The winner of the 45-way search is `perceived_bill_saving_gbp × portfolio_premium_pct`. The first of
those is decision-only. **A rung's household count is set by the pair that WON**, so one
renewal-scoped field in the grid drags the whole rung back to the renewing subset however large the
book gets. Its refusal still reads *"it would take about 72 households carrying both fields of a
pair, against the 69 it has"* — which a reader takes as *the book is too small*. The book is 164.

I could not have predicted this before running it, and did not: the prediction on record was 149
households on the pair rung. Filed here beside the result rather than revised.

## The rung the whole book carries

`whole_book_pair_rung` runs the same search restricted to the fields declared `account_state` — six
of them, 15 pairs, **164 households**. The restriction is on *scope*, declared in the source before
this rung existed, not on outcome; both rungs are published side by side for the same reason the
uncorrected null still is.

    best pair       unit_rate_gbp_per_mwh x company_eac_kwh   held-out -0.1502
    corrected       does NOT clear,  p = 0.8458  (alpha 0.05)
    magnitude       +0.1492   band -0.2230 to +0.3345 over 40/40 partitions

**`honest_point_estimate.estimate` returns a number on this rung** — the drawn item's own done-when
— and the number does not clear its selection-corrected null. It is a **narrower** question than
the rung that refuses, not a better answer to the same one: it asks what can be recovered from what
the company holds about *every* account, which is the only version a book-wide programme can act
on. The all-candidate rung answers a real question about a smaller population with no route to the
rest of the book.

**What this does NOT do for A49.** It does not discharge the three BLOCKING findings that end
"coverage, unchanged". Two of them are about the all-candidate rung, which still refuses, and the
reason has moved from *coverage* to *the selection lands on a renewal-only field* — a different
defect needing a different decision, and one the seat should take deliberately rather than have
this lane take by narrowing a rung. What has changed is that the sentence is now checkable: the
instrument publishes which record carried each observable and whether its coverage is a defect or
the truth about the field.

## Controls, each poison-proven

Five landed; every one was run against the defect it names and observed to fail, then restored and
observed to pass.

| control | poison | fired |
|---|---|---|
| `test_the_worlds_account_record_is_written_outside_the_renewal_gate` | indent the append under a renewal gate | yes |
| `test_the_account_shaped_record_lifts_account_state_coverage_and_leaves_a_decision_field_alone` | `field_provenance` skips `account_state_log` | yes |
| `test_every_observable_declares_a_scope_and_the_declaration_is_a_partition` | collapse the scope column to one value | yes |
| `test_the_whole_book_rung_drops_the_decision_only_fields_and_keeps_the_rest` | filter keeps everything; undeclared field treated as whole-book | yes (both) |
| `test_the_whole_book_rung_REACHES_THE_READER_beside_the_refusal_it_explains` | render function defined and never called; rung renders without naming what it dropped | yes (both) |

The first is asserted on the AST because reaching it any other way costs a decade run, and it
carries its own reachability leg: the renewal-gated shape must still exist in `run_phase2b.py`, or
the assertion is not discriminating between two shapes and would pass on anything. The last is
asserted on text a browser rendered, not on markup — this panel is composed at runtime, so a grep
of `index.html` is blind to whether any of it reached a reader.

## Known-red at landing, and not mine

`tests/architecture/test_static_quality_ratchet.py::test_ruff_baseline_matches_frozen_census` and
`::test_ruff_no_stale_baseline_entries` are red in the shared tree: I001 reads 1318 against a frozen
1319. The working tree is BETTER than the baseline by one, from another lane's in-place edit. My
four files carry the same I001 count at HEAD as in the working tree (0, 0, 15, 0), so none of it is
mine, and banking the ratchet would wedge every lane. Landed by `tools.surgical_land`, which gates
the tree the commit would create.

## What I would take next, if the seat agrees

The all-candidate rung's refusal should stop being keyed to household count and start being keyed to
**what the selection landed on** — "the winner is a decision-only field, so this rung can only ever
carry the accounts that reached that decision" is the true sentence, and it is a different remedy
from more households. That is a change to a published refusal on a gated figure, so it belongs to
whoever holds A49, not to this lane.
