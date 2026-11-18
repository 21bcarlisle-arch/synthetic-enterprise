**Severity:** RECORDED · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** suppliers-accounts-and-capital -- `docs/market_research/why_gb_suppliers_failed_or_survived_2021_22.md`

# Result: the cash hole by strategy, Jul 2021 to Mar 2022 (2026-11-18)

*Delivery seat, step (d) of the director's 18 Nov steer. Instrument: `tools/strategy_cash_hole_2021_22.py`
(reads `sim/`, `simulation/` and published artefacts only; its electricity spot, `sim/cache/elexon_mid_2021_2023.json`, is gitignored, so it reruns only on a machine holding that cache). Full output: `SEAT_RESULT_CASH_HOLE_BY_STRATEGY_2021_22_2026-11-18.json`
beside this file. Pre-registration, unchanged:
`SEAT_PREREG_THE_WORLD_PUTS_A_BIGGER_CASH_HOLE_IN_THE_FAILED_STRATEGIES_THAN_IN_THE_CAP_TRACKING_SURVIVOR_2026-11-18.md`.*

## Headline

**The pre-registered test FAILS, and the cause is in the test's design, not the world.** At the sweep point fixed share = 1.0
there is no default-tariff book. S4 (fixed fully hedged) and S5 (fixed hedged at strike) are then the same book, and they
tie exactly at H = −£63.78. The rule asks for a band at *every* sweep point, so a tie fails it by definition. I did not see
this when I wrote the pre-registration.

**With that point removed (post hoc, labelled as such), the ranking holds with a wide margin.** S5's worst hole is £45.18
per customer, and the smallest hole in S1–S4 is £284.29. That gives a band of £239 in which a funder of size F rescues S5
and none of S1–S4 (F grid points £50–£275). There are no inversions. The rolling hedge reading gives the same answer
(£45.18 to £286.43).

**Per F11, as §5 of the pre-registration said in advance:** this pass is mostly arithmetic. It sets the real 2021–22 price
path against the cap's own index. It is weak evidence about the world's own mechanics.

## The holes (static reading, £ per opening customer; credit £65 and £80 give identical H, see below)

| Strategy | fixed 0.5 | fixed 0.75 | fixed 1.0 |
|---|---|---|---|
| S1 unhedged | −1,004.80 | −986.42 | −968.05 |
| S2 20%/15% | −829.33 | −818.07 | −806.81 |
| S3 PFP 91/70 · Together 87/95 | −475.52 · −436.73 | −351.53 · −293.34 | −227.54 · −149.96 |
| S4 Pure Planet | −504.80 | −284.29 | **−63.78** |
| S5 cap 6-2-12 | −26.58 | −45.18 | **−63.78** |

Every trough falls in Mar-22, the last month of the window, so every H is cut off by the window's end.

## Prediction beside outcome (§4 of the pre-registration)

| Predicted (written before the run) | Outcome |
|---|---|
| A band exists at every sweep point | **Wrong**, by definition at fixed share 1.0 (S4 ≡ S5). It holds at 0.5 and 0.75 |
| H_S1 ≤ H_S2 < H_S4 < H_S3 < H_S5 ≤ 0 | S1 < S2 < {S3, S4} < S5 holds everywhere. **S4 deeper than S3 holds only at fixed share 0.5.** At 0.75, S4 (−284) is shallower than Together-S3 (−293). At 1.0, S4 is far shallower |
| \|H_S5\| < ⅓ \|H_S1\| | Right: at most 64 against at least 968 |
| S1 and S2 "several hundred £" | **Bigger than predicted:** £807–1,005 |
| S5 residual from leavers and volume mismatch, and from the cap's operating allowances | **Wrong on both counts.** S5's wholesale leg is *positive* (+£19 to +£37), because cover sized on the opening book is sold back at spot when customers leave a rising market. Operating allowances are outside the instrument by construction (see Definitions). S5's whole hole is the seasonal drawdown of credit balances (−£63.78 by Mar-22), and every strategy pays the same drawdown |
| S1 and S2 take most of their hole by end Nov-21 | **Wrong.** They take about 20% by end of November (S1 −£204 of −£1,005). The hole is driven by gas winter *volume* (Dec–Mar is about two thirds of the window's gas) at a spot four times the allowance. The Sep-21 spike falls on summer volume |
| S3 and S4 keep deepening into Q1 2022 | Right. They are near zero or positive at end of November, and all of their hole comes in Dec–Mar |
| Refutation: the monthly gas smear hides the spike | Did not fire. The proxy is £59 / 79 / 73 / 100 per MWh for Sep–Dec 2021. It is a month-level stand-in, and the holes are large |

## Two properties of the pre-registered sweep, found by running it

1. **The credit-balance sweep cannot move H.** Only the *change* in balances held is cash inside the window. NERA's figure
   fixes the level, and the level cancels. Whether this is an equivalence or a missing test: it is an equivalence, shown by
   the algebra and held by `test_the_credit_balance_level_cancels_and_its_change_does_not`, which fires when the level is
   booked as cash. The seasonal *shape* does matter: it is S5's entire hole. Its source is the world (a flat direct debit
   against PC1 and HDD-normal volumes at cap rates), not NERA.
2. **Fixed share 1.0 makes S4 and S5 identical.** Held by `test_with_no_default_tariff_book_s4_and_s5_are_the_same_strategy`.
   A re-registration should either drop the 1.0 point or define S5's fixed book differently from S4's.
   **For the director:** the published record gives no S5 fixed-book hedge other than OVO's "secured under forward
   contracts".

## Definitions the instrument had to make (stated, not tuned; all fixed before the first run)

- **Revenue and cost on one basis: the cap's commodity allowance** (DF+CM, GB median, ex-VAT, from
  `ofgem_cap_unit_rate_composition.json`). Every wholesale price is put on that basis by the cap's own uplift from its
  index to its allowance, measured in the one period where both are published (Oct-21: electricity k = 1.433, gas
  k = 1.122). Network, policy and operating allowances pass through at the same rate under every strategy, so they are
  left out. Read on the full unit rate, they would show up as profit.
- **S5's Jul–Sep 2021 index** (the Apr-21 cap) is read back from that allowance through the same k. Its observation
  window (Aug-20 to Jan-21) predates the published forward, which starts 1 Feb 2021.
- **Hedges.** Under the *static* reading (primary, the one the pre-registration's S4 mechanism assumes), the cover is the
  book held at 1 Jul 2021 and the SVT cover was bought at the Feb–Jun 2021 mean forward. Under the *rolling* reading
  (a sensitivity the pre-registration did not name), each delivery month's last tranche is bought at its 3-month lead.
  Fixed-book cover is at strike, the Jul-21 forward, in both. The 12-month basket is used as the price for every delivery
  month, because the split inside the year is not published.
- **Leavers.** The world's annual departure rate (2021 published, 2022 record) is applied to the SVT book. Cover is sized
  on the opening book. **GAP:** the within-2021 collapse in switching after Sep-21. **GAP:** SoLR inflow to survivors.
- **Volumes.** Ofgem benchmark (3,100 / 12,000 kWh). Electricity is shaped by Profile Class 1. Gas uses the world's
  two-term form at 1991–2020 normal HDD. The real 2021–22 weather is not applied, so Together's "demand uncertainties"
  are not tested.
- The pre-registration's sign check on S1 and S2 credit reliance ("c. 80–90% of assets") was not run. There is no
  per-customer figure to put it on.

## What this does and does not establish

It establishes that the world's real price path, read against the cap's own index, does not reward the wrong strategy.
Under every reading run, the stylised failed-tier books take holes 6 to 38 times S5's at the same sweep point (fixed share 0.5 and 0.75). It does **not** test volume,
weather, leavers within the year, or SoLR inflow, which are the parts of the world that could press back. A next run
worth making: the same instrument with the world's real 2021–22 daily weather on gas volume, and with the 1.0 point
re-registered. Both changes are written down here before anyone runs them.
