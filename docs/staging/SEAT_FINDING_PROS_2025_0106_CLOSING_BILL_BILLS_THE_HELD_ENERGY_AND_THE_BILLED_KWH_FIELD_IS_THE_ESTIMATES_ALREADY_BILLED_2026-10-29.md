**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# PROS-2025-0106's closing bill does bill the held energy; `read_true_up_billed_kwh` counts estimates already billed, not true-up billed (2026-10-29)

**Item:** `pros-2025-0106-closing-bill-held-kwh` (Lane 0). Corrects the "Open 1" and the PROS-2025-0106 bullet of
`SEAT_FINDING_HELD_ESTIMATES_ON_THREE_ELECTRIC_HOMES_ARE_BILLED_AT_THE_NEXT_ACTUAL_READ_NOT_NEVER_2026-10-29.md`, beside the claim.
Prediction filed there ("it does not [bill it], a real defect on one account") is **refuted**.

## What the fields count (`monthly_bill_assembly.py` `_resolve_catchup`, ~L378-394)
- `read_true_up_billed_kwh` = kWh the run's *earlier bills* already charged (`billed_kwh` is 0.0 for a held bill, L971).
- `read_true_up_kwh` = metered use over the run minus that = the energy this closing bill must charge.
So 0.0 is not "nothing billed in the true-up"; it is "the held run had billed nothing before this bill". The earlier
finding read the field as energy billed by the true-up, which is wrong for all three accounts.

## The trace (209c3350ab `top__bills.pkl.gz`, PROS-2025-0106 electricity)
| Bill | Basis | kWh on bill | metered kWh | £ |
|---|---|---|---|---|
| 2025-04-17..30 | estimated, held | 1,289 | 1,047 | 355.7 (not issued) |
| 2025-05-01..31 | estimated, held | 2,460 | 1,084 | 681.2 (not issued) |
| 2025-06-01..07 final | actual | 304 | | 685.2 incl. catch-up |

Closing bill: `read_true_up_kwh` 2,131 = 1,047 + 1,084 metered; `catchup_adjustment_gbp` 599.49 = true totals 290.2 + 309.3;
direction `undercharge`, barred 0.0, no back-billing cap. The held energy is billed at what the meter showed.
The "3,749 kWh" in the prior finding is the held *estimate* (1,289 + 2,460), which was never meant to be charged: it
over-read the meter by 1,618 kWh, and the 79 kWh/day estimate is exactly what the volume half of the release rule stops.

## Consequence
- No billing defect on this account; the "held energy never billed" premise is false for all three accounts.
- `billing_accuracy.py` L845 sums `read_true_up_billed_kwh` into `graded_run_billed_kwh`; its name reads as true-up
  energy billed. Whether that grade means "estimates previously billed" should be read before it is cited: not changed here.
- Carbon-panel question (true-up kWh attributed to the months it reconciles) unchanged, still open, knowledge page first (K8).
