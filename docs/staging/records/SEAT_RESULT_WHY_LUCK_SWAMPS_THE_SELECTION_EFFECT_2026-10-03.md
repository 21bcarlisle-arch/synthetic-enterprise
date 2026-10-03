# Why luck swamps the selection effect: depth, width, flow, and a fourth cause

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

Director, 2026-10-03: test (a) depth, (b) width and (c) flow, chase any fourth cause, and say if
one of his is wrong. Everything below is measured from runs already on disk (the six 2025 seeds
61001-61006 at pin a322166cc, plus the depth and width cells of the depth-or-width prereg), at no
new compute. What still needs runs is named at the end.

## 1. What the residual is made of

`selection_gbp` = value arm minus level arm, per seed, summed over accounts.

| Measure (six seeds) | Value |
|---|---|
| Var(total) | 21.96M |
| Sum of per-account variances | 21.48M |
| **Design effect** | **1.02** (account level; see the correction below) |
| Sum of within-month covariances | -5.78M |
| Herfindahl effective accounts per seed | 7-10 of ~165 |
| Accounts holding half the variance | 5 |
| Largest single source | PROS-2016-0098, sd GBP 2,174 (arrears about GBP 12k) |

Accounts behave as independent draws. The noise is a few heavy accounts, not correlation between
them.

**CORRECTED 2026-10-03, beside the figure.** The account-level 1.02 is weak evidence: at six
seeds its own null band is 0.25-2.12. The sharper test is b35e8cfa4's, clustered by renewal
ANNIVERSARY DAY: 0.993 against a permutation null of 0.89-1.09 on the same six seeds. That is the
figure to quote. The conclusion is unchanged, and now rests on the test that can carry it.

## 2. (c) Flow: refuted as the cause of the noise, upheld as a fidelity defect

- Same-day clustering: Kish n_eff is 0.64-0.73 of n. The largest same-day cluster is 4.
- Outcomes: design effect 1.02 (above). Renewals that share a month do not move together.
- **But the batching was real.** The founder draw read a date-ordered stream and kept the first
  `wanted` candidates, so every drawn founder started between 1 January and 14 August 2016.
  Fixed (de903961c). In-market dates now also follow each year's published months (DESNZ QEP
  Table 2.7.1: October peak, January trough, 1.56x): founders and the trickle in b35e8cfa4,
  the campaign's prospects in af5a66f52. **CORRECTED 2026-10-03:** this line first cited
  b6ce7ce61, a second, rival seasonal mechanism this seat built in parallel with b35e8cfa4. It
  was never promoted and is withdrawn.

So "ten same-day renewals are one observation" does not hold at this scale, and spreading
acquisition is a fidelity gain more than an information gain. It could start to matter once
the book is large enough for market-wide shocks to dominate account-level ones.

## 3. The fourth cause: split survival paths

Both arms share one churn roll per renewal, with different P(stay). Where the roll falls between
them, one arm keeps the account and the other loses it, and the account's whole remaining life
lands in one arm.

| Accounts, per seed | Mean | Sd |
|---|---|---|
| Survival paths split | **-4,753** | 3,677 |
| Same path, priced differently | **+1,248** | 1,411 |
| Untouched | +68 | 95 |

The decisions themselves show selection, at SNR about 0.9 per seed. The coin on splits buries it.
How often splits happen is known exactly in advance (|P_v - P_l| per renewal), which is what
makes a control variate possible: `SEAT_PREREG_A_SPLIT_PATH_CONTROL_VARIATE_...`. A first
"multiply split accounts by |dp|" figure was biased toward zero and is withdrawn there.

## 4. (b) Width: right in spirit, and more than the director said

- The bad-debtor case is confirmed: PROS-2016-0098 is the single largest variance source, and in
  seed 61002 it alone is -5,984 of -12,726.
- **Years cannot dilute it, and neither can more seeds.** A seed re-rolls the same cast, so the
  same heavy accounts recur in every seed. Only more ACCOUNTS dilute a heavy tail. So seeds and
  width are NOT interchangeable, even though both cost about the same CPU per unit of SNR².
- **Half the width is spent on accounts that can never inform.** 86 of 165 settled accounts
  reach no priced renewal in ten years. The mechanism is identified: SVT households' yearly
  decisions go to `_svt_decisions`, not to the renewal log. The count per account is not yet
  measured. If it holds, raising the memory share buys priced decisions at about half its face
  value, unless the arm gains the SVT decision it lacks (conversion targeting, already named in
  the knowledge map as unbuilt).

## 5. (a) Depth: the only lever that grows the signal, not just cuts the noise

| Window | |mean| | sd | SNR/seed |
|---|---|---|---|
| 4y (2019) | 419 | 2,191 | 0.19 |
| 7y (2022) | 1,654 | 4,965 | 0.33 |
| 10y (2025) | 3,437 | 4,686 | 0.73 |

|mean| grows roughly as T^1.8 and sd as T^0.9, so SNR as T^0.9. Read naively, about 1.0 at 14 years
and 1.06 at 15. Three cautions:

- The six-seed SNR is uncertain by about ±0.4, so the three cells are not yet distinguishable from
  each other.
- The 10-year mean is NEGATIVE and mostly split-path, so the growing "signal" is partly the coin.
- The value arm discounted a debtor and kept him. The pricing fix (f29e6930d) is aimed at that.

So the honest landing point is: **depth grows the effect, but at six seeds the curve cannot yet
be placed.** The depth wiring past 2025 is built; its legs are queued.

**What the forward world holds, and why the cap is not modelled.** Past the record: prices from
the spine world and the scenario generators, and weather by analogue years. The domestic cap is
published through December 2026 and is HELD at that window after it. A forward cap was tested
and NOT built. The cap's published commodity allowance (Ofgem cap level model v1.31, via
`ofgem_cap_unit_rate_composition.json`) tracks the record's own SSP, lagged 105 days over a
90-day window, at correlation 0.92, but the ratio is 1.62 ± 0.42 and ranges from 0.96 to 2.71
across 24 cap periods. Ofgem prices it off forward contracts, plus shaping and imbalance, over an
observation window the knowledge map records as not established. A pass-through fitted to that
would be a number picked to fill a slot, so the cap is held, and every forward run says so in
`beyond_the_record`. The error runs one known way: when forward wholesale falls, a held cap
overstates headroom.

## 6. Signal per unit of compute, as far as it can be said

- **Estimator (control variate):** zero compute. It removes the split coin's variance in
  proportion to rho², which is not yet measured on full per-renewal data.
- **Seeds:** about 1.45 CPU-h per seed at 10 years. They reduce noise but cannot dilute a heavy
  account.
- **Width:** about 13 decisions per GB at every multiplier measured (12.3-13.7). It dilutes the
  tail, but roughly half its accounts give no decision.
- **Depth:** about 0.7 GB per year of window at the earlier pin, and CPU in proportion. It is the
  one lever that grows |mean|.

## Wrong, and corrected here

- "0.73 at 10 years" was read as a selection effect approaching measurability. It is a NEGATIVE
  effect, dominated by split paths.
- The flow cause as the director stated it does not hold at this scale; the fidelity defect under
  it did.
- An "SNR 0.43 with expected values" figure was computed and withdrawn the same hour.

## A red on origin this work ran into

Promoting this work was refused three times by a red that was origin's own. With
`test_live_population_seam` and the whole-run tests in one selection, 19 tests errored
(DwellingNotDrawn, PROS-2016-0042). It was bisected to one test that memoised the campaign under
a different book setting, and the memo was keyed on the seed alone. Fixed at the key in
e825975e8: the 76-file selection went from 19 errors to 0.

## Still to run

Width x1.25 seeds 61003-61006 (queued, pin a322166cc). Paired P/C legs for the pricing fix
(queued). Depth cells at 2025 and 2029 on the depth commit (to queue once it lands). The control
variate graded on runs carrying every renewal.
