**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "the SVT household has no route back to a fixed term"

# Three lanes, one SVT edge: my code half is superseded and dropped, and what survives is the measurement that refutes the knowledge map's "structurally 0.0"

**Delivery seat, 2026-09-19, claim `the-svt-household-has-no-route-back-to-a-fixed-term`.**
Pre-registration filed before any measurement:
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_SVT_TO_FIXED_EDGE_IS_ABSENT_OR_MERELY_UNANCHORED_2026-09-19.md`.
All four of its predictions landed as written.

---

## 1. The disposition first, because it decides what the rest of this is worth

**I built the same thing two other lanes were building, and I found out at the promote.** While my
landing `f0bc1e057` sat in the pre-commit gate, origin/main moved four commits, two of them this
exact subject:

- `05684780e` — *feat(world): the household that ARRIVED on the default tariff gets the same exit
  the rolled one has.* The same repair to the same two builders.
- `b721b6acf` — *knowledge(J_svt): the rate a default household converts at is a named gap, and the
  record still establishes a floor.* `published_route_split.svt_internal_conversion_floor`, a
  DERIVED lower bound of 0.0449 per SVT household per six months, and
  `SVT_INTERNAL_CONVERSION_RATE = None` with its gap constant.

**Theirs is better on the axis mine was weakest, and `b721b6acf`'s own message says so before I
did:** the landed implementation splits `product` from `tariff_type`, where mine rebound
`tariff_type = "fixed"` after the opening stint — i.e. mine overwrote the arrival fact to make the
term loop accept the household. That works and reads wrong, and the landed version does not need
the trick.

**So I reset to origin/main and dropped my code half rather than merging it.** `f0bc1e057` was
never promoted and is not an ancestor of anything. This is the whole of what I would have re-landed
and did not:

| my file | why it is not landing |
|---|---|
| the arriving-on-cap exit in `renewals.py` and `run_phase2b.py` | superseded by `05684780e`, which is the same repair done better |
| `renewal_engagement.SVT_TO_FIXED_CONVERSION_RATE: float\|None = None` | **a second home for a gap that now has one.** `SVT_INTERNAL_CONVERSION_RATE` landed 47 minutes before my gate finished. Two names for one gap is the defect this repo keeps paying for, and mine is the one with no published floor attached to it |
| `renewal_engagement.converts_off_the_cap` and its three controls | see §4 — this one was NOT superseded, and dropping it was a judgement, not a forced move |

**No merge was attempted on the two contested modules** and nothing of theirs was rewritten. Memory
of this project's own history: a merge adopting one side's rewrite deletes the other side's
additive work, and my side had nothing additive left to protect.

## 2. What survives, and it is the half nobody else measured

The drawn item, the 2026-09-18 finding §3.3 it cites, and
`docs/institutional/knowledge_map.md`'s *Retention offers (SLC 22B)* row all said the same thing:
**the sim has no SVT→fixed edge at all, so its internal-switch rate is structurally 0.0 and cannot
be otherwise.** Measured on the live roster, before writing a line, building the electricity
schedules `run_phase2b` builds:

```
  resi electricity customers                134
  ever held an SVT term                     116
  held an SVT term and LATER a fixed term    68
  SVT -> fixed transitions                   94
```

**Sixty-eight of 134 households already did it.** C1b's passive stint is bounded at
`term_start + CONTRACT_LENGTH_DAYS - 1` and the term loop re-asks at the anniversary;
`renewals.py`'s own comment says making SVT absorbing was the refuted first draft, and
`test_svt_assignment.py::test_a_passive_household_leaves_the_fixed_product_and_can_come_back` has
held it there since 2026-08-30. **The world's internal-switch rate was never 0.0.**

This is a different measurement from the one `05684780e` carries. That one measures the ARRIVAL
route it built, on a 120-household real-grammar cohort. This one measures the MID-TENURE route that
already existed, on the live roster — which is the reading that refutes the claim in the knowledge
layer, and the knowledge layer is where the false claim was doing its damage. **The map is
corrected in this commit, beside the claim rather than over it**, and now points at
`svt_internal_conversion_floor` and `SVT_INTERNAL_CONVERSION_RATE` as the home of the rate gap —
the other lane's constants, not a third copy of my own.

`§3.3`'s second bullet is where the original reading went wrong: it describes a passive roller as
having *"its remaining decade rebuilt by `build_svt_schedule`"*. It does not. Bullet three — *"no
caller re-enters the term builder for a household already on SVT"* — was right, and is what
`05684780e` fixed.

## 3. What each number counts, before anything is divided

- **68 / 134** counts HOUSEHOLDS whose term sequence contains an `svt` row followed later by a
  `fixed` row, over the full report window. It is not a rate, not per year, and not per boundary.
- **94** counts TRANSITIONS, so it exceeds the household count because a household can convert more
  than once.
- **0.0449** (the other lane's floor) counts conversions per SVT household per SIX MONTHS, derived
  as a lower bound from a survey of all domestic respondents.

**68/134 and 0.0449 do not divide into each other in either direction** and nothing here rests on
their ratio. The comparable quantity to the floor is the per-account-year rate `05684780e`
publishes (0.1033 before its change, 0.1671 after), not anything in this document.

## 4. The one thing that was NOT superseded, and why I dropped it anyway

One call to `rolls_active_renewal` answers two different household decisions:

| coming off | the decision | what the record calls it |
|---|---|---|
| a FIXED term | re-fix, or roll onto the cap | the 35% active-renewal anchor is cut on exactly this |
| an SVT STINT | stay on the cap, or take a fixed deal | an **internal switch** |

The world answers both with one number, and CIM wave 6 Table 56 reads the two populations at 2.5%
and 7.0% on switching supplier in six months — a ~2.8× ratio on a field the supplier holds. I built
`renewal_engagement.converts_off_the_cap` to name the second decision separately, wired both
builders to choose by what the household currently HOLDS, and proved the split an equivalence: a
200-pair sweep across 2016–2025, and the identical `134/116/68/94` before and after. It cost no
number and made the borrow refutable in one place.

**I dropped it, and the reason is not that it was wrong.** After `b721b6acf`, the borrowed rate has
exactly one home and a published floor attached to it, in `tools/published_route_split`. A second
named decision in `simulation/` whose only content is *"which rate to borrow"* would either carry
its own constant (a second home — refused above) or point at one it structurally **cannot import**:
`simulation/` may not read `tools/published_*`, held by
`test_the_published_check_band_cannot_be_read_by_the_world_it_judges`. So the honest version of
this idea needs the seam designed first, and half of it landed now would be a name in `simulation/`
with nothing behind it.

**Filed as owed, not as done.** What closes it: decide whether the SVT-side decision gets a
world-side constant of its own — and if so, how the published floor reaches it across the wall that
keeps `tools/published_*` out of `simulation/` — before naming the decision in code. Until then the
borrow is declared in prose at the C1b block, which is where `05684780e` already declares it.

## 5. What this cost, and the mechanism that would have stopped it

**About one turn.** The draw's own duplicate-work check fired and named one live claim — my own id,
held by "another writer", which read as a self-collision and was treated as the note it said it
was. It was not: at least one other lane was on this subject under a different id, and
`b721b6acf`'s author found *their* rival by looking for a concurrent `surgical_land` in `ps` two
minutes into their gate, and killed their own commit. **That check works and I did not run it.**
The cheap mechanism is to `git fetch` and check `ps` for a rival `surgical_land` *before building*,
not at the promote — by the promote the work is already spent. Recorded here as the finding rather
than filed as a new register row, because the register already carries this class and an instance
that names its own remedy is worth more inside the result than in a list.

## 6. Boundaries held

No company-side conversion or targeting desk. `UPLIFTABLE_TARIFF_TYPES` untouched.
`SEAT_DECISION_AN_SVT_HOUSEHOLD_IS_NOT_A_DECISION_THIS_ARM_DECLINES_2026-09-07.md` §3 stands. The
2026-09-18 finding §5's three shortcuts are each honoured: `retention_offer_retained_fraction` was
not wired into the SVT branch, no divisor was relaxed, and the 0.10/0.20 anchors were not split by
the CIM 9.32/13.18 ratio.

**R13.** The fidelity argument was made blind to company results and is the other lanes' as much as
mine. Nothing here is a number to improve: 68/134 is a reading of this world's product mix, and
`tools/svt_generated_share_check.py` already records that mix as out of band in every judged year
in the direction of **too much fixed** — closing which moves households ONTO the cap, not off it.

## 7. Reversal

Documentation and one knowledge-map cell. Nothing in `simulation/`, `company/` or `saas/` moves.
