**Severity:** LATENT · **Lane:** W4_the_wall

**Rank:** backlog, ahead of the coal-and-interconnector build that EP13's L3 waits on — because
if this is what it looks like, that build improves the *intensity* side of a product whose
*consumption* side is the weaker half, and the ordering matters.

Found by the EP13 Expert Hour (2026-08-25, `expert_hour:EP13_adapter_carbon_intensity` in
`docs/observability/sanity_adjudication_ledger.json`) while back-solving a headline the blind
reviewer could not audit. The carbon findings from that pass are repaired. This one is not a
carbon defect at all, which is why it is filed separately rather than closed with them.

Not fixed on sight: SELF_INTERRUPT. Nothing is blocked on it, the supply of harness findings is
infinite, and the repair is a population question that belongs to whoever owns the half-hourly
consumption generator rather than to the atom that happened to multiply by it.

# Every carbon timing figure on Explore is intensity × a two-block consumption template, and the template is the same shape in three households, three years and both seasons

All claims `observed-with-evidence` unless labelled `inferred`.

## What the page publishes

The Explore carbon panels publish a per-household "timing effect": what the household's carbon
was, half hour by half hour, against what the same kWh would have been at the year's average
intensity. EP13's whole product is that number. It is a **product of two series** — the grid
shape, and the household's half-hourly consumption — and the Expert Hour spent all five of its
MAJOR findings on the first one.

The second one is this, read directly out of `site/data/explore_carbon.json` as served:

| account | date | kWh in the day |
|---|---|---|
| C7 | 2021-02-11 | 89.21 |
| C8 | 2022-12-15 | 86.99 |
| C9 | 2025-01-10 | 82.06 |
| C8 | 2016-07-24 | 9.93 |
| C9 | 2021-06-07 | 14.50 |

89 kWh in one day on a residential electricity account is roughly twelve times the UK average
day and would annualise to ~32,500 kWh. That alone is a tail case, not a defect — a large
electrically-heated home on a cold day can get there. The `profile` array underneath is the
finding.

## The shape, C7 on 2021-02-11, half hour by half hour

```
00:00-03:30   ~1.09 kWh each   (8 half hours)
04:00-05:30    0.075-0.09 kWh  (4 half hours)   <-- a 14x cliff, then
06:00-09:30   ~4.00-4.16 kWh   (8 half hours)   <-- ~8 kW flat
10:00-16:00   ~0.17-0.24 kWh   (13 half hours)
16:30-21:30   ~3.94-4.07 kWh   (11 half hours)  <-- ~8 kW flat again
22:00-23:30   ~0.15-0.25 kWh   (4 half hours)
```

Nineteen half hours at almost exactly 4 kWh carry ~77 of the day's 89 kWh. Between them the
house draws 150-500 W.

**C8 on 2022-12-15 and C9 on 2025-01-10 have the same structure**: near-zero baseline, a plateau
across periods 13-20, a plateau across periods 34-44, at 4.21-4.39 and 3.51-4.60 kWh
respectively. Three different households, three different winters, the same two windows, the
same plateau height to within 10%.

**C9's summer day (2021-06-07) is the same template scaled down** — the identical two blocks at
~0.41-0.51 kWh instead of ~4. The shape does not change with the season; only its magnitude does.

## Why it reads as an artefact rather than a household

Three things, in increasing order of how hard they are to explain away:

1. **The 04:00 cliff.** C7 draws ~1.09 kWh per half hour until 03:30, then 0.075 for four half
   hours, then 4.00 at 06:00. A house that is drawing 2.2 kW at 03:30 does not fall to 150 W at
   04:00 and rise to 8 kW at 06:00. Whatever is on at 3am is on at 4am.
2. **A flat 8 kW plateau.** Real half-hourly domestic demand is spiky — a kettle, an oven, a
   shower are each visible in a half hour. A plateau constant to ±2% across nine and a half
   hours is a load being *specified*, not measured.
3. **The plateau sits at the morning AND evening peak.** `inferred`: the only residential load
   that reaches 8 kW for hours is electric heating, and electric heating in GB is overwhelmingly
   storage heating on a restricted-hours meter, which charges **overnight** at the cheap rate.
   This profile does the opposite — it is off overnight and on at both system peaks.

## Why it matters here specifically, and why it is LATENT and not BLOCKING

The timing effect the page publishes is large *because* of this shape: 77 of 89 kWh land inside
the two windows the grid is dirtiest in, so the household necessarily scores as having drawn at
dirty times. The headline "108% more than the annual method reports" is then substantially a
property of the consumption template, not of the household — and the page attributes it to the
household in as many words ("**when** this household drew made its carbon 108% higher").

It is LATENT rather than BLOCKING on the honest reading of the ruling's own definition. The
published figure is not *wrong*: the arithmetic is correct, the kWh are the ones in the meter
file, and the page already says the days are chosen as the account's hardest. What is
unevidenced is the **attribution** — and one clause of copy, not a number, is what carries it.

It also cuts the other way and that belongs in the same paragraph rather than a footnote: the
EP13 Expert Hour refused L3 because the *grid* side's p95/p5 spread runs 3.6x wider than NESO's
by 2024. If the *consumption* side is a template, then the timing effect is a product of two
overstatements and the belief-vs-truth gap the page publishes is measuring the grid half of a
two-sided error. That does not make the gap wrong — it is still belief minus truth — but it
makes "close the grid model and the number is right" false.

## Where to look, and what would settle it

`site/data/explore_hh_days.json` is generated by `tools/generate_explore_hh_day.py`, which reads
each account's own half-hourly file and picks the day with the **highest total kWh** ("the
hardest winter day" — that selection is deliberate, documented, and not the issue). The template
is upstream of that generator, in whatever writes the per-account half-hourly series.
`inferred`: this pass did not open that producer, so no claim is made here about which module
builds the shape or whether it was ever meant to be more than a placeholder.

The smallest closed loop, in order:

1. **Name the producer** and read it. If the two-block template is an acknowledged simplification
   with a register entry, this finding closes as a duplicate and the page's attribution clause is
   the only repair.
2. **Check the 04:00 cliff against the producer's own intent.** It is the one feature that no
   design would choose on purpose, so it is the cheapest falsifier available: if the producer
   cannot explain it, the shape is not modelling anything.
3. **Population, not the five panels.** The page shows 6 measured household-days of 12. Whether
   the template is the whole book's half-hourly shape or only these accounts' is the difference
   between a copy fix and a world defect, and it is one query.
4. **Only then the copy.** If the shape stands, "when this household drew" becomes "when this
   household's profile has it drawing", which is both true and much less interesting — which is
   the correct outcome for a claim that turns out to rest on a template.

## What was NOT claimed

No claim that the consumption is *wrong*, that any published figure must be withdrawn, or that
the profile is unrealistic for every GB home — an 8 kW electrically-heated property exists. The
claim is narrower and is the one the evidence supports: **the shape is identical across three
households, three years and both seasons, and it contains a discontinuity at 04:00 that no
household behaviour produces.** A shape that does not vary between households is not a
measurement of households.
