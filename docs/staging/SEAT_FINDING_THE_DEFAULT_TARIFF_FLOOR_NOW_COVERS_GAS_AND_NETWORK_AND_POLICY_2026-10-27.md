**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `price-cap` -- `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`

# SEAT FINDING: the default-tariff floor now covers gas, network and policy

Follows `SEAT_FINDING_THE_DEFAULT_TARIFF_TERM_RATE_AGAINST_ITS_WHOLESALE_FLOOR_2026-10-26.md`
(580937a15). That check floored single-rate electricity on commodity (DF+CM) only. It left 12,047 of
27,197 graded default periods (all gas) UNCHECKABLE, and its worst pass margin was 1.26x. This
continues the correctness ruling's step 2: each SVT unit rate, per fuel and per period, against the
cap and against the cost the cap allows.

## Correction, beside the claim

580937a15 and its finding say network and policy "are not separable in the commons". **That is
wrong.** The cap level model it reads (v1.31, the same workbook) carries `NC` (network costs) and
`PC` (policy costs) as their own rows per region in every `*_Benchmark` and `*_Nil` sheet. It also
carries `Gas_{Other,SC,PPM}_{Benchmark,Nil}`. The artefact simply never extracted them.

## What the floor is, before measuring it

- **Floor = DF + CM + NC + PC unit-rate allowance**, using Ofgem's own construction (benchmark minus
  nil, over the benchmark kWh). It is the LOWEST over the three payment methods and fifteen region
  rows. These are the costs the cap passes through. Operating cost, smart-meter cost, EBIT, headroom
  and the adjustment allowance are left out on purpose: a default tariff priced inside those is a
  commercial choice, not a rate below cost.
- **Gas**: the same components from the `Gas_*` sheets. The benchmark is 12,000 kWh before 2026,
  then 11,500 (P15b) and 9,500 (P16b). Each is witnessed against the model's `1c` table, which
  refuses on disagreement, exactly as for electricity.
- **Still a GAP**: multi-register electricity. A per-register rate against a blended benchmark floor
  is not a quantity, because an off-peak rate is legitimately under it. Days after the last cap
  window stay a GAP too.

Printed at real inputs (v1.31, direct debit, lowest region) before writing the check: the cap unit
rate over the full floor runs **1.11x to 1.26x for electricity** and **1.08x to 1.23x for gas** over
2019 to 2026. The narrowest margins are in the crisis windows, Oct 2022 to Mar 2023.

## Pre-registration (filed before the ledger is graded)

Book: `/tmp/seat_floor_ledger.json`, the same regenerated ledger 580937a15 graded, so the floor
definition is the only variable.

- P1. All 27,197 graded default periods are gradeable. None is UNCHECKABLE for want of a gas floor
  (15,150 electricity + 12,047 gas).
- P2. All 27,197 clear the full floor. The ceiling check found every rate exactly at its cap.
- P3. The worst ratio, rate over floor, falls from 1.26 to between 1.05 and 1.15 and sits in a
  crisis window (Oct 2022 to Jun 2023). It falls because the floor rises, not because any rate moved.
- P4. Scaling every floor up by 1.30 turns every graded period into DISAGREED. The check can fail.

## Result

Measured 2026-10-27 on `/tmp/seat_floor_ledger.json` (not committed), by `compare_all` over every
account.

| default_tariff_rate_above_wholesale_floor | 580937a15 (commodity, electricity) | now (DF+CM+NC+PC, both fuels) |
|---|---|---|
| AGREED | 15,150 | **27,197** |
| DISAGREED | 0 | 0 |
| UNCHECKABLE | 12,047 (gas) | **0** |
| rate / floor, min | 1.26 | **1.078** (gas, Jan–Mar 2023) |
| rate / floor, median | 2.16 | 1.17 |
| rate / floor, max | 2.64 | 1.25 (Jul–Sep 2024) |

- P1 held: none uncheckable.
- P2 held: all clear the floor.
- P3 held: the worst ratio is 1.078, in a crisis window.
- P4 held: at 1.30x every one of the 27,197 is DISAGREED. My first tally printed 54,394, because
  each disagreement was counted twice, once in the claims and once in the account's `differences`
  list. That was a counting error in my probe script, not in the check.

The tests carry the partition, plus a mutation the old floor passes: a 55p rate in Jan 2023 sits
between the commodity allowance (50.68p) and the full floor (57.60p). Pointing the floor back at
commodity alone turns five of the seven tests red.

**For the ruling's step 2:** the crisis-gas example was 3.9p in Jan 2022. The cap then was 3.88p
ex-VAT and the floor 3.37p, so that rate is at the cap. This agrees with the refutation in the
Explore finding.

## What it does not show

- A rate between the floor and the cap is still unconstrained, but that band is now 8–25% wide,
  not 26–164%. Operating cost, EBIT and headroom are left out on purpose.
- Multi-register electricity has no floor (GAP, named in the claim).
- `docs/design/DOMAIN_INVARIANTS.yaml` still carries gas unit-rate rows whose lower bound is "logic
  only ... no gas commodity component in the commons". The commons now carries one. That suite was
  written blind, so changing its source is the next item, not this landing.
