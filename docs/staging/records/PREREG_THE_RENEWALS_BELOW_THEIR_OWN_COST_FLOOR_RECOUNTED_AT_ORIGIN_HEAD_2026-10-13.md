**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**What:** pre-registration, filed before any run: the 23 of 27 held loss notices whose renewal sat below its own cost floor, recounted at origin HEAD (d55598dd6, carrying 03a0b66da and 04913b693) · claim `the-renewals-below-their-own-cost-floor-are-recounted-at-origin-head`
**Status:** GRADED 2026-10-13 -- P1-P5 on 61109 (95b3a38d2); P6 holds on 61110-61112; P7 (a) refuted, (b) ungradable, (c) GBP 89 outside its band. Results are beside the finding's claims.

# The renewals below their own cost floor, recounted at origin HEAD: predictions

## What is being re-asked

`../SEAT_FINDING_ON_FRESH_SEEDS_THE_SAVE_NEVER_FIRES_BECAUSE_RENEWALS_SIT_BELOW_THEIR_OWN_COST_FLOOR_AND_THE_PRICE_MATCH_RENEWAL_CUT_LOSES_NET_2026-10-13.md`
(b234e27bd) ran every arm at ed668c733. That code lacks 03a0b66da, which floors writer 1's
discount at the term's own cost floor. The finding's count was re-read from its own artefacts
(`/var/tmp/regrade/out/sv-k1-611{09..12}.json`, `save_on_loss_notice_log`, `invitation_held`) and
it reproduces: held 7/7/6/7, below floor 6/6/5/6.

**The floor is one definition on both sides.** The save's `cost_floor` (`run_phase2b._price_match_inputs`)
is `company_fwd + locked policy + locked network`. That is the same sum writer 1 now floors at
(`domain_invariants.own_cost_floor`).

**The shape of the 23 at ed668c733.** Renewal over floor: 17 sit at 0.972-0.975, which is writer 1's
signature. Gas 61109/179 and 61110/150 sit at 0.926-0.928. Four rows have a floor above the published
default rate (61109/045, 61110/150, 61112/038, 61112/127), so the cap can hold the rate under the
floor, and 03a0b66da's return check exempts that route.

## The arithmetic that decides the save, before any run

`price_match_save_rate` offers `max(cost_floor, default x (1 - gap))`, and only if that is below the
renewal. A renewal floored at its own cost leaves no room: the match can never be under it. **Lifting
a renewal to its floor therefore cannot make a save fire.** A save needs a renewal above
`max(floor, best published deal)`. The finding's hope ("it may already be answered") is about the
floor count. On the save it is wrong by construction.

## Predictions (seed 61109, save arm k = 1, 400 founders, budget 0, to 2025-06-07, frozen payment world)

The book is path-dependent, so the set of held notices can change with the code.

- **P1.** There are 5-9 held loss notices (7 before).
- **P2.** **0-2** held notices sit below floor by more than GBP 0.01/MWh (6 before). Any that remain are
  the cap route: their floor is above the published default, or the chain entry names the cap.
- **P3.** At least half of the held notices that were writer-1 rows before now sit AT the floor,
  within GBP 0.05/MWh.
- **P4.** **0 save offers** (0 before). The floored renewals leave no room for the match. If one fires,
  it is on a renewal above floor that writer 1 did not touch.
- **P5.** Across all answered loss notices, held or not, the below-floor count falls from 44/61 to 10 or
  fewer.

## What the grade does next

- **P2 holds (the count moves from 6 to 2 or fewer):** amend the finding's verdict beside its claim.
  Re-run 61110-61112 and the renewal-cut pair, as the item directs.
- **P2 fails:** name the chain writer (from `renewal_rate_chain` components) for each remaining
  row, and queue its fix.
- **P4 holds:** the save's inertness is NOT a cost-floor defect any more. It is the price match's own
  shape: on a book renewed at cost, there is nothing cheaper than the floor to offer. Say so beside the
  claim, as a question about the save's design, not about pricing.

## Addendum, filed after the seed-61109 count and before any further run (2026-10-13 ~08:45 BST)

The 61109 result and its writer attribution are in the finding's amendment. In short: 2 of 8 held
notices are below floor, and both are risk-tier retention cuts applied after the chain. This addendum
is for the runs the item calls for next: seeds 61110-61112 (save k = 1), and the price-match arm of
the renewal-cut pair on 61109. The risk_tiers side is the save run already done: with 0 offers the
save arm is the CURRENT_POLICY run, and at ed668c733 the two nets were identical (233,035.45).

- **P6.** Seeds 61110-61112 at HEAD each have at most 2 held notices below floor (6/5/6 before). Every
  such notice is a retention cut: rate / (1 - tier) lands at or above floor for a tier in
  {0.03, 0.05, 0.08}. 0 save offers on every seed.
- **P7.** Price-match renewal cut on 61109 at HEAD:
  - (a) retention offers fall below 47, the ed668c733 count, because a renewal now sits at its floor
    and the match cannot cut it;
  - (b) 0 renewals below floor anywhere in the run's loss-notice log (the match is floored);
  - (c) on net, match minus tiers (253,051): **I cannot say the sign.** Fewer cuts saves money and more
    departures costs it. The band is within GBP 3,000, either sign.
- **The rule from the finding stands:** do not recommend the switch if net falls on every seed. Only
  one seed is run here, so this pair can withdraw nothing and confirm nothing on its own.
