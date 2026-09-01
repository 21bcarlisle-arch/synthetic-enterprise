**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `the-only-control-holding-the-level-anchor-is-red-and-reports-a-constant-pass`

# The level anchor's only accountability route has been blind to 2022 since the capture was swapped — and 2022 is the year it was wrong about

**Found:** 2026-09-01 at clean HEAD `77e1d68e6` (== `origin/main`), working the Lane 0 delivery
direction *"two tests are red at clean HEAD and they are the accountability route for the quantity
every other item depends on"*. Verified by `git archive HEAD` into a clean stem, not from this tree.

**The direction asked which of three defects emptied the subject: a year stopped being PRODUCED,
stopped being READ, or stopped being CLASSIFIED. The answer is the first, and it is datable.**

---

## 1. The red, and what it actually says

```
tests/architecture/test_switching_rate_commons.py   2 failed, 24 passed, 1 xfailed
  AssertionError: only 7 years of realised rate to judge
  AssertionError: only 7 years had their margins checked -- a control over an emptied subject
                  reports a constant PASS
```

Both legs share one cause. `COMPARISON_YEARS = range(2017, 2025)` is **eight** years.
`tools.measure_departure_level.world_realised_rate_pct()` returns **seven**:
`[2017, 2018, 2019, 2020, 2021, 2023, 2024]`.

**The missing year is 2022.** Not a year at the window's edge — the interior one, and the one the
published record puts at its trough (band 2.9–4.3%).

## 2. Which of the three defects: PRODUCED

Rows in the committed capture `docs/reports/c2_departure_factors.json`, by year:

| 2016 | 2017 | 2018 | 2019 | 2020 | **2022** | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 20 | 16 | 18 | **0** | 17 | 17 | 16 |

2021 carries 23. Every year in the span carries 16–23 **except 2022, which carries zero.** That is
not sampling and it is not truncation: it is a hole in the middle of the run.

- It did **not** stop being READ. `COMPARISON_YEARS` still contains 2022; the reader is unchanged.
- It did **not** stop being CLASSIFIED. The registers in `test_switching_rate_commons.py` are
  untouched.
- It stopped being **PRODUCED**, at a nameable commit.

**`b46318106`** — *"the capture the published departure figures were already produced from lands"* —
replaced the capture. Its parent `71242c941` carried **465 rows with 54 in 2022**; `b46318106`
carries **148 rows with none**. Two commits earlier the capture had 92 rows in 2022.

Both count assertions were written when 2022 was still there: `len(world) >= 8` at `71242c941`
(the same commit whose capture had 54 rows in 2022), `checked >= 8` at `6168ae6bf`. **They were
correct when written and the artefact moved underneath them.** Nothing anywhere said a year had
left, because an intersection reports a year it excluded and a year the run never produced
identically — as absence.

## 3. The `_HELD_INDIRECTLY` claim is wrong, and this is the part that matters

`test_switching_rate_commons.py` classifies `YEAR_LEVEL_ANCHOR` and `year_level_anchor` under
`_HELD_INDIRECTLY`, stating they are

> *held through its EFFECT — the world's realised departure rate, which is `_PRINCIPAL_SUBJECT`
> above and is band-checked every run.*

**That claim is false for 2022 and has been since `b46318106`.** `_PRINCIPAL_SUBJECT` is the
renewal-route reading. It has no 2022 value at all, so `YEAR_LEVEL_ANCHOR[2022] = 1.524110` is held
by nothing. The register claims the indirection for ten years and it delivers for seven.

**2022 is exactly the year the anchor was already known to be wrong about.** `year_level_anchor`'s
own docstring records that the fallback took 2022 to `3.053619` against `1.524110` committed —
**1.982x** — and that on the record's lowest year this pushes departures *up*, away from the record.
The direction's summary is confirmed: *this is what made a silent 1.98x on 2022 survive a capture,
a fit and two preregistrations.*

**The honest answer the direction asked for: for 2022 the indirection never held it.** Not "stopped
holding it" — the register was written on 2026-08-31, after `b46318106` had already emptied the
year. The claim was never true for 2022 on the day it was written.

## 4. It is not unobservable — the whole-book route sees it, and reports it badly out of band

The renewal route is blind to 2022 for a reason that is a fact about the world, not a gap:
in the crisis no household reaches a renewal roll (`market_switching_propensity` carries
`2022: -200.0` savings — *"no competitive alternative below SVT"*). Every 2022 departure is on the
SVT route. `tools/fit_year_level_anchor.py` records the same absence independently as its
*"no renewal population"* refusal, and separately as *"unreachable: SVT alone expects 12.80%
against a target of 4.30%"*.

But `world_book_rate_pct` — the whole-book reading — **does** cover 2022:

| year | band % | book expected % | dep renewal | dep SVT | accounts |
|---|---|---|---|---|---|
| 2022 | 2.9–4.3 | **12.83** | 0 | 4 | 52 |

Roughly **3x above the band** in the year the anchor nearly doubles. So the quantity is observable;
it is the *chosen indirection* that cannot see it. The register pointed at the one route that is
structurally blind to the one year that mattered.

**Correction owed in the register** (not landed — see §6): `_HELD_INDIRECTLY` must either point at
the whole-book reading, which covers 2022, or state plainly that the renewal-route indirection
does not hold 2022 and name the year. It must not keep claiming an indirection it does not have.

## 5. What landed

`tools/measure_departure_level.py`:

- **`realised_rate_coverage()`** — returns `({year: reading}, {year: why there is none})` as a
  **partition** of `COMPARISON_YEARS`. Every comparison year is in exactly one. A year that cannot
  be read is named with its reason instead of vanishing from a dict.
- The two causes are **kept apart**, because they want different repairs: a year *outside the
  capture's span* means the run was shorter (re-capture for longer); a year *inside the span with
  zero decisions* means the run reached it and produced nothing (re-capturing will not help). A
  single "no data" message sends the reader to the wrong repair.
- `world_realised_rate_pct` is **unchanged**. It is a band control's subject; changing a control's
  subject shape inside the commit that repairs what it measures makes the move unattributable — and
  a producer turned fail-closed crashes every existing consumer.
- **The refusal reaches the surface.** The unread year used to print as `nan`, which reads as a
  rendering accident rather than a fact about the run — and then entered `fmean`, making the whole
  summary `nan`, and `min`/`max`, making the resolution line order-dependent. **One unread year
  silently destroyed every aggregate beneath it.** It now prints:

```
  2022            2.9–  4.3        3.0              4.3           REFUSED    ...   NO READING

  YEARS IN 2017–2024 WITH NO READING (1 of 8) -- named, not dropped:
    2022: 2022 is inside the capture's span (2016–2025) and carries ZERO renewal decisions,
          so the run reached it and produced nothing to measure
  Every figure below is over the 7 year(s) that DO have a reading (2017, ..., 2024).
```

`tests/architecture/test_a_departure_reading_declares_its_population.py` — three legs, **keyed to
the property and not to seven or to eight**, each mutation-proven with `python3 -B` and a cleared
`__pycache__`:

| leg | mutation | fired |
|---|---|---|
| every comparison year is read or refused by name, never merely absent | absent years `continue` with no refusal | ✓ *"2022 is in NEITHER"* |
| a hole is refused differently from an edge | collapse the two refusal branches | ✓ |
| the instrument prints the year it could not read rather than `nan` | restore the bare `nan` row, drop the block | ✓ |

A count assertion was deliberately **not** used. `>= 8` goes red the day 2022 comes back — green
when the subject rots further and red when the code becomes more honest, which is backwards.

## 6. What did NOT land, and why — read this before assuming the two legs are green

**The two originally-red legs in `test_switching_rate_commons.py` are still red at HEAD.** That
file could not be touched this turn, and the reason is a separate and more serious finding filed
alongside this one: its index holds another lane's branch that predates `58c496f64` and would
**silently revert three landed controls**, including the only one that can see 2022. Committing the
repair into that file would have reintroduced, under a commit message claiming to fix it, exactly
the defect this finding is about.

So the accountability route now exists, is mutation-proven and prints its refusal — but it lives in
the sibling file. **Owed:** re-key the two legs in `test_switching_rate_commons.py` onto
`realised_rate_coverage()`, and correct `_HELD_INDIRECTLY` per §4 — both after the contended index
is resolved.

## 7. The shape, for the catalogue

**An intersection cannot tell an excluded year from a year that was never produced.** Both are
absence. Any control that counts what it checked will therefore report a smaller PASS rather than a
failure when its subject loses a member — and the member it loses is not random: it is the year the
world found hardest, which is the year the control was most needed. *Key the control to the
partition, not to the count.*
