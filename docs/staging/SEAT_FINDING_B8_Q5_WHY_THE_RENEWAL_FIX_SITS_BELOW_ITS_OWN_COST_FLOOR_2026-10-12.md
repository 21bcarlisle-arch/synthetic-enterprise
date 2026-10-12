**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# B8 Q5: why 71-77 renewals per seed have a re-fix below their own cost floor

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
