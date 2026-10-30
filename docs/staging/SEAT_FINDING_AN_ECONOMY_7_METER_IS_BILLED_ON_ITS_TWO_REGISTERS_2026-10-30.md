**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A supply point settled on Profile Class 2 is billed on its Day and Night registers: the build, the blind row, and the predictions for the next fresh run (2026-10-30)

Ruling step 3's storage-heating cause
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`). K8 page:
`docs/market_research/a_storage_heated_homes_default_tariff_is_two_rate.md`, written before this build
(4c40f6b31b).

## The defect

On the 209c3350ab book, 36 of 560 electricity accounts are storage-heated. The world settles them on
PC2, "Domestic Economy 7", and the company billed all 537 of their term rows single-rate. So the same
meter was two-rate in settlement and one-rate on its bill.

## Pre-registration (written before the probe below was run)

The probe takes the 209c ledger, stamps each electricity invoice with the profile class the world
registered (PC2 for a drawn `electric_storage` home, PC1 for every other non-half-hourly electricity
account), and grades INV_E7_METER_BILLED_ON_TWO_REGISTERS on it.

- P1. Leg (a) breaches on every graded period of the storage homes, and on those only: the breaching
  accounts number 36, or fewer if some have no electricity invoice in the ledger.
- P2. Leg (b), Day/Night on PC1, breaches 0: before this build nothing printed Day or Night.
- P3. Leg (c), one-band flags, is 0 for the same reason.

## Red on the 209c book

Probe `/var/tmp/e7-probe/classes.py` (run from the book's worktree) and `/var/tmp/e7-probe/red.py`,
against `/var/tmp/wo-grade-209c/ledger.json`:

| | breached | flagged | checked |
|---|---|---|---|
| INV_E7_METER_BILLED_ON_TWO_REGISTERS | 1,638 | 0 | 27,641 periods |

- P1 held: every breach is leg (a), on 33 accounts, all of them storage homes. The other 3 storage homes
  (PROS-2016-0090, PROS-2022-0400, PROS-2025-0119) printed Peak/Off-peak, on smart ToU fixed terms,
  which the row does not grade. I did not predict that cause. The build puts them on Day/Night as well,
  because the meter's class takes precedence over the smart offer.
- P2 and P3 held: 0 and 0.

## The build (this commit)

- **Seam.** The world stamps `registered_profile_class` on the customer record, beside `metering` and
  `smart_meter` (`simulation/run_phase2b.stamp_registered_profile_class`). It is the MPAN top line's
  class, which the supplier allocates. The heating system stays in the world.
- **Company.** `tou_desk.offers_tou` returns true on every term of a PC2 meter, the default included. So
  the renewal chain grades that term on the multi-register cap. `decide_tou_offer` strikes a Day/Night pair
  with `0.58 x day + 0.42 x night` equal to the flat rate (`saas.tariff_pricing.split_flat_rate_to_economy_7`).
  The night/day ratio, 0.47, is a labelled COMPANY BELIEF anchored on the one published point (G1).
- **World.** On an E7 term, `run_hedged_term(economy_7=True)` bills the 00:30-07:30 half hours on Night
  and the rest on Day. The window is the one the storage heater charges in. The home stays settled on its
  PC2 profile and gets no demand-response shift.
- **Bill.** Day and Night are bands of `TOU_BANDS`, with register ids 4 and 5. The ledger prints the
  term's contracted pair as Day/Night at the E7 split, and the multi-register row blends Day/Night at 58/42.
- **Export and row.** Each period exports `profile_class`, and INV_E7_METER_BILLED_ON_TWO_REGISTERS
  grades it. The row's text was written by a reader given the pages, not the code. The seat's two notes
  are marked in its `gap`.

**Correction to the K8 page's choice 2, beside it.** The page said that before 2019 the pair "waits on
G2". The build prices the pair in every year. Before the cap, the pair comes off the company's own
single-rate list price at the 58/42 split. That is the same aggregate rule, so no E7 list price is
invented. The alternative was to bill a two-rate meter on one rate for three years. G2, the real E7
price level before 2019, is still open.

**Not built: the estimate half of choice 3.** An unread month on a PC2 meter is still estimated on its
total, shaped by the PC1 proxy (`unread_month_estimate.MONTHLY_SHARE_OF_ANNUAL_USE`). The estimate is then
split by the month's settled bands. A per-register estimate on PC2's shape needs PC2's monthly shares on the
company's side of the wall. Handed on as its own item.

## Predictions for the next fresh run (filed before it exists)

- N1. INV_E7_METER_BILLED_ON_TWO_REGISTERS reads **0 breaches**. Flags are possible only on one-band stubs
  (a supply start or end inside the night window).
- N2. Every storage home's electricity invoices print Day/Night, the 3 smart ToU homes above included.
- N3. INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER grades the storage homes' SVT terms from 2019 with 0 breaches,
  because the chain clamps them to the multi-register cap.
- N4. The storage homes' electricity revenue falls against 209c. Two effects push it down: the
  multi-register cap sits below the single-rate one (0.93 in Jan 2019), and their night share sits above 42% (G4).
- N5, **the K8 page's own prediction**: E2 (a)'s three summer over-estimates (PROS-2017-0336,
  PROS-2024-0010, SYN-2016-565) leave INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS. **My prediction is
  that they do NOT leave on this build.** That page's prediction rests on a per-register estimate on PC2's
  shape, and this build leaves the estimator untouched (see "Not built"). If they do leave, the cause is
  something other than the estimate shape, and that is itself a finding.
