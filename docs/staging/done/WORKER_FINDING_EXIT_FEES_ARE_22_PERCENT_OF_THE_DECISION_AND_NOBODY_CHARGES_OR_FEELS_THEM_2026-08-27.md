# Exit fees are 22% of the switching decision, and in this world nobody charges one or feels one

**Date:** 2026-08-27. **Author:** the delivery seat. **Status:** DISCOVERY. No code changed.
**Occasion:** the evidence gathered for the price-sensitivity recalibration named exit fees as the
third-largest driver of switching, so the world's treatment of them was checked. It has none.

## The evidence

Ofgem / BMG Research, *Understanding Consumers' Energy Tariff Choices* (conjoint, n = 3,235 GB bill
payers, census-representative, fieldwork Mar–Apr 2024, published Jul 2025):

| feature | importance |
|---|---|
| annual savings | 41% |
| customer service rating | 32% |
| **exit fees** | **22%** |
| tariff type | 5% |

It is not a marginal effect. Holding everything else optimal, the presence of an exit fee drops the
probability of choosing a deal from **90% to 61%**, and *"the most significant drop occurs when
transitioning from no exit fee to a minimal £50 fee, highlighting the psychological barrier that
even a small fee introduces."* Ofgem price the trade directly: **"A £38 reduction in price savings
is equivalent to a £50 increase in exit fee."**

And there is a named minority with a genuinely different decision rule: **"17% of consumers
disproportionately prioritise exit fees over other factors when deciding to switch"** — identified
from *individual* feature-importance scores, i.e. real within-population structure rather than a
subgroup mean. Ofgem note that group skews younger, more financially vulnerable, more likely to be
behind on bills, and — *"crucially"* — to understand exit fees least, which they attribute to
ambiguity aversion.

## What this world does with them: three layers, all inert

1. **`company/billing/exit_fee.py` — implemented and never called.** It knows the Ofgem licence
   condition (no fixed-term exit fee inside 42 days of the end date) and carries per-fuel
   pence-per-kWh rates. `calculate_exit_fee` has **no production caller anywhere** — only its own
   test file. Verified by import as well as by symbol: nothing outside `tests/` imports
   `company.billing.exit_fee`.

2. **`company/crm/renewal_notice_register.py` — discloses £0.00, always.** `exit_fee_gbp: float`
   defaults to `0.0` and is only ever passed through, never computed from the calculator sitting
   one directory away. Every renewal notice this company issues therefore tells the customer their
   exit fee is nothing.

3. **The world has no response to them at all.** No module under `simulation/` or `sim/` reads an
   exit fee. A household here cannot be deterred by one, cannot be locked in by one, and cannot be
   the kind of customer Ofgem measured 17% of.

## Why this is the same defect twice, on opposite sides of the wall

Earlier today the three drawn attitude axes (`price_sensitivity`, `green_stance`, `channel_pref`)
were found drawn, coverage-tested, wall-guarded, mutation-tested against leaks — and read by no live
module (`WHAT_A_HOUSEHOLD_DECIDES_ON.md`). This is that shape again on the **company** side: a
capability built to a real regulatory specification, wired to nothing, with a data field beside it
permanently reading zero.

The consistent tell in both cases is a **default that is indistinguishable from the real answer**.
`exit_fee_gbp = 0.0` looks exactly like a lawfully waived fee; a drawn trait that nothing consumes
looks exactly like a trait that does not matter. Neither state can announce itself.

## Why it is worth building, and why it is cheap

- **It is the largest unmodelled decision weight available.** 22%, against a price axis whose
  honest per-household spread turned out to be only 1.26x between-group.
- **It creates lock-in, which this world has no mechanism for.** Every retention question here is
  currently "will they leave?"; an exit fee makes it "can they afford to leave *yet*?", which is a
  different and more realistic shape, and it interacts with the 42-day licence window already coded.
- **It is genuinely observable to the supplier** — the company sets the fee and knows its own
  contract terms — so unlike the hidden attitude axes it can support real inference. It is also
  something the company can *choose*, which makes it a decision surface and not just world physics.
- **The 17% segment is a published, individually-measured minority**, not a subgroup mean — the kind
  of within-population structure the director asked for and the price axis could not supply.
- **Three of the four pieces already exist**: the calculator, the licence window, and the disclosure
  field. What is missing is the wiring and a world-side response.

## What it would take

A world-side response to a disclosed exit fee at the renewal decision, calibrated to Ofgem's own
curve (90% → 61% across £0 → £300, the steepest step at the first £50) and to the £38-per-£50
exchange rate against savings; the company actually populating `exit_fee_gbp` from
`calculate_exit_fee`; and — for the 17% — a per-household fee-aversion draw, which on this evidence
should be **correlated with low understanding**, not independent of it, since that is what Ofgem
found and what would make it discoverable through observed behaviour.

**Not built here.** Filed as a roadmap item, per the standing instruction that where the world is
too simple that is a discovery rather than a defect to fix in place. Sequenced in
`WHAT_A_HOUSEHOLD_DECIDES_ON.md`, ahead of the trade-off work, because it is better evidenced and
cheaper than anything else remaining.

---

*Evidence: Ofgem/BMG 2024 as cited; absence verified by import-graph and symbol search over the live
tree, excluding `tests/` and `.claude/worktrees/`. R13: the response curve would be baseline
fidelity; the FEE LEVEL the company charges is a company decision, and the population share of
fee-averse households would be curriculum — the director's.*
