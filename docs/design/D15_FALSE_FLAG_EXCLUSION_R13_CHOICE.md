# The W2_5 ↔ C7 false-flag denominator — an R13 curriculum call, with all three rates on the table

**Atom:** `D15_w2_5_false_flag_direction_r13_choice` · **Built:** 2026-08-09 (worker tick)
**Instrument:** `tools/couple_w2_5_c7.py` · **Controls:** `tests/tools/test_couple_w2_5_c7.py`
**Upstream finding:** `docs/design/D13_SELF_RATIONING_NEGATIVE_POPULATION_DISCOVER.md`
**Status:** the second direction is BUILT and PUBLISHED; the basis is **PROVISIONAL** at option **C**,
recorded here and sent to the director, reversible by a one-line edit.

---

## The question, in one line

The pair now scores both error directions. The miss direction is settled. The false-flag direction
needs a denominator — **which customer-years is a distress flag *wrong* on?** — and there are exactly
three candidate answers, because `income_stress` has exactly three values. Picking between them moves
the published number **×2.88** with company behaviour held literally fixed.

This is not a threshold on a continuum. It is a named, enumerable question with a measured consequence
attached to each answer, which is why it can face the director as an R13 curriculum call rather than
being quietly chosen inside a build.

## The three populations (each built by its own predicate, never as a leftover)

Reference population: 2000 customers × 2016–2025 = **20000 customer-years**.

| population | definition | n |
|---|---|---|
| **must-flag** | a distress event *dated in that year* | 1099 |
| **NEITHER** | no event that year, but the household carries income stress at a year end | 2772 |
| **must-not-flag** | no event that year, LOW income stress at **both** year ends | 16129 |

The NEITHER band is the whole of the problem. `income_stress` **persists**: a job loss in 2019 leaves a
household HIGH until an `income_recovery` event fires, and `simulation.payment_timing` keeps mapping
that stress onto LATE/DD_FAILED records for as long as it lasts. A C7 flag in 2020 on such a household
is **correct** — the household really is in distress — but a naive denominator scores it as one of the
company's false flags. 2772 cases is 14.7% of that naive denominator.

## The three candidate answers, measured

| basis | holds the company to | false_flag_rate | balanced gap |
|---|---|---|---|
| **A_naive_universe_minus_truth** | flagging distress only in the year an event is dated; a household still HIGH from last year's job loss must NOT be flagged | **0.1661** (3140 / 18901) | 0.0871 |
| **B_exclude_carried_high** | flagging severe carried distress is allowed; flagging carried MODERATE distress (a prior-year new baby, divorce, retirement) still counts against it | **0.1491** (2674 / 17937) | 0.0786 |
| **C_settled_low_at_both_ends** | flagging a household that was demonstrably not in distress at any point the harness can name — and nothing else | **0.0576** (929 / 16129) | 0.0329 |

The miss direction is **0.0081 on all three** (recall 1085/1099): the company is fixed, only the
denominator moves. The swing is flat under scale, so it is not a small-sample artefact:

```
  5,000 instances : 0.1752 -> 0.0626  (x2.80)
 10,000 instances : 0.1674 -> 0.0590  (x2.84)
 20,000 instances : 0.1661 -> 0.0576  (x2.88)
```

## The recommendation — **C**, and why the reason is the set and not the number

**R12 hazard, stated first because it is the obvious objection: C produces the lowest of the three
rates, and it is being recommended by the agent whose atom closes when this instrument publishes.**
That is exactly the shape this repo keeps catching, so the argument has to stand on the *population*
and be checkable without reference to the value it yields.

It does. The false-flag direction asks: **on which cases would a flag be WRONG?** The harness cannot
call a flag wrong on a household it holds to be carrying income stress — that is the harness scoring
the company down for being right, the same error D11 measured on the payment triad, where counting
late-past-grace successes as false flags inflated the wrongful-dunning rate from 0.0009 to 0.2834.

The deeper reason is a **shape mismatch between the two directions**, and it is worth stating plainly
because it is the thing a future reader will need:

* the **miss** direction's truth is **EVENT-shaped** — "a distress event is dated in this year";
* the **detector's actual claim** is **STATE-shaped** — "this household is in distress now".

Those two disagree on exactly one region: the carried-distress band. Basis A resolves the disagreement
by holding the company to the event shape it never claimed. Basis C resolves it by scoring the company
only where both shapes agree the household was fine. B is a halfway house with no principle behind the
cut — it excuses carried HIGH stress but not carried MODERATE stress, and `payment_timing` disrupts
payments under both.

**What would change the recommendation:** a decision that the *curriculum* should hold this company to
timely detection specifically — i.e. "we want to know whether the support team notices distress in the
year it starts, and a flag on a two-year-old unresolved job loss is a late flag we are choosing to
count against them". That is a legitimate thing for the director to want and it is a **curriculum**
choice, not a measurement error. If that is the intent, the honest instrument is **not** basis A —
it is a new *latency* dimension beside this one (the payment triad already has one), because basis A
prices timeliness by corrupting the false-flag denominator rather than measuring it.

## What is published, and how to overturn it

* `tools/couple_w2_5_c7.py::PUBLISHED_EXCLUSION_BASIS` is the choice. **One constant.** Point it at
  `A_naive_universe_minus_truth` or `B_exclude_carried_high` and every published rate moves on the next
  run with no other edit.
* **All three rates are computed and printed on every run** (`false_flag_measures` scores every basis,
  `format_r13_choice_table` prints them side by side, `measure()` puts them in
  `components["candidate_false_flag_rates"]` so they travel into the gap ledger). The choice cannot
  hide inside a headline, whichever way it goes.
* The exclusion is **published, not silent**: `n_excluded` and its reason travel in the components, and
  `gap_metric.detection_measures` RAISES on an unexplained exclusion (D10's rule).
* R12: every rate here is a **diagnostic**. None of them is a target, and no basis may be selected
  because of the number it produces.

## R15 — what the controls prove, both ways

`tests/tools/test_couple_w2_5_c7.py`, 20 tests, each a differential:

* **the complement derivation is refused at the source.** Redefine NEITHER as `not must_flag` — the
  exact defect — and a settled LOW/LOW case matches two populations, so `_classify` raises. The
  opposite mutation (a case matching nothing) raises too.
* **the populations are re-derived from the SIM**, not from each other: the membership test recomputes
  `household_at_date` per instance, so a self-consistent lie fails.
* **the band is not a no-op.** Fold NEITHER back into the negative population and the rate must move
  ≥1.5× (it moves 0.0576 → 0.1661).
* **the published direction tells a real false flag from a carried-distress flag.** One company that
  flags a single carried-distress year scores **0** false flags; one that flags a single settled LOW/LOW
  year scores **1**. Under basis A both score 1 — the defect, demonstrated rather than described.
* **neither degenerate can buy a good score.** Flag EVERYTHING and flag NOBODY both land on the 0.5
  baseline under all three bases. This is the debt closing: the retired recall-only metric gave the
  flag-everything company a perfect 0.0, and `DETECTION_DIRECTION_CONTRACT`'s class control now scores
  this pair's degenerate through this pair's own scorer.
* **one name, one quantity.** The shared renderer's default nouns are the payment triad's
  ("truly-failed", "the wrongful-dunning exposure"). This pair's truth is a distress year and its false
  flags are not dunning, so it names its own quantity — the D16 class applied at birth rather than
  after a reader is misled — and the triad's default render is asserted byte-identical.

## Register state after this atom

`tools/couple_w2_11_d5.py::DETECTION_DIRECTION_CONTRACT`: three of four published detection dimensions
now count both error directions (D11 headline, D12 cell grid, D15 this pair). One named debt remains —
`couple_w2_8_c10.detection`, owned by `D14_w2_8_needs_negative_drops`, whose measure is **vacuous**
rather than unchosen (0 of 3752 non-rationers have any consumption drop, so its rate is 0.0000 for any
detector). That is a world-depth gap, and D13's finding that the two self-rationing pairs were never
one problem is what let this half close while the other stays open.
