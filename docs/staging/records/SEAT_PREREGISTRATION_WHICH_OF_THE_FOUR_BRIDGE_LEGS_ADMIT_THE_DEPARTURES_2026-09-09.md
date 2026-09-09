**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — discharge the survivorship finding against the four legs) · **Class:** measurements_that_mirror

# PRE-REGISTRATION — which of the four bridge legs admit the departures, and how many

Filed **before** `_leg_conditioning` is written or run on any leg. The Lane 0 item states a
premise I intend to refute in part, so the refutation has to be written down before the
measurement rather than after it.

## The premise being tested

The drawn item says:

> *"If the decisions the concordance scores exclude the accounts that departed, then every one of
> those four numbers — including the worse-than-chance estimand — is a statement about survivors
> and not about the book."*

The antecedent is established: `method_skill.survivorship` on the 09-09 run reads 40 dropped for
`the_priced_term_carried_no_settled_row`, 40 of them departures, 0 unattributed, 0 scored
departures. **The consequent does not follow for all four legs**, and which legs it fails for is
the whole question.

## What is NOT yet established, and why it cannot be derived

`fixed_horizon.sample` publishes 10 display rows, not the leg populations. So no per-leg
departure count exists in any artefact on disk, and the arithmetic that looks like it would give
one — `survivorship.decisions_dropped_for_no_settled_row` (40) minus
`fixed_horizon.zero_outcomes_the_world_recorded_as_a_departure` (37) — **is exactly this
project's most expensive shape and I am refusing it.** Those two counts come from two different
funnels with different gate orders: 40 is a drop count in `method_skill`'s funnel, 37 is a row
count in `_fixed_horizon`'s. Their difference is not a quantity, and "3 departures are censored
out" is a sentence I must not write from it. It has to be measured on one key, in one pass.

## The predictions

Graded against the next three-arm run that carries `_leg_conditioning`, on the 09-09 book if the
world digest matches and on whatever book it runs against otherwise.

- **P1** — Leg 0 `the_published_population_ratio_outcome` admits **0** departures.
- **P2** — Leg 1 `settled_only_ratio_outcome` admits **0** departures.
- **P3** — Leg 2 `settled_only_pounds_outcome` admits **0** departures, and exactly the same
  population as leg 1 (it is the same decisions by construction; a difference is a defect here).
- **P4** — Leg 3 `every_priced_decision_pounds_outcome` admits a **non-zero** count of
  departures. This is the prediction that refutes the item's premise if it holds.
- **P5** — Leg 3 admits **37**, and the count of priced decisions the world recorded as a
  departure is **40**, leaving **3 departures excluded from the estimand as well**. This is the
  arithmetic above, re-asked as a measurement on one key; I am recording it as the expected
  answer precisely because I refused to publish it as a derivation. If the measured pair is not
  (37, 40) the derivation was wrong and the refusal was right.
- **P6** — Every departure leg 3 excludes is excluded for
  `horizon_open_at_the_end_of_the_settled_book`, and none for a coverage or join reason. A
  coverage or join reason appearing here is a **defect** in the estimand, not a bound on it:
  it would mean the estimand drops departures for a reason we could fix.

## What each outcome means

**If P1–P4 hold:** the item's premise is refuted for the estimand and confirmed for legs 0–2. The
worse-than-chance figure is a statement about the book, not about survivors — which is what it
was built for — and the three legs above it are survivor cuts that the page must label as such.

**If P4 fails** (leg 3 admits zero departures): the estimand does not do the one thing it exists
to do, the item's premise is confirmed in full, and the 0.4210 reading must be withdrawn from the
page rather than qualified.

**If P6 fails:** the estimand is partly conditioned for a reason we control, and the size of that
residue bounds how much of the worse-than-chance reading survives.

## The declared limit, before the answer

Whatever P5 returns, leg 3 is **not** an unconditioned estimand: censoring removes decisions
before it, and if any of those are departures then the estimand conditions on survival too, just
far less. The honest surface is the count and the share, never "unconditioned". A page that reads
"the estimand admits the departures" without the residue beside it is making the same
over-claim in the opposite direction.

## Independence

The two sides of every count are independent by the same argument `_survivorship` rests on: the
leg population is built from a join against the settled book, the departure is a tally of
`event_type == "churned"` in the world's own event log, and neither is computed from the other.
`_leg_conditioning` must not be given anything derived from `_survivorship`'s output, or the
agreement between them stops being evidence.
