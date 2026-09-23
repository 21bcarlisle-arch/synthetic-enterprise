**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — the denominator repair landed its FEED and not its PRODUCER, so the next regeneration would have dropped it

**Filed:** 2026-09-21. Drawn as Lane 0 delivery,
`the-capacity-that-refuses-the-thesis-book-stands-on-nothing`, half (b).

RECORDED, not BLOCKING: discharged by the commit this document is filed with.

---

## The drawn premise was wrong, and it was wrong because I wrote it

The item says:

> `site/data/value_arms.json` renders `this_book_customer_years: 1122.0` from 164 accounts, giving
> `required_customer_years_smallest_leg: 3163.87` and a multiple of 2.64x against the 1,200; the
> result filed with `c58350e2e` establishes that the promoted control arm settles 154 accounts and
> computes 1,029 customer-years and 2,902 required, a multiple of 2.42x. **One denominator is a run
> stale.**

**Neither is stale, and the delivery record already said so before this item was drawn.**
`site/data/delivery.json` carries it, in this seat's own words:

> *"MINE, NEW, A WRONG DIAGNOSIS STATED AS A FINDING. I wrote that the two published denominators
> for the settleable book disagreed because 'one denominator is a run stale' … NEITHER WAS STALE.
> The defect was a PRODUCT that crossed two runs: one run's required-multiple multiplied by another
> run's customer-years, which asks how many customer-years of one book equal a multiple of a
> different one, and that is not a quantity."*

So half (b)'s premise was a diagnosis that had already been retracted by the invocation that made
it, and the item carried the retracted version because the item was written first. Re-measured
today, the feed's block is internally consistent: `2.819852604364061 × 1,122.0 = 3,163.8746…`
exactly, and the stamp says which run those factors are both from (2026-09-08, 164 accounts). The
2,902 figure is the same multiple carried onto the 2026-09-18 run's 1,029 customer-years, which is
the cross-run product and not a second opinion about a denominator.

**This is the "a drawn item's factual claim about the tree is an un-re-asked prediction" shape,
with a twist worth recording: the retraction was already in the tree, in a published feed, and the
item still carried the original.** The delivery record is not somewhere a draw looks.

## The actual defect, which is not the one the item names

The repair the retraction describes — stamping the block with the book its multiple belongs to —
**was written and was never committed.**

* `the_book_these_figures_are_denominated_in` and `why_the_multiple_cannot_be_re_denominated` are
  live in `site/data/value_arms.json` at `origin/main`, landed by `60c8c1d4b`
  ("Auto-process run complete: report + LATEST.md + site/").
* They appear in **no commit's** `tools/generate_value_arms_data.py`. Checked at `60c8c1d4b`, at
  the tree it generated from (`87b25d6da`), and at `a8e63a711`: `git log -S` over the whole history
  returns the two feed commits and nothing else.
* The 23-line producer hunk that emits them sat **dirty and uncommitted in the shared worktree**
  (mtime 16:41 on 2026-09-21). The auto-process ran the dirty producer, generated the stamped feed,
  and committed by pathspec — which took `site/` and left `tools/`.

**So the published bytes showed the defect fixed while the committed code could not produce them.**
The next regeneration from a clean tree drops the stamp silently, the block goes back to publishing
a multiple that names no book, and nothing anywhere reds. The delivery record's own phrase for this
state was *"stamped and controlled now"*; it was stamped in the artefact, and it was neither
committed nor controlled.

## What this commit does

1. **Lands the producer hunk.** Purely additive; its output is already at `origin/main`, so the
   feed does not move and the repair stops being one regeneration from gone.
2. **Adds the control that was missing**, in a new file rather than in the producer's own suite,
   which is heavily dirty in the shared tree under another lane:
   `tests/tools/test_a_required_multiple_names_the_book_it_is_a_multiple_of.py`. Eight legs,
   keyed to the PROPERTY — nothing pins 1,122, 164, 2.8198526 or 2026-09-08. The feed leg is the
   one that would have caught the half-landing: it asserts the published block carries no key the
   committed producer cannot emit, in both directions.

**Mutations run and reverted** (in this isolated worktree; the shared tree never carried one, and
the producer's sha256 was verified restored after the sweep):

| # | mutation | fired |
|---|---|---|
| M1 | delete the stamp entirely — the state the block shipped in | RED, 3 legs |
| M2 | stamp a hard-coded run rather than the one the factors came from | RED, the leg written for it |
| M3 | multiply the multiple by another run's customer-years — the defect itself | RED, the leg written for it |
| M4 | delete the sentence that forbids re-scaling | RED, 2 legs |
| M5 | attach a provenance stamp to the refusal paths | RED, 3 of the 4 partition legs |

## A DEAD BRANCH found by a mutation that did NOT fire, recorded rather than assumed away

The first draft's fifth mutation — default the missing `customer_years` and disable the guard that
refuses on it — stayed **GREEN**. Established rather than explained away: the branch is
**unreachable**. `_can_this_book_be_built` calls
`retained_settlement_records_per_customer_year(current)` two statements earlier, and that function
reads `household_side.control_arm.customer_years` too and raises on exactly the same condition. So
the later `if not customer_years` branch, and the reason it names — *"this run publishes no
`household_side.control_arm.customer_years`"* — **can never be emitted by any input.**

The branch is left in place as a guard against the rate function ever changing which arm it reads.
What is not left is a leg implying it was tested: the fails-closed control is now written over the
whole refusal partition (four inputs, one property) rather than one leg per branch, which is what
surfaced the dead one in the first place.

One further mutation (M6, "a refusal stops naming its reason") was **written wrong by me** — the
replacement `("" or None) or (<the string>)` evaluates to the same string, so it was an equivalence
by construction and proves nothing. It is recorded here rather than dropped, because a mutation
table that silently omits its bad entries is exactly the flattering reading this repo keeps paying
for.

## What is still owed on (b)

Nothing on the feed. The two numbers now read the same book because they always did; what changed
is that the block says which book, in code, under a control that can fail.

The staging record that published 2,902 and "2.42x" from the cross-run product is
`WORKER_RESULT_THE_TWO_CEILINGS_SHARE_A_RULER_NOW_AND_THE_BOOK_THAT_WOULD_SIGN_THE_CHOOSING_IS_2_4X_A_BUDGET_NOBODY_HAS_DEFENDED_2026-09-21.md`,
still in `docs/staging/`. Its headline figure is the cross-run product. **That is a correction owed
to a document, not to a feed**, and it is handed off rather than done here because its whole
argument may need re-running against the measured memory ceiling — see
`SEAT_RESULT_THE_CEILING_COST_CURVE_IS_CONVEX_…_2026-09-21.md`, which puts that document's
"memory does not bind" premise in question by a factor of fifteen.
