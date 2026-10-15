**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** acquisition-and-retention-economics -- the save rate's published basis is `docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md` §5c and `assumption_toggles.yaml::q4_save_rate_on_loss_notice`; the floor that sizes the save is `SEAT_FINDING_RENEWALS_SIT_AT_THEIR_COST_FLOOR_BECAUSE_THE_FLOOR_CARRIES_THE_STANDING_CHARGES_NETWORK_AND_THE_PREMIUM_READS_THE_STANDING_CHARGE_AS_MARGIN_2026-10-14.md`

# The save is seen, and it is taken at about the published rate, so 0 of 23 is what the world predicts (2026-10-15)

*Worker, LANE 0 draw `the-save-fires-and-no-customer-takes-it`. Everything here comes from reading code
at origin/main `ed80ed28b` (a descendant of `4492d17bd`) and from per-offer logs already on disk. No new
arm was run.*

## The answer: the third of the three, with a qualifier

**Acceptance is correct and rare.** The acceptance model sees every offer. On every logged offer
P(stay) at the save price is higher than at the renewal price. In 4 of 5 logged offers the save is also too
small to clear the switch, because the cost floor caps it. But in the one offer that fully matches the
market's best deal, the world still saves only 1.3% of leavers. Across the logged offers the world
saves about 0.7% of the households it is asked about. The published proxy band for saves through the
losing supplier is 0.4–1.3% of domestic switches away, with a ceiling of about 4.1% (§5c). So the rate
sits inside the published band, and at 23 offers the expected number of saves is about 0.17.
**P(0 saves of 23) ≈ 0.84.** The sample cannot tell "nobody takes it" from "it is taken at the
published rate".

## The trace

1. **The company's side.** `simulation/run_phase2b.py` (save branch, ~L3732) enters only for a domestic
   household leaving a fixed term at its renewal, with the Invitation to Intervene held.
   `_price_match_inputs` hands the door the published default (ex VAT), the quarter's best-deal gap and
   `term_cost_floor`. `company/interfaces/save_offer.request_save_offer` calls
   `company/crm/save_offer.price_match_save_rate`. That returns `max(floor, default × (1 − gap))`, and
   only if it is below the renewal.
2. **The world's side.** The run re-asks `roll_lifecycle_event` at the save price, with every other
   argument unchanged, so it uses the same `churn_roll_for_renewal` die. A leaver is saved iff the roll
   lies in `(P(stay|renewal), P(stay|save)]` (`simulation/save_on_loss_notice.py`, scale 1.0). The
   world reads the price through `_price_differential_vs_market` → `churn_position_multiplier`, in
   pounds against the household's own trailing bill. That moves only the price/market risk. Bill
   shock, dissatisfaction and the year's level anchor do not see the save.
3. **Conditional on having left,** P(saved) = (P(stay|save) − P(stay|renewal)) / (1 − P(stay|renewal)).

### The traced offer

The regrade5 grade scripts (`/var/tmp/regrade5/cut_arm5.py`) kept counts only, so **no 61112 offer can
be traced**: its per-offer log no longer exists anywhere on disk. I traced the 2025 offers from the only
post-`afd818b22` runs that kept `save_on_loss_notice_log`, which are seed 61109 at `72ab9d113` ("fix")
and at `58e1e8905` ("ori") in `/var/tmp/w1-basis-out/`. Rates are GBP/MWh ex VAT. Pounds are a year
at the logged EAC, inc VAT at 5%. The *switch gain* is renewal minus the market's best published deal
(default × (1 − gap)).

| run | cust | start | renewal | save | floor | default | best deal | save £/yr | switch gain £/yr | share of gain | P(stay) renewal → save | P(saved \| left) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fix | 038 | 2025-02-05 | 247.3 | 242.4 | **242.4** | 236.8 | 221.8 | 8.2 | 43.1 | 19% | 0.2795 → 0.2850 | 0.76% |
| fix | 227 | 2025-05-12 | 257.2 | 255.5 | **255.5** | 257.4 | 221.4 | 5.3 | 116.6 | 5% | 0.4135 → 0.4151 | 0.27% |
| fix | 264 | 2025-05-28 | 228.1 | 221.4 | 214.9 | 257.4 | 221.4 | 20.4 | 20.4 | **100%** | 0.5974 → 0.6025 | 1.27% |
| ori | 038 | 2025-02-05 | 242.4 | 238.3 | **238.3** | 236.8 | 221.8 | 7.0 | 34.8 | 20% | 0.2850 → 0.2896 | 0.64% |
| ori | 227 | 2025-05-12 | 255.5 | 251.1 | **251.1** | 257.4 | 221.4 | 14.6 | 111.3 | 13% | 0.4188 → 0.4233 | 0.77% |

**SYN-2016-038, 2025-02-05 (fix), in one line:** the household leaves a renewal at 247.3 when the
market's best deal is 221.8, a gain of £43 a year. The match would be 221.8, but the floor is 242.4, so
the save is 242.4: £8 a year, a fifth of the gain. The world moves P(stay) by 0.55 points, which saves
0.76% of such leavers.

Over the five rows, the arms tool's own `implied_save_rate` (Σ gain / Σ leave) comes to 0.0213 / 3.006
= **0.71%**.

### Why I chose the third reading over the first

- **"Too small to clear the switch"** holds for 4 of 5 rows. On each of those the save is the floor
  to the penny, and the floor sits above the best deal and, on 038, above the published default
  itself. That is the defect already filed in `SEAT_FINDING_RENEWALS_SIT_AT_THEIR_COST_FLOOR_…_2026-10-14.md`:
  the floor carries the network cost the standing charge recovers. Its owner is B_commercial's
  writer 1 and floor work, and the fix belongs there, not in the save.
- **But row 264 refutes it as the whole cause.** That offer meets the best deal exactly, and the world
  still keeps 1.3%. In this world a household on a renewal is mostly leaving for reasons a price does
  not reach, and a £20 move is small on the calibrated pound-based curve. The published record agrees
  in magnitude: the losing supplier stopped 0.4–1.3% of switches.
- **"The acceptance model never sees it"** is refuted: P(stay|save) > P(stay|renewal) on 5 of 5 rows.
- **I have not established this:** whether a *deeper* save, below the floor, would be taken at a rate
  that pays. The 2026-10-08 flat-cut arms (`/var/tmp/save_arms/on-k1.json`, pre-`afd818b22`, out of
  scope for the list below) saved 3 of 12. Two of those were 24 MWh accounts, where a 4% cut is
  hundreds of pounds. That points to the pound size, not the model, as the lever.

## Every save-on grade since afd818b22

STALE = the run's head is not a descendant of `4492d17bd`. **Every one is STALE.** But for all of them
the stayers fix (`cc258be0a`) is a **no-op by construction**. Its only code change is that the rival's
ledger observes `_rate_the_rival_sees = unit_rate`, the rate *before* a save. With no save taken,
`unit_rate` is never replaced, so the ledger sees identical rates. What can still move these grades is
every *other* commit between their heads and origin, not the stayers fix.

| grade | head | seeds | offers made | saves_taken | STALE |
|---|---|---|---|---|---|
| floor recount `sv-k1` (`/var/tmp/floor-recount-out`) | `d55598dd6` | 61109–61112 | 0 | 0 | STALE |
| writer-1 basis, origin arm (`w1-basis-out/origin-sv-k1-61109`) | `58e1e8905` | 61109 | 2 | 0 | STALE |
| writer-1 basis, fix arm (`w1-basis-out/fix-sv-k1-61109`) | `72ab9d113` | 61109 | 3 | 0 | STALE |
| regrade5 `risk_tiers` | `87e9f4245` | 61109 / 10 / 11 / 12 | 3 / 3 / 2 / 4 | 0 / 0 / 0 / 0 | STALE |
| regrade5 `match_where_published` | `87e9f4245` | 61109 / 10 / 11 / 12 | 3 / 2 / 2 / 4 | 0 / 0 / 0 / 0 | STALE |
| regrade4 `price_match`, `risk_tiers_from_2019` | `5e5358092` | 61109 | not recorded | not recorded | STALE (no save fields: not a save grade) |

The 23 offers in the item are the regrade5 rows: 12 on tiers arms and 11 on hybrid arms
(`cc1a2e637`). The item said "19 offers in 9ab9b7959, plus 4 in 61112", and that matches.

## What follows

- **No defect in the acceptance model.** The save's size is the floor's defect and is already filed
  (named above).
- **A grading defect is filed:**
  `WORKER_FINDING_A_SAVE_GRADE_COUNTS_REALISED_SAVES_WHERE_THE_LOG_ALREADY_HOLDS_THE_EXPECTED_ONES_2026-10-15.md`.
