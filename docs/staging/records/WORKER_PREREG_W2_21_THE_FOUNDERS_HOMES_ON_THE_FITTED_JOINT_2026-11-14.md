**Severity:** RECORDED · **Lane:** W2_customer_generator · **Atom:** `W2_21_the_premise_joint_is_fitted_not_drawn_independently`

# The founders' homes on the fitted joint: measured before building, and held until the 16 Nov book is graded (2026-11-14)

## Where the atom stands

The stock that net-new acquisitions are won from, and every mover's destination, already draw a whole NEED row
(`premise_population.draw_premise_from_joint`). The 387 drawn founders do not. `population_draw._draw_dwelling`
still calls `draw_premise` with `raked_joint()`, the three-axis joint (type x era x EPC band). Everything else
about a founder's home is drawn on its own: no floor area, no PV, and insulation read off the EPC letter.
e5e0cdcae7 held this step until the insulation flags were read correctly. e17ebc596a fixed that on 13 Nov, so
the step is now unblocked on its merits.

**It is not landed on this tick.** DIRECTION's `not_now` parks world changes under the 16 Nov book. Switching
the founders moves the home of every founder account, and so every founder bill. Six grades and the BLOCKING
level-DD finding's share leg are pre-registered on that book
(`SEAT_RECORD_WHAT_THE_INSULATION_CHANGE_CAN_MOVE_IN_THE_16_NOV_PREREGISTRATIONS_2026-11-13.md`). That record
showed the founders dominate those figures, and that their homes did not move under e17ebc596. Landing this now
would put a second whole-book change under every one of those grades. This record does the part that confounds
nothing: it measures the switch, and it files the prediction before the build.

## Measured (probe `/var/tmp/w221-founders/`, seed 20260724, no tree change)

`live_population._drawn_founder_pairs(20260724)` was run twice. The first run is the tree as it stands. In the
second, `_draw_dwelling` is replaced by `draw_premise_from_joint` over `fitted_stock_joint()`, the net-new
stock's own path. Shares are per household, so a dual home counts once.

| per household (n = 387 in both) | current (raked, 3 axes) | fitted joint | published |
|---|---:|---:|---:|
| flat | 25.3% | **21.7%** | 21% (EHS 22-23 AT1_5) |
| detached (bungalows folded in) | 24.8% | 28.2% | 25% |
| terraced | 28.2% | 27.6% | 29% |
| has a gas meter | 86.8% | 80.1% | 86.0% (EHS AT3.5), 84% (DESNZ 2024); the joint itself 83.7% |
| insulation POOR / PARTIAL / FULL | 9.3 / **87.9** / 2.8 | 17.8 / 47.5 / 34.6 | POOR bound 33% (e17ebc596) |
| floor area, PV | not drawn | drawn (PV 1.4% of records) | |

The sampling SE on a ~21% share at n = 387 is 2.1 points. The fitted arm's gas share is 1.7 SE below its own
joint, which is sampling. The current arm's 87.9% PARTIAL is the EPC-letter lookup that e17ebc596 removed
from the stock path and left on this one.

**The director's founder number is met in both arms**: 387 households (400 less the 13-account roster). My
first reading said the fitted arm came back 21 short. That was wrong: I had counted records, not households.
The 21 are fewer dual-fuel second legs, because fewer homes have a gas meter: 284 dual homes become 263.

**Exit leg 2, a published association the current path cannot produce, on the founders themselves:**

| lift over the cell's own marginals | NEED (fitted joint) | raked joint (current source) | founders, current | founders, fitted |
|---|---:|---:|---:|---:|
| terraced x oldest age band | 1.80 | 1.02 | 1.31 | 1.78 |
| detached x oldest age band | 0.42 | 1.09 | 0.77 | 0.74 |
| flat x <=50 m2 | 4.06 | not drawn | not drawn | 5.32 |
| detached x >200 m2 | 3.49 | not drawn | not drawn | 3.21 |

NEED's oldest band is pre-1919 plus about 42% of 1919-44 (`need_stock_joint.era_band_weights`). The founder
columns use PRE_1919 alone, so they are close to the NEED figure but not the same quantity. The raked joint has
almost no type x age association (1.02 and 1.09). The current founders' 1.31 on terraced is sampling noise
around that, not structure.

**GAP:** EHS publishes dwelling type by age (AT1_5 is a cross-tab). The knowledge layer does not hold that
cross-tab, so the association above is NEED's, the atom's named fitting source, not EHS's. Reading the EHS
cross-tab into `docs/market_research/` is a separate knowledge step.

## Prediction for the landing (filed before the build)

The build is one change. `_draw_dwelling` draws from `draw_premise_from_joint`, with the fitted joint fitted
once per stream as `raked_joint()` is now. It does not change the account's acquisition sequence, because the
dwelling draws on its own substreams (C-S2).

1. Founder households stay at **387**. Their ids, dates and bands are unchanged up to the dual/gas decision,
   which reads the home.
2. Dual-fuel founder homes go **284 -> 263** at seed 20260724, and founder records go **671 -> 650**.
3. Founder insulation goes **POOR/PARTIAL/FULL 9.3/87.9/2.8 -> 17.8/47.5/34.6**.
4. Over the whole book, gas legs fall by about 21 and founder heating demand moves in both directions. I cannot
   yet say the sign of the change in total consumption. FULL rises by 32 points and POOR by 8.
5. The control `test_the_live_stock_reproduces_the_type_by_floor_area_association_an_independent_draw_cannot` (in `tests/simulation/test_the_world_had_no_field_for_what_the_demand_vector_measures.py`) gets a founder twin: the founders'
   terraced x pre-1919 lift is **at least 1.4**, and the same founders drawn from the raked joint read **below
   1.2**. The must-fail arm is the current path.
6. `tools/world_claims`' founder gas share (84.88% today) moves down by about 4 to 7 points. Whether it
   crosses its 81.5% floor is the same unresolved sampling-allowance question as
   `WORKER_FINDING_THE_CAMPAIGN_ROUTES_GAS_SHARE_SITS_ON_THE_BANDS_EDGE_..._2026-11-13.md`, which should be
   settled first.

If (1) fails, the switch has leaked into the acquisition stream. If (2) moves by more than about 10 homes,
something other than the gas-meter share decides dual.

## When it lands

After the 16 Nov book is graded, on its own run, as W3_3 is held. The atom row carries a `PARKED` block_reason
that names this record. Unpark it to land.
