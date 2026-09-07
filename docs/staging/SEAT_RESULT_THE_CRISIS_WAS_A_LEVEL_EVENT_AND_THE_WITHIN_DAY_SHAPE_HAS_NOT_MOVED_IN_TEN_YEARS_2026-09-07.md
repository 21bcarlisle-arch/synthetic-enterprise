**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# The crisis was a level event: the within-day shape has not moved in ten years, and what did move the faced ratio was the unit rate's composition

**Measured:** 2026-09-07, delivery seat.
**Claim:** `a49-does-the-2021-2023-episode-reach-the-evidence-range`
**Instruments:** `tools/tou_price_shape_episode.py`, `tools/ofgem_cap_unit_rate_composition.py`.
**Artefacts:** `docs/observability/tou_price_shape_by_episode.json`,
`docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json`.
**Pre-registration:** `docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_2021_2023_EPISODE_PUTS_THE_FACED_RATIO_INSIDE_THE_EVIDENCE_RANGE_2026-09-07.md`
— filed before either source was opened, graded line by line at the foot of this file.

**Supersedes** the "this does not retire the product, the panel just ends too early" hope in
`docs/market_research/domestic_shift_response_as_a_function_of_pass_through.md` (landed 8369a541e).
**Closes both of that file's two cheapest named gaps.**

---

## The question, and the answer

The landed shift-response work established the Arcturus 2.0 response function and then could not
locate the interior optimum, naming the reason precisely: **the price shape was too flat.** Median
within-day wholesale ratio 1.77:1, household facing 1.26:1 at full pass-through, against an
evidence base starting at 2:1 and an Ofgem statement that a factor of about three is needed. It
called its own panel possibly unrepresentative rather than decisive, because **the panel ends
2020-12 by construction** — before the gas crisis — and named testing 2021-2023 the highest-value
measurement it had.

**Measured. The answer is no, and the reason is much stronger than "we lacked the years".**

| episode | days | median ratio | p90 | s (median) | mean day price £/MWh | created £/hh-yr | faced @ α=1.0 | days ≥2:1 |
|---|---|---|---|---|---|---|---|---|
| 2016-2020 *(the landed panel)* | 1520 | **1.77** | 3.38 | 0.429 | 44.7 | 51.36 | 1.280 | 2.8% |
| **2021-2023** *(the question)* | 1078 | **1.79** | 3.71 | 0.572 | **135.9** | **178.59** | **1.400** | 9.9% |
| 2024-2025 *(the control)* | 731 | **1.70** | 6.67 | 0.559 | 75.6 | 106.93 | 1.342 | 14.6% |

The 2016-2020 row is **re-measured by the identical code path**, not quoted — 1520 days, 1483 with
a positive cheapest window, median 1.77, £51.36 per household-year. It reproduces the landed
artefact exactly, which is what licenses reading the other two rows against it.

## THE CRISIS WAS A LEVEL EVENT. THE SHAPE DID NOT MOVE.

This is the finding, and it is the trap the measurement was built around.

- The **level** of wholesale prices went up **3.0×** (£44.7 → £135.9/MWh).
- The **created value** a perfect time-of-use tariff could capture went up **3.5×** (£51.36 →
  £178.59 per household-year).
- The **within-day shape**, which is the only thing a time-of-use tariff actually sells, went from
  **1.77:1 to 1.79:1**. One per cent. Over the largest energy price shock in the record.

A ratio is scale-free: multiply every half hour of a day by three and dearest-over-cheapest does
not move. The crisis multiplied days, not shapes. **Ten years of GB half-hourly wholesale prices —
2016 through 2025, 3,329 whole days — never produce a median within-day ratio above 2.4:1, and the
two widest years (2016 at 2.37 and 2020 at 2.21) are the two *cheapest*, not the dearest.** 2022,
the dearest year in the record at £198/MWh, has a median ratio of 1.82.

## And what DID move the faced ratio was not the price at all

The faced ratio did improve, 1.280 → 1.400 at full pass-through. Two things changed at once, so it
cannot be attributed without the one-variable version. Run:

| | faced ratio, median, α = 1.0 |
|---|---|
| 2016-2020 shape, its own s = 0.429 | **1.2797** *(baseline)* |
| 2021-2023 shape, **old** s | **1.2812** ← the shape's whole contribution: **+0.0015** |
| 2016-2020 shape, **new** s | **1.3865** ← the commodity share's contribution: **+0.107** |
| 2021-2023 shape, its own s = 0.572 | **1.4001** *(measured)* |

**Essentially one hundred per cent of the improvement came from the commodity share of the unit
rate, and none of it from the wholesale price shape.** The crisis helped the tariff — by making
wholesale a bigger fraction of what a household is charged per kWh, not by making the day's prices
more different from each other.

**And that mechanism has already unwound.** `s` peaked at 0.81 in Jan-Mar 2023 and was back to 0.56
by Oct-Dec 2023. The one thing that moved the number in our favour was a transient.

## The prerequisite, closed: `s` is not a constant and was never 0.40

Read off Ofgem's own default tariff cap level model (v1.19), by the model's own construction —
benchmark-consumption allowance minus nil-consumption allowance, over benchmark kWh, per component.
The nil column *is* the standing charge, so this is Ofgem's decomposition, not an apportionment
invented here.

| cap period | s | unit rate p/kWh ex-VAT |
|---|---|---|
| Apr-Sep 2021 | 0.423 | 18.00 |
| Oct 2021-Mar 2022 | 0.478 | 19.78 |
| Apr-Sep 2022 | 0.627 | 26.94 |
| Oct-Dec 2022 | 0.761 | 49.25 |
| **Jan-Mar 2023** | **0.808** | 64.14 |
| Apr-Jun 2023 | 0.739 | 47.91 |
| Jul-Sep 2023 | 0.572 | 28.54 |
| Oct-Dec 2023 | 0.560 | 25.96 |

**The landed bridge's best-supported row was s = 0.40 — below every value the law has carried in
every period the cap has been in force** (minimum 0.408). The direction is exactly the one that
finding predicted from the denominators, so its reasoning was right and only its number was low.
`s` is **not a scalar**: 0.41 to 0.81. Any caller citing one value must name the cap period.

**The decomposition is corroborated, not asserted.** Derived unit rate × 1.05 VAT reproduces the
published including-VAT cap levels across **13 periods, worst error 1.34%** — 19.78p → 20.77 against
a published 20.8p; 26.94p → 28.29 against 28.34p. That cross-check **fails closed**: if it missed by
more than 2% the tool refuses to publish anything under it.

One honesty correction caught in the build: Ofgem's model also carries pre-2019 columns it labels
*"for illustration only"* — a cap level for periods in which no cap existed. **Several fall below
0.40** (0.370 in Oct 2016). Reading those as cap periods would have made the "always above 0.40"
claim false in the flattering direction. They are published, flagged `cap_in_force: false`, and
excluded from the headline.

## What this does and does not retire

**It does not retire the time-of-use product**, and the reason is not politeness. Created value per
household-year is £178.59 on the 2021-2023 panel and £106.93 on 2024-2025 — against £51.36 on the
landed panel. **The ceiling got substantially bigger.** Company value at the argmax pass-through
rises from £0.61 to £2.35 per household-year (opt-in) and from £0.04 to £0.32 (opt-out).

**But the shape of the problem is unchanged and now much better evidenced.** Every faced ratio in
every episode, at every pass-through, sits **below 2:1 at the median** — outside the range over
which every published response was estimated. The optimum's location is still not established
(argmax α 0.285 opt-in vs 0.70 opt-out — a factor of 2.5, narrowed from the landed 8× only because
`s` is now measured rather than gridded). And the level is still pounds against a ceiling of
hundreds.

**The binding constraint was never which years we held.** It is that GB within-day wholesale spreads
are, and have been for a decade, roughly half of what the domestic shift-response literature needs
to say anything — and retail dilution then halves that again. The landed finding's conclusion
stands; what changes is that it is no longer provisional on a panel that stopped too early.

**An artefact found by the controls and pinned rather than smoothed.** The Arcturus primary
specification's constant is −0.011, so **at a ratio of exactly 1:1 the arc returns a 1.1% peak
reduction** — a household shown no price difference at all. That is a regression intercept fitted
over a sample that starts at 2:1, not a claim that flat pricing moves load. It means the **opt-in**
column has a floor it did not earn: company value at zero pass-through is £1.96/household-year on
the 2021-2023 panel, which is the intercept and not a response. The measured argmax (£2.345 at
α = 0.285) is still strictly above it, so the interior optimum survives — but the opt-in numbers
should be read as *intercept plus response*, and the **opt-out** column, which clips to zero at 1:1
(−0.028 + 0.039 = +0.011), is the cleaner one. Both are pinned by controls so neither drifts
unnoticed. *(This was not in the pre-registration. I did not predict it and it was found by writing
the test, not by reading the formula.)*

**One forward-looking signal, recorded and not built on.** 2024-2025 has the *flattest* median of
any period (1.70) and by far the *fattest* tail (p90 6.67, against 3.38 on the landed panel), and
the highest share of days clearing 2:1 at full pass-through (14.6%). The distribution is becoming
more skewed — many flat days plus a few extreme ones, which is the renewables-and-scarcity
signature. **A tariff that pays only on the extreme days is a different product from one that pays
every day**, and nothing here measures it. That is the next question, and it is not this one.

---

## Predictions, graded

Filed before either source was opened. Nine of nineteen refuted.

**On `s`:**
- **P1a** — `s` above 0.40 in every in-force cap period. **CONFIRMED** (min 0.408).
- **P1b** — 2021 H1 lands in 0.45–0.60. **REFUTED.** 0.423, below the range.
- **P1c** — crisis periods above 0.65. **CONFIRMED for Oct 2022–Jun 2023** (0.76, 0.81, 0.74).
  **Partially refuted:** Apr-Sep 2022 is 0.627, just under; Jul 2023 onward falls back to 0.57.
- **P1d** — `s` is not a constant and needs a range keyed to the cap period. **CONFIRMED**, and
  more strongly than expected: a factor of two, 0.41 to 0.81.

**On the price shape:**
- **P2a** — the level rises severalfold and is not the measurement. **CONFIRMED** (3.0×). Naming it
  in advance is what made the attribution below legible rather than a surprise.
- **P2b** — median ratio widens to 1.9–2.3. **REFUTED.** 1.79. It did not widen at all.
- **P2c** — the median clears 2:1 raw. **REFUTED.**
- **P2d** — p90 above 4.5. **REFUTED** for 2021-2023 (3.71). Would have been **confirmed** had I
  named 2024-2025 (6.67) — the tail did fatten, three years later than I predicted.
- **P2e** — 2022 is the widest of the three. **REFUTED.** 2021 is (1.84), then 2022 (1.82), then
  2023 (1.73). The dearest year was not the widest.

**On the faced ratio and the arc:**
- **P3a** — median faced ratio still below 2:1, in 1.5–1.9. **Direction CONFIRMED, magnitude
  REFUTED.** 1.400, below my range. I predicted the right answer for a reason that was too generous
  by a third.
- **P3b** — days clearing 2:1 rises to 0.15–0.40. **REFUTED.** 0.099.
- **P3c** — opt-out response at the argmax stays under 3%. **CONFIRMED** (0.60%).
- **P3d** — company value rises by more than an order of magnitude and stays under £10.
  **REFUTED on the first clause, confirmed on the second.** £0.038 → £0.321 opt-out is 8.4×;
  £0.608 → £2.345 opt-in is 3.9×. Both under £10.
- **P3e** — argmax α stays unstable, narrowing by less than half. **CONFIRMED**, though for a
  reason I did not name: the narrowing (8× → 2.5×) came from *measuring* `s` rather than gridding
  it, not from the new panel.

**On what it would not settle:**
- **P4a / P4b** — persistence and shiftable share untouched. **CONFIRMED**; both still open, both
  still multiply.
- **P4c** — 2021-2023 is an episode, not a forecast, and I would have to say so on the artefact.
  **CONFIRMED**, and it became more important than predicted: the one mechanism that helped is the
  one that has already unwound.

**The prediction I most wish I had filed and did not:** that the shape would not move *at all*. I
predicted a modest widening and got none. Having pre-committed to separating level from amplitude,
I still expected amplitude to move — which is the same instinct that makes a level event look like
a mechanism.

---

## What is next

1. **`s` is now established and the landed bridge understates every figure it prints.** The arc
   artefact's grid and its optimum table are keyed to s ∈ {0.30, 0.40, 0.55, 1.00} with 0.40 called
   best-supported. That row is now known to be below the floor. Updated in place by this work.
2. **The skew, not the spread, is the live question.** 2024-2025's p90 of 6.67 against a median of
   1.70 is the shape a tariff might actually be sellable against, and no instrument here measures a
   product that pays only on extreme days. **This is the highest-value measurement now named.**
3. **Shiftable share (R3's gap) still multiplies everything** and is untouched.
4. The MID caches for 2021-2025 are gitignored source data fetched into this worktree. Both
   instruments **fail closed** when they are absent rather than reporting a flat market.

## Reproduce

```
python3 -m tools.ofgem_cap_unit_rate_composition   # -> docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json
python3 -m tools.tou_price_shape_episode           # -> docs/observability/tou_price_shape_by_episode.json
```
