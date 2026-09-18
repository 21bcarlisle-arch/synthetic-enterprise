**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** the world's SVT product

# The rolled household already had its exit, and only the one that ARRIVED on the cap was absorbed

**Answered:** 2026-09-18, delivery seat, claim
`the-svt-household-has-no-route-back-to-a-fixed-term`.

**The work, as drawn.** *"Build the missing WORLD-side edge in `simulation/`: a household that is on
SVT must be able to end up on a fixed term. Today it cannot — `tariff_type` is resolved once per
customer at schedule-build time and SVT is absorbing."* Take the hazard from the published record,
never a picked number; write the control as a reachability one first; do not touch the company arm.

---

## 1. The drawn item's central factual claim is REFUTED on the live tree, and the correction is one line

**A household on SVT could already end up on a fixed term before this turn, and did, at 0.1033
conversions per SVT-account-year.** Measured through the world's own builder on the real SSP feed,
120 real-grammar households, 2016-06-01 → 2023-12-31, **before anything was written**:

```
  households: 120    ever on svt: 120
  transitions: fixed->fixed 139, fixed->svt 181, svt->fixed 61, svt->svt 2779
  svt account-years: 590.28
  svt->fixed: 61   per svt-account-year: 0.1033
```

`svt->fixed 61` is the edge the item says does not exist. It landed on 2026-08-30 with C1b, and
`simulation/renewals.py` states the reasoning in its own comment — *"Making SVT absorbing instead
was the first draft and the published split refutes it: with no route back, the fixed share decays
to 12% by the second renewal and to nothing after 2022"* — controlled since by
`test_svt_assignment.py::test_a_passive_household_leaves_the_fixed_product_and_can_come_back`.

The item's §3.3 citation is where the claim comes from, and it is half right about the tree it
names. `run_phase2b.py:747–759` does rebuild a passive household's schedule with
`build_svt_schedule`, but **not** *"its remaining decade"*: the stint is bounded by
`min(_anniversary - 1 day, report_end)` and the loop then resumes at the anniversary, so the
household gets its next look at the market a year later. The absorbing read is of a draft the tree
no longer holds.

## 2. What WAS absorbing, and it is a landmine rather than a live defect

**A household that ARRIVES on the default tariff.** Both builders carried an early return —
`renewals.py:103` and `run_phase2b._build_gas_renewal_schedule` — handing back the whole window of
cap segments with no route out. Two routes onto one product, and only the mid-tenure one had an
exit.

**No caller reaches it today.** `population_draw.DrawnCustomer.tariff_type` defaults to `None`,
`resolved_tariff_type` turns that into `"fixed"`, and nothing in `simulation/`, `tools/` or
`company/` ever sets a record's `tariff_type` to `"svt"` — the only producer of the string is
`build_svt_schedule` itself. So the branch is **dead code with an absorbing state in it**, and the
day anything mints a default-tariff arrival — a SoLR intake, an acquired default book, both real GB
events — that household is absorbed for its whole tenure and nothing says so.

That is the honest severity and it is why this is LATENT, not BLOCKING. It also means **this
change cannot move a single published figure**: it is inert on every live run, and the reachability
control has to construct the caller itself.

## 3. The published warrant, derived and not picked

`tools.published_route_split.svt_internal_conversion_floor()`. The identity the module already
states is `I = s·J_svt + (1−s)·0.35·(1−φ)`; the renewal route's ceiling is `(1−s)·0.35` at φ=0, so

```
    J_svt  >=  (I - ceiling) / s
```

Three choices, all pushing the floor DOWN so a world that clears it cannot be argued to have
cleared it by the arithmetic: `s` at the LARGEST published default share, the ceiling already at
the most generous published fixed share, and `I` left as the survey's SIX-MONTH rate against an
annual ceiling.

| wave | fieldwork | I (6 mo.) | ceiling | s_max | **floor on J_svt** |
|---|---|---|---|---|---|
| W1 | March 2022 | 0.1318 | 0.070 | 0.90 | 0.0687 |
| W2 | July 2022 | 0.1248 | 0.070 | 0.90 | 0.0609 |
| W3 | Nov/Dec 2022 | 0.1449 | 0.070 | 0.90 | 0.0832 |
| W4 | July 2023 | 0.1104 | 0.070 | 0.90 | **0.0449 ← binding** |
| W5 | January 2024 | 0.1159 | 0.070 | 0.90 | 0.0510 |
| W6 | Jan/Feb 2025 | 0.1702 | 0.126 | 0.86 | 0.0514 |

**The point estimate remains a named gap.** `SVT_INTERNAL_CONVERSION_RATE = None`: no published
series cuts the internal-switching row by the tariff the respondent was on *before* the move, so
`J_svt` is unestablished and the floor is a **bound**, carried as one. It is used as a CHECK on the
rate the world produces from its own mechanism, never as a value to set the world to — writing a
bound into a slot named for a point estimate is the shape this repository has paid for repeatedly.

## 4. What was built

The exit is the C1b roll **unchanged**: no new rule, no new constant, no second mechanism. The
household looks at the market on its own annual cadence and `rolls_active_renewal` decides, at the
same anchored 35% population rate, with the same per-household engagement archetype, forced passive
across the same `FTC_WITHDRAWAL_WINDOW`. All the branch adds is the FIRST stint — a year on the cap
before the first boundary, because arriving on the default tariff is not a decision the household
revisits on day one. Domestic only, because `simulation/svt_rates.py` is the Ofgem domestic cap.

**A draft that was caught by printing it rather than by thinking about it.** The first version
recursed into a fresh `build_renewal_schedule` call at the anniversary. That call arrives with
`first_term = True`, which is the one condition that SKIPS the roll — every SVT-origin household
would have converted at its first anniversary with probability 1. The continuation falls through
into the loop instead, and `test_the_edge_can_be_taken_and_is_not_taken_by_everybody` refuses both
that draft and the absorbing one in a single assertion over the partition.

**Measured after, on the same real feed:**

```
  SVT-ORIGIN households: 120
    ever reach a fixed term: 79    never: 41
    transitions: fixed->fixed 93, fixed->svt 117, svt->fixed 117, svt->svt 3273
    svt->fixed per svt-account-year: 0.1671   (published binding floor: 0.0449)
```

Gas leg, 60 households: 34 reach a fixed term, 26 do not.

## 5. What each number counts, before anything is divided

- **0.1033 / 0.1671** count *transitions from a cap segment to a fixed term, per year an account
  spent on the cap*. Not households, not offers, not decisions.
- **0.0449** counts *conversions per SVT household per six months*, derived as a lower bound from a
  survey of all domestic respondents. It is not a per-boundary probability and it is not a rate
  anyone published.

They are compared as a floor against a produced rate, in the conservative direction (§3), and
nothing here rests on their ratio.

## 6. R13 and the arm

The fidelity case is §3 and stands alone: the GB record codes internal switching above the entire
fixed-term renewal population's ceiling in six waves of six, so most of it is default-tariff
households converting, and a world with no such route contributes zero to it forever. No company
result was read. `UPLIFTABLE_TARIFF_TYPES` is untouched, no conversion or targeting desk was built,
and `SEAT_DECISION_AN_SVT_HOUSEHOLD_IS_NOT_A_DECISION_THIS_ARM_DECLINES_2026-09-07.md` §3 stands.
Because §2 establishes the branch is unreachable in a live run, this change cannot enlarge the
decision population either — the consequence the item was careful to exclude from the argument does
not arise, and saying so is not an argument for the change.

## 7. Still owed

1. **Nothing arrives on the default tariff.** §2 is the finding under the finding: the world has a
   default-tariff product, a published ~58–90% default share to hit, and a population in which every
   household begins on a fixed term. Whether the drawn book should carry SVT arrivals is a
   population question for the world lane, decided blind to company results, and it is not answered
   here.
2. **The world's produced rate is not calibrated, only bounded.** 0.1671 clears 0.0449 by 3.7×; the
   floor cannot say whether it clears it by too much, because `J_svt` has no published point value.
   Closing that needs an instrument that cuts internal switching by prior tariff, which §3 records
   as not existing.

## 8. Not a target

R12. Neither the produced conversion rate nor the default-tariff share is a number to move. Both are
readings of GB's product mix.

## 9. The landing, and the file list it was drawn with was one path too long

**Added 2026-09-18 by the landing turn.** The delivery item that landed this named FIVE modified
paths. Only four of them are this work, and establishing that was the whole risk in the landing.

`tests/simulation/test_the_tariff_type_read_has_one_home.py` is **not this change and must not be
landed with it.** Its working copy has mtime **2026-09-07 09:43**, eleven days before the SVT work
(19:15–19:30 on 09-18), and its diff runs BACKWARDS: it replaces
`test_the_two_commodities_are_now_read_the_same_way_on_purpose` with the older
`test_the_two_commodities_are_read_differently_and_that_is_the_finding`, re-asserting that a drawn
gas record resolves to `None`. That is the state before `dcb8c6d10` ("the gas leg rolls onto the cap,
and the read and the roll had to land together"), which is in HEAD. **Committing the working-tree
copy would have reverted a sibling lane's landed gas-fidelity repair** and re-armed the 158
unlabelled gas terms it closed.

The same stale checkout explains the DELETED
`tests/simulation/test_the_gas_leg_rolls_onto_the_cap_like_the_electricity_one.py` (392 lines): that
file was ADDED by `dcb8c6d10`, it is present in HEAD, and it is absent from disk. **It is a stale
working copy, not a deliberate drop, so it takes no `--drops`** — an exemption there would have
recorded a deletion nobody decided. The four other contested paths the item named
(`test_phase40a_pass_through.py` 09-03, `test_policy_cost_values_vs_source.py` 09-07,
`test_home_move_undeliverable_win.py` 09-03,
`test_the_settled_book_draws_its_headcount_from_the_census_and_not_from_bedrooms.py` 09-18 05:53)
all predate the SVT work too, and none were landed.

**The item's file list is an un-re-asked prediction, and it was wrong on one path of five.** The
mtimes, not the list, are what decided it.

**Evidence the change is sound, taken before landing.** The two SVT suites are green on the real SSP
feed in the shared tree — `test_the_svt_origin_household_can_reach_a_fixed_term.py` and
`test_svt_product.py`, 13 passed. `test_svt_assignment.py` and the gas-leg roll controls were run
from HEAD's own bytes and pass; by construction they cannot be touched, because this change alters
only the `tariff_type == SVT_TARIFF_TYPE` branch AT ENTRY, which a household that ROLLS onto SVT
mid-tenure never reaches.

**One ratchet red on the shared tree is not this change.** `test_static_quality_ratchet` reports
I001 at 1307 against a frozen 1308. Attributed by diffing HEAD's bytes against the working copy file
by file: the drop is in `tests/tools/test_generate_maturity_map_data.py`, another lane's uncommitted
edit. All five of this change's paths are I001-clean, and the tree this commit creates carries that
file at HEAD.
