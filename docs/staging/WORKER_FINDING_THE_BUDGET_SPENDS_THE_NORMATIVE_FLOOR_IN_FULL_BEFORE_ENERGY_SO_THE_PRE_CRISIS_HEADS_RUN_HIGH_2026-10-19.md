**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `W2_38_the_worlds_debt_is_graded_against_ofgems_quarterly_series` · **Claim:** `the-under-water-household-has-no-exit-so-the-budget-switch-stays-off`
**Knowledge:** debt-and-collections -- `docs/market_research/household_budget_w2_4.md`, "2026-10-19: how an under-water spell ends in the record" and "U1-U4 graded"

# The budget spends the normative floor in full before energy, so the pre-crisis heads run high and the switch stays off

**What is established.** Behind `BUDGET_DECIDES_PAYMENT`, an under-water household's spell now ends
at DWP's published 36% a year (78a36a84c). On the paired run, U1-U4 hold. The share that never
settle falls from 54% to 23%. £ per account behind at Q4 2023 is £828 (Ofgem £1,303). What is
left is a **chronic heads excess**: +1.0 to +2.7 points over the switch-off world in every Q4 from
2016 to 2021, and +3.1 at Q4 2022, at R3's refutation line.

**The most likely cause.** `margin_in_year` takes the whole JRF ex-energy basket, and the drawn
housing cost, off income *before* energy. That basket is a **normative** minimum. Citizens Advice's
negative-budget debt clients, measured on actual spending, were on average **£28 a month** short
(Sep 2023). A household below a normative floor goes without some of it. It does not stop paying
energy, a priority debt, by the full shortfall.

**GAP, and the question to research before any number.** How much of a normative shortfall shows up
as energy non-payment rather than as going without? Candidate evidence: Citizens Advice and
StepChange negative-budget distributions (actual spending), ONS OPN cost-of-living behaviours
(2022-23), Trussell *Hunger in the UK*, and JRF's destitution series. Also in scope: the housing
draw (R10, uniform £400-1,100 with no tenure link), the other half of the floor.

**Prediction for whoever builds it, written now.** A floor that compresses toward actual spending
lowers the pre-crisis ON-OFF excess below +1 point in every Q4 2016-2021, and leaves U1 at or
under 30%. If the excess stays above +1, the housing draw is the larger part. Grade it on the same
paired run (`/var/tmp/budgetpay/grade4.py`).

**Not this finding:** the company-side exits (arrangement, PPM, Fuel Direct, write-off), which are
W2_38's and `UNREACHED_EXITS`'s, and the stress drift (its own finding, 2026-10-16).
