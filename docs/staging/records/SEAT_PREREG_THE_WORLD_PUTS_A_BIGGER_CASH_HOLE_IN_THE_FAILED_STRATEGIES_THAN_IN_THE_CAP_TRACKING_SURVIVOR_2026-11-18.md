**Severity:** RECORDED · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** suppliers-accounts-and-capital -- `docs/market_research/why_gb_suppliers_failed_or_survived_2021_22.md` (strategies S1–S5 and §S5)

# Pre-registration: the world should put a bigger cash hole in S1–S4 than in S5 through 2021–22 (2026-11-18)

*Delivery seat, continuation `world-ranks-real-2021-22-supplier-strategies`, step 3 of the director's 18 Nov steer
(`docs/staging/advisor/done/DIRECTOR_STEER_THE_WORLD_MUST_RANK_REAL_2021_22_SUPPLIER_STRATEGIES_IN_THE_ORDER_REALITY_DID_2026-11-18.md`).
Written before any strategy has been run through the world. Nothing below has been measured yet.*

## 1. Step (b), discovery: can the world run a stylised supplier's cash path outside `company/`?

**Not as one thing yet. All the inputs exist, and the composer that joins them does not.** Read at `190199b73a`:

| Input the instrument needs | Where the world has it | Fit for 2021–22 |
|---|---|---|
| The cap's unit rate on each date, with the real six-month resets (Apr-21, Oct-21, Apr-22) | `simulation/price_cap_enforcement.ofgem_cap_unit_rate_gbp_per_mwh_inc_vat` (published windows; elec 189.5 → 208.0 → 283.4 £/MWh, gas 33.4 → 40.7 → 73.7 £/MWh inc VAT at 1 Jul 21 / 1 Oct 21 / 1 Apr 22) | yes |
| The forward a hedge was bought at | `sim/data/ofgem_forward_weekly_{electricity,gas}.csv` from 1 Feb 2021, with its delivery axis in `docs/market_research/ofgem_forward_weekly_with_delivery_start_2021_2026.json` | yes for trade weeks from Feb 2021. A 12-month basket only: **the split inside the year is not published** |
| Spot for the unhedged share | electricity: Elexon MID half-hourly (`sim/cache/elexon_mid_2021_2023.json`); gas: `sim/gas_prices_history` (a **monthly TTF proxy**, not NBP) | elec yes. Gas is monthly, so the Sep-21 spike is smeared across a month. Stated, not fixed |
| The per-period hedge P&L | `sim/hedging.settle_hedged_period` | yes, one period at a time |
| SVT leavers | `simulation/market_switching_propensity.market_departure_rate` (annual: 2021 published 17.9–18.4%, 2022 crisis trough) | annual only. **GAP:** the within-2021 collapse in switching after Sep-21 is not resolved inside the year |
| Credit balances | `simulation/dd_balance_book` is per household inside the run loop, with no book-level aggregate | the instrument states NERA's £65–80 per customer (page §S5) rather than drawing it |
| SoLR inflow to survivors | **absent** | GAP. A survivor's book grew by SoLR transfer. The instrument leaves it out and says so |

**So the instrument is a new harness composer** under `tools/`. It reads only `sim/`, `simulation/` and published
data, and nothing in `company/` or `saas/` (W7, R13). The company never sees it or its output.

## 2. The quantity, defined before it is measured

**The cash hole, H_s,** for strategy s: the most negative value, per customer, of the cumulative strategy cash flow
from 1 Jul 2021 to 31 Mar 2022. Each month the flow is:

    revenue (cap or fixed rate × volume)
    − cost (hedged share × the forward it was bought at + unhedged share × spot) × volume
    + change in credit balances held

It is one supplier, one typical dual-fuel customer, with the same volumes for every strategy. **Equity is not in H.**
The page's §S5 found that equity does not separate the tiers at the licensed company (OVO −£443m survived on parent
support). Survival is read as "the hole is small enough that someone funds it", and the size a funder accepts, F, is
GAP. It is swept, never picked: F ∈ {£0, £25, £50, … £400} per customer.

Each strategy's parameters come from the page's table, with no others:

- S1: hedged 0% / 0%. Fixed share swept over {0.5, 0.75, 1.0} (NAO 3.22: "more than half"). Fixed rates struck at the
  Jul-21 forward.
- S2: hedged 20% at 3m, 15% at 9m, with the same fixed-share sweep.
- S3: hedged 87–91% at 3m, 70–95% at 9m on fixed. SVT stepped 100% → 20% over 6 months (Together).
- S4: fixed 100% / 100%. SVT 100% for 3 months, 0% beyond (Pure Planet).
- S5: SVT hedged on the cap's 6-2-12 reference profile, with fixed contracts hedged forward at strike.

Credit balances: £65–80 per customer at the Sep–Dec 2021 average (NERA), swept across both ends. S1 and S2 add the
page's "c. 80–90% of assets" only as a sign check, since there is no per-customer figure for those firms.

## 3. The real ordering (from the page, F11 reading)

- **Tier F (failed Sep-21 to Jan-22):** S1, S2, S3, S4.
- **Tier S (survived to Mar-22):** S5.
- Within tier F there is only a weak tendency: the unhedged books (S1, S2) are hurt no later than the well-hedged one
  (S3). **No strict order within F is claimed**, because reality failed firms hedged from 0% to 91% in the same month.

## 4. The predicted world ordering, written before the run

1. **The ranking test passes if** there is a band of F in which H_S5 > −F while H_S1, H_S2, H_S3 and H_S4 are all
   below −F, at every point of the fixed-share and credit-balance sweeps. The band's width in £ per customer is
   reported. **It fails if** no such band exists, or if any of S1–S4 has a smaller hole than S5 at any sweep point.
2. **Predicted holes:** H_S1 ≤ H_S2 < H_S4 < H_S3 < H_S5 ≤ 0, with |H_S5| under one third of |H_S1|. Predicted
   sizes: S1 and S2 several hundred £ per customer, driven by gas spot Sep–Dec 2021. S4 smaller, driven by the
   unhedged SVT after Oct-21, whose cap was set from Feb–Jul 2021 forwards. S3 smaller again. S5 near zero, with its
   residual from the leavers/volume mismatch and the cap's operating allowances, not from wholesale.
3. **Timing prediction:** S1 and S2 take most of their hole by end Nov-21. S4 and S3 keep deepening into Q1 2022.
4. **What could refute this, and what each would mean:**
   - S3 ends shallower than S5. That would mean either the instrument mis-prices the 6-2-12 basket or the
     forward-at-strike leg, or Together's stepped SVT ladder beat the cap's own index in this window. Diagnose before
     reading any fidelity meaning into it.
   - All five holes are small, because the gas proxy's monthly smear hides the spike. That is a fidelity finding on
     `sim/gas_prices_history`, a world defect (a TTF monthly proxy standing in for NBP daily).

## 5. Said before the run: what a pass does NOT establish (F11)

The world's prices for 2021–22 are the real record, and S5 is defined as the hedge the cap itself assumed. **A pass is
therefore largely the arithmetic of the real price path against a published index, and it is weak evidence about the
world's own mechanics.** What the world can get wrong, and the instrument can see, is the non-price part: volume and
weather (Together's "demand uncertainties"), leavers, and credit balances. A fail is informative. A pass says the
world's price path does not reward the wrong strategy, and no more. Reality's sharper discriminator, whether a funder
turns up, is outside the world by design.
