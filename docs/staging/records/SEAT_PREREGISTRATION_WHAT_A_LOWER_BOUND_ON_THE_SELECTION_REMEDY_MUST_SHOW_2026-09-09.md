# PRE-REGISTRATION — what a lower bound on the selection leg's remedy must show

**Severity:** RECORDED
**Lane:** G_data_learning
**Filed:** 2026-09-09
**Claim:** `the-page-cannot-say-what-would-settle-the-sign-of-the-only-leg-that-matters`

---

## The question

`site/data/value_arms.json → current_world.selection_leg` publishes £270.21 with a ±£1,810.50
nine-seed bound, says the quantity carries no sign, and then stops. `current_world.what_would_answer_it`
is `None`. The only remedy arithmetic on the page — `floor_decomposition` — is measured on a
DIFFERENT book (the arm priced 104 of 2,009 renewals; the published run priced 214 of 2,035) and
splits a DIFFERENT contrast (`value_advantage_gbp`), and the feed refuses to state a remedy from it
for exactly those two reasons. So a reader who reaches the refusal has nowhere to go.

The direction says: re-run the decomposition against `selection_gbp` on the published run's own book
at the nine seeds the rest of the page uses. **A full decomposition needs two more nine-seed floor
legs (`only`, `except`) on this book — each is nine full three-arm decade passes at a measured
~6.4 GB peak, run one at a time. That is many machine-hours and does not fit this turn.**

## What I am doing instead, and why it is not a smaller version of the same thing

The undecomposed nine-seed floor on THIS book already exists
(`docs/observability/value_cycle_ab_s1_noise_floor.json`, mode `all`, seeds 11111–99999, world
`39a192ce04c1eda8`) — it is the artefact the selection leg's own ±£1,810.50 bound is read from.

Write `V` for that leg's `selection_gbp` variance, `V = V_priced + V_rest` for the split the two
missing legs would measure, and `c` for the contrast. Growing the priced book by `m` shrinks the
priced half as `1/m` and leaves the rest-of-book half alone, so the page's own resolution rule
(`_resolvable`: `|c| > sd`) is met when

    V_rest + V_priced/m  <=  c^2      =>      m = (V - V_rest) / (c^2 - V_rest)

With `A = V > c^2`, `f(x) = (A-x)/(c^2-x)` has `f'(x) = (A - c^2)/(c^2 - x)^2 > 0` on `[0, c^2)`.
**`m` is strictly increasing in `V_rest`, so `m >= V / c^2`, attained only when `V_rest = 0`.**

That is a LOWER BOUND on the remedy that holds whatever the two missing legs turn out to say, and it
is computable from the floor already on this book, on this contrast. It fails closed: the true
requirement is larger, never smaller. If the lower bound already exceeds what this world can build,
the verdict is settled and running the legs cannot unsettle it.

## What I predict, BEFORE running it

I derived these to two significant figures by hand from the published feed before writing this file;
I am recording them so the exact run can refute them.

| # | Prediction | Refuted by |
|---|---|---|
| P1 | Against the PUBLISHED DRAW (`c` = £270.21) the lower bound is ~45× this book | any `times_this_book` outside 40–50 |
| P2 | That is ~9,600 priced decisions against this book's 214, and ~91,000 renewals offered against 2,035 | either count out by >10% of the multiplier |
| P3 | The settled-book ceiling (`simulation.premise_population.settled_book_ceiling(years=1)`, 632 accounts against this book's 164) is ~3.9× — so P1 is **UNATTAINABLE**, and no book this machine can settle gives the published draw a sign | a ceiling ≥ 45× this book, or a ceiling that reads unavailable |
| P4 | Against the NINE-SEED MEAN (`c` = −£1,078.17) the lower bound is ~2.8× this book, which is INSIDE the ceiling — so the two contrasts give OPPOSITE verdicts and the page must publish both | a multiplier for the mean that also exceeds the ceiling, or one under 1.0 |
| P5 | The rendered `site/value-arms` page moves: the selection leg's block gains a named decisions/renewals row where today it ends at the refusal | the door test passing against the pre-change feed |

**P4 is the one I am least sure of and it is the interesting one.** If it holds, the honest sentence
is not "no book can" and not "here is the book" — it is *"which book depends on which figure you
mean, and the page publishes one of them as its headline"*. That is the definitional split this
project keeps paying for, arriving one more time.

## What this does NOT establish, and must say so on the page

- **The split itself.** `V_rest` is unmeasured on this book. Every number here is the `V_rest = 0`
  corner, i.e. the most optimistic book in the family. The page must say the real book is larger.
- **Whether growing the book is a lever at all.** `where_the_priced_decisions_come_from` on the
  older book found 26 of 67 priced accounts were drawn households. Not re-measured here.
- **The nine-seed mean is itself an estimate** with SEM £603.50. Pricing against it prices against a
  centre that is not established to be non-zero.

## Correction policy

If any of P1–P5 is refuted, the refutation is written into this file beside the prediction and the
page states what was measured, not what was predicted.

---

## RESULT, recorded 2026-09-09 beside the predictions above

Measured from `docs/observability/value_cycle_ab_s1_noise_floor.json` (9 seeds, mode `all`, world
`39a192ce04c1eda8`, `selection_gbp` variance 3,277,913 GBP²) against
`value_cycle_ab_s1_three_arm_20260908.json` (the run the `current_world` panel publishes: 214 priced
decisions of 2,035 renewals offered, `selection_gbp` = £270.21).

| # | Predicted | Measured | Verdict |
|---|---|---|---|
| P1 | ~45× | **44.90×** | **HELD** |
| P2 | ~9,600 decisions / ~91,000 renewals | **9,608 / 91,331** | **HELD** |
| P3 | ceiling ≈ 3.9×, so P1 unattainable | **REFUTED — the comparison cannot be made at all** | **REFUTED** |
| P4 | ~2.8× against the nine-seed mean, inside the ceiling | **2.82×** (604 decisions / 5,742 renewals); "inside the ceiling" falls with P3 | **HELD on the number, and its second clause dies with P3** |
| P5 | the rendered page moves | the selection leg's block now renders both rows; four poison rounds on the render each red | **HELD** |

### P3 is the one worth reading, and it was refuted before it reached the page

I predicted the settled-book ceiling would settle attainability at ~3.85× (632 accounts against this
book's 164). It does not, and the reason is this project's own recurring shape: **632 and 164 are not
the same quantity.** `settled_book_ceiling(years=1)` is customers × ONE year against a memory budget;
the book's 164 accounts are counted over a TEN-year window. The same function at `years=10` returns
**63** — fewer than the book that demonstrably runs today. A ratio of those two numbers would not be
a quantity, and I had already written it into P3 as though it were.

So the page states the requirement and states **no verdict on reachability**, and says so in
`what_would_settle_the_sign.what_is_not_established` rather than in a footnote. What would settle
reachability is a settled-book ceiling stated over the window this book actually runs — a
measurement nobody has made, and one this block must not be read as having made.

### What the answer turned out to be

Neither "here is the book" nor "no book can" — it is **both, depending on which figure you mean**,
and that is the finding:

* to give **the published draw** (£270.21) a direction: more than **44.90×** this book — ~9,608
  priced renewals out of ~91,331 the world must offer;
* to give **the centre of its own nine-seed re-draw family** (−£1,078.17) a direction: more than
  **2.82×** — ~604 priced renewals out of ~5,742.

An order of magnitude between them, and the two figures are on opposite sides of zero. Both are the
`V_rest = 0` corner, so both are lower bounds and the real books are larger. Filed as
`SEAT_FINDING_THE_BOOK_THAT_WOULD_SETTLE_THE_SELECTION_SIGN_DEPENDS_ON_WHICH_FIGURE_THE_PAGE_MEANS_2026-09-09.md`.
