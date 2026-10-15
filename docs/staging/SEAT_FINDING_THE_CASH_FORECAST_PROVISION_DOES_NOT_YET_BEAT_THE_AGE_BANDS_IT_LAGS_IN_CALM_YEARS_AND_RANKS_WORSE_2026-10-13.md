**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build`
**Knowledge:** none -- a grade of a built estimator; the method is in docs/market_research/bad_debt_provisioning.md

# The cash-forecast provision does not yet beat the age bands: it lags in calm years and ranks worse (2026-10-13)

**Fate (2026-10-15):** ATOM -- folds into `E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build` (re-pointed 2026-10-15; an ATOM fate names its atom).
**Fate (2026-10-13, clear-the-decks):** ATOM -- n/a P2 -- doc's own close: "do not switch the run's provision to CF"; files follow-on atom "the-cash-forecast-provision-learns-a-prior-and-the-oldest-age-before-it-is-re-graded".

The director's Order 1: measure the expected-loss provision against held-back loss on the frozen world.
The estimator is company/finance/cash_forecast_provision.py (16ba6249c, dormant). It was built
to switch the run's provision "once the grade shows it beats the matrix".

**Set-up.** Book seeds 61109-61112, 40-founder all-wins shape, frozen payment world (553d7c855), on
the head carrying the board fix (a070c2195). At each year end T from 2016 to 2022, the grader computes
point-in-time, for every account owing:
- CF, the cash-forecast expected loss;
- AB, the flat age-band provision the run publishes;
- realised loss: owed at T minus payment credits in (T, T+24 months], oldest bill first. A write-off
  credit is not cash, so a written-off bill counts as lost.
The grader wraps the run's own end-of-run reader, so nothing the run does changes. Harness, predictions
and read-out are in /var/tmp/provgrade/. The predictions were filed and hashed
(sha256 a5e75f0e...) before any run.

**Two defects were found and fixed on the way:**
- the run cleared its DD stop-notice board before reading the company's provision, so every run since
  42b2eb254 published "could not be read" (a070c2195);
- the grader's own first draft read the wrong ledger handle. That cost one run, not a result.

## The result, pooled over 4 seeds

| T | owing accounts | owed | realised loss | CF | AB | CF / realised | AB / realised |
|---|---|---|---|---|---|---|---|
| 2016 | 35 | 3,386 | 36.80 | 256.24 | 114.06 | 6.96 | 3.10 |
| 2017 | 62 | 4,251 | 212.43 | 164.27 | 399.78 | 0.77 | 1.88 |
| 2018 | 96 | 7,245 | 436.97 | 304.37 | 662.21 | 0.70 | 1.52 |
| 2019 | 116 | 8,223 | 1,019.15 | 527.30 | 1,051.76 | 0.52 | 1.03 |
| 2020 | 186 | 11,151 | 2,067.30 | 1,124.58 | 1,844.48 | 0.70 | 1.14 |
| 2021 | 267 | 19,637 | 2,564.03 | 2,390.38 | 2,934.58 | 0.93 | 1.14 |
| 2022 | 313 | 49,070 | 2,994.87 | 3,389.76 | 4,589.65 | 1.13 | 1.53 |

GBP. CF and AB are each summed over the accounts it covers; CF covered 99.1% from 2017.

| # | Prediction | Result | |
|---|---|---|---|
| Q1 | CF closer to realised than AB at 4+ of the dates | 4 of 7 | **held, barely** |
| Q2 | AB over-provisions at most dates; CF within 0.5-2.0 at most | AB over at 7 of 7; CF in range at 6 of 7 | **held** |
| Q3 | both under-provision at the 2021-22 crisis dates relative to the others | the reverse: both are nearest or above 1 there | **refuted** |
| Q4 | CF ranks "any loss" better than AB (AUC) | CF 0.964, AB 0.976, over 1,058 account-dates | **refuted** |
| Q5 | CF gives a figure for at least 90% of owing account-dates from 2017 | 99.1% (9 with no method on the register) | **held** |

## What it says

- **CF under-provisions in the calm years (0.52-0.77 in 2017-2020)** and is closest in 2021-22, once
  the book has seen accounts close. It learns its roll rates and its post-close recovery from the
  company's own book, point in time, so early on it has seen few closes to learn from. The fixture
  showed the same: no closes yet, so a near-zero provision against real losses. The 2016 date is the
  extreme, with almost no history (6.96).
- **The age bands over-provision at every date (1.03-3.10)**, as predicted: their rates are a GB
  supplier's real ones, and this world's write-offs run 5-7x low (553d7c855). Yet they **rank accounts
  slightly better** (AUC 0.976 against 0.964): an account's oldest unpaid age is a strong signal.
- Total absolute error across the seven dates is close: about GBP 2,400 for CF against 2,700 for AB.

**Recommendation: do not switch the run's provision to CF.** The pre-stated condition was that it beat
the matrix, and it does not, clearly. Two cheap improvements are worth testing next week as an atom,
graded on these same seeds:
- a prior for the roll rates until the book has resolved enough closes (a labelled range, since no GB
  roll rate is published);
- the oldest-unpaid age as a state in CF's chain, which is what AB's ranking advantage comes from.

**P2 atom: the-cash-forecast-provision-learns-a-prior-and-the-oldest-age-before-it-is-re-graded.**
The world's absolute bad-debt level stays a named gap (553d7c855), so this grade compares the two
estimators and says nothing about the absolute provision.
