**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# Held bills are not "never released": the three accounts' energy is billed at the next actual read (2026-10-29)

**Item:** `held-bills-are-never-released` (Lane 0). Corrects section 3 of
`SEAT_FINDING_THREE_SMALL_EXCEPTIONS_TRACED_ON_THE_209C_BOOK_...2026-10-29.md`, beside the claim.

## What was measured (209c3350ab `top__bills.pkl.gz`, `validate_bills`)
7 held bills, all `resi`, all `billing_basis == "estimated"`, all `premise_council_tax_listed == True`.
`release_confirmed_domestic` refuses them **by design**: the listing refutes the mislabel half, but an estimate
over the ceiling stays held until an actual read replaces it (its docstring, the volume half). Nothing is
broken in the release code; a listing cannot vouch for a volume.

## The premise "nothing ever works the queue" is wrong
The held month is reconciled as billed nothing (back_billing_and_liability.md s.12), so the next actual-read bill
carries it as `read_true_up_billed_kwh`; the same correction was made for held credit bills in `fccc0a41c7`.
- PROS-2024-0010: held Jan-Feb 2024 (and Mar-Apr estimated); the 2024-05 actual bill carries 3,925 kWh billed true-up.
- SYN-2016-582: held Dec 2016-Feb 2017; the 2017-07 actual bill carries 7,156 kWh billed true-up.
- PROS-2025-0106: held Apr-May 2025; the account's final bill (2025-06-07, actual) shows `read_true_up_billed_kwh` 0.0
  against `read_true_up_kwh` 2,131. **Not established** whether the held 3,749 kWh is billed there; this is the one
  account the premise might still be true of.

## So what the carbon breach is
Not an unworked queue. The carbon panel sums issued bills' `total_consumption_kwh` by year, which excludes the
true-up energy, while the usage panel sums settlement consumption. The held months' kWh sit in the true-up field of
a later bill (and in 2017 for the 2016 account). That is a panel-definition question (does "used" include true-up
kWh, and in which year), not a billing-ledger release. The CO1 reading in the earlier finding stands: both panels
should count energy used.

## Decision
No code change. Making the exception queue release these estimates would issue a month's estimate at 79 kWh/day
with no read behind it, the very defect the volume half exists to stop (five 2025-06 stub estimates).

## Open (one-variable next step)
1. PROS-2025-0106: does its closing bill carry the 3,749 held kWh anywhere? Prediction: it does not (0.0 billed), a
   real defect on one account; trace `release_at_closing_read` / the catch-up on a final bill.
2. Carbon panel: attribute true-up kWh to the months it reconciles. Knowledge page first (K8).
