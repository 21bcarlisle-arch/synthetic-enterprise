**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: a won switch is supplied from its win (21 Nov 2026)

Follows `SEAT_FINDING_A_WON_SWITCH_IS_NEVER_PUT_ON_SUPPLY_SO_THE_SWITCHING_GSOP_HAS_NO_ACCOUNT_TO_CREDIT_2026-11-21.md`.

**The change.** `run_phase2b._supply_won_switch` puts each fresh-market win on supply from its win
date, the way `_admit_incoming_occupant` supplies an incoming occupant: the adopted weather book, the
domestic-leg set, the per-leg hedge and term state, and its own electricity renewal schedule pushed
into the term heap (opening term fixed, as `resolved_tariff_type` resolves a won record).
`_known_customers()` now includes `ACQUIRED_CUSTOMERS`, so a win is on the settlement roster, can
move, can churn, and is read by the collateral and triad passes. The two readers that already
appended `ACQUIRED_CUSTOMERS` by hand no longer do it twice.

**Named stand-in.** The won household reads its predecessor's premise data (weather, fabric trace,
property, EAC). `register_acquired_point` already clones that record, saying "it IS the same
property", while the renewal loop says a leaver "vacates nothing". The two cannot both hold. The
world draws no new household for a win, so a twin at a premise like the one lost is the nearest
thing it has. This is a fidelity GAP, not a finding that the premise transfers.

**Predictions, written before any run of the changed code.**

Short probe, `main(report_end="2017-12-31")`, fast mode:
- P1. Every id in `acquired_customers` has at least one settled record and at least one bill.
  Refuted by any won id with none.
  **Refuted, 21 Nov, first probe.** The run settled every win and then raised at
  `settlement_providers_match_eligibility`: SYN-2016-163_3 and SYN-2016-585_3 settled with no fabric
  verdict. Both predecessors are gas-only households, and `register_acquired_point` stamps every win
  electricity, so there was no electricity premise to read. The change now refuses such a win, with
  its reason, in `won_switches_not_supplied` (published). P1 is restated for the electricity wins
  only. Supplying a gas-only win as gas is handed on.

Full Phase 2b run (graded later, on the first book built at a commit carrying this change):
- P2. Every win from an electricity household carries at least one bill: 14 of the 16 on the 20 Nov
  draws, if the draws before the first 2017 win are unchanged, and the other 2 are in
  `won_switches_not_supplied`. Refuted by any electricity win with no bill. (Restated after P1's
  refutation; it said 16 of 16 before.)
- P3. The count of wins rises. A supplied win can churn, and its churn goes back to market. Central
  estimate 18 to 22 wins against 16. Refuted if 16 or fewer.
- P4. `total_net_gbp` moves by between -£15k and +£15k against 725,626 on the 20 Nov book, central
  +£4k. That is about 50 supplied customer-years at a domestic margin of about £100 a year, less the
  funnel cost of the extra market visits and any 2021-22 fixed-term losses. I cannot predict the
  sign with confidence: the hedge book and the replacement cascade both move.
- P5. The switching GSOP count stays at 0 or 1 (expected erroneous transfers 0.065 on 13
  pre-CSS wins, rising only with P3).

P4 has more than one cause moving at once (margin, acquisition spend, hedge). If it lands outside
its range, I cannot yet attribute it, and the one-variable split is the per-won-id net beside the
change in acquisition spend.

## Reg 6C, filed 22 Nov 09:55 GMT before the probe's output was read

Probe: `/tmp/seat_6c/probe.py`, 2016-2017 window, `ERRONEOUS_TRANSFER_SHARE_PRE_CSS` forced to 1.0 so
every pre-CSS win is agreed erroneous.

- **R1.** Every supplied win appears in exactly one of `erroneous_gains_returned` or
  `erroneous_gains_not_returned`; the only not-returned reason is "the return falls after the run's
  window", for wins after about late October 2017.
- **R2.** Each `returned_on` is 55 to 62 calendar days after its win (20 + 21 working days).
- **R3.** No returned win has a settled day on or after its `returned_on`.
- **R4.** Each returned win has exactly one `_leg_departures` row, dated `returned_on`.
- **R5.** Gas-only wins (refused supply) appear in neither list.

**Graded 22 Nov 10:35 GMT.** The probe ran as the test fixture `_phase2b_every_pre_css_win_erroneous`, because the
standalone script queued behind the in-flight book at box admission. All five hold, on one supplied win: R1 (1 of 1
supplied win returned; nothing not returned), R2 (60 days), R3 (last settled 17 May < 18 May), R4 (one departure row,
18 May), R5 (SYN-2016-163_3 and SYN-2016-585_3 in neither list). With one win, this shows the mechanism works. It
says nothing about rates.

## P2-P5 not yet graded (24 Nov 07:25 GMT)

The published book is still the 20 Nov run (producing commit 6a588a832f), which does not descend
from f80fe3951, so it cannot grade P2-P5. sim-runner has deferred every cycle behind the queued
s.12g rankq value test. The grade row is held until 25 Nov 09:00 and re-checks the producing
commit before reading anything.
