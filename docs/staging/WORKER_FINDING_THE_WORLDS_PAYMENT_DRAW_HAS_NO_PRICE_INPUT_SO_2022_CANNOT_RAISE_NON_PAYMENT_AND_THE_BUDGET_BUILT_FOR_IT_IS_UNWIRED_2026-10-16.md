**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `the-worlds-2022-non-payment-against-the-published-arrears-record`
**Knowledge:** debt-and-collections -- `docs/market_research/gb_domestic_bill_payment_failure_and_arrears_prevalence.md` §(d), `docs/market_research/debt_and_collections.md` §2.1 (Ofgem Q4 series 2016-2025), `docs/market_research/ofgem_cap_windows.md` (the 2021-23 bills)

# The world's payment draw has no price input, so 2022 cannot raise non-payment, and the budget built for that is not wired in

*Diagnosis only. Nothing in the world changes before the 2026-10-19 publish. The fix below is
filed for a build after it, with its effect predicted before that build. A fidelity decision,
taken blind to company results.*

**The layer that falls short is the world's per-bill payment draw.** That is
`simulation/arrears_engine.payment_outcome`, reached through
`simulation/payment_behaviour_source.generate_payment_event` from
`background/live_payment_triad.py`. Its failure probability is a function of income-stress tier
alone. The bill's size, the price and the household's budget are not inputs to it. The one
mechanism written so that "a crisis-era bad-debt step-up can EMERGE from income-minus-essentials
arithmetic" is `simulation/household_budget.py` (W2_4). No payment path reads it.

## What each published series counts (say this before any figure)

| Series | Experience it counts | Unit | Clock |
|---|---|---|---|
| Ofgem "in arrears" | a bill unpaid for more than 91 days, with **no** repayment arrangement; later consumption excluded | accounts per fuel (heads) | stock at quarter end |
| Ofgem "in debt" | the same unpaid bill, now on an arrangement lasting more than 91 days | accounts per fuel | stock at quarter end |
| Ofgem average arrears / debt | the **pound balance** per account in each of the two buckets | GBP per account | stock at quarter end |
| FCA Financial Lives, "behind on electricity" | adults who say they have fallen behind (2.2% in 2020, 3.0% in 2022, 3.4% in 2024) | people, by survey | point in time |

**The definition used here** is Ofgem's: electricity, at Q4 quarter ends, accounts holding a bill
due at least 91 days earlier and still unpaid. The world has no repayment arrangements (the plan
toggles are off), so every world debtor sits in the no-arrangement bucket. The like-for-like heads
comparator is therefore **arrears + debt**, as `tools/grade_world_debt_against_ofgem.py` already
argues. The pound comparator is printed both ways: the no-plan average, and the blended average
over arrears + debt. The FCA series counts people, not accounts, so it is not used in the table.

## The mechanism, at real 2022 inputs (`/var/tmp/nonpay2022/probe_2022.py`)

Typical dual-fuel bill per year, from `ofgem_cap_windows.md`. The draw was run for 4,000
households × 12 months at each bill:

| Bill | Annual GBP | LOW fail share | MODERATE | HIGH |
|---|---|---|---|---|
| Oct 2021 cap | 1,277 | 0.0090 | 0.0351 | 0.1017 |
| Apr 2022 cap | 1,971 | 0.0090 | 0.0351 | 0.1017 |
| Oct 2022 EPG | 2,500 | 0.0090 | 0.0351 | 0.1017 |
| Oct 2022 cap, without the EPG | 3,549 | 0.0090 | 0.0351 | 0.1017 |

The four rows are identical, not merely close. The amount is carried onto the event and never
read by the draw. Tier table: LOW 0.0087, MODERATE 0.0348, HIGH 0.1015.

Stress comes from `simulation/life_events.py`: job loss, illness, a new baby, retirement and
divorce. It is read once per term at the term's end (`run_phase2b.py`, "Phase MW"). No life event
is keyed to price or year. **Nothing in 2022 can move a household's tier.**

The two other doors that could carry price are both shut:
- **DD4b**, `simulation/dd_shock_response.py`, raises failure while a materially raised direct
  debit is in force. Its strength, `dd4b_failure_uplift_after_shock`, ships at 0 (range 0.25-3.0).
  It reaches direct-debit payers only, and only those whose annual review raises the amount.
- **The hidden budget**, `simulation/household_budget.py`. Drawn over 20,000 ids, with the bill
  rise over Oct 2021 taken out of the monthly margin:

| Bill | Rise per month | Margin below zero | Margin below zero, savings under GBP 1k |
|---|---|---|---|
| Oct 2021 cap | 0 | 7.3% | 2.5% |
| Apr 2022 cap | 57.8 | 8.3% | 2.8% |
| Oct 2022 EPG | 101.9 | 9.0% | 3.0% |
| Oct 2022 cap, without the EPG | 189.3 | 10.8% | 3.6% |

So the budget responds to 2022: under the EPG, 1.7 points more households cross zero. The payment
draw cannot see it.

## The world beside the published series, by year

*Capture running: `tools.grade_world_debt_against_ofgem capture` to 2024-12-31, default dice,
wrapped to keep each bill's amount and stress (`/var/tmp/nonpay2022/capture_with_amounts.py`).
The table lands in the next commit. The predictions below were written before it existed
(`/var/tmp/nonpay2022/PREREG.md`, 2026-10-16T18:19Z).*

- **P1, heads.** The world's Q4 2022 share behind is within ±1.5 points of its Q4 2021 share.
- **P2, pounds.** World GBP per account behind at Q4 2022 is at least 1.3× Q4 2021: unpaid bills
  are bigger, so intensity rises with the bill and not with incidence.
- **P3, level.** The world's share stays above Ofgem arrears + debt (about 4.3-6.3%) in every year
  2017-2024.
- **P4, persistence.** World GBP per account behind at Q4 2023 is below 1.2× Q4 2022, because
  crisis debt clears inside the run. Ofgem's no-plan average rises 1,028 → 1,303 (×1.27).

## The fix, for a build after the publish, and its predicted effect

**Smallest mechanism.** Feed the budget into the tier. Each billed month, a credit-meter household
whose margin falls below zero because of the energy bill's rise over its own pre-shock bill, and
which holds under GBP 1k of savings, is read one tier up (LOW → MODERATE, MODERATE → HIGH) while
that holds. This adds no new probability: it reuses the tier relativities `_DD_TIER_RATIO_TO_LOW`
already holds. The crossing is defined against the household's own pre-shock bill, so households
whose margin is negative before any shock do not move. That leaves the 2016-2021 level untouched,
and the level is a separate, already-filed question (W2_38; the 2026-10-08 finding).

Knowledge page first (K8). The budget's ladder and housing draw are R10 shapes, and the
"savings under GBP 1k" cut is a design choice, not a published figure. The page must say so
before the build.

**Predicted effect on the crisis share (electricity, Q4 2022, the definition above).** Without the
savings condition, 1.7 points of households cross under the EPG. With it, 0.5 points do.
Stock share by tier is taken as proportional to the monthly fail ratio (1 : 4 : 11.7), on a world
share of about 8%, which puts LOW at about 4% and MODERATE at about 17%. That predicts **+0.1 to
+0.2 points** on the Q4 2022 share, and no more than +0.5 points with the uplift on every
crossing household. That is about a 2-6% relative rise.

Two consequences follow, and both are themselves predictions:

1. **On one seed the fix cannot be seen in heads.** The account-clustered interval is about ±3
   points wide. Grade it on pooled dice seeds, or on the budget-crossing households alone.
2. **The heads gap is not where the published crisis is.** Ofgem's arrears + debt fell from 1.755m
   (Q4 2021) to 1.656m (Q4 2022), with the EBSS and EPG in force, while the no-plan average rose
   ×1.8 from 2019 to 2024. **If P2 holds and P4 holds, the remaining crisis gap is persistence:
   world debt clears and the published debt accumulates.** In that case the next layer is the
   cure, `payment_behaviour_source.later_settlement_date` and the "repaid within 22 months"
   rule. Wiring the budget alone will not close it.

*Refutation:* if the build moves Q4 2022 heads by more than +1 point on pooled seeds, the
proportional-stock assumption is wrong, and the tier's unpaid duration differs by tier. Say so
beside this line.
