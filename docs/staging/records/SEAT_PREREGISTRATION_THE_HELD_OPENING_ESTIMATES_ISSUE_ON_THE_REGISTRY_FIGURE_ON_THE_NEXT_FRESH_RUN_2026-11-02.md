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

## Before the run: the PROS caveat in prediction 1, read on the desk (2 Nov, 23:50Z; NOT the grade)
No run carries 54f76662d1 yet. The 0a6391d186 run (21:22Z) predates it. Its ledger (`docs/state/billing_ledger.json`,
22:59Z) holds the same 9 entries, and at 23:35Z the shared tree's HEAD (c144971dab) did not contain the fix.
The caveat is settled on that run's inputs. Each account's first `account_state_log` `company_eac_kwh`,
put through the landed `_registry_share_kwh`:

| account | EAC | held estimates, kWh | registry shares, kWh | landed rule |
|---|---|---|---|---|
| SYN-2016-582 | 22,909.7 | 1,868.9 / 2,633.2 / 2,403.2 / 2,527.4 | 1,868.9 / 2,633.2 / 2,403.2 / 2,527.4 | release ×4 |
| PROS-2024-0010 | 22,745 | 1,518.0 / 2,385.9 / 2,509.2 | 1,518.0 / 2,386.0 / 2,509.2 | release ×3 |
| PROS-2025-0106 | 33,938 | 1,224.1 / 2,231.1 | 1,289.1 / 2,460.3 | release ×2 |

Both PROS accounts' held months are opening estimates on a registry EAC. PROS-2024-0010's estimates are that EAC's
share to 0.1 kWh, so the caveat's failure route ("handed no EAC") is not what these inputs show. One route remains.
PROS-2024-0010 also carries a later company EAC of 18,357. If the assembly stamps that figure instead of the
registration one, all three of its bills stay held: the shares come to 1,225.1 / 1,925.6 / 2,025.1. The run is what
tells these two apart, so prediction 1 stands as written.

## Result
(written after the run, below this line)

**The run graded:** `run_complete_20261103T010219Z`, Git 8b2a07d8dd. It is the first run whose stamp descends from
54f76662d1 (`git merge-base --is-ancestor` true); the run before it, 0a6391d186 (21:22Z), does not. This run's
publish is held for the weekly window, so `docs/state/billing_ledger.json` on the shared tree is still the 0a6391d186
run's (`meta.source_json` says so). I built this run's ledger to a temp path with `tools.generate_billing_ledger.generate`
at worktree HEAD 6fb4731a41. That HEAD descends from 8b2a07d8dd, and the only billing file it changes is
`statement_export.py`, which is not on the hold path. The ledger was not published.

| prediction | 0a6391d186 | 8b2a07d8dd | verdict |
|---|---|---|---|
| 1. `exception_queue` holds 0 of the 9 | 9 held | **0 held** (book-wide `held_bill_count` 0) | **holds** |
| 2. SYN-2016-582's first printed bill is 2016-12-31; its 2017-07 bill has `catchup_unbilled_periods` 0 | first 2017-04-30; 4; £1,220.95 | first **2016-12-31**; **0**; £30.65 | **holds** |
| 3. No new hold anywhere | 9 | 0; invoice count 52,828 → 52,837 (+9, the nine released) | **holds** |
| 4. INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL loses its checks on these three accounts | — | not read | **UNGRADED**: it reads the printed pages, and this run has none until the publish window (Mon 9 Nov 04:00 GMT) |

**The open route is closed.** The assembly stamped the registration figure, not the later company EAC.
PROS-2024-0010's estimates carry `registry_annual_kwh` 22,744.6, not 18,357. The other two carry 22,909.7 and 33,937.5.
All three first-read bills now reconcile with nothing unbilled: `catchup_unbilled_periods` is 0/0/0, against 4/3/2 before.

**What the release costs the household. This was not predicted; it was read after the run.** On both PROS accounts the
registry EAC over-billed the opening months, so the first actual bill is a credit:

| account | estimated kWh billed before the first read | true-up kWh | money true-up | first actual bill |
|---|---|---|---|---|
| SYN-2016-582 | 13,972.6 (7 bills) | −771.8 | −£156.82 (overcharge) | £30.65 |
| PROS-2024-0010 | 8,171.0 (4 bills) | **+1,528.1** | −£381.23 (overcharge) | −£208.17 |
| PROS-2025-0106 | 3,455.1 (2 bills) | −1,324.0 | −£489.30 (overcharge) | −£427.66 |

PROS-2024-0010's kWh and money true-ups point in opposite directions. That is not a sign error. The estimates
split day and night 48/52, which is the published PC2 split. The meter actually advanced 842 kWh day and 9,581 kWh night,
so 92% of the use was at night (storage heating). More kWh at a cheaper mix nets to a credit. This is a known limit of
estimating from a profile class, and the first read corrects it as the rule intends. No finding is filed for it.

The three registry EACs (22.7k–33.9k kWh a year on accounts labelled resi) are still what the old hold reasons named:
a probable SME-as-household mislabel. The release decides only *whether the estimate is sent*. It does not settle the
segment question, and that question is not reopened here.

**Next:** grade prediction 4 against the first printed pages built from a run that descends from 54f76662d1.
