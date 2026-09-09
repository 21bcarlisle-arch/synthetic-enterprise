**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — discharge the survivorship finding against the four legs) · **Class:** controls_that_cannot_fail

# RESULT — three of the four legs are survivor cuts, and the estimand is the one that is not

Dispositioning `SEAT_RESULT_THE_UNSCORED_DECISIONS_ARE_EXACTLY_THE_DEPARTURES_SO_THE_METHOD_CONCORDANCE_CONDITIONS_ON_SURVIVAL_2026-09-08.md`
against the four legs measured in the 09-09 run. Graded against
`docs/staging/records/SEAT_PREREGISTRATION_WHICH_OF_THE_FOUR_BRIDGE_LEGS_ADMIT_THE_DEPARTURES_2026-09-09.md`,
filed before `_leg_conditioning` was written.

**ANOTHER LANE DISCHARGED THE FINDING WHILE THIS WAS BEING BUILT, and the discharge is theirs.**
`a10da2a48` closed its item 4 — the "a bigger book fixes it" reading — and wrote the discharge
block on the finding itself. I found out at the promotion, which is where this project keeps
finding it out. Their discharge stands untouched; nothing here re-claims it. **The finding's
severity is therefore not what this document moves.** What it moves is the Lane 0 item's own
premise, which the discharge does not address and which was wrong: the item asserted all four
legs are survivor cuts, and that was never measured by anything either lane landed.

## The premise, and the half of it that is wrong

The Lane 0 item drew one consequence from the finding:

> *"If the decisions the concordance scores exclude the accounts that departed, then every one of
> those four numbers — including the worse-than-chance estimand — is a statement about survivors
> and not about the book."*

The antecedent holds and is measured: on the 09-09 run `method_skill.survivorship` reads 40
dropped for `the_priced_term_carried_no_settled_row`, 40 of them departures, 0 unattributable, 0
scored departures. **The consequent is false for the leg it matters most for.**

`method_skill.fixed_horizon.zero_outcomes_the_world_recorded_as_a_departure` on that same run is
**37**, and those 37 rows are inside `every_priced_decision_pounds_outcome`'s population by
construction — `scorable` is the settled rows *plus the zeroes*. So the worse-than-chance
estimand, 0.4210 at p = 0.0045, is computed over a population containing **37 measured
departures**. It is not a statement about survivors. It is the one leg that was built not to be,
and the number is adverse *because* the departures are in it.

Legs 0, 1 and 2 are survivor cuts. Their populations are filtered on
`settled_within_the_horizon`, and a household that leaves at the renewal settles nothing, so the
zeroes are disjoint from all three.

| leg | n | concordance | admits departures? |
|---|---:|---:|---|
| 0 `the_published_population_ratio_outcome` | 168 | 0.5338 | no — the concordance's own population |
| 1 `settled_only_ratio_outcome` | 124 | 0.4993 | no |
| 2 `settled_only_pounds_outcome` | 124 | 0.5130 | no |
| 3 `every_priced_decision_pounds_outcome` — **the estimand** | **161** | **0.4210** | **yes — 37 measured** |

**So the reading survives the conditioning.** The adverse number on the page is about the book.

## What I refused to publish, and it is the interesting part

40 departures dropped by the concordance; 37 departures scored at zero by the estimand. The
sentence a reader builds from those two numbers is *"3 departures are excluded from the estimand
as well"*, and **I have not written it as a measurement and the code does not compute it that
way.** Those are two different funnels with two different gate orders — 40 is a drop count in
`method_skill`'s, 37 is a row count in `_fixed_horizon`'s — and their difference is not a
quantity. It is this project's most expensive recurring shape, arriving in the middle of the
document that was commissioned to catch it.

It is worth an answer, so it is asked properly instead: `_leg_conditioning` measures every leg's
departure count on the `(account, term_start)` key, in one pass, from every priced decision's own
recorded fate. **P5 of the pre-registration records (37, 40) as what I expect it to return, so
the derivation I refused is falsifiable rather than merely avoided.**

## What landed

1. **`_leg_conditioning`** in `tools/run_value_cycle_ab.py` — per leg: the decisions it holds,
   how many the world recorded as departures, how many departures it cannot see, and whether it
   is conditioned on survival. Plus the estimand's **residue by the reason that removed it**,
   because a censoring reason is a bound a longer run lifts and a coverage or join reason would
   be a departure dropped for something we control — a defect in the estimand, not a limit on it.
   Fails closed with a named reason when a run published no event log.
2. **`_skill_leg_conditioning`** in `tools/generate_value_arms_data.py` — passthrough on the same
   fail-closed shape as `_skill_survivorship`. A run predating the split publishes the ABSENCE.
   The verdict above is **not** inlined: it is true of the runs measured so far and is not a
   property of the mechanism.
3. **A column on the bridge table** in `site/capabilities/index.html` — *"Departures this cut can
   see"*, rendered per row from that row's own measured count, amber when the row is a survivor
   cut. A column and not a paragraph: the conditioning is a property of each row, and a paragraph
   under the table goes on naming the old rows the day a population changes. The verdict beneath
   is `_leg_conditioning_reading`'s sentence, composed from the counts.
4. **Ten controls, mutation-proved.** Producer battery 6/6 killed, door battery 4/4 killed.
   **Two poison rounds run before either real shape is asserted** — an estimand that admits NO
   departure, and a survivor leg that admits one — because `the_estimand_admits_the_departures`
   is the flattering answer here, and a block that returned it on every input would pass every
   test written against today's number.

## The limit, stated because the surface states it

The estimand is **less** conditioned than the concordance, not unconditioned. Censoring removes
decisions before leg 3 sees them — 47 on the 09-09 run — and any departure among those is a
departure the estimand cannot see either. The page carries the residue beside the admission for
exactly that reason; a surface reading *"the estimand admits the departures"* with no residue
would be over-claiming in the direction that flatters the estimand, which is the mirror image of
the defect the survivorship block was built to fix.

## What is next

1. **The counts light up on the next three-arm run.** The split needs every priced decision's
   fate and the world's event log in one pass, so no artefact on disk can have it reconstructed;
   today's feed renders the named absence, as `survivorship` and `fixed_horizon` each did on the
   day they landed. **Grade P1–P6 against that run** — P5 and P6 are the ones that can refute me,
   and P6 (every excluded departure excluded for censoring) is the one whose failure would be a
   defect rather than a bound.
2. **The page is a run behind for a second time if the floor run finished.** Not checked here and
   not this document's claim.
