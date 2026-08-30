# What an anchor means beyond the record

**Date:** 2026-08-30. **Author:** the delivery seat. **Status:** REGISTERED — a choice for the
director, framed with a recommendation, before the generative-futures work starts.
**Occasion:** director, 2026-08-30: *"I want the world to run past the ten years of real history —
the generative futures capability the model page already claims and nothing has drawn on. Before it
starts, settle one thing: every calibration landed this week is anchored to the record, so once the
world runs past 2025 there is nothing to be inside the band of, and the guard you just rebuilt
loses its subject … Those are different projects and I'd rather choose than drift."*

---

## The premise was worse than stated, and it is measured rather than argued

The concern was that past 2025 there is nothing to be inside the band of. True. But the world does
not become *unanchored* past 2025 — **it becomes frozen**, and it does so silently.

```
year   market_switching_multiplier   market_departure_rate_pct   year_level_anchor
2024                          1.000                       16.1            1.000  (reference)
2025                          1.112                       17.9            2.119
2026                          1.114                      17.93            3.021
2030                          1.114                      17.93            3.021
2040                          1.114                      17.93            3.021
```

Every year after the record returns **the same numbers, forever**. Not a distribution, not a drift,
not a scenario — a constant.

### And a claim of mine in this document's first draft, withdrawn on the numbers

I wrote that the level anchor "jumps from 2.119 to 3.021 at the 2025/2026 boundary, a **43% step**",
called it a defect under any route, and said I would repair it without asking. **Then I printed the
table, and it does not survive:**

```
2016 4.5973   2017 4.2569   2018 3.3458   2019 3.2281   2020 4.4257
2021 3.2199   2022 1.5241   2023 2.0915   2024 3.0208   2025 2.1186
```

The anchor swings **1.52 to 4.60 inside the record**. 2021→2022 falls 53%, 2022→2023 rises 37%,
2023→2024 rises 44%. A 43% move at the boundary is *smaller than three moves the record itself
contains*, so it is not a discontinuity — it is this table's ordinary behaviour. And the fallback
reaches for 2024 because 2024 is the last **complete** year and the year
`market_switching_multiplier` is normalised to; 2025 is a five-month partial year and is the worse
candidate to carry forward, not the better one. The module's stated argument holds and I had not
read it carefully enough before proposing to overrule it.

Kept here rather than deleted, because a wrong claim beside its refutation is the evidence the check
was made. What survives is the freeze, which is the part that matters.

**So the prize the director named does not currently exist.** *"A generated world is the first place
the company's predictions meet something the model wasn't fitted against"* — but a company
predicting a constant meets a constant. Its churn belief would be trivially right, its concordance
would clear a null that means nothing, and the measured "skill" would be an artefact of a world with
no variance to predict. Under the standing rule
(`INDEPENDENCE_IS_NOT_INFERENCE_2026-08-30.md`) that is not evidence of anything, and the page would
have to say so.

**This is the strongest argument for doing the work, not against it.** The capability is claimed on
the model page and what stands behind it is a flat line.

---

## The two projects, as the director framed them

### A — The generator preserves the statistical shape; we validate shape, not level

The anchor stops being *a value the world must land on* and becomes *a process whose properties the
world must reproduce*: distribution, volatility, autocorrelation, cross-correlation with weather and
wholesale prices, regime-switching frequency and persistence. A generated 2027 is valid if a
statistician handed 2016–2035 could not tell which decade was measured.

**What it buys.** The world stays lawful past the record, so a company prediction meeting it is
meeting something genuinely unseen but not arbitrary. That is the only version in which the prize is
real: an unlawful future can be predicted badly by a good model and well by a lucky one, and nothing
distinguishes them.

**What it costs, and this is the binding constraint.** Shape validation needs enough observations to
estimate a shape. This project's series do not have a uniform amount:

| anchored series | observations in the record | shape-validatable? |
|---|---|---|
| GB domestic switching rate | **10** (annual, 2016–2025) | **No** |
| `MARKET_SAVINGS_BY_YEAR` | **10** (annual) | **No** |
| SVT / cap rate series | ~26 (quarterly from 2019) | Marginal |
| grid intensity feed | ~1,300 | Yes |
| half-hourly settlement, prices, weather | ~10⁵ | Yes |

Ten annual points cannot support a claim about autocorrelation or regime persistence. This is the
same wall as `INSTRUMENT_RESOLUTION` — 17 binary decisions put a 5.9pp floor under a measurement, and
no amount of care beats the arithmetic. **An honest version of A therefore cannot be uniform**, and
a version that pretends it is would be publishing a shape claim estimated on ten points.

### B — The future is honestly unanchored and carries that as a permanent caveat

Every figure computed past 2025 is labelled a scenario, never a measurement. No validation is
claimed because none is possible.

**What it buys.** It is unfalsifiable in the good sense — it makes no claim that can be wrong — and
it is cheap.

**What it costs.** It forfeits the prize. If nothing says the generated world is lawful, then a
company prediction meeting it says nothing about the company. B is a stress-testing instrument, not
an epistemics instrument, and the director's stated reason for wanting the capability is the second.

### C — the one that happens if nobody chooses

The current behaviour: the last fitted values are frozen and carried forward silently, the guard
loses its subject and returns a refusal nobody reads, and figures computed in a constant world are
published beside figures computed in the real one with no marker between them. **This is the drift
the director said he would rather choose than have.** It is also today's state, so "do nothing" is
not neutral.

---

## Recommendation: A at high frequency, B at low, and the boundary stated on every figure

Not a compromise — the frequencies are genuinely different problems and one answer for both would be
wrong for one of them.

1. **High-frequency generators (prices, demand, weather, grid intensity) take route A.** Thousands of
   observations support a real shape test. This is where the interesting futures live anyway —
   negative prices, dunkelflaute, bimodal price distributions at high renewable share are all
   half-hourly phenomena, and they are what the R&D findings already point at.
2. **The annual behavioural calibrations (switching rate, savings, the level anchor) take route B**,
   because ten points cannot support anything else. Past 2025 they are **declared constant and
   declared unvalidated**, which is what they already are — the change is that it becomes visible
   instead of silent.
3. **The 2025/2026 boundary becomes a first-class fact on every artefact**, the way `data_regime`
   already marks historical from synthetic. A figure whose window crosses it says so. A figure
   computed wholly past it is a scenario and is never quoted beside a measurement without that word.
4. **The co-calibration guard keeps its subject by keeping its window.** It compares each side's
   table against the record over the years the record covers, and past 2025 it has no opinion —
   which under its own fail-closed rule is a refusal, correctly. It does not need changing; it needs
   the boundary marker so a reader knows why it went quiet.
5. ~~**Fix the 43% step regardless of the route chosen.**~~ **Withdrawn** — see the correction
   above. The move is within the table's own range and the fallback's choice of the last complete
   year is the right one. What replaces it: **2025's anchor is fitted on five months of record and
   is carried into every figure that quotes it**, which is a live question inside the window and
   not a boundary question at all. It belongs with C1b's owed re-fit, where the table is being
   re-derived anyway.

**Why this and not pure A:** because pure A would require me to publish a shape claim about the
switching series estimated on ten annual points, and the first thing anyone competent would ask is
how many points. **Why this and not pure B:** because it throws away the prize on the series where
the prize is actually available, and half-hourly is where this world's most interesting untested
dynamics are.

## What is the director's and what is mine

**His:** which route, and whether the generated window is 5 years or 20 — a curriculum value in the
sense he reserved (how long the window runs).

**Mine, and I will do these without asking:** making the 2025/2026 boundary visible on artefacts,
and ensuring nothing published quotes a post-2025 figure beside a measured one without the marker.
Both are corrections and neither flatters us — a visible boundary makes our figures look more
provisional, not less. (The third item here was the boundary step, and it is withdrawn above.)

---

*Registered before the work, as instructed. Nothing here has been built.*
