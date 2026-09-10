**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the withdrawn concordance has a priced route out, and the one it had was indexed on the wrong unit

RECORDED rather than BLOCKING: the defect is discharged by the commit this document is filed with,
and both answers are on the page beside the withdrawal. Written up because two of the four findings
generalise — a remedy quoted in the unit the reader met the figure in rather than the unit the law
indexes on, and a sample count published under a population label in the block a remedy divides by.

**Filed:** 2026-09-10, delivery seat. Drawn as Lane 0 delivery:
`what-run-would-settle-the-within-year-concordance-and-can-this-world-supply-it`.

---

## What the reader was told

`site/capabilities/` withdrew its household claim on 2026-09-10 — correctly. The within-year
concordance is **0.444 on 402 same-year pairs against a null of 0.376–0.619**, inside it, so the
words *"real information about who stays"* came off the page. What the reader then met, about
earning it back, was one clause:

> "On 402 same-year pairs this sample cannot tell either way; about four times as many would halve
> the interval."

No book size, no cost, no route. The **selection leg on the same page** got a priced route in
August — `what_would_settle_the_sign`, 2.8× or 44.9× this book, both counts stated, the corner
named as a lower bound. The leg that carries the director's thesis got a shrug.

## Four findings, and the first is the one that recurs

**1. The remedy was indexed on the wrong unit, and the error is a factor of four.** The permuted
half-width falls as `1/sqrt(DECISIONS)`. Same-year pairs grow as the **square** of decisions. The
sentence's own subject was `same_year_pairs` — "402 … about four times as many". Four times the
pairs is twice the decisions and a **29%** narrower interval, not half. Halving it takes four times
the decisions, which is **sixteen** times the pairs. Measured, not argued: permuting the stratified
null at n = 123/246/492/984 gives scale constants within 5% of each other.

This is the project's most expensive recurring shape wearing new clothes — a figure quoted in the
unit the reader happens to hold rather than the unit the law is stated in. Nothing was wrong with
either number.

**2. The account count in the block a remedy divides by was a sample count.**
`decisions.auc_population.accounts` published **17** for a population of **66**. It read
`len(accounts)` where `accounts` came from the artefact's `matched_sample` + `unmatched_sample` —
ten rows each. Three hundred pixels away the same block's reading says "123 decisions on 100
accounts", and the noise floor's every seed row says `accounts_redrawn: 66`. Three account counts,
one population. Reading 17 into `detectability` would have overstated the required book by nearly
four times.

**3. Re-running seeds looks like the cheap route and is not one — and the demonstration is exact.**
`price_elasticity_for_customer` is a pure function of `(customer_id, seed)`, so a re-seed re-rolls
the **same 66 households**. Pooling *s* seeds multiplies decision ROWS by *s* and leaves the belief
values, and therefore the ordering a concordance reads, exactly where they were. Replicate this
run's 123 rows unchanged and:

| copies | rows | same-year pairs | concordance | null | outside? |
|---|---|---|---|---|---|
| 1 | 123 | 402 | 0.444030 | 0.373–0.621 | no |
| 2 | 246 | 1,608 | 0.444030 | 0.414–0.586 | no |
| 4 | 492 | 6,432 | 0.444030 | 0.441–0.558 | no |
| **5** | **615** | **10,050** | **0.444030** | **0.446–0.552** | **YES** |

Five copies of one book — not one new observation — manufactures exactly the result this page is
being asked to earn, and **at almost the multiple the honest arithmetic demands (4.75×)**. That
coincidence is why the refusal is published beside the requirement rather than left to the reader.

**4. No book size makes the grading population independent, and the obvious repair is worse.**
Four accounts (C5_2, PROS-2019-0024, PROS-2021-0324, SYN-2016-034) left under the value arm and not
under the control; one (PROS-2018-0137) left under the control and not the value arm. **12 of the
123 scored rows and 4 of the 40 departures** sit on those five. "Score only the accounts both arms
agreed about" conditions on a **post-treatment** variable — the subset is defined by the outcome and
removes exactly the cases where the price bit. It would make the figure look cleaner and mean less.

## What ships

| | before | after |
|---|---|---|
| route out of the withdrawal | one clause, no book, no cost | priced, on the page, in both units |
| requirement | — | **584 scored decisions (4.75×)**, ~314 accounts, 9,062 same-year pairs |
| the book | — | **~1,017 priced renewals of ~9,668 the world must offer** |
| seeds | unasked | **refused, with the replication table as the evidence** |
| cost of the run we have | — | **≥1.16 machine-hours, ≥6.4 GB peak, serial** |
| cost of the larger book | — | **not established** — one clean probe point, no slope |
| `auc_population.accounts` | 17 (a sample) | 66 (the population); the sample keeps its own name |
| attainability | — | **`None`**, and `True` is not a value the arithmetic can produce |

The arithmetic is `tools.inference_claim.detectability`, **called and not copied** — the same
function the two method-skill cuts already use. Neither `window_years` nor `settled_book_accounts`
is passed, for exactly the two reasons those call sites give, so the attainability verdict is `None`
with its cause named and the cost block is what answers "can this world supply it".

## Controls, and both surfaces are graded

`tests/tools/test_the_within_year_remedy_is_indexed_on_decisions.py` (6) and four new tests in
`site/test_the_stratified_concordance_reaches_the_reader.py`, whose subject is the **rendered
element the withdrawal is in** — a remedy three panels down is a remedy the reader who met the
withdrawal never sees.

Two of the six are measurements rather than assertions and are the ones that can refuse the block:
the `1/sqrt(decisions)` law permuted at four sizes, and the replication table above.

**The null control is the load-bearing one.** `test_a_probe_that_HAS_a_slope_takes_the_refusal_off_
the_page` asserts the OTHER branch is reachable before anything is asserted about the live one. My
own first draft of the cost render hard-coded *"What the larger book costs is not established"* — a
sentence that would have gone on saying it on the day `settlement_ceiling_probe` lands its second
clean point, which is the outcome the block exists to make worth having. Keyed to today's answer,
caught by writing the null control rather than by rereading the render.

R15 — nine mutations, each fires on a named test:

* `times_this_runs_pairs = multiple` instead of `multiple²` → `..._stated_in_both_units_...` red.
  This is finding 1 restored.
* `accounts = 17` → `..._the_population_and_not_the_artefacts_sample` red.
* a `machine_hours` figure added to the **refused** larger-book block →
  `..._refuses_to_price_a_larger_book_...` red. The fail-open shape: a reader takes the number and
  drops the caveat.
* "dropping them" offered as the repair → `..._not_repaired_by_dropping_...` red.
* the whole remedy paragraph dropped from the door → three door tests red. Fail-silent: the feed
  keeps it and the reader never meets it.
* the pair count dropped from the render → `..._route_out_...` red. Finding 1 on the page.
* the independence paragraph dropped → `..._would_not_make_the_grading_population_independent` red.
* the "not established" refusal dropped from the cost render → `..._never_prices_a_larger_book_...`
  red.
* the refusal pinned to a string rather than to `recommendation.decidable` →
  `..._HAS_a_slope_takes_the_refusal_off_the_page` red. This is the draft I actually wrote.

## What is next

**The cheapest thing on this page is not in the table above.** Every figure in
`what_would_settle_it` needs a bigger book. The independence gap needs **one field**: the control
arm's own `(account, term_start, retained)` rows, recorded on the same schedule
`belief_vs_outcome.scored_decisions` records the value arm's. Both arms already run in one pass on
one world, so it costs **no extra pass at all** — and it is the only route to grading the belief
against an outcome the belief did not cause. That is the next item.

Not done here and not blocking: the `-1` on the `I001` ratchet in the shared tree is another lane's
uncommitted improvement over the frozen baseline, green in a clean HEAD extract. Not banked —
freezing from a dirty tree wedges every lane.
