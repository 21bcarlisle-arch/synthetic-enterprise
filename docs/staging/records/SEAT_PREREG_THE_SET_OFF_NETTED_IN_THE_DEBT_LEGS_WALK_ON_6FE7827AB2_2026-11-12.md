**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# Pre-registration: the closing set-off netted in the debt leg's own walk, replayed over 6fe7827ab2 (2026-11-12)

Written before the replay. It follows `SEAT_RESULT_THE_CLOSING_DUAL_FUEL_SET_OFF_REPLAYED_OVER_6FE7827AB2_2026-11-12.md`,
where the set-off posted beside the debt leg's case took `INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT` from
60 to 31 and `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` from 0 to 4 breached.

**The change.** `balance_settlement_from_outcomes(set_offs=)` nets each set-off against the debt leg's
outstanding bills, oldest first, after `closing_out` and before the write-off at close. The run walks twice
(the refund log needs the first walk's closing balances), the page's walk reads the set-offs from the run's
`credit_refund_log`, and the P&L cut that sat beside the case is gone.

**Input.** `/var/tmp/n29/run_setoff.json`: the 6fe7827ab2 run JSON with its refund log replayed through the
set-off door (42 set-offs, GBP 1,339.69). The refund log is unchanged by this build, so it is the right input.

**Predictions, written down now.**
1. `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` reads **0 breached** (the 4 legs OCC-6387bf64272a, SYN-2016-323,
   PROS-2016-0207, OCC-cede70b10116g close at 0). *Confidence: high.*
2. The blind row reads **between 20 and 31**. Netting in the walk lowers the debt leg's page balance at the
   refund day no differently from the posted-beside build (the set-off entry was already on the page), so most
   of the 31 stay; the 20 world-says-0 households are the two-walk class and cannot move. *Confidence: moderate.*
3. Summed over the book, the page's write-offs fall by between GBP 1,000 and GBP 1,339.69 against the control.

**Reverse.** Delete this file.
