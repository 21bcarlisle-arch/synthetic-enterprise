**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# FINDING — the level fit solves onto the published band's CEILING, so `capture → fit → capture` cannot converge inside the band, and "6 of 8 in band" is six years sitting in the top 6% of their own bands

**Found 2026-09-03, delivery seat, Lane 0, isolated worktree, while checking whether the 2021 half
of the whole-book band xfail was reachable with one more capture-fit pass.** It is not, and neither
is anyone else's — for a reason that is a property of the loop rather than of 2021.

---

## 1. Measured, on the live capture

`tools.measure_departure_level.world_book_rate_pct()` on `c6_second_pass`, against the commons:

| year | world | lo | hi | hi − world | band width | position in band |
|---:|---:|---:|---:|---:|---:|---:|
| 2017 | 13.9997 | 13.50 | 14.00 | +0.0003 | 0.50 | **99.9%** |
| 2018 | 20.0003 | 19.50 | 20.00 | −0.0003 | 0.50 | **100.1%** |
| 2019 | 21.3002 | 20.70 | 21.30 | −0.0002 | 0.60 | **100.0%** |
| 2020 | 22.9728 | 22.50 | 23.00 | +0.0272 | 0.50 | **94.6%** |
| 2021 | 18.5306 | 17.90 | 18.40 | −0.1306 | 0.50 | **126.1%** (out) |
| 2022 | 2.4999 | 2.90 | 4.30 | +1.8001 | 1.40 | −28.6% (out, no lever) |
| 2023 | 12.3996 | 8.90 | 12.50 | +0.1004 | 3.60 | **97.2%** |
| 2024 | 15.9607 | 12.50 | 16.10 | +0.1393 | 3.60 | **96.1%** |

**Every fitted year sits in the top 6% of its band.** Three of them are on the ceiling to four
decimal places, and two of those three (2018, 2019) are *arithmetically above* it — they read as
in-band only because `inside_band` compares at the record's own published precision, which is
reasoned and correct and is not the issue here.

## 2. Why, and it is one line

`tools/fit_year_level_anchor.fit_whole_book` solves

```
(expected departures on BOTH routes) / (accounts on the book) == market_departure_rate(year)
```

and `market_switching_propensity._published_departure_rates` returns **`rate_pct_hi`** — the band's
HIGH END, in every year:

```
2017 target 14.0  band 13.5-14.0   TOP        2021 target 18.4  band 17.9-18.4   TOP
2018 target 20.0  band 19.5-20.0   TOP        2022 target  4.3  band  2.9-4.3    TOP
2019 target 21.3  band 20.7-21.3   TOP        2023 target 12.5  band  8.9-12.5   TOP
2020 target 23.0  band 22.5-23.0   TOP        2024 target 16.1  band 12.5-16.1   TOP
```

**The high end is a deliberate, sanctioned curriculum choice and this finding does not dispute it.**
It is the director's §7 tie-break of 2026-08-30 — *where the evidence is ambiguous, choose the
option that makes the company's advantage harder to demonstrate* — settled in
`gb_switching_rate_denominators.md` §6, derived from the artefact rather than written down, and
argued in `_published_departure_rates`'s own docstring. More departures is a harder book to hold.

**What is a defect is using that same edge value as the SOLVER'S TARGET.** The fit's target and the
control's verdict are different shapes: the fit aims at a POINT on the boundary, the control demands
CONTAINMENT. `departure_level_anchor`'s own note states the loop's dynamics — *"the fit is exact on
the run it was fitted to and approximate on the next one … raising the level changes the book, so
the population the following year is not the one the anchor was solved against"*. Compose the two
and the year's expected position after a re-capture is **the ceiling**, with the deviation free to
go either way. Roughly half of any capture-to-capture movement lands outside the band, in every
year, forever.

## 3. What this says about the xfail, which is not what the xfail says

`test_the_whole_book_departure_level_is_inside_the_published_band` reads 2021 as *"an overshoot of
the re-capture, not a level error … a tenth of a point on 51 accounts is inside the draw"*. Both
clauses are true and the conclusion drawn from them — that a further capture-fit pass may close it —
does not follow. A pass that closes 2021 moves 2021's anchor and therefore the book, and every other
year is sitting on its own ceiling with **zero upside margin**. The marker requires all eight years
inside SIMULTANEOUSLY, from a design in which each year's expected position is its boundary.

Observed magnitudes on the one movement available: 2021 came in **+0.13pp** above a target it was
solved onto, against a band **0.50pp** wide. 2023 and 2024 sit 0.10pp and 0.14pp below theirs. So
the movement is of the same order as a quarter of the narrow bands' width, and the years have
between 0.0003pp and 0.14pp of room.

**n = 1, and that is stated rather than dressed up.** One capture-to-capture movement is not a
spread. What would measure it: two captures of the same book under the SAME anchor block at
different seeds, differenced per year. That is the one-variable experiment and it has not been run.
c5 cannot supply the second point — it ran under the anchors the second re-fit replaced, so
`stale_anchor_refusal` correctly refuses a band reading off it, which is the control working.

## 4. Recommendation, and it is the director's to name

**Keep the anti-flattering tie-break for the world's published LEVEL. Give the SOLVER a target with
margin.** Solving onto something inside the band — the high end less one measured capture-to-capture
deviation — leaves the world's departure level in the upper part of every band (still the harder
book, still §7's direction) while making the expected position INSIDE rather than ON the boundary.
It is the difference between "the world departs as hard as the record allows" and "the world is
pinned to the record's ceiling and half its runs fall off".

**This is a curriculum value and therefore not mine to change unilaterally** — CLAUDE.md's
baseline/curriculum wall: *"Which world the company lives through is the director's, named and
versioned in a file he can read."* Where in the band the world sits is exactly that, and §6 of
`gb_switching_rate_denominators.md` is where it is named. Escalated on NTFY with this
recommendation; proceeding on everything that does not depend on the answer.

**Do the deviation measurement first regardless of the answer** — two same-anchor captures at
different seeds. Without it the margin would be a number picked because a number was needed, which
is the shape this repository has a rule about.

## 5. What must NOT be done

* **Do not widen the band.** It is the published record.
* **Do not move `_published_departure_rates` to the midpoint as a repair.** That changes the world's
  published level claim as a side effect of fixing a solver, and it is the flattering direction —
  the tidier default that §6 explicitly refused. If the world's level claim should move, that is a
  separate, named, director-authored change.
* **Do not read "6 of 8 in band" as a converging loop.** It is six years within 0.14pp of a ceiling
  they were aimed at.
