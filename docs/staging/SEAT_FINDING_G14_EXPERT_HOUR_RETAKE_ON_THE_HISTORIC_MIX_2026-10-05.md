**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `G14_half_hourly_grid_carbon_intensity_aligned_to_settlement` · **Claim:** `g14-expert-hour-retake-on-the-historic-mix`

# G14 Expert Hour re-take on the historic mix: the page lagged the code; fixed, and a second re-take finds no MAJOR

At draw time the duplicate-work note named this same id as already held. The holder was this
invocation (the executor's own pid). Nothing else on G14 was running.

## The re-take

This was a fresh-context cold-eyes pass with a veteran GB grid-carbon persona, priors written
first. The reviewer was fed `done/SEAT_FINDING_G14_REBASED_ON_NESO_HISTORIC_GENERATION_MIX_2026-10-05.md`
and the earlier FAIL (`done/SEAT_FINDING_G14_NESOS_2020_04_28_LEVEL_STEP_2026-10-05.md`), and measured
the shipped artefacts. As the cold-eyes protocol says, this is blindness, not independence.

- **MAJOR-2 (basis step) is resolved.** The fuel-mix arithmetic over the shipped history, taking
  28 days either side of 2020-04-27, reads 1.0407 → 1.0456 (+0.5%). Placebo cuts move about the
  same amount: 2019-04-27 gives +1.0% and 2021-04-27 gives +1.3%. 20 gaps in 175,324 values.
- **MAJOR-1 was resolved in the code but still live on the page.** Both published files,
  `docs/market_data/grid_intensity_feed.json` and `site/data/explore_carbon.json`, were generated
  at 09:12 and 09:13, before the last label edits in `cd30ba424`. Explore still read "loss-corrected
  to a consumption basis" and "demand-weighted over the year, loss-corrected". Both
  `versus_published.source` strings still read "Consumption basis: LOSS-CORRECTED … at the exporting
  country's intensity". I confirmed this by grep before acting. The existing controls read the
  Python constants, which is how it passed.
- **MINOR (new): the API has a second regime change.** Monthly API/historic runs 1.02-1.06 from
  2020-05 to 2021-04, then 1.00-1.01 from 2021-05. A cut at 2021-04-27 steps -3.4%. That explains
  the "2020-05..12 at 1.045" MINOR, as a step rather than an anomaly. In 2025 the monthly ratio
  swings 0.95-1.075, so "agrees within about 2%" holds for annual sums only. The API is the
  cross-check, not the series, so this does not block.
- **MINOR (new): ~990 half hours inside 2016-03..2025-06-07 are absent from the feed and not
  named.** They are INDO demand holes; only 20 are history gaps.
- **MINOR (open):**
  - The feed ends 2025-06-07 and gives annual levels for 2017-2024 only, because of INDO weighting.
    A "2016-2025" claim needs restating, or FUELHH demand weighting.
  - The futures `level_error` is 11.6 g in-sample, against a rolling-origin annual bias of -37.7 to
    +25.8 g. This blocks a futures L3, not the history.
  - CO2 is carried under a `co2e` name.
  - Import factors are fixed.
- **MINOR (moot):** the `fuelmix_fill` reaches no published value. It is still biased about ±9 g.
- **Held up:**
  - the rebase conditions: the edition caveat, the embedded generation and imports treatment
    measured, and the 1.1287 scale gone;
  - the code's basis constants;
  - 34 tests pass.

## Fixed in this landing

- Regenerated both artefacts from the current code. Only the label strings and timestamps changed;
  no number moved.
- `tests/tools/test_grid_intensity_feed_and_explore_carbon.py::test_the_SHIPPED_files_carry_the_basis_text_the_code_now_holds`
  compares the shipped strings with the constants that own them. It also refuses "loss-corrected" or
  "consumption basis" anywhere in either file. Mutation: red against each pre-fix file separately,
  green on the regenerated pair.
- `trust_ledger.json`: the re-take is recorded as `needs_work`. The map row's `expert_hour` carries
  this verdict.

## Second re-take, on the regenerated files (same persona, fresh context, priors first)

**No MAJOR on the files this landing carries.** It read HEAD as well as the working tree, and its one
MAJOR was that the regenerated pair was not yet committed. It closes when this lands. "On the
working-tree files alone, I find no MAJOR."

Its checks:

- It swept every string in both JSON files: there is no loss-corrected, consumption or
  delivered-basis wording except inside the losses-not-included gap. Every owning constant ships
  verbatim.
- No step at 2020-04-27 on the history, tested two ways:

  | Test | At 2020-04-27 | Placebo cuts |
  |---|---|---|
  | History ÷ FUELHH recomputation | -0.45% | -1.8% to +1.3% (six cuts) |
  | Raw level | -8.2% | -10.5% to +35.7% |

- Time-weighted annual means for 2016-2024 (273.8 … 124.0 g) all sit inside its stated priors. The
  demand-weighted published levels run 5-6% above them, as the weighting text says.
- 20 gaps out of 175,344 values. NESO's factor table matches.
- 2017 kWh × level reproduces the published kg.
- Futures are not presented anywhere on the page.

Its new MINORs:

- **Partial-year panels are labelled as "the year" (it says this must be fixed).** Day panels use
  `allow_partial=True`, so the 2025-01-10 panel's "year's average" is the 1 Jan to 7 Jun mean,
  about 6% above the full year, and "Across 2025 as a whole" quotes 7,582 half hours. The timed kg
  is still NESO's value; only the comparator's label is wrong. Handed on.
- `site/data/proof.json` and `site/data/simplified.json` still quote "already loss-corrected" and
  "consumption basis counts imports at the exporting country's intensity". The source is the
  2026-08-14 log entry in `docs/design/simplifications/archive/EP13_adapter_carbon_intensity.001.yaml`,
  a dated record of a parked atom's reasoning. It is wrong since 2020-04-27 P34, but it is history,
  not a label on G14's series. Left as is.
- The `source` headline says FUELHH "fills", but `fuelmix_fill` reaches no value in any year. The
  named gaps say so.
- It counted 868 INDO-hole half hours absent from the feed in 2017-2024. They do not move the
  levels.

All the earlier MINORs are graded non-blocking. The futures `level_error` blocks only a futures
claim, and no page makes one.

**Disposition.** The Expert Hour bar for L3, no MAJOR gaps or flaws, holds for the landed files, and
the map row records `expert_hour: passed`. **The level is NOT moved.** The director's open question
`no-atom-can-reach-l3-while-an` asks whether a same-model pass, which is blindness and not
independence, can carry L3. `DIRECTION.yaml` already says that ruling holds G14 too. G14 is now in
H45's exact position: every question closed except independence. His ruling moves both, and a
level recorded ahead of it would decide his question for him.

**Correction to `done/SEAT_FINDING_G14_REBASED_ON_NESO_HISTORIC_GENERATION_MIX_2026-10-05.md`.** That
finding said whether household figures add losses was "raised to the director with a
recommendation". It was not: `for_the_director` had no such row. It is raised now as
`a-household-s-electricity-carbon-is-shown`. The recommendation is a separate named line at
DESNZ's T&D factor, never folded into NESO's series. The claim is marked beside it.
