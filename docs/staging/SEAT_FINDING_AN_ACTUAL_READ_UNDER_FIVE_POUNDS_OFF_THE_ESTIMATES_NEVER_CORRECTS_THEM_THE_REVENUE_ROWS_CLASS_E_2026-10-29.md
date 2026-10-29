**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# An actual read that finds the estimates under £5 out never corrects them: the revenue row's class (e) (2026-10-29)

**Item:** `the-fresh-run-at-9553d403b7-is-graded` (Lane 0, correctness stretch). This traces class (e) of
`INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE` in `docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml`, which said "the
mechanism is not traced". The classes were set in
`SEAT_FINDING_THREE_SMALL_EXCEPTIONS_TRACED_ON_THE_209C_BOOK_..._2026-10-29.md`.

## The cause, on the 209c3350ab book (`/var/tmp/clse/e1.py`, output `e1_209c.txt`)

All six (e) accounts follow one pattern. The bill on an actual read charges only its own month's register
advance, with the opening read set to the meter at the start of that month. When an actual read ends a run of
estimates, `monthly_bill_assembly._resolve_catchup` computes the run's error. But
`CATCHUP_MATERIALITY_THRESHOLD_GBP = 5.0` drops the correction whenever it is under £5. So the estimate error stays
on the account for good: billed kWh never meets settled kWh. Each of the 12 runs on these six accounts misses by
less than £5:

| account | runs (ex-VAT error £, kWh) | account gap |
|---|---|---|
| PROS-2016-0370 | +3.07 (+23 kWh, 4 est.) | +1.75% kWh |
| PROS-2024-0321 | +4.51 (+25 kWh, 1 est.) | +2.40% |
| SYN-2016-236 | −1.57 (−16 kWh, 4 est.) | −2.12% |
| SYN-2016-360g | +4.16, +4.00, +4.03, −4.62 | +3.79% |
| SYN-2016-395g | −2.56, +2.23, +3.93 | +1.49% |
| SYN-2016-477g | +3.09 (+131 kWh, 1 est.) | +4.74% |

The row breaches these accounts because each has small lifetime revenue (£80 to £324). On those accounts, a few
uncorrected pounds is more than the row's 1% band.

## How wide the floor reaches (same book, every bill)

| quantity | value |
|---|---|
| actual-read reconciliations of an estimate run | 6,452 |
| dropped as immaterial | **2,747** |
| accounts with a dropped correction | 754 of 1,293 |
| energy never billed or refunded (absolute) | 92,490 kWh |
| energy corrected by the 3,705 applied catch-ups (absolute) | 1,475,085 kWh |

The knowledge layer saw the same floor from the accrual side on 2026-10-05: 83% of the old "estimated billing
outstanding" was estimates closed under it (`docs/market_research/unbilled_energy_and_revenue_assurance.md`, K1 row).

## Why this is a defect, not a lawful tail

- **The floor has no source.** Its comment says "real suppliers typically do not bother billing a correction".
  It borrows the £5 from `smart_meter_reconciliation`, which models a different mechanism. Nothing in
  `docs/market_research/` or the commons establishes a materiality floor on a read-to-read bill.
- **It contradicts how a read-to-read bill works.** A bill on an actual read charges closing read minus the last
  billed read. When that last read was an estimate, the correction is built into the bill's own advance. The
  supplier never takes a separate decision about whether to bill it. The run models the correction as a separate
  line, so a floor on that line drops energy, and a read-to-read bill cannot drop energy.
- **K2:** leaving the correction off asserts it is zero. On these accounts the meter says it is not.

## What would retire it (not done here: K8, knowledge first)

1. Amend `how_a_supplier_shapes_an_estimate_for_an_unread_month.md` (or the back-billing page) to say what a bill on
   an actual read charges after estimates. Cite Ofgem SLC 21B and the Citizens Advice / Ofgem consumer guidance on
   estimated bills. Label it GAP if no published source speaks to a floor.
2. Remove the floor from `_resolve_catchup`'s application (`is_material`), keeping it at most as a display choice.
   Then every run is netted to the meter.
3. Predicted on a replay of the 209c book with the floor removed: class (e) goes to 0. The row's other classes
   do not move except (a), whose catch-ups already apply.

**Also unresolved:** (a)'s own volume side. On some accounts `catchup_kwh` does not reconcile billed to settled.
That is a separate question and is not traced here. The actual-read bill's printed opening register (the meter at the
month's start, after an estimated month) is the class already open in
`SEAT_FINDING_THE_PRINTED_REGISTER_FIX_EXPOSES_ESTIMATES_FROM_ONE_READ_AND_PRINTS_6436_OPENING_READS_NOBODY_TOOK_2026-10-28.md`.
The fix in step 2 and that finding's fix would make the same change from two sides: the bill opens on the last
billed read.
