# PRE-REGISTRATION — repointing the departure instrument at the committed capture, and which way the book must move

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Filed:** 2026-09-03, delivery seat, Lane 0, **before** any repoint or re-fit is run.
**Companion finding:** `SEAT_FINDING_THE_INSTRUMENT_JUDGES_THE_WORLD_ON_A_SUPERSEDED_CAPTURE_WHOSE_SVT_HALF_IS_IN_NO_COMMIT_2026-09-03.md`.
**Replaces, in the corrected direction:** §8 prediction 3 of `docs/market_research/gb_switching_rate_denominators.md`.

Everything below is written with the answer unknown. What I already measured — the two captures'
whole-book tables — is in the finding and is **not** predicted here; predicting a number I have
already read would be filing a prediction after the answer.

---

## P0 — the act (d) instruction was to replace a detector that is correct, and I am not replacing it

Lane 0 instructed: *"§8 prediction 3 says any headline company result improving after the change is
a defect in the change. It was written for a move that raises churn. This move lowers it toward the
record, so the book gets easier to hold and that detector fires on a correct change. Write the
replacement prediction down first."*

**The premise is refuted by the committed capture and the detector needs no replacement.** On
`c4_whole_book_departure_factors.json` the world sits *below* the published band in six of eight
years and in band in one. The correcting move therefore **raises** departures, not lowers them; the
book gets **harder** to hold, not easier; and "any headline company result improving after the
change is a defect in the change" is pointed at the correct tail exactly as written.

This is recorded here rather than acted on silently, because the instruction to invert it was
explicit and a reader who finds §8 prediction 3 unchanged is entitled to know it was examined.
**Prediction P0: after the re-fit, §8 prediction 3 will still be the right detector and will not
have been edited.** Refuted if the fitted anchors come out *below* the live block in a majority of
the seven leverable years.

## P1 — direction of the anchor move, per year

The re-fit solves each year's anchor onto `market_departure_rate(year)`. Given c4's margins, I
predict the fitted anchor moves **up** for 2017, 2018, 2019, 2021, 2023, 2024 and **down** for 2020.

Refuted if any of those six moves down, or if 2020 moves up.

## P2 — 2022 will not move at all, and that is the inert-slot finding, not a fit failure

`UNFITTED_YEARS[2022]` records zero renewal decisions in this capture family, and
`departure_risks`'s `CAUSE_SVT_INERTIA` line carries no `level_anchor`, so the anchor has no path
into the only route 2022 has. c4's SVT rows record `sim_level_anchor` 1.0 at 2022 — that is the
identity being *logged*, not the anchor being *applied*, and the two must not be read as the same
thing.

**Prediction P2: 2022's whole-book expected rate is byte-identical before and after the re-fit.**
Refuted if it moves by any amount. If it does move, the inert-slot finding
(`SEAT_FINDING_THE_2022_ANCHOR_SLOT_IS_INERT_SO_ITS_DECLARED_VALUE_IS_UNFALSIFIABLE_2026-09-02.md`)
is wrong and that is the more important result.

## P3 — size, stated as a range because the anchor reaches only one of the two routes

Over the seven leverable years c4's mean expected whole-book rate is **16.27%** against a mean
published midpoint of **17.20%** — a gap of **+0.93pp** to close, upward.

The anchor scales `build_departure_risks` only; it does not scale `svt_inertia`. So the whole-book
move must be carried entirely by the renewal share of departures. **Prediction P3: the fitted
anchors rise by more than 0.93pp-equivalent — the renewal-route expected rate moves by roughly
2–3× the whole-book move**, because the renewal route carries well under half the departures.

I am deliberately not predicting a single multiplier. Refuted if the renewal-route move is smaller
than the whole-book move, which would mean the anchor is reaching the SVT route after all.

## P4 — the book gets worse, and by roughly the churn increase

More departures means more revenue at risk and more re-acquisition spend. **Prediction P4: after
the re-fit, headline net margin and enterprise value both fall.** I do not predict a magnitude
beyond "not zero": the current published pair is £157,913 against £153,245, and a ~6% relative
increase in departures should be visible in both figures rather than absorbed.

**Refuted — and this is the trap detector, in its original and correct direction — if any headline
company result IMPROVES.** An improvement means the change made the world easier rather than more
faithful, and the change is the defect, not the result.

## P5 — what must NOT happen, checked by reading the artefact and not by recalling my own behaviour

The band must not be widened. `measure_departure_level`'s own text says so: *"A year flagged OUT OF
BAND means the anchor has gone stale against a world that moved under it -- re-capture and re-fit,
never widen the band."*

Discharged by pasting `git diff --stat` for
`docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json` and
`tools/measure_departure_level.py::published_bands` and showing both unchanged.

## P6 — the repoint's own control

The control the repair needs is *the capture an instrument judges on must have executed under the
anchor block that is live, and both its halves must be tracked*. **Prediction P6: written against
the live tree today, that control goes RED on `c2` for two independent reasons** — the untracked
sibling and the 2022 anchor of 3.053619 against a live `NO_LEVEL_CORRECTION` of 1.0 — **and GREEN
on `c4`.** Two reasons matter: a control that reds for only one of them would go green the moment
somebody committed the stale sibling, which is the fail-open.

Refuted if it reds on c2 for only one reason, or if it reds on c4.

---

## Grading

To be completed **beside** these predictions, whichever way each goes, in this file. A prediction
graded somewhere else is a prediction the next reader cannot check.

| | prediction | outcome |
|---|---|---|
| P0 | §8 pred 3 needs no inversion | **CONFIRMED** — graded below; the fit came out above the live block in 6 of 7 |
| P1 | six anchors up, 2020 down | **CONFIRMED, all seven** — graded below |
| P2 | 2022 does not move | **CONFIRMED** — 2022 is absent from the fitted block, as `UNFITTED_YEARS` says |
| P3 | renewal move 2–3× the book move | **OPEN** — needs the re-capture; the fit alone cannot show it |
| P4 | net margin and EV both fall | **OPEN** — needs the re-capture and a published run |
| P5 | band unwidened | **HELD**, graded below — neither the repoint nor the re-fit widened anything |
| P6 | control reds on c2 for two reasons, greens on c4 | **CONFIRMED**, graded below |

The re-fit HAS now been run (2026-09-03, second tick). P0, P1 and P2 are settled below. P3 and P4
stay open for a stated reason rather than a missing one: **both are quantities of the NEXT run, and
the re-fit changes what the next run is.** Grading them off `c4` would be grading the new anchors
against the population they were solved from, which is the fit's own fixed point and would confirm
itself by construction.

### P6 — CONFIRMED, and for the two independent reasons it named

Measured 2026-09-03 from the landed commit `5554c2910`, calling both refusals directly on both
captures:

| capture | renewal/SVT rows | `stale_anchor_refusal` | `untracked_capture_refusal` |
|---|---|---|---|
| `c2_departure_factors` | 148 / 1221 | **REFUSES** — *"ran under a superseded level anchor in 1 year(s) of 10 — 2022: ran at 3.05362, live block says 1 (187 row(s))"* | **REFUSES** — *"1 of this capture's two halves are in no commit (`c2_departure_factors_svt_segment_decisions.json`)"* |
| `c4_whole_book_departure_factors` | 156 / 1373 | passes (`None`) | passes (`None`) |

Two reds on `c2`, from two causes neither of which is the other, and two passes on `c4`. Not
refuted. The reason the two-reason requirement was written down is now load-bearing: had only the
untracked leg existed, committing that stale sibling — an obvious, well-meant tidy-up — would have
turned the control green while leaving the 2022 anchor of `3.053619` reading a band verdict off a
world the live block retired.

**187 rows, not the whole capture.** The refusal names one year of ten, and that is the honest
size of it: `c2`'s renewal half agrees with the live block everywhere. This is a capture whose two
halves disagree with *each other*, which is why the refusal reads both and why a reading of either
half alone would have passed.

### P5 — held for this commit, and the discharge is the artefact, not my recollection

P5 asked to be discharged by reading the artefact. `5554c2910` touches three files:

```
tests/architecture/test_a_capture_may_only_judge_the_world_that_produced_it.py | 253 +++++
tools/departure_population.py                                                  | 135 +++++
tools/measure_departure_level.py                                               |  38 +++-
```

`git diff --stat 5554c2910^ 5554c2910 -- docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`
returns empty — the commons band file is untouched. `published_bands` is byte-identical between
`5554c2910^` and `5554c2910`. Nothing was widened to make anything pass.

This is **not** the full discharge P5 asked for, which covers the re-fit as well. It is the half
that exists, recorded now so the next tick grades only what is still open.

### P0 — the half that could be checked, and it is the half act (d) would have broken

P0 predicted §8 prediction 3 would still be the right detector and would not have been edited.
`docs/market_research/gb_switching_rate_denominators.md` is not in `5554c2910`'s pathspec and is
unedited. The full prediction still needs the fitted anchors to come out *above* the live block in
a majority of the seven leverable years; that is the re-fit's to settle.

Worth restating because a future tick will read the drawn direction before it reads this file:
**act (d) instructed inverting a detector that is correct.** The instruction was written from
`c2`'s reading that the world departs *harder* than the record; on the committed capture it departs
*less* hard in six of eight years. Inverted as instructed, the detector would have been pointed at
the wrong tail and would have passed a change that flattered the book.

---

## The re-fit, run 2026-09-03 (second tick) — P0, P1, P2 graded

`PYTHONPATH=. python3 -m tools.fit_year_level_anchor docs/reports/c4_whole_book_departure_factors.json`,
whole-book fit, 156 renewal and 1,373 SVT decisions. The block was emitted, not refused — checked
explicitly against `WORKER_FINDING_A_REFUSED_WHOLE_BOOK_FIT_STILL_PRINTS_THE_PASTE_READY_BLOCK_AND_EXITS_ZERO_2026-09-01.md`,
which is the shape where a refusal still prints a paste-ready block and exits zero.

### P1 — CONFIRMED on all seven leverable years

| year | live block | fitted on c4 | predicted | observed |
|---|---|---|---|---|
| 2017 | 4.547299 | 7.249189 | up | **up** |
| 2018 | 2.882178 | 3.249206 | up | **up** |
| 2019 | 4.803900 | 5.253168 | up | **up** |
| 2020 | 6.412007 | 5.477177 | **down** | **down** |
| 2021 | 4.488202 | 5.268609 | up | **up** |
| 2023 | 0.364038 | 2.053916 | up | **up** |
| 2024 | 3.053619 | 4.120424 | up | **up** |

Not refuted: no predicted rise fell, and 2020 did not rise. P1 named the direction of seven
independent numbers before any of them was computed.

**Read the margin, never the verdict.** These are not seven equal results. 2023 moves 5.6× and 2017
1.6×, against whole-book gaps of −0.98pp and −2.41pp; 2019 moves 1.09× on a −0.22pp gap that
`measure_departure_level`'s own stated resolution cannot distinguish from noise on a 156-renewal
capture. 2019's move is inside the instrument's error bar and is reported here as a direction only.

### P0 — CONFIRMED, and the refutation condition was explicit

P0's refutation condition: *"refuted if the fitted anchors come out below the live block in a
majority of the seven leverable years."* They came out **above in six of seven**. The correcting
move raises departures, so §8 prediction 3 — *any headline company result improving after the
change is a defect in the change* — is pointed at the correct tail and is **unedited**.

`git diff --stat HEAD -- docs/market_research/gb_switching_rate_denominators.md` is empty.

The drawn instruction to invert it was therefore wrong in the direction that would have mattered:
inverted, it would have accepted a change that made the book easier to hold.

### P2 — CONFIRMED, and 2022 is absent rather than unmoved

2022 carries **zero renewal decisions** in c4, so the fit reports `2022: NOT FITTED — no renewal
decisions in this year` and emits no value. The inert-slot finding
(`SEAT_FINDING_THE_2022_ANCHOR_SLOT_IS_INERT_SO_ITS_DECLARED_VALUE_IS_UNFALSIFIABLE_2026-09-02.md`)
stands: the anchor has no path into the only route 2022 has.

Stated precisely, because "did not move" and "was never computed" are different claims and only one
of them is true here: 2022's anchor was **not solved for**, so P2's prediction that it would not
move is confirmed in the weaker of the two senses it could have been. A reader wanting the stronger
sense should read `UNFITTED_YEARS[2022]`, not this row.

### P5 — HELD, discharged by reading the artefacts

Neither the commons nor `published_bands` is touched by this work:

```
$ git diff --stat HEAD -- docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json
(empty)
```

`published_bands` in `tools/measure_departure_level.py` is unchanged by this tick's diff; the edits
to that file are the refusal-parity repair described below and touch no band value.

### P3 and P4 — OPEN, and why they cannot be graded off this capture

Both are quantities of the run that has **not happened yet**. The anchor's own docstring states the
iteration: *capture → fit → capture.* The fit is exact on the population it was solved against, so
reading P3's renewal-vs-book ratio or P4's margin and EV off `c4` would be reading the fixed point
the fit just constructed — a measurement that confirms itself.

The re-capture under the new anchors is what settles them, and it is the next increment.

### AND THE RE-FIT CANNOT BE LANDED ALONE — the controls said so, correctly

Applying the new block and running the suite reds two controls:

```
FAILED tests/architecture/test_switching_rate_commons.py::test_the_capture_the_band_verdict_is_read_from_was_produced_by_the_live_anchor
FAILED tests/architecture/test_a_capture_may_only_judge_the_world_that_produced_it.py::test_the_LIVE_DEFAULT_passes_both_refusals_whatever_it_is_pointed_at
```

Both are right and neither is a defect in the change. `stale_anchor_refusal` says a capture may only
judge the world that produced it, and changing the anchors is exactly what makes `c4` stop being
that world — in 9 of its 10 years.

**So the anchor block and its capture are one commit, not two.** This was not written down anywhere
before this tick, and it is the reason the previous tick could land the repoint but recorded that
"the re-fit has not run": a re-fit that lands without its capture wedges every lane in the tree.

---

## GRADED, 2026-09-03 — the re-fit ran, and the capture with it

Two captures of the same book at the same seed, differing in the anchor block and in nothing else.
`c5_refitted_departure_factors.json` (139 renewal / 1,338 SVT) is the treatment arm. The control arm
was re-run today with nothing injected and came out **byte-identical to `c4` in both halves**, so
`c4` IS the control and the pair is a genuine one-variable comparison rather than two runs compared
across a gap.

| | prediction | outcome |
|---|---|---|
| P0 | §8 pred 3 needs no inversion | **CONFIRMED** |
| P1 | six anchors up, 2020 down | **CONFIRMED, exactly** |
| P2 | 2022 does not move | **mechanism CONFIRMED; the prediction as written was untestable** |
| P3 | renewal move 2–3× the book move | **not refuted on its stated test; the point estimate was low** |
| P4 | net margin and EV both fall | **CONFIRMED** |
| P5 | band unwidened | **HELD** |
| P6 | control reds on c2 for two reasons, greens on c4 | CONFIRMED (graded above) |

### P1 — CONFIRMED, every year, no exceptions

| year | live | fitted | | |
|---|---|---|---|---|
| 2017 | 4.547299 | 7.249189 | **up** | ×1.59 |
| 2018 | 2.882178 | 3.249206 | **up** | ×1.13 |
| 2019 | 4.803900 | 5.253168 | **up** | ×1.09 |
| 2020 | 6.412007 | 5.477177 | **down** | ×0.85 |
| 2021 | 4.488202 | 5.268609 | **up** | ×1.17 |
| 2023 | 0.364038 | 2.053916 | **up** | ×5.64 |
| 2024 | 3.053619 | 4.120424 | **up** | ×1.35 |

Six up and 2020 down, which is the prediction named year by year. Its refutation condition — *any of
those six moving down, or 2020 moving up* — did not occur. **P0 follows**: the fitted anchors came
out above the live block in six of the seven leverable years, so the correcting move raises churn,
so §8 prediction 3 is pointed at the correct tail as written and has not been edited.

### P2 — the mechanism holds and the prediction was not testable as written

P2 said *"2022's whole-book expected rate is byte-identical before and after the re-fit"*, refuted
if it moves by any amount. It moved: **2.5356% → 2.5125%**, −0.023pp.

**That is not a refutation of what P2 was about, and saying so is not a rescue.** P2's subject is
whether the anchor reaches 2022 at all, and the direct test of that is what the capture RECORDS:
`sim_level_anchor` at 2022 is **1.0 in both captures**, with **zero renewal decisions in both**. The
anchor has no path into the only route 2022 has, exactly as `UNFITTED_YEARS[2022]` and the
inert-slot finding say. The 0.023pp is 213 SVT decisions becoming 205 — a different draw.

**The defect is in the prediction, and it is mine.** "Byte-identical" assumed the same capture
re-measured. A re-fit *requires* a new capture, and in a new capture every year moves by sampling.
The prediction was therefore refutable only by noise, in a direction that says nothing about its own
subject. Recorded here rather than quietly restated: **a prediction whose stated test cannot
distinguish its own mechanism from sampling is not yet a prediction**, and the fix is to name the
recorded quantity (`sim_level_anchor`) rather than a derived rate.

### P3 — not refuted, and the size was under-called

| year | renewal Δ | whole-book Δ | ratio |
|---|---|---|---|
| 2017 | +8.30 | +2.79 | 2.98 |
| 2018 | +5.46 | +1.86 | 2.93 |
| 2019 | −1.35 | −1.11 | 1.22 |
| 2020 | −4.64 | −2.84 | 1.63 |
| 2021 | +2.48 | +0.82 | 3.01 |
| 2023 | +13.06 | +4.64 | 2.82 |
| 2024 | +8.18 | +1.99 | 4.12 |
| **mean** | **+4.50pp** | **+1.16pp** | **3.87×** |

P3's stated refutation was *"the renewal-route move is smaller than the whole-book move, which would
mean the anchor is reaching the SVT route after all"*. It is larger in **every one of seven years**,
so the mechanism is confirmed and the prediction is not refuted. The point estimate — *"roughly
2–3×"* — was **low**: 3.87× on the means, with four years above 3. Kept beside the result rather
than adjusted.

### P4 — CONFIRMED, and the trap detector did not fire

One variable. Everything below is the same book, same seed, same code.

| | control (live anchors) | treatment (re-fitted) | Δ |
|---|---|---|---|
| gross margin | £401,580.43 | £386,196.20 | **−£15,384.23 (−3.8%)** |
| net margin | £126,487.72 | £120,932.62 | **−£5,555.10 (−4.4%)** |
| final treasury | £376,487.72 | £370,932.62 | −£5,555.10 |
| capital costs | £6,995.30 | £6,792.71 | −£202.59 |
| bad debt | £32,851.32 | £32,009.20 | −£842.12 |
| renewal decisions | 156 | 139 | −17 |
| SVT decisions | 1,373 | 1,338 | −35 |

Net margin and gross both fall. **No headline company result improved**, so the detector §8
prediction 3 arms — *"any headline company result improving after the change is a defect in the
change"* — did not fire, in the direction it was written and deliberately not inverted.

Bad debt and capital costs fell too, which is worth naming rather than presenting as more good news:
they fall because there are fewer customer-years on the book, not because the company got better at
anything. The book is smaller and harder to hold, which is what a more faithful churn level is
supposed to do to it.

### What this did NOT achieve, stated first because the numbers above read like success

**Six of eight years are still outside the published band.** Mean distance outside falls
0.875pp → 0.425pp and the worst year 2.40pp → 1.30pp; years inside go 1 of 8 → 2 of 8. That is a
convergence step, not an arrival, and the whole-book strict xfail stays on because it must. The
iteration is capture → fit → capture and this is one pass of it; the fit is exact on the population
it was solved against and approximate on the next one, which is a property of the thing and not a
defect in the fit.

**And the world is still not GB.** Everything the company has published about its own advantage was
measured inside a world whose departure level sat outside the record in every year. It is closer
now. It is not inside.
