**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# A won switch from a gas-only household is never supplied (22 Nov 2026)

**Split out of** `SEAT_FINDING_A_WON_SWITCH_IS_NEVER_PUT_ON_SUPPLY_SO_THE_SWITCHING_GSOP_HAS_NO_ACCOUNT_TO_CREDIT_2026-11-21.md`,
whose BLOCKING defect (no win was ever supplied) is fixed by f80fe39511 for electricity wins. That
finding said the gas-only wins were "already handed off"; no item carried them, so this is the item.

**What the tree does.** `run_phase2b._supply_won_switch` supplies a win from an electricity
household. A win from a gas-only household stays off supply and is published in
`won_switches_not_supplied` (`simulation/run_phase2b.py:3213`), because `register_acquired_point`
stamps every win as electricity and supplying a win as gas is not built. Its switching GSOP, if one
is owed, is refused by name in `switching_gsop_credits_refused` rather than booked bare.

**Measured** on the 20 Nov run (6a588a832f): 2 of 16 wins (SYN-2016-163_3, SYN-2016-585_3). The
book therefore books the funnel cost of these wins and never their revenue, a small understatement
of acquisition value on the gas side.

**Done means.** A gas-only win is registered on a gas point and settled, billed and collected from
its win date, and `won_switches_not_supplied` is empty on a full book (or carries only a reason
other than "gas not built").

**23 Nov 2026: where the gas build is (the seat's tick).** Direction row `supply-a-win-from-a-gas-only-household-as-gas`
said the 22 Nov landing (`longjob-land-reg-6c-erroneous-gains`, pid 134360) carried gas-only supply.
It did not. Its six frozen copies in `/tmp/seat_6c/` (18:07Z) hold reg 6C only. The gas build was
written after that, in a fork that was killed. It survives only in the salvage commit
`eccf3dc756` (tag `salvage/detached-eccf3dc75681`, 18:53Z), which carries reg 6C plus a gas branch in
`run_phase2b.py` (+82/-21, reg 6C included), `saas/customers.py`, `annual_report.py`, `test_run_phase2b.py` and
the knowledge page. The salvage was committed --no-verify and never gated, so it is a source, not a landing.
`run_phase2b.py:3231` on HEAD still refuses the win.

The 6C landing refused at 22:34Z: its commit gate ran past 3600 s. 1c9cd8195f has since cut reg 6C's
selection from 172 to 56 files, and the same bytes are re-landed once, as
`longjob-land-reg-6c-erroneous-gains-2` (log `/tmp/seat_6c/land2.log`). The gas hunks are then
carried from the salvage onto that landed reg 6C (continuation `build-gas-supply-for-a-gas-only-win`).
This item stays open until they land.

**23 Nov 2026, 04:30Z: the salvage's gas branch was red on today's origin, and why.** Merged
cleanly onto reg 6C (rebuilt on 8a52399b8), the salvage's own control errored in 832 s:
`_book_method_of('ACC-SYN-2016-163_3'): no account on the roster`. The salvage named a gas-only win
`<household>_<n>g`. `household_of` strips the `g`, so the account is `ACC-SYN-2016-163_3`, and the
roster held only `SYN-2016-163_3g`. The salvage was green at 40e31f5998 only because 7527a2e36 (a
leaver's final month opens on any closure) had not yet put every book account through the
own-book method register. The salvage's reason for the `g` was "the seed book's id convention", and
that was wrong: a drawn gas-only household is named bare (`SYN-2016-163`, commodity gas), and the `g`
names only a DUAL household's gas leg. The landed build names a gas-only win bare.
