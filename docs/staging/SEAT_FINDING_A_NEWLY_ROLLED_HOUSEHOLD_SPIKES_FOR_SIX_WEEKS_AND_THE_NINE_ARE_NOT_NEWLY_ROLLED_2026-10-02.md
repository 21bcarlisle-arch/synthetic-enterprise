**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `is-a-newly-rolled-default-household-as-sticky-as-svt-stock` (Lane 0 delivery)

# A newly rolled household spikes for six weeks, and the nine value-arm accounts that stopped leaving are not newly rolled

**The question.** Is a household that has just rolled onto the default at end-of-fix more mobile in
its first months than long-tenure default stock? If it is, has C1b flattered the value arm's
−9 exits since the decline rule went on (757c8cada, graded in 72b646431)?

**Premise check.** Both commits are on origin. The question was the open item those commits left,
so their landing does not spend it. The duplicate-claim note named this item's own id.

## What I found

1. **The world already separates the two populations, and by tenure.** `years_on_svt` is the
   current default stint (`svt_product.py:233`, `_svt_stint_start`), so a household that has just
   rolled runs the *recent* band from day 0. Over the value-arm book, C1b gives an expected
   0.177 a year under 3 years on the default against 0.066 a year at 3+ years, about 2.7×.
2. **"0.03–0.05 a year" in the decline finding was a units slip.** That figure is a per-cap-segment
   hazard. Corrected beside the claim.
3. **The −9 does not involve any newly rolled household.** All nine accounts sit on the default
   continuously from 2016–18 to 2025, and C8 has one stint reset, in 2020. They decline
   *conversion* offers at their anniversaries. Under C1b they faced 8.42 expected exits between
   them, over 5–9 years each. So the open question cannot flatter the −9. The 9 accounts survived
   against about 8.4 expected exits. That reads as selection on the outcome (the nine were chosen
   because they stopped leaving), and it is not a defect.
4. **The published spike is real.** Ofgem's *End of Fixed Term Communications Trial* (Sep 2019,
   RCT, ~20k) has a control arm of passive rollers. In the six weeks after the fix ended, 19% of
   them requested a tariff change: 6% to another supplier and ~14% internally. C1b gives that cohort
   2.1–2.4% over the same 42 days. The world under-prices the external move by about 3×, and it has no
   internal re-fix in the window. Written up in `svt_rates_active_passive_2016_2025.md` §4a.

## What this does NOT establish, and what is next

The trial is one supplier, one cohort and March 2019, with six weeks of follow-up and no decay
curve. It is also unclear how much of the spike the world's end-of-fix renewal roll already carries,
because that roll is the leave decision *at* the end date and the trial took only households who had
not acted by then. No constant is changed here. Before building a post-roll hazard, the next step is to
count how many genuine end-of-fix passive rolls the world produces per run, and what 6%/42 days
against 2.1% would move. That gives the size of the fidelity gap, and it is owed before any build.
