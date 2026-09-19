**Severity:** LATENT · **Lane:** C_customer_ops / world · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, claim `a-producer-of-default-tariff-arrivals`

# The world now mints default-tariff arrivals, and three drafts of the control passed under its own mutation

*The producer landed and the exit is reached. The more expensive result is the second one: the
tripwire written in August to catch exactly this event never fired, and three successive rewrites of
it also passed under the mutation they named. "Opens on SVT" is over-determined by the label — two
independent mechanisms produce it — so every draft that asserted the opening was measuring
something other than the thing it was written for.*

**Delivery seat, Lane 0, 2026-09-19.** Premise re-measured before starting: the item cites
`05684780e`, already an ancestor of `origin/main`. It is cited as an established fact to build on,
not as work to land, so the premise is intact — the same reading the arrival-exit finding made of
the same commit.

---

## 1. What was owed and what landed

`docs/staging/SEAT_RESULT_THE_ARRIVAL_EXIT_REACHES_A_PRICED_BOUNDARY_AND_NO_ROSTER_MINTS_A_HOUSEHOLD_THAT_CAN_TAKE_IT_2026-09-19.md`
§5 measured **232 of 232** roster records at `tariff_type: None`. The arrival-exit was reachable code
behind an unreachable input. This is the input.

| | before | after |
|---|---|---|
| live roster (`run_phase2b.CUSTOMERS`, 226) | `None` × 226 | `None` × 191, **`svt` × 35** |
| `resolved_tariff_type` over the roster | `fixed` × 226 | `fixed` × 191, **`svt` × 35** |
| SVT-origin electricity accounts reaching a non-SVT term | — | **19 of 31** |
| first non-SVT term index, those 19 | — | 4, 5, 10, 15, 20, 25 (min **4**) |

`MIN_TERM_INDEX_FOR_UPLIFT` is 1, so every one of those conversions clears the `acquisition_term`
stage — the guard the arrival-exit finding traced and predicted would be cleared "with three indices
to spare". It is, by the mechanism that finding named: `term_indices` increments on every term in
`all_terms` with no branch on `tariff_type`, so a cap segment consumes an index exactly as a fixed
term does. The 12 of 31 that never convert are passive households, which is the world deciding and
not a defect. The gas leg builds without special-casing (20 SVT segments, 6 fixed).

**Done, as the item defined it:** households arrive on the default tariff, take the exit, and reach
a term the arm's funnel admits. What is NOT yet measured is the published decision count — see §5.

## 2. The number, and why it is not the published SVT share

This is roadmap item **C6**, and `docs/market_research/gb_domestic_default_tariff_share_2016_2025.md`
§4 had already named this absence as the cause of the world's shortfall: *"home-move-onto-incumbent
does not exist in this world."*

**The quantity had to be defined before it could be sourced, and the obvious anchor is the wrong
one.** The published default-tariff share is a **stock** — the share of the book sitting on SVT at a
point in time. What the draw needs is a **flow**: of the accounts a supplier opens in a year, what
share open on the incumbent's default tariff. Setting the flow from the stock would also have
violated `simulation/svt_product.py`'s standing rule in terms — the published split is the CHECK on
this output and never an input, and `simulation/` may not import `tools.published_tariff_mix` at all.

So an account opens by exactly one of two routes, and both are published:

    share = m / (m + s)

- `m` — move-ins per household-year, by tenure. English Housing Survey 2024-25, Annex Tables 1.1 and
  3.7 (fetched 2026-09-19). Owner-occupier **3.8%**, private renter **17.5%**, social renter
  **4.6%**. A move-in takes supply without agreeing terms, so a deemed contract arises automatically
  with the incumbent at default-tariff rates, cap-protected — the licence position, quoted in
  `docs/domain_artefact_library/scope_briefs/ADVISOR_SCOPE_BRIEF_CHANGE_OF_TENANCY_2026-08-07.md`.
- `s` — external changes of supplier per domestic electricity account-year, from the regulation
  commons already readable by `simulation/`.

Both count **account openings per account-year**, which is what makes the ratio a share. Produced,
at the high end of each switching band (the anti-flattering tie-break, which gives the *smallest*
default share):

| year | owner | private rent | social rent | population-weighted |
|---|---|---|---|---|
| 2016 | 0.176 | 0.498 | 0.208 | 0.243 |
| 2020 | 0.141 | 0.432 | 0.167 | 0.200 |
| 2022 | 0.467 | 0.803 | 0.517 | **0.539** |
| 2025 | 0.174 | 0.494 | 0.205 | 0.240 |

2022 is the record's own natural experiment and the shape is not tuned: switching collapsed to ~4%,
so the same move volume is a much larger share of a much smaller inflow. On the live roster this
lands at 35 of 226.

**Two declared weaknesses, both biasing DOWN.** The per-tenure flows sum to 1.62m against the same
report's headline 1.8m movers, because EHS does not break out every inter-tenure flow; the shortfall
is carried by `move_rate_reconciliation()` rather than distributed, because distributing it would
invent a split nobody published. And this is one of three routes onto SVT — never-engaged and
rolled-off-a-fixed already exist (C1b). Both make the repair *understate* itself.

**R13.** Baseline-world fidelity change. Its warrant is that the world's SVT share is below published
in every comparable year and 0.0% in 2016 against a published 66–74%. **The direction was known
before it was built and is not claimed as a blind prediction** — what was not chosen is the
magnitude, which falls out of two published rates and a ratio.

## 3. The expensive result: a tripwire that never fired, and three rewrites that also didn't

`test_the_world_still_has_NO_standard_variable_product_to_assign_the_rest_to` was written on
2026-08-28 with an explicit instruction in its own docstring: *"When the SVT product lands, this
test is the one that should be updated."* Its assertion was `'"svt"' not in src.lower()` over
`simulation/renewals.py`.

**The SVT product landed on 2026-08-30 and it stayed green for three weeks.** `renewals.py` branches
on the product through the imported constant `SVT_TARIFF_TYPE`, so the literal three characters in
quotes never appear in that file. A grep for a NAME is blind to the MECHANISM implemented without
it. Nothing anywhere noticed, and the test could not have been mutated to fire at all.

The rewrite then failed three times, each caught by running the mutation rather than by reasoning:

| draft | assertion | why it passed under `if tariff_type == SVT_TARIFF_TYPE:` → `if False:` |
|---|---|---|
| 1 | `svt` in the schedule's set of kinds | the **C1b passive roll** also emits SVT segments |
| 2 | `schedule[0]` is `svt` | a household passive at its FIRST boundary rolls onto SVT at index 0 |
| 3 | a bound pair — same household as switcher vs mover — differing at index 0 | same cause, one layer deeper |

**The generalisable finding: "opens on SVT" is over-determined by the label.** Two independent
mechanisms produce it — the arrival branch, and `rolls_active_renewal` reading `tariff_type` and
returning False for an SVT household. Neuter either and the observable survives on the other. The
observable belonging to the arrival branch **alone** is not the opening but the **exit**: without the
branch the household never leaves the default tariff.

That is now leg 3, and it fires. The bound pair is kept, because it is what establishes the subject
is not a passive roller — assert the pair CAN discriminate before asserting what it says.

## 4. Controls, all mutation-proven

`tests/simulation/test_the_default_tariff_arrival_producer.py`. Seven mutations run in a HEAD extract
and reverted; each was checked for firing on **its own** leg, not merely for going red.

- the partition is **one** control over both branches, not a leg each — a producer labelling
  everything passes "some are svt", and the pre-C6 world passes "some are None". Both mutations run
  in both directions (410/0 and 0/410).
- domestic-only carve-out. **Its subject had to be manufactured**: `DEFAULT_SEGMENT_WEIGHTS` is
  `{"resi": 1.00}`, so written over the default draw this control would have asserted over an empty
  list and passed for free forever. The fixture overrides the weights; the population assertion is
  what caught it.
- the unlabelled remainder still gets no upliftable product — the 2026-08-28 determination stands,
  and C6 does not overturn it by the back door.
- **the arrival PATH**, which is the item's own stated test for insufficient work.
- the share is keyed to the mechanism (it must rise as switching falls), never to today's value.
- fail-closed `None` outside the commons' years, with the reverse clause so a function returning
  `None` for everything cannot pass it.
- the move anchor reports what share of published volume it carries. No silent caps.

Also classified in `_NOT_A_LEVEL_READING`: this module's two readings, plus
`tools.fit_year_level_anchor:_BASE_RESTRICTION_THRESHOLDS` — **not authored here**. It landed with
another lane's work on 2026-09-19 and left the commons census red for every lane, so it was cleared
in the same pass rather than routed around. It is a 0.0-to-1.0 sweep grid; holding eleven evenly
spaced tenths to the switching band would be holding the x-axis to the y-axis.

## 5. Pre-registration, filed before the answer is known

The arrival-exit finding's **P1** said the next `run_value_cycle_ab` would report
`decisions_that_existed = 107`, unmoved, *"because no household enters it"*. That premise is now
false by construction, and P1's own escape clause names this exact case: *"a roster change landing a
record with `tariff_type` set."*

**P2 — mine, and it is P2 of that finding made live.** The next completed `run_value_cycle_ab` on
this roster will show `decisions_that_existed` **above 107**, with the increment appearing in
`priced` or `declined` and **not** in `acquisition_term`, and `no_observed_history` staying at zero.

*What would make P2 wrong:* the cap stint failing to settle; a guard between `decide_renewal_rate`
and `margin_arm_uplift` that neither I nor §4 of that finding found; the 19 conversions falling
outside the A/B's own observation window. **If `decisions_that_existed` moves but
`acquisition_term` moves with it, that is the term-index mechanism and not new arrivals** — read the
stage counts before attributing it, exactly as P1 required.

**This is not yet measured.** A full run is hours and this is a bounded invocation; the landed
increment is the producer and its controls. Everything in §1 is measured on the live roster and on
built schedules, and nothing above rests on a run that has not happened.

## 6. A ratchet red that is not mine, measured rather than assumed

`test_static_quality_ratchet` reds in the shared tree with *"I001: baseline 1308, now 1307"*, whose
prescribed remedy is to lower the baseline. **I did not, and the measurement is why.**

Measured in a `git archive HEAD` extract, per that log's own standing rule — the tree the commit
WOULD create, never the dirty shared tree:

| tree | I001 |
|---|---|
| clean HEAD | **1309** |
| clean HEAD + exactly this commit's files | **1309** |
| the shared working tree | 1307 |

**This commit moves I001 by zero**, and none of its five python files carries an I001 at HEAD or
after. So the −2 in the shared tree is another lane's uncommitted fix and is theirs to bank. Banking
it here would freeze a floor no committed tree reaches and red every lane the moment this landed
alone — which is exactly the lesson the 2026-09-01, 09-08 and 09-16 entries in that log each paid
for.

Separately, and worth its own line: **clean HEAD reads 1309 against a frozen baseline of 1308**, so
the ratchet's other leg is red at HEAD for a reason that predates this work. That is a HEAD red
owed to whichever lane raised it, not a thing this commit can clear.

## 7. Owed

- The run in §5, and P2 settled against it.
- **The gas leg's label asymmetry is now partly live.** The 2026-08-30 addendum to the determination
  recorded that a won account's electricity leg carries `tariff_type` present-and-`None` while its
  gas leg omits the key and defaults to `"fixed"`. C6 mints on the electricity path; 4 drawn gas
  legs now carry `svt`, and the asymmetry between *drawn* and *won* gas legs is untouched. It
  remains latent — the commodity guard refuses gas a stage earlier — and it remains owed.
- **`svt_generated_share_check` should be re-run.** It is the check on this output and it has not
  been run since the producer landed; the world's SVT share will have moved toward the published
  series, and by how much is a measurement nobody has taken. It must stay a check: if the share has
  to be set to land in range, the behaviour is wrong.
