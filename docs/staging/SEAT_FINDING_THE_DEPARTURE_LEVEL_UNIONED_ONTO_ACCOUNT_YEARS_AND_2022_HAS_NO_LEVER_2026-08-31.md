**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# The departure level now reads on the whole book, and 2022 cannot be fitted at all

*Seat, 2026-08-31. Lane 0 delivery: "union both departure routes on a declared denominator, and
re-fit `YEAR_LEVEL_ANCHOR` on the two-route capture."*

**Landed this turn:** the union, on a declared denominator, shared by both level instruments.
**Measured this turn and NOT landed:** the re-fit is feasible in nine years of ten and
**structurally impossible in 2022**, for a reason that is a result about the mechanism rather than a
number to clamp.

---

## 1. The union, and the denominator that nearly went wrong

`tools/departure_population.book_departure_level` is one reading over both routes, read by
`tools/measure_departure_level` and `tools/population_anchor._churn_by_year`. One implementation,
two callers — the VAT rule is what five copies of one calculation looks like a year on.

**The obvious union is the wrong one and it would have published a flattering number.** An SVT
account faces a segment decision at every boundary — 198 of them in 2022 across 55 accounts — and a
fixed account faces one renewal roll a year. A mean of `realized_churn_probability` over *decisions*
therefore mixes a per-segment probability with an annual one:

| union denominator | 2017 | 2020 | 2022 | 2024 | published band 2022 |
|---|---|---|---|---|---|
| **over decisions** (wrong) | 6.02% | 6.78% | **3.56%** | 5.34% | 2.9–4.3% |
| **over account-years** (landed) | 13.68% | 19.51% | **12.09%** | 16.02% | 2.9–4.3% |

The per-decision column runs 3.6–7.5% across the record and would have been published as *"the world
departs far below the record"*. On the account-year denominator the world departs **three times
above** the record in 2022. The two readings do not merely differ in size; they disagree about the
sign of the error in the year that matters most.

So the landed reading combines each account's decisions within the year — `1 - PROD(1 - p)` — and
means over **accounts**. That is the denominator class the published switching rate uses.

**It is an upper bound and says so.** An account facing no decision in a year cannot depart and is
not in the denominator. The direction is stated on every row (`book_departure_bound: "upper"`)
because it is what makes a verdict readable: a year out of band *above* cannot be explained away by
the bound, while a year reading inside might be outside on the full book.

## 2. What the whole book actually reads, against the record

Both routes, account-year denominator, on the committed two-route capture
(`docs/reports/ladder_churn_factors.json`, 144 renewal + 1,266 SVT decisions):

| year | band % | book E[depart] % | renewal-only E[depart] % | accounts | verdict |
|---|---|---|---|---|---|
| 2016 | 17.0–17.6 | 5.92 | 17.63 | 3 | OUT −11.1pp |
| 2017 | 13.5–14.0 | 13.68 | 14.20 | 57 | **in band** |
| 2018 | 19.5–20.0 | 21.38 | 29.56 | 53 | OUT +1.4pp |
| 2019 | 20.7–21.3 | 18.07 | 20.44 | 39 | OUT −2.6pp |
| 2020 | 22.5–23.0 | 19.51 | 29.57 | 48 | OUT −3.0pp |
| 2021 | 17.9–18.4 | 15.93 | 17.44 | 54 | OUT −2.0pp |
| 2022 | 2.9–4.3 | **12.09** | **— no renewal decisions at all** | 55 | OUT **+7.8pp** |
| 2023 | 8.9–12.5 | 16.21 | 15.67 | 54 | OUT +3.7pp |
| 2024 | 12.5–16.1 | 16.02 | 22.50 | 54 | **in band** |
| 2025 | 14.3–17.9 | 11.36 | 21.29 | 48 | OUT −2.9pp |

**The renewal column is not a worse version of the book column — it is a different population.** It
runs up to 13pp away from it, in both directions, and in 2022 it does not exist. That empty cell is
why the eight-year renewal summary printed `nan` for 2022 with nothing saying why.

## 3. The re-fit: nine years yes, 2022 no

`build_departure_risks` puts `level_anchor` on the three household hazards and **deliberately not on
`svt_inertia`** (`simulation/departure_risks.py:324`, and the comment there says so explicitly). So
the anchor's only lever on the whole-book level is the renewal route. Sweeping the renewal anchor
from 0 to 10³ and reading the book level at each end gives the reachable interval per year:

| year | band % | renewal decisions | floor (anchor→0) | ceiling (anchor→10³) | band reachable? |
|---|---|---|---|---|---|
| 2016 | 17.0–17.6 | 1 | 0.04 | 33.37 | yes |
| 2017 | 13.5–14.0 | 20 | 8.80 | 43.50 | yes |
| 2018 | 19.5–20.0 | 20 | 10.66 | 47.41 | yes |
| 2019 | 20.7–21.3 | 14 | 10.85 | 46.30 | yes |
| 2020 | 22.5–23.0 | 17 | 9.30 | 42.10 | yes |
| 2021 | 17.9–18.4 | 22 | 9.08 | 48.72 | yes |
| **2022** | **2.9–4.3** | **0** | **12.09** | **12.09** | **NO — floor is 7.8pp above the band ceiling** |
| 2023 | 8.9–12.5 | 17 | 11.69 | 40.71 | yes |
| 2024 | 12.5–16.1 | 18 | 8.66 | 41.38 | yes |
| 2025 | 14.3–17.9 | 15 | 4.80 | 35.63 | yes |

**In 2022 the floor equals the ceiling.** No account reached a renewal roll, so the anchor multiplies
nothing; the book's entire 2022 departure level is SVT drift, which the anchor does not scale by
construction. The year is not badly fitted — it is **unidentified**, and no value of the constant
changes its reading by a single basis point.

And the direction of the miss is the awkward one. 2022 is the record's *trough*: the crisis year in
which the published switching rate collapsed to 2.9–4.3% because there was nowhere to switch to. The
world departs 12.09% that year, entirely by drift off the standard variable product. **A world whose
accounts drift off SVT at a rate insensitive to whether the market has anything to offer is what the
record contradicts most sharply**, and the anchor was never the thing that could fix it.

`fit_year_anchor` already refuses an unreachable target rather than clamping to the bracket end
(*"That is a result about the mechanism — do not clamp it"*). That refusal is correct and this is
its first real subject.

## 4. What is owed, in order

1. ~~**Wire the whole-book target into `tools/fit_year_level_anchor`**~~ — **DONE in the commit
   carrying this finding**, which is also the commit that first lands §1 and §2 above. Nothing in
   this section had landed when it was written: the union, the controls and this document were all
   still uncommitted in the shared tree, and the fit had been measured in a scratch copy and never
   written to the tool. `book_emission_refusal` is the re-key — the observability clause survives
   and the minority clause does not, because under a whole-book target a minority renewal route is
   the state the repair exists to accept. `emission_refusal` is left exactly as it was, still
   guarding the renewal-only fit, so no existing control was weakened to land this.

   **And the fitted numbers moved, for a reason worth carrying rather than quietly restating.** The
   pre-registration's result tables combined an account's decisions ADDITIVELY (`Σp`); the landed
   code uses the competing-risks form `1 − Π(1−p)` that the rest of `departure_risks` uses. 2022's
   SVT-only level is 12.80% one way and 12.09% the other, and every fitted anchor in that block was
   ~12% low as a result. The correction is appended to the pre-registration beside its own tables
   and changes no verdict — P1 confirms on a wider margin, P2 stays refuted with the same split,
   P3 and P4 are untouched. `test_the_whole_book_fit_combines_an_accounts_decisions_as_competing_risks`
   is the control that now owns it, keyed to the additive form being UNBOUNDED rather than to any
   year's figure.

   Two years the first draft emitted are now refused rather than fitted: 2016 and 2025 sit outside
   `measure_departure_level.COMPARISON_YEARS`, and without that guard the fit published
   **2016: 15.988769** — six decimals solved off ONE renewal decision. The guard reuses the window
   this repository had already declared and justified rather than minting a fresh minimum.
2. **2022 is not part of that fit and must not be made to be.** Never a widened band and never a
   clamp. It is a mechanism finding: `svt_inertia_hazard` is a function of `years_on_svt` and
   `segment_days` and of nothing about the market, so a crisis year in which switching collapsed
   reads the same as any other. That is rung-2 work — a mechanism the world must obey — and it
   belongs with `docs/design/LADDER_APPLIED_TO_CHURN_2026-08-31.md` item 2.
3. **The band control still takes the renewal-only subject.** `world_realised_rate_pct` is
   unchanged and remains what `tests/architecture/test_switching_rate_commons.py` reads;
   `world_book_departure_rate_pct` is the new one beside it. Re-pointing the control is a separate
   act on a separate day, deliberately — rewriting what a control measures inside the commit that
   repairs the measurement makes the move unattributable, and this project has paid for that.
4. **`population_anchor._churn_by_year` still cannot show 2022 at all**, because its year set comes
   from `customer_events` and no account renewed that year. It now names the omission on every row
   (`book_departure_years_this_gate_cannot_show`). Widening the year set means fail-closing five
   arithmetic consumers of `sim_churn_rate` first; inserting 2022 with a `sim_churn_rate` of 0.0
   would publish a measured zero-churn crisis year and average it into the RAG checks.

## 5. Controls

In `tests/architecture/test_a_departure_reading_declares_its_population.py`, mutation-proven in an
isolated copy (a live publish held the index lock; mutating the shared tree manufactures another
lane's red). Each mutation killed exactly its own control and no other — no equivalences:

| mutation | control that fires |
|---|---|
| mean over decisions instead of account-years | `test_the_whole_book_level_is_a_mean_over_accounts_and_not_over_decisions` |
| fall back to the renewal-only level when the SVT route is unreadable | `test_the_whole_book_level_refuses_a_capture_that_cannot_see_both_routes` |
| read an unrecorded hazard as 0.0 | `test_an_unrecorded_hazard_makes_its_year_unknown_rather_than_zero` |
| drop the bound's direction | `test_the_whole_book_level_states_its_denominator_and_its_direction` |
| drop the named years the churn gate's year set omits | `test_the_churn_gate_names_the_years_its_own_year_set_cannot_show` |

Plus a null control on the real capture —
`test_the_whole_book_and_renewal_only_levels_are_two_different_readings` — asserting no year, no
threshold and no direction, only that the two populations give different answers and that at least
one year has departures the renewal route cannot see. It goes red the moment someone quietly
re-points the whole-book reading at the renewal rows.
