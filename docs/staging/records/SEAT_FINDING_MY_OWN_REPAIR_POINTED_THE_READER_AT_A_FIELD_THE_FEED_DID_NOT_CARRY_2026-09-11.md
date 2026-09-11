**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# FINDING — the repair removed the wrong instruction and replaced it with a pointer to nothing

**Filed 2026-09-11, delivery seat.** Against my own work, one commit old. Repaired in the same
commit as this record.

---

## What was wrong

`9f570da6c` fixed a headline that told readers to **divide a booked count by 0.183** over a book
whose per-account weights span 259×. The replacement prose ends:

> "… each settled account carries its own weight in the company's own wins, and
> **`settlement_weight` on each row below** is what reads across to the supplier."

That was the *only* route to the supplier the new sentence offered — correctly, because under a
chosen sample no single number undoes the sample. And **`settlement_weight` reached no row of the
feed.** `generate_book_growth_data.build` copies `funnel_wins`, `wins` and the refusal count off
the campaign record into each published year row; it never copied the weight. The campaign record
has carried it since `3957ba848`.

So a reader who followed the instruction found nothing. Measured on the regenerated feed: all ten
published year rows, no `settlement_weight` key.

## Why it is the same defect wearing the opposite clothes

The sentence it replaced was dangerous because a reader **could** carry out its arithmetic and get
a wrong number silently. The sentence that replaced it is weaker but not harmless: a reader who
cannot find the field cannot read the supplier from the sample **at all**, and the page no longer
offers any other route — the divide instruction, which was right under the cull, is gone.

## Why no control caught it

**Every assertion was on the sentence.** `test_the_headline_tells_the_two_SELECTIONS_apart_and_
only_one_says_divide` asserts `"settlement_weight" in chosen_says` — the string is in the
sentence, the sentence is in the feed, green. The door test asserts the same string reaches the
rendered page — green. **Both ends of that assertion are the same end.** Nothing asked whether the
thing being pointed AT exists.

This is the class already in the register as *a pointer's referent can render nowhere, so probe
both ends and not just the pointer*, and I wrote the pointer end twice and the referent end zero
times, inside the same hour as writing a finding about a claim being fixed in one layer and not
the other. The general shape is the same one both times: **a repair is checked where it was
written, not where it is consumed.**

## The repair

`settlement_weight` is copied onto each published year row from the campaign record, `None` when
the record does not carry it — never `0.0`. A year that stands for nothing the company won and a
year we cannot speak for are different claims and `0.0` is the flattering one.

## The controls

`test_the_field_the_headline_SENDS_THE_READER_TO_is_on_every_row_it_sends_them_to` **reads the
field name out of the published sentence** and demands it of every row, rather than hard-coding
the string in the test as well — a control that spelled `settlement_weight` itself would agree
with itself and go green if the headline were re-worded to point somewhere else entirely.

`test_a_year_whose_record_carries_NO_weight_publishes_null_and_never_zero` holds the fail-closed
value down, and asserts the KEY is present before asserting the value is `None`: a missing key is
the dangling-pointer state and an honest `None` is not, and one control should not report them as
the same thing.

**Mutation-proven.** Deleting the one line that copies the weight onto the row reproduces the
shipped state exactly, and both controls fire. Restored, 29 pass.

## What this does NOT claim

It does not claim the published rows are now readable by a reader — `settlement_weight` reaches
the feed and the page's chart does not yet render it as a column. That is a further step and it is
handed on, named, rather than implied by this repair. **What is fixed is that the field the
headline names now exists in the bytes the page is built from**; what is not yet true is that a
reader sees it without opening the JSON.
