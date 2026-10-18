# Pre-registered: the read instruction switched on in a published run, at both access ends

*Filed 2026-10-18, before any run with the switch on exists. Direction item
`wire-the-read-instruction-into-the-published-run`. Knowledge:
`docs/market_research/read_access_and_theft_duties.md` §2.8. Earlier decomposition and its grade:
`WORKER_PREREG_WHAT_A_READ_INSTRUCTION_AT_THE_ELEVENTH_ESTIMATE_REACHES_AT_BOTH_ACCESS_ENDS_2026-10-17.md`.*

## The door this item built

- `DecisionPolicy.instruct_reads_in_billing_run` (default False, FIELD_CONSUMPTION `run_argument`).
- `simulation/run_phase4c_on_phase2b.py`. `main(policy=..., instructed_read_arm="register")`
  resolves the switch with `read_instruction_request(policy)`, which takes `CURRENT_POLICY` through
  `run_phase2b`, and hands it to `build_monthly_bills`.
  - The direction named `run_phase2b.py`, but the run's bills are assembled in
    `run_phase4c_on_phase2b`, and that is where the switch now goes.
- Two other callers rebuild bills inside the run: the in-loop DD review and the collection book's
  stop notice. They pass no policy, so they take the **standing** policy's switch, at the
  `register` arm.
  - **Switch it on by flipping `CURRENT_POLICY`, not by handing `main` an experiment policy.**
    Otherwise those two callers see bills without the instruction.
  - At `ceiling` they still bill at `register`. Their DD figures are therefore a decomposition at
    that end. None of the three quantities below reads them.

## The run to issue after the 19 Oct publish is read

The switch-on is the only change. Seed, book and code stay at the publish's commit plus the flip.

- **No-access end (the published run).** `CURRENT_POLICY.instruct_reads_in_billing_run=True`,
  then `python3 -m tools.run_phase4c_pipeline --save-json`. While
  `q6_read_visit_access_failure_rate` is null, `register` is the honest world.
- **Read end (a bound, not published).** The same policy, with
  `main(instructed_read_arm="ceiling")` called from a tool. Every instructed visit reads.
- **Instrument.** `python3 -m tools.closing_estimate_run_money --read-duty` on each output. Run it
  **without** `--instructed-read`: the bills now carry the visits themselves, so this is a re-run
  and not the 17 Oct decomposition.
- **Baseline.** The 19 Oct published run, through the same instrument. The book has changed since
  the 17 Oct grade (c136809f5: 220 homes, 73.6% dual), so predictions 3 to 6 are stated as ratios
  and bounds, not as the 17 Oct pounds.

## Predictions

1. **Off reproduces the publish.** With the switch off, the run's output is equal to the published
   run's, figure for figure. This checks that the comparison is one variable, not a finding.
2. **The no-access end moves no money.** Open closing undercharge new demand, the 21BA bar at
   closure on the crossed undercharge runs, and the on-supply catch-up write-off are each **equal
   to the penny** to the baseline. The only difference is the `read_instruction_*` keys.
   - Reason: under a null access rate the visit is the period's own read drawn again on the same
     key.
   - What the company gains at this end is a dated record of the 21B.4 step, not money.
3. **Instructions.** At either end, between 1.0 and 1.4 times the 21B.4 register's duty rows.
   **0** on prepayment.
4. **Open closing undercharge new demand at the read end** is between **0.40 and 0.65** of the
   no-access end. The 17 Oct decomposition gave 0.77 (£2,662.61 / £3,470.63).
   - Most of the extra fall is list item 1: after a visit, the real run estimates from the visit's
     read (`trailing_actual_periods`), and the decomposition did not.
   - **Refuted** if the ratio is above 0.70, which would mean re-estimating adds almost nothing, or
     below 0.30.
5. **The 21BA bar at closure on the crossed undercharge runs, at the read end,** is **under 1%** of
   the no-access end. The decomposition gave 0.14% (£5.49 / £3,929.05).
6. **The on-supply catch-up write-off on credit runs of 12+ estimates, at the read end,** is **£0**.
   - At `ceiling` every credit run is broken at its 12th bill. The write-off on prepayment runs
     equals the no-access end's.
   - Recovering what the visits true up is a transfer (M2). The 21BA bar on those true-ups is **£0**.
7. **C7's tail (list item 1).** If C7 is on the book, its open closing undercharge after its last
   visit, at the read end, is **under £200**. The decomposition gave £925.08.
   - C7 is the EV home billed on the TDCV fallback. Once a visit has read it, the estimate is
     its own use.
   - **Refuted** at £462 or more, half the decomposition's figure. That would mean the
     overstatement was not the stale estimate.

## Not predicted

- Where the truth lies between the two ends. That depends on the share of visits that fail to get
  in, a practitioner question (§7). Neither end is the answer.

## Graded

*(after the run, below this line; nothing above is to be edited)*
