**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — the book that would settle the selection sign is 44.9× or 2.8×, depending on which figure the page means

RECORDED rather than higher: nothing published was wrong. The page refused correctly, and its
refusal was complete as far as it went. What was missing was the other half of the result — what it
would take — and that gap is now closed on the rendered page. The finding proper is the shape of the
answer: it is not one number.

**Filed:** 2026-09-09, delivery seat (isolated worktree).
**Pre-registration:** `docs/staging/records/SEAT_PREREGISTRATION_WHAT_A_LOWER_BOUND_ON_THE_SELECTION_REMEDY_MUST_SHOW_2026-09-09.md`,
written before the arithmetic ran, with the refuted prediction (P3) recorded beside the result.

---

## The state the page was in

`site/data/value_arms.json → current_world.selection_leg` publishes £270.21 against a ±£1,810.50
nine-seed bound, states that the nine re-draws fall on both sides of zero so the quantity carries no
sign — and stopped there. `current_world.what_would_answer_it` was `None`, because that key knew one
cause only (a missing bound) and every bound had landed.

The page's one piece of remedy arithmetic, `floor_decomposition`, refuses itself twice and both
refusals are right: it was measured where the arm priced **104 of 2,009** renewals against this
page's **214 of 2,035**, and it splits `value_advantage_gbp` and not this leg. So the reader who
reached the page's central refusal — on the only leg that could be value CREATED rather than
MOVED — had nowhere to go.

## What was done instead of the full decomposition, and why it is not a smaller version of it

A full decomposition on this book needs the `only` and `except` floor legs re-run at these nine
seeds: nine full three-arm decade passes each, at a measured ~6.4 GB peak, one at a time. Many
machine-hours, and not one turn's work.

But the requirement is **bounded below without them.** Write `V` for the leg's own nine-seed
variance, `V = V_priced + V_rest` for the split those legs would measure, `c` for the contrast.
Growing the priced book by `m` shrinks the priced half as `1/m` and leaves the rest of the book's
churn cascade alone, so the page's own rule (`_resolvable`) is met when

    V_rest + V_priced/m <= c^2    =>    m = (V - V_rest) / (c^2 - V_rest)

With `V > c^2` this has derivative `(V - c^2)/(c^2 - V_rest)^2 > 0`, so **`m` is strictly increasing
in `V_rest` and `m >= V/c^2`.** The corner where the whole spread is the priced households' own draw
is the cheapest member of the family. The two missing legs can only move the number **up**.

A bound that can only be optimistic is safe under "not enough" and unsafe under "enough" — so the
page prices the requirement and states no verdict on whether it can be met.

## The result: the answer is two answers, and they are an order of magnitude apart

| To give a direction to | Which is | Book must be | Priced renewals | Renewals the world must offer |
|---|---|---|---|---|
| the published draw | £270.21 | more than **44.90×** | 9,608 | 91,331 |
| the centre of its own re-draw family | −£1,078.17 | more than **2.82×** | 604 | 5,742 |

Against this book's 214 priced renewals of 2,035 offered. Both are lower bounds.

**The two figures are on opposite sides of zero and are answered by books sixteen times apart.**
Publishing either alone would be the page choosing which reading of its own refusal to answer —
`average unit rate`, `net margin`, `bill shock`, the journey's end with two homes, arriving one more
time on the sentence written to end that class. So both render, each with what it counts.

## What was refuted, and it was mine

P3 predicted that `simulation.premise_population.settled_book_ceiling` would settle attainability:
632 accounts against this book's 164, so ~3.85×, so 44.90× unreachable. **That comparison cannot be
made.** 632 is customers × ONE year against a memory budget; the book's 164 accounts are counted over
a TEN-year window. The same function at `years=10` returns **63** — fewer than the book that
demonstrably runs. Two numbers that are not the same quantity, and I had written their ratio into a
prediction as though it were one.

So no reachability verdict is stated, and the page says so where a reader meets it rather than in a
footnote.

## What is next

1. **Run the two missing floor legs** (`--redraw-mode only` and `except`, nine seeds, this book).
   They cannot change the direction of any statement above — the numbers only rise — but they turn
   two lower bounds into two measurements, and they would answer whether the rest of the book's
   churn cascade alone already exceeds either contrast, which is the "no book of this shape can"
   verdict this page still cannot state.
2. **Establish a settled-book ceiling over the window the book actually runs.** Until then no
   attainability claim about ANY of this page's remedies is available — including the one
   `method_skill.the_book_this_would_need` already makes at `years=1`, which is the same units
   question one panel down and is **not** repaired here.
3. **`where_the_priced_decisions_come_from` is measured on the other book.** Whether growing the
   book reaches this arm at all is unestablished on the book the page publishes.

## What landed

* `tools/generate_value_arms_data.py` — `_what_would_settle_the_sign` (priced on this book, this
  leg's own spread, this contrast, reusing `remedy_price_table`) and `_what_would_answer_it`
  (two causes, each naming itself and its own different work).
* `site/capabilities/index.html` — `whatWouldSettleIt`, rendered directly under the refusal in
  `legVerdict`.
* `tests/tools/test_generate_value_arms_data.py` — six controls, five declared mutations each run
  and reverted. One of them (M1) was found to pass a control **vacuously** by emptying its loop;
  the control now asserts its own subject is non-empty, and the note says why.
* `site/test_the_baseline_comparison_reaches_the_reader.py` — three door controls against the real
  feed, four poison rounds on the render each red.
