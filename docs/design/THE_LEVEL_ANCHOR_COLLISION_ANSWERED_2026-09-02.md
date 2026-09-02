# The level-anchor collision, answered

**Decided 2026-09-02, delivery seat, Lane 0.** The question had been owed for three orientations.
The input to it — the whole-book block that existed in no commit — was preserved at
`docs/design/UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md` and **had already landed on
`origin/main` at `9238075d9` before this tick opened**; the instruction to land it first was
discharged by verification (`git ls-files` matches, `git diff origin/main` empty), not by re-doing it.

The pre-registration, filed before any run and graded beside its own text, is
`docs/staging/WORKER_PREREGISTRATION_WHAT_ANSWERING_THE_LEVEL_ANCHOR_COLLISION_MUST_MOVE_2026-09-02.md`.

---

## The question, and why both offered answers are wrong

> *Does an in-record year the whole-book fit cannot identify REFUSE, or FALL BACK?*

**Refusing** crashes the world. `year_level_anchor` is on the hot path — `customer_events.py:610`,
`run_phase2b.py:1634`, `:1667`, `:1719`, each on `int(term_start_str[:4])` — and 2016, 2022 and 2025
term starts occur in every capture on disk. Measured this tick by composing HEAD's guard with the
seven-year block: 2016, 2022 and 2025 all raise `ValueError`; 2024 and 2030 return. A world that
cannot run the record it exists to run is not failing closed, it is failing absent.

**Falling back** is the catalogued defect `9fd700366` was built to stop: the reference year's anchor
ran 1.98x on 2022, silently, on the record's lowest year, in the direction that *adds* departures.

## The premise is false, and it is the same defect one set over

`9fd700366` found that the fallback's **condition** was the fitted table while its **justification**
was the published record — two different sets — and replaced the condition with the record. But the
fit's declared scope is **neither**. It is
`tools.measure_departure_level.COMPARISON_YEARS = range(2017, 2025)`, restricted there because 2016
carries 1–3 renewal decisions and 2025 is a partial year.

**Three sets, not two:** the fitted table, the published record (2016–2025), and the comparison
window (2017–2024). The guard picked the second when the fit is scoped by the third. That is what
turned a scope statement into a crash.

## The answer, by case, because the three absences are not alike

### 2016 and 2025 — FALL BACK, and the guard was what was wrong, not the fit

They are outside the comparison window. A year the fit never *claimed* is not a year the fit *failed
to identify*. The exclusion is corroborable and I re-counted it rather than citing it: 2016 carries
**1** renewal row in `c2` and `ladder` and **3** in `c3`; 2025 carries **15–35** against a full
year's 49–59. The reference-year fallback's existing justification —
`market_switching_multiplier(year)` already carries the year-to-year level movement, and what the
anchor supplies is the calibration of a factor population to a rate, which is a property of the
population and not of the year — applies to them exactly as it applies to a synthetic future.

### 2022 — REFUSES, but the refusal belongs to the FIT and the SURFACE, not to control flow

2022 is inside the window, so the scope argument does not cover it, and it is genuinely
unidentified. **Two independently binding causes, and the scope of each is stated:**

1. **Capture-scoped.** 2022 is 100% crisis-forced-passive (`renewal_engagement.CRISIS_PASSIVE_YEARS`),
   C1b routes every passive roll to the SVT segment table, so the `c2`/`ladder`/native family carries
   **zero** 2022 renewal decisions — the anchor multiplies nothing and floor equals ceiling.
   **This is FALSE of `docs/reports/c3_shown_price_departure_factors.json`, which carries 53 renewal
   rows in 2022** under the retired ten-year block. Counted independently this tick.
2. **Not capture-scoped, and this is the one that binds.** 2022's SVT floor is 12.09% against a
   published 4.30% ceiling, and `build_departure_risks` deliberately does not scale `svt_inertia`, so
   **no anchor ≥ 0 brings 2022 to the record.** Not a gap a re-fit closes.

Not clamped, not interpolated, band not widened.

### The mechanism: a PARTITION, not a binary

Every record year is **fitted**, or **unfitted with a declared cause**. The guard is unchanged in
condition and can still fire — an undeclared gap inside the record still raises. What lifts it is a
named reason, never a value. `anchor_coverage()` returns the two sides, because a float cannot say
whether it was fitted: the previous unfitted block was detectable *only* because its three unfitted
years all read `3.053619` in a capture's `sim_level_anchor` column, which is a coincidence of the
fallback and not a disclosure.

### 2022's declared value is 1.0, and I flag the direction against myself

`NO_LEVEL_CORRECTION = 1.0` is the identity of the parameter and `build_departure_risks`'s own
default — the arithmetic form of *"no calibration is identified"*, not a calibration borrowed from
another year's population. HEAD's own committed docstring already established the borrow is wrong
here.

**The objection, stated because it is real:** 1.0 is lower than both 1.524110 (retired) and 3.053619
(the borrow), so it removes departures — the flattering direction, and therefore the one to distrust.
The defence is that 2022's whole-book floor is already ~12.09% against a 4.30% ceiling, so the year
runs ~2.8x *above* the record before the anchor touches it; and that the reason for 1.0 is that it is
the identity, not that it moves toward the record. If that defence fails, the entry is one line and
it is declared, not buried.

## Which table is live, and the retired one's unfollowable citation

**The seven-year whole-book block is live. The ten-year block is RETIRED**, and its table and full
reasoning are preserved at `UNLANDED_WHOLE_BOOK_LEVEL_ANCHOR_BLOCK_2026-09-01.md`.

The ordering was **re-measured, not taken from the correction that asserts it.** Every capture records
the anchor it executed under in `sim_level_anchor`:

| artefact | mtime | `sim_level_anchor` | ⇒ ran under |
|---|---|---|---|
| `ladder_churn_factors_svt_segment_decisions.json` | 08-31 16:44 | ten-year values, all 10 years | **ten-year** |
| `c2_departure_factors_svt_segment_decisions.json` | 08-31 20:54 | seven-year values; 2016/2022/2025 all `3.053619` | **seven-year** |

So: ten-year block → `ladder` capture → seven-year block → `c2` capture. The tree's block is HEAD's
**successor**.

**The retired block could not be re-cited, which is why it is retired rather than re-cited.** Its
docstring named `docs/reports/c2_departure_factors.json` as its fit input; `b46318106` overwrote that
file in place a day later, and the artefact carrying the name today **ran under its own successor**.
The citation resolved, at HEAD, to a capture produced two steps after the block it claims to have
produced — `figures_on_a_superseded_clock`, a stable path over a moving run. Re-citing it would have
meant inventing a provenance. The live block's provenance is stated as *measured from the
`sim_level_anchor` column* rather than as a filename, for exactly that reason.

## What this costs the company, which is the point

| year | retired | live | ratio |
|---|---|---|---|
| 2016 | 4.597312 | 3.053619 | 0.664 |
| 2017 | 4.256902 | 4.547299 | 1.068 |
| 2018 | 3.345826 | 2.882178 | 0.861 |
| 2019 | 3.228064 | 4.803900 | 1.488 |
| 2020 | 4.425742 | 6.412007 | 1.449 |
| 2021 | 3.219914 | 4.488202 | 1.394 |
| 2022 | 1.524110 | 1.000000 | 0.656 |
| 2023 | 2.091517 | 0.364038 | 0.174 |
| 2024 | 3.020806 | 3.053619 | 1.011 |
| 2025 | 2.118624 | 3.053619 | 1.441 |

**R13: this is BASELINE, not curriculum.** The level is the published record's, external to this tree
and decided blind to company results. The denominator moved from renewal decisions — a *selected*
sub-population, the households that demonstrably shop — to account-years, which is the population the
published rate actually counts. It moves hard against us: 4.50% lost per renewal becomes the record's
15.50%, 3.4x more revenue at risk and 3.4x more re-acquisition spend. A book that loses 4.5% a year is
trivially easy to hold, and easy-to-hold flatters us in the one dimension the thesis is about.

## What is still owed, and is NOT claimed done here

1. **Neither table is band-verified until a re-capture runs, and that is the honest state.** The band
   leg reads the *stored* capture, so the module is not in its read path: this commit moves no
   published band verdict, and the leg remains `xfail(strict)` with the world out of band in 7 of 7
   readable years. **"We cannot tell yet" is the result for the live block's band performance**, it is
   on the register rather than in a footnote, and the discharge is a re-capture
   (`tools/capture_departure_factors.py`) followed by a re-fit — never a widened band.
2. **The disclosure handshake fired and the register was corrected to match, not re-keyed.** The
   `_HELD_INDIRECTLY` denominator moved nine-of-ten → seven-of-ten, the 2022 entry is kept in the past
   tense beside what replaced it, and the three new symbols are classified.
3. `tools/population_anchor.py`'s 2022 consumers — repaired in this commit, see the prereg's P5.
