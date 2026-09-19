**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, "the SVT-side decision has no home because simulation cannot read the published floor"

# Decision: the SVT-side boundary decision is named on the CHECK side, because a check may not reach the world it judges

**Delivery seat, 2026-09-19, claim
`the-svt-side-decision-has-no-home-because-simulation-cannot-read-the-published-floor`.**
Pre-registration filed before the measurement:
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_WORLDS_OWN_INTERNAL_RATE_CLEARS_THE_FLOOR_THE_RECORD_SETS_FOR_THAT_SAME_ROUTE_2026-09-19.md`.
All six of its predictions landed as written.

---

## 1. The question, and the answer in three lines

The item asked: **does the SVT-side boundary decision get a name in `simulation/`, and if so how does
the published conversion floor reach it across the wall that keeps `tools/published_*` out of
`simulation/`?**

1. **No name in `simulation/`.** Not because a name would be untidy — because there is nothing left
   for it to carry. The rate gap has one home on the check side and the discriminator the name would
   need is already in the world's OUTPUT.
2. **The floor does not reach `simulation/`, and that is the answer rather than the obstacle.** The
   floor is a CHECK. A check that reached the thing it judges would stop being evidence of anything —
   `svt_product.py`'s own words, and `svt_internal_conversion_floor`'s own docstring: *"NOT a
   parameter to set the world to."*
3. **So the seam is not an import. It is the captured artefact**, read by `tools/`, in the direction
   that was already legal and already used. The floor reaches the decision by **judging its output**.
   That wire did not exist and now does.

## 2. Why the premise check came back spent, and why the work was not

The draw reported `b721b6acf` as already an ancestor of `origin/main`. It is — but it was never
work to be done: the item CITES it as the reason the rate gap has one home. The premise is intact.

The duplicate-claim note named this same id held by "another writer". Per the 2026-09-19 result's own
§5, that shape has been read as a self-collision once already and was not. I checked before building:
`git fetch`, and no concurrent `surgical_land` in `ps`. It was this claim, held by this draw.

**One of my own hypotheses was refuted before it cost anything, and it is recorded because that is
the cheap half.** I expected to find the wall one module wide — `test_the_published_check_band_cannot
_be_read_by_the_world_it_judges` names only `tools.published_tariff_mix`, and a rule with one
implementation and a second unguarded home is this repository's signature defect. It is not one here:
`test_the_published_route_split_does_not_read_the_worlds_clipped_constants` carries a second scan over
`simulation/**` for `tools.published_route_split`, and holds BOTH directions. The item's phrase
*"a module `simulation/` structurally cannot import"* is exactly right, and the structure is already
built. No work was owed there.

## 3. Why no name in `simulation/`, stated as what the name would have to carry

A name for the SVT-side decision could carry one of two things, and both are already placed:

| what the name would carry | where it already lives |
|---|---|
| **the RATE** — which number this decision uses | `tools.published_route_split.SVT_INTERNAL_CONVERSION_RATE`, a declared `None` with `SVT_INTERNAL_CONVERSION_RATE_GAP` naming why, and `svt_internal_conversion_floor()` bounding it below. One home. A world-side twin is the one-rule-two-homes defect and the prior invocation dropped its own `SVT_TO_FIXED_CONVERSION_RATE` for exactly this |
| **the DISCRIMINATOR** — which of the two decisions a given boundary is | **the world's own emitted rows.** Each term carries its product, so "the previous row was `svt` and the next is `fixed`" is a fact about the output, recoverable by anything reading a capture. `fit_year_level_anchor._svt_stints` / `_stint_fate` already recover it |

**A third thing a name might have carried is the CLAIM — that one call answers two populations — and
that is prose, not a symbol.** It is already written at both C1b blocks
(`simulation/renewals.py`, `simulation/run_phase2b._build_gas_renewal_schedule`) and, more sharply,
in the check artefact's own `the_draw_that_produces_it.the_second_use_that_is_not_sourced`: *"One
published anchor, two events, and nothing in the tree sources the second."* Whoever wrote
`svt_internal_return_and_tenure` had already named this decision. It is named on the check side, and
that turns out to be the right side.

**What a `simulation/`-side name would actually have cost.** A function whose body delegates to
`rolls_active_renewal` and whose only content is "which rate to borrow" is a symbol a future session
must read, keep and reason about, which changes no number and refutes nothing. The prior invocation
measured that exactly: a 200-pair sweep, identical `134/116/68/94`. An equivalence is not a reason to
land something; it is a reason to ask what the symbol buys. It buys nothing the artefact does not
already give, and it puts a name in the one directory that cannot reach the evidence for it.

## 4. What was actually missing, and it is an interconnection defect

`b721b6acf` landed a bound on `J_svt` — the SVT→fixed conversion route alone. The one reading that
measures the world's `J_svt` is twelve days older than it, and **does not know it exists.**

`fit_year_level_anchor._internal_return_vs_record` compares the world against CIM C4's raw internal
row `I`. Its own module says why that was the only option: *"`of_the_whole_book` … the ONLY one in
which the world and the record can be put beside each other at all."* True when written. But `I` is
**mixed** — `published_route_split`'s own identity is `I = s·J_svt + (1-s)·0.35·(1-phi)` — while the
world figure counts **only** this route. One numerator against a record filled by two, and
`world_below_record` biased toward True for a reason that is not about the world.

**This is the class only the seat can see.** Neither side is wrong. `b721b6acf` is right, the older
reading was right when written, and no bounded invocation is looking at both. It is the VAT shape
again: the newer, better instrument landing beside an older comparison that nobody re-asked.

## 5. What the un-mixed comparison says

`tools/fit_year_level_anchor.py` now carries `_internal_return_vs_the_published_floor`, wired into
the reading as `against_the_floor_for_this_route` and printed by `--internal-return`. It crosses no
wall: `fit_year_level_anchor` has imported `tools.published_route_split` since it was written, and
both are on the check side.

```
binding floor 0.044919 (6 waves);  world 0.185887 per SVT account-year = 4.14x — CLEARS
years below the floor: ['2016', '2017', '2022'] of 10 scored  (no returns at all in 2016, 2022)
```

**What each number counts, before either was compared.** World: `returned_to_fixed` stints over SVT
account-years of exposure, this book's resi electricity accounts. Floor: `(I - (1-s)·0.35) / s_max`,
conversions per SVT household per six months, GB domestic survey respondents, both fuels. **Same kind
of quantity** — conversions per SVT household per unit exposure on the product — which is what makes
this admissible and the mixed one not. Two mismatches remain, named and not corrected: a year against
a half-year, and this book's electricity accounts against GB households.

**THE BAR IS THE FLATTERING ONE AND IS NOT STRENGTHENED.** A six-month floor read as an annual bar is
lower than the true annual bar, so "clears" is the weak verdict and a year BELOW is below by at least
that much. Annualising would need the repeat-switching assumption `svt_internal_conversion_floor`
declines to make; inventing one to strengthen my own verdict is the single move that would make this
worthless.

**And it cannot say the world's rate is right.** The floor is one-sided and
`SVT_INTERNAL_CONVERSION_RATE` is still `None`, so 4.14x above a bound is not 4.14x too high — there
is no ceiling beside it. 2016 is the window's first year at 0.0055 SVT account-years, which is an
exposure count and not a behaviour; 2022 is the year the record's **own** register
(`published_route_split.STRUCTURAL_BREAK_YEARS`, imported rather than restated) excludes.

**The correction to the older reading is recorded beside it, not over it.** Nothing in
`against_the_record` changed. It gained one field saying what it is comparing, and the module
docstring's *"the ONLY one"* now carries the date it stopped being true.

## 6. The control, and that it can fail

`tests/tools/test_the_worlds_internal_route_is_judged_against_the_floor_for_that_route.py`, 9 legs,
**keyed to the property and not to today's answer** — a leg pinned to "clears" reddens when the world
is made more honest, and one pinned to "3 years below" reddens on the next capture.

Eight mutations run, **every one caught by the leg written for it** and not merely by a neighbour
(checked without `-x`, because the first run's `-x` had four mutations caught by an earlier leg and
that is the flattering reading):

| mutation | leg |
|---|---|
| `>=` → `>` at the bound | `..._the_boundary_is_not_strict` |
| SVT-exposure → whole-book denominator | `..._is_svt_exposure_and_not_the_whole_book` |
| freeze the per-year verdict True | `test_both_verdicts_are_reachable` |
| fail open when the floor is `None` | `..._is_refused_and_never_passed` |
| freeze the uniformity flag | `..._is_derived_and_not_declared` |
| bar becomes the mixed raw `I` | `..._and_not_the_mixed_internal_row` |
| delete the weak-direction statement | `..._names_which_direction_its_bar_flatters` |
| a `None` rate read as `0.0` | `..._is_scored_as_neither` |

`test_both_verdicts_are_reachable` is the one CLAUDE.md's rare-branch rule asks for: today's capture
clears in 7 of 10 years, so a verdict frozen True would look exactly like the mechanism working. One
control over the whole partition rather than a leg per branch.

## 7. Boundaries held

Nothing in `simulation/`, `company/` or `saas/` moves — no world-side constant, no second home for
the gap, no import across either wall. No company-side conversion or targeting desk. The floor stays
a check and `SVT_INTERNAL_CONVERSION_RATE` stays `None`. R13 does not arise: no world parameter
changed, so there is no fidelity move to decide blind.

## 8. What is still owed, and it is a sourcing question and not code

**The point estimate.** `SVT_INTERNAL_CONVERSION_RATE` is `None` and this reading gives it a floor,
not a value. What closes it is unchanged and unchanged by anything here: **one published domestic
instrument that cuts the internal-switching row by the tariff the respondent was on BEFORE the
move.** Until then the world borrows the 35% fixed-expiry anchor for the SVT-side decision, the
borrow is declared in prose at both C1b blocks, and `against_the_floor_for_this_route` is where it is
refutable.

**A ceiling would be worth more than a better floor.** The floor is one-sided and the world sits
4.14x above it, so the bound is not currently biting. CIM w6 Table 56's 2.5% vs 7.0% split on
*switching supplier* is the nearest thing to a ceiling on the SVT side, and it is the wrong event —
external change of supplier, not an internal move. Whether that ratio transfers to the internal
decision is a borrow nothing establishes, and it is not assumed anywhere in this landing.

## 9. Reversal

One `tools/` module, one new test file, one regenerated report artefact, two staging documents.
Deleting `_internal_return_vs_the_published_floor` and its call restores the previous reading exactly;
the artefact regenerates with `python3 -m tools.fit_year_level_anchor --internal-return`.
