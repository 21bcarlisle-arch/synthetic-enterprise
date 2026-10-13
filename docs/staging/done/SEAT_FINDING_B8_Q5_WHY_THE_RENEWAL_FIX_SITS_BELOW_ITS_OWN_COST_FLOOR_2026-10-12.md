**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# B8 Q5: why 71-77 renewals per seed have a re-fix below their own cost floor

**Fate (2026-10-13, clear-the-decks):** DONE -- 03a0b66da Floor class DISCRETIONARY_RATE_NOT_BELOW_OWN_COST_FLOOR built and on origin; the arm-base follow-on it hands off is separately landed at 434d87587/04913b693 (see two 2026-10-13 findings below).

*2026-10-12, delivery seat (direction `b8-q5-why-does-the-renewal-fix-sit-below-its-own-cost-floor`).*

In the B8 Q5 full-window price-match arms (`/var/tmp/se-b8-q5-full/price_match-*.json`), 71-77
renewals per seed are declined by `retention_cut_share_at_price_match` only because
`cost_floor >= unit_rate`. Example: 2017-01-09 electricity, fix GBP 132.19/MWh, floor 136.27. The
item asked which it is: (a) the desk strikes fixes under its own unit cost, or (b) the floor counts
cost the standing charge recovers, so it is not comparable to a unit rate.

## What the source already settles (read before measuring)

- The floor (`simulation/run_phase2b.py::_price_match_inputs`) is `company_fwd + locked_policy +
  locked_network`, read off the term dict that `simulation/renewals.py` writes from the company's
  own `RenewalOffer`: the SAME forward and the SAME locked components the strike used.
- The strike (`saas/tariff_pricing.price_fixed_tariff`, via `renewal_desk.strike_fixed_unit_rate`)
  is that same sum PLUS GBP 2 target margin PLUS capital cost (1.645 x 0.5 x 0.15 x 0.10 = 1.23%
  of the forward before 2023). `_apply_competitive_ceiling` can only lower it to
  `max(ceiling, cost_floor)`. So at quote time the fix is never below the floor.
- So (b) as framed is refuted at source: whatever the per-MWh network figure recovers, the floor
  and the strike count it identically. The question becomes what moves the rate between the quote
  and the retention decision: `decide_renewal_rate` (portfolio premium, margin surcharge,
  profitability uplift, value arm, cap clamp) is the only reassignment of `unit_rate` between
  `run_phase2b.py` line ~2668 and the price-match call. The cap clamp cannot act in 2017 --
  `cap_ceiling_ex_vat` returns `None` there -- and `CURRENT_POLICY.renewal_margin_arm` is
  `flat_rules`.

## Pre-registration (filed before the probe runs)

Probe: a short-window run (`report_end` 2017-03-31) with `decide_renewal_rate` wrapped to record
struck rate in, rate out, and the term's floor, for every renewal.

- **P1.** Every below-floor renewal entered the chain at or above its floor; the chain moved it
  below. If any entered below, the quote path has a defect I have not read and this note is wrong.
- **P2.** The writer that moved it is writer 1, the portfolio learning premium, with a NEGATIVE
  `portfolio_premium_fraction` (recent book margin above target pricing the renewal down), or
  writer 2's margin surcharge negative for the same reason. I put 70% on writer 1, 20% on writer 2,
  10% on something else.
- **P3.** If P2 holds, the answer is (a): the desk can strike a fix under its own unit cost, because
  the learning premium is applied after the cost floor and nothing re-floors the result. That is an
  absurdity class for `company/compliance/domain_invariants.py`, not a defect of the match's floor.

## Result (probe `/var/tmp/se-b8-floor/probe.py`, run at `f8dfb8951` to 2017-03-31, CURRENT_POLICY + price_match)

**The answer is (a). The desk strikes at or above the floor, then writer 1 (the portfolio learning
premium) discounts the rate below it, and nothing re-floors the result.**

| term | struck | premium | out | floor | out - floor |
|---|---|---|---|---|---|
| 2017-01-09 elec (the item's example) | 139.15 | -5.0% | **132.19** | 136.27 | -4.08 |
| 2017-01-17 elec | 159.14 (ceiling held it AT the floor) | -5.0% | 151.18 | 159.14 | -7.96 |
| 2017-02-16 elec (x3, not below) | 123.07 | ~-2.1% | 120.52 | 120.38 | +0.14 |

Over 18 unique electricity renewals in the window: all 18 were discounted by writer 1 (-2.57% to
-5.0%); 15 ended below their floor, short by GBP 0.48-7.96/MWh. Writers 2-4 and the value arm moved
none of them. Gas renewals were not discounted (writer 1 reads the electricity book) and every
gas fix sat above its floor.

- **P1 HELD.** Every renewal entered the chain at or above its floor (headroom GBP 0.00-2.91/MWh:
  the GBP 2 margin plus capital cost, or zero where the competitive ceiling had already pressed it
  to the floor).
- **P2 HELD on writer 1.** The 70% leg. No margin surcharge, uplift or arm entry on any row.
- **P3 HELD.** It is the desk's own absurdity: `renewal_desk._apply_competitive_ceiling` states the
  rule "an undercut ceiling may cost margin, it may never force a sale below cost", and the
  learning premium, applied afterwards, breaks it. The headroom the strike leaves is ~2.2% of the
  rate, and `PORTFOLIO_PREMIUM_MIN` is -5%, so any premium below about -2.2% crosses the floor.

## What this means for the B8 Q5 flip

**The match's floor is right, and the flip need not wait on it.** The 71-77 declines per seed are
the match correctly refusing to cut a fix that is already below cost. Re-flooring writer 1 would
lift those fixes TO the floor, where `cost_floor >= unit_rate` still holds, so they would still
decline. The decline count barely moves. What moves is the margin those renewals earn, on both arms
alike.

## What is owed (handed on, not built here)

1. **Re-floor writer 1** in `company/pricing/renewal_rate_chain.py::decide_renewal_rate`: the
   discount may take the rate down to `company_fwd + locked_policy + locked_network` and no
   further. The chain does not hold those three today. They are the company's own offer values,
   already on the term dict, so they can cross the door the way the struck rate does. This changes
   every electricity renewal priced under a negative premium, so K8 comes first: a knowledge page
   on what a renewal discount may and may not go under.
2. **The class, not the instance,** in `company/compliance/domain_invariants.py`: no fixed unit
   rate the company contracts may sit below its own forward plus locked pass-through costs.
   Checked where the chain returns, so a future writer cannot reopen the gap.
3. **Two margin targets in one chain (an observation, not established):** the strike prices a GBP 2
   flat margin (~1.5-2% of the rate) while writer 1 steers to `PORTFOLIO_TARGET_MARGIN_RATE` = 8%
   of revenue. The premium goes negative only when the realised book beats 8%, and this note has
   NOT established what made it beat 8% in 2016-17 (hedge gains are the suspect, unmeasured).
   Whether discounting renewals on that over-achievement is the policy intended is a design
   question for the knowledge page in (1).
4. **Open, not claimed:** domestic electricity also bills a standing charge. Whether the GBP
   32-46/MWh network figure ALSO covers cost that standing charge recovers is a separate fidelity
   question. It does not touch this verdict, because the floor and the strike count that figure
   identically.

## The re-floor (direction `renewal-learning-premium-discounts-fixes-below-their-cost-floor`)

*2026-10-12, delivery seat. Knowledge first: `site/data/knowledge_topics.json` ->
`acquisition-and-retention-economics`, section "How far a renewal discount may go".*

Built: writer 1 may take a rate down to `company_fwd + locked_policy + locked_network` and no
further. The three cross the typed record (`RenewalDecisionInputs`) the way the struck rate does.
Where any of the three is unknown, a NEGATIVE premium is not applied at all (fail closed: a
discount nobody can check against cost is not given); a positive premium is unaffected. The class
is `domain_invariants.DISCRETIONARY_RATE_NOT_BELOW_OWN_COST_FLOOR`, checked where the chain
returns: the contracted rate may sit below the floor only where it entered below it or the cap
clamp (law) put it there.

### Pre-registration (filed before the re-run of the probe)

Same probe, adapted to wrap `decide_renewal` (the run loop's door since 2026-10-12), to 2017-03-31.

- **R1.** No electricity or gas renewal leaves the chain below its floor (0 of N, against 15 of 18
  electricity before).
- **R2.** Each of the 15 that were below now leaves writer 1 at its floor to the penny, so
  writer 1's logged `unit_rate_after` equals the floor and `floored_at_cost` is true on those 15
  and false elsewhere.
- **R3.** The 3 that were discounted but not below stay byte-identical; gas is unchanged.
- **R4.** The price-match decline count barely moves (the fixes now sit AT the floor, where
  `cost_floor >= unit_rate` still declines). I put it at the same count +/- 2 per window.

### Result (probe `/var/tmp/se-b8-refloor/probe.py`, CURRENT_POLICY + price_match, to 2017-03-31)

- **R1 HELD.** 0 of 19 unique electricity renewals leave the chain below their floor (15 of 18
  before).
- **R2 HELD, with one more row than predicted.** All 15 that were below now leave writer 1 at
  their floor exactly, `floored_at_cost` true. A 16th, SYN-2016-150's 2017-03-23 renewal, exists
  only in the new run (the world moved once rates did: it now reaches the price match) and is
  floored the same way. I predicted 15 because I counted the old population; the new run's
  population is not the old one.
- **R3 HELD for electricity.** The 3 discounted-but-not-below rows are byte-identical. **Gas:
  ungraded.** The probe joins the chain to the price-match row by the leg's customer id, and gas
  rows carry none, so gas went unrecorded in both runs. "Gas unchanged" is not established here.
- **R4 UNGRADED.** The probe records the price match's inputs, not its outcome, so the decline
  count was not measured. I cannot yet say whether it moved.

**The value arm, run because it could trip the new refusal** (same probe, `renewal_margin_arm=
value_based`): 27 unique electricity renewals, 0 below floor, 23 floored by writer 1 and then
priced by the arm, smallest arm margin chosen GBP 3.75/MWh. No refusal fired. **LATENT, not
reached here:** the arm adds `chosen margin - GBP 2` to whatever writer 1 left, on the assumption
that the struck rate still carries the GBP 2. On a rate writer 1 has floored it does not, so an arm
choice below GBP 2 (the grid starts at 0.50) would take the rate up to GBP 1.50 under the floor, and
the chain would now REFUSE it, stopping the run with a message naming the term. Correct by the
rule, and the fix belongs in the arm's base (price against the cost floor, not `struck - 2`), not
in a softer check. Handed on.

**Correction, same day, to the paragraph above:** it was not latent. Within the hour,
`tests/tools/test_the_decision_probe_compares_rules_without_moving_the_book.py` reached it: the
probe prices every renewal at each level of the flat-at-level grid, and levels under GBP 2 on
SYN-2016-009's floored 2017-01-09 renewal sold at 134.77 against a floor of 136.27, exactly GBP
1.50 under. The return check refused, as designed. So the arm's move now goes through the same
floor as writer 1 (`_floor_a_discount`): the arm may lower a rate, never under cost, and its entry
carries `floored_at_cost` on a cut. This changes the contracted rate ONLY where an arm or level
choice under GBP 2 meets a floored rate; the arm's logged belief stays the one for the rate it
chose. What stays open is the arm's base (`struck - GBP 2`), which is wrong on any rate writer 1
moved, in either direction: handed on.
