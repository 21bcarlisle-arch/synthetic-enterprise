# C1b — the book lands on the SVT product the world already chose

Delivery seat, 2026-08-30. Direction: *"carry on with R5, C1b and C2's own work"* (console, 18:44Z)
and *"then carry on with C1b"* (19:40Z). Roadmap: `docs/design/CHOICE_AND_CHANNEL_ROADMAP.md`,
corrected order C1a → C2 → C1b. Governing determination:
`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`. Product: `simulation/svt_product.py`
(C1a). Risk family: `simulation/departure_risks.py` (C2).

---

## What was wrong

`simulation/renewal_engagement.rolls_active_renewal` has been called at every electricity renewal
since Phase 33. It returns, in its own docstring's words, *"False if a passive SVT roll"*. It is
per-household, persistent across a tenure, and its population shares are externally anchored (Ofgem
RMI 45/35/20; `PASSIVE_RENEWAL_RATE = 0.35`, cited to the Ofgem Consumer Engagement Surveys and CMA
2016).

**The world computed who had rolled onto the standard variable tariff, wrote the answer into
`event["is_active_renewal"]`, and then built that household another fixed term anyway.** The answer
died at the log. `build_renewal_schedule` never saw it.

So no rule and no constant was owed here. What was owed was to stop discarding an answer the world
already had.

## What landed

**Assignment** (`simulation/renewals.py`). At each term boundary a domestic account reaches, the
builder asks the same function, with the same seed grammar (`{household}_{term_index}`) and the same
per-household engagement probability the run loop uses. Passive → the household spends that
anniversary year on the SVT product, priced off the published Ofgem cap by `build_svt_schedule`,
with no notice served, no rate struck and no renewal offered. Active → a fixed term, exactly as
before. 2022's crisis forcing comes along unchanged.

**The opening label** (`simulation/run_phase2b.py`). `c.get("tariff_type", "fixed")` became
`c.get("tariff_type") or "fixed"`. `population_draw.to_customer_dict` renders the key
unconditionally, so 137 of 146 electricity legs carried it **present with value `None`** and the
default was never reached — section (a) of the determination, re-measured today. This resolves the
**opening** term only; every boundary after it is the roll's. It is therefore not the blanket
`fixed` the determination refused, which was a claim about a whole tenure.

**Departure** (`simulation/svt_product.inertia_hazard_for_term`, rolled in `run_phase2b`). The
interlock `svt_product.py` wrote against itself — *"an account on this product cannot leave… so the
product exists and settles, and nothing is assigned to it"* — is discharged in the same commit as
the assignment, which is the only order R13 permits. The guard lives in a function that returns
`0.0` for any term that is not an SVT segment, so it can be driven by a test rather than reached
only through a decade run.

---

## The numbers, measured and not estimated

### Reachable renewals, before and after

Built over the full window on the live roster, counting every term that is a renewal decision
(term index ≥ 1, not an SVT segment) and asking whether its `tariff_type` is in the company's
`UPLIFTABLE_TARIFF_TYPES = {fixed, pass_through}`:

| | renewals reachable | accounts reachable | measured on |
|---|---|---|---|
| before | **78 of 797** | 9 of 130 | a `git archive HEAD` checkout, clean |
| after | **276 of 276** | 88 of 88 | the working tree |

**THE "BEFORE" ROW WAS FIRST WRITTEN AS 71 OF 790 AND IT IS CORRECTED HERE RATHER THAN QUIETLY
RESTATED.** That reading was taken in the shared working tree with the C1b branch switched off,
which measures this lane plus whatever else was uncommitted around it — the failure this project
already has a name for. Re-measured on a clean `git archive HEAD` checkout, with `sim/cache`
symlinked so the price feed is the same one, the same script reads 78 of 797. The 9-of-130
accounts figure is unchanged. Nothing in the argument moves: 78/797 is 9.8% against 71/790's 9.0%,
and the "after" row is still every renewal that is still a renewal.

Two things happened and they must not be read as one. The gate opened — 78 → 276 priceable
renewals — and **the denominator fell by 65%**, because 521 of those 797 "renewals" were never
renewals: they were households sitting on a default tariff that nobody was going to offer them a
price for. The determination predicted this in advance and put the number at *"the order of a third
of 222 ≈ 70 electricity renewals"*; the realised figure is 276 renewals across a decade on 88
accounts, which is the same third.

**Every renewal that is still a renewal is now priceable.** That is the sentence the value arm was
stuck behind, and it is not a bigger `n` — it is a smaller and honest one.

### Generated fixed/SVT split against the published record

`python3 -m tools.svt_generated_share_check` — domestic electricity account-days, a stock, against
the published domestic fixed share in the determination §(b). **This is a check on the output and is
never an input**: nothing in `simulation/` reads this tool, and there is no dial in it.

| year | fixed | svt | published fixed | |
|---|---|---|---|---|
| 2016 | 100.0% | 0.0% | 0–30% | **OUT** |
| 2017 | 57.4% | 42.6% | 40–46% | **OUT** |
| 2018 | 45.3% | 54.7% | (not reported) | |
| 2019 | 44.7% | 55.3% | 44–46% | IN |
| 2020 | 41.8% | 58.2% | 44–46% | **OUT** (2.2pp low) |
| 2021 | 42.0% | 58.0% | (not reported) | |
| 2022 | 21.5% | 78.5% | 10–20% | **OUT** (1.5pp high) |
| 2023 | 26.9% | 73.1% | 10–20% | **OUT** |
| 2024 | 45.0% | 55.0% | (not reported) | |
| 2025 | 50.5% | 49.5% | 30–36% | **OUT** |

**The steady state is right and it was not fitted.** 42–45% fixed across 2018–2021 falls out of the
anchored 35% active-renewal rate and nothing else; 2019 lands inside the published band and 2020
misses it by 2.2pp. No parameter here was chosen to make that happen, which is the only reason the
agreement is worth anything.

**Four years are out and each has a nameable cause. None of them is a reason to touch a number.**

1. **2016 at 100% fixed.** Every account is *born* on a fixed term, because the roster mints it
   that way and nobody has reached a first renewal yet. The book's OPENING product is not drawn
   from the published distribution — only its subsequent boundaries are. This is the remaining half
   of the determination's repair and it is owed: `population_draw` should mint a share of accounts
   already on SVT at acquisition. It flatters the company in the early years, because a fixed book
   is a priceable book.
2. **2017 at 57.4%.** The same effect decaying: first renewals land through the year.
3. **2023 at 26.9%.** `CRISIS_PASSIVE_YEARS` holds `{"2022"}` only. The published record has fixed
   deals withdrawn until April 2023. Extending the set is a world change with a published reason
   and belongs in its own decision, not folded into this one.
4. **2025 at 50.5%.** A part year (the record ends 2025-06-07) and the crisis cohort's anniversaries
   returning to fixed together.

### Departure

Segment hazards on the real cap calendar come out at 0.045–0.060 per cap quarter, recomposing to
roughly 17–22%/yr before the action-propensity damping — against the published 10–20% band the
hazard is built from. 21 SVT departures over the 2016–2019 window against 16 renewal-point churns.

---

## Corrections and consequences, on the artefact

**The year level anchor is no longer applied to the inertia hazard, and the note that put it there
was wrong about its own magnitude.** `3bf3345de` wrote `level_anchor * svt_inertia *
action_propensity` and reasoned, in the comment beside it, that the realised rate would land ~14%
*below* the published band because `action_propensity` averages 0.8635. That is only the story if
the anchor is about 1.0. It is a per-year table running **1.524 to 4.597**. The first assignment run
printed segment hazards of 0.2532 for a single cap quarter — about 68%/yr against a published
10–20%. The prediction is kept beside its refutation in `departure_risks.py`; what was wrong was the
assumption under it, and it was caught by printing the numbers at real inputs, not by thinking
harder.

The exemption is principled: every other risk in the family is a dimensionless response and
`level_anchor` is the fit that gives the family units. `svt_inertia` already has units — it is a
published annual rate — and the two anchors agree when it is left alone (SVT drift 10–20%/yr against
a whole-population published switching rate of ~15.5%).

**Its cost, stated rather than buried.** The anchor no longer scales every hazard by the same
factor, so within a year it now moves the reason MIX as well as the LEVEL. The module note's claim
is narrowed to the three response risks rather than kept and quietly falsified. **And the anchor is
now over-fitted**: it was fitted on a run where the renewal roll was the only departure route, and
55–58% of domestic account-days no longer reach that roll. `test_the_worlds_realised_departure_rate_
is_inside_the_published_band` is the control that will say so; the repair when it fails is
capture → refit → capture, never a widened band.

**Only the inertia risk fires on an SVT segment.** A household on SVT can in reality also leave over
a bill shock, our price position or our service. All three need per-renewal state the SVT branch
does not compute (`_price_response` needs the felt differential against an offer that was never
made). Omitting them **removes departure routes, which favours the company**, and it is stated here
because it will not be visible in any aggregate. What is *not* true is that SVT accounts leave less
than fixed ones: the inertia band alone sits at or above this book's anchored whole-population level
in most years.

**An SVT departure does not trigger a replacement acquisition.** The renewal-point churn path goes
to market for a replacement; this one does not. The company loses the account and does not spend to
replace it — against the company on revenue, for it on spend, and the net is not asserted here.

**Home move stays out.** C1's declared simplification (C6). The third real route onto SVT — moving
house onto the incumbent — does not exist in this world, so the generated share is short by whatever
that route carries, in the direction that leaves more of the book priceable than reality would.

**SVT departures are in their own list, `svt_departures`, not in `customer_events`.** Putting them in
the shared log crashed the run's own summary on `evt['churn_probability']` — a key an SVT departure
has no business carrying, because there was no renewal decision to estimate a churn probability for.
Twelve consumers index that key unguarded and every one has renewal decisions as its subject. The
repair is *not* `evt.get(...) or 0`, which would put a departure with no renewal into a CLV survival
sum as a customer certain to stay. **Owed, named here rather than left to be found:**
`tools/population_anchor._churn_by_year` and `tools/measure_departure_level` have ALL departures as
their subject and must union the two lists, or they will report a level missing the route this
commit added. Neither is live against the log today (both read captured artefacts), so nothing
regresses on landing; both go stale at the next capture.

**The gas leg is untouched.** The determination's addendum records that a won account's two legs
disagree about whether its product was ever decided — electricity present-and-`None`, gas absent and
defaulting to `fixed`. This commit resolves the electricity leg, which is the arms commodity and the
only one anything reads. The gas leg is still latent and still owed.

---

## Controls

`tests/simulation/test_svt_assignment.py` — the assignment is the world's own roll; an always-active
household never reaches SVT (2022 excepted, and why); SVT is not absorbing; a fixed-term household
is never given the inertia hazard; an SVT departure is not recorded as a renewal; the level anchor
does not scale the published rate. R15 mutations recorded in the file's docstring.

`tests/simulation/test_svt_product.py::test_an_account_on_the_svt_product_can_leave_it` — the
interlock, **re-keyed**. It read the roster for `tariff_type: "svt"` and would have stayed green
through this entire change, because C1b assigns mid-tenure and never touches the roster: a control
keyed to one route while the work arrived by another.
