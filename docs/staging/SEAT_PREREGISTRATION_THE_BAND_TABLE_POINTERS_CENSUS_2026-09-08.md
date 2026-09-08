**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — how many sentences point a reader at `#arms-redraw`, and from where

**Filed:** 2026-09-08, delivery seat (isolated worktree), **before** the census was run.

The drawn item names two producers in `tools/generate_value_arms_data.py` that send a reader to the
re-draw band table — `_redraw_band_clause` ("the band table directly below this headline") and
`_the_level_legs_family` ("the re-draw band table higher up this section"). It asks whether the
untied direction words are worth a control.

Before running anything, the two questions and my answers:

**Q1. How many string literals in `tools/generate_value_arms_data.py` claim a DIRECTION to the band
table?** Prediction: **three** — the one in `_redraw_band_clause` and the two branches of
`_the_level_legs_family`. No fourth producer anywhere in `tools/` or `site/`.

**Q2. For each such sentence, how many regions of `site/capabilities/index.html` does it render
into?** Prediction: **one each**. That is the premise the item is written on — "both are true
today only because of where their own regions sit" — and it is also the premise
`_the_level_legs_family`'s own docstring reasons from ("`#arms-composition` sits BELOW
`#arms-redraw`"). If it holds, the honest answer is probably *a small control*, because the cost of
the defect is a reader's scroll and not a number.

**What would change the answer.** If any of those sentences reaches more than one region, the two
regions sit on opposite sides of `#arms-redraw` and one of them is already saying something false —
in which case this is not a latent drift hazard at all but a live wrong pointer, and the control
stops being optional.

*The result is recorded beside this in
`SEAT_FINDING_A_POINTER_SENTENCE_WITH_TWO_HOMES_IS_FALSE_IN_ONE_OF_THEM_2026-09-08.md`.*
