**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# FINDING — the page stopped calling the book uniform; the FEED did not, and it is the feed that carries the divide instruction

**Filed 2026-09-11, delivery seat.** Found while taking the second of the two pieces
`3957ba848` handed on ("regenerating the feed and landing a door over the chosen branch").
Repaired in the same commit as this record.

---

## What was wrong

`3957ba848` replaced the count cull with the chooser and re-worded every sentence that called the
settled book uniform — **in the page's own JavaScript**. Two branches in
`site/capabilities/index.html`, both keyed to `d.settlement_selection`, both correct.

A third sentence says the same thing and is built **server side, in the feed**:
`generate_book_growth_data.build`'s `engine_bound_statement`. It was not keyed to anything. It
read, verbatim, from the feed generated at this HEAD:

> The company won 500 accounts and OUR settlement engine could settle 83 of them — **a uniform
> 18.3% sample**, 417 wins refused. **Every year is represented in proportion to what it won**, so
> the SHAPE of this curve is commercial; its HEIGHT is our machine. **Divide a booked count by
> 0.183** to read the supplier rather than the sample.

All three emphasised clauses are false of a chosen sample:

* **"uniform"** — the sample is chosen for difference over the demand axes, deliberately not uniform.
* **"in proportion to what it won"** — proportionality is now a *fitted* property (reconstructed to
  0.1%), not a construction. Chosen and proportional-by-count are opposed criteria; `3957ba848`'s
  own result document says so.
* **"Divide a booked count by 0.183"** — the damaging one. Per-account weights on this book span
  **0.057 to 14.774**, a 259.7× spread. There is no single number that undoes this sample, and this
  is an arithmetic a reader can actually carry out. It returns a wrong number **in silence**, with
  the rest of the page now saying the opposite.

`site/capabilities/index.html:299` renders it: `$("growth-headline").textContent =
d.engine_bound_statement`. It is the page's *headline*, above the two sentences that were fixed.

## Why it was LATENT and not BLOCKING

`site/data/book_growth.json` at HEAD predates the chooser and carries no `settlement_selection`, so
nothing chosen was on the page yet. The false sentence would have been published by the **next run
that regenerated the feed** — `background/process_run_complete` calls
`generate_book_growth_data.generate()` on every completed run. It was one daemon tick from live.

## Why no control caught it

**Both selections give a sample rate below one.** Every assertion in
`tests/tools/test_generate_book_growth_data.py` was keyed to the *rate* —
`"20.0% sample" in ...`, `"Divide a booked count by 0.200" in ...` — and the rate cannot
discriminate the two mechanisms. The controls were correct, stayed green, and were blind by
construction. This is the R15 shape where a control's key is one axis short of its subject.

It is also the ordinary consequence of a change landing in two layers: the JS branch was added and
the feed's own prose was not, and nothing relates the two because they are different files in
different languages saying one thing.

## The repair

`_engine_bound_statement(sample_rate, selection, funnel_wins, refused)` — hoisted out of the dict
literal it was a four-deep ternary inside, and keyed to **both** axes. `selection` defaults to
`"uniform_count"` when the record does not carry it, the same fail-closed direction the feed key
already took: every campaign record older than today describes a genuine uniform cull, and
defaulting the other way would relabel the whole history as chosen.

The chosen branch says what the cull branch cannot: the accounts were picked to differ, the sample
**cannot be undone with any single number**, and `settlement_weight` on each row is what reads
across to the supplier. Deleting the false clauses alone would have left the reader with no route
to the supplier at all, which is a different defect.

## The controls, and what they are keyed to

`test_the_headline_tells_the_two_SELECTIONS_apart_and_only_one_says_divide` asserts over **both
branches from one record**, not a leg per branch: a generator returning a single sentence for both
mechanisms — *exactly the defect that shipped* — fails on the first assertion. Keyed to the
property rather than today's wording: the cull branch must hand the reader one number to undo the
sample with, and the chosen branch must refuse to, because under per-account weights no such number
exists.

**Mutation-proven.** Replacing `if selection == "chosen_weighted":` with `if False:` reproduces the
shipped defect and the control fires, naming both sentences as identical. Restored, 27 pass.

`test_a_record_written_BEFORE_the_chooser_is_read_as_the_cull_and_not_as_chosen` holds the
fail-closed default down.

## What this does NOT claim

It does not claim the rest of the feed is clean. It claims one sentence was, and that the *class* —
a claim about the selection mechanism written somewhere other than the branch that was fixed — was
searched for by grepping `uniform` and `in proportion to what it won` across `tools/`, `site/` and
`simulation/`. **Reporting what that search returned rather than only the part that suits the
repair:** beyond this sentence it found no other *published* uniformity claim, and two pieces of
now-stale **comment** prose which are left alone deliberately —

* `tools/generate_book_growth_data.py:123` and `:368`, narrating what the 2026-08-29 ceiling did.
  Historical narrative about a dated change, still true of that date.
* `tools/couple_pb3_book_growth.py:281`, "Under the uniform sample the two differ in EVERY year and
  by a factor of five and a half", inside a docstring about `funnel_wins` vs `wins`. The *reasoning*
  it supports — a belief formed on the funnel must not be scored against booked wins — is untouched
  by which mechanism does the settling, and the sentence is an illustration of magnitude, not a
  claim the page makes. Worth a re-word when that file is next opened; not worth opening it for.

Neither reaches a reader. The distinction this finding turns on is exactly that one: the sentence
repaired here is rendered, and `site/capabilities/index.html:299` is the line that renders it.

**My own first draft of the replacement prose said "there is no single number to divide by" and my
own control refused it.** The control forbids the word on that branch rather than the instruction
shape; I changed the prose instead of narrowing the control, because a narrowing added to admit one
acceptable use is the asymmetric repair that only ever hides the next real one.
