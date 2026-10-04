# A decision is charged only the bad debt of its own term

**Pre-registered 2026-10-04 by the delivery seat, before any run of the change below.**

## Why

Graded in `SEAT_PREREG_THE_CHOICE_IS_HELD_DOWN_BY_A_TOO_STEEP_BELIEF_..._2026-10-03.md`: with the
default known, the value rule's whole remaining loss to the best flat price in hindsight is one
decision, PROS-2016-0098 on 2017-03-31.
- **What the company could see.** Its own ledger shows one GBP 487 miss in November 2016, cured
  by December, and nothing open at the decision.
- **What the probe scored.** It charged that decision with the household's LIFETIME bad-debt
  share (about 0.5), which is arrears it ran up years later.

A one-term score charging a decision with debt from terms it did not price is the probe's own
defect. It is the director's fairness point about whole-book comparisons, recurring inside the
per-decision instrument.

## The change

`tools/decision_probe.term_bad_debt_shares` sets each row's `term_bad_debt_share`: GBP written off
on this leg's bills whose period ends inside the term the decision priced, over the GBP billed on
those bills. The write-offs come from the world's `arrears_engine.balance_write_offs`. The term
runs from the decision to the leg's next probed decision, or a year where there is none.

`expected_term_margin_gbp` scores on it by default (`bad_debt_basis="term"`). The lifetime share
remains, under `bad_debt_basis="lifetime"`, so the two can be compared on one run.

## Predictions, written before the run

Four 2025 paths, origin with the world's debt objection on (bf0d37c2f). Scored on the term basis,
compared with the lifetime basis on the same rows:

- **T1.** PROS-2016-0098's 2017-03-31 `term_bad_debt_share` is below 0.05 on every path. Its
  lifetime share is about 0.5.
- **T2.** capped - flat-55 on the term basis is at least -300 on every path. On the lifetime
  basis it was -165 to -1,098. I.e. at parity once the unforeseeable debt is not charged.
- **T3.** capped - flat-55 on the term basis is POSITIVE on at least 2 of 4 paths. This is the
  first time a per-customer rule would beat the best flat price in hindsight. I hold it at 50/50
  and say so.
- **T4.** Ranking of rules by total term-basis margin: capped >= capped_learned > value > flat on
  every path.

Runs: `/var/tmp/se-probe-out/probe_term_*.json`, launched 2026-10-04 ~01:40 at base
`3adca7a2b`. The base has the world's debt objection and does NOT yet have the world's debt cure,
which is still landing. So the objection's reach is still the upper bound.

## Grading

Below, after the runs.
