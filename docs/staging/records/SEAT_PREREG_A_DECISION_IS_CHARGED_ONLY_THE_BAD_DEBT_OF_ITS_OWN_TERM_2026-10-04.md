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

## Correction, before grading: my first term window was wrong (2026-10-04 ~02:35)

The first two paths (`/var/tmp/se-probe-out/term_v1/`) put PROS-2016-0098's 2017-03-31
`term_bad_debt_share` at 0.49 (default) and 0.44 (61001), against a lifetime share of 0.56 and
0.50. So T1 failed as built, and the cause is the instrument, not the world.

The window ended at the leg's NEXT PROBED DECISION. This household has no probed decision
between 2017-03-31 and 2021-03-30, so its "2017 term" swept in four years of later arrears. A
2017 fix prices one year.

Fixed: the term ends at whichever comes first, one year or the next decision. The control now
holds a leg whose next decision is four years away, and ending at the next decision alone reds it.
Each row also keeps its term's bills and write-offs (`term_bills`), so the next mistake of this
kind can be re-scored offline rather than re-run.

On the lifetime basis the two v1 paths reproduce the earlier figures (capped - flat-55: -771 and
-1,139). On the faulty term basis they read -603 and -987.

**The runs that grade T1-T4 are re-launched** (`probe_term_*.json`) at base `4bf859f0b`. That base
now ALSO carries the world's debt cure (471ab8960): failed bills are paid later at Ofgem's 2016
rates, and indebted renewals fell from 56% to 47%. So the lifetime-basis figures will differ from
the earlier runs for that reason too. T1-T4 are graded on the re-launched runs, term basis against
lifetime basis on the same rows. The predictions above are unchanged.

## Grading, all four paths (2026-10-04)

`/var/tmp/se-probe-out/probe_term_*.json`, at base `4bf859f0b` (the world's debt objection and
debt cure on), with the fixed one-year term window (ddfbc61f6). Term basis and lifetime basis are
scored on the SAME rows.

| path | PROS-2016-0098 2017 term share (lifetime) | capped - flat-55, lifetime | capped - flat-55, term (SNR) | best flat level, term | capped - best, term (SNR) | term totals: capped / capped_learned / value / flat |
|---|---|---|---|---|---|---|
| default | 0.000 (0.565) | -797 | **+478 (1.63)** | 45 | **+341 (1.29)** | 3,470 / 3,406 / 3,148 / -1,666 |
| 61001 | 0.000 (0.505) | -1,139 | -3 (0.01) | 50 | -37 (0.10) | 5,433 / 5,289 / 5,220 / -1,272 |
| 61002 | 0.000 (0.565) | -1,147 | +125 (0.47) | 50 | +79 (0.31) | 2,943 / 2,883 / 2,794 / -2,336 |
| 61003 | 0.000 (0.506) | -1,101 | +40 (0.09) | 55 | +40 (0.09) | 4,914 / 4,906 / 4,633 / -1,386 |

- **T1 HELD 4/4.** The 2017 term carries no write-off at all. Its debt is later.
- **T2 HELD 4/4.** -3 to +478, all at least -300.
- **T3 HELD, 3 of 4 positive.** But read it plainly: against the best flat price IN HINDSIGHT the
  margins are +341, -37, +79 and +40, at SNR 0.1-1.3. This is parity with a slight lean positive,
  NOT a demonstrated win. I held T3 at 50/50 and it came out on the favourable side by noise-sized
  margins.
- **T4 HELD 4/4.** capped >= capped_learned > value > flat on every path.

**What this establishes about the selection question.** Once each decision is charged only what its
own term costs, per-customer choosing is at least as good as the best flat price chosen in
hindsight, on all four paths. It needs two things to get there:
- knowing the household's default (that a stayer pays at most it);
- the company's own payment history (the value rule's inputs).

It needs no hindsight. Every earlier "the choosing loses" was carried by two instrument defects, now
both fixed:
- crediting stayers with margin above the default they never pay (3475058ef);
- charging a decision with arrears accrued after its term (ddfbc61f6).

The world gaps found on the way (the debt objection and repayment of failed bills) were fixed on
published law and rates, not on these results.

**What it does not establish.** That the choosing BEATS a flat price a company could have set in
advance by a margin worth having. The comparator is the best level in hindsight, chosen on the very
rows it is scored on, so it is biased toward flat. Even so, a fourth-path SNR of 0.09 says the
difference is inside the noise. The next test of the thesis is a flat level fixed IN ADVANCE from
the company's own pre-period book, scored out of sample. Learning the price slope (capped_learned)
still adds nothing: about -10 to -140 a path.
