# The flat churn belief now reaches a reader, and the book it is measured on is not this page's

**2026-09-22, delivery seat.** Lane 0 item `publish-the-flat-churn-belief-block-on-the-arms-page`.
Landed; the claim is released.

## The premise, re-measured before any work

The draw flagged `7179a7087` as already an ancestor of `origin/main`. It is — and that is the
item's premise rather than its subject. The item commissioned the **publication**, explicitly
naming the measurement as done. Re-measured at draw time:

| The item's claim | What the tree said |
|---|---|
| the measurement is landed | true — `tools/churn_belief_size_response.py` and its artefact are identical to HEAD |
| `tools/generate_value_arms_data.py` holds the publication | false — HEAD carries no churn block; the working copy was another lane's mix |
| `site/capabilities/index.html` is dirty | false — identical to HEAD, so the render was genuinely owed |

So the premise was **live, not spent**. The path note's `already landed` tags were correct about
the measurement and correct that nothing was owed there.

**The duplicate-work check named `the-companys-churn-belief-is-flat-across-the-book-where-the-
world-responds-nine-fold`.** It is NOT this item. That claim holds the five MEASUREMENT paths
(`tools/churn_belief_size_response.py`, the artefact, its test, `process_run_complete.py`, its
seat record) and no site or generator path at all; the live claims file says so, against the
draw note's assertion that it holds `site/data/value_arms.json`. Measurement and publication,
two claims, no overlap in paths. Carried on rather than taking a disposition.

## What landed

A block in `tools/generate_value_arms_data.py` (`_churn_belief_size_response`) that READS
`docs/observability/churn_belief_size_response.json` and derives nothing, a render in
`site/capabilities/index.html` immediately under the error bar, the regenerated feed, and two
test files — the door test for the render and four legs in the producer's own suite for the
refusals the door test structurally cannot reach.

The page now carries the artefact's own sentence, word for word: the belief is flat in household
size for 235 of 244 supply legs, over a book where the world's churn response spans 11.57x.

## The thing worth flagging, and it is the caveat and not the finding

**This artefact's book is not the book the arms above it are scored over.** It cuts the 244 supply
legs `site/data/customers.json` holds; the comparison it now sits inside is scored over 154
accounts whose per-account rows are not persisted anywhere. Whether the 154-account book falls
differently against the knee is **NOT ESTABLISHED**, and reconstructing it means re-running the
arms.

That is why the artefact's own `population_is_not_the_published_arms_book` string is rendered
verbatim on the panel rather than paraphrased, and why the door test's load-bearing leg is the one
that reds when it is dropped. A count over one population rendered inside a section scored over
another, with nothing saying so, is this project's recurring shape — and adjacency alone would
have made a reader do the join.

**Still owed, and not by this item:** the knee cut over the 154-account book. It needs an arms
re-run, so it is not a turn's work.

Second flag, carried onto the surface rather than into a footnote: `BILL_STRESS_THRESHOLD_GBP`
sets where the knee falls and appears in this repo's own register of domain constants carrying no
origin. Reported, not repaired — re-picking an unsourced number replaces one invention with
another. The page marks it amber where a reader meets it.

## R15 — the sweep, run before landing

Twelve mutations, each caught by the leg written for it.

*Render (7):* delete the assignment → 12 legs red · print the reading as a literal → 3 (the two
neighbours read the same sentence and say so) · render the asymmetry verdict unconditionally → 1 ·
drop the population caveat → 1 · collapse the three-valued segment column to two branches → 1 ·
style the finding muted instead of amber → 1 · drop the unsourced-threshold caveat → 1.

*Producer (5):* drop the knee-is-a-bill refusal → 1 · drop the book refusal → 1 · re-word the
reading at publish time → 1 · move the block below the `available` gate → 1 · hard-code a count
→ 1.

**One mutation did not fire on its first run and the reason was mine, not the control's.** The
sweep's anchor `"reading": reading,` occurs twice in a 13,000-line generator and
`str.replace(old, new, 1)` took the other one, 6,600 lines away. Re-run against a unique anchor it
fires. Recorded because the flattering reading of a silent mutation — "that must be an
equivalence" — was available and wrong, and the cost of establishing which was one grep.

## Why the block sits above the `available` gate

It is not a reading of the A/B run. "The choosing found nothing" and "we could not run the
comparison" are the two states a reader of this page confuses, and the account of why the choosing
has little to find is true in both — so withholding it when the run artefact is unreadable would
withhold it exactly where it is most needed. `test_the_block_is_published_even_when_the_AB_RUN_
cannot_be_read` is the leg that keeps it there.
