**Knowledge:** the-customer-needs-framework

# What the payment-behaviour score counts beside the arrears state, and why the renewal price reads only the state (2026-11-25)

Written for `WORKER_FINDING_THE_VALUE_ARM_RENEWAL_PRICE_STILL_READS_NO_PAYMENT_BEHAVIOUR_SCORE_2026-11-25.md`.
The question was whether the value arm's renewal price (`company/pricing/value_based_renewal.py`)
should also read `behaviour_score`, given that it already reads `arrears_state`. Both signals come
from the supplier's own ledger.

## 1. What each signal counts, for the same account

| | `arrears_state` | `behaviour_score` |
|---|---|---|
| Built by | `churn_model.arrears_state_from_collections` | `payment_behaviour_analytics.score_payment_history` |
| Reads | undisputed overdue £ on the collections snapshot at `term_start`, and the previous snapshot | every payment event on the account, all time: ON_TIME / LATE / DD_FAILED / MISSED |
| Is | a **stock and its direction** *now*: no_debt, in_arrears_steady, worsening, unknown | a **flow history**: on-time share and unpaid share over the account's whole life, cut into EXCELLENT..CRITICAL |
| Moves churn through | `arrears_hazard_ratio`, a ratio on the segment base rate, applied inside the price-dependent rate model | `CHURN_UPLIFT_BY_SCORE` (+0.10 POOR, +0.20 CRITICAL, absolute), added to a separate estimate that is combined with the rate model by `max()` |
| Source of the size | Ofgem CIM wave 6, Table 56 (C4, n=3,458): 4.2% no debt, 6.8% "getting harder", 5.3% population, six-month switching | **none**. Set in Phase MY (2026-07-02, `NEXT_PHASE_MY.md`) with no citation |

**The score does carry information the state does not.** An account that missed bills and has since
cleared them is `no_debt` and POOR. An account that pays late but always pays before the snapshot is
`no_debt` with a lower on-time share. A new account seen once in arrears is `unknown` by state, but
its score reads its first bills. So the two do not simply re-count each other.

**Nothing published sizes that extra information against switching.** Table 56 and the CIM waves 3–6
tables read in `revealed_switching_by_age_and_arrears_and_the_needs_tables_in_cim_waves_4_6_2026-11-02.md`
cut switching by *current* arrears only, and R4 there finds behind-on-bills makes no starred
difference to compared-not-switched. We have found no published source for switching by payment
*history* given arrears state. **GAP:** the switching propensity of a household with past but cleared
missed payments, compared with a household with none, has not been established.

## 2. What forwarding the score would do to the price (measured, not argued)

`decide_margin(arm=VALUE_BASED)`, resi electricity, EAC 3,100 kWh, tenure 3, cost to serve £60,
fixed revenue £180, three expected periods. Each cell is the chosen margin in £/MWh. The columns
are the score: None / EXCELLENT / FAIR / POOR / CRITICAL.

| year, base→current £/MWh | state | margin by score |
|---|---|---|
| 2017, 120→150 | no_debt | 30.5 / 30.5 / 34.8 / 45.2 / **60.2** |
| 2017 | worsening | 28.0 / 28.0 / 28.0 / 38.0 / **53.0** |
| 2019, 130→160 | no_debt | 30.2 / 27.2 / 35.0 / 46.2 / **62.5** |
| 2021, 180→200 | no_debt | 64.8 / 64.8 / 64.8 / 73.5 / **93.8** |
| 2023, 280→300 | any | flat across scores (rate term dominates) |
| 2024, 200→240 | any | flat across scores |

**A worse payment record raises the margin, by up to £30/MWh.** The mechanism is the `max()`: the
score's estimate does not move with price, so for small moves it becomes a floor on the believed
leave probability (CRITICAL: 0.183 at a 0–5% move, where the rate model says 0.129). Across that
floor the arm sees no loss from pricing up, so it prices up until the rate model rises above the
floor. The arm is not responding to anything it believes about how these households react to price.
It is exploiting a term that has no price response, which is the same shape as the 0.95 asymptote
`churn_model.py` documents.

## 3. The choice the design makes, and why

**The renewal price does not read the score.** `DISTRESS_SCORES` and `DISTRESS_BILL_SHOCKS`, which
nothing read, are deleted. Three reasons, strongest first:

1. **It would load cost onto households in difficulty.** The director's principle (2026-09-23,
   restated 2026-10-08) is that cost is not loaded onto a group because it is less able or less
   likely to push back. Section 2 is that move, in its plainest form.
2. **It is transfer, not creation (M2).** The added margin comes from a believed inability to
   leave, not from any value delivered.
3. **The size is unsourced.** The state's effect is sourced from Table 56. The score's +0.10/+0.20
   is not. Stacking it would make an invented number move a price.

The price still hears payment history where a source supports it. The state moves the hazard, and
`unpaid_bills_by_age`, `credit_risk` and the learned default belief move the bad-debt cost.

**What would reopen this:** a published or own-book estimate of switching by payment history
*given* arrears state, entering the rate model as a ratio (as the state does), not as a price-flat
floor. The churn desk's belief in `run_phase2b` still reads the score. That belief is reported and
guards retention, and it sets no price.

`decide_margin` still accepts `behaviour_score`
(`test_the_payment_observables_the_director_named_are_actually_present` asserts that it does), and
no production caller passes it. The control
`tests/company/pricing/test_the_renewal_price_does_not_read_the_payment_score.py` fails if the
chain's adapter starts forwarding it.
