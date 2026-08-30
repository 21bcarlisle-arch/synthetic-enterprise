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
