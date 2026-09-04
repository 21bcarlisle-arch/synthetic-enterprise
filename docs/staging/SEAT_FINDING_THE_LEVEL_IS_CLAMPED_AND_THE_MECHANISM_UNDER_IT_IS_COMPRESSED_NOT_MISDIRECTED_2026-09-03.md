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

---

## 6. Step 1 is worked, and its answer is a gap — appended 2026-09-03, later the same day

§4 item 1 named two sources and said the next session should go at them or ask the practitioner.
Both were done. **Neither settles it**, and the reading is
`docs/market_research/household_switching_response_amplitude.md`.

- **Ofgem Retail Market Indicators** gives a per-fuel *count* (243,754 electricity / 183,180 gas,
  April 2026). It settles the fuel-scope conversion the knowledge map owed for a different reason —
  a both-fuel numerator is ≈1.75× its electricity leg — and it establishes nothing about dispersion,
  because there is no household in it.
- **Ofgem/Ipsos Consumer Survey 2021** (n = 4,037, fieldwork 19 Aug – 17 Sep 2021) defines its
  *engaged* segment as *"switched supplier, tariff, or compared in the past 12 months"*. **The
  engaged-vs-disengaged switching ratio is therefore infinite by construction.** §4 above wrote that
  a segment-level dispersion is not a household-level one and that saying so when it arrived would
  matter more than having it. That was right about the direction and understated the problem: the
  segmentation named *engagement* is the switching outcome under a different name, so the route is
  **closed, not merely coarse**. What the survey does carry is a between-group *level* ratio of at
  most **1.94×** (16–34 at 33% against social tenants at 17%), self-reported, one cross-section, and
  over-stating the market level by about 1.5×. A level ratio between household types is not a
  response amplitude across years, and substituting it would be dividing two numbers whose ratio is
  not a quantity.

**The practitioner question is asked**, on NTFY, with the recommendation attached (do not invent it;
keep the per-year anchor declared as a clamp meanwhile; prefer a structural route — make the
response amplitude a function of the savings actually on offer to the household, which is already
observable in-world — over another search). **Nothing in `YEAR_LEVEL_ANCHOR` was edited,
`fit_whole_book` was not touched and no constant was chosen**, which was constraint 4 and is honoured
a second time.

**The three declarations of this gap now point at each other**, which they did not before:
`docs/institutional/knowledge_map.md` *Customer lifetime / churn* row,
`docs/market_research/continuous_behavioural_engagement_w2_14.md` §4 item 6, and the new file as
their single home. The *world's departure LEVEL* row's own "Next question" cell also carried the
claim that the Consumer Survey *"carries switching by engagement segment, which is the closest
published thing to a dispersion"* — **that claim is now refuted and is corrected in place, beside
itself.**

**Items 2 and 3 of §4 remain owed and this finding stays BLOCKING.** The prediction filed in §4
(that repairing the compression closes most of the gap but not all, and that 2017 is the year that
remains out) is untouched and still unanswered: step 2 has not been attempted.

## 7. The band is now a check the world can fail, and it fails it — landed 2026-09-04

The drawn direction's *"finished when"* was: **the band is a check the world can fail and the record
says plainly which years it fails.** That half is landed. The mechanism repair under it (§4 item 2)
is not, and is still gated on the gap §6 established.

**What the reading was missing, and it was not the measurement.** §3 measured the emergent level and
§4 called the one-constant sweep *"a repeatable instrument, not an argument"*. It was neither, quite:
`emergent_level_sweep` printed a table inside `tools/fit_year_level_anchor.main` and **nothing in the
tree could read it**. A measurement that exists only on a terminal cannot go stale loudly, cannot be
cited and cannot be a check — so the world's only standing band verdict remained the one taken off
the fitted anchors, where `achieved == published` to four decimals by construction. The gap between
"we have measured this" and "the tree carries it as a check" is the whole of what landed here.

**What is on disk now.**

- `tools/fit_year_level_anchor.emergent_level_verdict` — the rung-1 verdict at
  `NO_LEVEL_CORRECTION`. That anchor choice is the load-bearing one: 1.0 is the multiplicative
  IDENTITY and this tree already establishes it as *"the arithmetic form of 'no calibration is
  identified'"*, so the measurement **invents nothing**. The best single constant (k≈2.8) reads
  better — 2 of 7 rather than 1 of 7 — and is a number with no source, so it is deliberately not
  what the verdict is taken at. Swapping seven fitted scalars for one invented one is trading a
  clamp for a placeholder.
- `docs/reports/departure_level_rung1_verdict.json`, committed, written by
  `python3 -m tools.fit_year_level_anchor --emergent-verdict` — which writes on the **refused**
  outcome too, because a producer whose only failure mode is to write nothing leaves the previous
  run's file looking current. That is the catalogued *a fix that removes one cause of a silent
  absence leaves the absence*, avoided at the site rather than discovered later.
- Three legs in `tests/architecture/test_switching_rate_commons.py` and two mutations.

**The verdict, on `c6_second_pass_departure_factors.json`:**

| year | band | emergent % | pp outside |
|---|---|---|---|
| 2017 | 13.5–14.0 | 6.95 | **−6.6** |
| 2018 | 19.5–20.0 | 14.32 | **−5.2** |
| 2019 | 20.7–21.3 | 12.90 | **−7.8** |
| 2020 | 22.5–23.0 | 13.51 | **−9.0** |
| 2021 | 17.9–18.4 | 10.27 | **−7.6** |
| 2023 | 8.9–12.5 | 9.57 | in band |
| 2024 | 12.5–16.1 | 9.19 | **−3.3** |

**Six of seven, every one of them LOW, by 3.3pp to 9.0pp.** Against 7 of 7 in band under the fit.
That is the same fact §3 established; what is new is that it is now the tree's own answer rather
than this document's, and `simulation/departure_level_anchor.py` carries it beside
`YEAR_LEVEL_ANCHOR` with the block declared as a clamp in as many words.

**The controls, and what each is keyed to** — deliberately split, because they fail for different
reasons and a reader must be able to tell which:

1. `test_the_rung_1_verdict_is_measured_on_the_world_the_fit_did_not_touch` — **cannot go stale.**
   It asserts nothing about which years pass or how many; only that the verdict's anchor is the
   identity and identically not one of the solver's outputs. It exists because the next session
   repairing the compression will be tempted to re-measure "the emergent level" at the best
   constant, since 2/7 reads better than 1/7 — and that is the clamp returning under a longer name.
2. `test_the_committed_rung_1_verdict_still_reproduces_and_names_every_year_it_fails` — a drift
   detector over a **declaration**, the shape `test_every_declared_svt_floor_reproduces_under_the_
   hazard_the_world_actually_runs` already uses here. It reds **in either direction**: a repair that
   brings 2019 in reds exactly as hard as a regression that pushes 2023 out, because the record has
   stopped being true in both cases. Mutation-proven on disk, not by argument — perturbing 2024's
   declared level to 13.0 fires it with the live 9.1911 in the message.
3. `test_mutation_l_...wired_to_the_world_and_not_to_the_file` — scales the anchor the live reading
   is taken at and requires **every** year to move, and to move UP. Without it the leg above could
   compare a committed file against a reading that had come loose from the world and pass forever,
   which is the catalogued *a control whose PASS branch is unreachable reports a constant verdict*.

**What this does NOT claim.** It does not claim rung 1 passes — it does not. It does not touch
`YEAR_LEVEL_ANCHOR`, move a solver target, or choose a constant, so §4's constraint 4 is honoured a
third time. The clamp is still the world's live level and is still what every arm comparison sits
on; what changed is that it can no longer travel without its unclamped reading beside it, and the
six failures are now a fact the tree asserts rather than a paragraph in a staged document.

**Noticed while running the suite, and it is not this finding's subject.**
`docs/reports/c2_departure_factors_svt_segment_decisions.json` is **untracked** in the shared tree.
`tests/architecture/test_a_departure_reading_declares_its_population.py` passes at clean HEAD and
fails in the working tree because of it — `declare()` finds the sibling, so the file chosen as the
one-route fixture reads as two-route and the null control's two arms collapse. That is this repo's
*green at HEAD, red in the shared tree* shape arriving from an artefact nobody committed, and it is
exactly what `untracked_capture_refusal` exists to name. Recorded here rather than minted as its own
document because the parked class already covers it
(`CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md`).

**Still owed, unchanged:** §4 items 2 and 3, both gated on the amplitude gap in §6. The §4 prediction
(most of the gap closes, 2017 remains out) is still filed and still unanswered — and it is now
checkable against something, which it was not this morning.

— Delivery seat, 2026-09-04.

## 8. The diagnosis in §3 was wrong about WHICH LEG, and the measurement is beside it — 2026-09-04

§7 landed the rung-1 verdict: six years of seven, all LOW. It did not say where the miss comes
from. §3 and §4 did, and **they guessed**:

> *"`market_switching_multiplier` and `market_opportunity` already move the hazards year to year;
> they move them too little."*

That sentence sent this project after the household-level amplitude of switching response, which
§6 then established is a gap declared in three places and settled by nothing — and put to the
director as a practitioner question. **The guess is now measured, and it is refuted.**
`tools/fit_year_level_anchor.route_amplitude_attribution`, committed at
`docs/reports/departure_level_route_attribution.json`:

| route | relative slope vs the record | 95% interval | decisions | share of the level |
|---|---|---|---|---|
| **SVT route** | **+0.99** | [+0.88, +1.11] | 1,022 | 70.5%–87.2% |
| **renewal route** | **−0.08** | [−0.45, +0.31] | 118 | 12.8%–29.5% |

Relative slope is dimensionless and taken at the means: **1.0 is a route that tracks the record
proportionally, 0.0 is a route that does not move with it at all.** The SVT route's interval
excludes 0.0 and contains 1.0. The renewal route's interval contains 0.0 and **excludes 1.0**.

**The route where `market_opportunity` acts is the flat one.** It contributes a near-constant
1.2–3.1pp whatever the record did. `market_opportunity` reaches the bill-shock and price-position
hazards and nothing else, so no value of the household amplitude gap can move an amplitude that
leg does not carry — and the counterfactual says so as a bound rather than a trend. Scaling both
opportunity hazards by 2, 4 and 8 takes the world's relative slope from +0.78 **down** to +0.26;
setting them to `WORLD_MAX_CHURN_PROBABILITY` for every renewal household in every year — the most
that leg can ever do — leaves **relative slope +0.09 and 0 of 7 years in band**, at levels of 35pp
to 47pp. Adding a constant to a proportional quantity dilutes it. The repair §4 prescribed makes
the amplitude monotonically worse all the way to its ceiling.

**Why nobody could see this.** The level and the amplitude had never been separated, and a world
short on both looks like a world with one problem. §3 read the emergent spread (9.1–19.6 against a
record spread of 12.5–23.0), correctly called it compressed, and attributed the compression to the
only year-to-year mechanism anyone had in mind. The compression is real; it is `0.49 × record +
2.39`, and the 0.49 is the SVT route delivering the right SHAPE at about half the level while the
renewal route adds a flat intercept. The 2026-09-01 repair that wired `market_switching_multiplier`
into `svt_inertia_hazard` (see `svt_market_invariance_refusal`, discharged) worked, and worked
well — the route it fixed is the one now carrying the record's movement almost exactly.

**§4's prediction, graded, beside itself.** It said repairing the compression would close most of
the gap but not all, and that 2017 would be the year that remains out. **REFUTED for the repair it
was filed against**: the ceiling counterfactual is that repair at its maximum, it closes none of the
gap, and 2017 is not distinguished — all seven years leave the band, high. It stays *unanswered*
for the repair that now looks binding, because that repair has not been attempted and its subject
is a different leg. A prediction filed against a route that turned out not to exist cannot be
collected either way, and it is not quietly retired here.

**What this does and does not change in what is owed.**

- **§4 item 1 / §6's gap is still a real gap and is no longer on rung 1's critical path.** The
  household-level amplitude of switching response is unestablished, three declarations point at
  each other, and the question is with the director. Nothing here withdraws it. What is withdrawn
  is the claim that supplying it repairs the level — it does not, whatever its answer.
- **§4 item 2 is re-aimed, not discharged.** The mechanism's debt is the SVT route's LEVEL: it
  carries 41%–56% of the record's departures per year with a year-to-year shape that is right. The
  next question is which of the three things under that is short — the hazard per SVT decision, the
  size of the SVT population, or the routing that decides who reaches which route — and it must be
  measured before it is guessed at, which is what §3 did not do.
- **The question to research changed shape and got easier.** It is no longer a household-level
  dispersion nobody publishes. It is a COMPOSITION question — what share of GB domestic switches
  originate from default/SVT households against households reaching a fixed-term contract end —
  and Ofgem publishes both a default-tariff share and switching by tariff type. That is a search
  worth running, and it is the one this finding should have asked for.

**Nothing in `YEAR_LEVEL_ANCHOR` was edited, no solver target was moved and no constant was
chosen.** §4's constraint 4 is honoured a fourth time. The attribution is measured at the
multiplicative identity for a reason specific to it: the per-year anchor acts on the renewal route
alone, so the same arithmetic run under the fit would show the renewal route carrying exactly the
movement the solver put there, report the opposite conclusion and look entirely reasonable.
`test_the_attribution_is_measured_on_the_world_the_fit_did_not_touch` refuses that by construction.

Five legs in `tests/architecture/test_switching_rate_commons.py`, four of them mutation-proven on
disk: a perturbed slope, a fitted anchor declared, a broken partition, and the artefact deleted
each fire the leg that owns them.

**This finding stays BLOCKING.** The world's level is still clamped and still published. What
changed is that the repair is now aimed at the leg that carries the defect.

— Delivery seat, 2026-09-04.

## 9. The SVT route's level is short in the HAZARD, and the other two legs cannot reach it — 2026-09-04

§8 re-aimed the repair at the SVT route and named three candidates under it — *"the hazard per SVT
decision, the size of the SVT population, or the assignment that decides who reaches which route"* —
and said they must be measured before they are guessed at. **They are now measured.**
`tools/fit_year_level_anchor.svt_route_shortfall_decomposition`, committed at
`docs/reports/svt_route_shortfall_decomposition.json`, at `NO_LEVEL_CORRECTION` on
`c6_second_pass_departure_factors.json`.

**§8's three were not the right three, and that is the first result.** On a capture, "the size of the
SVT population" and "the assignment that decides who reaches which route" are ONE quantity — an
account reaches the SVT route in a year exactly when it is on the SVT product in that year — and the
factor the pair leaves out is **exposure**: how much *of* the year a reached account spends on the
product. The arithmetic decomposition is exact:

> `svt_pp_of_book  =  100 × reach × exposure × hazard`

`reach` = accounts taking an SVT decision over accounts on the book. `exposure` = SVT segment-days
per reached account over 365.25. `hazard` = expected departures per SVT-account-**year** of exposure,
which is the unit `SVT_INERTIA_ANNUAL_RECENT` is published in and therefore the only unit in which
the world and its own source can be compared at all.

| year | reach | exposure | hazard | SVT pp | needs × | headroom: reach / exposure / hazard |
|---|---|---|---|---|---|---|
| 2017 | 0.672 | 0.643 | 0.1327 | 5.74 | 2.14 | 1.49 / 1.55 / 7.16 |
| 2018 | 0.840 | 0.697 | 0.1908 | 11.17 | 1.46 | 1.19 / 1.44 / 4.98 |
| 2019 | 0.707 | 0.806 | 0.1972 | 11.25 | 1.69 | 1.41 / 1.24 / 4.82 |
| 2020 | 0.783 | 0.762 | 0.1910 | 11.39 | 1.79 | 1.28 / 1.31 / 4.97 |
| 2021 | 0.784 | 0.749 | 0.1414 | 8.31 | 1.92 | 1.27 / 1.33 / 6.72 |
| 2023 | 0.981 | 0.736 | 0.0935 | 6.75 | 0.90 | 1.02 / 1.36 / 10.15 |
| 2024 | 0.772 | 0.785 | 0.1146 | 6.94 | 1.48 | 1.30 / 1.27 / 8.29 |

`needs ×` is taken at the band's **LOW** endpoint — the least the record will accept — because the
question is whether a factor can *possibly* close the gap and the honest form of "possibly" is the
most generous one. All three endpoints are in the artefact and the ordering does not turn on the
choice.

**The question is not which factor is small. All three are. It is which factor has the HEADROOM.**

- **reach** is already 0.67–0.98 of the book. Its ceiling is 1.0. **Closes 1 year of 7** — 2023,
  whose band is the widest in the record.
- **exposure** is already 0.64–0.81 of the year. Its ceiling is 1.0. **Closes 1 of 7**, the same year.
- **hazard** is 0.094–0.197 per account-year against a ceiling of `WORLD_MAX_CHURN_PROBABILITY`.
  **Closes 7 of 7.**

**The bound that makes this decisive rather than suggestive**, and it is the same shape as §8's
ceiling counterfactual. Take BOTH bounded factors to their ceilings at once: the entire book on the
SVT product, every day of the year. That world has no renewal decision left to price, so the renewal
route contributes nothing and the SVT route must carry the whole band alone — and at the hazard this
world runs it reaches the band's low endpoint in **1 year of 7**. *The two factors §8 named cannot
close rung 1 between them, at any value they are capable of taking.* That does not depend on how the
residual is apportioned, and it does not depend on what the composition question's answer turns out
to be.

**So the leg is the hazard per SVT-account-year, and the gap is 1.6×–1.7× against the world's own
published source.** `svt_inertia_hazard` re-references the published 0.20 recent / 0.10 long-stayer
pair by `market_switching_multiplier / svt_inertia_base_multiplier()`. That divisor is the *mean* of
the multiplier over `SVT_INERTIA_BASE_WINDOW`, so the factor is 1.0 **across** the window and not
within each of its years — 0.962 at 2019 and 1.040 at 2020, against 0.56–0.90 everywhere else. In
those two years the world is running the published rate to within 4%, and its tenure mix there is 0%
and 16% long-stayer, so almost every decision is on the 0.20 branch. The record needs **0.334 at 2019
and 0.342 at 2020**, against a published 0.20: **1.67× and 1.71×**. Both ratios are published — against
the published rate and against the re-referenced rate the world actually ran — because they differ by
that 4% and quoting one as the other is the shape this repo pays for.

*(The first draft of the control on that block asserted the per-year re-referencing factor was 1.0,
which is what the constant's own docstring reads like. It is 0.962 at 2019 and the leg went red on
its own first run. The claim above is the corrected one; the control now holds the property that is
actually true — the window's factors average to 1.0 and every year in it is nearer 1.0 than any year
outside it — rather than a distance from 1.0 written down to go stale.)*

**Nothing here picks a number.** No constant was edited, no solver target was moved, no anchor was
touched; §4's constraint 4 is honoured a fifth time. The gap is published in the units of the
constant that would have to move, so the next session can take it to the published record rather than
to a slot. And the source itself says what that next step is: `svt_rates_active_passive_2016_2025.md`
§4 calls the pair a **structural inference at confidence M**, states plainly that *"direct published
SVT vs fixed churn rates by tariff type are not available"*, and its own band for the recent-SVT
segment tops out at 20% — the value the world took. A rate 1.7× that is outside what the source can
supply, so the question is not "raise the constant" but **whether 0.20 is the right published quantity
for what this hazard models at all**: the hazard is drift off the SVT *product*, and the band it is
being asked to reproduce is external change of *supplier*. Those are not the same event, and nobody
has established the relation.

**What this does to the composition question.** §8 sent the next session to source what share of the
GB domestic book sat on a default/SVT tariff each year — the same question as focus item
`the-arms-reach-is-a-missing-world-product-not-a-company-choice`. That sourcing is still worth doing
and its answer is still owed, **and it is now known in advance not to repair rung 1**: `reach` is the
factor it would move, `reach` closes 1 year of 7 at its arithmetic ceiling, and this world's reach is
0.67–0.98 — already at or above any published default-tariff share. If the sourcing comes back saying
the real share was lower, the world's reach is too HIGH and the hazard gap widens. The composition
question is a fidelity question with its own worth; it is not this repair.

**Six legs in `tests/architecture/test_switching_rate_commons.py`, all six mutation-proven on disk:**
a perturbed factor breaking the identity, a factor credited with a year its own ceiling cannot reach,
the renewal route left inside the saturation bound it abolishes, the reading taken under a fitted
anchor, the published-rate comparison extended past the window where it is a comparison, and the
committed file drifting from the live world. `test_mutation_o` additionally requires the *required
multiple* to FALL when the renewal anchor rises — the one direction that distinguishes a residual
taken from the renewal route from a cached column.

**This finding stays BLOCKING.** The world's level is still clamped and still published. What changed
is that the repair is now aimed at a single named quantity, with the size of its gap measured and the
sourcing question that governs it stated.

— Delivery seat, 2026-09-04.

## 10. The composition question is sourced, and it closes nothing — 2026-09-04

§8 sent the next session to source what share of the GB domestic book sat on a default/SVT tariff
each year, and §9 said in advance what it expected that to do. **It is now sourced, the world is
measured against it, and both of §9's statements about it were wrong in the same way.** The sourcing
is `docs/market_research/gb_domestic_default_tariff_share_2016_2025.md`, its numbers have one home in
`tools/published_tariff_mix.py`, and the counterfactual is committed at
`docs/reports/svt_composition_vs_published.json`, measured at `NO_LEVEL_CORRECTION` on the same
capture as §9.

The pre-registration for this is
`SEAT_PREREGISTRATION_WHETHER_THE_WORLDS_SVT_ACCOUNT_DAY_SHARE_SITS_ABOVE_OR_BELOW_THE_PUBLISHED_ONE_2026-09-04.md`,
filed before the sourcing. It is graded here, all four, beside the result.

### The headline: composition at the published share closes nothing

| year | world SVT share | published | ×  | band low | rescaled | held |
|---|---|---|---|---|---|---|
| 2017 | 0.433 | 0.636 | 1.47 | 13.5 | 9.22 | 9.65 |
| 2018 | 0.585 | 0.586 | 1.00 | 19.5 | 14.32 | 14.32 |
| 2019 | 0.570 | 0.586 | 1.03 | 20.7 | 13.14 | 13.20 |
| 2023 | 0.722 | 0.900 | 1.25 | 8.9 | **9.43 ✓** | **11.24 ✓** |
| 2024 | 0.606 | 0.860 | 1.42 | 12.5 | 10.65 | 12.10 |

*2020 and 2021 are REFUSED, not scored: no published figure is established for either and the gap
spans the crisis, so interpolating it would manufacture a reading in the two years the world is
hardest to check. The denominator here is 5 of 7 and is reported as 5.*

One of five reaches the band — and **2023 was already reaching it before the counterfactual ran**
(its `required_multiple.at_band_low` in §9 is 0.90, below 1). `years_newly_closed_by_composition` is
**empty on both accountings and on both published bases**. Two accountings are published because the
choice could otherwise pick the verdict: `renewal_rescaled` moves the renewal route down as the SVT
route moves up, which is the consistent one and the headline, because an account-day put onto SVT is
an account-day taken off a fixed term; `renewal_held` is arithmetically incoherent and is reported
because it is the most generous thing composition could possibly do. Neither closes a year.

**This confirms §9 and strengthens it.** §9's bound was at the arithmetic ceiling — the whole book on
SVT every day — and a ceiling bound can be vacuous. This is the same conclusion at the value the
record actually published, which is a much smaller move and a real one. The hazard per
SVT-account-year is still the leg.

### §9 was wrong about the direction, and about which quantity to compare

§9 said: *"this world's reach is 0.67–0.98 — already at or above any published default-tariff share.
If the sourcing comes back saying the real share was lower, the world's reach is too HIGH and the
hazard gap widens."* **Both halves are refuted.** The published share is *higher* than §9 assumed,
and the world's share is *below* it in every year that can be compared — the opposite sign.

The cause is a defect this repo has a rule about. `reach` is decisions over accounts; the published
statistic is a **stock**, the share of accounts on a default tariff on a given day. Those are not the
same quantity, and their ratio is not one either. The comparable figure is `reach × exposure` —
account-days over account-days — which is **0.43–0.72**, not 0.67–0.98. §9 divided before saying what
each number counted, and the flattering reading is the one it got.

### The sourcing's own first result: it was already in the tree, three times

The item read as a research task and was mostly a reconciliation task. The same Ofgem series was
already held as prose in `svt_rates_active_passive_2016_2025.md` §2–3, as a table in
`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` §(b), and as a Python dict in
`svt_generated_share_check.PUBLISHED_DOMESTIC_FIXED_SHARE`. None cited the others; this finding cited
none of them; and two focus items were each about to source it again. That is the VAT shape, and the
note on the focus item that exists to prevent it was written *after* it had already happened.

**And the copies were wrong in a way that matters.** Ofgem's headline default share for 2017–2019
excludes prepayment; >90% of prepayment customers are on a default tariff and prepayment was ~15% of
GB customers. All three copies dropped the qualifier. Restoring it moves 2019 from 53% to ~59% — and
**it reverses this world's verdict for 2018 and 2019**, which read *above* the record on the
as-published basis and *below* it on the restored one. Which basis is right is not settled and is
deliberately left open: this world models no prepayment meter, so its book is neither published
population. Both bases are carried and every caller names which it used.

### The pre-registration, graded

- **P1 — CONFIRMED, and for the reason it predicted.** §9's sentence is refuted, and refuted because
  it compared `reach` against a stock. Predicted the world would be below published in at least four
  of seven fitted years and that the sentence would survive only for 2019 and 2020: it survives for
  **2018 and 2019 on the as-published basis only**, and survives nowhere on the all-domestic basis.
  The year-naming was half right — 2019 yes, 2020 has no published figure at all and could not have
  been graded either way, which the prediction should have anticipated and did not.
- **P2 — CONFIRMED.** `simulation/svt_product.py`'s docstring predicted the generated SVT share would
  come out low against the published one, before any of it was measured. It does, in every comparable
  year. This is the first time that sentence has been checked against a number.
- **P3 — REFUTED for 2024, and by a long way.** Predicted 65–80%; the sourced figure is 80–86%,
  derived from Ofgem's explicit "twice the proportion recorded in July of the previous year" against
  ~one-third at July 2025. 2024 is the worst year in the whole comparison, at −25 to −31pp, and the
  interpolation would have hidden that. 2018 (predicted 52–60%, sourced ~59%) is inside; 2021 could
  not be graded because it is a declared gap.
- **P4 — CONFIRMED.** No new published series was needed for 2016–2023 or 2025; the deliverable is
  the reconciliation and the control, as predicted. One genuinely new figure was found (2024) and one
  genuine correction (prepayment), neither of which P4 anticipated — it was right that the answer was
  in the tree and wrong that nothing new would come of looking.

### A correction to the docstring I shipped this reading with

The first draft of `published_composition_counterfactual`'s docstring stated that 2024 would reach
the band on the generous accounting and miss on the consistent one. That was hand arithmetic against
the *schedule*-derived SVT share (0.55) rather than the *capture*-derived one (0.606) the reading
actually rescales. Run at real inputs it misses on both, 12.10 and 10.65 against 12.5. Corrected in
the docstring itself rather than in a footnote, and caught by printing the table before shipping the
prose — which is the only reason it was caught at all.

### Controls

Seven legs added to `tests/architecture/test_switching_rate_commons.py`, all seven mutation-proven on
disk: a counterfactual crediting itself with a year it inherited; a refused year filled by
interpolation; the prepayment restoration dropped (and applied twice); a complement band with its
endpoints inverted, which is a silent always-fail rather than a crash; `simulation/` importing the
check band it is judged against; the rescaled accounting holding the renewal route fixed; and the
committed reading drifting from the live world. `test_mutation_q` additionally moves the anchor and
requires the renewal route to rise while the SVT share does not — the one direction that separates a
reading recomputed from the world from a cached column.

**Nothing here picks a number.** No constant was edited, no solver target moved, no anchor touched;
§4's constraint 4 is honoured a sixth time.

**This finding stays BLOCKING**, and the repair is where §9 left it: the hazard per SVT-account-year,
and the question of whether `SVT_INERTIA_ANNUAL_RECENT = 0.20` — drift off the SVT *product* — is the
right published quantity for a band made of external changes of *supplier*. Composition is now
measured, sourced and out of the way, and it is a fidelity debt in its own right rather than this
repair.

— Delivery seat, 2026-09-04.

## 11. The published record cannot adjudicate the hazard, and it says which quantity would — 2026-09-04

§9 and §10 both closed on the same sentence: *"the question is not 'raise the constant' but whether
0.20 is the right published quantity for what this hazard models at all."* **That question has now
been asked of the record directly, and the record's answer is "I cannot tell you, and here is
exactly what would."** `tools/published_route_split.py`, committed at
`docs/reports/published_route_split.json`. **There is no world in this reading** — three published
series composed against each other — except one labelled section that reads §9's committed artefact.

The pre-registration is
`SEAT_PREREGISTRATION_WHETHER_THE_PUBLISHED_SEGMENT_RATES_COMPOSE_TO_THE_PUBLISHED_BAND_2026-09-04.md`,
filed before the module existed. All five are graded below, beside the result.

### The identity, and why it admits a line rather than a point

> `R(y)  =  s(y) · H_svt(y)  +  (1 − s(y)) · H_fixed(y)`

`R` is the commons' band — GB domestic **electricity changes of supplier** over all GB domestic
electricity accounts, whose own numerator field says *"NOT tariff switches within the same supplier,
which Ofgem's survey instruments do count and which are a different quantity."* `s` is §10's
published default-tariff share. One equation, two unknowns.

**And `H_fixed` is not 0.35.** `svt_rates_active_passive_2016_2025.md` §4's *"fixed at expiry →
active switch ~35%"* counts households actively renewing onto **a new fixed deal**, of whom an
unestablished share stay with their existing supplier. So `H_fixed = 0.35 · φ`, and **φ — the
external share of active fixed-term renewals — is the quantity nothing published establishes.**
`EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` is `None` in the tree and
`test_the_external_share_of_active_renewals_stays_a_declared_gap` keeps it `None`.

### The result: the admissible interval contains both candidate answers

| year | band % | published share (all-dom.) | admissible `H_svt`, φ∈[0,1] | world's required (§9) |
|---|---|---|---|---|
| 2017 | 13.5–14.0 | 0.620–0.636 | **0.003 – 0.226** | 0.2841 — **REFUSED** |
| 2018 | 19.5–20.0 | 0.586 | 0.085 – 0.342 | 0.2793 ✓ |
| 2019 | 20.7–21.3 | 0.569–0.586 | 0.098 – 0.375 | 0.3340 ✓ |
| 2022 | 2.9–4.3 | 0.800–0.900 | **−0.051 – 0.054** | not a fitted year |
| 2023 | 8.9–12.5 | 0.800–0.900 | 0.024 – 0.156 | 0.0842 ✓ |
| 2024 | 12.5–16.1 | 0.800–0.860 | 0.069 – 0.201 | 0.1692 ✓ |

*2016 and 2025 are scored and omitted from this table only because they are not fitted years; they
are in the artefact. **2020 and 2021 are REFUSED**, not scored — §10's declared gaps, still not
interpolated. The denominator is 8 scored of 10 banded, and 5 of 7 fitted.*

**At 2019 the record admits everything from 0.098 to 0.375. The published 0.20 is inside it. The
world's required 0.334 is inside it. The record cannot tell them apart**, and the width is not
looseness in the arithmetic — it is φ sweeping [0, 1]. **This is a "we cannot tell", and it is the
result.** §9's gap of 1.67× is real and it is not, by itself, evidence that the source is wrong.

### Three things the record does say, none of them predicted

1. **The record REFUSES φ = 1 at 2017 and 2022.** Where `H_svt` at φ = 1 comes out negative, the
   fixed route at its published ceiling *alone* already exceeds the whole published band. That is
   the only place published evidence constrains φ from above at all, and it is why the endpoint is
   reported negative rather than clipped to zero —
   `test_a_negative_admissible_endpoint_is_reported_and_never_clipped` holds that, because a clip
   turns a refusal into a boundary and the reader cannot tell the two apart.

2. **The two repairs are not additive, and 2017 is where that shows.** §9's `required_hazard` was
   computed holding the world's *own* SVT share fixed — and §10 then measured that share as **below**
   the published one. So "raise the hazard to what §9 requires" and "correct the share to published"
   are not two independent repairs that can both land: applied together at 2017 they **overshoot the
   record**, needing φ of −0.227 to −0.146 (as-published) or −0.360 to −0.270 (all-domestic). The
   record refuses the pair. Nothing said this before, because §9 and §10 each held the other's
   subject fixed, and this is the interconnection question the seat is the only place able to ask.

3. **2022 binds the constant hard and nobody had noticed.** Admissible `H_svt` there is
   −0.051 to 0.054 — **`SVT_INERTIA_ANNUAL_RECENT = 0.20` is refused by the record at 2022 by
   roughly a factor of four.** 2022 is not a fitted year so this does not bear on rung 1, but it is a
   published constraint on a live world constant and it is filed here rather than acted on.

### The pre-registration, graded

- **P1 — REFUTED**, and filed weak on purpose because I had hand-derived its direction. Predicted
  the published pair at φ=1 would overshoot in **every** comparable year on both bases. It overshoots
  robustly — on *every* tenure mix — in **2 of 8**: 2017 and 2022. At the one published tenure mix it
  overshoots in 4 of 8 (as-published) and 3 of 8 (all-domestic), and **overlaps** the band elsewhere.
  The cause of my error is the substitution this module exists to refuse: I composed at
  `H_svt ≈ 0.17`, which is the *world's* near-0.20 value, instead of the published tenure-composed
  **0.0942–0.1442**. A hand check that borrows the world's number to test the world is not a check,
  and it produced the flattering answer here exactly as it did in §9.
- **P2 — CONFIRMED, and narrowly enough that it should not be counted as skill.** Predicted the φ
  admitting the world's required `H_svt(2019) = 0.334` would be below 0.25. It is **0.182–0.249** on
  the as-published basis — inside by 0.001 — and **0.079–0.153** on the all-domestic basis. One
  rounding in the share and the as-published half of this reads the other way.
- **P3 — CONFIRMED, in all 8 scored years on both bases.** The record's lower bound on `H_svt`,
  taken at φ = 1, is below 0.20 everywhere: 0.077, 0.003, 0.085, 0.098, −0.051, 0.024, 0.069, 0.027
  (all-domestic). **The published 0.20 is not a floor the record insists on**, so "the world needs
  1.7× its own source" is not by itself evidence against the source.
- **P4 — CONFIRMED.** φ is established nowhere in this tree. And the adjacent record was already
  here: `gb_switching_rate_denominators.md` §7 notes Ofgem's CIM wave 6 is *further* from the
  reason-split question *"because its population includes internal tariff switches"* — the same
  instrument, the same shortcoming, written down weeks ago and never connected to this question.
  That is the §10 shape again, one degree weaker: not a duplicated number this time, but a known
  limitation of a known instrument that nobody had pointed at the question it settles.
- **P5 — CONFIRMED.** No constant edited, no solver aim point moved, `YEAR_LEVEL_ANCHOR` untouched,
  `emergent_level_verdict` still six of seven outside their bands. §4's constraint 4, a seventh time.

### A verdict that turns on one survey year says so

The SVT segment's composed band rests on a single published tenure split (Ofgem CES 2018: 29% on SVT
3+ years, 23% under 3). Carrying one survey across nine years is a real weakness, so every forward
verdict is computed twice — at that mix and at the **mix-free envelope**, the value the segment could
take under any mix — and `verdict_is_mix_dependent` is derived per year from the two.
**2018's and 2019's overshoots are mix-dependent; 2017's and 2022's are not.** That was not the
answer the leg was written expecting, which is why the flag is computed rather than asserted.

### Controls

Eight legs in `tests/architecture/test_switching_rate_commons.py`, all eight mutation-proven on
disk: a dropped departure-band corner, the fixed-route term with its sign flipped, the negative
endpoint clipped to zero, the gap years scored instead of refused, φ acquiring a value, the check
importing the world's clipped constants (and the world importing the check), the mix-dependence flag
frozen, and the committed artefact drifting from the live record.

**One of them was measured to be an equivalence first and was repaired rather than recorded as one.**
The identity leg's first draft stayed green when a departure-band corner was dropped, because
`forward_composition` never reads the band's endpoints — it composes from the share and the segment
band and only compares against the record afterwards. Only the drift detector fired, and a drift
detector goes quiet the moment somebody regenerates the artefact. The leg now recomputes
`admissible_svt_churn` longhand as well, which is the half that does read both endpoints.

`admissible_svt_churn` is registered in `_NOT_A_LEVEL_READING` with its reason: it is a hazard
**within one segment**, and the published band's denominator is **all** GB domestic electricity
accounts. Holding it to that band would be dividing two numbers whose ratio is not a quantity, which
is the defect this whole control file exists over.

### Where this leaves the repair

**This finding stays BLOCKING.** The world's level is still clamped and still published, and rung 1
is unmoved. What changed is that the repair is no longer aimed at a constant at all:

> **The binding unestablished quantity is φ — the external share of active fixed-term renewals — and
> until it is sourced the published record cannot say whether `SVT_INERTIA_ANNUAL_RECENT = 0.20` is
> right, too low, or too high.**

What would close it: a domestic instrument separating *"switched supplier"* from *"switched tariff
with the same supplier"* on one base. Ofgem's Consumer Impacts of Market Conditions survey fields
both events and publishes them combined; the cross-tabulation is in the underlying data tables and
was not reachable this pass. **That is the next sourcing, and it is a narrower question than any
this finding has asked so far** — one cross-tabulation of one survey, against the household-level
dispersion §6 went looking for and the composition series §10 reconciled.

And the second thing owed, which is not a sourcing job: **§9's and §10's readings must be re-run
jointly, not separately.** Result 2 above is only visible when the hazard and the share move
together, and each of those readings holds the other's subject fixed by construction.

**The first leg of that is landed here rather than left as a note.**
`tools/fit_year_level_anchor --svt-shortfall` now prints the admissible interval beside its own
`required_hazard`, per year, with 2017 marked *REFUSES the required hazard* and 2020/2021 marked
refused for want of a published share. That pairing exists because a reader who sees *"the record
needs 0.334"* and nothing else will read it as a repair to apply — which is what §9 invited, and
what result 2 says is wrong. It is also the wiring that keeps this module out of the no-caller
class: the orphan ratchet refused the first landing of this work, and the honest answer to that
refusal was to make the reading reachable from something that runs, not to declare it dormant and
freeze it beside `svt_generated_share_check`.

— Delivery seat, 2026-09-04.

## 12. §11's refusal was the mixed pair, not the record — and the repair is unmoved — 2026-09-04

§11 closed owing two things. One is a sourcing job (φ). The other was not, and it is done here:

> *"**§9's and §10's readings must be re-run jointly, not separately.** Result 2 above is only
> visible when the hazard and the share move together, and each of those readings holds the other's
> subject fixed by construction."*

**§11 took that step with a mixed pair, and its result 2 is refuted by the consistent one.**
`tools.published_route_split.where_the_worlds_joint_point_falls`, committed in
`docs/reports/published_route_split.json` beside the section it corrects. Pre-registration:
`SEAT_PREREGISTRATION_WHETHER_THE_RECORD_STILL_REFUSES_THE_PAIR_WHEN_THE_PAIR_IS_PRICED_JOINTLY_2026-09-04.md`,
filed before the module existed. All six graded below.

### What was wrong with §11's step

`where_the_worlds_point_falls` computes `phi_admitting_required` by feeding §9's `required_hazard`
— solved holding the world's **own, lower** SVT share fixed, and therefore sized to close the entire
gap on the SVT route alone — into a composition evaluated at the **published** share. That is not
"both repairs land". It is one repair sized to do all the work, applied on top of another repair
that has already done part of it. It double-counts, and the double-count is the whole of result 2.

The self-consistent quantity was already published by §10 and nobody had multiplied it out:
`H_joint = world_hazard × hazard_multiple_still_required_at_band_low`, where the multiple already
has the renewal route moved to the complement of the published share. `H_joint` is then judged
against an admissible interval and a φ **pinned to that same share** — not swept over the published
pair, which is the same mixture one level down.

### The result: the record refuses the joint pair in no year

All-domestic basis, published share at its high endpoint, `renewal_rescaled`:

| year | §9's required | `H_joint` | admissible at that share | in? | φ (joint) | φ (mixed, §11) |
|---|---|---|---|---|---|---|
| 2017 | 0.2841 | **0.1999** | 0.0122 – 0.2200 | ✓ | 0.061–0.100 | **−0.360 – −0.270** |
| 2018 | 0.2793 | 0.2793 | 0.0853 – 0.3416 | ✓ | 0.217–0.251 | 0.217–0.251 |
| 2019 | 0.3340 | 0.3263 | 0.1058 – 0.3638 | ✓ | 0.110–0.151 | 0.079–0.153 |
| 2023 | 0.0842 | 0.0876 | 0.0600 – 0.1389 | ✓ | 0.290–1.318 | 0.309–1.405 |
| 2024 | 0.1692 | 0.1361 | 0.0884 – 0.1872 | ✓ | 0.163–0.898 | −0.418–0.367 |

*2020 and 2021 stay REFUSED for want of a published share, unchanged and still not interpolated.
The denominator is 5 of 7 and is reported as 5.*

`years_the_record_refuses_the_joint_pair` is **empty on both bases, at both share endpoints, under
both accountings** — 40 corners, no refusal. **§11's 2017 REFUSED mark is withdrawn.** Jointly,
2017 needs `H_svt` of 0.193–0.221 against an admissible ceiling of 0.220–0.237, at φ of 0.061–0.134.

### And composition does not rescue the hazard, which is the result that matters

The flip is real and it changes nothing about where the repair is aimed. Against the published
`SVT_INERTIA_ANNUAL_RECENT = 0.20`, all-domestic:

| year | §9's required ÷ 0.20 | `H_joint` ÷ 0.20 |
|---|---|---|
| 2017 | 1.42 | **1.00** |
| 2018 | 1.40 | 1.40 |
| 2019 | 1.67 | **1.63** |
| 2023 | 0.42 | 0.44 |
| 2024 | 0.85 | 0.68 |

**§9's headline stands almost exactly.** Its 1.67× at 2019 becomes 1.63×; 2018 does not move at all,
because there the published share equals this world's to three decimals. Only 2017 moves materially.
The repair stays where §9 and §11 left it: the hazard per SVT-account-year, and whether 0.20 —
drift off the SVT *product* — is the right published quantity for a band made of external changes of
*supplier*.

### The direction is not forced, and I filed a prediction saying it was

`H_joint` is **higher** than §9's required hazard at 2018 and 2019 on the as-published basis and at
2023 on both — up to 1.118×. Two causes, and neither was in the hand argument that produced P1:

1. **The published share is not always above the world's.** §10 established that on the as-published
   basis this world reads *above* the record at 2018 and 2019, and I carried the all-domestic sign
   into a prediction that spanned both bases.
2. **The renewal route is not always small against the band.** Moving account-days onto SVT takes
   them off fixed, so the renewal route shrinks — and where it is a large share of a small band
   (2023: 2.82pp of an 8.9pp band low) that costs the SVT route more than the larger share gains it.

**And the falsification criterion I filed was itself wrong.** P1 said *"if it comes out FALSE the
implementation is wrong, and that is worth knowing before the interesting predictions are read."* It
came out false and the implementation is right. A prediction that pre-commits "false ⇒ my code is
broken" is a trap when the "forced" claim rests on an assumption the filer did not notice making —
it would have sent the next hour after a bug that does not exist. Recorded here rather than quietly
dropped, because it is a better lesson than the prediction was.

### The basis choice now has a price, and §10 left it open

On the all-domestic basis the joint requirement **falls** in 4 of 5 years; on the as-published basis
it **rises** in 3 of 5. That is entirely §10's prepayment restoration, which §10 deliberately left
unsettled because this world models no prepayment meter and its book is neither published
population. It was an open note there. It is a priced decision here, and it is the first place the
choice changes a number anyone would act on.

### One φ for every year: EMPTY — and it was empty before the repair, so it says nothing about it

Derived after the numbers were seen and labelled so in the artefact. φ is one behavioural quantity
per year describing one market, so the per-year intervals having an empty intersection is a
statement about the world. Taken as the union over both share endpoints, all-domestic,
`renewal_rescaled`:

> 2017 [0.061, 0.100] · 2019 [0.110, 0.151] · 2024 [0.163, 0.898] · 2018 [0.217, 0.251] · 2023 [0.290, 1.318]

2017, 2019 and 2018 are **pairwise disjoint** — three consecutive years each requiring a different
φ, and not in date order. **No single φ reconciles the jointly-repaired world with the record.**

**And that is not evidence about the repair**, which is why the artefact carries the same reading at
the world's *current* hazard: 2017 [0.395, 0.437], 2019 [0.628, 0.672], 2018 [0.574, 0.608] —
**also empty, also disjoint, and already true before any of this**. The joint repair moves the
required φ down by roughly 0.3–0.5 and leaves the year-to-year spread where it was. So the honest
statement is a fidelity one and not a verdict on the repair: *this world's SVT route cannot be
reconciled with the published route split by any constant φ at any hazard level, before or after.*

That does not contradict §8's finding that the SVT route's relative slope is +0.99. §8 measured the
world's SVT departures against the record's **total** departures; this measures an implied φ, which
also carries the published **share** series' year-to-year movement. A mismatch here can live in the
share series as easily as in the hazard, and 2020 and 2021 are missing from that series entirely.
**Which of the two moves is the next question**, and it is narrower than the one §11 handed on.

### The pre-registration, graded, all six

- **P1 — REFUTED**, and it was filed as "arithmetically forced". See above; the error and the bad
  falsification criterion are both recorded rather than the prediction being retired.
- **P2 — CONFIRMED.** 2017 flips on both bases, at both share endpoints, under both accountings, and
  is the only flip. Predicted the as-published `H_joint` would land in 0.21–0.24 and stay inside
  [−0.014, 0.237] narrowly: it is **0.2140**, inside by 0.023.
- **P3 — CONFIRMED.** φ ≥ 0 in every comparable year on both bases at all 40 corners; the record
  refuses the pair nowhere. Predicted 2017's φ in [0.00, 0.15]: it is 0.061–0.134 across every
  corner.
- **P4 — SPLIT, and the split is the prepayment basis.** Predicted the joint requirement would sit
  inside or below the published 0.15–0.20 in at least 3 of 5. **CONFIRMED on all-domestic** (2017
  0.1999 inside, 2023 and 2024 below — exactly 3). **REFUTED on as-published** (2 of 5). I filed the
  converse explicitly and it is the half that holds: *"if `H_joint` is still above 0.20 in most
  years, composition is a second-order correction and §9's headline stands."* It is, and it does.
- **P5 — REFUTED in 2 of 5, and its second half CONFIRMED.** Predicted `renewal_held` would move
  `H_joint` by under 0.01 everywhere: it does at 2017 (0.007), 2018 (0.000) and 2019 (0.001), and
  does not at 2023 (0.020) and 2024 (0.017) — the two years with the smallest bands. It flips **no**
  verdict anywhere, which was the point: the result cannot be picked by choosing an accounting.
- **P6 — CONFIRMED.** 2020 and 2021 stay refused, the denominator stays 5 of 7, and
  `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` is still `None`.

### Two defects caught in this reading's own machinery

**φ was taken off the unrounded hazard while the rounded one was published**, so the artefact did not
reproduce from its own printed inputs — a reader recomputing φ from the published `H_joint` got a
different number in the last place. Caught by the control, which recomputes longhand from the
artefact rather than by calling the module's own helper; fixed by rounding before φ is taken, not
after.

**The first draft of the one-φ control could not fail.** Both intersections are empty, so replacing
`is_non_empty` with a constant `False` reproduced the artefact exactly and the leg stayed green. That
is an equivalence, and it was repaired rather than recorded as one: the rule is now the module-level
pure function `intersect_spans`, and the control exercises both branches on spans it constructs, so
the True branch is reachable whatever the world says this week.

### Controls

Seven legs in `tests/architecture/test_switching_rate_commons.py`, all seven mutation-proven on disk
across ten mutations: `at_share` accepted and ignored; the joint hazard judged over both share
endpoints (the mixed pair one level down); the basis crossed between requirement and interval; every
admitted year credited as a flip; a φ above 1 reported as a refusal, and φ clipped into [0, 1]; the
joint hazard replaced by §9's column; the unrepaired-world companion dropped; the intersection
written down; its verdict frozen; and an empty intersection clipped instead of crossed. The drift
detector over the committed artefact gains the joint section, because a published section outside
its key list has no drift detector at all.

**Nothing here picks a number.** No constant edited, no solver aim point moved, `YEAR_LEVEL_ANCHOR`
untouched, `emergent_level_verdict` still six of seven outside their bands. §4's constraint 4, an
eighth time.

**This finding stays BLOCKING.** The world's level is still clamped and still published. What
changed: §11's result 2 is withdrawn, the record admits the joint pair everywhere, composition is
confirmed second-order, and the binding unestablished quantity is still φ — now with the added
constraint that no constant φ can reconcile this world's SVT route with the record in every year,
which was already true before any repair was attempted and which nothing has yet attributed.

— Delivery seat, 2026-09-04.

## 13. "Empty" was not a verdict, because nobody named the tenure mix — and the share series is not what moves — 2026-09-04

§12 closed owing two things. One is the φ sourcing, still owed and untouched here. The other was
its handover question, and it came with a premise nothing had checked:

> *"A mismatch here can live in the share series as easily as in the hazard … **Which of the two
> moves is the next question**."*
> *"φ is one behavioural quantity per year describing one market, so the per-year intervals having
> an empty intersection is a **statement about the world**."*

**Both are answered here from three published series with no world in them at all.**
`tools.published_route_split.whether_a_constant_phi_survives_the_record_alone` and
`…how_much_of_the_records_move_the_share_series_can_carry`, committed in
`docs/reports/published_route_split.json`. Pre-registration:
`SEAT_PREREGISTRATION_WHETHER_A_CONSTANT_PHI_SURVIVES_THE_PUBLISHED_RECORD_WITH_NO_WORLD_IN_IT_2026-09-04.md`,
filed before the module existed. All six graded below.

### The premise is refuted, and the reason is a flag §11 built two sections earlier

Ask §12's intersection of the record on its own — `H_svt` free per year inside a **published**
segment band, φ constant — and the answer depends entirely on which band, which is the distinction
§11 invented `verdict_is_mix_dependent` for and which §12's one-φ reading never applied to itself.

| `H_svt` free inside | as_published | all_domestic |
|---|---|---|
| `tenure_composed` 0.0942–0.1442 | **REFUSES** — refused by 2017/2018 and 2017/2019 alone | **REFUSES** — same two pairs |
| `mix_free_envelope` 0.0500–0.2000 | **ADMITS** φ ∈ **[0.612, 0.770]** | **ADMITS** φ ∈ **[0.618, 0.850]** |

*Seven scored years, 2022 excluded by name (below). 2020 and 2021 stay refused for want of a
published share and are still not interpolated.*

**So an empty φ intersection is not distinctive to this world** — the record's own best segment
estimate produces one too — **and it is not forced either.** Widen `H_svt` to what the segment could
take under any tenure mix and the record admits a constant φ over every scored year but the crisis.
`verdict_is_mix_dependent` is **True** for the fitted set and for the headline set, and False only
where 2022 refuses on both bands.

**The whole refusal rests on one survey year.** `tenure_composed` weights the two published churn
rows by Ofgem CES 2018's single tenure split (29% on SVT 3+ years, 23% under 3), carried across nine
years. §11 already called that "a real weakness" and computed the mix-free companion for its own
forward verdict. §12 then shipped a verdict with no mix companion at all. That is not a new class of
defect in this repository — it is the VAT shape one degree weaker again: a control built, sitting in
the same module, not applied to the next reading that needed it.

### And a constant PAIR is refused outright, by a third of φ's range

The tightest form of the question needs no segment band, so it cannot inherit the tenure survey's
weakness: is there **one** `H_svt` and **one** φ, both constant, that the record admits in all five
fitted years? Sweeping `H_svt` across [0, 0.40] at a step of 0.0001 — 4,001 points:

| basis | H values admitting a common φ | widest slack | at |
|---|---|---|---|
| as_published | **0 of 4,001** | −0.3093 | H = 0.0685 |
| all_domestic | **0 of 4,001** | −0.3374 | H = 0.0542 |

The margin is published and not just the verdict, because a bare `False` cannot be told apart from a
sweep that never ran. At −0.31 the record is refusing constancy in both parameters by a third of
φ's whole range — not by a rounding.

### 2022 is excluded by name, and its own numbers are published beside the exclusion

Its φ interval at the tenure-composed band is **[−2.880, −0.463]**: entirely negative on both bases,
which is the record refusing the whole published segment band there, extending §11's result 3 from
`SVT_INERTIA_ANNUAL_RECENT = 0.20` to the band's low end as well. At the mix-free envelope it is
**[−4.314, +0.043]** — not a refusal but a near-zero ceiling on the external share, which is what a
market with no fixed-term offers on sale actually looks like. Excluding it is a judgement and it
gets the discipline a judgement gets here: named in `STRUCTURAL_BREAK_YEARS` with its reason, its
own span published in `per_year`, and a control requiring the exclusion to change some verdict —
because a register nobody's answer turns on is one that will rot.

### Which of the two moves: the share series cannot carry the record's steps

Hold **both** behavioural parameters at any constants and the composed rate moves by exactly
`dV = (s₂ − s₁)·(H_svt − 0.35φ)`. That bounds what the published share series can supply on its own.
All-domestic, tenure-composed:

| step | record moved | share series can reach | |
|---|---|---|---|
| 2016→2017 | −4.10 to −3.00 pp | −1.74 to +3.08 pp | **cannot** |
| 2017→2018 | +5.50 to +6.50 pp | −0.74 to +1.30 pp | **cannot** |
| 2018→2019 | +0.70 to +1.80 pp | −0.25 to **+0.44** pp | **cannot** |
| 2022→2023 | +4.60 to +9.60 pp | −2.56 to +2.56 pp | **cannot** |
| 2023→2024 | 0.00 to +7.20 pp | −1.54 to +2.56 pp | *no move required* |
| 2024→2025 | −1.80 to +5.40 pp | −3.17 to +5.63 pp | *no move required* |
| 2019→2022 | −18.40 to −16.40 pp | −8.48 to +4.78 pp | *spans the 2020–21 gap* |

**0 of 4 judged pairs on three of the four band/basis grids, and 1 of 4 on the fourth** (mix-free ×
as-published, 2016→2017 only). At 2018→2019 — the step §12's disjoint φ intervals turn on — the
share series reaches at most **0.44pp of a step the record puts at 0.70–1.80pp**. **The movement is
behavioural. It is not composition.**

**A pass branch that could not fail, caught on this reading's own first run.** Two pairs came out
`share_can_carry = True`, and in both the record's move interval *contains zero* — the published
bands are wide enough that no move is required, so anything carries it including nothing. Counting
those as evidence would have been a control keyed to an answer true by construction. They are
flagged `record_requires_a_move: false`, excluded from the denominator, and the denominator is
reported as what it is. `test_a_pair_the_record_requires_no_move_from_is_not_counted_as_carried`
holds it, and requires such a pair to exist so the exclusion is exercised.

### An interval for φ falls out of this, and it is NOT going into the constant

`[0.618, 0.850]` (all-domestic) is the first published-evidence-derived interval for φ in this tree.
It is **conditional on φ being constant across 2016–2025 excluding 2022** — an assumption the record
does not supply and this reading does not adopt. `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` is still `None`
and `test_the_external_share_of_active_renewals_stays_a_declared_gap` still keeps it there.

Worth reading beside §12 rather than instead of it: that interval sits **entirely above** §12's
per-year joint φ intervals for 2017 [0.061, 0.100], 2018 [0.217, 0.251] and 2019 [0.110, 0.151], and
inside 2023's and 2024's. The cause is mechanical and not a second finding — the mix-free envelope
admits `H_svt` down to 0.05, and a lower SVT hazard needs a higher external renewal share to reach
the same band. It is the same trade the identity has made throughout.

### The pre-registration, graded, all six

- **P1 — CONFIRMED, and one pair short.** The tenure-composed band refuses a constant φ over the
  fitted years on both bases. Predicted **{2017, 2018}** as a minimal refusing pair: it is one, on
  both bases. **{2017, 2019} is also one and I did not predict it.** The other half holds: no
  minimal refusing pair in the fitted set involves 2022, 2023 or 2024.
- **P2 — CONFIRMED, and unusually precisely.** Predicted the mix-free envelope would rescue
  2017/2018, come out non-empty on `all_domestic`, land inside φ ∈ [0.55, 0.90], and be bound by
  2019's low end and 2017's high end. It is **[0.6178, 0.8503]**, and those two years are exactly
  the binding constraints. Predicted `as_published` would also admit, at a **lower** interval,
  because its shares are smaller: **[0.6122, 0.7700]**, lower at both ends.
- **P3 — SPLIT, and the refuted half is the better result.** Predicted 2022's φ interval would come
  out entirely negative "on both bands". **CONFIRMED at `tenure_composed`** on both bases.
  **REFUTED at `mix_free_envelope`**, where it is [−4.314, **+0.043**] — not a refusal but a ceiling
  of a 4.3% external share. That is a more useful sentence than the one I predicted: the record does
  not say the crisis year is impossible, it says almost nobody left a fixed deal for another
  supplier's, which is what the crisis was.
- **P4 — CONFIRMED on the claim, REFUTED on the years, SPLIT on the arithmetic.** The share series
  fails to carry the record's move in 4 of 4 judged pairs on three grids and 3 of 4 on the fourth —
  the majority claim, and stronger than predicted. **The named years are refuted:** I predicted the
  crisis-crossing pairs (2019→2022, 2022→2023) would be the ones it *can* carry, and both are
  `cannot` on every grid; the two that "carry" are 2023→2024 and 2024→2025 and they carry only
  because the record requires no move at all. My reasoning was that a big move in both series would
  let one explain the other, and it ignored that the share series' *reachable* interval scales with
  `|Δs|` while the record's band width does not. On the numbers: predicted the share series' maximum
  2018→2019 contribution at under 70% of the record's minimum move and under 30% of its maximum.
  **CONFIRMED on all-domestic** (62.1% and 24.2%). **REFUTED on as-published** (73.1% and 28.4%) —
  the first half misses by 3.1pp, and I filed one number across two bases §10 had already shown
  differ.
- **P5 — CONFIRMED.** φ is still `None`; the interval is published with its assumption named beside
  it. One deviation recorded rather than glossed: I said the field would be called
  `conditional_interval` under an `assumption` key and it is `the_assumption_that_is_not_the_records`
  beside the intersections themselves. The commitment was the refusal and the naming, and both hold.
- **P6 — CONFIRMED.** No constant edited, no solver aim point moved, `YEAR_LEVEL_ANCHOR` untouched,
  `emergent_level_verdict` still six of seven outside their bands. The committed artefact's diff is
  **insertions only** — every world-derived section in it is byte-identical, which is what a reading
  with no world in it should do. §4's constraint 4, a ninth time.

### Controls

Seven legs in `tests/architecture/test_switching_rate_commons.py`, all mutation-proven on disk under
`python3 -B` across eight mutations: the φ span's band endpoints swapped (a silent always-empty that
reads as a finding), an intersection written down instead of derived, the structural break excluded
without being named, the mix-dependence flag frozen, the constant-pair slack blanked, its grid
collapsed to 40 points (which would turn a real admitting interval into a REFUSED — the flattering
direction), the carrying denominator taken over every pair, and the sign flipped in
`(H_svt − 0.35φ)`. Both branches of the constant-φ verdict are live in the same run — the
tenure-composed band refuses and the mix-free envelope admits — so a frozen `is_non_empty` of either
polarity breaks the leg, which is what §12's own first draft could not manage. The drift detector
gains both sections.

### Where this leaves the repair

**This finding stays BLOCKING.** The world's level is still clamped and still published, and rung 1
is unmoved. What changed:

> **§12's `one_phi_for_every_year` emptiness is withdrawn as evidence about this world.** It is a
> reading whose verdict turns on a tenure mix nobody named, and at the mix-free envelope the record
> admits a constant φ. The share series is measured out as the thing that moves. **The binding
> unestablished quantity is still φ, and the binding weak INPUT is now the single Ofgem CES 2018
> tenure split**, which is carried across nine years and is what separates a record that refuses
> constancy from one that admits it.

Two things owed, and they are narrower than anything this finding has asked before. First, still,
the φ cross-tabulation from Ofgem's Consumer Impacts of Market Conditions survey — one
cross-tabulation of one survey, unchanged from §11. Second, and new: **a second tenure split for the
SVT segment in any year other than 2018.** One more observation of that one quantity decides whether
the record refuses a constant φ or admits 0.62–0.85 of one, and it is the highest-leverage sourcing
question this chain has produced.

— Delivery seat, 2026-09-04.

---

## 14. The second tenure observation was already in the tree, and it refutes §13's dichotomy — 2026-09-04

§13 closed by naming its own binding weak input and asking for exactly one thing:

> *"**a second tenure split for the SVT segment in any year other than 2018.** One more observation
> of that one quantity decides whether the record refuses a constant φ or admits 0.62–0.85 of one,
> and it is the highest-leverage sourcing question this chain has produced."*

**It was in this tree when §13 asked for it, cited, dated and load-bearing since 2026-07-22.**
`docs/market_research/ASSUMPTIONS.md` L176 carries Ofgem's Retail Market Indicators October-2025
default-tariff stock split — the R13 ruling on the engagement mix turns on it — and
`continuous_behavioural_engagement_w2_14.md` §1a cross-validates the same figure against CMA
Appendix 9.1. Nothing pointed either of them at the segment band. That is §10's shape for the
**fourth** time in this one chain, and the structural fix is the one `published_tariff_mix` applied
to the share series: one home. `SVT_TENURE_OBSERVATIONS` in `tools/published_route_split.py` is now
that home, and it is a register of observations with their instruments rather than a pair of
percentages. Reading:
`whether_the_constant_phi_verdict_turns_on_one_survey_year`, committed in
`docs/reports/published_route_split.json`. Pre-registration:
`SEAT_PREREGISTRATION_WHETHER_THE_CONSTANT_PHI_REFUSAL_SURVIVES_A_SECOND_TENURE_OBSERVATION_2026-09-04.md`,
filed before the register existed. All eight graded below.

### The two observations disagree by 19 points, and they are not a trend

| | instrument | population | within-SVT long-stayer | composed band |
|---|---|---|---|---|
| Ofgem CES **2018** | consumer survey, self-report | GB domestic, PPM included | 29/(29+23) = **0.5577** | [0.0942, 0.1442] |
| Ofgem RMI **Oct-2025** | supplier-returned stock | GB domestic electricity, **non-PPM** | 20.3/(20.3+34.6) = **0.3698** | [0.1130, 0.1630] |

One is a survey and one is administrative stock; one includes prepayment and one does not. **Two
points on two instruments over two populations are not a series**, so the reading interpolates
nothing and extrapolates nothing — it takes the **hull**, [0.0942, 0.1630], which is every mix
between the two and needs neither assumption. The 2025 row's exclusion is carried as a **direction
and never a factor**: `published_tariff_mix` already establishes that prepayment is ~15% of domestic
accounts and >90% of it sits on a default tariff, so restoring it can only move that share **up,
toward 2018's**. 0.3698 is a lower bound, which is the direction that makes the hull an upper bound
on the disagreement.

### The headline: the record refuses at every mix anything has observed

| band | implies a segment | as_published | all_domestic |
|---|---|---|---|
| `tenure_composed` (2018) | 0.558 long-stayer | REFUSES | REFUSES |
| `tenure_composed_2025` | 0.370 long-stayer | **REFUSES** | **REFUSES** |
| `observed_mix_hull` | 0.558 → 0.370 | **REFUSES** | **REFUSES** |
| `mix_free_envelope` | **1.000 → 0.000** | ADMITS φ ∈ [0.612, 0.770] | ADMITS φ ∈ [0.618, 0.850] |

*Fitted years and the headline set (2022 excluded by name) agree; every scored year refuses at all
four bands because 2022 does.*

`refuses_at_every_observed_mix` is **True** on both bases, and
`admits_only_outside_every_observed_mix` is **True** with it. **§13's dichotomy has no slot for
that result.** The record does not refuse *or* admit 0.62–0.85 of a constant φ — it refuses at
every mix any instrument has seen, and admits only in the gap between the observed hull and the
mix-free envelope.

**And that gap now has a name, which is the part worth keeping.** Inverting the composition at each
band's endpoints says what segment each one describes: the mix-free envelope's low end is a segment
that is **entirely long-stayer** and its high end one with **no long-stayers at all**. Anything
observed sits between 0.370 and 0.558. So §13's `[0.618, 0.850]` is not an interval the record
allows for φ — it is an interval the record allows *if* the SVT segment's tenure composition is
something no instrument supports, and it is **weaker evidence after this reading than before it**.
`EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` is still `None` and has one more reason to be.

### Three results nobody predicted, one of them a new refusal

**The 2025 mix makes 2023 refuse against the pre-crisis years.** New minimal refusing pairs appear
that the 2018 mix does not produce: **2019/2023** on both bases and **2018/2023** on `all_domestic`.
The higher band pushes the post-crisis years' φ intervals down far enough to separate them from
2018's and 2019's, which the 2018 mix does not. The refusal is not merely preserved by the second
observation — it is broader under it.

**At the hull the binding pair is 2017/2019, not 2017/2018.** The pre-registration hand-derived the
2017/2018 crossing at −0.057 and got it exactly; the *set* crossing is **−0.128** (`all_domestic`)
and −0.134 (`as_published`), carried by 2017/2019. Widening the band from 0.0500 to 0.0688 narrows
the 2017/2018 gap and leaves 2017/2019 wide.

**The share series reaches LESS at the 2025 mix, not more, and the reason refutes P5's arithmetic
rather than its claim.** `dV = (s₂ − s₁)·(H_svt − 0.35φ)`; for a pair where the default share
*falls*, `Δs` is negative and the reachable maximum is `|Δs|·(0.35 − H_lo)` — it is set by the
band's **LOW** end, not by its width. So 2018→2019's maximum reach is **0.435pp at both the 2018 mix
and the hull** (identical, because they share a low end) and **0.403pp at the 2025 mix**, against a
record step of 0.70–1.80pp. Raising the hazard band lowers what composition can supply.

### The pre-registration, graded, all eight

- **P1 — CONFIRMED on the claim and on the pair; one arithmetic slip, and the set crossing was not
  predicted.** The 2025 mix REFUSES on both bases. Hand-derived 2017's high end at 0.5389 against
  an actual **0.5350** — a calculator slip of 0.004 in my own working, not in the module — and
  2018's low end at **0.6862**, exact. The 2017/2018 crossing goes −0.1330 → **−0.1512** (predicted
  −0.147, off by the same slip). I predicted a *pair* crossing and quoted it as if it were the set's:
  the fitted-set crossing is **−0.222**, carried by 2017/2019, and I did not predict it. The OPEN
  half — *"whether any new pair joins them"* — is answered **yes**, and that is the section's most
  substantive unpredicted result.
- **P2 — CONFIRMED, including the number, and the open half is answered against my expectation.**
  The hull REFUSES on both bases. Hand-derived 2017/2018 crossing −0.057; actual **−0.0572**. The
  binding pair is **2017/2019**, which I explicitly flagged as uncomputed.
- **P3 — CONFIRMED exactly.** `mix_free_envelope` is unchanged: [0.6122, 0.7700] `as_published`,
  [0.6178, 0.8503] `all_domestic`. Held by a control that mutates the register and requires it not
  to move, so this is a property and not an observation.
- **P4 — CONFIRMED exactly.** The constant-pair sweep is unmoved: 0 of 4,001 on both bases, widest
  slack −0.3093 at H = 0.0685 and −0.3374 at H = 0.0542.
- **P5 — CONFIRMED on the claim, REFUTED on the arithmetic, and the refutation is the useful half.**
  0 of 4 judged pairs carried at `tenure_composed_2025` and at `observed_mix_hull`, on both bases.
  I predicted 2018→2019's reach at the hull would land in **0.55–0.70pp** on the reasoning that the
  reach scales with the band's width. It is **0.435pp** — identical to the 2018 mix's. My reasoning
  was wrong about which endpoint binds, as set out above. The two `record_requires_a_move: false`
  pairs are still flagged and still excluded at both new bands.
- **P6 — CONFIRMED, including the mechanism.** 2022's φ high end at the hull is exactly −0.46264,
  the same figure as at the 2018 mix because the two bands share a low end, and at the 2025 mix it
  falls to −0.6774. Entirely negative at both.
- **P7 — CONFIRMED.** §13's sentence is refuted as posed: the second observation decides neither
  branch of the dichotomy it offered.
- **P8 — CONFIRMED on the property, and its stated FORM was wrong.** No existing value in
  `published_route_split.json` changed, no key was removed, and the only additions are the four
  named new ones — verified by a structural walk over the parsed JSON. But I predicted the artefact's
  **diff** would be *"insertions only"* and it is not: 375 lines read as removals, because two dicts
  gained trailing commas and because git realigns repeated JSON blocks. **A line diff was the wrong
  instrument for the claim** and I filed it as the evidence. The claim was about values; the check
  has to be over values. `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` is `None`, `YEAR_LEVEL_ANCHOR` is
  untouched, no solver aim point moved, and `emergent_level_verdict` is still six of seven outside
  their bands. §4's constraint 4, a tenth time.

### Two defects this reading's own machinery caught, both in the first draft

**A register keyed by tuple position.** `svt_segment_churn_band` read
`SVT_TENURE_OBSERVATIONS[1]` — a register that cannot lose a row or gain one in the middle. It was
found by the isolation control handing the module a one-row register, which raised `IndexError`
rather than reporting anything. The bands are now keyed by the observation's **year**, and the hull
always includes the historical observation so an emptied register produces a reading rather than a
crash.

**A control whose docstring claimed a mutation it did not catch.** The composition leg said in terms
that it caught the units error — reading `29%` where the within-segment ratio `0.5577` belongs — and
it did not: `long_stayer_pct / 100` survived every assertion, because 0.29 is as valid a share as
0.5577 and composes to a band still between the two published rows. That is this file's own
recurring shape and it was caught by running the mutation rather than by re-reading the docstring.
The property that separates them needs no reference to today's numbers: **both published rows are
fractions of the whole account base and the SVT segment is a strict subset, so the within-segment
share must be strictly larger than the raw percentage read as a fraction.** A second survivor —
dropping the per-observation bands, leaving only the hull — was also a missing test, not an
equivalence: a hull refusing says nothing about its interior, so §14's claim that the record refuses
at *each* observed mix needed each mix scored on its own.

### Controls

Five legs in `tests/architecture/test_switching_rate_commons.py`, all mutation-proven on disk under
`python3 -B` across twelve mutations: the register collapsed to one observation, a population
blanked, the exclusion direction blanked, the within-segment ratio replaced by the raw percentage,
the two published churn rows swapped in `compose_at_mix`, the observed hull replaced by the mix-free
envelope, `refuses_at_every_observed_mix` frozen True, `the_verdict_is_the_same_at_every_observed_mix`
frozen True, `mix_free_envelope` admitted into the observed-mix band list, the endpoint inversion
replaced by the endpoint itself, the per-observation bands dropped from the verdict, and the
historical observation duplicated into the register.

**The reachability leg injects its missing branch rather than asserting a derivation.** All three
§14 flags are constant across today's data — the record refuses at every observed mix on both bases
and in every year set — so a leg that recomputed them from the same dict would be testing `all()`
and one that merely read them would pass against a written-down `True`. So the branch is
manufactured: two observations are injected at an all-long-stayer and an all-recent segment, which
are the only mixes whose hull reaches the mix-free envelope. The hull then ADMITS while both real
observations still refuse, and all three flags must flip. No published number is touched — only the
register. The exclusion-direction leg carries its own correction beside it: its first draft banned
every digit and fired on the citation *"2018"*, which would have pushed the provenance out of the
field to keep a control green; it now forbids a magnitude and permits a year.

### Where this leaves the repair

**This finding stays BLOCKING.** The world's level is still clamped and still published, and rung 1
is unmoved. What changed:

> **§13's binding weak input is discharged, and the admission it protected is relocated rather than
> confirmed.** The tenure split is no longer one survey year carried across nine: there are two
> observations on two instruments, they disagree by 19 points of within-segment share, and the
> record refuses a constant φ at both of them and at every mix between them. The `[0.618, 0.850]`
> interval survives only at a segment composition that is entirely long-stayer at one end and has no
> long-stayers at the other, and **nothing has observed either.** The binding unestablished quantity
> is φ, alone, with no weak input standing behind it.

One thing owed, and it is now the only one: **the φ cross-tabulation from Ofgem's Consumer Impacts
of Market Conditions survey** — one cross-tabulation of one survey, separating "switched supplier"
from "switched tariff with the same supplier" on one base. Unchanged since §11, and it is no longer
competing with a sourcing question about tenure. Before sourcing it externally, **look in this tree
first**: that instruction has now been right four times in this chain, and the fourth time it was
right about a figure a director ruling had already turned on.

— Delivery seat, 2026-09-04.

---

## 15. The φ instrument exists, it does not close φ, and what it does close is a route the world has no mechanism for — 2026-09-04

§14 closed owing exactly one thing:

> *"the φ cross-tabulation from Ofgem's Consumer Impacts of Market Conditions survey — one
> cross-tabulation of one survey, separating 'switched supplier' from 'switched tariff with the same
> supplier' on one base. Unchanged since §11 … Before sourcing it externally, **look in this tree
> first**."*

**The tree was searched first and was dry, and that was written down before the fetch.** The one
result worth carrying from the in-tree pass: `simulation/renewals.py` and `renewal_engagement.py`
have **no internal-switch concept at all** — no `same_supplier`, no retention move, no re-contract —
so there was no in-tree value that could have been mistaken for φ. Then the external pass ran, and
**the instrument exists.** Source and provenance:
`docs/market_research/gb_domestic_switcher_split_cim_2022_2025.md`. Register:
`SWITCHER_SPLIT_OBSERVATIONS` in `tools/published_route_split.py`. Reading:
`whether_the_survey_split_identifies_phi`, committed in `docs/reports/published_route_split.json`.
Pre-registration:
`SEAT_PREREGISTRATION_WHETHER_A_PUBLISHED_SWITCHER_SPLIT_CAN_CLOSE_PHI_AT_ALL_2026-09-04.md`,
filed before any source was fetched. All seven graded below.

### The instrument, and where the four previous sections were looking

Ofgem CIM **question C4** — *"Which, if any, of these have you or your household done in the past 6
months?"*, base all respondents — carries *"switched to a new supplier"* and *"switched tariff with
the same supplier"* as **separate codes on one base**, as reported behaviour, across all six waves.

**§11's "not reachable this pass" and §7 of `gb_switching_rate_denominators.md`'s *"the domestic
instrument does not split it"* were both true of the question they were reading and false of the
instrument.** That file was reading CIM's *stated-reason* battery, whose base is switchers and whose
codes do not separate the two events. C4 is a different question in the same survey, and it does.
The correction belongs beside the claim: the split was three tabs away in a survey this repository
had already cited twice.

| wave | fieldwork | switched **supplier** | switched **tariff, same supplier** | net | φ_survey |
|---|---|---|---|---|---|
| W1 | March 2022 | 9.32% | 13.18% | 22.01% | 0.4237 |
| W2 | July 2022 | 8.30% | 12.48% | 20.77% | 0.3994 |
| W3 | Nov/Dec 2022 | 7.30% | 14.49% | 21.79% | 0.3351 |
| W4 | July 2023 | 4.60% | 11.04% | 15.64% | 0.2939 |
| W5 | January 2024 | 5.58% | 11.59% | 17.17% | 0.3251 |
| W6 | Jan/Feb 2025 | 5.29% | 17.02% | 22.31% | 0.2371 |

### It does not close φ, and the reason is an equation that arrives with its own unknown

The base is ALL HOUSEHOLDS, so both rows mix the two routes:

```
E  =  s·H_svt  +  (1−s)·0.35·φ          ← external. This IS the record's R.
I  =  s·J_svt  +  (1−s)·0.35·(1−φ)      ← internal. The survey's new row.
```

`J_svt`, the rate at which default/SVT households move onto a fix **with their existing supplier**,
is published nowhere. **One new equation, one new unknown.** `φ_survey` is a route *mixture* and is
not φ — and, contrary to what this pass predicted, it is not a bound on φ in either direction.
`EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` is still `None`, now for a reason that is measured rather than
asserted. `test_the_sourced_switcher_split_does_not_become_the_unestablished_constant` is the leg
that stops the arriving instrument becoming the arriving number, which was this section's live risk.

**The tariff-type banner is the obvious next reach and it does not work.** Table 109 gives φ_survey
of 0.221–0.398 among fixed-tariff respondents and 0.356–0.540 among variable-tariff ones. Tariff
type is recorded *after* the switch, so switching onto a fix puts a household in the fixed column
whichever route it came from. This is exactly the contamination
`household_switching_response_amplitude.md` §2.4 recorded for this survey family — *"so the next
session does not reach for the biggest number on the page"* — and the warning caught this session.
The figures are published so nobody re-fetches 26MB to learn they are unusable; they are not used.

### What it does close, needing only `J_svt ≥ 0`

Drop φ. The renewal route's internal output is `(1−s)·0.35·(1−φ)`, so its ceiling at any φ is
`(1−s)·0.35`. Taken at the **largest** published fixed share across every year each recall window
touches, against the survey's **un-annualised six-month** rate — both choices push against the
conclusion:

| wave | internal (6 mo.) | renewal-route ceiling (annual) | multiple |
|---|---|---|---|
| W1 | 13.18% | 7.00% | **1.88×** |
| W2 | 12.48% | 7.00% | **1.78×** |
| W3 | 14.49% | 7.00% | **2.07×** |
| W4 | 11.04% | 7.00% | **1.58×** |
| W5 | 11.59% | 7.00% | **1.66×** |
| W6 | 17.02% | 12.60% | **1.35×** |

**Six of six, over the ceiling, comparing six months against a year.**

> **Most GB domestic internal switching is default/SVT households taking a fix with their existing
> supplier. It cannot be fixed-term renewal — there are not enough fixed-term households in the
> record for it to be. And the world has no such move at all.**

### Why that is the useful result, and it runs against us

§9 closed on a question it could not settle: *"the hazard is drift off the SVT **product**, and the
band it is being asked to reproduce is external change of **supplier**. Those are not the same event,
and nobody has established the relation."* This is the published half of that relation.
`SVT_INERTIA_ANNUAL_RECENT = 0.20` is sourced as a product-drift rate; the external share of that
drift is below 1; so the external rate it implies is **below 0.20**, and §9's gap against the
record's required 0.334–0.342 is **wider** than the published 1.67×–1.71×, not narrower.

**No magnitude is quoted for the widening**, because `J_svt` is what would set it and `J_svt` is the
unknown this whole section is about. A direction with no magnitude is what the evidence supports.

### The pre-registration, graded, all seven

- **P1 — REFUTED.** I predicted the cross-tabulation would NOT be reachable from the published
  tables, at about 60/40. It is: question C4, six waves, one base, behavioural, in both the main
  report and the data tables. My reasoning generalised from CIM's *stated-reason* battery — the one
  question this repo had already read — to the whole instrument. **The graded prediction is the
  reason the search happened at all**, and it was wrong in the direction that costs nothing.
- **P2 — REFUTED, and not narrowly.** Predicted φ_survey ∈ [0.45, 0.70], point 0.58. Actual
  **0.237–0.424**: every wave below the interval's floor, and my point estimate is 1.4×–2.4× the
  observed values. I over-weighted the pre-2022 external-switching era that the waves do not cover.
- **P3 — CONFIRMED as stated, and its force is reduced by P6.** φ_survey is below 0.618 in 6 of 6
  waves, far below. But I framed this as the record's admissible interval being contradicted, and
  P6's confirmation means φ_survey is not the quantity that interval is about. **A confirmed
  prediction about the wrong quantity is not evidence, and it is graded that way here rather than
  banked.**
- **P4 — VOID, and deliberately not collected.** It predicted what the implied `H_svt` would be at
  φ_survey. Computing that would be substituting a route mixture into an identity that needs the
  renewal route alone — the exact misattribution `test_the_sourced_switcher_split_does_not_become_
  the_unestablished_constant` exists to refuse. A prediction whose antecedent the pass refutes
  cannot be collected either way, and it is recorded as uncollectable rather than quietly answered.
- **P5 — REFUTED, and the miss is in our favour.** I predicted every wave would be 2023 or later.
  W1–W3 are 2022. The useful half: waves DO fall inside fitted years 2023 and 2024, better coverage
  than predicted. The half that stands: **nothing covers 2016–2021**, the 2022 structural break sits
  between the instrument and the years that most need it, and no carry-back is adopted.
- **P6 — SPLIT: CONFIRMED on the claim, REFUTED on the reasoning, and the refuted half is the
  section.** The base is not φ's base and the split does not close the constant — as predicted, and
  it is the prediction I held most strongly. But I said φ_survey is an **UPPER bound** on renewal
  φ *"because the SVT route is overwhelmingly external — an SVT household has no fixed deal to
  internally renew onto."* **That sentence is wrong.** An SVT household taking a fix with its
  existing supplier is an internal move, and the ceiling table above shows it is the *dominant* form
  of internal switching in the record. The SVT route loads both rows, so φ_survey bounds nothing.
  Following that error to its end is what produced the `J_svt ≥ 0` ceiling, which is the only
  assumption-free result this pass has.
- **P7 — CONFIRMED.** No constant edited, no solver aim point moved, `YEAR_LEVEL_ANCHOR` untouched,
  `emergent_level_verdict` still six of seven outside their bands. §4's constraint 4, an eleventh
  time. Verified by a **structural walk over the parsed artefact**: exactly one top-level addition,
  zero removals, zero changed values — §14's P8 lesson applied rather than restated.

### Controls

Five legs in `tests/architecture/test_switching_rate_commons.py`, all mutation-proven on disk under
`python3 -B` across seven mutations: the ceiling taken at `min` over the recall window, the ceiling
taken at the fixed band's LOW end (both shrink the ceiling and flatter the verdict), the unjudgeable
branch collapsed to `False`, the unjudgeable wave silently dropped from the reading, φ_survey taken
over the SUM instead of the published union, the internal rate annualised before comparison, and φ
filled in from the survey.

**The unjudgeable branch is INJECTED, not asserted.** All six real waves touch a year with an
established fixed share, so `internal_exceeds_the_renewal_routes_ceiling` is `True` six times and the
`None` branch never runs on today's data — a leg that only read the six would be testing `all()` over
a constant. So a wave whose window touches only 2020 and 2021, the two years `published_tariff_mix`
declares unestablished, is injected; the reading must return `None` for it, must NAME the two years,
and must leave the denominator unchanged. `False` there would be a fail-open reading as *"checked,
and it did not exceed"* when nothing was checked.

**The union leg needs W1 to exist.** Waves 2–6 have zero overlap between the two actions, so summing
and unioning agree; **W1's rows exceed its published union by 14.4 weighted respondents**. The leg
requires a non-zero overlap to be present, so it cannot be satisfied by a register that happened to
store equal values — §13's own pass-branch defect, one turn later.

### Where this leaves the repair

**This finding stays BLOCKING.** The world's level is still clamped and still published, and rung 1
is unmoved. What changed:

> **The sourcing owed since §11 is discharged as an INSTRUMENT and refused as a VALUE.** φ is not
> closed and is not closeable by this survey, because the survey's second row carries `J_svt` with
> it. What is now established, with no assumption beyond `J_svt ≥ 0`, is that **the dominant
> internal-switching route in the GB record is default/SVT households re-contracting with their own
> supplier — a route `simulation/renewals.py` does not model at all** — and that this widens §9's
> hazard gap rather than closing it.

One thing owed, and it has changed identity: **not φ, but `J_svt`** — the rate at which
default-tariff households take a fixed deal with their existing supplier. It closes the system by
supplying the unknown instead of the ratio, it is the easier of the two to imagine a
supplier-returned series carrying, and unlike φ it names a mechanism the world is missing rather
than a constant the world would have to be given.

— Delivery seat, 2026-09-04.
