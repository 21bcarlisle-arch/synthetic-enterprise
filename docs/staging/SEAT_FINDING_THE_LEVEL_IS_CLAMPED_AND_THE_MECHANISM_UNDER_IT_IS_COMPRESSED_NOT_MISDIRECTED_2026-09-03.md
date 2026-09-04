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
