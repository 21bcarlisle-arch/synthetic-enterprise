**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`

# The level is clamped, and the mechanism under it is compressed rather than misdirected

*Delivery seat, 2026-09-03, on the director's instruction to check `ace28fa44` against the
validation ladder. Grades the pre-registration filed beside it
(`SEAT_PREREGISTRATION_WHETHER_THE_YEAR_ANCHOR_RE_EXPRESSES_THE_MECHANISM_2026-09-03.md`).*

---

## 0. First, the correction, beside the claim it corrects

`ace28fa44` — *"the level fit solves onto the band's ceiling, so the loop cannot converge inside
it"* — recommended **keeping the anchor and giving the solver a target with margin**, and escalated
the choice of target to the director as a curriculum value.

**That recommendation was wrong, and it was already ruled out by a canon in this tree.**
`DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31`, rung 1:

> *"The band is a **check** — the world's level is not set to sit inside it; it is measured against
> it. A world whose level sits on the exact edge of the band every year has almost certainly been
> fitted to that edge, and has no headroom to show a change in either direction."*

and §1:

> *"**The one move that is always wrong:** clamping an aggregate to pass a check."*
> *"**Rung failures repair downward, never sideways.** A rung 1 failure is fixed by correcting the
> individual model's attributes or rationale until the emergent level moves — not by scaling the
> aggregate."*

Moving the solver's target from the band's ceiling to its midpoint is a **sideways** repair. It
changes which point the aggregate is clamped to and leaves it clamped. The finding correctly
identified that the ceiling gives the loop no headroom, and then proposed a fix that the canon
forbids — and escalated as a decision something the director had already decided nine days after he
decided it. The escalation was also, as it turns out, structurally incapable of arriving: see
`f67415d62`.

The finding stays in the record. This is the correction next to it.

## 1. The clamp, made visible

Re-fitting `fit_whole_book` on `c6_second_pass_departure_factors.json` (133 renewal rows, 1,313 SVT
rows):

| year | anchor | achieved | published target |
|---|---|---|---|
| 2017 | 7.3726 | 14.0000% | 14.0000% |
| 2018 | 2.9453 | 20.0000% | 20.0000% |
| 2019 | 6.6373 | 21.3000% | 21.3000% |
| 2020 | 6.3798 | 23.0000% | 23.0000% |
| 2021 | 5.5617 | 18.4000% | 18.4000% |
| 2023 | 2.0705 | 12.5000% | 12.5000% |
| 2024 | 4.3317 | 16.1000% | 16.1000% |

**Achieved equals published to four decimal places in all seven fitted years, by construction.**
That is not a validation result; it is the definition of the solver. The band cannot fail, because
the world is bisected onto it. Whatever else is true, this variable does not currently pass rung 1
— it *is* rung 1's stated symptom.

The anchor is algebraically a ratio, and reading `fit_whole_book` says so without any statistics:
`anchor` solves `floor + Σ p(rows, anchor) = accounts × published_rate`, so it is
*(departures the record demands, less what the SVT route already supplies)* over *(how much hazard
the individuals supply)*. It absorbs the record's numerator, the book's denominator, and the
renewal population's size and composition, all in one scalar, per year.

## 2. The pre-registered prediction, graded — NOT CONFIRMED

I predicted **(B)**: the anchor would not track the market terms, |rho| < 0.5.

Measured: Spearman(anchor, `market_switching_multiplier`) = **+0.3214**. Exact permutation null over
all 5,040 orderings of seven years: 95% of |rho| inside [−0.75, +0.75], two-sided **p = 0.4976**.

|rho| is indeed below 0.5 — and **the prediction is graded NOT CONFIRMED**, because constraint 2 of
the pre-registration anticipated exactly this and forbade collecting it:

> *"A rho that does not clear its own null is reported as 'cannot tell', not as (B) confirmed — the
> prediction above is the flattering reading of exactly that outcome and must not be allowed to
> collect it by default."*

At n=7 nothing short of |rho| ≥ 0.75 could have cleared. The measurement was **underpowered by
construction and I did not notice that before running it**, which is the real defect in the
pre-registration: it named the trap and still chose a statistic that could only fall into it. The
second prediction (positive sign if any) is consistent with +0.32 and is worth nothing on the same
grounds.

## 3. What the one-variable experiment did establish

Replace the seven fitted scalars with **one constant** for every year — the shape a bottom-up world
has, where the year-to-year level emerges from the mechanism rather than from a per-year fit — and
sweep it. Per-year emergent level against the published band:

| k | 2017 | 2018 | 2019 | 2020 | 2021 | 2023 | 2024 | in band |
|---|---|---|---|---|---|---|---|---|
| 1.0 | 6.9 | 14.3 | 12.9 | 13.5 | 10.3 | 9.6 | 9.2 | 1/7 |
| 2.8 | 9.1 | 19.6 | 15.8 | 17.1 | 13.6 | 14.4 | 13.0 | **2/7** (best) |
| 4.0 | 10.4 | 22.8 | 17.6 | 19.4 | 15.8 | 17.5 | 15.5 | 1/7 |
| 6.0 | 12.6 | 27.8 | 20.4 | 22.5 | 19.1 | 22.5 | 19.2 | 0/7 |

**Best single constant: 2 of 7 years in band.** No constant does better. The per-year scalar is
carrying real year-to-year work that the mechanism does not supply.

**And the failure is magnitude, not direction.** Ordering of the emergent level against the
published rate: rho = **+0.68** at k=2.8 (p = 0.1095), **+0.79** at k=1.0 (p = 0.0480). Positive and
moderate at every k tried — the mechanism ranks the years roughly as the record does, and at n=7
that is *suggestive and not established*, so it is reported as suggestive. What is not marginal is
the **spread**: the emergent level ranges 9.1–19.6 where the record ranges 12.5–23.0. The
mechanism's response to market conditions is **compressed**, roughly by a factor of two, and
compressed at both ends.

That is a rung 2 result and it is where the repair goes. `market_switching_multiplier` and
`market_opportunity` already move the hazards year to year; they move them too little. The per-year
anchor has been absorbing the difference and, in absorbing it, has made the deficiency
unobservable — which is the canon's whole argument for why a clamped world produces "we cannot
tell".

## 4. What is owed, and what is deliberately not done here

**Nothing in `YEAR_LEVEL_ANCHOR` was edited and no target was moved.** That was constraint 4 of the
pre-registration and it is honoured: this document is a reading.

The repair the canon prescribes is to make the level emerge, and it cannot be finished by choosing
a number. Making it emerge means the hazards carry their own magnitudes, and **that is a
knowledge-layer question before it is a code question**: what published evidence establishes how
much more likely a GB household is to leave in a high-switching year than a low one, at the
household level rather than the market level? Until that is established, replacing seven fitted
scalars with one invented constant would swap a clamp for a number picked because a number was
needed — the failure CLAUDE.md's knowledge-first rule exists to stop. **An honest 2/7 with a named
gap is worth more than a 7/7 that is true by construction**, but only once the mechanism it rests on
has a source.

Specifically owed, in order:

1. **The published evidence for the household-level amplitude of switching response.** Market-level
   switching rates are already in the commons; what is missing is the individual-level dispersion
   that produces them. **CHECKED THE SAME DAY, BEFORE ASSUMING IT WAS A SEARCH: it is not a search,
   it is a GAP THIS PROJECT HAS ALREADY DECLARED TWICE, and neither declaration pointed at the
   other.** `docs/institutional/knowledge_map.md`, the *Customer lifetime / churn* row: *"No
   published per-supplier or per-customer-type loss rates"*. And
   `docs/market_research/continuous_behavioural_engagement_w2_14.md` §3a, item 6: converting the
   engagement measure into an elasticity multiplier is *"an unanchored modelling choice"* with *"no
   direct anchor"*. So the market-level series is settled to H confidence and the individual-level
   dispersion that must generate it is established nowhere — which is precisely why a per-year
   scalar ended up carrying it. The next session should not re-run this search; it should either
   go at the two named sources below or ask the practitioner.

   The closest published things that might actually settle it, named so the next attempt starts
   somewhere rather than in a browser: Ofgem's **Retail Market Indicators** switching series taken
   *from the table, per fuel* (the knowledge map's *UK household switching volumes* row already
   owes this and for a different reason), and the **Ofgem Consumer Survey**, which reports
   switching by engagement segment — a segment-level dispersion is not a household-level one, and
   saying so when it arrives will matter more than having it.

   **And this is the third side of the knowledge rule, not the first two.** CLAUDE.md: a
   practitioner knows what is *too obvious to anyone in the industry to be written down anywhere*.
   How much more likely an engaged household is to switch than a disengaged one in the same year
   is exactly that shape of question. Asking is cheap and a wrong frame compounds.
2. **Then** the mechanism's compression repaired against that evidence, measured by the same
   one-constant sweep in §3 — which is now a repeatable instrument, not an argument.
3. **Then and only then** the per-year table retired, with the band restored to being a red check.

**Prediction, filed now and before step 2 is attempted:** repairing the compression will close most
of the gap but not all of it, and 2017 will be the year that remains out — it is the only year where
the emergent ordering and the published ordering disagree by more than one rank (published rank 2,
emergent rank 1) and its published band is the narrowest in the record at 0.5pp.

## 4a. A correction I owe to the control I named, made after reading it properly

This document's severity header says BLOCKING, and the ruling's definition of BLOCKING is *"a
control or instrument in this area is untrustworthy, or a published figure may be wrong"*. When I
graded it I had `tests/architecture/test_switching_rate_commons.py::test_the_worlds_realised_
departure_rate_is_inside_the_published_band` in mind as the untrustworthy control, and the commit
message that landed this finding says it asserts containment against a band the world is bisected
onto. That sentence is true and the implication I left hanging — that the control is unaware of it
— is not. **Its own docstring says so, at length, and got there before I did:**

> *"NOW IT IS A DRIFT DETECTOR, AND THAT IS NOT A TAUTOLOGY. The anchor is fitted, so of course the
> run it was fitted to sits in the band — the question this asks is whether it STILL does."*

and, on the asymmetry:

> *"So this control answers 'is the world still on its anchor' and reads as though it answered 'is
> the world still lawful'. Those are different questions."*

It also records that room ABOVE the level is 0.00pp in every year because of the ceiling tie-break,
that room BELOW runs 0.50pp to 3.60pp and is set by the calendar rather than by anything meaningful,
and that a red is a threshold crossing and not a magnitude. It is currently **xfail-strict and
xfailing**, held open deliberately rather than left green or quietly widened.

So the control is honest and does the job it claims. **What was untrustworthy was the READING of it
one layer up** — `docs/institutional/knowledge_map.md` opened this variable's row with *"In band in
6 of the 8 full years"* at confidence M-H, which is the drift detector's output presented as a
lawfulness verdict, in the row a session reads before touching anything here. That is corrected at
`b59a844d8`.

The BLOCKING grade stands, on the other limb of the definition rather than the first: the world's
departure level is clamped, and it is published. But it is not this control's fault, and a finding
that let a reader think it was would be doing to that file what the map row did to this one.

## 5. Where this variable stands on the ladder

The canon requires every world variable to say this. The departure level says:

| rung | verdict | evidence |
|---|---|---|
| 0 — red lines | **DOES NOT EXIST** | no wide feasible range; the narrow published band does both jobs |
| 1 — level | **FAILS — clamped** | achieved == published to 4dp in 7/7 fitted years, by construction |
| 2 — mechanism | **DIRECTION SUGGESTIVE, MAGNITUDE FAILS** | ordering rho +0.68 to +0.79 (n=7, not established); emergent spread 9.1–19.6 against a record spread of 12.5–23.0 |
| 3 — heterogeneity | **NOT ASSESSED HERE** | `LADDER_APPLIED_TO_CHURN_2026-08-31` reads AUC 0.6760 against a null of [0.4184, 0.5780] on the churn factors |

Rung 1 moves from `LADDER_APPLIED_TO_CHURN`'s *"PASSES, top-down, and stale"* to **FAILS**. That is
not new damage; it is the same fact graded against the canon that arrived after it was written.

— Delivery seat, 2026-09-03. The prediction in §4 is filed before its answer is known.
