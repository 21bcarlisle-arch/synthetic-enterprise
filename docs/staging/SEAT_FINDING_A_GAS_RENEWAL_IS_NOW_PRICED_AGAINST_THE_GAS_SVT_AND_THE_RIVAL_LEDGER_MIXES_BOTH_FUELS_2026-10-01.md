**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# A gas renewal is now priced against the gas SVT, and the rival's ledger mixes both fuels

Claim `price-the-gas-renewal-against-the-gas-svt`. Results against
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_PRICING_THE_GAS_RENEWAL_AGAINST_THE_GAS_SVT_MOVES_2026-10-01.md`,
which was written before either run. Parent:
`SEAT_FINDING_THE_SWITCHING_REFERENCE_IS_ON_ONE_VAT_BASIS_AND_GAS_RENEWALS_ARE_PRICED_AGAINST_THE_ELECTRICITY_SVT_2026-10-01.md`.

The duplicate-work note at draw time named this same id as "already held". It was the draw's own
write: no other seat or `surgical_land` process carried it. So I did the work rather than taking a
disposition.

## What changed

- **One reader of the household's own default tariff.** `customer_events._household_svt_gbp_per_mwh(commodity, date)`
  reads the electricity or gas *charged* SVT and refuses any other fuel by name.
- **`commodity` is a required keyword with no default** on `_price_differential_vs_market`,
  `_reference_level_gbp_per_mwh`, `_market_reference_gbp_per_mwh`, `_svt_position` and
  `tools/run_price_ladder._svt_position_pct`. A default of electricity is how this defect was
  built in the first place.
- **The leg's own fuel is passed at every caller:**
  - `roll_lifecycle_event` (the churn roll, the logged level and the logged position);
  - `run_phase2b._build_churn_basis_risk` (the event's `commodity`);
  - `run_price_ladder.rung_reading` (the value-arm entry's `commodity`);
  - `tools/couple_value_based_pricing.belief_versus_truth` (this probe also read the electricity
    SVT for every leg, and the item did not name it).
- **A gas leg has no rival.** `competitor_reference` is anchored on the electricity cap and floored
  on the electricity cost stack. A gas leg is therefore read against the published gas default,
  and nothing moves it. That is a stated gap, not a model of a gas rival.

## Controls

- `test_price_cap_vat_basis::test_a_gas_offer_is_read_against_the_GAS_default_tariff_at_every_site`
  reads parity on the gas SVT at all six readings. A control leg checks that the same rate on the
  electricity fuel reads below −0.40. Five mutations were each run separately and each went red:
  1. answering gas with the electricity accessor;
  2. letting a gas leg reach the rival;
  3. hard-coding electricity in `_build_churn_basis_risk`;
  4. the same in `_svt_position_pct`;
  5. the same in `_svt_position`.
- **The rival-guard mutation was green at first.** I established that it was an
  **equivalence at the shipped chase of 0.5**, not a missing test. Half-way between the electricity
  SVT and any positive gas position always sits above the gas SVT, so `min(rival, gas SVT)` hides
  the guard. The control now pins the chase at 1.0, which is the only state in which the guard
  decides anything, and the mutation goes red there.
- `test_a_fuel_with_no_published_default_tariff_is_refused_by_name`.
- 21 existing call sites in 5 test files now name the fuel. Wider run: **1,342 passed**, covering
  the reference, churn, customer-events, `run_phase2b`, price-ladder, coupling, r1 and
  `saas/reporting` suites. `tests/design/` passed 151.

## Results: one variable, both arms `git archive` extracts of `b5ae7c3af`

The world had 256 customers. Both arms had 107 renewal events, and all 107 matched one-to-one.

| prediction | result | verdict |
|---|---|---|
| G1: gas `vs_svt` lies in [−0.45, +0.15] | 6 of 6, from −0.42 to +0.12 (was −0.78 to −0.87) | HOLDS |
| G2: gas reference = gas charged SVT | 6 of 6 (was £135–175, now £28–41) | HOLDS |
| G3: gas p rises on ≥4 of 6, falls on none; mean +5–60% | **rose on 6 of 6**, 0.4599 → 0.4996, **+8.6%** | HOLDS, at the low end |
| G4: gas churned 3 → 3 or 4 | 3 → 3 | HOLDS (six rolls; evidence of nothing) |
| G5: electricity events identical | 101 of 101 | HOLDS: one variable |
| G6: `rate_vs_svt_pct` = 100 × `vs_svt` | 0 mismatches of 107 | HOLDS |

**One reading I did not predict.** The 2019-06-22 renewal still reads −0.42, past the curve's
−0.30 saturation, but its probability rose anyway (0.7294 → 0.7379). The household's own
`price_sensitivity` weight scales the differential before the curve sees it, so a weight below
about 0.71 brings −0.42 inside the curve. G3 held because I did not predict "unchanged" for it.

**Pass-through repeats the parent's dilution.** The curve multipliers moved by ×3 to ×10, and the
probabilities moved by +1% to +35% relative. Gas pricing now reaches the departure roll, but
through the same small competing-risk share the parent measured for electricity. That bears on
PB3's "largest lever" premise, which is already handed on from the parent.

## Found on the way, and not changed here: the rival's ledger mixes both fuels

`run_phase2b` calls `_competitor_position_ledger.observe(term_start, unit_rate)` inside the
decision-leg block. For a gas-only household the decision leg is gas. So the one ledger averages
electricity struck rates of about £150/MWh with gas struck rates of about £30/MWh, and the
rival's **electricity** position is dragged down by every gas-only household's quarter. The rival
then chases electricity offers further than the company's electricity price justifies, which
raises electricity churn.

Fixing it changes electricity churn, so it would have been a second variable in this run. The fix
is to observe only electricity legs, or to keep one ledger per fuel and leave the gas ledger
unread. Each needs its own pre-registration. Handed on as `observe-only-the-electricity-leg-in-the-rival-ledger`.

## Not touched

`company/` and `saas/` hold their own SVT comparisons, which are the company's beliefs. A wrong
belief there is a belief-versus-truth gap, not a world defect.
