**Severity:** BLOCKING · **Lane:** C_customer_ops · **Epoch:** 4 · **Atom:** `C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv`

# C34's renewal margin is the all-in rate less the wholesale forward, so it is not a margin, and it is what put 11% of rows over the floor

**Found by** the delivery seat on 20 Oct 2026, while grading P1–P4 of
`records/SEAT_PREREG_C34_DECIDES_AT_THE_RENEWAL_ROLL_BEHIND_A_SWITCH_THAT_DEFAULTS_OFF_2026-10-19.md`
(the r4 on-arm run of the `8b6fea024` book).

## The defect

The renewal-roll caller (`18503313a`) hands C34
`monthly_margin_gbp = (unit_rate − company_fwd) × company_eac / 1000 / 12`
(`simulation/run_phase2b.py`, `observe_roll` and `observe_riding_leg`).
- `unit_rate` is the **all-in** tariff unit rate. PROS-2022-0400 rolled on 2023-12-21 at
  £252.6/MWh against a £273.5 default-tariff rate.
- `company_fwd` is `estimate_forward_price`, the company's **wholesale** forward.
- The difference therefore still carries network charges, policy costs and the supplier's own
  operating cost. It is the spread over wholesale, not what the supplier keeps.

§6.1 of `docs/market_research/next_best_action_and_cross_sell.md` chose this expression because
"the retention guard already uses" it. It calls the result "our margin", and it is not one.

## What it did to the reading

All figures are from `/var/tmp/se-c34-grade-out/on_arm.json`. They were read post hoc and were not
predicted.
- Household margin: median £29.7/month, p90 £59.6, max £448 (one 24 MWh electricity account).
- **0 of 495 rows at ≤ £30/month are advised.** 109 of 483 above £30 are advised.
- The advised rows' median hazard is 0.023/month, inside the B11 range.
- So C34's floor stopped binding because the margin is too large. The churn belief did not run hot.
- 0 households have a negative margin, including 2021–22.

P2 read 11.1% against a design line of 10%. That reading does not show the floor fails on the
company's belief. It shows the floor was fed the wrong quantity.

## What is not established

- **Whether the retention guard's own use is a defect too.** The guard at `run_phase2b.py` ~L3542
  sets `expected_margin` against `discount_pct × term revenue`. What it should weigh there is
  contribution, so the same question applies. It has not been checked.
- **What the right per-term contribution is.** The run already decomposes rates into components
  (`rate_decomposition_log`) and builds the gas term from published network and levy schedules.
  A contribution net of pass-through costs, and of cost to serve, may already exist at that roll.
  **Look for it before writing any constant** (CLAUDE.md, knowledge first).
- **Why the on-arm book is about 1.5% larger than the published book.** This is recorded in the
  prereg's grade and is unattributed.

## What would discharge it

The caller is handed a margin net of pass-through and cost to serve, from a quantity the company
already computes. §6.1 states what the margin is before it is used. The on arm is then re-read, with
the P2 band re-predicted before the run. The switch stays off until then.
