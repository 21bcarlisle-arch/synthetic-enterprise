# Pre-registration: compare pricing rules decision by decision, on one book

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

Written 2026-10-03 while the first full-decade probe run is in flight, before its result exists.

## The question (director, 2026-10-03)

"Once one arm loses a customer the other keeps, they hold different books, and by year ten
they're comparing different populations." Is a per-decision comparison fairer, and is it cheaper?
For each customer at each renewal, what would each rule have earned on THAT customer at THAT
moment?

## The instrument

`tools/decision_probe.py` runs the engine once on the control path (the reference book). At every
renewal it asks each rule for its offer from the same company observables, and asks the world for
its true P(stay) at each offer, holding the roll, market and household fixed. Each rule's expected
earnings on that decision are then:

    P(stay at its offer) x [margin x annual volume - true bad-debt share x bill (+ continuation)]

with no coin. The bad-debt share is the arrears engine's emergent write-offs and provisions over
revenue billed. Continuation (the account's remaining reference-path renewals at the flat margin) is
scored as a range, never alone. Noise is estimated by bootstrapping ACCOUNTS within the run.

The 2017 dry run (26 decisions, 24 accounts) gave value - flat = +3,067 with bad debt, sd 626,
SNR 4.9. That was a test of the instrument, not a result.

## Predictions for the full decade (default book seed)

- **D1. Noise.** The per-decision SNR, bootstrapped over accounts, is at least 3x the book-level
  per-seed SNR at ten years (0.73), so at least 2.2.
- **D2. Sign before bad debt.** Margin only, the value rule earns more than flat per decision,
  because it raises price where P(stay) falls little.
- **D3. Bad debt bites where the book-level loss came from.** Adding the true bad-debt share
  lowers the value rule's advantage, and lowers it most on the accounts with the largest shares.
  PROS-2016-0098's decisions turn negative or shrink.
- **D4. Compute.** The decade probe peaks under 6 GB and takes under 1.5 CPU-h for one book,
  against 11-13 GB and about 3 CPU-h for a two-seed three-arm A/B leg. Each further rule costs
  only offline scoring.
- **D5. What it cannot say.** One book's bootstrap measures sampling over its accounts, not
  over books. Between-book variation needs book seeds, and is not claimed here.

- **D6 (added before the decade run with level rules, after the 2017 window showed value-flat
  +3,087 but value-level -501 +/- 508).** Over the decade, the value rule's lead over FLAT is
  mostly LEVEL: against a flat rule at its own median margin (the book-level A/B's selection
  contrast), the per-decision difference is near zero, |SNR| < 2. If it is clearly positive,
  the decisions do select and the book-level negative was the books; if clearly negative, the
  value rule selects badly.

Graded beneath, as `## Result`, with each prediction marked held or refuted.

## Result (graded 2026-10-03, default book seed, full window, one run)

82 priced decisions on 44 accounts. Cost: 23 min wall, 0.35 CPU-h, 5.1 GB peak, including 30
level rules re-asked at every decision. A two-seed three-arm A/B leg costs about 3.3 CPU-h and
11-13 GB.

| Contrast | Margin only | + true bad debt | + continuation |
|---|---|---|---|
| value - flat | +7,399 (SNR 6.9) | +7,250 (sd 1,060, SNR 6.8) | +7,443 (SNR 6.9) |
| value - level at value's median (51.35 GBP/MWh) | -1,661 (SNR 2.4) | **-2,668 (sd 1,202, SNR 2.2)** | -2,709 (SNR 2.2) |

Level sweep (value minus a uniform level, with bad debt): at 20, +2,196; at 30, +140; at 40,
-1,530; at 50, -2,668; at 60, -3,171. The largest single selection loss is PROS-2016-0098 (-994).

- **D1, HELD.** Per-decision SNR is 6.8 against flat and 2.2 against level, against a book-level
  per-seed 0.73. One caution: they are not the same estimand. The bootstrap measures sampling
  over this book's accounts; the book-level sd is between seeds.
- **D2, HELD.** Margin only, value beats flat by 7,399.
- **D3, HELD, and sharper than predicted.** Bad debt barely moves value-flat (-150), but it moves
  value-level by about -1,000 (-1,661 to -2,668). It bites in the SELECTION contrast: the value
  rule's per-customer prices keep proportionally more of the bad payers than a uniform level does.
  PROS-2016-0098 is the largest single term.
- **D4, HELD.** 0.35 CPU-h and 5.1 GB against about 3.3 CPU-h and 11-13 GB, and every extra rule
  is free.
- **D5, STANDS as the limit.** One book. Between-book variation needs book seeds, at about 20
  min each.
- **D6, REFUTED.** Predicted near zero, |SNR| < 2. Measured: clearly negative, SNR 2.2. The
  value rule's whole lead over flat is level, and its choosing loses money against charging
  everyone its own median.

**What this means.** The fairer, cheaper measure says the noise problem was mostly the
measure. On the same customers at the same moments, the value rule's selection is measurably
negative, and bad payers are where it loses. That is a finding about the pricing rule (its churn
belief and its value function), not about compute or years. It is now testable rule by rule at
minutes per book.

## Correction, 2026-10-03 (later the same day)

**Every margin above was scored on the OFFER, and a stayer offered a fix above its default does not
pay it.**

The world's decline-and-stay rule is live (`DECLINE_A_FIX_ABOVE_THE_DEFAULT`). A household that
stays refuses any fix above its default and is billed the default. The probe credited the offer.

The value rule priced above the default on 68-74 of 77-82 decisions per path; the level rule at the
value median did so on 59-67. Re-scored offline with the world's own rule, value - level on the
four 2025 paths:

| path | was | now (SNR) |
|---|---|---|
| default | -2,668 | -1,184 (1.25) |
| 61001 | -3,046 | -1,482 (1.69) |
| 61002 | -2,146 | -1,019 (1.43) |
| 61003 | -2,827 | -1,560 (1.79) |

value - flat roughly halves (e.g. 7,250 -> 3,663).

**The direction of every conclusion here holds; the sizes do not.** The probe now records
`stayer_pays_gbp_per_mwh` and scores on it. See
`SEAT_PREREG_A_STAYER_PAYS_THE_DEFAULT_SO_THE_VALUE_RULE_SHOULD_NOT_PRICE_ABOVE_IT_2026-10-03.md`.
