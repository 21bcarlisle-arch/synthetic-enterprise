**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: the ledger's held opening estimates issue on the registry figure on the next fresh run

**Claim:** `work-the-held-bill-queue`
**Written BEFORE any run carrying the change.** Rule: `docs/market_research/unbilled_energy_and_revenue_assurance.md` §4f.

## What changed
`release_on_measured_rate` releases an estimate before the account's first read when the dwelling is listed
and the estimate is no higher than the registry figure's share of its own days (PC1 shape or PC2 split,
whichever is larger). The assembly stamps `registry_annual_kwh` on each estimated bill. Both doors ask the
same function, so the first read's catch-up counts a released estimate as sent.

## What is already known (not a prediction)
SYN-2016-582's four held bills equal the registry share of EAC 22,909.7 to the tenth: 1,868.9 / 2,633.2 /
2,403.2 / 2,527.4 kWh, against 1,868.9 / 2,633.2 / 2,403.2 / 2,527.4 recomputed.

## Predictions, next fresh run on the 08f267b666 inputs or later
1. The ledger's `exception_queue` holds **0** of the 9 entries on SYN-2016-582, PROS-2024-0010 and PROS-2025-0106.
   For the two PROS accounts this rests on their held months being opening estimates on a registry EAC,
   which I have not read; if either was handed no EAC, it stays held and the prediction fails there.
2. SYN-2016-582's first printed bill is 2016-12-31, and its 2017-07 actual bill carries no lump: its
   `catchup_unbilled_periods` is 0, against 4 (the £1,220.95 bill).
3. No new hold anywhere: the change only releases.
4. INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL loses its checks on these three accounts.

## Result
(written after the run, below this line)
