# PRE-REGISTRATION — does the departure residual CLOSE, or does it PLATEAU?

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

**Filed:** 2026-09-03, delivery seat, Lane 0, **before** the pass-2 anchor block is applied and
**before** any re-capture under it is run.
**Predecessor:** `SEAT_PREREGISTRATION_WHETHER_REPOINTING_THE_INSTRUMENT_AT_THE_COMMITTED_CAPTURE_HOLDS_2026-09-03.md`,
which pre-registered and graded pass 1.
**The question is not mine.** `docs/institutional/knowledge_map.md`, the world's-departure-LEVEL
row, states it as the owed next step in its own words: *"Run the next capture → fit pass and see
whether the residual closes or plateaus; if it plateaus, the remaining gap is a mechanism question
and not a calibration one."* This file answers that and nothing wider.

---

## WHAT I ALREADY KNOW, DECLARED FIRST SO IT CANNOT BE PASSED OFF AS A PREDICTION

This is the part a reader must be able to check, because a prediction filed after the answer is not
a prediction and the only defence is to name the answers already in hand.

**Already read, and NOT predicted below:**

1. **The pass-2 fitted block.** `PYTHONPATH=. python3 tools/fit_year_level_anchor.py` run against
   the live default (`c5_refitted_departure_factors.json`, 139 renewal / 1,338 SVT) emitted a
   whole-book block before this file was written. Its seven values are in the table below. Nothing
   here predicts them.
2. **`c5`'s whole-book verdict.** 2 of 8 years in band (2017, 2024); mean distance outside the band
   0.43pp; worst year 2019 at 1.32pp low. Read off `measure_departure_level.py` at HEAD today.

**Not yet run, and therefore the legitimate subjects of prediction:** the capture taken *under* the
pass-2 block (`c6`), every whole-book figure measured on it, and every company headline under it.

## The observation this whole file turns on, stated before its consequence is tested

Two passes of the fit are now in hand, and put side by side they do not look like a sequence
converging on a fixed point:

| year | pre-pass-1 | pass-1 (= live block) | pass-2 (fitted on `c5`) | pass-1 move | pass-2 move | **net over both** |
|---|---|---|---|---|---|---|
| 2017 | 4.547299 | 7.249189 | 7.372584 | ×1.594 | ×1.017 | ×1.621 |
| 2018 | 2.882178 | 3.249206 | 2.945347 | ×1.127 | **×0.906** | **×1.022** |
| 2019 | 4.803900 | 5.253168 | 6.637286 | ×1.094 | ×1.263 | ×1.382 |
| 2020 | 6.412007 | 5.477177 | 6.359296 | **×0.854** | **×1.161** | **×0.992** |
| 2021 | 4.488202 | 5.268609 | 5.641346 | ×1.174 | ×1.071 | ×1.257 |
| 2023 | 0.364038 | 2.053916 | 2.033232 | ×5.642 | ×0.990 | ×5.585 |
| 2024 | 3.053619 | 4.120424 | 4.259915 | ×1.349 | ×1.034 | ×1.395 |

Geometric-mean anchor move: **pass 1 ×1.4724, pass 2 ×1.0578.** Pass 2 is an eighth of the nudge.

**2020 went down and then back up, and after two passes sits ×0.992 of where it started. 2018 did
the same at ×1.022.** Two of seven years have travelled a round trip. That is the signature of a
fit tracking sampling noise, not of one converging — and the per-year renewal counts say why it
would: **13 to 21 renewal decisions per year.** A year's rate estimated off 17 draws carries several
points of binomial noise, and the fit is exact on whatever draw it is handed.

I am *not* asserting that as the finding. It is the reason the predictions below take the shape they
do, and each of them can refute it.

---

## Q1 — the residual PLATEAUS rather than closes

Applying the pass-2 block and re-capturing as `c6`: **mean distance outside the published band, over
all eight full years, will NOT fall below 0.215pp** — that is, it will not halve again as it did
from pass 0 to pass 1 (0.875 → 0.425).

**Refuted if it falls below 0.215pp.**

## Q2 — in-band count does not reach the finish line

**Years in band on `c6` will be at most 4 of 8.** Pass 1 moved 1 → 2.

**Refuted if 5 or more of the eight full years land inside the band.** If that happens the residual
is closing, the plateau reading is wrong, and the strict xfail is within reach of a further pass —
which is the outcome I would rather have and am predicting against.

## Q3 — in-band membership is NOT monotone, and that is the plateau's fingerprint

**At least one of 2017 and 2024 — the two years that are INSIDE the band on `c5` — will fall OUTSIDE
it on `c6`.**

This is the sharpest of the five, because a converging process does not eject years it has already
taken. A noise-tracking one does, routinely.

**Refuted if both 2017 and 2024 remain in band.**

## Q4 — capture noise dominates the anchor signal in the years the anchor barely moved

2017's anchor moves ×1.017 and 2023's ×0.990. Those are moves of under 2%, far under the
instrument's own stated resolution. A ~2% change in a multiplicative anchor cannot move a whole-book
rate sitting near 13% by anything close to half a point.

**At least one of 2017 and 2023 will move by more than 0.50pp in whole-book expected rate between
`c5` and `c6`.** A move that size in a year whose anchor did not move is capture noise by
elimination, and it is what makes the plateau a sampling problem rather than a calibration one.

**Refuted if both move by 0.50pp or less.**

## Q5 — the trap detector, kept in its correct direction, and how an improvement will be read

§8 prediction 3 of `docs/market_research/gb_switching_rate_denominators.md` — *any headline company
result improving after the change is a defect in the change* — is **not being inverted**, for the
second tick running. The pass-2 anchors rise in five of seven years and the net move is +5.8%, so
the correcting move still **raises** departures and still makes the book **harder** to hold. Pass 1
established this against a drawn instruction to invert it; nothing since has changed the direction.

**Prediction: net margin and gross margin both fall again, and each falls by LESS than pass 1's
−4.4% and −3.8%** — because the anchor nudge is an eighth the size.

**Refuted if either headline improves, OR if either falls by more than pass 1's magnitude.**

**And I am pre-committing to how an improvement will be read, because after the fact it would be
arguable either way.** If a headline improves, the two candidate explanations are (i) the change
flattered the book, which is the defect §8 prediction 3 exists to catch, and (ii) run-to-run
sampling noise on a book of ~50 accounts a year. I will **not** be free to pick the flattering one.
The discriminator, fixed now: the net anchor move is **+5.8% upward** and upward means more
departures, so a *material* headline improvement (>1% on either margin) is graded as **the detector
FIRING** and the change is treated as the defect. A sub-1% improvement is graded **ambiguous and
reported as ambiguous**, not as a pass.

## Q6 — what must NOT happen, discharged by reading the artefact and not by recalling my own conduct

The band must not be widened, and neither the commons nor `published_bands` may be touched.
Discharged below by pasting `git diff --stat` for
`docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json` and for
`tools/measure_departure_level.py`, and showing no band value moved.

## Q7 — the anchor and its capture land in ONE commit

Not a prediction about the world; a constraint on my own conduct, recorded because pass 1 discovered
it the expensive way. `stale_anchor_refusal` says a capture may only judge the world that produced
it, so landing a new block without its capture makes every capture on disk stale and wedges every
lane behind two red controls.

Discharged by pasting `git show --stat` for the landing commit and showing
`simulation/departure_level_anchor.py` and both halves of the new capture in one pathspec.

---

## Grading

To be completed **beside** these predictions, in this file, whichever way each goes.

| | prediction | outcome |
|---|---|---|
| Q1 | mean distance outside does not halve again (≥0.215pp) | **REFUTED** — 0.4300 → **0.0663pp** |
| Q2 | at most 4 of 8 years in band | **REFUTED** — 2 of 8 → **6 of 8** |
| Q3 | 2017 or 2024 falls OUT of band | **REFUTED** — both stayed in |
| Q4 | 2017 or 2023 moves >0.50pp on a ~2% anchor move | **REFUTED** — 0.13pp and 0.16pp |
| Q5 | both margins fall, by less than pass 1 | **CONFIRMED** — −2.0% and −1.9%, on an established one-variable pair |
| Q6 | band unwidened | **HELD** |
| Q7 | anchor and capture in one commit | **HELD** |
| Q8 | land only if the residual does not worsen | **LAND** — 0.0663 ≤ 0.4300 |

---

# GRADED, 2026-09-03 — I PREDICTED A PLATEAU AND GOT CONVERGENCE, ON ALL FOUR COUNTS

Four predictions about the world, four refutations, and they were not close. The pass-2 block took
the world from **2 of 8 years in band to 6 of 8**, cut the mean distance outside the band by **6.5×**,
and did it while moving the company's headlines **against** it.

## The measurement

Capture: `docs/reports/c6_second_pass_departure_factors.json`, 133 renewal and 1,313 SVT
decisions. **That is not the file this grading was originally taken on, and the difference is the
most interesting thing in this document — see the replication section at the end.**

| year | published | `c5` (pass-1) | `c6` (pass-2) | move | verdict |
|---|---|---|---|---|---|
| 2017 | 13.5–14.0 | 13.87 inside | **14.00** | +0.13 | inside → inside |
| 2018 | 19.5–20.0 | 20.84 high 0.84 | **20.00** | −0.84 | **out → IN** |
| 2019 | 20.7–21.3 | 19.38 low 1.32 | **21.30** | +1.92 | **out → IN** |
| 2020 | 22.5–23.0 | 21.78 low 0.72 | **22.97** | +1.19 | **out → IN** |
| 2021 | 17.9–18.4 | 17.79 low 0.11 | **18.53** | +0.74 | out → out (**high by 0.13**) |
| 2022 |  2.9–4.3  |  2.51 low 0.39 |  **2.50** | −0.01 | out → out (low by 0.40) |
| 2023 |  8.9–12.5 | 12.56 high 0.06 | **12.40** | −0.16 | **out → IN** |
| 2024 | 12.5–16.1 | 15.82 inside | **15.96** | +0.14 | inside → inside |

**In band 2 → 6. Mean distance outside 0.4300pp → 0.0663pp. Worst year 1.32pp (2019) → 0.40pp (2022).**

## The pair is one-variable, and this time that had to be established rather than argued

**Nine commits from other lanes landed between the run that produced `c5` and the run that produced
`c6`.** "Same seed, same driver" was therefore not available as an argument, and pass 1's
established control could not simply be cited across that gap.

A control arm was run at this head with the pass-1 block still in place. It came out **byte-identical
to `c5` in both halves** — md5 `bb671977a59be26887e14e893733c8af` on the renewal half, and `cmp`
clean on the 669,959-byte SVT half. So those nine commits did not move the world, `c5` IS the
control, and `c5`-vs-`c6` differs in the anchor block and in nothing else.

Without that arm, every number above would have been two runs compared across a gap.

## Why I was wrong, which is worth more than the result

**I read the noise floor off the wrong denominator.** The whole file's reasoning rested on one
sentence: *"the per-year renewal counts say why it would: 13 to 21 renewal decisions per year. A
year's rate estimated off 17 draws carries several points of binomial noise."*

The quantity being fitted is **not** estimated off 17 draws. It is the whole book: the denominator
is accounts (41–59 a year) and roughly half its departures arrive on the SVT route, which carries
**1,313 decisions**. I took the noise base from the renewal route — the sub-population the
instrument's own banner warns is 51% of the departures — and applied it to a quantity computed over
the book. A per-year `n` an order of magnitude too small made a converging sequence look like a
random walk.

**Q4 is the prediction that shows the error most cleanly, and it refuted itself in one line.** It
said 2017 and 2023 — whose anchors moved ×1.017 and ×0.990, under 2% — would nonetheless swing more
than 0.50pp, because capture noise would swamp the anchor signal. They moved **0.13pp and 0.16pp**.
Years whose anchors barely moved barely moved. That is the *opposite* of noise domination: the
anchor-to-outcome relation is tight, and the capture is far quieter than I assumed.

**The round trips I built the plateau case on were not noise either.** 2020 went ×0.854 then ×1.161
and 2018 ×1.127 then ×0.906, and I read those as a fit chasing its own sampling error. They were the
fit correcting a pass-1 overshoot — and both years' whole-book rates moved decisively the right way
in `c6` (2020 out → in, 2018 out → in). An oscillating *parameter* and an oscillating *outcome* are
different things, and I inferred the second from the first without checking.

## Q5 — CONFIRMED, and the trap detector did not fire

Measured on the one-variable pair above:

| | `c5` (control) | `c6` (treatment) | move |
|---|---|---|---|
| gross margin | £386,196.20 | £378,553.66 | **−2.0%** |
| net margin | £120,932.62 | £118,614.39 | **−1.9%** |

Both fall, as predicted, and both fall by **less** than pass 1's −3.8% and −4.4%, as predicted —
which is what an eighth-the-size anchor nudge should do. **No headline improved**, so §8 prediction 3
of `gb_switching_rate_denominators.md` did not fire, and the pre-committed reading rule for an
improvement (>1% = detector firing; <1% = ambiguous) did not have to be used.

§8 prediction 3 remains **unedited**, for the second tick running, against a drawn instruction in
act (d) to invert it. Pass 1 established the instruction was written from the superseded capture's
sign; pass 2 confirms the direction again — the correcting move raises departures and makes the book
harder to hold.

## Q6 — HELD, discharged by reading the artefacts rather than by recalling my conduct

```
$ git diff --stat HEAD -- docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json
(empty)
```

`published_bands` in `tools/measure_departure_level.py` is untouched by this commit's diff; the
edits to that file are the `DEFAULT_TABLE` repoint and its provenance comment, and no band value
moves. The band was not widened, 2022 was not excluded, and the xfail was not re-keyed to "six of
eight" — all three of which would have bought a green while the claim stayed false.

## What this does NOT establish

- **Not** that the world is in band. Six of eight is not eight of eight and the strict xfail stays
  on. It is doing exactly what it was built for.
- **Not** that 2021 is genuinely high. It is out by **0.13pp** on a book of ~53 accounts. Reporting
  that in the same breath as 2019's old 1.32pp would be the verdict-not-margin error this
  instrument's own banner warns about, twice.
- **Not** that a third pass closes the last two years. **2022 cannot be closed by any fit**: it has
  zero renewal decisions and the anchor has no path into `svt_inertia`. The knowledge map's standing
  question — *"if it plateaus, the remaining gap is a mechanism question and not a calibration one"*
  — is answered in an order it did not anticipate. It did **not** plateau; it converged, and the
  residue that survived convergence is the mechanism question all along.
- **Not** that the fit is exact going forward. It is exact on the population it was solved against
  and approximate on the next, which is why `c6` is a re-capture and not the fit's own output.

---

## Q8 — the LANDING RULE, fixed before the capture is run

Added 2026-09-03 immediately after this file was committed and **before**
`tools/capture_departure_factors.py` was invoked for `c6`. The ordering is checkable: the commit
carrying this file precedes `c6`'s mtime, and `c6` did not exist when this was written.

It has to be fixed now because after the numbers are in it would be arguable either way, and
"we ran a pass and kept whichever block looked better" is fitting to the answer.

**I land the pass-2 block only if the residual does not WORSEN** — mean distance outside the
published band on `c6` must be less than or equal to `c5`'s 0.43pp.

- **Residual improves or holds** → land the pass-2 block with its capture, grade Q1–Q7.
- **Residual worsens** → the live (pass-1) block STAYS, `c6` is landed as evidence and nothing
  else, and the plateau is reported as measured rather than as predicted. A worsening pass is the
  strongest possible evidence for Q1 and Q2 and it must not be buried by reverting quietly.

Either branch is a result. Neither is a reason to run a third pass looking for a better draw —
that is the fit-to-the-answer this rule exists to prevent.

**Q8 GRADED: LAND.** `c6`'s mean distance outside the band is **0.0663pp** against `c5`'s
**0.4300pp**. The residual improved by 6.5x, so the first branch applies and the pass-2 block lands
with its capture. The "do not land" branch was never reached and is kept above rather than deleted,
because a rule that is only ever read in the branch it took is not evidence that the other branch
existed.

---

## THE REPLICATION — this pass was run TWICE, by two seats, in two worktrees, and the artefacts are byte-identical

Everything above was measured in an isolated worktree on a capture this seat took and named
`c6_pass2_departure_factors.json`. While it ran, **another seat drew the same Lane 0 item and did
the same pass independently**, landing first at `8242dcc25` with a capture named
`c6_second_pass_departure_factors.json`. Neither seat could see the other's work: origin showed
nothing until the losing seat tried to promote.

That is a duplicate, and duplicates are waste. It is written up here rather than quietly dropped
because of what fell out of it — **an unplanned, genuinely independent replication of the whole
pass**, which is a stronger form of evidence than either seat could have produced alone.

| | this seat | the seat that landed | agree? |
|---|---|---|---|
| fitted 2017 anchor | 7.372584 | 7.372584 | **yes** |
| fitted 2018–2024 anchors | 2.945347 / 6.637286 / 6.359296 / 5.641346 / 2.033232 / 4.259915 | identical | **yes** |
| capture, renewal half | md5 `3c56848b7ba64b6761efaa730e61bc73` | md5 `3c56848b7ba64b6761efaa730e61bc73` | **BYTE-IDENTICAL** |
| years in band | 2 of 8 → 6 of 8 | 2 of 8 → 6 of 8 | **yes** |
| mean distance outside | 0.4300 → 0.0663pp | 0.425 → 0.066pp | yes (rounding) |
| gross margin | £386,196.20 → £378,553.66 | identical | **yes** |
| net margin | £120,932.62 → £118,614.39 | identical | **yes** |
| control arm | byte-identical to `c5` in both halves | reproduced pass 1 "to the penny" | **yes** |

**Two seats, two worktrees, two control arms, one answer to the byte.** The determinism the whole
comparison rests on — that a re-run with nothing injected reproduces the prior capture exactly — has
now been established four separate times across three days, twice today by writers who did not know
the other existed.

**And the two pre-registrations were NOT the same, which is the part worth keeping.** The other
seat's (`SEAT_PREREGISTRATION_WHAT_THE_SECOND_REFIT_PASS_ON_C5_MUST_MOVE_2026-09-03.md`) predicted
the pass would move the world in. **This one predicted a plateau, on four counts, and all four were
refuted.** Two independent priors, opposite in direction, graded against one shared result — and the
one that was wrong is this one. A record that kept only the correct prediction would be evidence of
nothing.

**What was adopted and what was kept.** The other seat's anchor block, capture, instrument repoint
and xfail rewrite are on origin and this seat's duplicates of all four were discarded rather than
merged — identical values, so there was nothing to reconcile and no case for a second capture of the
same run sitting in `docs/reports/` under a second name, in a thread whose entire subject is
instruments reading the wrong capture. The discarded commit is preserved at
`refs/preserved/duplicate-pass2-040dbbff0` rather than deleted. What is kept is what only this lane
has: this grading, and the finding on `capture_departure_factors.DEFAULT_OUT`.

**The process defect this exposes, stated plainly:** two seats spent a full turn each on one item
because a Lane 0 claim was drawn twice, and the claim store showed it held. Roughly thirty minutes of
compute and two world runs bought a replication nobody asked for. Worth having once; not worth
having by accident again.
