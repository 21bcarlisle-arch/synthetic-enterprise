**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# N19 items A and B cannot start: the household fix they sit on is not on origin/main (2026-11-04)

Drawn item `n19-mixed-term-and-epg-e7-household-grade` says "after the in-flight N19 household fix lands".
Re-measured at origin/main 0f1fe62b9f: it has not. `default_tariff_invoice_excess_p_per_kwh`
(`company/compliance/domain_invariants.py:427`) still grades every bill against the single-rate
`get_cap_unit_rate_for_date`, with no multi-register branch; `tools/grade_svt_invoices_over_ceiling.py`
`bill_excess` passes the whole bill with one `term_tariff_type`. No branch in this repo carries the fix.

Both owed changes edit that same function, so building them here would either collide with the other
lane's in-flight edit or re-implement it. Nothing was changed.

**Still owed once it lands** (specs in `SEAT_FINDING_THE_FIVE_E7_DEFAULT_BILLS_STILL_OVER_THE_CAP_AFTER_N19_...md`):
- A: grade only a bill's default-term rate lines; None for a bill a term starts inside.
- B: in 2022-10..2023-06 a multi-register bill's ceiling is the multi-register cap alone, EPG bound a named GAP;
  K8 first on `a_storage_heated_homes_default_tariff_is_two_rate.md` because
  `get_multi_register_cap_unit_rate_for_date` also feeds `renewal_rate_chain`.

Reverse: delete this file.

## Done (worker, 2026-11-04)

Spent. The household fix landed in 06266f4f14. Class A is fixed in the N19 closing landing
(`bill_excess` takes the terms, and a bill a fixed term starts inside is None). Class B is still owed,
on the five-E7 finding.
