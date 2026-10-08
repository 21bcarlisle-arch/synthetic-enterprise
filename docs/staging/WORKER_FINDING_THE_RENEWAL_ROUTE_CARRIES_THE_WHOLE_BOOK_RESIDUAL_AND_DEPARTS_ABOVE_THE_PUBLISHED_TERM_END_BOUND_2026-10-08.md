**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The renewal route carries the whole book's residual, and departs above what the published record allows at a term end

*Filed 2026-10-08 as the fidelity defect named by
`SEAT_FINDING_THE_WORLD_LOSES_FORTY_PERCENT_AT_EACH_ANNIVERSARY_AGAINST_A_PUBLISHED_SIX_2026-10-08.md`
(tests 1 and 2 graded there). Fix it blind to company results. This finding does not touch the churn
draw.*

## The defect

The settled world's renewal route departs at **E[depart] 41.9% per renewal decision, 2017-2024**
(`python3 -m tools.measure_departure_level`, capture
`qep_g_second_qep_pass_anchor_departure_factors.json`): 35.0 / 28.6 / 43.3 / 42.7 / 44.7 at
2017-2021, **56.9 at 2024 and 67.8 at 2025**. The coin-drawn decision set reproduces it
independently (0.40 pooled), so it is the world and not the set.

The whole book is in band (17-21% at 2017-2020), so the LEVEL is right and the SPLIT between routes
is not. The mechanism is named in `tools/fit_year_level_anchor.py::svt_composition_refusal`: *"the
whole-book fit holds the SVT contribution fixed and solves the renewal anchor around it."* The
renewal anchor (`departure_level_anchor.YEAR_LEVEL_ANCHOR`, 2.0x to 20.8x) is therefore the residual
between the published total and whatever the SVT route and the world's fixed-term share leave. No
published term-end figure constrains it.

## Why it is outside the record, on published figures only

Two bounds, neither an invented number:

1. **Arithmetic against the total (2024-2025).** Departures at a term end, over all accounts, cannot
   exceed all switching. Ofgem State of the Market (January 2026) puts the GB fixed-term share at
   about one third by July 2025 and half that a year earlier. At 2025, 1/3 x 0.678 = 22.6% of accounts
   against a published total of 10.4%. At 2024, 1/6 x 0.569 = 9.5% against 9.0%. Both exceed the
   total before a single SVT household has switched. The ceiling the record allows on P(leave | term
   end) is 0.104 / 0.333 = **0.31 at 2025** and 0.09 / 0.167 = **0.54 at 2024**, even if every
   switch came from a term-ender.
2. **Composition from the trials (2017-2021).** EFTC (Ofgem 2019, n = 19,553): 6% external
   switching in the **six weeks** around term end, in both arms. A household that does not leave then
   rolls to the default, and default-tariff households leave at about 1% a month (CMOL control, 1.0%
   over 30 days; CMOC control 2.9%). That composes to roughly 6% + 11 x 1-3% = **17-39% in the year**.
   The world's 43-45% at 2019-2021 is above the top of that. This is a rough composition of two
   published figures with different populations, NOT an established term-end rate: the record
   publishes no annual departure share for a term-ender, and that gap is the knowledge item.

2017-2018 (35.0, 28.6) sit inside the composed range and are not shown wrong.

## What this is not

- **Not the price response.** On the decision set, offering 5-40% below the default moves pooled
  P(leave) only from 0.40 to 0.33 (0.399 / 0.403 / 0.400 to 0.328 / 0.331 / 0.329 on seeds 42 / 101 /
  202). At 2025 a 40% cut still leaves 0.54 against the 0.31 ceiling in bound 1. No market fix
  closes the gap, so the level is not a default-vs-fix artefact.
- **Not the whole-book level.** That is fitted to the published record and is in band. Re-fitting
  the whole-book anchor does not fix this; it is the constraint the fit lacks.

## What would fix it (for the W2 lane, blind to company results)

Give the fit a second constraint: a term-end departure share bounded by the published record (the
ceiling in bound 1 per year, the EFTC six-week external share as a floor) so the residual can no
longer land wholly on the renewal route. Where it then cannot meet both the whole-book band and the
term-end bound, the remainder belongs to the SVT route or the world's fixed-term share, and that is
the next measurement, not a number to pick. Knowledge first: a published annual departure share for
GB term-enders (Ofgem RMI or the EFTC follow-up) would replace the composed range.

## Who reads the wrong number today

Every retention figure divides by the share leaving: the save-offer decision set
(`tools/grade_save_offer_shapes.py`), the B8 holdout grade, and any retention arm on a settled run.
The shape RANKING there is likely to survive (reactive save first); the LEVELS are not.

NEXT for W2: add the term-end bound to `tools/fit_year_level_anchor.py` as a refusal before any
re-fit, then re-capture and re-fit; this finding's bound 1 is the control.
