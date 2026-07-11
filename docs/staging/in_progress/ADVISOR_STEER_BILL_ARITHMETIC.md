**STATUS (2026-07-11): items 1+2 FIXED, committed, pushed (f4e4d806) --
independently re-verified before commit (2622 tests, full epistemic scan,
spot-checked C1's real regenerated data directly: 331.1 kWh now reconciles
with reads 21084.0->21415.1; C1-INV7/C1-INV11 now show WRITTEN_OFF). Historical
sweep: 664/1588 bills violated under the old logic, 239 rounding-class now 0.
Residual, registered not hidden (sanity_adjudication_ledger.json,
defect:estimated_bill_amount_on_true_consumption): the other 425 violations
are a separate, larger, pre-existing gap -- estimated bills' amounts are
computed from true consumption, not the estimate, since the billing engine
has no estimate-then-true-up model at all (confirmed: not a new epistemic
leak, meter_reads.py generates its actual/estimated narrative from
ALREADY-COMPUTED bills). Belongs to saas/bill_generator.py + the estimation
physics layer, out of scope here.

STILL OPEN: item 3 (plausibility anchors) queued alongside COLD_EYES_PROTOCOL.md.
Live pixel verification (R11) not yet done -- same as ADVISOR_STEER_THESIS_CHART.md,
blocked on confirming the Cloudflare cache-purge fix (bf777d21) actually took
effect on the next natural site/data deploy cycle.**

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