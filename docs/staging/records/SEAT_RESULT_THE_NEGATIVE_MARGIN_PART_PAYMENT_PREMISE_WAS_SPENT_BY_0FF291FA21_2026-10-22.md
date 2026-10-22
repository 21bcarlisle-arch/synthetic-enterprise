# The negative-margin part-payment premise was spent by 0ff291fa21 before the draw

*Lane 0 delivery, 2026-10-22. Drawn item: `W2_demand_negative_margin_part_payment`. It asked for
three things: count the deficit account-years that pay nothing on the demand reading, read the
knowledge layer on part payments, and decide whether to change anything.*

---

## Each step had already landed

| Step the item asked for | Where it landed |
|---|---|
| Count deficit account-years paying zero on `arm_demand_s2.json` | `0ff291fa21`: 26 of 257 pay nothing all year; replaying the rule on its own gives 28/24 against 26/22 |
| Read `household_budget_w2_4.md` on part payments before any change (K8) | `0ff291fa21`: section "2026-10-22: held money is a part payment"; also corrects the page's earlier growth formula to the level-off value (m+C)B/C |
| Decide and build | `0ff291fa21`: `HELD_MONEY_IS_A_PART_PAYMENT`, default off, with partition and mutation controls |
| Grade it | `21265c55fc` (seed 1): zero-payment account-years 24 to 0, engagement up to 91-100% (DRS about 90%), Q4 2023 pounds 580 to 366, H1-H5 held |

Seed 2 is pre-registered, and both arms are running at the time of writing:
`longjob-held-{off,on}-arm-s2` are active and their logs reach 2021-09. The pounds gap to Ofgem
widens from about 2.2x to 3.6x. Seed 1 already recorded that as the safe direction (F11).

## What this turn did

It did not do the work a second time. It released the claim and handed the seed-2 grade on as
`grade-held-money-part-payment-seed-2`, because no live continuation owned it.
