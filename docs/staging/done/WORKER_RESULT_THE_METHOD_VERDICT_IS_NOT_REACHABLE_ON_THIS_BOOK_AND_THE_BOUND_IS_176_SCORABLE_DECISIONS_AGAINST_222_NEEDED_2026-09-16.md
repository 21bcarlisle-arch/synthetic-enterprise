**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — is-the-method-verdict-reachable-on-this-book-at-all)

# The method verdict is not reachable on this book, and the bound is 176 scorable decisions against 222 needed

**2026-09-16, scheduled tick, delivery seat.** The Lane 0 direction was that the page which
answers the director's thesis returns "we cannot tell", and that the curve saying what WOULD
settle it read null on the ceiling of every row — so a reader could not separate *not yet* from
*not ever here*, and that separation is what decides whether the next stretch improves the arm or
widens the book. It is now stated, from data that was already inside the artefact.

## The answer

**The observed excess is NOT resolvable on this book.** Reading the departure this run saw
(concordance 0.544, an excess of 0.044 over no-information) needs about **222 scored decisions**.
This book yielded **170**, and at most **176** of its **280** decisions were ever scorable. It is
46 short of the most this book could ever have supplied, so the verdict needs a **wider book** and
not more work on this one.

R12: that is a bound being reported, never a book size to grow towards. A book grown until this
arm returns a direction is the failure the arm exists to be able to report.

## Where the ceiling came from, and why the old one could not supply it

`within_the_settled_book_ceiling` reads `None` on every row and **still does**, correctly. It is
priced against the settled book's ACCOUNT ceiling, which is stated per customer-year and refuses
without a declared window — and it is an UPPER bound, so it can refuse and never certify.

The second ceiling was in the artefact all along and nothing read it. The run's own drop-out
funnel reconciles **170 scored + 110 dropped = 280 logged** and classes every one of the 110. That
is a bound in DECISIONS — the same unit and the same population `decisions_needed` is stated in —
so it needs no window and no account bridge. It is exactly what the 2026-09-10 repair could not
have: a bound counted over the population the requirement is counted over.

| count | what it counts | direction |
|---|---|---|
| 280 `decisions_that_existed` | renewals at which a per-customer decision existed | context, not a bound |
| 176 `scorable_ceiling` | 170 scored + 0 join + 6 coverage | UPPER — refuses only |
| 170 `decisions_scored_this_run` | what the book actually yielded | LOWER, attained — certifies |

The 104 between 280 and 176 are 65 the arm declined (no price exists to rank) and 39 the world
never billed under the price that was chosen (no outcome to rank against). Both are properties of
what happened. Neither is recovered by code or by sourcing — only by a wider book.

## Which population each figure is counted over, stated before any of them is divided

This is the clause the direction asked for first, and it is now `inference_claim.DECISION_POPULATIONS`
rather than prose anyone can skip:

- **the concordance** — 170 decisions on 73 accounts: priced renewals that SETTLED.
- **the decision ceiling** — 280: renewals at which a decision existed. A SUPERSET, by the run's
  own reconciliation, which is why the comparison is a quantity at all.
- **`decisions.auc_population`** — 124 on 66 accounts, 85 retained against 39 who left. **A THIRD
  SET.** It scores a CHURN belief against whether a household departed, not a renewal price
  against value created. No ceiling on this block bounds it, and it is named here because it sits
  a few hundred pixels away on the same page and is the obvious thing to divide by next.

## Two ceilings, two fields, deliberately not merged

The direction said to fill `within_the_settled_book_ceiling`. **That field was left alone**, and
the reason is the failure this whole block was built to have stopped making: it is counted over
settled-book ACCOUNTS and can never certify, while the new verdict rests on a REALISED count and
therefore can. One name with two answers is *average unit rate* arriving again. The row now carries
`reachable_on_this_books_decisions` (tri-state) beside it, and `verdict_rests_on` naming which of
four branches fired. Every published row is filled; none reads `undecidable`.

`_attainability` is untouched and still has no `True` branch.

## What can refuse it

- `test_all_three_book_verdicts_are_reachable_and_the_bound_is_what_moves_them` — the whole
  partition over ONE fixed requirement (the 0.05 rung, 177 decisions), moving only the bound. A
  verdict frozen on a single leg passes every per-branch test and nothing else here would see it.
- `test_the_ceiling_is_what_is_scorable_and_never_what_the_book_decided` — fires on using 280 as
  the bound, which is a fail-open by 104 decisions, and closes the arithmetic for the reader.
- `test_a_funnel_that_does_not_add_up_or_carries_an_unknown_class_bounds_nothing` — an unknown
  drop-out class refuses rather than landing on either side; the permissive reading would make the
  ceiling TIGHTER and its refusals therefore unsafe.
- `test_the_two_routes_to_the_decision_population_have_to_agree` — the renewal funnel's stage
  counts and the arm's own decision log both say 280 today; a run where they disagree refuses
  rather than picking one.
- `site/test_the_baseline_comparison_reaches_the_reader.py::test_the_page_says_whether_that_floor_is_reachable_on_the_book_that_actually_ran`
  — scoped to the survivor cut's own region, expected clause built from the FEED's counts.

## What this does not settle

It says nothing about whether a LARGER book puts decisions in the eligibility class. The funnel's
own class description refuses that question by name and this ceiling inherits the refusal: the
claim is about THIS book only.

It also leaves the other three `detectability` callers — `fixed_horizon`, `churn_auc_within_year`,
`decisions.discrimination_auc_within_year` — reading `undecidable` on every row, because none of
them carries a drop-out funnel of its own. That is fail-closed and honest, and it is the next
thread: those cuts score different populations and each would need its own reconciled funnel
before a ceiling could be put to it.
