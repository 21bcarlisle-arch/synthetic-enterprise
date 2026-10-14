**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** acquisition-and-retention-economics

# On writer one's corrected basis the unit-rate margin still reads well above its target on fixed terms, so the full -5% still lands on 38% of them (2026-10-14)

**Fate (2026-10-14):** ATOM -- folds into B12_writer_one_reads_its_margin_on_the_unit_rate_so_a_renewal_floor_is_its_true_unit_cost, the same subject.

**Source:** the seed-61109 grade of
`docs/staging/records/PREREG_WRITER_ONE_READS_THE_UNIT_RATE_MARGIN_AND_THE_SAVE_TAKES_ITS_FLOOR_2026-10-14.md`
(P2's band and P3 failed). That pre-registration said in advance that a fail-high P2 is this finding.

## What was measured

Seed 61109, 400 founders, to 2025-06-07, with writer 1's unit-rate basis and the one floor (head 72ab9d113,
`/var/tmp/w1-basis-out/fix-sv-k1-61109.json`). The numbers are from `account_state`, electricity rows that
carry a portfolio position:

- **The target is right.** It is what each term's strike priced for: median 1.67% on fixed terms, all 230
  unclamped rows in [0.5%, 3%]. This is read as mean + 2 x premium where the premium is unclamped.
- **The realised rate is not.** The fixed-term median is 8.5%. By year, fixed terms read +8.5% (2016), +2-4%
  (2017-18), **+18% and +14% (2019-20)**, -1% (2021), **+14% and +15% (2023-24)**. Across all rows the median is
  0.15%, but the spread runs from -45% (p10) to +25% (p90).
- So the full -5% is still taken on 144 of 375 fixed terms (38%; it was 80% on the old basis).

## What could explain it (ranked by evidence, none tested)

I cannot yet say which of these it is.

1. **The lookback is portfolio-wide and mostly SVT.** `PORTFOLIO_PREMIUM_LOOKBACK` is the last 4 completed
   electricity terms of any tariff, and SVT rows outnumber fixed ones about 10 to 1 (4,627 against 435). An SVT
   term priced at the cap earns the cap's headroom when wholesale sits under it, as in 2019-20 and from mid-2023.
   That is real margin, but it is the default book's margin, and writer 1 compares it with the margin a FIXED
   strike priced for. The years that read high are the years the cap sat above cost. That fits, but it does not
   prove it.
2. **Hedge gains on fixed terms.** A fixed term hedged before wholesale fell earns its spread over spot. That is
   real too, and it is not something the premium should discount next year's strike for.
3. **A cost still missing from `net_margin`.** For example, opex or the cost to serve. That would bias every
   year the same way, and 2017-18 and 2021 do not read high, so this is the weakest of the three.

The wide spread is a separate effect. A mean over only 4 terms is noisy whatever the basis, and it is what
puts 707 rows at the +15% cap and 1,316 at the -5% floor.

## The one-variable run that would separate (1) from the others

Restrict the lookback to fixed terms only. A completed term already knows its tariff type at
`PortfolioMarginBook.term_ended`. Then re-run seed 61109 on F, and pre-register the prediction before
it runs: if (1) holds, the 2019-20 and 2023-24 fixed medians fall to within about 2 points of the target,
and the share at -5% falls below a quarter. Before building it, amend the knowledge page (K8) with whether a
supplier's renewal pricing should learn from its default book at all.

## Also seen, outside the pre-registration

2 of the 3 held GAS renewals on F sit on the floor. For 045 the premium is -5% on a gas margin of 13.7%.
179 has a premium of +0.03% and still sits 2.8% under its strike, so another lever cut it (most likely the
renewal cut). The prediction did not cover gas, and nobody has graded the gas book on the new basis.
