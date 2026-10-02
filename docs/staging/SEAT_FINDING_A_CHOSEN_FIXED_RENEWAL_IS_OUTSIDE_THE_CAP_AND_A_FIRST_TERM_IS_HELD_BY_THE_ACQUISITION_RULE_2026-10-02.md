**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `W3_1b_intra_year_price_cap_granularity` · **Claim:** `does-a-chosen-fixed-tariff-belong-under-the-cap` (Lane 0 delivery)

# A chosen fixed renewal is outside the cap; a first term is held by an acquisition rule, because the world's acquisition cannot see a price

Results against `docs/staging/records/SEAT_PREREGISTRATION_DOES_A_CHOSEN_FIXED_TARIFF_BELONG_UNDER_THE_CAP_2026-10-02.md`,
written at `db2184ec9` before any run returned. The draw's duplicate-work note named this same id;
its `claimed_at` was the draw's own write seconds before this process started, and no rival seat or
`surgical_land` held it.

## The decision

- **A fixed RENEWAL leaves the cap.** `CAPPED_TARIFF_TYPES = ("svt",)`. A fixed tariff the customer
  chose is outside SLC 28AD (commons, `slc_28ad_multi_register_cap_test.md`, "What the text settles"
  4). The world can press back: the renewal churn roll reads the chain's contracted rate
  (`run_phase2b` passes `_chain.unit_rate_gbp_per_mwh` to `roll_lifecycle_event`).
- **A fixed FIRST term stays held at the cap, under a named commercial rule and not the law.**
  `ACQUISITION_HELD_AT_CAP_TARIFF_TYPES = ("fixed",)`, with `held_at_published_cap(tariff_type,
  term_index)` as the one predicate that both the arm's ceiling and writer 4 read. The reason is
  the world, not the law. **The world's acquisition is price-blind.** `PRICE_DIFFERENTIAL_PCT = 0.0`
  (`simulation/customer_events.py`), the win is decided in `live_population._resolve_campaign`
  before any term rate exists, and nothing turns down a fix quoted above the default. Uncapped,
  first terms in 2021-22 were booked at up to ×3.55 the cap (PROS-2022-0063g, gas, won
  2022-02-27, struck at £137.7/MWh against a £38.8 cap). No real household takes that, and the world
  could not refuse it. That is value transfer counted as value, which is worse than the
  understatement it replaces.

## The runs: one variable, one commit

Each arm is the same commit with `CAPPED_TARIFF_TYPES` patched in-process (`/var/tmp/se-fixed-cap/`,
`measure.py` + `compare.py`). *nofixed* removes `fixed` everywhere (the pre-registered variable).
*landed* is the code as committed (renewals uncapped, first terms held). All six runs are at
`db2184ec9`. The landing's base is `6fbca3b7c`, which took the departure roll off an SVT conversion
(a world change). The two changes touch different branches of the renewal block, but the
interaction is unmeasured.

| | flat base | flat nofixed | flat landed | value base | value nofixed | value landed |
|---|---|---|---|---|---|---|
| domestic fixed clamped by writer 4 | 40 (29 first terms, 11 renewals) | 0 | 29 | 38 (29 / 9) | 0 | 29 |
| fixed contracted > cap ex-VAT | 0 | 31 (max ×3.55) | 7 (max ×1.48) | 0 | 66 (max ×3.55) | 42 (max ×2.36) |
| value-arm fixed `ceiling_bound` | – | – | – | 43 of 113 | 0 of 104 | 0 of 104 |
| churned billing accounts | 95 | 95 | 95 | 96 | 103 | 103 |
| total net £ | 110,285 | 114,908 | 110,328 | 118,178 | 119,177 | **114,591** |
| SVT calls whose rate moved | – | 10 of 2,839 | 0 | – | 77 of 2,724 | 67 of 2,724 |

## Grading, as written

- **P1 HOLDS in count and is REFUTED in where.** 40 clamps (≥20). But 1 of 40 fell in the EPG
  window, not half; 21 were in 2021. The bigger miss is that I framed the whole question as
  *renewals*. **29 of the 40 were first terms**, which the chain also runs through (`term_index`
  0). Writer 4 was mostly clamping acquisitions, not renewals.
- **P2 HOLDS.** 0 → 31 above the cap, inside ±25% of 40. No fixed rate moved down.
- **P3 HOLDS on the flat policy and is REFUTED on the value arm.** Flat: churn is unchanged, but
  the world's retention probability falls on every repriced renewal (PROS-2019-0321 at ×1.48:
  0.30 → 0.14). With 11 renewals, no roll crossed. Value arm: +7 accounts, above the ≤5 I
  predicted.
- **P4 HOLDS.** 10 of 2,839 SVT calls moved (0.35%), all through the portfolio premium; 0 on landed.
- **P5 HOLDS for base and change, and is REFUTED on the graded part.** Of 36 base ceiling-bound
  fixed decisions matched in the change, **34 became interior optima and 2 extrapolation-bound**,
  not at least half extrapolation-bound. Unbounded, the arm repriced 46 renewals at a mean ×1.38 of
  the capped rate, max ×2.4, and its own churn belief called each of them optimal. The law, not
  the evidence frontier, was what held the arm.
- **P6 HOLDS on three arms and is REFUTED on the one that ships under the value policy.** Net
  rises on flat nofixed (+£4,623), flat landed (+£43) and value nofixed (+£999). It **falls £3,587
  on value landed**. The two value arms differ only by the first-term rule, so the uncapped first
  terms were worth about £4.6k of transfer that the world could not refuse. That is the same figure
  as on flat, and it is why they stay held. With that transfer removed, uncapping the arm's
  renewals loses money. The arm repriced 46 renewals at a mean ×1.38 (max ×2.4), its belief said
  each was optimal, and the world churned 7 more accounts. **The cap had been shielding the value
  arm from its own churn belief.** Keeping a cap the law does not impose would hide that. With it
  gone, the realised A/B can see it.

## What this changes downstream

- The value arm's population (fixed and pass-through renewals) is no longer capped in production,
  so its ceiling machinery has no production caller. The five controls that test it keep testing
  it through a fixture that re-admits `fixed` (`arm_population_capped`), and
  `test_a_chosen_fixed_renewal_the_arm_prices_is_handed_no_ceiling` holds the production property
  with both partition legs. Mutations: `fixed` back in the tuple reds it plus two seam controls,
  and an empty acquisition tuple reds it plus the SVT control's EPG leg.
- The seam's order control lifted writer 3 past the clamp. Writer 3 uplifts only fixed renewals,
  which are no longer capped, so that mutation became **equivalent by construction**. The control
  now lifts writer 2 (the surcharge), which does meet the cap on an SVT renewal.

## Handed on, not taken here

1. **The acquisition is price-blind, and the first-term rule only carries the gap.** Held at the
   cap, the company still sells 2021-22 first terms below its own cost floor. PROS-2022-0063g was
   struck at £137.7 and sold at £38.8. The renewal desk refuses to do that on a renewal
   (`_apply_competitive_ceiling`: "it may never force a sale below cost"). A real supplier in
   2021-22 stopped acquiring rather than sell below cost. The repair has two legs: a price-aware win
   in the world, and a no-offer path at acquisition in the company. Once both exist,
   `ACQUISITION_HELD_AT_CAP_TARIFF_TYPES` should go.
2. **The arm's churn belief calls a ×2.4 renewal optimal, and uncapped it costs £3.6k.** This is
   now the value cycle's first-order subject (`THE_VALUE_CYCLE_REALISED_AB.md`). The world
   disagreed by 7 accounts. The in-flight world-D value-arms retake at `0bac2b8be` predates this change and
   describes its own HEAD.
3. **The EPG on a fixed deal is still read as a ceiling at `min(cap, EPG)`** for the first-term
   rule. One clamp in this world fell in the window. The per-unit EPG discount on fixed deals, with
   the supplier compensated, is not modelled.
4. The previous finding's follow-ons 2–4 stand (0.95× per-account SVT pricing; the uncalled
   `domain_invariants.check_sold_unit_rate_within_cap` on `min(cap, EPG)`; `household_charged`
   never reaching settlement).
