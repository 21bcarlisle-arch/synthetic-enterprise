**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# Pre-registration: B11 slice 5, forward-value error split into stayers, switchers and movers

Written 2026-10-11, before the run that answers it had produced a byte, and before any split
number existed. Claim `the-forward-value-backtest-splits-switches-from-moves`. Results go in a
separate finding. This file is not edited after the run.

## The run

One full book from `tools.run_annual_report` at `3f1ebfac3` (origin/main at draw). It has
`c4fb2931b` as an ancestor, so the reducer forwards `home_move_outs`, and home moves are ON
(`docs/design/curriculum/home_moves_activation.json`, director 2026-10-08). B7 slice 7 (a mover's
final bill drawn from the world's exit model) was still inside its landing gate when the run
started, so this run does not have it. Slice 7 moves a mover's final-bill collection. It does not
move `per_customer_monthly.net_gbp`, which is what B11 forecasts, so the run uses `c4fb2931b`.

The latest sim-runner run (`cf8706023`, 2026-10-10 01:32Z) predates `c4fb2931b` and carries no
register. That was checked by the key's presence alone, and no split was computed from it.

## What is measured

At the default cut (2020) with the deviation window read from the wholesale record (at cut 2020
that is the fit window), every graded account is put in exactly one held-back outcome:

- **stayer**: supplied through the book's last month;
- **mover**: its last supplied month is its move-out month (slice 4's rule);
- **switcher**: any other departure.

For each outcome: the paired absolute margin error and the paired departure Brier score,
per-customer minus flat, with the 95% interval. A negative difference favours per-customer.
The verdict reads "cannot tell" when the interval straddles zero. Also the mean signed margin
error (forecast minus realised) per outcome, for each rule.

## Predictions

- **P1 (reachability, the B7 test).** The run carries a register and the held-back window counts
  at least one move. If not, B7 stays on `blocked_on`.
- **P2.** Movers are between 10% and 50% of held-back departures. Basis: EHS move-in rates run
  from about 3%/yr for owners to more than 15%/yr for private renters, over a 4.5-year window,
  competing with switching.
- **P3 (stayers, Brier): per-customer better.** The interval is wholly below zero. A stayer's
  Brier is p², and the contract-year hazard gives a long-tenured account a lower p than its
  segment's average.
- **P4 (switchers, Brier): flat better, or cannot tell with a positive point estimate.** It is
  the same mechanism read from the other side: (1-p)² punishes the lower p.
- **P5 (movers, Brier): cannot tell, with a positive point estimate.** A move does not follow
  supply tenure, so the per-customer rule's tenure shape is noise for movers, and it lowers p
  for the long-tenured.
- **P6 (margin error).** Cannot tell in all three outcomes. No sign is predicted, because I have
  no basis for one.
- **P7 (margin bias).** For both rules, the movers' mean signed error is above the stayers'. The
  forecast weights an all-cause survival that a mover leaves early, and a stayer outlives it.

## What would change what we do

- P1 holds: B7 comes off B11's `blocked_on`.
- P5 refuted the other way (per-customer better on movers): the tenure shape carries move
  information, which is a surprise worth chasing.
- Per-customer losing on movers by more than on switchers: the all-cause survival needs a
  separate move term. That would be the next slice, and it would come before any retention use.
