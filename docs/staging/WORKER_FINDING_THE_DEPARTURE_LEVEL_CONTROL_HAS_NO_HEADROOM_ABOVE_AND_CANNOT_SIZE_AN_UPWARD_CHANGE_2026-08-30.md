**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# The departure-level control sits exactly on its band's ceiling, so any upward change fails it and none can be sized

**Found:** 2026-08-31, as a by-product of the C3 counterfactual
(`WORKER_PREREGISTRATION_WHAT_THE_SHOWN_PRICE_MUST_SHOW_2026-08-30.md`). It is worth more than the
experiment that found it.

## The measurement

Two full captures of the same tree, differing by one variable. The **baseline** column is the world
as it stands on `main`:

| year | published band | baseline realised % | headroom above |
|---|---|---|---|
| 2016 | 17.0–17.6 | **17.60** | **0.00** |
| 2017 | 13.5–14.0 | **14.00** | **0.00** |
| 2018 | 19.5–20.0 | **20.00** | **0.00** |
| 2019 | 20.7–21.3 | **21.30** | **0.00** |
| 2020 | 22.5–23.0 | **23.00** | **0.00** |
| 2021 | 17.9–18.4 | **18.40** | **0.00** |
| 2022 | 2.9–4.3 | **4.30** | **0.00** |
| 2023 | 8.9–12.5 | **12.50** | **0.00** |
| 2024 | 12.5–16.1 | **16.10** | **0.00** |
| 2025 | 14.3–17.9 | **17.90** | **0.00** |

**Ten years out of ten, the world's realised departure level sits on the exact top of its band.**

## Why, and it is not an accident

`simulation/departure_level_anchor.YEAR_LEVEL_ANCHOR` was fitted to the band's **high endpoint** —
the deliberate anti-flattering tie-break: a stickier book earns more, so aiming at the top of the
published range is the choice that makes the company's position harder rather than easier. **The
choice was right.** Its consequence was not noticed.

## The consequence: the control is one-sided and cannot size anything

`test_the_worlds_realised_departure_rate_is_inside_the_published_band` compares against the band at
the record's own precision. With zero headroom above:

* **Any** upward movement fails it. In the C3 arm, a **+0.11pp** move in 2024 — a 0.7% relative
  change that moved *zero departures*, 79 either way — "leaves the published band". So does a
  change ten times larger. The control's verdict is identical for both.
* **Downward movement has room and is therefore invisible** until it crosses the band's low end —
  0.6pp in 2016, but 3.6pp in 2023 and 3.6pp in 2025. So the same size of change is caught or
  missed depending on how wide that year's published band happens to be, in a direction that
  **favours the company**: fewer departures is a stickier book.

The control answers "is the world still on its anchor" and reads as if it answered "is the world
still lawful". Those are different questions and only the second is worth having.

This is close to the instrument-resolution class already on record
(`project_instrument_resolution_is_seventeen`): the question is not only what moved, but what the
instrument could have detected. **Here the instrument's resolution above the line is zero and below
the line is between 0.6pp and 3.6pp depending on the year.**

## What is owed

1. **Report the DISTANCE, not only the verdict.** The measuring tool
   (`tools/measure_departure_level.py`) already computes everything needed; it should print each
   year's margin to both band edges so a reader can tell +0.11pp from +5pp. This is the same repair
   shipped this evening for the "worse than guessing" count, and for the same reason: a threshold
   crossing is not a magnitude.
2. **Decide whether the anchor should aim at the band MIDPOINT instead of its high end.** This is a
   genuine trade and it belongs to the director, because it trades one anti-flattering property for
   another: aiming high keeps the book maximally leaky (against us), aiming at the midpoint gives
   the control symmetric detection (against us in a different way — it would start catching
   downward drift that currently hides). **I am not making that change: it is a curriculum-adjacent
   choice, not a correction, because both options are defensible and the honest version does not
   obviously make our position worse.**
3. **Nothing here should be repaired by widening the band.** The band is the published record.

## What this does NOT say

It does not say the anchor's values are wrong, or that the world is mis-calibrated. The fit is good
— that is exactly why every year lands on the endpoint. It says the **control built on top of that
fit cannot distinguish sizes in one direction and has year-dependent resolution in the other**, and
that anyone reading a red from it, including me an hour ago, will over-read it.

---

## DISCHARGED 2026-08-31 — items 1 and 3. Item 2 remains the director's.

**1. Report the DISTANCE, not only the verdict. DONE.**
`tools/measure_departure_level.py` grows `band_margins()` and two columns, `room to LOW pp` and
`room to HIGH pp`, signed, at the record's own precision. Negative means already outside. Beneath
the table it now states its own resolution in both directions. Measured output confirms this
finding's table exactly: **room above is +0.00pp in every one of the ten years; room below runs
+0.50pp (2017) to +3.60pp (2023, 2024, 2025).**

**The one-sidedness is now stated ON THE CONTROL**, in
`test_the_worlds_realised_departure_rate_is_inside_the_published_band`'s own docstring, where the
next reader hits it — not only here, where nobody re-reads. The failure message carries both
margins too, so a red cannot be over-read without the size in front of you.

**A test that fails if the margin output is dropped: two of them.**
`test_the_instrument_prints_the_distance_to_both_band_edges_and_not_only_the_verdict` asserts the
columns are present and equal to what `band_margins` computes; it is keyed to the property, so
re-aiming the anchor at the band midpoint passes it. `test_band_margins_are_signed_distances_and_
go_negative_outside_the_band` holds the sign against an independent expectation — needed because
the first leg shares `band_margins` with the producer and therefore cannot see that function
change under it. Both mutation-proven in-process (no file edits: another lane's hook chain was
live in this tree).

**A mutation that could not fire, found while proving these and corrected in place.** The band
control's docstring said *"MUTATION: divide any `YEAR_LEVEL_ANCHOR` entry by two and this fires."*
**It does not.** The control's subject is a captured artefact
(`docs/reports/c2_departure_factors.json`) and the anchor module is not in its read path — halving
`YEAR_LEVEL_ANCHOR[2020]` leaves it green, because the captured table still carries
`sim_level_anchor: 4.425742` from the run that produced it. Not a fail-open: the control does fire
on the quantity it actually reads (halving 2020's captured rate fires with the margins in the
message). But a reader following the old instruction would have concluded the control was broken,
or that the anchor was safe to edit. The docstring now names the mutation that fires and says the
anchor reaches this control **only through a re-capture**.

**3. Nothing was repaired by widening the band, and the anchor was not re-fitted.**

**2. The band MIDPOINT question is still the director's and is still not being taken.** Unchanged:
it trades one anti-flattering property for another, and both are defensible. What has changed is
that the cost of the current choice is now *visible on every run of the instrument* rather than
resting on someone remembering this document.

### What the C3 split added, and it strengthens item 2

`tools/split_price_response_by_curve_position.py` (filed against the C3 pre-registration) shows
C3's departure-level move is **+100.75pp where the company undercut the market and −53.99pp where
it priced above** — same world change, opposite signs by price side. So the upward band exits this
finding could not size are, in that instance, **not a property of the world change at all** but of
the arm it was measured in. That is the strongest case yet that a verdict without a margin is
unreadable here: the control fired ten times and none of the ten firings meant what it appeared to.

**Status: LATENT → the instrument leg is discharged; the anchor-aim question stays open for the
director.**
