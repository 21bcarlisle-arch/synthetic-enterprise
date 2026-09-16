**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a-commons-artefact-cannot-tell-when-its-source-was-revised

# PREREGISTRATION — what the page will say when the departure headline moves to the whole book

Written **before** any edit to `tools/generate_value_arms_data.py`, against
`SEAT_FINDING_THE_PAGES_DEPARTURE_HEADLINE_IS_A_MEAN_OVER_SHOPPERS_JUDGED_AGAINST_A_BAND_OVER_EVERYBODY_2026-09-09.md`
item 1, which requires it. The outcome is filed beside this document, right or wrong.

## How these numbers were obtained, and what is actually being predicted

**RE-DERIVED, NOT COPIED.** Nothing here is taken from the result document the finding names
(`SEAT_RESULT_THE_CORRECTED_RECORD_MAKES_THE_WORLD_LOOK_WORSE_...`) and nothing is read off the
live `site/data/value_arms.json`. Every figure below comes from calling
`tools.measure_departure_level`'s own primitives — `published_bands`, `world_book_rate_pct`,
`inside_band`, `publisher_comparison` — on `docs/reports/c6_second_pass_departure_factors.json`
today, 2026-09-16, and then doing by hand the arithmetic `_world_departure_level` does: round each
year to 2dp, take `fmean` over the rounded column, take `fmean` over the band midpoints.

**WHAT HAS PREDICTIVE CONTENT AND WHAT DOES NOT, said plainly rather than left for a reader to
work out.** The per-year LEVELS are not a prediction in any interesting sense: they come out of the
same module before and after, and the swap changes only which of its two functions the publisher
calls. What IS being predicted, and what can be wrong, is everything the PUBLISHER composes on top
of them — which rows survive `COMPARISON_YEARS`, which aggregate the sentence is built from, which
branch of `_departure_statement` fires, what the stated discount factor becomes, and whether
anything else on the page moves. Three of those (P5, P8, P9) are the ones I could not have read off
any instrument, and P5 is the one the finding is about.

## The predictions

**P1 — the comparison gains a year and loses seven.** The headline table will carry **8** years,
2017–2024. It gains **2022**, which the renewal column cannot cover at all (the capture family
carries zero 2022 renewal decisions; C1b routes every crisis-year passive roll to the SVT table).
The renewal column's 7 years leave the headline and are published as the second quantity.

**P2 — the levels, per year.** 2017 **14.00%**, 2018 **20.00%**, 2019 **21.30%**, 2020 **22.97%**,
2021 **18.53%**, 2022 **2.50%**, 2023 **12.40%**, 2024 **15.96%**.

**P3 — the verdicts.** Inside the band in 2017, 2018, 2019, 2020, 2023 and 2024; OUTSIDE in
**2021** (out HIGH, +0.13pp against a 17.9–18.4 band) and **2022** (out LOW, −0.40pp against
2.9–4.3). So `years_inside_the_band` **6**, `years_compared` **8**, `all_inside_the_band`
**false**. The two misses point in OPPOSITE directions, which the mean cannot show.

**P4 — the aggregates.** `world_mean_pct` **15.96**, `published_midpoint_mean_pct` **15.50**,
`mean_share_of_the_band` **0.857**.

**P5 — the sentence, and this is the figure the finding is about.** `_departure_statement` takes
its not-all-inside branch (6 ≠ 8) and, since 15.96 > 15.50, its ABOVE clause. The page's stated
discount factor becomes **1.03x**, against the **1.63x** live on origin today. The DIRECTION does
not change — the world still departs faster than the record's midpoint, so the page goes on telling
a reader the money figures read LOW — but the size of the discount it instructs collapses from 63%
to 3%. The sentence's own denominator claim ("% of electricity accounts a year") becomes TRUE
without a word of it being edited, which is the tell that the defect was always the caller and
never the prose.

**P6 — against the publisher.** 8 years compared, world mean **15.96%**, publisher mean **14.03%**,
`ratio_of_means` **1.137**, and the world reads above DESNZ in **6** of 8 — below in **2017**
(0.77x) and **2022**. Today's page states **1.80x** here.

**P7 — the second quantity.** The renewal-decision reading stays on the page, labelled, over its
own 7 years at a mean of **28.08%**, and it will carry **no in/out verdict and no ratio**, because
nothing in the commons publishes a switching rate over the households who reach a fixed-term end.
That absence is filed as a knowledge gap in the same landing rather than guessed at.

**P8 — which standard is the flattering one, after the move.** 1.03x against the refuted band and
1.14x against its publisher, so the **band is still the flattering standard** and
`_publisher_bound_statement`'s clause saying so stays true. I expect to have to REWRITE that
function even so, because both of its current sentences are false the moment the headline moves:
its lead calls the headline "the renewal-decision level", and its tail says "NEITHER FIGURE IS THE
COMPARABLE ONE".

**P9 — nothing else on the page moves.** The regenerated `site/data/value_arms.json` will differ
from the committed one **inside `departure_level` only**. If any other block moves, the swap has
reached something it has no business reaching and the landing is wrong, whatever the departure
figures read.

## What would refute this

Any of P1–P9 coming back different. The most likely place to be wrong is P4/P5: the mean of the
band MIDPOINTS over 8 years (15.50) includes 2022's 2.9–4.3 band, which drags the published mean
down a long way, and it is not obvious in advance that a world mean of 15.96 still sits ABOVE it.
If the mean had landed below, the page's whole instruction would have flipped from "reads LOW" to
"reads HIGH" and this would have been a much bigger move than a re-siting.

**Measured:** 2026-09-16, delivery seat, Lane 0. **Outcome:** filed beside this as
`SEAT_RESULT_THE_DEPARTURE_HEADLINE_NOW_COUNTS_THE_POPULATION_THE_BAND_COUNTS_2026-09-16.md`.
