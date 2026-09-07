**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# R1's only unbiased magnitude was measured, written to the artefact, and reached no surface

**Found:** 2026-09-07, delivery seat, claim `r1-ceiling-coverage-is-what-buys-a-magnitude`.
Repaired in `tools/generate_delivery_page.py` and `site/harness/index.html`, controlled by three
mutation-proven tests in `site/test_harness_delivery_record.py` and
`tests/tools/test_r1_inference_ceiling.py`.

**This continues, and does not restate,
`SEAT_FINDING_R1S_MAGNITUDE_WAS_NEVER_A_COVERAGE_PROBLEM_AND_THE_RUNG_THAT_FIXES_IT_WAS_MEASURED_AND_NEVER_LANDED_2026-09-07.md`**
— the earlier turn of this same claim, which established that the direction's coverage diagnosis was
already two-thirds delivered, that `whole_book_pair_rung` is the rung this book can power, and which
handed on one piece explicitly: *"A49 must decide, explicitly and in view, which rung it gates R3
and R4 on."* **It cannot be decided in view while one of the two rungs is invisible.** That is what
this fixes. The gating decision itself is still not made here.

I re-derived the coverage table independently from the run output before reading that finding, and
it reproduces exactly: `portfolio_premium_pct` and `mean_recent_margin_rate` at 164,
`perceived_bill_saving_gbp` at 69. One thing to add to it — the 69 is **one gate, not three write
sites**. Five log families carry the identical 69 households, not merely the same count:

    churn_journey_log · customer_events · churn_basis_risk · demand_estimation_log ·
    feedback_survey_log     — all 69, all the SAME 69, a strict subset of the 164

`run_phase2b.py:2159` appends `churn_journey_log` inside the priced-renewal branch. That is the
pre-registration's own refutation branch for prediction 2 (*"a shared upstream gate — one branch,
three fields — not three independent write sites"*), and it is what was there.

---

## The defect

`whole_book_pair_rung` landed in `fc9d943a5` carrying the only unbiased magnitude this book buys:

    three-way split, pair rung  : REFUSED (5.00 households/cell, needs 8)
    three-way split, whole book : +0.2513  vs noise floor +0.1628 (p=0.01), 13.75/cell,
                                  fit fold 55, estimate fold 54, all 164 households

The instrument computed it, printed it to stdout, and wrote it to
`docs/observability/r1_inference_ceiling.json`.
**`tools/generate_delivery_page.py::the_number_the_programme_rests_on` lifted the two rungs beside
it and not this one.** So the delivery feed published `magnitude: null`, `/harness/` rendered a
refusal, and R3 and R4 stayed gated on a null while the measurement that answers them sat on disk
one function short of the surface.

This is the shape of `613f9bd17` — *the page published a hedge where we already had the
measurement* — one layer down. Not a hedge standing in for evidence, but a **lift** that stopped
one key short. **A fixture-fed door test cannot see this class at all**: it supplies the field the
generator never produced and passes on both legs. So the control for it
(`test_the_generator_LIFTS_the_only_rung_that_can_carry_a_magnitude`) calls the generator against
the real artefact and asserts the panel carries **what the artefact holds**, whichever way that
falls, including a refusal. Pinning `+0.2513` would go red the day the book grows and green the day
the lift returns a stale constant, which is backwards.

## Three published sentences that had rotted

`_magnitude_sentence` is appended to `what_it_does_not_say`, which the page renders. Three literals
asserted facts the function had no access to. Each was true on the run it was written against and
stayed put when the run moved.

1. **"So R1's ceiling clears its null on this book"** — emitted unconditionally, while the paragraph
   it is appended to opens **"WE CANNOT TELL"**. One rendered note contradicting itself, live.
2. **"…inside its own noise floor — indistinguishable from nothing"** about the full-coverage rung —
   emitted whenever a floor existed at all. That rung reads **+0.2992 against a floor of +0.1557 at
   p=0.005**: it is *above* its floor, and the sentence was understating R1 on its own page.
3. **"What closes it is COVERAGE, not a re-run"** — the coverage arrived on 2026-09-06 and did not
   close it. **The cause was wrong, not merely stale**: this rung's population is set by whichever
   pair *wins*, and the winner reaches through a `decision_only` field, so it collapses to the
   renewing subset *however large the book grows*.

All three are now derived from the run — `clears`, `exceeds_its_own_noise_floor` and
`book_magnitude` are arguments. `A49`'s `map_notes` still carry claim 3 in its own words (*"what
closes this is COVERAGE (the pair fields populated on every household)"*) and are now refuted by the
instrument's own artefact.

## What is published, and what is not claimed

The page now renders the whole-book rung beside the headline, never instead of it, carrying **both**
of its readings — because on this rung they point opposite ways:

| | figure | verdict |
|---|---|---|
| selected maximum | +0.1963 vs p95 bound +0.3103 | **does not clear**, p=0.4726 |
| de-biased three-way magnitude | +0.2513 vs floor +0.1628 | **clears its floor**, p=0.01 |

Not a contradiction — different statistics against different nulls, and removing the selection is
what buys the power — but a magnitude published without it beside it converts *"a magnitude over
this population"* into *"a bound"*, which this rung has not earned. The control asserts the
disagreement is rendered when there **is** a magnitude and **absent** when there is not, because a
sentence a panel always emits is boilerplate rather than evidence.

- **A49's gating decision is still not made.** Both rungs are on the surface so it can be made in
  view; choosing whichever rung has a number is the outcome-driven selection the scope mechanism
  exists to prevent.
- **`perceived_bill_saving_gbp` was not reclassified.** Moving a field's declared scope because it
  is the one blocking the winning pair is the same defect wearing the fix's clothes.

## Controls, and that they can fail

Baseline green first; each mutation poisoned separately and the target asserted present before
patching, so no survival is a patch that never applied.

| mutation | killed by |
|---|---|
| generator stops lifting `the_whole_book_rung` | `test_the_generator_LIFTS_the_only_rung_that_can_carry_a_magnitude` |
| page emits the disagreement block unconditionally | `..._WHOLE_BOOK_magnitude_and_its_disagreeing_verdict...` leg 2 |
| page drops the rung's own ceiling verdict | same, leg 1 |
| `"clears its null"` restored as an unconditional literal | `test_the_published_sentence_cannot_ASSERT_a_verdict_it_did_not_READ` |
| `"indistinguishable from nothing"` restored unconditionally | same |
| the coverage cause restored unconditionally | same |

Each of the six fires on a distinct assertion. The prose control asserts **both legs of all three
partitions** — including that a rung genuinely inside its floor is still reported as such, and that
with no answering rung to point at, coverage *is* still named as the honest cause. A repair that
deleted the honest reading along with the stale one would otherwise pass.

## Loose ends, named rather than left to be found

- **A49's `map_notes` still say what closes it is coverage.** Refuted above. A level move is
  recorded and never authorised, so the row is untouched here; the note is the next correction.
- **`site/data/delivery.json` in this tree predates all of it** (`magnitude_refused: null`,
  `households_in_the_book: null`, `p_value: 0.0249`). It regenerates on the publish lane. This is
  why the lift control reads the artefact directly rather than the feed, and does not skip.
- **Whether a whole-book analogue of `perceived_bill_saving_gbp` honestly exists** is open. Every
  term has a rate that replaced a previous one, renewal or not — but the question must be settled on
  the field's own merits and not by the fact that it would unblock a figure.
- **`max(0.0, unit_rate - old_elec_rate)`** at `run_phase2b.py:2149` makes the perceived *saving*
  positive when the new rate is **higher** than the old. Spotted while reading the write site, not
  investigated, not touched. Either a sign error or a naming one, and it feeds the journey
  register's `advance()`.
