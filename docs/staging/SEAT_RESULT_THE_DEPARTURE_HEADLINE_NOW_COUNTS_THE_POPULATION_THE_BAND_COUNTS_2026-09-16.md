**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# The departure headline now counts the population the band counts, and every preregistered figure held

Outcome of
`SEAT_PREREG_WHAT_THE_PAGE_WILL_SAY_WHEN_THE_DEPARTURE_HEADLINE_MOVES_TO_THE_WHOLE_BOOK_2026-09-16.md`,
which discharges
`SEAT_FINDING_THE_PAGES_DEPARTURE_HEADLINE_IS_A_MEAN_OVER_SHOPPERS_JUDGED_AGAINST_A_BAND_OVER_EVERYBODY_2026-09-09.md`
(BLOCKING, seven days, fourth instance of its class in a fortnight).

## What the page said, and what it says now

| | before | after |
|---|---|---|
| headline column | mean expected departure at a RENEWAL decision | every departure on either route over the accounts on the book |
| years compared | 7 (2017–21, 23, 24) | 8 (2017–2024, gaining 2022) |
| mean level | 28.08% | 15.96% |
| band verdict | **0 of 7 inside** | **6 of 8 inside** |
| stated discount factor | **1.63x** | **1.03x** |
| against DESNZ QEP 2.7.1 | 1.80x | 1.14x |

The sentence a reader meets is composed, not edited, so its own denominator claim — "% of
electricity accounts a year" — became TRUE without a word of it changing. That is the tell that the
defect was always the caller and never the prose: `tools/measure_departure_level` exposed two
correctly-named functions and `_world_departure_level` called the wrong one.

## The preregistration, graded

**P1 ✓** 8 years, 2017–2024, gaining 2022. **P2 ✓** every per-year level to the 0.01pp
(14.00 / 20.00 / 21.30 / 22.97 / 18.53 / 2.50 / 12.40 / 15.96). **P3 ✓** 6 inside, out in 2021
(HIGH) and 2022 (LOW), `all_inside_the_band` false. **P4 ✓** 15.96 / 15.50 / 0.857. **P5 ✓** the
ABOVE branch at **1.03x**, direction unchanged, magnitude down from 63% to 3%. **P6 ✓** 8 years,
15.96% against 14.03%, ratio 1.137, world above in 6 — below in 2017 and 2022, the two named years.
**P7 ✓** the renewal column stays, 7 years at 28.08%, with no band, no verdict and no ratio.
**P8 ✓** the band remains the flattering standard (1.03x against 1.14x), and both of
`_publisher_bound_statement`'s sentences did have to be rewritten rather than adjusted.

**P9 ✓ on the substance, and the method had to change to establish it.** Attribution was taken by
publishing twice from two clean clones of HEAD differing in one file — `git clone --shared`, so the
publish identity is the real `dcb8c6d10` and not a throwaway repo's. The only top-level key that
moved between them is `departure_level`, plus `generated_at`, which every publish moves. The first
attempt at this used a `git archive` extract with `git init`, and it FAILED CLOSED instead:
`book_reading_refusal` could not run `git ls-files`, so the block published "could not be
established" — the new fail-closed path working on its first live application, before it was asked
to.

**Nothing was wrong.** That is worth saying plainly rather than passing over: the predictions were
re-derived from the instrument's own primitives and the arithmetic of the publisher was what was
being predicted, so a miss would have been in P4/P5/P9 and would have mattered. P4 was the one that
could have gone either way — the 8-year band-midpoint mean is 15.50 because 2022's 2.9–4.3 band
drags it down, and a world mean of 15.96 sits only just above it. Had it landed below, the page's
instruction would have flipped from "reads LOW" to "reads HIGH" and this would have been a much
larger move than a re-siting.

## Why the committed feed was SPLICED and not republished

`site/data/value_arms.json` in this landing is the committed feed with `departure_level` and
`generated_at` replaced, and that is deliberate. A full republish from HEAD bytes would have
silently reverted the `realised` block to a six-day-old run: the newest run artefact
(`docs/reports/run_output_dbd92cedc_20260916T044947Z.json`) is UNTRACKED in the shared tree, so a
clean clone cannot see it and republishes `run_output_258720283_20260910T005624Z.json` instead.
Landing that would have moved the published supplier's net margin by £672 as a side effect of a
departure-level repair — the exact shape of unattributable move this preregistration exists to stop.
The shared tree could not be used either: it cannot import the producer at all
(`ImportError: cannot import name 'departure_decision_leg' from 'simulation.customer_events'`,
another lane mid-edit, and the subject of its own repeating alarm in the queue).

## What the controls now hold, and the one that had to move

`site/test_the_baseline_comparison_reaches_the_reader.py::test_the_level_on_the_page_is_the_one_the_measuring_tool_REPORTS`
read `world_realised_rate_pct` and was GREEN throughout the week the page misread itself, because
the page did agree with the function it called. Its subject is re-sited to `world_book_rate_pct` in
the same commit as the repair — which this project's own rule warns against — and the mitigation is
this preregistration plus a second leg that keeps the old subject alive:
`test_the_shoppers_column_reaches_the_reader_AND_carries_no_verdict` asserts the renewal readings
reach the reader, that the reason they carry no verdict reaches them too, and that no row in that
block ever grows a `band_lo_pct`, an `inside_band`, a `share_of_the_band` or an
`against_the_publisher`. Re-rendering a band one table lower is how this defect would come back.

**A control cannot catch this class and that is the finding under the finding.** Every control over
this block checked that the page agrees with the function it calls. Choosing the wrong one of two
correct functions is invisible to all of them, and it is invisible to a thirty-minute tick for the
same reason: the question is *which quantity does the reader need*, which only the seat holds.

## The knowledge gap, filed rather than guessed

The renewal-decision column is a real quantity about a real population — how readily a household
that reached a fixed-term end leaves — and for a company whose thesis is finding movable customers
it may be the more interesting one. So it stays on the page, labelled, with the absence stated
where the number is: nothing published states a GB switching rate over that sub-population. Filed
in the switching-rate row of `docs/institutional/knowledge_map.md`, with the near-miss named —
Ofgem's retail market indicators carry a tariff-type split of the STOCK, which is not a rate at the
switch and must not be substituted for one.

## Measured beside this, not repaired here

`tests/tools/test_the_value_arms_pages_undriven_pointers.py` is RED AT HEAD — four errors, and they
are HEAD's, not this landing's: measured in a clean clone of `dcb8c6d10` with nothing of mine in it.
`build()` takes 8 artefacts and that file's `_real_inputs` fixture supplies 6, so the whole rung
errors at setup and judges no pointer at all. Its own docstring predicted exactly this failure mode
and asked for the refusal to name itself, which it does. Left for its lane with the cause named
rather than swept into a departure-level commit.

## Item 3 of the finding is NOT done

"Sweep for the same shape — every other place in the tree that divides a count by a population and
compares it to a published rate should be asked which population each side counts." That is a
census, it is the right next move, and it is not in this landing. It is the residue of this finding
and the reason the class keeps recurring.

**Measured:** 2026-09-16, delivery seat, Lane 0.
