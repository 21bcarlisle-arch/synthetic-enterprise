**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# SEAT PROPOSAL — home-mover retention as a supplier lever (2026-10-10)

*Delivery seat. The director, 2026-10-10: "Next supplier items, unless you see better: make the reactive
save on the loss notice a live supplier capability in the run, then home-mover retention now that moves
are on, then debt management as a next best action." Filed before any code, with its predictions.*

## What the lever is

When **our** household moves out, it tells us at least two Working Days before the move (SLC 24.1(a);
`docs/market_research/home_moves.md` §8.1). That notice is the one moment a retention offer can be made
before the household is gone (§8.4). A **move-with-us offer** supplies the household at its new home,
usually by carrying its tariff across and waiving the exit fee closing the old contract would trigger
(§8.3). At the new home another supplier is the incumbent, so taking us with them is a switch gained
at the destination, through the ordinary registration route.

## What exists today, and what does not

- **The world draws the destination and nothing reads it.** `sim/customer_state_layer.draw_home_move`
  returns `mover_arrives` (a derived destination premise, the same occupancy, starting on the move date).
  No caller consumes it, so every mover simply leaves our book.
- **The company receives no move-out notice.** §8.2 defines the honest observable (meter point, move-out
  date, date the notice arrived; destination absent unless the household says so), and nothing carries it.
- **No take-up rate is published** (§8.5 G8.4, re-confirmed by Ofgem OFG1164, June 2026).

## Proposed build, smallest first

1. **The notice (seam).** A move-out notice wire, dated two Working Days before the move: the latest notice
   consistent with the world's own decision that every mover notified in time (§8.1). Company side: a
   register that files it.
2. **The offer (company).** On the notice, the company decides per household whether to offer to carry the
   tariff to the new home with the exit fee waived. The decision reads only what it holds: its own
   forward value of the household (its CLV belief), the tariff in force, and the notice. A household the
   company knows to be vulnerable is never offered less than its twin (director, 2026-10-08).
3. **The world's answer.** No take-up rate exists, so none is invented. The household answers on **the same
   renewal roll** it would face at its next renewal, at the carried tariff (as the save does on the loss
   notice), and a labelled sensitivity `k` scales that response between 0 (no mover ever takes us) and 1
   (a mover stays as often as a renewing household at that price). The two ends are run and reported. A
   result that turns on `k` is reported to the director as turning on an unpublished number.
4. **The destination supply.** A household that takes us is supplied at the destination premise
   (`mover_arrives`) under a new account on the carried tariff, with the destination's demand drawn by the
   world's existing premise draw. This is the world work the lever needs, and it is admitted because it
   blocks this supplier result.

## Measurement and predictions (written before any code)

Arms on the production book: `off` (no offer, today) and `on` at k = 0 and k = 1. Same base seed.

- **P1, byte-identity.** `off` equals today's run on every account-term; `on` at k = 0 equals `off`.
- **P2, the stayers.** No stayer's price moves between `on` and `off` at either end: a retained mover is
  supplied at its carried tariff, and its margin must not enter the feed the portfolio premium reads (the
  save's lesson, `_held_on_a_save`).
- **P3, vulnerability.** Zero twin shortfalls; no known-vulnerable mover left unoffered while others are.
- **P4, the size.** The 400-founder run settles ~3,100 account-years; the world's move hazard runs from
  0.073/yr (all tenures) to 0.175/yr (private rent; EHS 2023-24, `home_moves.md`). So I expect
  **roughly 230-540 move-out notices** over the window, nearer the low end for an owner-heavy book; the
  run's own `home_move_outs` count is the check. At k = 1 I expect most offered movers to be
  retained (renewal stay share ~0.60), and `on` minus `off` total net positive, of the order of the
  retained accounts' remaining margin; at k = 0, exactly zero. I cannot predict the size better than that,
  and the result **will** turn on `k`.

## Found after filing (same day): an older model of the same event, and it is a world defect

`saas/home_move_win_rate.py` (Phase 7e, 4b-4) and `simulation/customer_events.py:1037-1042` roll, for
**every** household that churns at a renewal, whether "we win the home-mover's business": a property win
at `BASE_WIN_PROBABILITY` resi 0.55 / SME 0.35, adjusted by price and EPC, which activates a pre-drawn
successor supply point (`SUCCESSOR_MAP`) when one exists. Three things are wrong with it now:

1. **It is not a mover take-up rate.** It models winning the *new occupant* at the vacated premises
   (§8.4 step 4), and its two numbers are seed estimates its own module calls open questions. So "no
   take-up rate is published" above still holds; this proposal's `k` is not replaced by it.
2. **It applies to switchers.** A household that switches supplier at renewal does not vacate the
   premises; no new occupant arrives. Treating every churn as a move-out is a factual error.
3. **B7 now models the real event.** Moves are drawn by tenure (`account_move_out`) and the incoming
   occupant is admitted on a deemed contract after a void (`_admit_incoming_occupant`). The old roll
   double-counts what B7 measures, and would double-count this lever's result with it.

**Proposed, as a factual correction ahead of the lever:** retire the Phase 7e roll for renewal churn
(a switcher wins no property), leaving property wins to B7's incoming occupant. The book changes by the
successors it activated (the scale lane's 40-founder book carried 2). Measured as its own step, so its
effect is not mixed into the lever's.

## What this needs from the director

Nothing to start. The take-up gap is carried as `k` with both ends reported, exactly as the save's
response scale was. If the result turns on `k` (P4 says it will), the director is told so with both ends,
and a practitioner's view of how often a mover takes their supplier is the one number that would settle it.

## Step 0 result: the Phase 7e roll retired (2026-10-10)

**Prediction, written before the after-run.** 40 founders, budget 0, same seed. The renewal roll and
its hazard are untouched (the `(1 - win_probability)` factor stays inside the hazard; see below), so
the renewal departures are the same households on the same days. What changes: every successor the
old roll activated is no longer supplied (the scale lane's 40-founder book carried 2), and each of
those leavers goes to market instead, where the growth desk may or may not replace it. So
`total_net` moves by minus the successors' term margins plus whatever replacements land. A successor's
term margin fed the portfolio premium like any other term's, so later renewal prices of other
households may move as well; I cannot say in which direction, and the account-terms will show it.

**Result** (40 founders, budget 0, base seed, the scale lane's harness; before = `c9a4edc4e`):
- The old roll had activated **2 successors**: C5_2 (from C5's churn on 2016-12-31; supplied three
  terms, then itself left on 2018-12-31) and C3_2 (from C3's on 2017-07-01; supplied one term, then
  its own drawn move admitted an incoming occupant, OCC-b5fc2cbb6584, for two terms). After: none.
  C5 and C3 went to market instead; neither was replaced (C5 cancelled in cooling-off, C3 failed at
  application).
- Founders' renewal decisions are identical (31 events, 6 departures, once C5_2's own three are
  removed from the 33/7 before). 6 account-terms fewer (723 to 717).
- **58 renewal prices of other households moved** (C2, C7, C9, OCC-60f411c2ddb5 from 2017-10-01 on):
  the successors' margins fed the portfolio premium, as predicted. Direction not predicted, as said.
- `total_net` **+£89.41** (32,048.26 to 32,137.66), bad debt -£174.63 (408.05 to 233.42), billed
  revenue -£7,380. Net up on a smaller book: the successors' terms and their knock-on prices
  together cost more than they earned. Not decomposed further: four things moved at once.

**Each reader of the retired roll, decided:**
- `run_phase2b`'s activation branch and `won_successor_activations`: deleted; every renewal leaver
  goes to market. The successor roster stays (never supplied) because its weather and fabric draws
  share streams; retiring it from the roster is its own measured change.
- `customer_events`'s `(1 - win_probability)` factor inside the departure hazard: **kept**, with a
  comment. `year_level_anchor` was fitted through it against the published band, so removing it is
  a refit of the world's departure level (a baseline change, decided blind), not part of this one.
  At the shipped price position it is a constant segment scale (0.45 resi, 0.65 SME).
- `saas/enterprise_value.py` and `saas/reporting/annual_report.py` compute their own win rates as
  the company's valuation belief (churn net of winning the next occupant). They never read the
  roll, so nothing here changes them. They rest on the same premise, though (every leaver vacates),
  and that belief now runs against a world where no switcher does. **Filed here as a finding for
  the company lane, not changed.**
- Controls: `tests/simulation/test_home_move_undeliverable_win.py` held the old disposition; it now
  holds the opposite (a successor-bearing leaver goes to market, its successor never supplies).
  The four `home_move_won` tests in `test_customer_events.py` became one: a leaver carries no
  property win. The lineage test in `tests/tools/` no longer reads the deleted map.
