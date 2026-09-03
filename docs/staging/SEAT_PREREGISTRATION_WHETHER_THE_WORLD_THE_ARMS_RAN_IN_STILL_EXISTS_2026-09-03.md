**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `value_cycle_ab`

# Whether the world the three value arms ran in still exists, and which way it moved

*Delivery seat, 2026-09-03, lane-0, claim `the-baseline-was-beaten-in-a-world-that-no-longer-exists`.
Filed BEFORE the anchor-swap table of act (a) was run, before any re-run of the arms, and before any
edit to the published page. §1 is read off the tree and off the artefacts' own provenance columns —
nothing in §1 is a prediction. §2 and §3 are.*

---

## 1. The state this starts from, read off the artefacts, not predicted

The three published value-arm artefacts and the commit each one's own `producing_commit` block names:

| artefact | `generated_at` | `producing_commit` |
|---|---|---|
| `value_cycle_ab_s1_three_arm.json` | 2026-08-31T03:47:57Z | `fe4df178b` |
| `value_cycle_ab_s1_noise_floor.json` | 2026-08-31T07:05:53Z | `4240e1478` |
| `value_cycle_ab_floor_decomposition.json` | (last written 2026-08-30) | — |

`git show` of `simulation/departure_level_anchor.py` at BOTH producing commits returns the same
ten-year block. That block, and the block live at `ace28fa44` today, are:

| year | anchor the arms ran under | anchor live today | live is FITTED or DECLARED |
|---|---|---|---|
| 2016 | 4.597312 | 4.259915 | declared (outside fit window → reference year) |
| 2017 | 4.256902 | 7.372584 | fitted |
| 2018 | 3.345826 | 2.945347 | fitted |
| 2019 | 3.228064 | 6.637286 | fitted |
| 2020 | 4.425742 | 6.359296 | fitted |
| 2021 | 3.219914 | 5.641346 | fitted |
| 2022 | 1.524110 | 1.000000 | declared (`NO_LEVEL_CORRECTION`, unidentified) |
| 2023 | 2.091517 | 2.033232 | fitted |
| 2024 | 3.020806 | 4.259915 | fitted |
| 2025 | 2.118624 | 4.259915 | declared (outside fit window → reference year) |

**Six of the ten anchors rose, four fell.** The rises are large (2019 +106%, 2021 +75%, 2017 +73%,
2020 +44%, 2024 +41%, 2025 +101%); the falls are small except 2022 (−34%, and 2022 is the year the
anchor multiplies nothing — see `UNFITTED_YEARS[2022]`).

**The drawn direction's stated premise is the opposite of this.** It says: *"The world got easier to
hold — fewer departures on the renewal route than the old anchor produced — so there is less book to
re-win."* The anchor block's own docstring, written by the pass that produced it, says:
*"AND THE NET MOVE IS UPWARD… this pass makes the book HARDER to hold, not easier."* This is the
**second consecutive Lane 0 direction to carry this premise**; the first was refuted in
`SEAT_PREREGISTRATION_WHAT_THE_SECOND_REFIT_PASS_ON_C5_MUST_MOVE_2026-09-03.md` §2 P2, where the
cause was identified: the premise is read off the **renewal-route** table, which is 7-of-7 out and
high, while the **whole book** is the comparable quantity. I am recording it here before measuring
so that the table below cannot be read as having been steered.

### The units problem in the drawn decision rule, stated before it bites

The direction's stop rule is: *"If the years the arms span moved by less than the seed spread the
floor artefact already measures — `stdev_gbp` **2291.07** on `value_advantage_gbp` … then say so
plainly."* Those spreads are in **GBP on an advantage**. The act (a) table is in **percentage points
of whole-book expected departure**. There is no bridge between them that does not require the re-run
the rule exists to decide on — pp of departure → accounts lost → margin at risk is exactly the chain
the arms compute. So the rule as written cannot be applied literally, and I will not manufacture a
conversion factor to make it look as though it was. What I will decide on instead is stated as D1
below, and it is declared here, before the number.

**D1 — the decision rule I am actually using.** Re-run if the whole-book expected departure rate
moves, in the years the arms span, by an amount that is large *relative to the departure level
itself* — concretely, if the mean absolute per-year move across 2017–2024 exceeds **1.0pp**, or if
any single year moves by more than **2.0pp**. Rationale: the published bands themselves are
0.5–3.6pp wide, and `union_by_year`'s own docstring puts one year's realised binomial noise at ~5pp
on ~50 accounts while noting `expected_rate_pct` is the model-free level and carries none of it. A
move of that order is a different world by the band's own resolution. Below it, the honest act is a
dated provenance line.

---

## 2. The predictions for act (a) — the anchor-swap table

Measured on ONE population (`docs/reports/c4_whole_book_departure_factors.json` + its SVT sibling —
the capture taken under the ten-year block, i.e. the world the arms ran in), recomputing every
renewal row's departure probability at the old anchor and at the live anchor and leaving everything
else identical. One variable.

### P-A1 — direction

**The world got HARDER to hold, not easier.** Whole-book expected departure under the live anchor is
HIGHER than under the anchor the arms ran under, in a majority of 2017–2024, and higher in aggregate
across the window.
**Refuted by:** the aggregate 2017–2024 expected-departure move being ≤ 0, or by a majority of years
falling.

### P-A2 — size

The aggregate move across 2017–2024 is **between +1pp and +6pp of expected departures summed over the
window** (mean +0.15 to +0.75pp/yr), and it is SUBLINEAR in the anchor: the anchors rose 41–106% in
five years, but every hazard is clipped and the union is `1 − PROD(1−h)`, so a 2x anchor does not
double the year's rate. Largest single-year rise: **2019** (largest anchor rise, +106%). Largest
fall: **2022** (only year whose anchor fell materially).
**Refuted by:** the aggregate landing outside [+1pp, +6pp]; separately graded, by 2019 not being the
largest riser or 2022 not being the largest faller.

### P-A3 — 2022 does not move at all

2022's anchor fell 1.524110 → 1.0, but `UNFITTED_YEARS[2022]` states the year is 100%
crisis-forced-passive, every roll is diverted to the SVT segment table, and the SVT route's three
anchor-multiplied hazards are all built at 0.0. So **2022's expected rate is expected to be
IDENTICAL to six decimals under both anchors** — the anchor multiplies nothing there.
**Refuted by:** any movement in 2022's expected rate. If it moves, `UNFITTED_YEARS[2022]`'s stated
cause is wrong and that is a finding about the anchor block, not about the arms.

### P-A4 — the decision D1 resolves to RE-RUN

Given P-A1 and P-A2, I expect D1 to trip and the honest act to be a re-run rather than a provenance
line. **I am recording this because it is the self-serving answer** — a re-run is more work and more
visible work than a dated footnote, and a seat that predicts "re-run" and then measures its way to
"re-run" should be checked. If P-A2's aggregate lands below +1pp with no year over 2.0pp, the
provenance line is the whole of the work and I will land that and stop.
**Refuted by:** measuring a move that trips D1 but is driven entirely by years the arms' window does
not span.

---

## 3. The prediction for act (c) — what the re-run must show, if it happens

Filed now rather than after act (a), so that no part of it can be written with the table in hand.

### P-C1 — direction of the advantage

**More departures means MORE book to re-win, not less.** The per-customer arm acts on renewal
decisions; a harder-to-hold world puts more accounts through a decision the arm can price. So the
naive expectation from the drawn direction ("less book to re-win → advantage shrinks") is expected
to be **wrong in its premise**. But the sign of the effect on `value_advantage_gbp` is **NOT
predicted to be positive** either, and this is the part that matters: the control arm also keeps
more of nothing, and the published `value_advantage_gbp` of **£12,071.08** already sits inside a
seed spread of **±£2,291.07 at n=3** — a 5.3:1 signal-to-spread that is the only reason the headline
is publishable at all.

**What I predict: `value_advantage_gbp` moves by more than one seed-spread (>£2,291) and I do not
predict its sign.** Saying "it shrinks" would be a guess dressed as a prediction; the honest
pre-registration is that the magnitude of the change is material and the direction is genuinely
unknown to me.
**Refuted by:** `value_advantage_gbp` moving by less than £2,291.07 from £12,071.08.

### P-C2 — the flattering-result trap detector

**Any re-run in which `value_advantage_gbp` RISES and `selection_gbp` also rises is a defect in the
re-run until proven otherwise, not a win.** The world moved against the company on the baseline side;
a change that improves both the headline advantage AND the selection residual, simultaneously, in a
world that got harder, is the signature of an arm accidentally re-scored against a floor from the
other world — the exact defect `c30b98048` was filed for on 2026-08-31. First thing to check if it
fires: that the noise floor and the decomposition were re-run on the SAME anchor block as the
headline arm, by diffing their `producing_commit` fields.
**Fires on:** both figures rising. **Discharged by:** all three artefacts naming one producing commit
whose anchor block equals the live one.

### P-C3 — the floor widens

The floor legs re-run in a harder world will have a **wider** `stdev_gbp` on `selection_gbp` than
**3776.27**, because more accounts reach a priced decision and the priced side already carries
**99.99999%** of the variance (`priced_share_of_variance` in the decomposition). More priced
decisions at 3 seeds is more variance in the published figure, not less, until n rises.
**Refuted by:** `selection_gbp` stdev falling below 3776.27 with priced decisions unchanged or higher.

---

## 4. What must NOT happen, and how it is checked

- **The old figures are not deleted.** `git status --porcelain` on `docs/observability/` after this
  work must show no deletion of `value_cycle_ab_s1_three_arm.json`,
  `value_cycle_ab_s1_noise_floor.json` or `value_cycle_ab_floor_decomposition.json`. Superseded-with-
  provenance is the correction; deletion is not. Checked by pasting the porcelain output into the
  grading section, not by recalling my own behaviour.
- **No headline is re-run against a floor from the other world.** If act (b) runs, all three
  artefacts must carry one producing commit.
- **This file is graded beside itself.** Every prediction above gets a verdict written under it in
  this same file, with the refutation kept where it was refuted.

---

## 5. Grading

### Act (a), graded 2026-09-03, immediately after the run and before any further work

The anchor-swap table, one variable, on `c4_whole_book_departure_factors.json` + its SVT sibling —
the capture taken under the block the arms ran under. Renewal rows recomputed at each anchor; SVT
rows carry their own recorded probability.

| year | acc | ren | svt | band % | OLD exp % | NEW exp % | move pp | ratio |
|---|---|---|---|---|---|---|---|---|
| 2016 | 3 | 1 | 2 | 17.0–17.6 | 5.748 | 5.351 | −0.397 | 0.931 *(partial, excluded)* |
| 2017 | 57 | 20 | 116 | 13.5–14.0 | 10.764 | 14.128 | **+3.365** | 1.313 |
| 2018 | 55 | 21 | 144 | 19.5–20.0 | 20.268 | 19.150 | −1.118 | 0.945 |
| 2019 | 45 | 16 | 122 | 20.7–21.3 | 17.510 | 23.735 | **+6.225** | 1.356 |
| 2020 | 51 | 18 | 137 | 22.5–23.0 | 20.945 | 24.531 | **+3.586** | 1.171 |
| 2021 | 55 | 23 | 153 | 17.9–18.4 | 14.541 | 19.071 | **+4.530** | 1.312 |
| 2022 | 55 | 0 | 213 | 2.9–4.3 | 2.536 | 2.536 | **+0.000** | 1.000 |
| 2023 | 57 | 20 | 210 | 8.9–12.5 | 12.599 | 12.445 | −0.154 | 0.988 |
| 2024 | 62 | 19 | 181 | 12.5–16.1 | 13.765 | 16.389 | **+2.624** | 1.191 |
| 2025 | 57 | 18 | 95 | 14.3–17.9 | 10.400 | 16.392 | +5.992 | 1.576 *(partial, excluded)* |

**Window 2017–2024: OLD sum 112.926pp → NEW sum 131.985pp. Aggregate move +19.058pp.**
Mean per-year +2.3823pp; **mean absolute 2.7002pp**; max |move| **6.225pp** at 2019.
Rose: 2017, 2019, 2020, 2021, 2024. Fell: 2018, 2023. Unmoved: 2022.

**P-A1 — CONFIRMED.** The world got HARDER to hold. Five of eight years rose, aggregate +19.06pp.
**The drawn direction's premise is refuted**: it says *"the world got easier to hold — fewer
departures on the renewal route than the old anchor produced — so there is less book to re-win."*
Every fitted year but two moved the other way. This is the **second consecutive** Lane 0 direction
to carry this premise, and the cause is the one already identified in the C5 pre-registration: the
premise is read off the renewal-route table, and the whole book is the comparable quantity.

**P-A2 — REFUTED on size, CONFIRMED on the largest riser, REFUTED on the largest faller.**
I predicted an aggregate of **+1pp to +6pp**; it is **+19.06pp**, more than 3x the top of my band.
My reasoning for the band was that hazard clipping and `1 − PROD(1−h)` would damp a 41–106% anchor
rise heavily. The ratio column says how wrong that was: the year-on-year ratios run 1.17–1.36, so
the response is damped but nothing like as hard as I assumed — a 73% anchor rise at 2017 still
delivers a 31% rate rise. **I was directionally right and quantitatively wrong, and the error was
in the flattering direction for the "no re-run needed" branch**, which is the branch I would have
had to argue for had the number come in small. 2019 IS the largest riser as predicted. 2022 is NOT
the largest faller — 2018 is (−1.118pp) — because 2022 does not move at all, which is P-A3.

**P-A2 and P-A3 were mutually inconsistent and I did not notice when filing.** P-A2 named 2022 as
the largest faller on the strength of its anchor falling 34%; P-A3 said 2022 cannot move because
the anchor multiplies nothing there. Both cannot be true. P-A3 was the correct one and it was
reasoned from the mechanism (`UNFITTED_YEARS[2022]`) while P-A2's clause was reasoned from the
anchor table alone. Recorded rather than tidied away: the failure is that I wrote a prediction from
a table without re-reading the mechanism I had already written down two paragraphs earlier.

**P-A3 — CONFIRMED, exactly.** 2022 moves **+0.000pp**, ratio 1.000, on 0 renewal decisions and 213
SVT decisions. `UNFITTED_YEARS[2022]`'s stated cause holds: the year is 100% crisis-forced-passive,
every roll is diverted to the SVT segment table, and the anchor reaches none of the SVT hazards.

**P-A4 — CONFIRMED, and D1 trips on both legs, not one.** Mean absolute move 2.70pp against a
threshold of 1.0pp; max single-year 6.23pp against a threshold of 2.0pp. Neither is marginal. The
move is also **not** driven by years outside the arms' window — the arms span 2016–2025 and the five
risers are all inside 2017–2024. **The honest act is a re-run, not a provenance line**, and the
prediction that it would be was filed before the table was printed.

### Act (d), graded 2026-09-03

`git status --porcelain docs/observability/` shows **no deletion** of any of the three artefacts;
the re-run writes to a NEW dated path (`value_cycle_ab_s1_three_arm_20260903.json`) chosen for that
reason. Pasted rather than recalled:

```
 M docs/observability/.human_last_input
 M docs/observability/.seat_heartbeat.json
```

Neither is a value-arm artefact. The §4 constraint holds.

### Act (b), headline arm — graded 2026-09-03

`docs/observability/value_cycle_ab_s1_three_arm_20260903.json`, `generated_at`
**2026-09-03T10:17:07Z**, `world_identity.digest` **39a192ce04c1eda8** — which **equals the live
digest**. This is the first value-arm artefact in the repository that can say which world it ran in.

| figure | 2026-08-31 (superseded world) | 2026-09-03 (live world) | move |
|---|---|---|---|
| control net | £145,881.43 | £138,152.77 | −£7,728.66 |
| value-arm net | £157,952.50 | £140,488.64 | −£17,463.86 |
| level-arm net | £155,378.13 | £138,311.98 | −£17,066.15 |
| **`value_advantage_gbp`** | **£12,071.08** | **£2,335.87** | **−£9,735.21** |
| `level_advantage_gbp` | £9,496.70 | £159.21 | −£9,337.49 |
| `selection_gbp` | £2,574.37 | £2,176.66 | −£397.71 |
| `level_share_of_advantage` | 0.787 | **0.068** | −0.719 |
| renewals priced / offered | 120 / 1,953 | 104 / 2,009 | more offered, fewer priced |

**P-C1 — CONFIRMED.** I predicted the advantage would move by **more than one seed spread
(>£2,291.07)** and explicitly declined to predict the sign. It moved **£9,735.21 — 4.25 seed
spreads**. The refusal to call the sign was the right call and is the reason this grade is worth
anything: had I written "it shrinks", I would now be claiming a correct prediction for a guess.

**The drawn direction reached the right outcome by reasoning that act (a) refutes, and that
distinction must not be lost.** The direction predicted the advantage would shrink *because* "the
world got easier to hold … less book to re-win". The advantage did shrink. **The world got
harder** — +19.06pp of expected departure across 2017-2024 — and the direction's stated mechanism
is refuted by its own act (a). A premise that is wrong and a conclusion that is right is the most
expensive combination available here, because the conclusion is what gets quoted and the premise is
what gets reused. What actually happened is visible in the table: **every arm lost money** in the
harder world, and the control lost the *least* (−£7.7k against −£17.5k). More departures did not
hand the per-customer arm more to win; they cost it more than they cost the flat rule.

**P-C2 — REGISTERED AND DID NOT FIRE.** The trap was "advantage RISES and selection RISES → defect
in the re-run". `value_advantage_gbp` fell and `selection_gbp` fell. The detector stands unused and
uninverted, exactly as filed.

**The largest single movement is one nobody predicted, including me.**
`level_share_of_advantage` **0.787 → 0.068**. The page currently publishes *"the price level
accounts for 79% of the per-customer arm's advantage"*; in the live world it accounts for **7%**.
That is a qualitative reversal of the page's central reading, not a re-scaling of it, and it is
**unbounded until the floor lands** — `level_advantage_gbp` of £159.21 against an old-world spread
of £1,486.83 is indistinguishable from zero, and the new world's spread is not yet measured. **No
direction is claimed from it here.**

### Act (b), floor legs — IN FLIGHT, and the artefact is deliberately NOT promoted

The same-world noise floor is running now to
`value_cycle_ab_s1_noise_floor_20260903.json`. **The new three-arm artefact is committed at its
dated path and is NOT promoted to the canonical path the page reads**, and that is a decision rather
than an omission: promoting it would put a live-world contrast beside an 08-31 floor, which is
precisely the cross-world pairing this whole item exists to remove. The superseded pair on the page
is at least internally consistent and is now correctly labelled as history. **One world on both
sides, or it is not a comparison** — and that applies to the intermediate state too.

**P-C3 — UNGRADED.** It predicts the floor's `selection_gbp` stdev widens beyond **3776.27**. The
priced count *fell* (120 → 104), which cuts against my stated reasoning ("more accounts reach a
priced decision"), so this one may well be refuted on a premise I can already see is shaky. Recorded
now, before the floor returns, rather than quietly amended.
