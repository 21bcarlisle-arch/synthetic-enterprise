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
| P0 | §8 pred 3 needs no inversion | *not yet run* |
| P1 | six anchors up, 2020 down | *not yet run* |
| P2 | 2022 does not move | *not yet run* |
| P3 | renewal move 2–3× the book move | *not yet run* |
| P4 | net margin and EV both fall | *not yet run* |
| P5 | band unwidened | *not yet run* |
| P6 | control reds on c2 for two reasons, greens on c4 | *not yet run* |
