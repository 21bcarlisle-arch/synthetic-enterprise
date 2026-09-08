**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a53-the-supplier-cm-charge-reaches-nothing

# PRE-REGISTRATION: where the supplier CM charge should land, and what it will disagree with

**Written:** 2026-09-07, delivery seat, claim `a53-the-supplier-cm-charge-reaches-nothing`, BEFORE
wiring anything and BEFORE computing the company-side series.

---

## The decision, taken before the measurement so the measurement cannot flatter it

a53 offers two exits: wire `company/regulatory/capacity_market.py` to the consumer that should
have it, or delete it with the reason recorded. **I am wiring it**, and the reason is a pattern
already in the tree rather than a judgement about whether the module is nice.

`company/regulatory/statutory_obligations.py` composes the supplier's own annual statutory
return — RO, FiT levelisation and CCL — off ONE shared electricity-volume accumulator, and hands
it to `simulation/run_phase2b.py` through the `company/interfaces/` door. Its docstring states
the doctrine: *"Working out what you owe under the Renewables Obligation, the FiT levelisation
levy and the Climate Change Levy is not physics — it is a licensed supplier doing its own
statutory accounting off its own supply volumes."*

The Capacity Market supplier levy is that same sentence with a fourth noun in it. It is a
per-MWh charge on electricity supplied, it applies to every demand segment with no exemption,
and its obligation year is Apr–Mar exactly as RO's is. **CM is the missing fourth leg of a
return that already has three.**

**What this is NOT.** It is not a new consumer invented to justify the module — that is the move
a53 forbids and it is the move that produced the `0.92`. `build_statutory_obligations` exists,
runs in production, and already computes the other three levies off the accumulator CM needs.

## The thing that could make this wrong, stated first

**CM already reaches the annual report — from the SIM side.** `_section_policy_cost_breakdown`
publishes a `CM` column, fed by `years[yr]["cm_levy_gbp"]`, which
`simulation/hedged_settlement.py` accumulates per settled record from
`simulation/policy_costs.get_cm_levy_per_mwh`. So wiring a company-side CM figure puts **two CM
totals on one page**, and "two homes that disagree" is this project's most expensive recurring
shape.

I am doing it anyway, because the same is already true of all three existing legs and is
deliberate:

| Levy | SIM side (the pass-through in the settlement) | Company side (the supplier's own return) |
|---|---|---|
| RO | `years[yr].ro_levy_gbp` | RO Cost Observatory ← `roc_ledger` |
| FiT | `years[yr].fit_levy_gbp` | FiT Levelisation section ← `fit_book` |
| CCL | `years[yr].ccl_gbp` | CCL Observatory ← `ccl_ledger` |
| **CM** | `years[yr].cm_levy_gbp` | **nothing — this is a53** |

`ro_commons.py` names the rule the pair has to satisfy: *"This module holds the company's
reading; `simulation/policy_costs.py` holds the world's, and they are allowed to differ. What is
NOT allowed is the two lanes holding different LAW."* CM is currently the one levy of the five
where only the world has a reading at all.

**So the deliverable is not just a number — it is the number WITH its reconciliation against the
settlement figure printed beside it on the same page.** A second CM total published without the
delta and its cause would be the fourth-home failure, not a fix for it.

## What I predict, before computing any of it

Basis: `docs/reports/run_output_latest.json` (frozen), whose electricity volumes are ~170–230
MWh/yr, 2016–2025.

1. **The company-side series will be systematically LARGER than the SIM series in most years,
   and the cause will be the year keying, not the levy.** The company side multiplies a
   CALENDAR-year volume by the levy indexed at that same integer; the SIM side buckets each
   settled record into its Apr–Mar obligation year, so Jan–Mar of year *N* is charged at year
   *N−1*'s levy. Through a rising series that pushes the SIM figure down relative to the
   company's.

2. **The exception is any year whose levy FELL.** 2021 (4.67, down from 5.86) and 2022 (3.37,
   down from 4.67) should invert: there the SIM's Jan–Mar carry-back charges the HIGHER prior
   rate, so SIM > company. **If 2021 and 2022 do not invert, my account of the difference is
   wrong and I must not publish "obligation-year bucketing" as the cause.**

3. **The gap will be roughly a quarter of one year's step**, i.e. |Δ| ≈ 0.25 × |levy(N) −
   levy(N−1)| × volume — single-digit to low-tens of percent, not a factor.

4. **2025 will be a PUBLISHED GAP on the company side and a NUMBER on the SIM side.** Annex 9
   ends at obligation year 2024, `cm_levy_gbp_per_mwh(2025)` returns `None` and
   `compute_cm_obligation` raises; `get_cm_levy_per_mwh` carries the last known year forward and
   the frozen run already shows £647.59 for 2025. **This divergence is the correct behaviour of
   the company side and the section must say so on the page, not hide the year.** It is also the
   sharpest evidence the two readings are genuinely different readings rather than a copy.

5. **Total company-side CM cost, 2016–2024: £6,000–£8,000**, against an RO buy-out total of
   ~£40,000 on the same volumes. CM is the second-smallest of the four legs.

**Disclosed peek.** While writing this I hand-checked 2016 (169.6 MWh × £0.50 = £84.80 against
the run's £84.81) and 2017 (227.3 × £1.10 = £250.03 against £205.01). Those two are therefore not
predictions. They are what suggested claim 1; claims 2, 3, 4 and 5 are untested when this is
filed, and claim 2 is the one that can refute the account.

## What I cannot say yet

Whether the residual, after obligation-year bucketing is accounted for, is fully explained by it.
If a year's gap does not shrink to near zero once the Apr–Mar split is applied to that year's own
volumes, then something other than keying differs — a segment filter, a gas record leaking into
the electricity accumulator, or a volume basis mismatch — and that is a finding, not a rounding.

## Done means

1. `company/regulatory/capacity_market.compute_cm_obligation` has a PRODUCTION caller.
2. The figure reaches the annual report as the supplier's own statutory CM position.
3. The page states the delta against the settlement figure and its cause, and states 2025 as a
   gap with its named reason rather than as zero or as a carried-forward number.
4. A control that fails if the wiring is removed, and a control that fails if the unpublished
   year is silently filled.
