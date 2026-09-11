# A sample-bound control demands the divisor, and a chosen book does not have one

**Severity:** LATENT · **Lane:** H_harness

LATENT and not BLOCKING because nothing published is wrong and the control's own verdict still
stands: the assertion passes, and passes honestly. What has gone false is the sentence that tells
the next session what the assertion is *for*.

**Found:** 2026-09-11, while dooring the chosen-sample branches of `#arms-sample` and `#growth-note`.
**Subject:** `site/test_the_baseline_comparison_reaches_the_reader.py`,
`test_the_sample_bound_carries_the_producers_own_numbers_and_not_its_own`

---

## The claim

That control ends with:

```python
assert "{:.3f}".format(rate) in rendered, (
    "the page tells a reader the count is a sample without giving them the divisor that "
    "turns it back into the supplier: {}".format(rendered))
```

It was correct when written. Over a **uniform count cull** the rate genuinely is a divisor: divide
the settled count by 0.183 and you have the supplier. The control required the page to supply it,
and the remedy sentence said exactly why.

Since `3957ba848` the settled book is **chosen** for difference and every account carries its own
weight — on this book spanning 0.057 to 14.774, a 259.7x spread. **There is no divisor.** No single
number turns the book back into the supplier; `settlement_weight` on each row is what reads across.

## Why this is LOW and not MEDIUM

**The assertion still passes, and it passes honestly.** Both branches print `r.toFixed(3)` — the
cull as an instruction to apply, the chosen branch as *"dividing by 0.183 would be wrong"*. The
arithmetic the control performs is right. What has gone false is the sentence explaining what the
arithmetic is *for*.

So this publishes nothing wrong to a reader and blocks nothing. It is on the record because a
remedy sentence is what the next session reads when the control finally goes red, and this one will
send them looking for a divisor to add to the page. Adding it would be the defect.

## The related thing that was NOT low, and is already fixed

The same blindness had a serious half. Because that control keys on the divisor being *present*,
and `test_the_book_on_this_page_is_named_as_a_sample_of_the_business` keys on the word *"sample"*,
**both are satisfied by both branches**. Neither could discriminate a chosen book from a cull, and
neither was written to — they predate the chooser.

Measured rather than argued: poisoning the index so `#arms-sample`'s chosen branch falls through to
the cull prose left **145 tests green** while the published page told a reader of a chosen book to
*"divide it by 0.183 to read the supplier instead"*. That gap is closed by
`site/test_the_chosen_book_is_not_called_uniform_on_the_two_JS_built_anchors.py`, landed the same
day. The full measurement, including the four mutations and the two I did not pre-register, is in
`docs/staging/records/SEAT_PREREG_WHETHER_THE_CHOSEN_BRANCH_OF_ARMS_SAMPLE_AND_GROWTH_NOTE_IS_DOORED_AT_ALL_2026-09-11.md`.

## What is next

Re-word the remedy to the property rather than to the cull's mechanism — the page must give the
reader **whatever turns the count into the supplier**, which is a divisor under a cull and the
per-row weights under a chooser. Deliberately not done in the commit that added the replacement
door: changing a control's prose beside its new neighbour is how a correct fix stops being
attributable to either.

**Do not** simply delete the assertion. Under a cull it is load-bearing, and the cull branch is
still live for every campaign record written before 2026-09-11.
