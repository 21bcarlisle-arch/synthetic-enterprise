**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# The portfolio premium now reads only ended terms, and the foresight had been costing margin

Claim `bound-the-portfolio-premium-to-terms-ended-before-the-renewal`. This closes the BLOCKING
finding `done/SEAT_FINDING_THE_PORTFOLIO_PREMIUM_PRICES_A_RENEWAL_OFF_MARGINS_THAT_HAVE_NOT_HAPPENED_YET_2026-10-01.md`.

The duplicate-work note at draw time named this same id as "already held". That was this draw's own
write: claimed 18:17:10Z by the executor that launched this turn, with no rival seat running. So the
work went ahead.

## What changed

`simulation/run_phase2b.py::EndedTermMargins` holds each term's realised margin rate until the
term's last settled day falls before the reading renewal's `term_start`. Terms are then released in
END order. The company side (`portfolio_position`, `PORTFOLIO_PREMIUM_LOOKBACK`) is unchanged, so
the seam is untouched. The controls are in
`tests/simulation/test_run_phase2b_portfolio_margin_is_read_as_of_the_renewal.py`. Three mutations
were run: release everything, release on the last day itself, and release in settle order. Each one
turns a test red.

## Pre-registered (18:25Z, before either run) against what came back

Two arms, one default world each: OLD = HEAD `6f5bb8b68`, NEW = the fix. The scripts and
pre-registration are in `/var/tmp/se-pp/`.

| | Prediction | Result |
|---|---|---|
| P1 | OLD look-ahead: mean share of the last-4 entries from unended terms ≥ 0.9, median 1.0 | **Held.** Mean 0.96, median 1.0 over 3,242 renewals. Every year was 0.94–0.98. The premium was almost entirely foresight. |
| P2 | NEW share exactly 0 | **Held.** 0 of 12,751 entries came from an unended term, and 0 entries were unmatched. |
| P3 | The reading differs on ≥ 80% of priced terms | **Held.** It differs on 3,182 of 3,191 (99.7%). |
| P4 | Foresight was worth money, so NEW book net margin is LOWER | **Refuted.** NEW is **higher**: £130,085 against £122,754 (+£7,331, +6.0%). Revenue is +£4,148. |
| P5 | Renewals in 2021H2–2022H1 carry a lower uplift under NEW, and 2023 a higher one | **Refuted** in both legs. 2021H2–2022H1 uplift is HIGHER under NEW (+3.9%/+22.0% against +2.4%/+20.1%). 2023 is unchanged. The largest move is 2022H2: +13.9% against +7.5%. |

The uplift is the whole renewal chain's output over its input, not only the portfolio premium.

Net margin by term-start year (OLD → NEW):
- 2021: £51 → £854
- 2022: −£7,106 → −£1,900
- 2024: £24,811 → £25,549

The other years are within ±£430.

## What I can and cannot say

- **Said:** the look-ahead was near-total (P1), and the fix removes it (P2).
- *Measured since (2026-10-01): the story below holds. In 2021H2–2022 the reading went −0.091 → −0.235, and
  `portfolio_premium` carries £9,291 of the +£7,331, which is revenue, not value. See
  `SEAT_FINDING_THE_LOOK_AHEAD_FIXS_MARGIN_RISE_IS_THE_PORTFOLIO_PREMIUM_..._2026-10-01.md`.*
- **Cannot yet say why foresight cost margin.** Here is one story the numbers fit; it has not been
  measured. In 2022H2, OLD's last-4 were terms that had just started and settled into the 2023 price
  fall. So OLD read healthy margins and cut renewal prices early. NEW read the crisis-loss terms
  that had actually ended. Testing this needs the per-renewal premium split by the end date of the
  entries it read. It has not been run.
- **Every downstream figure on the portfolio premium moves.** The "£1,040 of £1,356" in
  `SEAT_FINDING_THE_12_PERCENT_IS_...` was measured with the look-ahead in place. It should be
  re-taken before anyone cites it. The same goes for value-arm figures from runs before this
  landing.

## The residual look-ahead (LATENT, not fixed here)

The bound is `term_start`, and it treats the last settled day as known on that day. A real supplier
knows less than that:
- it prices a renewal offer weeks before the term ends;
- it sees settlement only after the SF and RF reconciliation runs.

Both of these make the remaining window shorter than one term. Neither is sized here. The lag
should come from the published BSC settlement timetable, not be picked.

The direct check that the leak is gone is still owed. It is the 2025-only standing-charge pair
that found the leak: with the fix in place, it should move 0 renewals priced in 2024.
