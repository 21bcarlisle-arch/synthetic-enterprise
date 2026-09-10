**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the page certified a book this world can supply, from an upper bound, read at the wrong window, in the wrong population

RECORDED rather than BLOCKING: the defect is discharged by the commit this document is filed with,
and the claim it produced is off the page. It is written up because the *shape* recurs — three
independent reasons a comparison was not a quantity, all pointing the same way, all composed
correctly from figures that were each individually right.

**Filed:** 2026-09-10, delivery seat. Drawn as Lane 0 delivery; the drawn premise —
`current_world.what_would_answer_it` being `None` — was already spent on origin at `fd9d6292a`, so
the work is item 2 of its own finding's "what is next":
`SEAT_FINDING_THE_BOOK_THAT_WOULD_SETTLE_THE_SELECTION_SIGN_DEPENDS_ON_WHICH_FIGURE_THE_PAGE_MEANS_2026-09-09.md`,
which named this and said in terms that it was **not** repaired there.

---

## What the reader was told

Twice on `site/capabilities/`, under both cuts of the method-skill panel:

> "The settled book can hold **632 accounts**, so a book this world can supply **does reach it** —
> and that is a statement about the instrument, never a plan."

Every number in it was real. The sentence was composed from the verdict rather than written beside
it, which is the control this file's own history exists to enforce, and that control worked. What
was wrong is that the verdict had no arithmetic under it.

## Three reasons, and each one alone is enough

**1. The window.** `settled_book_ceiling` is per customer-YEAR — it divides its memory budget by
`years`. `CEILING_SOURCE` read it at `years=1` and got 632. The requirement it was compared against
is in accounts counted over the run's **whole window**. The same function returns **63 at
`years=10`**, which is fewer than the **164 accounts this book demonstrably settles**. A bound the
observed system already exceeds is not a bound; that is how a reader could have caught it without
running anything.

**2. The population.** The ceiling counts the **settled book**. The requirement was stated in
accounts that carried a **scored decision** — a subset. On this run they are **72 and 164**. So the
requirement understated the book it needs by 2.3×, in the same direction as the window error. The
same mistake was one field along in `scored_decisions_at_the_ceiling`, which multiplied a
settled-book count by a decisions-per-*scored*-account rate and so placed the ceiling further right
on the published curve than it belongs — flattering, not merely wrong.

**3. The direction, and this one survives fixing the other two.** The ceiling is an **UPPER** bound.
Its own block says so, in words that were already on the page: *"the affordable book is SMALLER than
this number and never larger"*. The verdict was `needed <= ceiling`. That inequality establishes
**nothing**: the real book is smaller than the ceiling and may be smaller than the requirement too.
Only `needed > ceiling` was ever safe. `tools/inference_claim.settled_book_ceiling_accounts` had the
asymmetry written into its docstring — *"which is the direction that makes an 'unattainable' verdict
safe"* — and the code twelve lines below returned the other one.

## What the corrected comparison says

| | published | corrected |
|---|---|---|
| requirement | 162 scored-decision accounts | 369 settled accounts |
| ceiling | 632 (at `years=1`) | 63 (at `years=10`) |
| verdict | **attainable** | **not attainable**, by 306 accounts |

The right-hand column is *illustrative and is not what the page now publishes* — the run declares no
window, so the honest verdict is **`None`**, and that is what ships. But the direction is worth
recording: the repaired comparison does not merely fail to support the old verdict, it points the
other way by roughly a factor of six.

## What ships instead

`the_observed_effect_is_attainable` is now **`False` or `None`, and `True` is not a value the
arithmetic can produce at any effect size** — swept and asserted across the instrument's whole
range. The live feed carries `None`, with the cause in the reader's own sentence:

> "Whether this world can supply that book, this page cannot say. The settled-book ceiling is stated
> per customer-YEAR and the window these accounts are counted over was not supplied, so there is no
> window to read it at — 632 accounts for a one-year book and 63 for a ten-year one are the same
> function, and picking one would be picking an answer. It is a bound on the instrument either way,
> and never a book to grow towards."

`what_would_make_a_verdict_available` names three things, and the third is the point: **no amount of
the first two turns this verdict positive.** Certifying reach needs a LOWER bound on the affordable
book, and this project does not have one.

## A control that passed for the wrong reason, caught by its own poison round

The door assertion was first written against the whole `arms-method` panel. Blanking the survivor
cut's render left it **green** — because the estimand's cut renders the *identical* refusal about a
different population, so the panel still contained every string asserted. Found by poisoning one
panel rather than both, which is the only way the two are distinguishable. Now scoped to the
survivor cut's own region, on the split this file already uses for exactly this hazard, and
re-poisoned red.

## What landed

* `tools/inference_claim.py` — `_attainability` (one-sided by construction, returning the reason
  beside the verdict), `settled_book_ceiling_accounts(window_years=...)` with no default and a named
  refusal, the settled/scored population bridge, and the affirmative branch deleted from
  `_detectability_sentence` so no verdict has one to reach.
* `tools/generate_value_arms_data.py` — both call sites, with the reason neither `window_years` nor
  `settled_book_accounts` is passed. The second is deliberate: that count is `book_identity`, which
  `_book` withholds on unlabelled provenance, and passing it here would republish a gated count
  under a different key.
* `site/data/value_arms.json` — regenerated. Both blocks refuse.
* `tests/tools/test_the_concordance_curve_says_what_it_could_have_seen.py` — four new controls, one
  rekeyed from today's answer to the property. Six declared mutations run and reverted; all six
  fired. M1 (restoring the `True` verdict alone) does **not** fire the reader-sentence control, and
  the docstring says so rather than claiming coverage it does not have — it takes both controls.
* `site/test_the_baseline_comparison_reaches_the_reader.py` — the dead `True` branch replaced by the
  refusal branch the live feed actually takes, region-scoped and poison-checked.

## What is next

1. **A window declared by the producer.** `value_cycle_ab_s1_three_arm.json` carries
   `billing_accounts_settled_in_window` and a null `report_end`, and names the window nowhere. One
   field closes the units half of this for every consumer.
2. **A LOWER bound on the affordable book.** Without one, no surface in this repo can ever state
   that a remedy is reachable — only that it is not. That is a real limit on what the director's
   thesis can be shown to have met, and it is currently unowned.
3. **`method_skill.the_book_this_would_need` was item 2 of the 2026-09-09 finding and is now
   discharged. Item 1 (the two missing floor legs) and item 3
   (`where_the_priced_decisions_come_from` measured on the other book) are not**, and item 1 is
   many machine-hours rather than one turn's work.
