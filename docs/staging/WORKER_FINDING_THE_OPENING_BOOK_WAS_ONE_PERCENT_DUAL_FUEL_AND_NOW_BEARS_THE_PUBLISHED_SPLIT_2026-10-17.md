**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted` — director steer 17 Oct

# The opening book was 1% dual fuel; it now bears the published split, and a control holds it there

Answers the director's steer of 17 Oct
(`docs/staging/advisor/DIRECTOR_STEER_THE_BOOK_IS_SINGLE_FUEL_DO_THE_KNOWLEDGE_WORK_2026-10-17.md`).
His words: *"this tiny focus on dual fuel, is so fantastically wrong … Research and understand the
problem and get it to do knowledge work and self correct."*

**He was right on every count, and the repo already held the evidence.** A page written on 21 June
said ~75% of residential customers take both fuels from one supplier. The coin that made the book
1% dual was written three weeks after that page, and nothing pointed one at the other.

## 1. Knowledge (K8)

`docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md`.
Every figure there was read in its primary document this session:

| Question | Published answer | Source |
|---|---|---|
| Homes buying both fuels from one supplier | **72%** of homes; 19m of 23m gas customers (**83%** of homes with gas) | CMA/GfK 2014 ¶41; CMA EMI PF Summary ¶9 (Jan 2015) |
| Split supply (gas at one supplier, electricity at another) | ~9% of homes; a split home is equally likely to be any one supplier's electricity or gas | GfK Fig. 2; PF ¶9 (8m single-fuel electricity, 4m gas only) |
| Homes with no gas | 14–16% | EHS AT3.5 (14.0% unmetered); DESNZ 2024 (16% off the grid) |
| Gas-only with no electricity | <1%: a gas-only account is always a split home | Ofgem CES 2017 |
| How a home with both fuels switches | **as one household**: by 2017, ~90% of switching homes moved both fuels at once and 1 point in 18 moved one | Ofgem Consumer Engagement Survey 2017 §3 (n = 4,001); 2008 floor 71% |

**GAPs, labelled on the page:** a challenger's own dual-fuel split; whether a save or win-back
keeps both legs (inferred, not measured); which fuel a one-fuel switcher moves; anything after
2017.

## 2. Census of every route in, before and after (seed 20260724, the 400-founder production shape)

| Route | Before | After | Published |
|---|---|---|---|
| **Drawn founders** (382 records) | 382 homes, **0 dual**; 250 electricity-only and 107 gas-only on gas homes; 25 electricity on electric homes; 93% gas homes | **220 homes**: **162 dual (73.6%)**, 48 electricity only (36 with no gas, 12 split), 10 gas only (split); 83.6% gas homes | market 72% dual, challengers 80–90%+; 84–86% gas homes |
| Eight seeds pooled (after) | — | 1,732 homes: 76.4% dual, 84.9% gas homes, 3.9% gas only | same |
| **Trickle** (switching arrivals) | every account single fuel by the coin | the same shape, P(both \| gas) = 0.90; default seed 2 of 2 arrive dual | ~90% |
| **Campaign wins** | electricity + gas leg on every gas home (since 26 Aug) | unchanged | ~90% (range 71–94%) — **the one remaining departure, in the dual-heavy direction**, ~10 points |
| Hand-written roster (18 records, 13 homes) | 5 dual | unchanged | — |
| `iter_prospects` default | the coin | electricity only, the campaign's own leg; no production caller used the coin | — |

**Routes out, read rather than re-measured:** renewal departure is already household-level. One
leg rolls and the other rides it (`customer_events.py:466`; `run_phase2b.py:2638` skips both legs
of a churned household), and `household.household_of` joins `Xg` to `X`. **Not re-measured this
turn:** home moves, debt exits and the save path for a dual household. They are the next census
item.

**Predictions were filed before the build**
(`docs/staging/records/WORKER_PREREG_WHAT_DRAWING_THE_FUEL_FROM_THE_HOME_DOES_TO_THE_OPENING_BOOK_2026-10-17.md`):
223 homes (210–236) → **228**; 71% dual (64–78%) → **67.5%**; 175 gas and 207 electricity points
→ **175 and 207**; gas-only ≈16 → **21**, a little high. All of these were at the pre-registered
0.83. **The constant then moved to 0.90 on the advisor's supplier-accounts evidence, not on this
result.** Challengers run 80–90%+ dual and Poesys is one. The 0.90 book above is reported as a
second step, beside the prediction.

## 3. Root cause, and the mechanism that now catches it

1. **The knowledge existed and nothing pointed at it.** The 13 July placeholder named no page to
   anchor from, so "documented placeholder" read as owned debt and nobody looked for its anchor.
2. **The 26 Aug ruling was fixed where it was seen.** The funnel got its gas leg; the founders and
   trickle reached the same coin through `iter_acquisition_events`, and nobody searched every
   caller of the constant. *A ruling lands everywhere or it has not landed.*
3. **The 16 Sept "gas-only accounts cannot leave" finding treated the book as a fact about the
   world.** 107 gas-only accounts in 382 is 28%, against a published ~8–13%.
4. **The book grew thirtyfold on that coin (13 → 80 → 400)** and no control compared the book with
   the published record.

**Mechanism:** `tests/simulation/test_the_opening_book_bears_the_published_fuel_split.py` draws the
founder book at the production founder count over eight seeds (~1,730 homes pooled). It refuses a
dual share outside 70–85% (the market's 72% to a challenger's 80–90%+), a gas-home share outside 81.5–88.5%, or gas-only above 15%. The bands
are the published shares ±3 sd, not this draw's own constants. It runs on every commit, so a
founder-count change is re-asked automatically. **Mutation-proven** in a scratch worktree:

- P(dual) = 0 → red;
- the meter-first premise draw switched off → red (gas homes 90.4%, against 85.5% when correct);
- the 0.72/0.28 coin restored → red;
- clean → green.

An earlier three-seed version with wider bands stayed **green** under the meter-first mutation.
Eight seeds is what makes that leg decisive. A further leg asserts that it refuses the 17 Oct book.

## 4. The world correction (W7: freeze, then solve)

A correction of the world's draw, decided blind to company results, before any supplier result was
looked at. **This is the new held draw for EP17.**

- **The account takes its home's fuel.** `population_draw.fuel_arrangement`: no gas meter →
  electricity only; with a meter → dual at 0.90, the challenger/switching shape (range 0.83–0.94),
  otherwise split half electricity, half gas. Founders and trickle take the same shape. One uniform is still
  consumed where the coin drew, so band, EAC and payment method are unchanged and the fuel is the
  one variable.
- **Founder homes draw the gas meter first** (EHS AT3.5, 86.0%), then heating given the meter. This
  is the stock path's own order since W2_20. `published_heating_weights()` drops oil, communal and
  solid fuel, so it had made 90.7% of these homes gas. **Scoped to the book's own homes**
  (`draw_premise(meter_first=True)` from `_draw_dwelling`). The harness's 60-home panel
  (`draw_premise_population`, read by `tests/harness/test_premise_two_level.py`,
  `tools/couple_fabric.py` and `tools/headcount_counterfactual.py`) has the same 90.7% and stays on
  it for now. Moving it re-draws the panel and moves about ten pinned values in the two-level
  harness: L1.1 quantiles, gas median, the unjudged count, an L2.4 pass, one strict XPASS and the
  calm-home chain. **Handed on as its own item**, because those values need re-keying with their
  reasons, not overwriting.
- **A dual home is one household with two supply points** (`X`, `Xg`, one premise), built by the
  campaign's own `_gas_leg_for`. The founders are thinned **by home** to exactly the director's
  number of records.

## 5. Sweep of the same class

| Constant | What it shapes | Disposition |
|---|---|---|
| `DEFAULT_COMMODITY_WEIGHTS` | fuel of every drawn account | **retired** (this change) |
| `published_heating_weights` in `draw_premise` | founder homes' gas share; the harness panel's too | **replaced for the book's homes**; the panel is handed on (§4) |
| `DEFAULT_BAND_WEIGHTS` 0.30/0.45/0.25 | which TDCV band each account's EAC and AQ come from | **GAP, named**. Ofgem publishes the band values, not the share of homes in each band. The anchor is NEED's consumption distribution against the TDCV thresholds, measurable on this machine. Next item. |
| `DEFAULT_SEGMENT_WEIGHTS` resi 1.0 | segment | settled 30 Aug (the draw cannot build a non-domestic body); not a share |
| `_COMBI_SHARE_OF_GAS`, `_STORAGE_SHARE_OF_ELECTRIC` | demand shape within heating type, not book composition | labelled unanchored in place; GAP |
| `DEFAULT_ACQUISITIONS_PER_YEAR_LAMBDA` | trickle count | director curriculum (R13), not a fidelity constant |

## 6. What moves, and one proposal

Every per-customer figure moves, because the book is now ~220 founder homes holding 382 supply
points instead of 382 homes. The published account count does not move, because records are held.
Expected directions (pre-registered): founder gas volume up ~60%, electricity down ~25%, households
down ~40%, per-household CLV and cost-to-serve up, and gas-only accounts "that cannot leave" down
from 107 to 10. **The published run figures move at the next run on this code, and that run is
the measurement.** No run was made this turn.

**Proposal, raised with `director_concerns`:** the founder number now has two readings. 400
**supply points** is what `FOUNDER_BOOK.yaml` defines and what the settlement budget counts, and it
is held here. That is ~233 households. 400 **households** would be ~700 supply points and would
spend ~75% more of the founders' customer-year budget, squeezing the campaign. **Recommendation:
keep 400 supply points** (one variable, budget unchanged). He decides whether he meant
households.

## 7. Landing (delivery seat, 18 Oct)

**The §2 census was re-printed on the landed content.** It ran in an isolated worktree at
`a40f0b165` plus this change's hunks only, and nothing else from the shared tree. Drawn founders at
seed 20260724: 382 records, **220 homes**, 162 dual (**73.6%**), 48 electricity only, 10 gas only,
83.6% gas homes. Every figure matches the table above.

**`tests/company/billing/test_collections_journey.py` went red on this change, and it was the
window, not the ladder.**
- One-variable control: `test_a_live_run_asks_the_world_for_a_prepayment_meter_at_the_ninety_day_rung`
  is green at `a40f0b165` and red with this change.
- At HEAD, the 2016-07-31 window reached day 90 on exactly one of 84 journeys, `SYN-2016-016`.
  The fuel redraw no longer founds that account.
- On the new book (109 journeys, the dual legs included), no journey passes day 56 at the ends
  07-31, 08-31, 09-30 or 10-31.
- At 12-31 the first offer falls on 2016-10-26 (`SYN-2016-073g`, three offers, still one account).
  At 2017-03-31, four accounts reach it, but the run takes 158 s against 115 s.

**Re-key:** `LIVE_WINDOW_END` moves to 2016-12-31. The whole file then passes: 34 tests, 104 s.
The window ends are not nested, because the end is also the campaign's quote cutoff and so moves
the book. That is why 10-31 misses a rung that 12-31 reaches.

**Still knife-edge:** the rung is reached by one account, as it was before. Whether the new book
produces fewer 90-day debtors than the published record has not been established here. With about
110 journeys, the change from one to zero cannot be told from noise. It belongs with the §2 item
that is not yet re-measured (debt exits for a dual household).
