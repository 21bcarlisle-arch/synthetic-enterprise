**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** unassigned · **Atom:** `B7_customer_state_layer_moves_and_shocks`

*Triage, 20 Nov 2026 (supplier batch 1, docs/staging/SEAT_RECORD_TRIAGE_OF_THE_SUPPLIER_FINDINGS_BATCH_1_2026-11-20.md): **parked**. Stayer price moves where a follower is supplied are still unattributed (the one-variable arm never ran), but the offer is OFF (curriculum move_with_us_activation false). Must run before any activation. Atom B7. Knowledge gap: yes (move-with-us take-up). Revisit at an activation proposal or 2026-12-18.*
**Knowledge:** none -- a grade of a built capability against predictions already filed; the mover knowledge page is docs/market_research/home_moves.md

# The mover offer on fresh seeds: five predictions hold, and stayers' prices move where a follower is supplied (2026-10-12)

**Fate (2026-10-15):** ATOM -- folds into `B7_customer_state_layer_moves_and_shocks` (re-pointed 2026-10-15; an ATOM fate names its atom).
**Fate (2026-10-13, clear-the-decks):** ATOM -- n/a P2 -- M5 (stayer-price moves) refuted on 3/4 seeds and unattributed; doc files its own follow-on "the-mover-offers-stayer-price-moves-are-attributed-by-an-unsupplied-follower-arm".

The director's Order 1: re-grade the mover offer on fresh seeds across the world's ranges. The
predictions M1-M6 were filed first, in WORLD_FREEZE_DD_SHOCK_SAVE_AND_MOVER_AT_THEIR_RANGE_ENDS_2026-10-12.md
§3.

**Book:** book seeds 61109-61112, 40 founders, budget 0, on the frozen payment world (553d7c855), to
2025-06-07. **Arms:** off, k = 0.5 and k = 1 on every seed, and k = 0 on 61109. **Comparison:**
`tools/move_with_us_arms compare`, always against an `off` arm on the same head (see the defect
below for why that needed re-runs).

## A defect found first, and fixed (e71d5c1db)

Four of the eight `on` arms stopped at the run's own W1_11 guard. A follower moving from a
legacy-profiled home into a fabric-traced one settled on the destination's trace while still carrying
its old home's "not eligible" verdict. The verdict now follows the home, as the incoming-occupier path
already did. The four arms were re-run on the fixed head, and each `off` arm they are compared with
was re-run on the same head, so every comparison differs in one variable.

## Against the predictions

| # | Prediction | Result | Verdict |
|---|---|---|---|
| M1 | k = 0 against off: identical account terms, 0 followers | identical, 0 followers (61109) | **held** |
| M2 | followers at 0.5 never more than at 1; pooled 0.3-0.7 of k = 1's | 4/9, 3/4, 2/4, 4/6; pooled 13/23 = 0.57 | **held** |
| M3 | followers / answerable offers at k = 1, pooled, 0.4-0.8 | 23/37 = 0.62 | **held** |
| M4 | followers supplied at the new home: at most half of followers | 0/9, 1/4, 2/4, 4/6; pooled 7/23 | **held pooled; refuted on 61112 alone (4 of 6)** |
| M5 | stayer price moves 0; vulnerable twin shortfalls 0 | shortfalls 0 on every seed. Stayer moves **0 / 32 / 17 / 19**, and 0 only on the seed where no follower was supplied | **refuted on 3 of 4 seeds** |
| M6 | sign of on - off at k = 1 turns on the supplied count; 0.00 with none supplied | 61109 (0 supplied) **0.00**; 61110 (1) +GBP 86.90; 61111 (2) +GBP 1,861.83; 61112 (4) +GBP 2,039.09 | **held** |

## M5: what moved, and what I cannot yet say

The premium hold works: a follower's account never teaches the portfolio margin again
(`PortfolioMarginBook.account_held_on_a_save`). So the moves come through another channel. They are
mostly tiny and mostly DOWN (median -0.07%, -0.33% and -0.01% on the three seeds; 23 of 68 are rises).
That looks like the portfolio's cost, not stayers paying for the offer: a supplied follower changes
what the company holds and buys forward. But three terms moved more than 1%: +5.3% (one 2019 term on
61111), and +12.7% and +4.7% on terms starting July 2021 (61112, the crisis onset).

**I cannot yet attribute them.** The one-variable test is an arm with the offer on and the follower
NOT supplied at the new home. If the moves vanish, the channel is the new home's supply. That is a new
experiment, so under this week's rule it is an atom, not a run: **P2,
the-mover-offers-stayer-price-moves-are-attributed-by-an-unsupplied-follower-arm.** M5 stays refuted
until it runs. The offer ships off (move_with_us_activation.json), so no live price is affected.

## What the grade says

On fresh seeds the mover offer adds value exactly where followers are supplied at their new home, and
nothing where none is. Value is +GBP 87 to +GBP 1,000 per supplied follower, on 21-32k of book net.
How many are supplied is the binding quantity: 7 of 23 followers. The rest are lost to gas-only legs,
destinations outside the weather store, and half-hourly files not carried. The base seed's 2 of 9
was not an outlier.

## M5 attributed (2026-11-26, worker tick)

**The unsupplied-follower arm already exists, by construction.** `_supply_at_new_home` in
`simulation/run_phase2b.py` only reads state before it returns a not-supplied reason. Destination
drawing is seeded and the weather check is pure. Every write (relocation, next move, gas
destination) happens after the last refusal. So a follower that is not supplied changes nothing, and
the arm this doc asked for equals `off`. Seed 61109 is its instance: 9 followers, 0 supplied, 0
stayer moves, on minus off GBP 0.00. **The channel is the supplied follower**, as the doc suspected.

**What carries the moves inside that channel is the bad-debt belief.** Prediction filed first:
`/var/tmp/se-mwu-m5/PREDICTION.txt` (sha256 checked). This was one variable, on seed 61112 at HEAD
b1399c1083 (k = 1, 40 founders, budget 0). The variable was dd3f004de's save rule applied to a follower:
`_payment_triad.account_held_on_a_save(cid, _move_end)` beside the existing
`_portfolio_margins.account_held_on_a_save`.

| arms | stayer moves | raised | largest move | followers / supplied | net |
|---|---:|---:|---:|---|---:|
| on vs off | 16 | 3 | +0.184% | 10 / 6 | +GBP 6,547 |
| on-held vs off | 16 | 8 | +0.084% | 10 / 6 | +GBP 6,551 |
| on-held vs on | 16 (the same rows) | 13 | | 10 / 6 | +GBP 3.91 |

Graded: Q0 held (moves remain at HEAD). **Q1 refuted** (the hold does not zero them). **Q2 refuted**
(it does not reduce them: the same 16 rows, and rises go from 3 to 8). Q3 held (the hold changes
pricing only). All 16 rows move when the belief changes, so this is the channel. But **the save rule
is the wrong fix for a follower**. For a saved account, both arms see the same customer. For a
follower, the off arm sees a leaver's final bill and the on arm sees a customer's later payments.
Dropping the later payments still leaves the two arms' evidence different. Including the follower's
payments mostly *lowers* stayers' belief (13 of 16 rows are higher when it is held out). Not shipped.

**Correction beside the October claim.** The +12.7% and +4.7% moves on 61112 are gone at HEAD. The
largest move is now 0.18%, so they were channels later work closed, not the offer. What remains is
3 stayer rises of at most 0.18%, against 13 falls. These come from the company learning bad debt from
a book that is different because it kept its followers. Under the director's condition as written
(exact equality, no stayer raise) that is still a breach. The offer ships off
(`move_with_us_activation.json`), and switching it on is his call. That call should be made with
this row in front of him: 3 rises of at most 0.18% and 13 falls on 61112. The breach comes through
the bad-debt belief, and the save-style hold does not remove it.
