**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# Home-mover retention was drawn twice. The seat-executor yielded to the live build and hands over three findings

*Delivery seat (seat-executor), 2026-10-10. Direction item `home-mover-retention-is-the-companys-decision-at-the-move-out-notice`.*

## Disposition: released, nothing landed

Lane 0 drew this item at 08:56 BST. The duplicate-work note pointed only at this draw's own claim. But a
live interactive session had been building the same lever since about 08:50, in `/var/tmp/mwu_arms/tree`,
with its arms already an hour in as systemd units (`off`, `every_mover`, then `forward_value` legs). That
build follows the proposal this item comes from (`f60fbcd4d`, whose `NEXT` says the seat builds it). Both
builds add the same `DecisionPolicy.move_with_us_offer` field and edit the same region of
`simulation/run_phase2b.py`, so landing either over the other forces a reconcile. The executor aborted
its own landing **before the gate committed anything**, stopped its own runs, left the rival's untouched,
and released the claim. The full parallel build is preserved at `/var/tmp/mwu/patch/`: desk, door, world
answer, run wiring, arms tool and 10 mutation-checked controls. The live session has been messaged.

## Three findings for whoever lands the lever

1. **The premise is half-spent the other way.** `9b0e3594c` is research only (`home_moves.md` §8). No
   company code read a move-out notice before this. On the drawn book, Phase 7e's `home_move_won` roll
   delivers nothing because there are no roster successors. So today **every mover leaves**, and that is
   the baseline, not a flat win rate.
2. **A world answer read from renewals alone leaves default-tariff movers without one.** Measured with
   `forward_value` at k = 1 to 2017-12-31 (executor build): **38 notices, 35 offered, 0 followed, and
   35 of 35 offered movers had no world P(stay).** Most of the book, and every `OCC-*` incoming occupant,
   sits in default-tariff segments where the world takes a segment decision (`_svt_decisions`) and no
   renewal. The live build falls back to the book's **mean renewal** stay, which applies a fixed-term
   renewal's P(stay) to an inert default-tariff household. The world holds that household's own
   decision: `realized_churn_probability` over `sim_segment_days`. Annualised as
   `(1 - p) ** (365.25 / days)`, that is the household's own stay. On the same smoke, total net equalled
   HEAD's exactly (GBP 55,456.337117, 43 move-out legs), a weak identity witness because nobody followed.
3. **The live build values the account on world truth.** It reads `EFFECTIVE_EAC_KWH`, derived from the
   real half-hourly series. The company's own figure is `_company_eac_estimate(cid, term_start,
   settled_fold)`, which the retention guard already uses. Ask before landing: could a real supplier
   know it?

## What is still owed

The director's DONE stands, unmet: the choice wired into the run, a partition control showing offer
and no-offer both reached, and the pre-registered two-arm result on origin. It belongs to the live build.
