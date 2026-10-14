**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** unbilled-energy-and-revenue-assurance

# D48's row claims a billed-against-settled reconciliation, but no settled kWh is read (2026-10-14)

**Fate (2026-10-14):** ATOM -- remedy (a) taken in this commit: the twin is narrowed to reads, and K6 is named as a GAP on the row. Remedy (b), building K6 from settled volume the supplier can see, is the real capability and is drawn next week.

*From D48 Expert Hour, 2026-10-14. Adjudication: `SEAT_FINDING_D48_THE_EXPERT_HOUR_FAILS_ON_THE_CLAIM_NOT_THE_MEASURE_2026-10-14.md`. Not fixed in the turn that found it.*

D48's `real_world_twin` is "a revenue-assurance team reconciling billed kWh against settled kWh". `company/billing/billing_accuracy.py` compares bills only against the supplier's own later reads. The knowledge note lists K6, settlement versus billing (settled ≠ billed), and the module says K4-K7 "cannot arise in the run yet". The reviewer doubted this first. To a revenue-assurance lead, billed against reads is billing accuracy, and the reconciliation is billed against settled.

**Remedy, one of two:**
- (a) Narrow the twin to billing accuracy against reads, and name K6 as a GAP on the row.
- (b) Build K6 from what the supplier can see of its settled volume. `simulation/settlement_run_series.py` exists, but whether it crosses the seam as an observable is unchecked.

Option (a) is the cheaper route to L3. Option (b) is the real capability.
