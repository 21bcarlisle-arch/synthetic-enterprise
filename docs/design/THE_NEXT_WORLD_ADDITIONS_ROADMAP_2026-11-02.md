# The next world additions, ranked: a roadmap behind the correctness exit test (2026-11-02)

This answers Ask 2 of the 30 Oct corpus steer
(`docs/staging/advisor/done/DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`).
It also takes in the world asks of the 30 Oct reputation steer (Asks 2, 4 and 5), as that steer's done file says it would.
The director reads it as one `for_the_director` row (`the-next-world-additions-ranked-30-oct`). This note holds the detail.

**Nothing here is built before the correctness exit test holds** (`docs/direction/priority_order.yaml`,
`correctness_stretch`; `exit_met:` is not yet written). Each addition then enters as an area of the improvement loop
(`docs/design/THE_IMPROVEMENT_LOOP.md` §5). That means stage 0 knowledge, then stage 1 the world reacts at its range,
then frozen, graded and settled. The loop's first round is already chosen: a new account's first months.

## 0. What "value" means in the ranking

An addition ranks high when, without it, the supplier **cannot tell value created from value transferred** in some
decision it already makes (M2, M4). It ranks low when it only adds realism to something the supplier cannot yet act on.
"Cost" is the seat's own sizing from the modules each addition touches. It is a planning estimate, not a measurement:
S is one or two turns and one module, M is three to six turns and a new drawn trait, and L is a new channel or several
modules.

One cross-cutting rule comes from page 5 and applies to every row below. **A survey contrast enters the world as an
offset, not a multiplier, and a defaulted household responds a third to a half as much per head.** The "3-5×" figure
divides two populations, so it is not a parameter.

## 1. The ranking

| # | Addition | Evidence (grade) | What it unlocks for the supplier | Cost | What must come first |
|---|---|---|---|---|---|
| 1 | **Households react to pain points.** Today the world reacts to one pain point in seven: a price rise or renewal. A run of estimates, a refused refund and the other five draw no reaction. | Advisor pain-point packs (S/P). `SEAT_FINDING_THE_WORLD_REACTS_TO_ONE_PAIN_POINT_IN_SEVEN...` (D, a census of the code). Unbilled and estimate knowledge pages | Six areas where the supplier has nothing to optimise against today. It is the precondition for every customer-outcomes experiment, starting with the queued new-account round | M per pain point, about six | The exit test. Each area's stage-0 page with a range per reaction. The renewal-shock draw the loop design already sequences |
| 2 | **Price sensitivity as two traits:** cutting use (consumption elasticity) and shopping propensity, with shopping **anti-correlated with need** | Page 1 (D, CIM Waves 3-6). Page 2 (P): the Collective Switch trials move a 3+-year default book from 2.6-4.5% to 15-30% when hassle is removed | Renewal pricing can be graded for transfer against creation. It unblocks `PB4_engagement_separated_from_elasticity` (level 2, held by D4: SVT drift has no engagement term) | M. Touches `departure_risks.py` and the demand response; the engagement archetype already exists to carry it | The exit test. Row 1's renewal-shock draw, so the split has a reaction to scale |
| 3 | **Hassle price and per-class sensitivity** (C31, hidden, never scored: director's yes, 31 Oct) | C31 discover/frame §9 (A, with a range: DfT VTT upper, CMA forgone-saving lower). Page 2's trials, the only revealed bound | A supplier offer that saves time can finally beat a price cut. Without it the thesis loses by construction (loop design §8) | M. One drawn trait, read inside every household decision row 1 adds | Rows 1 and 2. Hassle is the price inside a reaction, so it has nothing to price until reactions exist |
| 4 | **Capability as a moderator of shopping.** Trust stays out | Page 6 (P/D): confidence separates engaged from disengaged by +31 to +34 points, trust by +2 to +6. Cross-sectional, same interview | Who an offer or advice reaches. Whether lowering hassle creates value or only moves engaged customers | S. A multiplier on row 2's shopping propensity | Row 2 |
| 5 | **Prepayment through both routes, chosen and imposed** | Page 2 §4 (P: the 2023 pause). The payment-method page (D: budgeting is the top reason prepayment payers give). Ofgem 2015 (S, via the advisor's pack and not re-read: about 60% of 2014 installs debt-driven). The current split is a GAP | Whether a prepayment offer meets a control need (created) or shifts debt risk (transferred). The world gates the imposed route today (`payment_method_dynamics.py`) but draws no chooser with a control need | S-M | The exit test's own root cause, prepayment billed as prepayment. Row 1's arrears reactions |
| 6 | **Reputation as stocks, with salience triggers** (reputation steer Ask 2): fast goodwill, slow asymmetric reputation, sector trust and the per-customer ledger. Resentment crystallises at events, not as smooth churn | Reputation calibration page (D/A): **no constant rests on a GB source**, and the reputation index and repair credit never decay (two world defects, log-only). CIM Waves 3-6 (D): trust decides **where** a move goes more than whether it happens | It lets the director's own hypothesis be tested: repeated small overcharges against fair pricing (reputation Ask 6), which is M2 directly | M | Fix the two decay defects. The GAP-R2 half-life event study, from Ofgem's satisfaction waves |
| 7 | **Life stage as a drawn factor, and life events that move needs** | Page 4 (D, CIM Wave 3): **age has the larger spread than income on all seven affordability measures**, and on switching intent (32.6 against 12.0 points). Worry plateaus to 54 and does not peak at 35-54. Tenure, young children and disability load on **different** needs | Which households to look for (M4), once the supplier can infer age from what it observes. Life events today move `income_stress` only | M-L. **Households carry no drawn age today**, only a `pensioner_present` flag (`dwelling_records.py`), so age comes first and must agree with the demand model's pensioner share | Rows 1-2, so there is behaviour for life stage to move |
| 8 | **The public review channel and the supplier's feedback loop** (reputation steer Asks 4 and 5): a Trustpilot-like platform whose organic reviews are negatively selected and invited reviews depend on supplier policy, a regulator's random panel, then ask, listen, fix and track | Reputation calibration page (P: both Trustpilot pages and Centrica AR 2018 were checked at source). Everything else is A | A gap the coupled triad scores: the supplier's reading of its reputation against the world's. Selective invitation becomes a temptation a regulator can see | L. A new channel plus a supplier lever | Row 6 |
| — | **Held: the precarity and affluence factors** | Page 4 and the framework page (D on marginals). The joint needs household-level microdata | — | — | The director's answer on the W11 row (`your-2-nov-ruling-to-register-with`). Until then, every factor is fitted from published cross-tabs |
| — | **Held: trust as a moderator, and segments** | Page 6 (trust: +2 to +6). Page 7: the six segments span 39-81% engaged, but one confidence question spans 44-74%, measured in the same interview | Nothing that capability (row 4) does not already give | — | New evidence that trust changes a revealed behaviour. The supplier should not infer segments as a step |

## 2. Why this order, and what would change it

- **Reactions come first because every other row scales a reaction.** Elasticity, hassle, capability and life stage all
  multiply something a household does. Where it does nothing, they multiply zero (K2).
- **Rows 2-4 are one family, built in sequence.** Shopping propensity is the trait. Hassle is its price. Capability
  moderates it. Building them apart would recreate the "engagement" conflation page 1 took apart.
- **Reputation ranks sixth, not first, though it carries the director's own hypothesis.** None of its constants has a GB
  source yet. A test of overcharging against fair pricing, run on unsourced decay rates, would publish the decay rate
  rather than the answer (F11). The half-life study is the cheapest move that changes that.
- **What would change the order:** if the W11 row is answered yes and the joint is fitted, life stage and precarity may
  rise above reputation. If GAP-R2 finds a short half-life, rows 6 and 8 fall further.

## 3. What this note does not do

It authorises no build. It names no constant: every range above is on its knowledge page, or is a GAP. The cost column
is a sizing, not a forecast; the first area through stage 1 is the test of it.
