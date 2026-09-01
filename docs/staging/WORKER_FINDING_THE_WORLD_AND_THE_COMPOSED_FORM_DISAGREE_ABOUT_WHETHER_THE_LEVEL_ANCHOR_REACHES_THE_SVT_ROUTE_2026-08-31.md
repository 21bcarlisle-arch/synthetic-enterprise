**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# One rule, two implementations: the world and `build_departure_risks` disagree about whether the year level anchor reaches the SVT route

**Found:** 2026-08-31, delivery seat, while unioning the two departure routes onto an account
denominator (item 1 of
`docs/staging/done/WORKER_FINDING_C1B_ADDED_A_DEPARTURE_ROUTE_AND_EVERY_INSTRUMENT_MEASURING_DEPARTURES_KEPT_READING_THE_OLD_POPULATION_2026-08-31.md`).
Found by asking what the whole-book fit is allowed to hold fixed — not by any control.

## The disagreement, measured

`simulation/departure_risks.build_departure_risks` composes the SVT hazard as

    CAUSE_SVT_INERTIA = clip(level_anchor * svt_inertia * action_propensity)

On all **1,266** rows of the committed two-route capture
(`docs/reports/ladder_churn_factors_svt_segment_decisions.json`), the world composed it as

    realized_churn_probability = svt_inertia_hazard(years_on_svt, segment_days) * action_propensity

with the recorded `sim_level_anchor` **not multiplied in**. Every row, no exceptions, to the
artefact's own six-decimal precision.

## The world is right and the composed form is wrong

`svt_inertia_hazard` converts an **already-absolute published annual rate** — 0.20 recent
stayer / 0.10 long stayer — into a per-segment hazard, and the function's own docstring pins that
recomposition to within a day-count rounding. The year level anchor runs 1.5–5.8. Multiplying the
two would put annual drift off SVT near **65%** against a published **20%**.

That is the class CLAUDE.md already names from the other direction: *a module that normalises a
published absolute rate destroys the only level anyone could check.* Anchoring one a second time
does the same damage — the published 20% stops being a level anyone can check, because what the
world runs is 20% times whatever the renewal route happened to need that year.

**The renewal route needs the anchor and the SVT route does not, and that asymmetry is principled
rather than an accident.** The renewal hazards are dimensionless response curves (~1.0 at a neutral
household); nothing in them carries a rate, which is exactly why `departure_level_anchor.py` had to
exist. `svt_inertia_hazard` already carries one.

## Why nothing is red, and why it is LATENT rather than BLOCKING

**The wrong line is unreachable.** `build_departure_risks`'s `svt_inertia` parameter defaults to
`0.0` and **no production caller passes it** — `simulation/customer_events.py` is the only caller in
this tree and it does not. The SVT roll that would pass it is C1b's, which was parked in the shared
tree as another lane's uncommitted work and is **not at this HEAD**: `simulation/run_phase2b.py`
here contains no SVT departure route at all.

So no number in any run moves today. What is true is that **the first commit to wire the SVT roll
through `build_departure_risks` would silently triple the world's SVT departure rate**, every row
would stay well-formed, and the only thing that would notice is the published band — after a
capture, a fit and a publish.

## What was done rather than left named

The C1b finding's own lesson is that *a named comment is not a control*, so this is not filed as a
comment at the site. `tools/fit_year_level_anchor.svt_composition_refusal` checks the capture's
rows against both compositions before the whole-book fit runs, and **refuses to fit** if the world
ever starts anchoring the SVT route — because the fit holds the SVT contribution fixed and solves
the renewal anchor around it, which is only legitimate under the unanchored composition. Mutation
`assume the SVT composition instead of checking` fires
`test_the_fit_refuses_when_the_world_anchors_the_svt_route`.

**The world module is deliberately NOT edited here.** Removing `level_anchor *` from that line is a
one-token change to `simulation/departure_risks.py`, and its only future caller is code this
worktree cannot see. Editing a world module to match an artefact produced by code that is not in
the tree is how the two implementations got out of step in the first place. The check refuses; the
repair belongs in the commit that lands the SVT roll, and that commit now has something that fails
if it gets it wrong.

## Also owed, and smaller

**`population_anchor._churn_by_year` has no row at all for a year with no renewal decisions.** Its
`by_year` is built from `customer_events`, so 2022 — 55 accounts, 198 SVT segment decisions, 4
departures, and zero renewals in the capture — simply does not appear in the board gate's output.
The whole-book fields added today are on every row the gate emits, but a year that departs entirely
via SVT emits no row to carry them. Not fixed here because `sim_churn_rate` would have to become
`None` for such a year, and a published gate metric turning fail-closed crashes its old consumers —
the exact shape this repository has paid for. It needs the consumer sweep first.

## And a trap in the mutation-proving itself, because it reported a false SURVIVED

Proving the seven legs of `test_a_departure_reading_declares_its_population.py`, one mutation
reported **SURVIVED** and was an artefact of the harness. Two successive mutations changed the same
file by the same number of bytes (` and False`, ten characters) within the same second. CPython
invalidates a cached `.pyc` on **(mtime, size)** — both matched, so the second run imported the
*first* mutation's bytecode and the check under test was still live.

**A mutation harness that writes same-size edits in quick succession will silently report the
flattering answer**, which is a control that cannot fail, one level up from the controls it is
grading. Re-run under `python3 -B` with `PYTHONDONTWRITEBYTECODE=1`, all seven fire. Any future
mutation pass in this repo should disable bytecode caching by default rather than remember this.
