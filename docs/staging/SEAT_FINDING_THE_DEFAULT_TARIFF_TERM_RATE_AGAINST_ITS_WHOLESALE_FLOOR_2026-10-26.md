**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `price-cap` -- `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`

# SEAT FINDING: the default-tariff term rate, checked from below

Follows `SEAT_FINDING_THE_DEFAULT_TARIFF_TERM_RATE_AGAINST_THE_PUBLISHED_CAP_2026-10-26.md`, which
bounded the SVT term rate from above only: every one of 27,197 graded periods sits exactly at the
cap, so a rate set too low still passed. This is the other side (correctness ruling step 2, item 4).

## What the floor is, before measuring it

- **Commodity allowance only**: Ofgem's cap-model DF + CM unit-rate component for the window,
  `share_min x unit_rate` from `ofgem_cap_unit_rate_composition.json`, taken as the LOWEST over the
  three payment methods and fifteen regions. A term under it is under what the cap allows for
  buying the energy in every region and method.
- **GAP, named in the claim's `why`**: network and policy costs. The commons artefact separates the
  commodity share but not network from policy from operating cost, so the floor is "wholesale",
  not "wholesale plus network and policy". Passing is weaker than the ceiling's pass.
- **GAP, fails closed**: gas and multi-register electricity (the artefact is single-rate electricity
  only), and any day after the last cap window. UNCHECKABLE with the reason, never carried forward.

## Result

Measured 2026-10-26 on a ledger regenerated into /tmp from the shared tree's `run_output_latest.json`
at 85dcdc3b83 (not committed). Pre-registered: all graded SVT terms clear the floor (the cap sits
at 1/share of it, 1.2x to 2.5x); gas uncheckable.

| default_tariff_rate_above_wholesale_floor | |
|---|---|
| AGREED | **15,150** (term rate / floor: min 1.26, median 2.16, max 2.64) |
| DISAGREED | 0 |
| UNCHECKABLE | **12,047**, all "single-rate electricity only" (gas) |

The ceiling check reproduces 27,197 AGREED = 15,150 + 12,047. The prediction held.
**The check can fail**: scaling every floor by 2.7 turns all 15,150 into DISAGREED and leaves the
12,047 uncheckable. Unit tests hold the partition (one control over all three verdicts).

## What it does not show

- 44% of the graded default periods (gas) have no floor: gas commodity allowance is not in the
  commons. Filing: extend `ofgem_cap_unit_rate_composition` to gas, then drop the gap.
- The margin is wide (1.26x at worst). The floor would only catch a gross under-pricing; a rate
  between the floor and the cap is unconstrained. A tighter floor needs the network and policy
  components, which the cap model publishes per component in the same workbook.
