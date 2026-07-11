**STATUS (2026-07-11): both defects root-caused, fix delegated (in flight).
Item 1: tools/generate_billing_ledger.py independently rounds opening_read_kwh/
closing_read_kwh/consumption_kwh from the same source instead of deriving
displayed usage from the already-rounded displayed reads -- classic compounding-
rounding bug, matches the observed 331.1 vs 331.2 kWh exactly. Item 2:
site/customers/index.html's per-bill "Outstanding" sum counts any non-"PAID"
invoice status as unpaid, but tools/generate_invoice_data.py's _STATUS_MAP has
no "written_off" mapping -- a written-off invoice's status never gets updated,
so it's double-counted as still-outstanding even though the household ledger
correctly zeroes it via total_written_off_gross_gbp. Item 3 (plausibility
anchors) queued alongside COLD_EYES_PROTOCOL.md, same non-interrupting class.**

---

# ADVISOR_STEER — bill arithmetic + same-page truth (Tier 2/Tier 1 mix)

**Staged:** 2026-07-11 by advisor from the director's live portal review
(C1, elec, July 2020 bill). Two verified-on-screen defects; fold into the
standing-charge fix already in flight (same component, bill_generator).

## 1. Reads-vs-usage mismatch (Tier 1: bill accuracy)
Displayed reads 21084.0 -> 21415.1 = 331.1 kWh; billed usage line = 331.2
kWh. A bill's reads and billed quantity must reconcile EXACTLY. Root-cause:
display-rounding after computing from unrounded values, or usage sourced
separately from the printed reads (provenance defect — worse). Fix at class
level (R10): new Tier-1 pre-bill invariant — billed_kwh == closing_read -
opening_read at full precision, display rounding applied consistently to
both; violating bills are HELD to the exception queue like any Tier-1. Sweep
ALL historical rendered bills for this class and report the count.

## 2. Settled-vs-outstanding contradiction (same-page truth)
Header: "Account settled to zero (net of £157 written off)" alongside
"Outstanding: £157". Mutually exclusive states on one screen. If written
off: outstanding = £0 and the write-off is its own labelled line (with date
and reason — it is a real credit-loss event, P&L-relevant). Fix the display
logic AND add this to the page-internal consistency invariant class from
COLD_EYES (figures/states on one page must reconcile).

## 3. Feed the plausibility anchors
12.77p/kWh (elec, Jul 2020) reads low vs cap-era ~17p — may be legitimate
(fixed tariff) but must be explainable ON the surface (tariff name/passport).
Add unit-rate-by-year sane ranges to the COLD_EYES plausibility anchor seed.

## DoD
Both fixes live + pixel-verified on C1's actual portal pages; the new
pre-bill invariant demonstrably holding a synthetic violating bill; historical
sweep count reported; anchors seeded; one digest line. Coordinate with the
SC-double-charge fix so bill_generator is touched once, not twice.