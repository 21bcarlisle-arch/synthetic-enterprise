# Delivery-seat stretch log

*What each stretch of work was about, what it got wrong, and the reasoning behind the calls made in
it. The commits record what changed; this records why. Newest first.*

*Written by `tools/stretch_log.py` as part of finishing a piece of work, not as a separate step.
A stretch that lands commits without an entry here is a finding, raised by `--check`.*

---

## 2026-09-18 — the gas half of the shape switch settled money and reached no reader -- it was carried into a print, and its own docstring said otherwise

<!-- head: 531d869285f2 -->

**Written 2026-09-18 ~12:20 BST.** Stage 1, the half-hourly shape reaching the book — the GAS half,
which turned out not to reach a reader at all.

## The electricity half is published; the gas half was printed

The electricity side settles 130 of 136 premises on fabric physics and publishes
`demand_provider_by_customer` and `fabric_eligibility` into every run artefact, so anyone can see
who is fabric-driven and why the rest are not. That is how the 213-to-0 weather refusal result was
readable at all.

The gas side does the same work: `seasonal_gas_splits_for_book` decides, once for the whole book,
which households settle on **their own** seasonal gas shape and which keep the population 70/30
split, and `run_phase2b` settles the gas term on that decision at line ~3012.

**And then prints it.** `gas_heating_fraction_by_customer` and `gas_shape_refusals` reached no
artefact. A reader of a run could not tell whether the per-household seasonal shape had arrived in
the gas book at all, or how many households were quietly on the population constant — which is the
electricity side's exact state before its provider split was published beside it.

## The code already claimed otherwise, and that is the third instance this week

`SeasonalGasRefusal`'s own docstring:

> *"Why this household has NO per-household seasonal shape, carried rather than discarded so a
> customer silently keeping the population constant is visible in the run instead of inferred from
> its numbers."*

It was visible on a terminal nobody keeps. The reason was genuinely carried — into a `print`.

That is the same shape as the two controls `fabric_demand_path` names as *"the failable control"*
and which did not exist (2026-09-17), and as the stretch-log constants whose comment promised *"a
machine that lands nothing for three days owes a report"* while the code one screen below made that
entry impossible (2026-09-18, the director's own diagnosis). **A docstring stating a property is not
the property.** Three in three days, all found by reading the prose beside the code rather than the
code — which is the cheapest place I have found defects all week.

## The repair

`gas_shape_provider_by_customer` and `gas_shape_refusals` now go into the run's returned mapping,
where the publisher writes them, beside the electricity split. The provider key is named to mirror
`demand_provider_by_customer` deliberately: one question, two fuels, and a reader who has to learn
two differently-shaped keys for the same question is a reader who will read one and assume the
other — which is how the gas half stayed unread while the electricity half was being quoted daily.

## The control, and why it is AST

`tests/simulation/test_the_gas_half_of_the_shape_switch_reaches_a_reader.py`, 3 legs, keyed to what
the module **returns** rather than to the names appearing in it. That distinction is the whole
defect: these names existed in the module — computed, printed, used to settle money — and did not
reach the caller. **A grep would have been satisfied by the print statement that was the problem.**

It carries a population floor (no returned dict with string keys at all is a refusal, not a pass),
and a second leg asserting the electricity half is still published — otherwise the gas key could
pass while the run as a whole went back to publishing no provider split, and the reader would be no
better off for the half that survived.

Mutation-proven: renaming the published key reds it with the sentence a reader would need.

What this does NOT do is restate the partition — every customer in exactly one of the two states is
`seasonal_gas_splits_for_book`'s own guarantee and `tests/simulation/test_household_demand_shape.py`
already covers it, along with every refusal reason. This file is only about reaching a reader.

## What is still unmeasured

**How many gas households actually settle on their own shape.** The keys are published now; the next
run will carry the counts, and until one completes I do not have them and will not guess. The
electricity half's answer took a run artefact to state, and so will this.

---

## 2026-09-18 — the sample earns its place on the average a book is summed over, not just on a KS -- and the cull settles a book 3.2% leakier than the population

<!-- head: 1d38d1d811ca -->

**Written 2026-09-18 ~11:50 BST.** Stage 1, on the director's budget instruction to spend what is
left on the people layer, the half-hourly shape, and the sample earning its place — and *"more of
that and less of the rest"*, that being the book-wide spread.

## The sample earns its place on the thing a book is actually summed over

`grade()` already answered *"is the settled sample's DISTRIBUTION closer to the population's"*, and
§A's P1b holds on it at 1.66x on the worst axis. **That is not the claim the sample has to earn.**

The settled book is the population every published figure sums over — margin, carbon, the
intervention ranking — and what those figures inherit is the sample's **error on the mean**, not its
distributional distance. The two can disagree: KS is driven by the worst point of the CDF, a mean is
driven by the tails' mass, so a sample can be distributionally closer and estimate the average
worse. A book summed over it would then be more wrong while the headline statistic improved.

Measured on the live campaign — 502 candidates, cull settling 90, chosen-and-weighted settling 83:

| axis | cull error | chosen error | shrink |
|---|---|---|---|
| `floor_area_m2` | −1.188% | −0.660% | 1.8x |
| `fabric_w_per_k` | +0.795% | −0.107% | **7.4x** |
| `raw_infiltration_ach` | **+3.165%** | +0.075% | **42.2x** |
| `customer_years` | −0.890% | −0.367% | 2.4x |

**Choosing estimates the book better on all four axes.** Not a split, and the verdict is reported as
a count of axes rather than a mean of ratios, because averaging per-axis ratios lets one near-zero
denominator carry the answer — the "two true numbers whose ratio is not a quantity" shape.

**The error is reported SIGNED, and the sign is the finding.** The cull does not merely mis-estimate
infiltration, it **overstates** it by 3.2%: the count rule settles a book leakier than the population
it is drawn from, and on a gas-heated book that overstates space heat. A book 3% too leaky and one
3% too tight are different errors with different consequences, and an absolute value would have
reported them as the same.

## And it answers the question I left open on 2026-09-16

That result recorded, as the thing it could not explain:

> *"The 4.54x on infiltration against 1.37x on `fabric_w_per_k` is not explained. The chooser is
> spanning the axis the population is most spread on, which is the expected behaviour of a
> space-filling criterion, but expected is not measured — and `fabric_w_per_k` is the axis the demand
> model is most sensitive to. Whether choosing harder on the axis that matters most beats choosing
> on the axis that spreads most is a real question and it is unasked."*

It is asked now, and the premise was wrong. The chooser is not spending its effort on a merely
spread-out axis: **infiltration is where the count rule is most biased** (+3.165%, four times any
other axis's error), and choosing collapses that to +0.075%. The KS profile and the estimator profile
agree about which axis the old rule hurts most, which is the opposite of the "wasted on the spread-y
axis" reading I had in hand and did not test.

## Controls

`tests/tools/test_the_settled_sample_is_graded_on_the_average_it_would_have_you_report.py`, 7 legs,
about the INSTRUMENT rather than today's result — so a future run that disagrees is read as a
disagreement and not as a bug. All three verdict states are asserted reachable, including SPLIT,
which is the one a real deterioration would land in. A split is **never resolved by majority**: three
axes better and one worse is a split, because the book is summed over all four at once.

Mutation-proven: dropping the weights from the arm's mean leaves a working function that returns the
*unweighted* membership mean — a plausible, silent, wrong answer — and the weighting leg reds on it.

## What this does not claim

One campaign, one seed, one window. It says the shipped chooser estimates these four inputs better
than the rule it replaced; it does not say the estimates are good enough for any particular figure,
and it is not a demand measurement — turning each candidate into annual kWh would need a trace
apiece, and the axes ARE the demand model's inputs, so estimating them badly is what makes the
outputs wrong.

---

## 2026-09-18 — the log fired on completion so a day of drift owed nothing -- now it fires on a clock; and P2 says one headcount per house moved net -0.51%

<!-- head: 26c10f997770 -->

**Written 2026-09-18 ~11:20 BST — the first entry written because the CLOCK said so, not because a
piece finished.** That change is the first half of this entry; P2's result is the second.

## The log fired on completion, so a day of drift owed nothing

The director's diagnosis, and he named the mechanism before I found it:

> *"The stretch log writes when a stretch completes. A day of machinery — reds, merges, publisher
> fixes — never completes a stretch, so nothing gets written, so you never have to state what the
> stretch achieved. A machine that never says what it achieved can't notice when it achieved
> nothing. That's the self-correction loop broken exactly where reflection would happen, and it's
> why the log records the wins and misses the drift."*

It was two lines in `owed()`:

```python
if n == 0:
    return {"owed": False, ..., "reason": "up to date"}
```

**A stretch that landed nothing was reported as up to date.** The one state most worth reading was
the one state that could never be reported.

And the constants directly above those lines had *already written the intent down*: *"OR, not AND: a
machine that lands nothing for three days owes a report as much as one that lands three hundred
commits in an afternoon."* That sentence has been false for as long as it has existed, because the
code one screen below contradicted it. **A comment stating a property is not the property** — the
same shape as the two controls named as "the failable control" that did not exist, found two days
ago in `fabric_demand_path`.

**The repair.** `CADENCE_HOURS = 3` is the entry condition; the commit count is a second reason,
never the gate. Escalation is the clock alone — past the cadence, whatever landed, including
nothing.

**What I got wrong doing it, twice, and both were caught by tests rather than by me.** First I
collapsed `owed` into `escalate`, which would have paged every publish cycle and earned the alarm
exactly the reader the run log had — the existing suite's own reachability test caught it, and its
reasoning was right even though its framing ("a report is written when a piece of work FINISHES")
was the thing being abolished. Second, my new control asserted the clock was the *only* trigger,
which is stronger than the design says; asserting more than the design is how a control ends up
arguing with its subject. Also a crash: my "nothing landed" message formatted `hours` as a float in
the one branch where it can be `None`.

Controls: `tests/tools/test_the_stretch_log_fires_on_a_clock_not_on_completion.py`, 7 legs.
Mutation-proven by restoring the exact two lines above — three legs red, naming the defect.

## P2: what one headcount per house did to the money

Owed since 2026-09-16, pre-registered in `b2f83bc2d` **before either arm reported**. Two arms of
`run_phase2b.main()`, same tree, same book, same weather, differing only in whether the physical
layer keeps its own second headcount draw.

| | control (two draws) | treated (one draw) | move |
|---|---|---|---|
| revenue | £685,541.28 | £683,074.19 | **−0.36%** |
| net margin | £143,853.25 | £143,125.42 | **−0.51%** |
| bad debt | £30,396.91 | £30,611.68 | +0.71% |
| fabric premises | 130 of 136 | 130 of 136 | — |

**P1 (volume < 1%) — NOT GRADED.** `total_volume_kwh` came back 0.0 in both arms: the settlement
records do not carry a `volume_kwh` key. **That is the fourth time this week I have read a working
instrument as a broken one by asking it the wrong question**, and I wrote the memory about exactly
this yesterday. It is not graded rather than graded as zero, because zero is what a missing key
looks like.

**P2 (revenue and net each < 1%) — HOLDS on the first half, REFUTED on the second.** Both moved
under 1%. But I predicted net would move *proportionally less* than revenue, because the standing
charge is per-account and cannot move when no account is gained or lost. It moved **more**: −0.51%
against −0.36%. Bad debt rose 0.71%, and that is the direction to look — a reassignment that moves
demand between homes moves bills, and bills that move move arrears. The standing-charge argument was
right about the standing charge and wrong about everything downstream of a bill changing.

**P3 (direction) — I refused to predict it, and both moved down.** Recording that I declined is what
stops me now claiming I expected it.

**P4 (fabric population unchanged) — HOLDS.** 130 of 136 in both arms.

**The second kill line tripped as written, and its purpose held.** I required both arms to report the
same record count; they differ by 489 of ~301,500 (0.16%). But record count is customer-periods, and
a headcount change moves demand → bills → arrears → departures, so a different record count is a
*consequence* of the variable, not evidence of a second one. The invariant I actually needed was the
**customer population** — 136 customers, 130 fabric-driven, identical in both arms. **The kill line
was mis-specified**, and saying so is better than quietly reinterpreting it: what I wrote down was
not the thing I meant, and the thing I meant held.

**What this does not say.** −0.51% on net is one book, one window, one seed. It is not a claim that
the correction is worth £728; it is a measurement that aligning the headcount did not move the money
much, which is what a fidelity fix with no distributional change should do. The change was justified
on fidelity alone and this number was neither the reason nor a check on the reason.

## Next

Stage 1 only, on the director's budget instruction: the people layer, the half-hourly shape reaching
the book, the sample earning its place on settlement selection. More of what the book-wide spread
was.

---

## 2026-09-17 — one house had two headcounts for 102 of 134 homes, and the red that found my wrong fix was a table that made a six-person home impossible

<!-- head: 2cc924ed9cf5 -->

**Written 2026-09-17 ~16:20 BST**, on finishing the people layer — the last of the four pieces the
director named this afternoon.

## One house had two headcounts, for 102 of 134 homes

Two functions drew the household size, and both were right:

- `household_physical_layer.people_count_for` — a band-then-within-band draw from ONS TS017 on
  substream `physical_layer_people_count_<id>`. **This is what the fabric path traces a premise on,
  and 130 of the book's 136 electricity premises settle on the fabric path.**
- `dwelling_records._derive_people_count` — a second TS017 draw on a different named substream, and
  what the PROPERTY RECORD carried, so what the legacy comparison arm, the EPC multipliers and the
  switch verdict all saw.

Neither was wrong about the population — property mean 2.388, physical-layer 2.485, ONS 2.37. **The
per-home assignment was two different answers to one question**, disagreeing for 102 of 134 homes by
as much as five people. The fabric path would trace a house holding one family while the property
record billed it for another.

`occupancy_band_for` names this exact shape in its own docstring — *"two draws of one quantity is
the defect this module just fixed"*. It was committed again, one module over, by the module that had
just written the warning down.

**And a third answer, which is why seven homes survived the first repair.** `build_properties`
applied `PEOPLE_COUNT_BY_CUSTOMER.get(cid) or _derive_people_count(cid)` **inline**, so the authored
roster outranked the draw at that one call site and nowhere else. A precedence written at a call
site is a precedence the next caller does not inherit. The precedence — authored > output area >
national — now lives in the function, and all three readers get it.

**134 of 134 agree.**

## The delegation direction was wrong first, and a red found it

I pointed `people_count_for` at the leaf and a test went red: mean headcount 2.260 against the
census 2.37. I did not touch the tolerance. Measured instead, at n=20,000:

| | 1p | 2p | 3-4p | 5+p | mean |
|---|---|---|---|---|---|
| leaf draw, as it was | 30.8 | 33.62 | 28.44 | 7.14 | **2.3167** |
| physical-layer draw | 30.23 | 34.48 | 28.24 | 7.04 | **2.3584** |
| ONS TS017 | 30.1 | 34.0 | 28.9 | 7.0 | 2.37 |

Both reproduce the **bands**. The gap is entirely in the tail: the leaf's table ended `(5, 0.070)`,
collapsing the whole 5-or-more band onto exactly five people. **That is right about the band and
wrong about the households in it — it makes a six-person home impossible**, and it costs 0.042 on
the mean, all of it in the largest homes, which are the ones with the most demand to get wrong.

So the leaf got the published split (5/6/7/8+ at 4.5/1.5/0.5/0.4%), which was already written down
in this repository in `_WITHIN_BAND_SHARES`. Nothing was invented; the table moved so there is one
copy, because two copies disagreeing is how the world came to hold two headcounts for one house.

## A second red, and it caught a real error in my own table

`test_the_household_size_anchor_agrees_across_its_copies` went red. The published within-band
figures sum to **6.9%** while the published band is **7.0%** — a rounding gap in the source. I had
written them in raw, so the whole table summed to 0.999 and one roll in a thousand fell off the end
into the float-rounding fallback. Renormalised into the band, the table sums to 1.0 and the 5+ total
is exactly the published 7.0%.

That control also had to change, and the change is worth stating because it is a **loosening**.
It asserted dict equality between the world's draw and `demand_model.HOUSEHOLD_SIZE_POPULATION_SHARE`.
Those two copies stopped being the same shape: `demand_model`'s is the fixed reference population
the volume normaliser divides by, held at 1/2/3/4/5+ **deliberately** — *"held here rather than
imported so the volume normaliser cannot be silently re-levelled by an unrelated edit to the segment
bands"*. Extending it would do exactly what that comment forbids. So the control now asserts what
must actually hold: 1-4 shares identical, and the world's tail summing to the published 5+ band.
Dict equality was forcing a choice between a draw that cannot make a six-person home and a
normaliser re-levelled as a side effect.

## And one tolerance I loosened, with the evidence, because it was keyed to today's answer

`test_the_headcount_reproduces_the_census_marginal` compared the mean to 2.37 with a fixed ±0.06. It
went red on a change that **altered no distribution at all** — delegation moved the draw to a
different named substream, same shares, same estimator, different assignment. One variable, over the
same 1,954 premises:

| | mean | se | z against the census |
|---|---|---|---|
| old substream | 2.3777 | 0.0308 | **0.25** |
| new substream | 2.2953 | 0.0292 | **2.56** |

and over 20,000 generic ids the two agree to four decimals. **The ±0.06 was calibrated on the old
substream landing, by luck, almost exactly on 2.37.** It is now three standard errors of the
sample's own mean — keyed to the property, "this population is drawn from TS017", rather than to
which substream drew it.

**A loosened tolerance has to be shown still to bite, or it is just a green light.** It does:
the truncated-tail table reads 2.2605 on that population, **4.08 standard errors out**, and the
refusal names the tail as the first suspect.

## What this does not claim

The distributions were always close and the book-level means barely move — this is an **agreement**
fix, not an accuracy one. What it buys is that no downstream figure can be computed over two
different households for the same address, which was silently possible in every run until now and
would never have shown up as a wrong number anywhere.

I have also not measured what it does to margin. That is the same debt the census-headcount change
left yesterday, and it still needs the money path.

---

## 2026-09-17 — the book is a spread and not rescaled copies -- 10.7x the legacy on the mean, zero near-identical pairs against the legacy path's 1,773

<!-- head: 6371f89d11fe -->

**Written 2026-09-17 ~15:30 BST**, immediately after the measurement, under the director's
instruction to keep this log current instead of interrupting him.

## The director's phase-one test, answered on the book

His words setting it: *"look across the book and see a credible spread of those, not a set of
rescaled copies of one profile."*

134 of the book's 136 electricity premises, priced over 2022-01-01..28 in their **own 131 distinct
cells**, every premise measured twice over the same window with the same household and the same
cell — once on the shipped fabric path, once on the legacy provider it replaced. The level is
divided out of every premise-day, so what is compared is shape alone.

| over 8,911 pairs | fabric path | legacy path |
|---|---|---|
| mean absolute difference in half-hourly share | **0.007966** | 0.000747 |
| median | 0.006924 | 0.000339 |
| p10 | 0.004960 | 0.000027 |
| identical pairs | 0 | 0 |
| **near-identical pairs (<1e-4)** | **0** | **1,773 — 19.9%** |
| **closest pair** | **0.0026** | **0.00000002** |

**The book is a spread, by a factor of 10.7 on the mean.** And the statistic that actually tests
"rescaled copies" is not the mean — it is the closest pair, because a healthy average can sit on top
of a duplicate. The legacy path has two premises identical to **eight decimal places** and a fifth of
all its pairs are near-identical. The fabric path has none, and its closest pair is a hundred times
further apart than the legacy path's.

The two premises not priced are a commercial office and a commercial warehouse, refused by name.

## Two defects in my own harness, found before any number left the room

**The legacy arm was a caricature and it flattered my hypothesis.** The first draft built its
property dict inline from `customer.get("occupancy_pattern", "family")` and
`customer.get("people_count", 3)` — **keys the live customer records do not carry.** So every premise
got the identical dict and the legacy arm reported *all 45 pairs identical at exactly 0.0*. That is
not the legacy provider collapsing; it is one input repeated forty-five times. It pointed the way I
expected, which is precisely when it should have been checked. It now uses `build_properties` — what
the runner itself feeds `build_demand_shape` — and the legacy arm's real answer is 0.000747 and
1,773 near-identical pairs, which is a *weaker* claim than the false one and the true one.

**And the refusals were reported by exception type.** `{'ValueError': 2}` names a class nobody can
act on. They now carry their message, which says *"the premise trace generator is DOMESTIC;
PropertyType.COMMERCIAL_OFFICE is not residential"* — a correct refusal, visibly correct. Two
hundred and thirteen identical sentences was the exact defect the whole weather run was about; I
reproduced it in the instrument built to report on it.

## Why this is a new measurement rather than a bigger old one

`book_shape_spread.measure` already existed and crosses 27 constructed households with the four
legacy archive sites. That was the right instrument while the archive *was* four sites: it asks
whether the fabric path **can** produce a spread, holding the population fixed and varying the
things that should move a shape.

It cannot answer the director's question. Its households are built by `make_household` to span era ×
insulation × property type, so the spread it finds is the spread somebody designed into it. **A panel
can prove the mechanism works and still say nothing about whether the book is a spread or a stack of
copies.** Both are kept: the panel is the capability, `--book` is the fact.

## What this does not say

It is one month, January, and a winter month is where fabric differences are largest — the same
measurement in July would be a different and probably smaller number, and I have not run it. It is
also silent on whether the spread is *correct*: it shows the premises differ from each other, not
that any one of them matches what that household would really do. That is the belief-vs-truth
question `couple_fabric` owns, and it is not this.

Next: the people layer.

---

## 2026-09-17 — the cell store is complete for every cell the book can reach, and the book now reads its own cell -- the "no weather archive" refusal went from 213 to zero

<!-- head: e18ca3ab4864 -->

**Written 2026-09-17 ~14:50 BST**, covering the W1_14 weather run of 00:30–09:20 and the five hours
after it. The director's word this afternoon: *"the weather work stopped at 07:54 and the five hours
since are publisher machinery… go back to W1_14 and keep going, and don't report back to me between
pieces."* This is the report that replaces the interrupting.

## The two pieces he named as next were already done, and I verified rather than assumed

**The cell store is complete for every cell the book can reach.** 221 cells held; 213 carry all five
fields; **149 are in the book and every one of them is complete**. The 8 incomplete cells are all
missing the same pair — `cloud_cover_pct` and `wind_speed_mean_ms`, the ERA5 half — and all 8 are
cells the book has **left**. `build_weather_world` draws its `todo` from the book, so those 8 can
never be completed by the pull loop, and it says so on the surface rather than letting a perfect run
be scored 8 short. They are kept on purpose: a cell that leaves the book keeps a current temperature
series instead of freezing.

**The book reads its own cell.** Three separate runs today agree:

| | 2026-08-27 run | 2026-09-17 runs (×3) |
|---|---|---|
| `fabric_physics` | 4 | **130** |
| `legacy_pc1_rescaled` | 203 | 3 |
| `hh_metered_reads` | 3 | 3 |
| refused "no weather archive" | **213** | **0** |

**The two shares are NOT a comparison and I will not present them as one** — the books are different
populations (210 settled customers against 136). The quantity that compares is the **refusal class**,
and it went from 213 to zero. That refusal is extinct: no premise in this book is now excluded from
physics for want of weather.

The remaining six non-fabric verdicts are all correct and none is a coverage failure: 3 half-hourly
metered (real reads outrank a generator), 2 non-domestic, 1 with no household record.

**What that means in supplier terms.** Yesterday 96.7% of the settled book priced against one
rescaled national profile. Today a household's demand comes from the weather over its own 1 km cell.
Two households in one cell get the *identical* sky by construction — the store is loaded once and
`days` is memoised per cell — so any difference between their demand is attributable to fabric and
people rather than to two different downloads. That was the director's architecture and it is the
reason this was a per-cell store rather than the per-property pull he refused in writing.

## Where the afternoon went, and he is right about it

Between 09:20 and 14:28: publisher machinery, deferred-delivery verdicts, browser probes, site-lane
reds, three merges. One of those commits is literally titled *"the full run's forty reds are two
other lanes'"*. I spent the afternoon on other lanes' failures.

The rule I did not have and now do: **another lane's red is not mine unless it blocks me, and if it
blocks me I fix the block and go back — I do not adopt their queue.** The distinction I kept getting
wrong is that a red I *can* fix and a red I *should* fix are different sets, and the gate refusing my
commit makes every red in the tree look like the first kind.

## What I found still open on this path, and it is not machinery

Two controls are named in `fabric_demand_path`'s own docstrings as *"the failable control"* for
claims this seam makes, and **neither exists**:

- `the_runner_reads_the_cell_store` — named at the `_archive_days` default as what says the
  settlement path passes `WeatherWorldSource.days` rather than the four legacy CSVs.
- `weather_days_for_two_premises_in_one_cell_is_the_same_sky` — named as what says the memoisation
  holds, i.e. that one cell means one sky.

Both are the load-bearing claims of the change that just landed, and both are currently prose. This
project's own standard is that a rule lives in prose *and* as enforced code or not at all, and the
`_archive_days` default is exactly the shape that rots quietly: it is still the DEFAULT, so a caller
that forgets to pass `weather_days_for` silently reads four CSVs and 130 premises fall back to a
national profile with no refusal anywhere. That is a product control on the demand seam, not
harness work, and it is the next thing I do.

Then the book-wide spread, then the people layer.

---

## 2026-09-16 — six days and 184 commits with no report, because the alarm that says so is hosted inside the publisher that was wedged -- and the product share is 7%, not the 36% the commit titles read as

<!-- head: c660084bb332 -->

**Written 2026-09-16 17:1x BST, six days and 184 commits late, on the director's direct question:**
*"what did today produce that a customer or a domain reader would notice? If the answer is nothing,
say so and tell me why the product-and-machinery canon isn't holding."*

This entry answers that, states the cause of its own six-day absence, and records what the split
actually is — which is worse than the director's own estimate of it.

## The answer, and it is close to nothing

The director's crude filter put 36 of 100 commits on the product side. The measure this project
built for exactly that question, `tools/product_machinery_split`, classifies by the PATHS a commit
touched rather than by its subject, and it says:

| window | product | machinery | neither | product share |
|---|---|---|---|---|
| last 50 | 2 | 28 | 20 | **6.7%** |
| last 100 | 5 | 65 | 30 | **7.1%** |
| last 200 | 11 | 140 | 49 | **7.3%** |
| last 400 | 15 | 304 | 81 | **4.7%** |

Floor is 25%. Every window is below it. **The subjects read more product-ish than the diffs are** —
that is the whole gap between 36% and 7%, and it is worth naming because a commit-title reading
flatters us by a factor of five.

Classifying today's 91 commits one at a time: **74 machinery, 10 neither, 7 product** — and three of
the seven are merges and tree-advances that carry product paths without doing product work. So the
honest count for a 91-commit day is **four**:

- **A gas-only billing account can now leave this world.** `departure_decision_leg` names, per
  billing account, the supply point the departure rolls on — electricity if the account holds an
  electricity leg, otherwise gas — replacing a literal `commodity == "electricity"` guard in two
  places. Eighteen gas-only accounts could not churn at all; the book's renewal-decision population
  nearly doubles. Four things travelled with it, each because the widened branch would otherwise
  read a fuel-specific fact about a fuel the account does not buy — including a rate-shock history
  that was permanently empty for those accounts, which reads downstream as *never had a bill rise*
  rather than *nobody looked*, understating departure risk in the direction that flatters us.
- **The gas leg rolls onto the cap** (repair 2 of the same determination; the read and the roll had
  to land together).
- **The gate that decides whose bill may scale the curve now lives with the curve.**

A domain reader would notice the first. It is a real structural blindness in the churn model, found
and closed, and it is the only thing today that a real supplier would recognise as work on the
business. The other 87 commits are the machine on itself.

## Why the canon is not holding, and it is not the dial

The canon's four pieces of WORK THIS CREATES were built. The distinction exists in code
(`classify_path`). The selector has a product-starvation override (`_product_starvation_stretch`,
supervisor RUNG 1c-override). The split is measured. The floor exists as `PRODUCT_SHARE_FLOOR`.

**Every one of them runs, and none of them can fail.**

- `tools/product_machinery_split.main()` prints `BELOW FLOOR` on all four windows and
  **`return 0`**. There is no `--check`, no non-zero exit, no alarm. Nothing anywhere consumes
  `below_floor`.
- The floor's one consumer is `supervisor._product_share_phrase()`, which composes a sentence into
  a **`log()` line**. That line right now reads: *109 commits since any product-priority atom was
  named, against a median of 6 over the last fortnight. Product share over the last 100 commits: 7%
  (5 product / 65 machinery, floor 25%).* Eighteen times the median gap, a third of the floor, and
  the only place that sentence exists is a daemon log nobody reads.

The comment above it says why, and the reasoning was deliberate and defensible: *"Logged rather than
filed: the register already exists for defects that can wait, and a rung that mints a document every
thirty minutes is the treadmill this is meant to end."* That is right about documents and wrong about
channels. It chose between *file a document every tick* and *log it* — and never considered *page
once, on the crossing*. `notify(..., transition_key=..., state=...)` has done exactly that for every
other alarm in this repo for weeks.

**So the canon's clause 4 — "the ratio itself becoming a finding when it goes wrong" — is the one
clause that was not built.** The ratio became a *sentence*. This is the class already written down
as *a finding in the routine channel is routine output*: the control fires every cycle, correctly,
and firing is indistinguishable from not firing.

And the second half is the queue. The draw this hour offered two live seats: *seat heartbeat keyed
store and cross-worktree sweeper*, and *clear nine paths so origin_reconcile can merge*. Both
defensible. Both machinery. Behind them the doorbell printed **roughly ninety unprocessed staging
documents**, of which I count fewer than ten that are about the world or the supplier. **Product work
cannot win a draw it is not in.** The override exists to let product-priority atoms jump the
blocking-finding exclusion — but an override that lets product win *when product is on the map* does
nothing when the map's top ninety items are the machine's own defects. The selector was fixed; the
queue is what chooses.

## Why this log was silent for six days, and it is not a fourth instance of the old class

The 2026-09-10 repair works. `tools/stretch_log.py --check` returns rc 1 and escalates correctly —
I ran it: *139h since the last report (escalates above 24h; longest gap this log has ever had is
16.7h); and 184 commits since the last report (escalates above 80; largest gap is 70).* The
mechanism is sound.

**Its only caller is `background/process_run_complete.py`.**

`process_run_complete` last succeeded on **2026-09-10 02:35** and did not succeed again until
**2026-09-16 14:41** — six days wedged, 34 consecutive refused publishes, a door reporting the
unpublished envelope as a skip seven times a run for 106 hours.

So the alarm that exists to say *the machine has stopped telling you why* is hosted inside the
subsystem whose failure is the loudest symptom of that. **The control shares a failure domain with
the thing it watches.** It is switched off precisely when it is needed, and its silence is
indistinguishable from a healthy machine writing its reports.

That is not *a landed fix is not a running one* — the fix was landed and its host was running, in
the sense that the process existed. It is not *a control keyed to a structure that moved*. It is a
distinct shape and it needs its own name: **an alarm hosted in the subsystem it reports on is
silent exactly when it is right.** Hosting was chosen for a good local reason — a stretch report is
owed when *a piece of work finishes*, and the publisher is where finishing is detectable. The cost
of that convenience was six days of the director having no account of 184 commits.

When it finally did fire — 2026-09-15 07:43, on a run that got far enough — it fired three times in
4.1h, and `background/alarm_repetition.py` correctly escalated it into
`docs/staging/WORKER_FINDING_REPEATING_ALARM_STRETCH_LOG_2026-09-15.md` and **suppressed the page**.
That is the escalation mechanism working as designed. The design assumes the staging queue drains.
It has not drained: that document has sat undrawn for 33 hours behind ninety others. So the last
channel that could have reached him was closed by a mechanism whose premise — *a filed defect is not
a forgotten one* — is currently false.

## What I am doing about it, and what I am not

**Doing.** Moving the stretch check out of the publisher's failure domain into the supervisor tick,
which ran throughout the six days, and giving the product floor a `transition_key`'d page so a
crossing reaches the director once. Two small changes, both in code that already exists, no new
register and no new document class. The smallest mechanism that can fail.

**Not doing.** Not raising the floor, not re-weighting the dials, not building a ratio-of-ratios.
The dial was never what chose. And not proposing a rule about how machinery findings get filed —
that would be machinery about machinery, which is the defect performing itself.

**The thing I am not fixing today and should say plainly:** ninety machinery findings in the queue
is a rate problem, not a draw problem. The machine files them faster than any draw can clear them,
and every one of them is real. I do not have a mechanism for that and I am not going to invent one
in the same hour I diagnosed it.

## Stage 1, where the rest of this turn goes

Measured first, because the premise was worth checking: **the sample does earn its place on the
settlement selection.** `tools/settlement_per_axis_gain` on this base — worst-axis KS **0.0588**
chosen-and-weighted against **0.0978** for the old uniform count cull, a **1.66x** improvement,
costing 7 settled accounts (83 against 90). P1b HOLDS. Per-axis gain runs 1.37x on `fabric_w_per_k`
to 4.54x on `raw_infiltration_ach`, a 20.7x spread — the choosing is doing almost all its work on
infiltration and almost none on fabric.

The filed evidence for this is **stale and must not be quoted**: it was measured at base 3957ba848,
which predates `0d86d6dfe` (the world's homes drawn from the fitted joint). The funnel is unchanged
and the home stock is not, so the filed KS figures describe a world that no longer exists. Five
scalars disagree. Refreshing them to this world is the first Stage 1 item, and it is a correction to
our own published evidence, not new work.

Then the people layer, and the half-hourly shape reaching the book.

---

## 2026-09-10 — the console capture read one folder while both were live, so the instruction naming the weekend's priority reached no record and the writer said it was current

<!-- head: ec46351f8aa2 -->

**Written 2026-09-10 22:1x BST**, immediately after the sample wiring landed, because I went to
check that your instruction had reached the record the autonomous ticks read before the weekend —
and it had not.

## Your words were not in the record, and the capture said it was current

`--write` printed **"no change -- records already current"** with both of tonight's turns sitting
unread on disk, including the one naming the weekend's priority.

**The cause.** A seat launched from `/` writes transcripts to `~/.claude/projects/-`; one launched
from the project writes to a derived folder. **This project runs both at once**, so both are live —
and the reader took `TRANSCRIPT_DIR` alone. First folder with files wins; the other session is
invisible.

`transcript_dirs()` was already there, already returned the union, and already said so in its own
docstring: *"The union, not a choice… **Reading only one is what broke.**"* Nothing called it except
an error message. The correct function was written for exactly this failure and left unwired, and
the reader kept the shape its docstring was written to condemn.

**Worse than the gap.** The refusal at the bottom of that module printed *"Reading: &lt;both
folders&gt;"* while the code read one. Anyone diagnosing a missing turn was told the union had been
searched. A false sentence about a control's own scope costs more than the turn it hides, because
it ends the investigation.

**Measured.** Across the union the reader finds **77 turns where it found 10**. Writing repaired
**eight day-records**, 2026-09-03 through today — every one short by turns that were on disk the
whole time. Landed with the fix, because a repair whose evidence is not committed leaves the next
reader unable to tell a fixed capture from a quiet one.

## Two controls were red for three days for no reason, and they gated the fix

Both already sat in `head_red_observed.json`, and neither was my regression.
`test_THE_CHECK_READS_THE_SAME_ROOM_THE_WRITER_WRITES_TO` wrote a record dated with the literal
string `2026-09-07` and stamped presence as `now` — so it asserted *"a record written today is not a
lapse"* while only ever writing one dated the day it was authored. Green on 2026-09-07, red every
day since. Its sibling had the same fixture, so the lapse verdict answered before the subject under
test could fire.

A control keyed to today's answer rather than to its property goes red when nothing is wrong, and a
control red for three days for no reason is a control someone switches off. Both now take the day
from the same clock as the presence stamp.

## The class, three times in one evening

This is the same shape as the stretch-log silence: **a mechanism that runs, reports success, and
carries nothing.** The stretch check fired 65 times into a log with no reader. The console capture
read the wrong folder and said "current". Both answer *"does anything call it?"* with **yes**, which
is why neither was found by the grep that finds the usual version of this.

The question that does find them is *"what does it carry, measured against something independent?"*
— which is precisely the check the console module already performs against `.human_last_input` for
its own lapse. It had the right instrument one level up from where it failed.

## Still open, and you should know about it

`check()` is still red, on a **different** finding: **the seat's side of today's conversation is
missing.** The `DIRECTOR_CONSOLE` record for 2026-09-10 now holds your turns and the `SEAT_REPLY`
record holds none, so that channel shows a reader the instruction and not the answer. The Stop hook
either is not firing for this session or writes somewhere the check does not read.

It does not cost you anything tonight — the answer is in this log, which is where you asked for it —
but the advisor channel is half a conversation until it is fixed. It is a separate subject from the
sample and I have not chased it, because you asked for the sample to be the only thing.

---

## 2026-09-10 — the generator is wired into the world's stock and the chooser is refused with a number, and the insulation ceiling the company sells against was understated by a third

<!-- head: 59a91d4a2be3 -->

**Written 2026-09-10 21:xx BST.** Director console the same evening: *"Wire the sample. That's the
priority until my allowance resets Monday morning, and I'd rather it were the only thing… the
population the world runs on should be the one the sampler chooses, weighted, and the settlement
budget should be the constraint we argue about rather than the one that silently refused 409 wins."*

**The generator is wired. The chooser is not, and that is a decision with a measurement under it
rather than an omission.** Read the second section before the third if you read nothing else — it
is the part where I measured the instruction's premise before building on it and found half of it
does not hold.

---

## What is landed

The world's homes are now drawn as whole rows of the **NEED-fitted joint** — 1,292 combinations that
were actually observed together — **raked onto this world's own published marginals**, instead of
three attributes from a 144-cell joint followed by heating, bedrooms and insulation drawn
independently or by lookup. The dwelling record gained four measured facts it did not have:
`floor_area_band`, `has_loft_insulation`, `has_cavity_wall_insulation`, `has_mains_gas_supply`.

Evidence supplies the **structure**; the published record supplies the **margins**. That split is the
canon's own — *"NEED is EVIDENCE, NOT POPULATION"* — and without it this would have been a fidelity
regression wearing an improvement's clothes: the world would have gained real co-occurrence and lost
the published composition it already had. The rake hits all three published margins to 1e-6.

## The measurement I took before building, and what it refuted

**The chooser buys nothing at the size the world runs.** `choose_for_difference` + `fit_weights`
against five random draws, worst KS across the six demand axes, 20,000-point population:

| N | chosen + weighted | random | ratio |
|---|---|---|---|
| 40 | 0.1361 | 0.2280 | **1.68×** |
| 91 | 0.0885 | 0.1448 | 1.64× |
| 400 | 0.0457 | 0.0597 | 1.31× |
| **4,400** — the world's stock | **0.0177** | **0.0184** | **1.04×** |

The design's whole value is compression, and at 4,400 draws out of a 20,000-point population there
is nothing to compress. Wiring it into the stock would have been machinery that changes no number.
So the instruction's first half — *the population the world runs on should be the one the sampler
chooses* — is **built** in the sense that matters (the generator) and **declined** in the sense that
does not (the chooser), with the table above as the thing to overturn if you disagree.

I have also **stopped quoting the "22× better than random" figure** from the 08 September reply. It
does not reproduce on KS distance at any N I measured; best case is 1.68×. It was probably measured
on distinct cells covered, which is a different quantity. Filed as its own question rather than
repeated.

**`smallest_n_chosen` returns 5,215** under its per-stratum criterion. The world's 4,400 is *below*
the sampler's own acceptance threshold — it is not a candidate for reduction from it, which is the
opposite of the framing everyone including me had been carrying.

## The correction that matters most, and it is against my own claim

I wrote — in the pre-registration, in two module docstrings and in a test file — that the demand
vector was **unmeasurable** on the world's population because `Household` had no floor area, and
that this was why `demand_vector_coverage` had no importer under `simulation/`.

**That is wrong.** `fabric_physics.floor_area_m2` derives an area from property type and bedroom
count; the six axes always evaluated. I found it by reading the function I was about to claim was
missing an input, after I had already written the claim down three times.

What is actually true is narrower and, I think, more useful: the area was **inferred from a bedroom
count that was itself drawn from property type alone**, so it carried nothing the property type did
not already carry; `insulation` was a **lookup on the EPC letter**, six values for the whole country;
`has_solar` was **hardcoded `False`** on every drawn home.

So this is a **level error on the mission's own quantity**, not a missing capability. At 4,400 homes,
weather held constant:

| | old (inferred) | new (measured) |
|---|---|---|
| mean floor area | 79.4 m² | 84.8 m² |
| mean fabric | 144.4 W/K | 168.8 W/K |
| **mean remaining insulation ceiling** | **41.5 W/K** | **61.4 W/K** |
| 10th percentile of that ceiling | **0.0** | 2.0 |
| spread (cv of fabric W/K) | 0.729 | 0.744 |

The remaining insulation ceiling is *what is left to do* — the size of the measure a household could
still be sold, which is the thing the company exists to find. **The old world understated it by a
third, and told us a tenth of the country had nothing left to insulate**, because an A/B rating
mapped to FULL insulation by construction. The spread barely moves. The level was wrong.

## The pre-registration, graded

Filed before the build, at `docs/staging/records/SEAT_PREREGISTRATION_WHAT_WIRING_THE_GENERATOR_
INTO_THE_WORLDS_STOCK_MOVES_2026-09-10.md`. **Three of seven hold, three fail, one was the wrong
question.**

| | prediction | outcome | |
|---|---|---|---|
| P1 | published marginals move < 1.0pp | worst move 1.84pp | **FAILS as written** |
| P2 | solar 1.2–2.2% | 1.50% (from 0.00%) | HOLDS |
| P3 | > 12 distinct (epc, loft, cavity) triples | 19 (from 6) | HOLDS |
| P4 | demand vector "becomes computable" | it always was | **WRONG QUESTION** |
| P5 | \|Δ net margin\| > 1% | **−0.37%** | **FAILS** |
| P6 | sample rate 0.183±0.005, refused 409±10 | 0.1820, 409 — identical both arms | HOLDS |
| P7 | accounts 582±30, settled 173±15 | 582 / 173 — identical both arms | HOLDS |

**P1 failed because I graded a population prediction on a sample.** The band compared the new stock
against the *old sample*; the property that matters is whether each stock carries the *published*
marginal. Asked that way the new stock is better: worst |z| against published on EPC goes **3.03 →
0.87**. A 1.84pp gap between two independent 4,400-draw samples is 2.0 standard errors across
sixteen categories.

A single-seed reading then nearly produced a second error on top of the first: `ERA_1919_1944` came
out **3.29 standard errors light**, which reads exactly like a biased band→era mapping. I checked
`_weighted_choice` (unbiased over 200k draws), checked the premise-keyed uniforms (χ²=4.05 on 9 df),
and then ran five seeds: mean z **−0.09**, no era beyond |0.44|. It was the draw. That is now a
control rather than a note, because a real bias there would be invisible to every other test.

**P5, P6 and P7 together are the R13 evidence.** Margin moves −0.37%; the book is identical to the
account — 582 commercial, 173 settled, 91 of 500 wins settled, 409 refused — in *both* arms. The
funnel and the settlement budget are insensitive to what the dwellings are. A baseline fidelity
change that leaves the score alone is the cleanest evidence available that it was not tuned against
the score. It also says plainly: **this buys fidelity, not profit.** Anyone reading the commit for a
P&L story should stop.

## Calls made, and where I stopped

- **Both arms run at one HEAD with one variable changed**, from a driver outside the tree rather
  than an env var or two tree states — no switchable surface left behind for a later run to drift
  on. Old arm 13 min, new 15 min. The published £147,887 was *not* used as the baseline: it comes
  from a different configuration, and comparing against it would have been the two-variables-changed
  error in the very document that exists to avoid it. The correct baseline is £376,131.94.
- **`AGE_TO_ERA` was the trap I walked up to.** NEED's four age bands map to this world's six eras,
  and `demand_case_coverage.AGE_TO_ERA` already maps each band to one representative era. Using it
  would have **erased `ERA_1919_1944` and `ERA_1965_1980` from the country** and moved the published
  era marginal by fifteen points. It is correct for what it is for — a fabric vector needs a
  representative age — and wrong here. Same table, different subject. The world gets a Bayes
  posterior instead, which reproduces the published era marginal to 0.0 exactly.
- **NEED's fuel flag is NOT mapped onto `heating_system`,** and there is a control that fails if a
  later lane tidies it up. It is a fact about a **meter** — 50.3% of flats read as "not gas" when
  they are communal or unmetered — and `heating_system` is a fact about a boiler. They now disagree
  visibly, by about seven points, instead of being reconciled by whichever the code reached first.
- **The unrated 30.2% are dropped before raking on EPC**, inheriting the decision and the recorded
  residual `need_stock_joint` already made for this same joint rather than making a second one.
  "No EPC" is a fact about the register, and this world already models that correctly and separately
  as `epc_lodged=None`.
- **One control was demoted rather than kept as a catch.** I repaired a real seam in `rake` — the
  convergence grade was pointed at axes 0..n while the sweep ran on the selected ones — then found
  by mutation that restoring the defect **raises loudly** on the real call. So the repair was
  defensive, not a caught live defect, and the test now says so and asserts the property instead of
  the pairing. Claiming that catch would have been free and false.
- **A text control fired on its own explanation.** The test that pins "the chooser is not wired in"
  grepped the source and went red on the comment explaining why the chooser is absent. It reads the
  AST now. That is the third time this class has cost me a cycle.

## A cost this buys, accepted with its eyes open

**The world is no longer buildable from the repository alone.** `raked_joint()` needed only
published constants; the fitted joint is measured from DESNZ NEED, which lives in
`~/.cache/synthetic-enterprise/` and is deliberately not in the tree because it is survey microdata.
On a machine without that file, `year_premise_stock` can no longer draw a single home.

I found this by asking where `NEED_CSV` actually points, after writing the code that depends on it.

The refusal is named rather than a `FileNotFoundError` three frames down: it says which file, says
the file is outside the repo on purpose, and names the one-line override — **and warns that the
override changes the population**, because a quiet fallback to the published joint would give a
second world that no figure carries a marker for, and "which world produced this number" would be
unanswerable afterwards. That is the trade I took: a refusal costs one message; a silent fallback
costs the ability to interpret every figure produced under it.

If you would rather the world stayed self-contained, the reversal is one constant and I will take
that as a fidelity-versus-portability call that is yours, not mine.

## What remains, and it is the second half of the instruction

**The settlement budget is untouched.** It still refuses 409 of 500 wins by a systematic count-based
cull — unbiased by year, deterministic, and completely blind to what the homes are.

The measurement above says exactly where the chooser earns its keep: **1.64× at N=91**, and 91 is the
size of the settled book. Now that the dwellings carry measured attributes, that sample *can* be
chosen for difference and weighted, so the settled 91 aggregate up to the 500 the company actually
won. That is what would turn "the constraint we argue about" from a phrase into a question with a
number attached.

It is not in this landing because it moves every published financial figure and needs its own
pre-registration. It is the next thing I pick up, and it is now unblocked by this one — the attributes
it would choose over did not exist this morning.

---

## 2026-09-10 — the report mechanism was never silent, its channel was: 75 findings went into a 250,000-line log, and the demand vector measures a population the world does not draw from

<!-- head: 21e807e7f8b1 -->

**Written 2026-09-10 19:45 BST, three days late, on the director's instruction.** The gap this
entry closes is 253 commits over 68 hours — 3.6× the largest gap this log has ever had and 4× its
longest silence. The mechanism that was supposed to prevent it is repaired in the same landing, and
the repair is the first thing below because the reason it failed is not the reason it looked like it
failed.

---

## The mechanism did not stop. Its channel had no reader.

The director's reading was that the stretch-report check "silently stopped". It did not. It ran on
**65 publish cycles** between 2026-09-07 and 2026-09-10, returned rc 1 every time, and named the
commits every time. Every one of those findings went to `log()`, which appends to
`docs/observability/sim-runner-log.md` — **250,269 lines** of routine progress chatter.

> **Corrected beside the claim, before landing.** My first draft of that sentence — and the commit
> message under it — said **75, across those three days**. 75 is the count over the log's *whole
> life*: the mechanism shipped at 2026-09-06 08:52 UTC and ten of the seventy-five predate the
> window. A lifetime total quoted as a window total, in a paragraph whose entire subject is a figure
> read from the wrong place. It was caught by re-grepping with a date filter while the landing was
> already in flight; the landing was killed twenty seconds in and re-run with the right number,
> which is cheaper than either publishing it or revising it quietly afterwards.

A finding written where the routine output goes *is* routine output. That is a third shape, and it
is worth separating from the two this project already has names for: it is not *an unwired mechanism
has no red state* (this one had a red state and reached it 75 times), and it is not *a control keyed
to a structure that moved* (nothing moved). **The instrument was loud; the channel was silent.** The
grep that finds the first class — "does anything call it?" — returns yes here, which is why three
days passed.

**The repair.** The log line stays, because it carries the *listing* and the listing is what says
what a report is owed **about**. The finding additionally goes to `notify(kind="real_alarm")`, which
is the one channel here that both suppresses an unchanged condition and, on the third repetition,
escalates itself into a staged finding document the tick draws as work. Both properties are needed:
without suppression this pages every publish cycle for three days and earns exactly the reader the
run log had; without escalation it is one more thing nobody actions.

**Two calls inside that repair, and the reasoning.**

- *Keyed explicitly, not by `notify`'s auto-key.* The auto-key normalises numbers, elapsed times and
  hashes out of an alarm's identity — but not prose, and the check's message carries twelve rotating
  commit subjects. An auto-keyed page would have been a **new condition every cycle**: no
  suppression, no escalation, and 75 escalation documents standing for one condition. That is the
  shape that once put 28 documents behind 2 conditions, arrived at from the opposite direction. The
  key is the subject; the **state** is the newest entry's head stamp, so writing a report clears the
  alarm by construction rather than by anyone remembering to.
- *A threshold, measured against this log's own history rather than chosen.* Every gap is "owed"
  almost all the time, correctly, because a report is written when a piece of work **finishes**. The
  eleven stamped entries give ten gaps — 1, 2, 2, 5, 8, 9, 20, 29, 37, 70 commits — and a longest
  silence of 16.7h. So the two legs sit above everything the log has ever done (24h, 80 commits),
  neither would have fired on any historical stretch, and they are an **OR**: a machine that lands
  nothing for three days owes a report as much as one that lands three hundred commits in an
  afternoon.

## The second silence, found while diagnosing the first

`_git()` returned `""` for a **failed** git command and `""` for one that legitimately produced no
output, and nothing downstream could tell them apart. The head stamp names a commit. If that commit
is not reachable — written in a worktree whose landing never promoted, on a branch since rewritten,
in a fresh clone — `git log <stamp>..HEAD` exits 128, the old code read that as **zero commits**, and
`check()` printed **"up to date"**. Forever. With no report ever written.

Not hypothetical in this project: stretch entries are written in linked worktrees and reach the
shared tree only if `promote_worktree_landing` succeeds. One refusal and the control goes green for
good. Both this and the escalation seam now fail closed — a missing log, a missing stamp and an
unreachable stamp all escalate, because "I could not look" must never render as "nothing is owed".

R15 both ways, three source mutations run against copies: restoring the `""`-on-failure swallow puts
`check()` back to rc 0 / "up to date" (the shipped defect, reproduced); making `escalate` equal
`owed` pages on five commits and one hour; excising the `notify_fn(...)` call leaves the log line
firing and zero pages, which is precisely the state the director found. 26 tests pass on the pair.

---

## What actually landed, 7–10 September

**336 commits. Where they went, by area** (commits touching each, so a commit spanning two areas is
counted in both — these do not sum to 336):

| area | commits |
|---|---|
| `docs/` | 279 |
| `tests/` | 130 |
| `tools/` | 113 |
| `site/` | 91 |
| `background/` | 23 |
| `simulation/` | 7 |
| `company/` | **3** |
| `saas/` | **0** |

That table is the honest headline and it is not a flattering one. Three days of work put three
commits into the company and none into the SaaS layer.

**The three `company/` commits, which are the answer to "what can it do today that it could not on
Monday":**

1. **The renewal objective now pays for the departures it causes** (`e1895d6c8`,
   `company/pricing/value_based_renewal.py`). The arm was pricing renewals without any term for the
   churn its own price bought. It now carries one. The crisis year is the one it still cannot reach.
2. **The offer book has a measure that costs the customer nothing** (`097f9a6c9`). Before this the
   book could only ever spend the customer's money. The free-advice measure is refused below a health
   floor rather than offered to everyone — and it is refused hardest for exactly the households a
   priced model would target hardest, which is the finding worth keeping from that landing.
3. **The electricity SVT table stopped being a second home for the published cap** (`03c09fd61`) —
   one home for one number, and my own prediction about which way it would move was wrong.

**Seven `simulation/` commits**, all fidelity: hot water corrected and re-baselined (which exposed
that **cooking gas was zero for every household**); gas got an inside temperature, setpoint anchored
to EFUS and schedule driven by presence, breaking a collinearity; the world can now say **who paid
the bill** (the HMT receipt leg and the household-charged rate); both SVT legs read the commons; and
the people physical layer now stands alone — which surfaced that the world had **a third of the
one-person households GB has**.

Everything else — 279 docs commits, 113 tools commits, 130 test commits — is instrument. Much of it
is instrument that found real defects, and this stretch's own repair is another one. But three days
that move the company three commits is the shape the 2026-07-23 PRODUCT FIRST ruling was written
about, and it is stated here rather than left to be inferred from a commit graph.

---

## The three questions, answered with numbers

### Is the demand vector complete? No — and the split is not where it looks.

The canon's five deliverables (`W2_29`…`W2_33`) are all **minted and built**. Two are at their
target level (`W2_32`, `W2_33`, both level 2 → 2). Three are not: `W2_29` and `W2_28` sit at level 1
against a target of 3, and `W2_31` at 0 against 3. So on the map it reads two-fifths done.

**The measurement that matters more is which of it the running world consumes.** Grepped
module-by-module across `simulation/`, `company/`, `saas/` and `background/`:

| module | reached by the running world? |
|---|---|
| `tools/need_stock_joint` | **yes** — `simulation/fabric_physics`, `simulation/premise_population` |
| `tools/people_physical_layer` | **yes** — `simulation/dwelling_records` |
| `tools/demand_vector_coverage` | **no importer anywhere** |
| `tools/stock_joint_generator` | **no importer anywhere** |
| `tools/space_filling_sample` | **no importer anywhere** |
| `tools/demand_case_coverage` | **no importer anywhere** |
| `tools/billing_axis_coverage` | `background/daily_self_note` only — a reporting surface |

So the honest statement is neither "it is done" nor "it is fake". **The NEED-sourced fidelity inputs
are wired and drawing. The sample-and-coverage apparatus — the fitted joint, the space-filling
sample, the weighted cases — is a measurement instrument that no generator consumes.** It measures
a cloud of points it draws itself, and the world's households are drawn somewhere else entirely.

That distinction is exactly the class this project keeps paying for, and I had to grep for it rather
than read it, because nothing on the map or the page states it.

### How big is the book?

Two numbers, and they count different things, so their ratio is not a quantity:

- **582 accounts** — the commercial book at end-2025: founders plus every account the funnel won,
  settled or not. This is the supplier an Ofgem return would describe.
- **173 accounts** — the settled book: the subset our settlement engine could actually process.
  Every figure derived from the run's own settled records — treasury, margin, the collateral desk's
  MCR — describes **this** supplier.

The company won **500** accounts and the engine settled **91** of them: a uniform **18.3%** sample,
**409 wins refused by the settlement budget**. The shape of the growth curve is commercial; its
height is our machine.

There is a second ceiling underneath and it is also ours: `PROSPECTS_PER_YEAR = 400`. In four of ten
years (2020, 2021, 2024, 2025) the company could afford more quotes than there were prospects to
quote — 863 affordable against 400 available in 2024. Those years understate what this supplier
would have done, and the page says so.

### Do 3,000 generated households exist, or is it still 264?

**Neither number describes the world's population, and 264 never did.**

- The world draws **4,400 households** — `PROSPECTS_PER_YEAR = 400` × eleven years. That is the whole
  synthetic GB stock the company can address, and the book is a subset of it (`n_stock: 4400`,
  `n_book_domestic: 93` in the current subset verdict).
- **264** was a *book* figure from an older `run_phase2b`, still quoted in that module's prose. The
  book today is 582 / 173 as above.
- **3,000** is not a population at all. It is a `--points` value passed to
  `demand_vector_coverage.measurement()` in one measurement run — the module's own default is
  `POPULATION_POINTS = 120_000`. At `points=3,000, k=40` it chose **48 cases**, 44 carrying weight,
  and the biggest single case stands for **1,575,773 GB households** (5.8% of the counted
  27,291,846). Those weights reach `weighted_ks` and a JSON report. They reach no generator.

So the answer to "do 3,000 generated households exist" is: **no, and they were never going to** —
that number was a sample size on an instrument, not a target for the world.

---

## What the two disconnected sessions left, and what was done with it

`skynet-swirling-owl` and the worker-seat bring-up both went idle with about nine hours behind them.
Three things were checked and here is each:

**Worktrees.** Seven locked worktrees; two are genuinely live (`se-seat-executor`, running a claude
turn since 19:06, and `se-floorrun-20260910`, running `run_value_cycle_ab` on the nine seeds since
earlier today) and were not touched. The other five were dead — one lock said "~2h15m run, do not
remove until inactive" and was **seven days** old. **None of the five carried a single commit that
was not already on `main`**, so nothing was orphaned; their uncommitted content was verified,
parked, and the worktrees unlocked and removed.

The mechanism behind "worktrees not reaped" is worth naming: six of the seven locks say *"LIVE RUN
… do not remove until inactive"*, and **nothing anywhere checks whether it went inactive**. The lock
correctly protects a running job — I once deleted a landing worktree nine minutes into its gate — and
there is no door for the state after the job ends. `disk_headroom.reapable()` returns one row, and
none of these were in it. That is a wall with no door for a state it forbids, and it is filed rather
than fixed on sight.

**Uncommitted work.** `se-direction-battery` looked like the prize: 171 modified files. It is not.
160MB of those 178 dirty lines are machine state every worktree rewrites (`run_output_latest.json`,
`sim-runner-log.md`, the ledgers). The code slice is 39 files; of those, **19 are superseded rivals**
— `main` moved past `commit_refusal_attribution.py`, `promote_worktree_landing.py` and
`settlement_ceiling_probe.py` on 8–9 September, after that worktree's 5 September head — and
`background/standing_red.py`, its most substantial-looking untracked module, was **adjudicated and
deleted from the shared tree at 18:29 today** as a draft its own successor dissolved. The remaining
18 are docstring prose in a tree whose declared purpose was a mutation battery, i.e. a tree
deliberately in a modified state. **Nothing there was finished work.** It is parked at
`/var/tmp/se-parked-20260910/` (341K code diff plus the seven untracked files) and the worktree is
gone.

**Claims.** None held. `seat_work_in_hand.held()` and `stale_claims()` are both empty; the only live
claim is the delivery lane's, taken by the running seat executor at 19:06. The 100-minute sweep had
already reclaimed whatever those sessions took, so there was nothing to release.

**The fast-forward refusal has a different cause than the sessions.** `origin/main` is 17 ahead and
`main` is 10 ahead — an ordinary two-lane fork, and the 17 are the seat executor's own promoted work.
What holds it open is that the **shared tree's working directory is never clean**: the repaired
reconciler now names seven real blockers, and four of them (`.launch_records.json`,
`capabilities_door.json`, `value_arms.json`, `orphan_baseline.json`) are tracked paths that daemons
rewrite every cycle. A merge that requires a clean tree can never run in a tree that is written
continuously.

**And underneath that, the thing I did not expect to find.** The shared tree carries **~4,100
uncommitted insertions across 57 source files**, plus **11 untracked new modules with their tests**
(`tools/inside_the_renewal_rule.py`, `tools/renewal_rule_price_response.py`,
`tools/book_shape_spread.py`, `tools/build_weather_world.py`, `tools/pull_book_weather.py`,
`tools/explain_premise_year.py`, `sim/weather_world.py` and four test modules). The oldest is dated
**30 August**; the newest is 20 hours old. That is an eleven-day backlog of work that was written in
the shared tree and never landed — far larger than the 915 orphaned lines this class was named for,
and it is upstream of both the fast-forward refusal and the commit latency, because the gates read
the whole tree.

I did **not** sweep it. Landing 4,100 lines across 57 files in one commit would violate the pathspec
discipline that exists precisely to stop that, eleven of those modules need REUSE blocks nobody has
written, and some of that residue is deliberately held — `e4aa02359` took the head-red pair out of
the index and left it on disk on purpose, and a tidy-up would have destroyed what that commit meant
to keep. It is filed as a finding with its per-file census and dates, so it is drawable work with a
subject rather than a mess.

---

## Calls made, and where I stopped

- **The repair is a finding, not a gate** — unchanged from the original framing and re-affirmed by
  the director in the same breath ("a finding that fires rather than a silence"). Refusing commits
  until a report is written would stop the work the report describes.
- **The threshold was measured before it was set**, against this log's own ten historical gaps,
  rather than picked to fit today's number. Had I picked one, 100 commits would have been the
  obvious choice and it would have sat *below* nothing and *above* one real gap of 70 — a constant
  chosen because a constant was needed.
- **I did not adopt the 57 files.** Scaling that down is not mine to do quietly; filing it with the
  census is.
- **I did not touch the two live worktrees**, and the liveness check earned its place: the first pass
  reported five processes with their cwd inside `se-direction-battery`, and all five were **my own
  shell**, which had drifted into the worktree three commands earlier. A pid check that counts your
  own hand is how a landing worktree gets deleted nine minutes into its gate.
- **I did not fix the worktree-lock-with-no-door**, or the two untracked observability artefacts
  (`book_growth_campaign.json`, `book_subset_verdict.json`) that every world run writes into every
  worktree — neither tracked nor ignored, so they read as uncommitted work in perpetuity. Both are
  filed. Both are one line to fix and neither is this stretch's subject.

## Where it stands

The stretch-log repair is landed and armed. The next page it sends will be the first one that
reaches a person. The company question is open and unflattering: three commits in three days, an
instrument layer that is measuring a population the world does not draw from, and a book whose
height is set by our own settlement engine rather than by anything commercial.

---

## 2026-09-07 — the number lands near 3,000, and three of the criteria that produced earlier ones were broken

<!-- head: 39a410f0d46c -->

A five-piece run, and the thread through it is that three of the numbers I published were produced
by broken criteria that all failed in the flattering direction.

THE NUMBER, AND THE PREDICTION IT TESTED

The director wrote a falsifier into the canon and asked me to honour it: *if payment method lands and
moves the figure by a tenth rather than threefold, the strata mechanism is wrong.*

    before payment method   2 strata (fuel)         6 axes    N =   102
    after payment + shape   4 strata (fuel x pay)   7 axes    N = ~3,000    (tolerance 0.10)

**It moved by about thirty.** The mechanism is confirmed — strata multiply, correlated axes do not —
and the arithmetic I used to get there is still wrong. I said *k* strata multiply by about *k*, which
predicts 2x. The measured factor is 30, because coverage is owed *within* each stratum on every axis
and the binding cost is the smallest cell of the cross (electrically heated, not direct debit, 5.7%
of the book), not the number of cells.

So I got the right magnitude — the pre-registration said "roughly 3,000 households… low thousands" —
from reasoning that does not support it. Worth saying rather than banking the hit.

EVERY AXIS OF THE CANON'S VECTOR IS NOW IN. `blind_to` is empty for the first time: annual gas,
annual electricity, seasonal swing, weather sensitivity, half-hourly shape, and both intervention
ceilings, stratified by fuel x payment method. What remains uncounted sits outside the demand vector
entirely, and each item now carries its reason.

THREE BROKEN CRITERIA, AND THEY ALL FAILED FLATTERINGLY

**A criterion whose bar loosened as the sample shrank.** Acceptance was "under the two-sample
critical value", which grows as n falls, so a 13-case sample passed trivially. It returned the two
smallest sizes on the ladder, which is the only answer that criterion can give.

**A random sample dressed as a weighted design.** The module quoted the canon's "each drawn case
carries the population mass it stands for" in its docstring and ran `rng.choice`. No weight entered
the test at all. 8,500 was an honest answer to a question nobody asked, and the director's own tell
caught it.

**Weights fitted globally and scored per stratum.** One weight vector solved to reproduce the
population, then each stratum's sub-sample scored against *that stratum's* distribution — a
sub-sample asked to match a distribution its weights were never fitted to. It returned "no size
accepts" at every tolerance, which reads as a gigantic requirement and was a broken test.

The pattern is the lesson: **a criterion that fails by demanding MORE cases is dangerous precisely
because more-is-conservative reads as caution.** Two of these three produced plausible large numbers
and neither looked like a bug.

AND I PUBLISHED A CONVERGENCE CLAIM THAT THE NEXT DATA POINT REFUTED

On two points — 2,716 at 12,000 reference households and 3,824 at 40,000 — I wrote that N grows with
the reference population and has not converged, and filed that as the honest headline. The third
point is 2,748 at 120,000. **It does not rise.** Two points looked like a slope because two points
always do. Corrected in place, and the document renamed to match what it now says.

WHAT ELSE LANDED

**A filer for director documents.** Four canons in two days arrived without the severity header and
51 without a Knowledge declaration; each silently blocked a level raise in every lane until a seat
attempted a merge. I transcribed it four times and said twice I would build the tool instead. Now
severity is *read* from the document's own Type block and refused if absent, lane is derived where
the subject says so and refused where it does not, and the Knowledge topic is never invented.

**Occupancy conditioned on the address**, with the fallback visible rather than silent. It buys 9%
of household-size variance, which is the finding rather than the caveat: occupancy is something this
company must meter, not look up.

**A knowledge page written and not landed.** The site lane is red at HEAD on another lane's
uncommitted change — a working-tree edit that deletes sixteen controls from the failing file. Making
the lane green by removing the red controls is not a call to make inside someone else's commit, so
the page waits and the wedge is filed with its cause. I checked origin again at the end of the run
rather than assuming it had cleared. It has not.

WHAT I GOT WRONG IN THE MECHANICS

A per-stratum reference rebuilt at every ladder step — the same pre-project-once defect this module
had already fixed one level up, committed again one level down. It ran twenty-five minutes without
finishing; hoisted, the same ladder takes thirty-eight seconds.

A plausibility rule that called observed dwellings impossible. "Cavity insulation in a pre-1930
home" looked physically obvious and the evidence produced it at 1.3%, because the band is *before
1930* and cavity construction is general through the 1920s. A rule that contradicts the data is a
wrong rule, not wrong data.

THE HABIT THIS RUN ARGUES FOR

Every one of the three broken criteria would have survived review, because each produced a number of
plausible size with a defensible story. What caught them was not inspection but **comparison** — the
random comparator beside the designed one, the held-out directions beside the fitted ones, the third
reference size beside the first two. A single number with a good story is the thing to distrust; the
cheapest defence is to compute the same quantity a second way and look at the two together.

---

## 2026-09-07 — a writer that exists while nothing checks it wrote

<!-- head: 219c26366d63 -->

Twenty-nine commits, and the thread is one sentence the director wrote twice: a writer that exists
while nothing checks it wrote.

THE CONSOLE CAPTURE HAD BEEN DEAD FOR SIX DAYS AND THE CAUSE WAS A HARDCODED PATH. The harness names
a transcript folder by slugging the session's working directory. On 3 September the seat moved under
systemd, its launch directory became the project, and every transcript landed in a differently-named
folder. The module had the old slug baked in. It kept reading a folder that still existed, still held
sixteen real transcripts, and never received another one.

WHAT MADE IT INVISIBLE IS THE PART WORTH KEEPING. The module was built to fail closed and its guard
was aimed one state to the left: it refuses when there is NO transcript. What happened was a folder
that had gone COLD, which to every reader is indistinguishable from a director who said nothing.
Blindness was guarded; staleness was not. And `observe()`, whose own comment says it runs in the
worker loop, has zero callers — so even the guard that existed was never invoked.

THE NAIVE FIX WAS WORSE THAN THE GAP AND I SHIPPED IT BEFORE I CAUGHT IT. Pointing the scanner at the
live folder swept daemon-injected turns into the record: 67% of one day's captured "director turns"
and 84% of the next were "You are the autonomous worker, woken by a scheduled tick" — the machine's
words quoted as his, in a file the release door reads as his authority. The tell was size: 485 KB,
992 KB and 1.56 MB against 22–54 KB for a real day. There is no structural discriminator to fall back
on; an interactive seat, a worker tick and a delivery-seat dispatch all write `userType: "external"`
with identical cwd and version. So the capture moved to the prompt-submit hook, where the answer is
simply known, and the scan became a backstop.

THEN THE PUSH CAUGHT A LIVE CREDENTIAL THE CAPTURE HAD SWEPT IN. A Cloudflare API token, pasted into
the pane weeks ago, recorded verbatim, carried by the backfill into a file bound for a remote. Push
protection stopped it and I did not bypass it. A verbatim capture of a human's typing will eventually
contain a secret — that is a property of the channel, not an accident — so redaction now runs inside
both writers before anything reaches disk.

AND MY FIRST REDACTION WAS ITSELF WORSE THAN THE PROBLEM. 33 files, 16 to 38 spans each: it was eating
UUIDs, which are the transcript filenames in every `Source:` line, so it destroyed the only pointer
from a record back to what produced it. Corrected with three exclusions — a 40-char hex string is a
git sha, a UUID is a filename, an underscore-separated identifier is a module path — it is 4 files and
17 spans.

THE SAME DEFECT APPEARED THREE MORE TIMES IN ONE DAY, EACH INSIDE THE FIX FOR THE LAST.

The new staleness control globbed the staging root and `done/` and never `console/`, the room its own
writer writes to, and reported a four-day lapse over records sitting on disk.

The backstop deleted evidence: `write()` reads a three-day transcript window, so re-running it
regenerates an older day from nothing. It cut 3 September from 22,907 bytes to 10,592 while being
repaired for losing six days, and I had not backed the file up.

The register repair had to be computed against the COMMITTED tree, not the working one. The tool
called a module "now wired" — true in the shared tree where an untracked file imports it, false in
the tree the commit creates, where deleting its ruling made it undispositioned. Same file, two trees,
opposite correct answers.

WHAT I STOPPED SHORT OF, DELIBERATELY. Six days exist in both `console/` and `done/`; the duplication
predates this and deciding which room owns an archived record is separate work. Two reds in the
capability index are another lane's — modules landed without index rows — and fixing them would mean
writing rows for code I did not build. Two half-staged archives belong to the lanes that made them:
one carries a disposition concluding CLOSED and the other is a bare move with no reason, and
completing either to clear my own path would bank a fail-open.

THE MEASUREMENT WORK, WHICH IS THE ACTUAL JOB. W2_22 landed: 233 houses for 99% of household-weighted
variance across five output axes, against 55 for the optimal partition — so drawing for difference
costs 4.2x the houses, knowingly. Four of five tails close at 610 and the fifth does not close at any
affordable size; it is a stratification problem, not a size one, and the page says 30% rather than
reporting N as complete. The director's own input-versus-output premise, measured on Britain rather
than assumed, came out half right: variance covered is identical to four decimal places between the
two draws, and what the input draw loses is the fill radius, three of 23 corners, and 40% of the level
tail. Right about why it matters, wrong that it shows in the aggregate.

AND THE COVERAGE NUMBERS WERE MEASURING THE WRONG THING, WHICH HE CAUGHT. Thirteen cases for 99% of
demand was measured on a scalar — annual kWh — when the thing being served is a vector. My own finding
had named the mechanism ("demand is a scalar") and filed it as an interesting property rather than as
a defect in the subject. The same collapse was on the input side too: three separable weather grids
against a response my own sensitivity table shows is fabric-dependent. One defect, twice, flattering
in the same direction both times.

THE HABIT THAT WOULD HAVE SAVED MOST OF THIS. Every failure above is a mechanism that existed and was
never checked to have run: a capture with no caller, a guard aimed at the wrong state, a stretch entry
appended and never landed, a reply hook writing into the wrong record. The question is not "does the
writer exist" but "what did it write, and when did anyone last look". The director asked it about the
reply hook within an hour of it landing, and the answer was that it fired and was writing other
sessions' words into his record.

---

## 2026-09-07 — four correct answers to questions nobody asked

<!-- head: e4bedd260172 -->

Sixty-nine commits, and the thread running through the ones that mattered is the same one: a figure
that was correct as an answer to a question nobody had asked.

WHAT WAS CORRECTED, IN ORDER, AND WHY EACH ONE WAS FOUND THE SAME WAY

The wind term. W1_19 published a per-cell wind map and reasoned about its granularity. The director
asked what wind is FOR, and the honest answer required looking at whether the world had a wind term
at all. It did not: `fabric_physics` clamped infiltration at a constant, so the SAP wind factor --
the only route by which wind reaches a household -- was missing. The map was granular about a
quantity the simulation ignored. I had predicted the sensitivity would be small and it was wrong
three ways, which is filed beside the measurement rather than revised.

The household placement. Three successive methods, each an improvement and each still anchored on a
postcode centroid. The director's "why not place dwellings directly?" was right and the version he
was questioning was a better approximation of the same approximation: 20,959 cells holding addresses
were unreachable from any postcode's 3x3 window, and 94.5% of addresses sat in cells claimed by five
or more output areas each sizing its share from all of them. ONSUD removed the centroid entirely --
70 seconds to build, half a second to place. The answer barely moved, which is the reassuring
outcome and not a reason it was not worth doing: the point is that the error is now bounded rather
than asserted.

The tilt table. `premise_population` said in its own docstring that its magnitudes were not anchored
and only their direction was. NEED had the cross-tab all along. One direction was wrong -- detached
homes are 1.21x MORE likely to be A/B, not less, because detached is bimodal. The table's single
claim was the thing it got wrong.

The cell counts. And this is the one that reframes the rest. 21, 21 and 5 cells for 99% coverage of
the three weather drivers is a correct partition of Britain's weather and it is not what sizes a
sample. Coverage of DEMAND is, and demand is house and weather together. 13 cases -- against 273 if
the two composed separably -- and the reason is not the correlation either of us expected but that
demand is a SCALAR.

WHAT I STOPPED SHORT OF, DELIBERATELY

Scotland is out of both the stock joint and the demand-case measurement. NEED is a DESNZ product
with no Scottish dwellings, and using the England-and-Wales mixture for the coldest 8% of the book
would be an assumption in the worst possible place. It is named on the page rather than absorbed.

The three-way interaction is in NEED and unused. The EPC-to-fabric map is a declared Choice whose
cost is not priced. Both are residuals I could have quietly closed and did not.

WHAT I GOT WRONG IN THE MECHANICS, BECAUSE IT KEEPS HAPPENING

The population map was published three times before it was right -- a binary flag reading 81%
against a 49.6% caption, then a proportion that saturated, then a 5 km picture carrying a 1 km
claim. All three were caught by LOOKING at the picture, none by more thinking about it. That is the
same lesson as printing the table at real inputs before shipping a formula, and I keep having to
relearn it in whatever medium the output happens to be in.

A mutation battery reported four false KILLs because its own runner had an unrecognised pytest flag
and exited 4 for every cell, mutated or not. The fix is a baseline through the identical command,
and the reason it matters is that "killed" and "the harness is broken" are indistinguishable from
the outside.

A `--content` land reverted another lane's map work, because my content was built from a HEAD that
had moved and the gate passed -- the reverted side was internally consistent. Six store files to
repair. After a `--content` land, diff against the commit you raced.

THE HABIT THAT WOULD HAVE SAVED ALL OF IT

Every one of these was found by asking what a number is an answer TO, rather than whether it is
right. The wind map was right about wind. The placement was right about postcodes. The tilt table
was right about magnitudes it never claimed. The cell counts were right about weather. Correct
answers to unasked questions do not announce themselves, and none of the four would have been caught
by checking the arithmetic.

---

## 2026-09-06 — The cell answer became a build decision, the world got the wind term it never had, and the site got its first map

<!-- head: 1ed1e7737af4 -->

**What this stretch was about.** Three instructions in sequence: state the cell answer as a build
decision rather than a curve; check whether solar gain is the same gap as the wind term (rather than
assume it); then fix the wind term, fix PV, and put the cells on the site.

**The decision.** Twenty-one cells each for temperature and wind, five for irradiance, one national
for wholesale price. Three grids, not one. `W1_21`'s 987 stands as arithmetic and falls as a
recommendation — it correctly answers "how many cells resolve all three drivers *jointly*", which is
a question nothing here asks.

**Solar gain was not the same gap, and it was checked by running the model.** The wind term was
*named* in `fabric_physics`'s own docstring as an available archive field and consumed by nothing, so
a check that greps for a word would have reported both drivers present. Zeroing the glazing aperture
and re-running the 2R2C integration takes half-year heating fuel from 7,274 to 9,138 kWh: **solar
gain offsets 20.4% of heating fuel**, larger than the wind effect, and it is wired.

And the two drivers turn out to be complementary across the stock, which no single median would have
shown. Over the same household spread, solar gain moves fuel by −1.2% in a leaky pre-1919 house and
−7.9% in a tight post-2000 one; wind moves the heat loss coefficient by +18.6% mid-stock and only
+2.9% in that same modern house, because the Part F minimum air change rate clamps the calm end. **A
targeting model using one as a proxy for the other would be wrong at both ends.**

**The world now has a wind term** — SAP 10.2/BREDEM's `raw ACH × wind/4`, with `wind_speed_mean_ms`
made a *required* field of `DailyWeather`. The column had been the sixth in every archive CSV since
the fetch, sitting next to `cloud_cover_pct` in the reader, skipped. At 4 m/s the new model is the
identity and the 60-test fabric suite passes unchanged, which is what makes it an extension rather
than a re-calibration.

**Three of the four predictions I filed before measuring were wrong**, and one cause explains three
of them. Heating-season wind is above the annual mean at every site, and I sized the prediction on
annual means. The Part F floor makes the effect one-sided — a calm day cannot ventilate below the
minimum. And the archive's own winter temp/wind correlation is +0.47 to +0.54, which means **cold
days are calm** — I had written that the two "coincide, so the cold tail widens", which inverts it.
So the wind term matters most in *mild windy* weather: the largest single-day effect in the 2023
replay is 8.3 °C at 9.9 m/s, +45.8%. Peak demand barely moves; the shoulder rises; daily variance
*fell* at three of four sites. For sizing a peak-demand hedge that is the opposite of the intuitive
answer.

**PV: a latitude lookup does not work, and that is the finding.** The five sunshine bands overlap
across four degrees of latitude — the Norfolk coast at 52–53 °N sits in the sunniest band and inland
Devon at 50.6 °N in the dullest, because Britain's sunshine is coastal and eastern as much as
southern. So the lookup keys on annual sunshine duration, which the Met Office publishes on a grid
and a supplier can read for any postcode. The company's single national 850 kWh/kWp becomes five
bands anchored to the MCS 2025 fleet average; the RMS error in annual generation falls from 3.4% to
0.95%. **Nothing pinned the old constant** — all 21 existing tests passed with it moved 3.8%.

**And the obvious sanity check does not hold**, which was worth more than one that did. The published
750–1,050 kWh/kWp range is quoted for optimally tilted south-facing installations at the extremes;
the fleet average is over all orientations. Two populations. The derived 835–947 spread being
narrower says nothing about either, and reading it as corroboration *or* refutation would both be
wrong. It is stated in the source because it is the first comparison anyone will reach for.

**The site now carries a map.** Two, and a coverage curve, all inline SVG composed by the page's own
JavaScript from a published feed. The class map shows scattered same-colour patches and the page
says why; the control *measures* the scattering rather than trusting the sentence.

**The third picture was wrong and I found it by looking at it.** The first population map shaded each
5 km block by whether *any* of its twenty-five kilometres held a household — which reads **81%
occupied against the 49.6% printed beside it**, because one populated square colours the whole block.
A chart contradicting its own caption is worse than no chart, and the suite was green. Rebuilt as an
occupancy density, with a control that holds the picture to the figure.

I also printed the land mask as ASCII and looked at it. It is unmistakably Great Britain — Orkney and
Shetland as dots, the Central Belt narrowing, the South West peninsula, East Anglia bulging right. A
grid-origin error would have produced a plausible blob 200 km from anywhere, and no test would have
noticed.

**What cost time, and it is all one shape.** A `--content` land silently reverted another lane's map
work: `surgical_land` re-gated against a HEAD that had moved, my content was built from the older
base, and `--content` overwrites a whole file. The gate passed because the reverted side was
*internally consistent* — removing a `notes_rehomed` declaration while its store file is untracked is
exactly as coherent as adding both. The repair needed six store files, three untracked and three
modified, found by running the design suite rather than by reading the diff. **After a `--content`
land the check is "diff against the commit I raced", not "did the gate pass".**

Two orderings that are not the same and neither is guessable from the other: `W1_25`'s level could
not be *recorded* until the map was *landed* (the ledger resolves an atom's lane from the live map),
while `W1_26`'s could not be *landed* until it was *recorded* (the level gate wants the entry at
commit time). Land, reconcile, record — in that order.

The orphan ratchet refused the site page twice. First I lowered the floor by four modules when only
three were wired. Then the generator itself was an orphan — and the *local* check said the floor was
clean while the gate refused it, because `orphan_ratchet.compute()` reads `git ls-files` and the new
module was untracked. **A local run of that ratchet cannot see the file it is about to be refused
for.**

And one commit landed nothing at all because `/tmp` was 91% full: the message file was written, lost,
and `surgical_land` was invoked with an empty `-m`. Freed 5.5 GB of stale HEAD extracts. A full
`/tmp` does not announce itself; it eats writes.

**Where it stands.** `W1_25`, `W1_26`, `W1_27`, `W1_28` closed. What remains of `W1_14` is the
knowledge page's own topic entry in the knowledge layer proper, and the open questions are named:
whether one grid of ~30 could serve both heat-load drivers, SAP's shelter factor, orientation on
both the gain and the yield side, and cloud used where irradiance is meant.

---

## 2026-09-06 — The director challenged the cell framing: wind turns out to be the smoothest driver and the largest unmodelled one

<!-- head: f58753811f9b -->

**What this stretch was about.** The director challenged `W1_21`'s framing rather than its arithmetic:
one cell grid was being asked to serve three different jobs, and he put a specific hypothesis to it —
that wind is genuinely fine-grained but reaches a household only through wind chill on heat loss,
which is second-order, so wind may need no household resolution at all and the 987 is an artefact.

**His diagnosis was right and his mechanism was wrong**, and the difference is what decides the build.

**Wind is the smoothest of the three drivers where people live.** Asked one at a time,
household-weighted, all three want about the same number of cells — 21 gets winter temperature to
99.3%, wind to 99.4%, sunshine to 99.4%. Wind's fine structure comes from terrain, coast and
exposure, and `W1_20` had already established that half of GB's land cells hold nobody: the ridges
and headlands that make a wind map look nuanced are the empty half.

So the 987 is not a wind artefact. It is the price of one partition resolving three drivers
*simultaneously* — dimensionality, not roughness. Which is his diagnosis, arrived at from the
opposite direction.

**But wind is not second-order in the bill.** The mechanism is published and it is linear: SAP 10.2
and BREDEM adjust infiltration as `raw ACH × shelter × (wind ÷ 4 m/s)`, straight into ventilation
loss. Measured over this project's own stock — 288 era × type × insulation × size combinations —
ventilation is 15–51% of the heat loss coefficient, and moving across the household wind spread
changes it by +2.7% to +29.7%, median **+14.9%**. The comparator, over the same percentile span of
the same population: winter temperature changes degree days by **−18.9%**. Wind is 0.79× temperature,
not a rounding error.

**Importance and resolution are separate questions, and conflating them produced both the 987 and
the challenge to it.** Wind matters as much as temperature *and* needs no more cells than
temperature. Neither of those implies the other, and I had been reading the joint curve as though it
did.

**The finding underneath, and it is the one worth keeping.** `simulation/fabric_physics.py` computes
infiltration from build era and insulation and nothing else — there is no wind factor anywhere in the
SIM's demand path, and `wind_speed_mean_ms` sits in that module's own docstring as an archive field
consumed by nothing. Meanwhile `company/pricing/weather_normalisation_belief.py` carries an optional
`HDD × excess wind` regressor a caller can switch on. **The company can fit a household wind-chill
coefficient against a world in which household wind chill does not exist**, and the fit will look
entirely healthy: real regressor, real data, reported r². That is a coupled-triad defect — a belief
carrying a term its truth does not have — and it is invisible to the triad gate because the regressor
is off by default. Minted as `W1_26` rather than patched: the repair is one multiplication, but it
moves every historical demand figure in the tree, which is a fidelity decision with its own evidence
bar.

**PV needs three to five cells against the one the company has.** `seg_export_estimator` applies 850
kWh/kWp to every household. Sunshine duration converts to irradiation by Ångström–Prescott, and
because the intercept is positive the relative spread in irradiation is *strictly* smaller than in
duration — elasticity 0.41, and 0.43–0.49 across the published coefficient range, so the conclusion
does not turn on the choice. One national figure carries 3.4% RMS error in annual generation; three
cells gets it to 1.5%, five to under 1%.

**What went wrong.** `_sim_has_a_wind_term` asked `"wind" in name.lower()` and returned **True** — on
`window_area`, `_WINDOW_U_BY_ERA`, `_WINDOW_AREA_RATIO`. It would have published "the SIM models
wind" on the strength of the glazing, in the one place where the entire finding is that it does not.
Caught by printing the number, not by a test; the test exists now and asserts both directions of the
segment match.

And `per_driver_curve` had no control at all until a mutation asked for one. A version that quietly
clustered on the full matrix returns three copies of the joint curve — three identical, plausible,
monotone curves — and the headline inverts with nothing to show for it. Its fixture is the eight
corners of a cube with three *different* native spreads, because with equal spreads a residual scored
against the wrong driver index is indistinguishable from one scored against the right one.

**One ordering lesson.** A `--content` land never touches the working tree, and
`record_level_up_self_certified` resolves an atom's lane from the *live* map file. So a level move
recorded straight after a content land is refused with `<lane-unknown>` — an atom that exists at
HEAD, is published, and is invisible to the ledger. The refusal was right and its message read like a
governance block on a blocked lane. The order is: land, reconcile the tree, then record.

**Where it stands.** `W1_21`'s 987 stands as arithmetic and falls as a recommendation. Heat load
wants ~21 cells on temperature *and* wind; PV wants 3–5 on sunshine; wholesale price wants one,
national, and is already wired that way. `W1_26` is next.

---

## 2026-09-06 — Closing the four weather atoms, and the two gate refusals the close ran into on the way

<!-- head: 7668df76190c -->

**A short addendum to the entry below**, covering the bookkeeping that finished it: `W1_19` through
`W1_22` are now at target in the closed half of the map, with their evidence and — more usefully —
what each does *not* cover recorded in the row itself, and all four ratified in
`gate_authorizations.jsonl` as self-certified with their provenance.

**Two gate refusals during that close are worth keeping.**

The first: the map content was assembled from a HEAD that moved under it. Another lane landed
`notes_rehomed` declarations for two atoms between the assembly and the land, and `--content`
overwrites a whole file, so the stale assembly would have reverted their declaration while looking
like a clean map edit. It was refused as a store/declaration mismatch. That refusal is the only
reason it was visible as anything other than a silent revert — the second time this exact shape has
been caught this week, and both times by a gate rather than by looking.

The second was better. `W1_21`'s `file_scope` named `tools/generate_weather_cells_data.py`, which has
never been written, and the scope-evidence gate refused the level: *a level is a claim about
evidence, and a path that does not exist is not evidence*. The fix was to re-point rather than to
build — the generator is the site lane, it is already in `W1_14`'s own scope, and the duplication was
in how the atom was minted rather than in the work. Worth noting that the atom would have closed
green on its tests alone; what caught it was a gate asking whether the row's own claim about where
its work lives was true.

**One observation about this log's own check, filed rather than fixed.** A commit that *closes*
already-reported work will always trip the "work landed without a report" finding, because the check
counts commits and cannot know that this one is bookkeeping for the entry above it. That is a false
positive by construction. It is not worth a mechanism — the finding is cheap, it is a finding rather
than a gate, and an exclusion rule would be one more thing to get wrong. Recorded so the next reader
does not spend the same thought on it.

---

## 2026-09-06 — Four bounded successors on the weather cells, and the answer to how much granularity Britain needs turns out to depend entirely on whether wind matters

<!-- head: 2af241e0c94d -->

**What this stretch was about.** Taking the four bounded successors that had just been minted for the
weather cells and running them to the end: the drivers per cell, the household weights, the coverage
curve that answers the director's actual question, and the persistence and synchrony a hedge would be
priced off. All four landed. Stage 1.

**The headline, in one table.** How much granularity Britain needs to capture the variation in
household heat-load drivers:

| target | cells | winter-temperature error |
|---|---:|---:|
| 90% | 34 | 0.22 °C |
| 95% | 89 | 0.15 °C |
| 99% | 987 | 0.06 °C |

The last four points cost eleven times the cells the first ninety did. There is no natural cell
count, only a price list — which is why the ruling insisted the answer be a curve.

**And the line under it that matters more.** Those counts come from weighting the three drivers
equally, which says a one-sigma move in sunshine matters as much to a heat bill as one in winter
temperature. That is almost certainly false. The module's docstring called equal weighting
*conservative* — an upper bound — and rather than leave that as a reassurance it was tested:
temperature-dominant weighting needs 13/34/377, and temperature alone needs **5/8/21**. The claim
holds at every target and in the right direction.

**So: twenty-one cells capture 99.3% of the household-weighted variation in winter temperature.**
Five capture 91%. If heat load is as temperature-dominated as the physics suggests, Britain needs
about twenty weather cells and not a thousand. What forces the count into the hundreds is insisting
that wind and sunshine be resolved to the same relative precision, and nothing yet establishes that
they should be. That is now a decidable question for `W2_21`'s fitted model rather than an argued one.

**Half of Britain's land has nobody on it.** 121,668 of 245,077 land cells hold a household. Weighting
for that halves the spread on every driver, and cuts the cells needed by about 40% at every target.
The weights came from the censuses via postcode, as the ruling requires: 1.67 million live residential
postcodes, TS041 for England and Wales, Scotland's Census 2022 UV402. 27,283,137 households placed
against a published total of 27.29 million.

**One published figure turned out to have three values, and all three are right.** `W1_19` had reported
winter temperature and wind correlating at −0.430 across land cells, refuting the ruling's prediction
of a positive relationship, while noting the repo's own temporal measurement of +0.507. Household-weight
the same cells and it is **+0.060** — among the places people actually live, the spatial relationship is
absent. The negative figure was a fact about empty uplands. So "REFUTED as written" was too strong for
the reading that matters, and the qualification was written back beside the original claim rather than
only in the new document.

**Cold snaps arrive in blocks, and Britain has no second weather.** Against a null that permutes the
same cold days within the same cell and winter — count held fixed, so only clustering varies — 51.3%
of all cold-decile days fall inside spells of five days or more, against 0.45% under independence.
Spells of seven days or more are a thousand times more likely than chance. And on 7 February 1991,
100% of the household book was in its own coldest decile on the same day; on one winter day in ten,
more than half of it was. The least synchronised pair of cells in Britain still scores 2.81 against
an independence baseline of 1.0.

That means `W1_21`'s cells are the right resolution for *level* and buy almost nothing in *risk*.
Both statements are needed. Publishing the first alone would imply the second, and any model treating
cells as partly independent understates the tail in the flattering direction.

**What went wrong, and it is the same defect twice.**

The `sys.path` script-versus-module defect shipped again, in `weather_cell_weights --weighted`. Run as
a script, `sys.path[0]` is `tools/` and not the repo root, so `from tools import ...` raises. Pytest
fixes the path before any test can import the module, so the whole suite stays green while the command
line is dead. It was caught by *running the command*, not by any test. Fifth instance in this
repository; three more modules written this stretch all carry the guard and a control now.

The nomis API caps an unpaged request at 25,000 rows and says so nowhere in the payload. The first
household pull returned a well-formed CSV with correct headers and real counts for 25,000 of England
and Wales's 188,880 output areas — 13% of the country — and every figure downstream would have been
computed and published without an error anywhere. Caught by checking the row count against the known
total, which is now the pull's own refusal.

And the mutation harness lied. Four mutations came back KILLED because the pytest invocation carried
an unrecognised `--timeout` flag and exited 4 every time, mutation or not. A harness that reports
success for a reason unrelated to the thing being tested is the same shape as the controls it exists
to check. Re-run without the flag, three died and one survived — and the survivor was the honest
answer: the three-variable land-mask intersection is an equivalence on this data release, recorded as
one rather than deleted, so it starts binding the day the masks diverge.

**One survivor was a missing test, not an equivalence, and it named the worst possible line.** Every
test of the coverage curve injected a synthetic driver space, which meant `_space()` — the only path
production takes — was never exercised. Replacing its household weighting with a bare `ones()` left
the entire suite green while every published figure silently became a statement about land: precisely
the defect the atom exists to prevent, surviving in the module that publishes the answer. Repairing it
surfaced a second untested line immediately.

**What was stopped short of.** The industry comparators are read at their *counts* (13 LDZs, 14 GSP
groups, 21 SAP regions → 82.3%, 83.1%, 87.0%) rather than from their actual boundaries, which are not
in this tree. That gives upper bounds, which is enough to make the argument — the settlement geography
the company receives its data on resolves at most 82–87% of the weather its customers experience — and
not enough to publish a per-boundary figure. Registered rather than fudged. Elevation correction to
house height is likewise registered as the open half of the weights atom, not implied by its absence.

**Where it stands.** The four successors are closed. What remains of `W1_14` is the knowledge page and
the site lane — `generate_weather_cells_data.py`, which is also the condition on which the three
frozen orphan modules unfreeze.

---

## 2026-09-06 — The weather pull sat undrawn for eighteen hours because the atom was a programme, and the first measurement refutes a ruling prediction by a sign

<!-- head: 5f5b8d74ebb8 -->

**What this stretch was about.** The HadUK-Grid weather pull finished on Saturday evening — 318
files, 19.8 GB, zero failures — and for eighteen hours nothing was drawn from it. The cause was the
same one that had already cost two other stretches: `W1_14` is a ruling-sized atom, "derive the
weather cells", and a bounded tick reading that has no first move, so it takes the machinery in
front of it instead.

**The fix, third time of asking.** Four bounded successors, each with a first move: `W1_19` the three
drivers per land cell (needs nothing but the disk), `W1_20` household weights from the censuses,
`W1_21` the clustering and the level coverage curve, `W1_22` cold-spell persistence and cross-cell
synchrony. Then the first one was taken.

**What W1_19 found.** The grid is 1450 × 900 and only 18.8% of it is land — 245,077 cells, matching
the count the pull had already recorded, so the read is independently corroborated. A mean over the
full array is a mean over the Atlantic.

The ruling makes two falsifiable predictions. *"The north–south gradient dominates solar"* is
confirmed, at −0.806 between latitude and sunshine. *"Winter temperature and wind are positively
correlated"* is **refuted as written**: across land cells it is −0.430.

**Both signs are right, and that is the actual finding.** The claim is true in *time* and false in
*space*. This project had already measured the temporal half — winter temp/wind correlation +0.507,
the cold-and-still joint tail with its 2.34× decile lift. In a given winter at a given place, cold
snaps arrive with still air. Across *places*, the windiest cells are northern, upland and exposed,
and those are the cold ones. Deriving cells partitions space, so the spatial figure is the one that
governs there; persistence, synchrony and hedging live in time and take the positive one. Pooling
them would be the definitional failure this project keeps paying for.

The most consequential number was not one of the predictions: **annual temperature and sunshine
correlate at +0.841 across space**, both dominated by the same north–south gradient. So clustering on
three drivers is not clustering on three independent axes, and the coverage curve should be expected
to rise faster than a three-dimensional argument suggests.

**What the tree cost, and it is worth recording.** The mint took seven attempts to land. Two atom-number
collisions with a concurrent lane minting the same ruling's phase-2 and phase-3 rows — they renumbered
and recorded the collision in their own store file, so nothing was lost, and their orphaned files were
removed only after checking their replacements were strict supersets. The map's size ratchet refused
the landing twice: it counts both map halves together and sits close to its ceiling, so any atom
addition can break it, and the long reasoning had to move into the simplifications store where the
control says it belongs. `site/data/` appeared in a file_scope again — the second time, caught by the
same guard both times. And the content file had to be rebuilt once because it was assembled against a
HEAD that moved: `--content` overwrites a whole file, so landing a stale assembly would have reverted
another lane's just-landed work. The gate caught that as a store/map mismatch rather than as a silent
revert, which is the only reason it was visible.

**Where it stands.** `W1_20` is next — household weights from the censuses via postcode, which the
ruling forbids taking from the SIM's own population because that would make the coverage curve a
statement about our draw rather than about Britain. It needs a pull this tree does not hold.

---

## 2026-09-06 — The startup anchors named the stalest documents and omitted every surface holding current reasoning

<!-- head: 66dfc5de04df -->

**What this stretch was about.** The set of documents a fresh session is told to read on startup —
the "anchors" — had stopped describing how to orient. It named PROJECT_OVERVIEW, the annual report
and ASSUMPTIONS: what the project *is*. It named nothing about what the project is currently *doing*
or why, all of which arrived later — the delivery seat's direction record, the decisions log, the
class registers, the stretch log.

**The measurement.** Of the five surfaces named, two had zero commits in fourteen days. Of the
surfaces the machine keeps current, the five most active were named nowhere: `PROJECT_STATE.txt`
(270 modifications in 30 days), `DIRECTION.yaml`, `decisions.jsonl`, `knowledge_map.md`, and the
stretch log. So the anchors pointed at the stalest documents and omitted the freshest.

**Why the obvious fix was the wrong one.** Ranking `docs/` paths by edit frequency and calling the
top ones anchors puts the *retired* `docs/shadow/` mirror pages above `knowledge_map.md`, and it
would never have caught the stretch log — two commits old on the day it was missed. Frequency
measures how busy a file is, not whether a reader needs it.

The structural signal is that **a module declares a path to it**. A surface the machine maintains is
one a reader can be sent to, however new. That finds eight published reader surfaces, five named and
three not — and a landing is now refused while any of them is unnamed. The instance and the class
close together.

**Two exemptions, named rather than papered over.** `DIRECTION.yaml` and `decisions.jsonl` are
assembled in two steps — a directory constant, then the filename — so an AST scan reading
single-expression constants cannot see them. They are listed with that reason, and a control reds if
either becomes discoverable, so the exemption cannot outlive its cause. This is the same shape as
`finding_classes` in the derived-artefact register, handled the same way.

**What the anchors now say.** Each entry carries a sentence saying what the surface is *for* rather
than what it is called — "Assumptions" became "every sourced assumption the world is built on, with
its anchor and its gaps". The rendered freshness table gained that as a column and an opening line
telling a reader to start there. The label is taken from the same line the path came from, so the
table cannot describe one anchor and age another.

**A live defect the new control caught immediately.** `ASSUMPTIONS.md` claimed "Last seeded:
2026-08-10" while another lane had committed rows to it on 2026-09-05 — 26 days out, and blocking
every landing. Its header now states the true date *and* says the line is checked against git, so
the next person adding a row is told what they owe rather than discovering it.

**Where it stands.** Eleven anchors, none unnamed, the check clean. Stage 1 is unchanged and next:
the fitted premise joint, the space-filling sample, and the people joint on small-area geography —
all above billing correctness, which is above the supplier optimising.

---

## 2026-09-06 — Stretch reports became a committed file on the mirror, and the lapse check shipped matching titles instead of paths

<!-- head: 073bb159ec0d -->

**What this stretch was about.** Making the reasoning behind the work durable. The director's
observation was that the prose written at the end of a piece of work — the corrections, the things
stopped short of, why a call went one way — is the most useful thing produced and the only thing not
kept: commits record what changed, and the why lived in a console window that gets cleared.

**What was already there, which is most of it.** The delivery seat writes roughly 3,000 characters
of stretch prose into `docs/direction/DIRECTION.yaml`'s `thesis_read` at every orientation, and
`tools/generate_delivery_page.py` already renders it into `site/data/delivery.json` for the
director's page. Three things were missing, not a mechanism:

1. it is a YAML scalar rather than a document — nobody reads a config field months later;
2. it is overwritten each orientation, so git holds the history and a reader does not;
3. it reaches `site/` (Cloudflare) and never `docs/`, which is the tree the GitHub Pages mirror
   publishes and the channel the advisor actually fetches.

And a fourth the seat could never have covered: an interactive session's reports entered none of it.

**What was built.** One file, `docs/status/SEAT_STRETCH_LOG.md`, newest entry first, published by the
same push as `LATEST.md`. `tools/stretch_log.py` appends entries and checks for lapses. It computes
nothing the existing renderer already computes.

**The two properties, enforced rather than requested.** A lapse is a *finding*, not a refusal:
`--check` counts the commits landed since the newest entry's recorded head and names their subjects,
and it is wired into the publish path as a log line. A gate would be wrong for a structural reason —
a report is written when a piece of work *finishes*, so refusing every commit in between would block
the work it exists to describe. And an entry must stand alone: `append` refuses a subject that leans
on the conversation it was written in ("as discussed", "per your last", "continuing") or one too
short to name its subject, because a reader in six months has none of that context. The phrase check
is on the subject only — a body may legitimately quote a console turn.

**The defect it shipped with, found within the hour.** The exclusion that stops the log counting its
own commit matched a *title* — subjects containing "stretch log". Its own landing commit was called
"the why, kept: stretch reports land in a committed file on the mirror", which says "stretch
reports", so it slipped through and the tool reported itself as owing a report for the commit that
wrote it. That is the same shape as two wrong measurements the day before, where module callers were
counted by text search and docstrings and dict keys counted as calls, and the same shape as a class
register whose title-keyed classifier could not see 92 findings. It is now excluded by *path*: if a
commit touched the log it is the report, whatever it is called.

**One thing worth keeping about the fix.** The control that drives it must answer the two `git log`
shapes differently — the commit range, and the range restricted to the log's path. A stub that
returns the same text for both makes every commit look like it touched the log, so nothing is ever
owed. A sibling test had exactly that stub and went red when the real behaviour arrived, which is how
the gap surfaced at all.

**Where it stands.** The log is live with two entries, published on the mirror, and `--check` is
green. Stage 1 continues: the fitted joint, the space-filling sample and the people joint remain
queued above billing correctness, which is above the supplier optimising.

---

## 2026-09-06 — Stage 1 housing and people anchors from NEED, two budget dials raised for one window, and a corrected sample size

<!-- head: b01b1dbe392e -->

**What this stretch was about.** Stage 1 of the three-stage sequence the director set on
2026-09-05: build a robust end-to-end SIM (weather, houses, people) before billing correctness, and
both before the supplier optimising. Concretely: anchoring the housing joint against published data,
measuring what the premise draw already carries, and sizing the space-filling sample. Plus two
budget dials raised for one allowance window, and the sequencing of a use-case register that arrived
mid-stretch.

**What was established, all from DESNZ NEED `anon2026_50k.csv` (50,000 dwellings, one row each):**

- *Floor area* is anchored from **HMRC** valuation bands via NEED, not the EPC register the housing
  ruling named. EPC needs a GOV.UK account and is the worse source on the ruling's own terms — ~60%
  coverage, transaction-biased, SAP-*modelled* consumption. NEED is open and metered. Median gas runs
  2.56× from the modal 51–100 m² band to >200 m².
- *Bungalows* are a first-class type at 7.9%, with a distribution unlike detached — closing the
  ruling's "folded into detached" gap with a published share.
- *"Off gas" is a fact about a meter, not the grid.* NEED's `MAIN_HEAT_FUEL` is derived: no matched
  meter **or** under 1,000 kWh in three years. 50.3% of flats read as "not gas", which cannot be
  off-grid — it is communal or electric heating with no individual meter. So the attribute drawn is
  `has_mains_gas_supply`, the fact a supplier actually holds. The true off-grid share stays a gap.
- *Independence invents one house in five.* Drawing the axes independently puts 19.6% of houses in
  cells the stock does not contain (1,303 detached under 50 m²; zero exist) while under-producing
  detached >200 m² — the top consumption band — by 5.15×.
- *Rejecting on labels covers 6.1% of the top-1% tail; rejecting on outputs covers 85.4%.* The
  label-based sample reports 92% overall and is nearly blind to the tail.
- *Area deprivation is mostly the house.* Median gas by IMD quintile spreads 1.38× raw and only
  1.09–1.20× within one floor-area band. Supports the housing ruling's H2; narrows the people
  ruling's geography claim to *composition*, not usage-given-the-house.

**The correction that matters most.** I published "N ≈ 100 houses covers 99.6% of the output space",
flagged as a lower bound because shape and gradient were unavailable. That was too generous. Adding
one further dimension the use cases actually need — inter-year consumption volatility, i.e.
bill-shock exposure — takes N=100 from 99.2% coverage to **32.7%**; at 250 it is 87.7% and still
short. The figure was an artefact of measuring the two dimensions that were easiest to obtain. It is
corrected beside the original claim as well as in a new document, because a figure quoted once gets
quoted again from wherever it was found.

**Calls made, and the reasoning.**

- *Source swapped from EPC to NEED* without asking: evidence in hand, reasoning sound, reversal is a
  one-line change.
- *Fork width raised to 2 — but only after refusing to do it myself.* A control asserted the value
  with "if someone widens this without a director decision, this fails". Widening it and then editing
  that guard would have been self-certifying, so it was backed out and the lever reported instead.
  The director then authorised it. The guard now pins its expected value to the window's **own
  clock** — 2 before 02:50Z on 2026-09-07, 1 after — so if the restore never runs the test reds by
  itself and says the timer did not fire. An earlier draft had the restore script edit the guard too;
  driving that on a copy left the tree red, a restore that breaks what it restores.
- *Tick cadence 1800s → 120s.* Duty cycle measured at 47%; the service is `Type=oneshot`, so systemd
  cannot stack activations — the dial's whole ceiling is ~2×, and that was reported rather than
  discovered later.

**Stopped short of, deliberately.**

- *Flow temperature* stays out of phase 1 and is a registered gap. It has zero occurrences anywhere
  in `simulation/`, and the director's reasoning is recorded: the lever only means something once a
  product could turn it down, and inventing hidden state for a ceiling nothing can act on is not
  fidelity. The consequence is written down so it is not rediscovered as an oversight — the
  turn-down lever's ceiling is *unstateable*, not merely uncomputed.
- *The use-case register's use cases* are stage 3 and none is built, however ready the mechanics look.
  Only its second half — the SIM fidelity each use case depends on — is stage 1, folded into the
  housing and people phase-1 atoms rather than minted as new work.
- *A third fork.* There is no third disjoint scope; W2_19 and W2_21 both touch
  `simulation/population_draw.py`, so it would buy contention.

**Mistakes the tree caught, worth keeping.** The map's hygiene control caught a data-asset atom filed
under the default value stream; the fix for it then landed on a *different* atom's identical two
lines, and the stale-id control named that in the same run. Separately, inserting the N correction
split a sentence and left "this is the number it asked for" standing immediately after the retraction
— worse than either alone, since a skimming reader takes the last sentence.

**Where it stands.** Stage 1 continues: the fitted joint (W2_21), the sample (W2_22) and the people
joint (W2_19) are queued and ranked above billing, which is above the supplier optimising. Both
budget dials revert automatically at 02:50Z on 2026-09-07.

---
