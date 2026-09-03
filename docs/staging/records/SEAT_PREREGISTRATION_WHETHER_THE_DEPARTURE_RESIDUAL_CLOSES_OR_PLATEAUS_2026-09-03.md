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
| Q1 | mean distance outside does not halve again (≥0.215pp) | *pending* |
| Q2 | at most 4 of 8 years in band | *pending* |
| Q3 | 2017 or 2024 falls OUT of band | *pending* |
| Q4 | 2017 or 2023 moves >0.50pp on a ~2% anchor move | *pending* |
| Q5 | both margins fall, by less than pass 1 | *pending* |
| Q6 | band unwidened | *pending* |
| Q7 | anchor and capture in one commit | *pending* |
