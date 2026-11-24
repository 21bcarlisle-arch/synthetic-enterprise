**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# D48 holds no weather-aware belief about what an unread month used, so W1_14's gap cannot be defined

Found by the worker, 24 Nov 2026, on the delivery-seat item
`d48-billing-accuracy-wall-reads-unmeasured-beside-a-ledger-row`.

**What was checked.** The coupled-triad wall held W1_14 at L2 and said its gap with D48 was
"unmeasured". Origin's `docs/observability/coupled_gap_ledger.json` carries a W1_14 row (book
`8a300fa561`, measured 18 Nov). Its gap is `null`, and its note says "UNDEFINED, not unmeasured". Both
were half right. The wall is right to hold, because no gap exists. Its reason was wrong, because the
pair had been measured and found to have nothing to grade. The reason now quotes the row (this
landing, `background/coupled_triad.py`, mutation-proven in `tests/test_coupled_triad_gate.py`). The
19 Nov d48-ledger-rows landings did reach origin. W2_30's row is measured, and its coupling is closed.

**The defect left.** The company's unread-month estimate is seasonal normal and holds no weather
feed (`company/billing/unread_month_estimate.py`). So D48 has no belief about what a home used in a
cold or mild month that could be set against the world's cell weather. The knowledge page says that
published billing practice is weather-blind too, so the bill route is not the defect. What is
missing is a separate diagnostic belief, built from observables: the home's reads, the published
weather, and the AQ method's form. See
`docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md` §12, with its three
GAPs.

**Done when.** D48 carries a weather-aware estimate of used kWh for each unread month, gas first.
Where a home's history cannot separate weather from use, the estimate is `None` with its reason. The
estimate sits beside the billed estimate and never bills. The W1_14 ledger row is then re-measured
as a numeric gap against the cell weather, or it says, with a reason, why it cannot be. **Owner:**
lane D_billing_metering (the D48 atom).
