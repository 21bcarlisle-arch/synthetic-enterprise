**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv`

# The median renewal reads negative because the contribution charges the cost the standing charge recovers, and credits none of it

**Found by** the delivery seat on 20 Oct 2026. It grades
`records/SEAT_PREREG_WHY_THE_MEDIAN_RENEWAL_CONTRIBUTES_MINUS_3_91_A_MONTH_2026-10-20.md`
(`84a8cfd08`, landed before the probe returned).

**The answer.**
- The term that makes the median negative is **cost to serve, £55 a year per leg**
  (`saas/cost_to_serve.FIXED_OVERHEAD_GBP_PER_YEAR["resi"]`). The contribution charges it in full
  and credits **none** of the standing charge.
- Ofgem's cap is built for the standing charge to recover that cost. In v1.31 the nil-consumption
  allowance (which *is* the standing charge) carries £41.6/yr of operating cost on electricity and
  £68.1/yr on gas (April 2019, direct debit).
- The book credits that revenue on every settled record, which is why the book is positive while
  85% of legs read negative.
- **The C34 concern's premise ("our side is negative") is ours, not the world's.** The world's
  costs are recovered: 478 of 487 legs price at or above `term_cost_floor`, and the other 9 miss it
  by at most £5/MWh.

## What each number counts

| | `term_contribution_per_year` (`company/crm/renewal_advice_desk.py`) | Book net margin (`cd1f976c7` clock) |
|---|---|---|
| Unit | One leg, one year of the coming term, at the renewal rate | Every leg, whole window |
| Revenue | Unit rate × company EAC | Unit revenue **+ the standing charge on every record** (`hedged_settlement.py:180`, `gas_settlement.py:187`) |
| Netted | `term_cost_floor` (forward + capital + locked policy + locked network) × EAC; £55 per leg | Wholesale, pass-through, cost to serve, provisioned bad debt |
| Standing charge | Not credited. §6.1 of `next_best_action_and_cross_sell.md` calls it a GAP | Credited in full |
| Bad debt | Not netted | Netted (provisioned) |

Dividing one by the other is not a ratio of anything. They count different revenue.

## The run

- The probe is the C34 on arm from `b8c665948` (both switches on), at `origin/main` `768f41ed1`,
  full window, default seed. It wraps the desk's inputs and changes no code.
- Output: `/var/tmp/se-med391-out/on_arm_legs.json`. Reader: `/var/tmp/se-med391-out/analyse.py`.
  The reader asserts that it reproduces every leg's recorded contribution to 1e-6.
- On this base the median is **−£3.66/month** over 321 decision states, with 85.0% negative and 4
  of 963 rows advised. At `c61d8b608` it was −£3.91, 85.8% and 4 of 972. The base moved by the
  household-budget commit; the shape did not.

Per leg, medians, £ a year. Margin = (rate − `term_cost_floor`) × EAC. Contribution = margin − cost
to serve. The last two columns are not in the quantity.

**By renewal year**

| Year | Legs | MWh | Revenue | Wholesale | Pass-through | Capital | Margin over floor | Cost to serve | Contribution | £/month | Negative | Rate − floor £/MWh | Legs below floor | Bad debt (not netted) | Standing charge (not credited) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2016 | 3 | 3.2 | 261 | 146 | 109 | 1.8 | 8.7 | 55 | −46.3 | −3.86 | 100% | 2.72 | 0 | 5 | 70 |
| 2017 | 99 | 4.0 | 350 | 147 | 175 | 1.8 | 21.0 | 55 | −34.0 | −2.83 | 91% | 4.60 | 0 | 7 | 69 |
| 2018 | 91 | 5.5 | 438 | 224 | 173 | 2.8 | 20.3 | 55 | −34.7 | −2.89 | 93% | 3.54 | 1 | 9 | 73 |
| 2019 | 74 | 4.7 | 344 | 135 | 160 | 1.7 | 21.4 | 55 | −33.6 | −2.80 | 95% | 4.47 | 0 | 7 | 81 |
| 2020 | 66 | 3.7 | 289 | 92 | 162 | 1.1 | 11.0 | 55 | −44.0 | −3.66 | 100% | 1.98 | 0 | 6 | 84 |
| 2021 | 59 | 4.0 | 528 | 301 | 185 | 3.7 | 32.0 | 55 | −23.0 | −1.92 | 69% | 9.63 | 5 | 21 | 86 |
| 2023 | 30 | 3.6 | 685 | 283 | 290 | 10.5 | 106.3 | 55 | +51.3 | +4.27 | 7% | 35.52 | 0 | 34 | 183 |
| 2024 | 42 | 4.6 | 617 | 299 | 256 | 11.1 | 23.6 | 55 | −31.4 | −2.62 | 81% | 3.69 | 0 | 19 | 208 |
| 2025 | 23 | 3.1 | 563 | 281 | 236 | 10.4 | 2.1 | 55 | −52.9 | −4.40 | 100% | 0.68 | 3 | 11 | 187 |

**By fuel**

| Fuel | Legs | MWh | Revenue | Wholesale | Pass-through | Capital | Margin over floor | Cost to serve | Contribution | £/month | Negative | Rate − floor £/MWh | Legs below floor | Bad debt (not netted) | Standing charge (not credited) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Electricity | 306 | 2.8 | 451 | 170 | 245 | 2.3 | 17.0 | 55 | −38.0 | −3.17 | 87% | 5.99 | 9 | 10 | 81 |
| Gas | 181 | 10.1 | 353 | 212 | 111 | 2.7 | 24.7 | 55 | −30.3 | −2.53 | 82% | 2.40 | 0 | 8 | 92 |
| **All** | 487 | 4.3 | 416 | 184 | 185 | 2.5 | 20.3 | 55 | −34.7 | −2.89 | 85% | 3.80 | 9 | 9 | 84 |

There are no 2022 rows. On this book no resi fixed leg rolled with a recorded floor in 2022.

## Graded against the pre-registration

- **P1 is refuted.** Rate − `term_cost_floor` is exactly £2.00/MWh on only 1 of 487 legs. It is
  above £2.00 on 359; the 5th to 95th percentile runs £0.26 to £35.0, and rolls (median £5.61) sit
  wider than riding gas legs (£2.42).
  - The rate the desk is handed is therefore not the bare strike at the recorded forward. Some
    uplift or ceiling has moved it.
  - **I cannot yet say which.** The probe records the rate and the floor, not the route between
    them. That attribution is owed (see below) and does not change the answer, because even the
    median £3.80/MWh × 4.3 MWh is £20 a year, against £55.
- **P2 holds in its claim and not in its number.** The term is the £55 per leg. The margin over
  the floor is a median £20 a year, against the £6–25 band, but it is not 2 × EAC (P1). No leg in
  the book is at or above the 27.5 MWh break-even that P2 named; that break-even assumed P1.
- **P3 holds.** 9 of 487 legs (1.8%) price below `term_cost_floor`: all electricity rolls, in 2018,
  2021 and 2025.
  - Every one is at or above `own_cost_floor` (forward + locked costs, **no capital**).
  - That is the competitive ceiling's own floor (`company/pricing/renewal_desk.py:_apply_competitive_ceiling`).
  - So two floors disagree by the capital term. The ceiling may clamp under the floor that writer
    one's discount stops at, by at most £4.82/MWh here. The mismatch is real and small, and it is
    not what makes the median negative.
- **P4 is half right.** 28 of the 73 non-negative legs are 2023 renewals, where the median rate
  sits £35.5/MWh over the floor. The positive legs are also larger (median 7.9 MWh against 4.3).
- **P5 holds.** Bad debt is not in the quantity. Netting the year's resi provision takes the median
  from −£2.89 to −£3.61 a month per leg, and the share negative from 85% to 90%.

## What credits the cost to serve, measured

The standing charge's own components come from Ofgem's cap level model v1.31,
`ElecSingle_Other_*` / `Gas_Other_*`, GB mean of regions, read 20 Oct 2026 off the cached workbook
that `tools/ofgem_cap_unit_rate_composition.py` reads.

| Opex allowance OC, £/yr | Elec at benchmark | Elec at nil (= standing charge) | Gas at benchmark | Gas at nil |
|---|---|---|---|---|
| Apr–Sep 2019 | 82.0 | 41.6 | 93.5 | 68.1 |
| Oct–Dec 2023 | 99.1 | 50.2 | 112.9 | 82.2 |
| Apr–Jun 2025 | 103.5 | 52.4 | 117.9 | 85.9 |

The nil column also carries EBIT of £1.5–4.6, headroom of £0.9–1.6 and SMNCC. The regulator
builds roughly half of electricity opex, and about three-quarters of gas opex, into the standing
charge.

Per leg, £/month, on this run:

| Contribution | Median | Negative | Median with bad debt netted | Negative |
|---|---|---|---|---|
| As built (no standing charge) | −2.89 | 85% | −3.61 | 90% |
| + the standing charge's opex allowance (Apr 2019 nil OC) | +1.47 | 26% | +0.46 | 42% |
| + the whole standing charge (upper bound; double-counts the post-2023 network residual) | +4.23 | 0% | +3.44 | 1% |

**Corrected beside the claim.** The knowledge page (§6.1) says how much of the standing charge a
supplier keeps "is not decomposed anywhere in the commons". The cap model already in the commons
decomposes it by component, and the opex row is the one this quantity needs. "Leaving it out
errs against our own thesis (F11)" is true of the level. It is not safe in this use, because
it puts 85% of households below zero, and every renewal decision that reads the quantity then
advises nobody, for a reason unrelated to the household.

## What to fix, and only this

1. **K8 first.** Amend `next_best_action_and_cross_sell.md` §6.1 and the knowledge map's
   "Cap formula" row with the nil-column decomposition above (OC, E and H by fuel and period).
2. **Then credit, per leg, the standing charge's opex allowance (nil OC) for that fuel and cap
   period** in `term_contribution_per_year`. Credit no network or SMNCC, which keeps the post-2023
   residual out.
   - This matches cost to serve against the revenue line the regulator builds to recover it.
   - It is a change to a rule C34, the save offer and the retention guard all read, so the
     retention guard's offers move. It needs its own pre-registration on the r4 book before
     landing.
   - The C34 switch stays off until it is regraded.

Owed and not filed as a fix, because the evidence does not name them as the cause:
- Attribute the rate − floor spread above £2/MWh (P1's refutation): a rate-route probe on one roll.
- Reconcile the two floors (the ceiling's `own_cost_floor` against `term_cost_floor`).
