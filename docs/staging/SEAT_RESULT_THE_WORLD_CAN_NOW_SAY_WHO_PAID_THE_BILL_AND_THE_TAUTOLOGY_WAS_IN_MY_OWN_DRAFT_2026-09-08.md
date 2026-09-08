**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** the-hmt-receipt-leg-and-the-household-charged-accessor-are-one-atom

# The world can now say who paid the bill, and the tautology was in my own draft

**2026-09-08. Lane 0 delivery.** Claim:
`the-hmt-receipt-leg-and-the-household-charged-accessor-are-one-atom`.

Predecessor: `docs/staging/SEAT_RESULT_BOTH_SVT_LEGS_READ_THE_COMMONS_AND_THEY_HAD_BEEN_ANSWERING_DIFFERENT_QUESTIONS_2026-09-08.md`,
"what is next", item 2. Premise re-measured at draw time: 71d3cfa16 is an ancestor of `origin/main`
and that is the PREDECESSOR landing correctly, not this work landing twice. The premise is live.

---

## What was wrong

One default-tariff electricity rate, read as two quantities. `svt_product` billed the Ofgem cap —
correct, because the Energy Price Guarantee reduced the household's bill and HM Treasury paid the
supplier the difference, so a supplier's revenue in 2022-10-01..2023-06-30 *was* the cap. Every
household-facing consumer read the same number, which is wrong by up to 33p/kWh in exactly the
three quarters that carry the most weight in the whole 2016–2025 record.

A January-2023 household's bill did not jump 30%. It was held at 34.0p. The world counted the jump
anyway, and `saas.churn_model` charged the household a churn uplift for a shock its bill never
showed it.

## What landed

The split, and the identity that closes it:

    ofgem_cap  ==  what the household paid  +  what HM Treasury paid

| date | cap (revenue) | charged | HMT receipt |
|---|---|---|---|
| 2019-01-01 | 165.2 | 165.2 | 0.0 |
| 2022-04-01 | 283.4 | 283.4 | 0.0 |
| **2022-10-01** | 518.9 | **340.0** | **178.9** |
| **2023-01-01** | 674.7 | **340.0** | **334.7** |
| **2023-04-01** | 506.0 | **340.0** | **166.0** |
| 2023-07-01 | 301.1 | 301.1 | 0.0 |
| 2028-01-01 | 263.2 | 263.2 | 0.0 |

340.0 £/MWh is the published 34.0p/kWh, in all three windows, from the commons and not from this
file. Gas moves too: receipts of 44.4 / 67.6 / 22.9.

* `simulation/price_cap_enforcement.hmt_epg_receipt_gbp_per_mwh` — the world's own receipt leg.
  Derived from the two accessors either side of it, so the identity holds by construction rather
  than by a control that would have to be believed.
* `simulation/svt_rates.get_svt_elec_rate_charged_to_household_gbp_per_mwh` — the household's
  number, over the binding instrument. Eight words long on purpose: the defect was one name
  answering two questions, and a short name would have invited it back.
* `simulation/svt_product` — every SVT segment now carries
  `household_charged_unit_rate_gbp_per_mwh` and `hmt_epg_receipt_gbp_per_mwh` beside the billed
  rate. **`unit_rate_gbp_per_mwh` did not move.** That is the half that protects revenue, and a
  control is keyed to it.
* Re-pointed at the household's number: `bill_shock_tracker` (the shock a household actually saw),
  `customer_events._price_differential_vs_market` / `_svt_position` /
  `_market_reference_gbp_per_mwh`, `run_phase2b._build_churn_basis_risk`'s `rate_vs_svt_pct`, and
  `tools/run_price_ladder._svt_position_pct` — the last because it is *reconciled against* the
  logged field, so a change here cannot be made in one file.
* `customer_events` now computes its reference **once**. The differential and the level published
  beside it were two copies of the same arithmetic that had already drifted: the differential
  substituted a non-None competitor reference, the published level fell back on a falsy one, so a
  reference of exactly 0.0 gave two answers under one name. Re-deriving a level whose only purpose
  is to equal the one that was used is the defect that function's own docstring describes.

## The EPG binds the rival too

`competitor_reference` stays anchored on the cap and is right to be — it models how a rival prices
a default tariff. But no domestic supplier could lawfully charge above the guarantee either, so the
moved reference is **clamped** at the household's rate rather than substituted for it. Outside the
scheme the ceiling is the cap and the clamp is a no-op, which is why it is one `min` and not a
second reading of the schedule. Mutation-proven: substituting instead of clamping fires a control.

## I wrote the tautology and the mutation battery found it

The first draft computed `receipt = rate - charged` inside `svt_product`. That makes
`unit_rate == charged + receipt` true by *arithmetic*, so the control asserting it could never
fail while reading as coverage of the one property this atom exists for. The battery caught it:
swapping the accessor call for the subtraction left **all fifteen controls green**.

Establishing which of the two it was, as the rule requires: it is an **equivalence**, not a missing
test. The two forms return identical values on every date — pre-2016 both legs are None, 2016–2018
both are the same pre-cap table so the difference is a true 0.0, and from 2019 the accessor *is*
that difference. No behavioural test can distinguish them. So the sixteenth control reads the
source with an AST walk and says so plainly, and `svt_product`'s comment was corrected to stop
claiming a distinction that no behaviour supports.

A second thing the printing caught before the test was written: the receipt accessor returning
`None` before 2019 (tidy, matching its two neighbours) while `svt_product` would compute 0.0 for
the same pre-cap date. One name, two numbers, in the first commit. The EPG has a definite span and
HM Treasury definitely paid nothing in 2016 — that is a fact, not a gap, so the accessor returns
0.0 there and `None` only for a fuel with no domestic cap.

## The controls, and what each fires on

`tests/simulation/test_the_hmt_receipt_leg_and_the_household_charged_rate.py`, 16 controls.
Poison round first (`test_the_epg_overlay_is_published_at_all`), because a commons that stopped
publishing the EPG overlay makes every other control here vacuously green.

| mutation | controls fired |
|---|---|
| receipt accessor returns `0.0` always | 5 |
| charged accessor points at the Ofgem cap | 4 |
| bill shock back on the revenue rate | 2 |
| `svt_product` differences instead of asking | 1 (the AST leg) |
| reference substituted instead of clamped | 1 |

The day-by-day control enumerates 2016-01-01..2029-12-31 rather than sampling: the failure being
guarded is an accessor right on the dates someone thought to test and wrong on a boundary.

## What is NOT established, said plainly

**The book was not measured, again.** The predecessor's P2 predictions are still unrefuted and this
change adds to them: bill-shock counts should FALL in 2022-10..2023-06 and churn with them, while
revenue is unchanged by construction. That is a prediction, filed before the run, and the ~8-hour
before/after is the only thing that can refute it. Nothing here should be read as having moved the
book.

**Fixed-term households are not subsidised and the EPG reached them in reality.** The scheme
applied to every domestic tariff. This world applies it only where a default-tariff rate is read,
because a fixed term here is priced by the company through `request_renewal_offer` and subsidising
it would mean reaching into a price the company struck. A real gap in the crisis quarters, named in
`hmt_epg_receipt_gbp_per_mwh`'s own docstring rather than left to be discovered from a number.

**Gas has no `charged_to_household` twin.** The same 6.8p/kWh split exists there. It is not built
because it would have no caller — every consumer re-pointed today is electricity-only — and an
accessor with no caller is an orphan that reads as coverage. Named in `svt_rates`.

**The company's register is still unwired.** `company/regulatory/epg_reconciliation_register.py`
remains without a production caller. The leg built today is the WORLD's, because `simulation/` may
not import `company/`; the register is the supplier's own audit trail of what it reclaimed, behind
the wall, and wiring it is separate work with a separate epistemic question.

## What is next, in order

1. The before/after book run against the predictions above and the predecessor's.
2. The company-side register: give `epg_reconciliation_register` a production caller from the
   company's own billing months, so the supplier can see its HMT receivable rather than only the
   world knowing about it.
3. `binding_cap_unit_rate_gbp_per_mwh_ex_vat` divides every row by 1.05 while the commons artefact
   says electricity is zero-rated 2026-10-01..2027-03-31 — carried forward from the predecessor,
   still open, still a live ex-VAT error on a published row from 2026-10-01.
