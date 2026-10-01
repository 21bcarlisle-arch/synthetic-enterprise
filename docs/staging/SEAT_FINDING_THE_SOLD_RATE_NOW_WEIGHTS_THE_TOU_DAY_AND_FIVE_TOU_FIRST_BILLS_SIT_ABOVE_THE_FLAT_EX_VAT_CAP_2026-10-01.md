**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# The sold rate now weights the ToU day, and five ToU first bills sit above the flat ex-VAT cap

Claim `weight-the-sold-rate-over-the-tou-day`. These are results against
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_WEIGHTING_THE_SOLD_RATE_OVER_THE_TOU_DAY_MOVES_2026-10-01.md`,
which was written before the run. The parent is handed-on item 1 of
`SEAT_FINDING_THE_SVT_SEGMENT_NOW_BILLS_EX_VAT_AND_NO_FIRST_TERM_SITS_ABOVE_THE_EX_VAT_CAP_2026-10-01.md`.

## What changed

`settlement_daily.fold_to_days` now writes `unit_rate_weighted_gbp_per_mwh` on every daily row. It
is Σ(rate × kWh) / Σ kWh over the day; a day with no kWh keeps its opening rate.
`experienced_bill_shock.sold_unit_rate` reads that field first. The opening rate,
`unit_rate_gbp_per_mwh`, is the 00:00 rate, which on a ToU account is the off-peak leg. The DD books
(`run_phase4c_on_phase2b._opening_dd_by_customer`) and the experienced bill shock both reach
the fix through `sold_unit_rate`.

Controls: `test_settlement_daily::test_the_day_carries_the_rate_its_consumption_was_charged_at`
and `test_the_dd_books_open_at_the_rate_sold::test_a_tou_account_is_sold_at_its_weighted_rate_not_its_off_peak_leg`.
Two mutations were run. Reading the opening rate in `sold_unit_rate` turns the second test red.
Writing the opening rate into the fold's new field turns both red.

## Results: one run, origin/main `649112975`, old and new read in the same process

Nothing in the run reads the field while it is going, so the run is the same with or without the
change. `old` strips the field and `new` keeps it. Rows are in
`/var/tmp/se-touweight-run/rows.json`.

| prediction | result | verdict |
|---|---|---|
| P1: non-ToU accounts moved by more than 1e-9 | **0 of 93** | HOLDS |
| P2: old/flat = 0.7857 on every ToU account | 27 of 27 | HOLDS (see the correction below) |
| P3: new/flat in [0.96, 1.04], median in [0.98, 1.02] | median **0.9952**; **23 of 27** in band. The 4 outside are 0.9006, 0.9018, 0.9265 and 1.0423 | median HOLDS; per-account band **FAILS on 4** |
| P4: 8 ToU SVT accounts, sold ÷ inc-VAT cap 0.7483 → [0.91, 0.99] | 7 of 8 in [0.93, 0.98]. `PROS-2024-0199` is at 0.858 | **FAILS on 1** |
| P4b: 2–6 of those 8 above the ex-VAT cap ×1.001 | **4** (2022-0010, 2022-0097, 2025-0013, 2025-0077) | HOLDS |
| P5: DD opening ratio for the 8 goes 0.83–0.84 → [0.95, 1.03] | 7 of 8 in [0.98, 1.021]. 2024-0199 is at 0.923 | **FAILS on 1** |

Every miss has one cause. I predicted a peak share of kWh between 0.25 and 0.36. The implied
first-month peak share is 0.16 to 0.36, with a median of 0.293. The low end is summer-acquired
households (2024-06, 2024-08, 2023-07), whose first month has little evening lighting load.
For the 19 fixed ToU accounts, the median DD opening ratio moved from 0.755 to 0.874. That is the
size of the defect that was removed from the fixed book.

**Correction, beside the claim.** The first pass of the analysis took "flat" to be the first
settled day's max rate ÷ 1.5. On 7 accounts that day was a weekend, where there is no peak, so the
pass read old/flat = 1.5. The error was in my instrument, not in the data. Flat is now taken as
old ÷ (11/14). The 20 accounts that settled a weekday first gave exactly 0.7857 under both
definitions.

## Open, not built on: is a ToU first bill above the flat cap a breach?

Five first bills now read above the flat ex-VAT cap ×1.001: the four SVT accounts above, plus
`PROS-2024-0263` at +4.2% of flat. All five are households whose peak share is above the 30% the
split assumes. As I understand it, the Ofgem cap applies to multi-register and ToU tariffs at a
benchmark consumption split, not to each household's realised average rate. If so, this is
correct behaviour and the world's SVT ToU pair is lawful. I have not established that from the
commons, so it is a question for the practitioner side, not a fact. No control here reads the
realised rate against the cap (`check_sold_unit_rate_within_cap` grades the company's struck flat
rate), so nothing has gone red on it. Next step: read the cap methodology's multi-register
treatment in `docs/domain_artefact_library/` before anything is keyed to it.

## Still handed on

Item 2 of the parent: the switching reference compares across VAT bases. It is untouched here.
