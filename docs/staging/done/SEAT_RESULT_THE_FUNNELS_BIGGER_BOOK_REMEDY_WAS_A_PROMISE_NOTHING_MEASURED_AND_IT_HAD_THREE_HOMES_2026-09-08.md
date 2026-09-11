**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — no attainable book can read the effect the skill instrument measured) · **Class:** controls_that_cannot_fail

# RESULT — the funnel's "bigger book" remedy was a promise nothing measured, and it had three homes

`SEAT_RESULT_THE_UNSCORED_DECISIONS_ARE_EXACTLY_THE_DEPARTURES...` (2026-09-08, at HEAD in
`2cfc4ec5f`) closed with four things owed. Its fourth was left deliberately undone:

> *"`drop_out`'s reading needs correcting where it is generated, not only qualified here. Left
> deliberately: changing the sentence and adding the block that refutes it in one commit would
> leave nothing able to show the two disagreed. The disagreement is the evidence."*

The disagreement is now evidence — recorded in that document, in its successor, and in a comment
in the assembly itself. So the correction is made here, and it turned out to be **three
corrections, not one**.

## The defect

One claim — *a larger settled book adds to this sample* — was published in three places, none of
which had measured it:

| # | home | what it said | who meets it |
|---|---|---|---|
| 1 | `run_value_cycle_ab._skill_drop_out_reading` | "THE SAMPLE CANNOT BE WIDENED FROM THIS BOOK: {n} is what the method has earned, and **only a larger settled book adds to it**." | anyone reading the artefact |
| 2 | `run_value_cycle_ab.SKILL_DROP_CLASSES[ELIGIBILITY]` | "Widening this is not available at any book size; **only a LARGER settled book adds decisions here**." | rendered beside the counts, met independently |
| 3 | `generate_value_arms_data._widening_consequence` | "The interval above is what this book can earn, and **only a larger settled book moves it**." | **in amber, on the page, directly above the concordance interval** |

Home 3 is the one that reaches a reader. All three are the VAT shape this project's own
instructions name: one requirement, several implementations, and a fix applied to one of them.
Correcting only the reading — which is literally what the parked item asked for — would have left
the sentence a reader actually meets untouched.

**Why it is wrong, and it is not a wording problem.** The class counts genuinely establish that
the sample cannot be widened by fixing our own code: `join` is 0 and `coverage` is 0, and those
are ours. They establish *nothing whatever* about what a bigger book would do. That is a claim
about a counterfactual, and `_survivorship` has since measured it: the eligibility class **is**
the churn class, so a larger book adds decisions and drops the same share of them. The published
remedy pointed at the one action that cannot work.

**A remedy is a different kind of claim from a count**, and this is the general form worth
keeping. Every number in that funnel was measured. The sentence composed from them was not, and
it sat in the same paragraph wearing the same authority.

## What changed

The remedy clause is now composed from the split, in both producers, with the composition in one
place per side (`_widening_remedy` in the runner, `_bigger_book_clause` in the generator):

- **Split measured, drops are departures** → "A LARGER SETTLED BOOK DOES NOT ADD TO IT: all N of
  these are renewals the world recorded as DEPARTURES... a selection in the estimand, not a
  sample-size bound."
- **Split measured, residue not attributable to a departure** → "ADDS AT MOST PART OF IT: N of
  these are NOT attributable to a departure" — the Lane 0 item's own recoverable hypothesis, which
  the code can now state the day a run carries it.
- **No split** → "**NOT ESTABLISHED BY THIS RUN**." Neither answer inherited.

**The third state is the point.** The two absences are not one absence: a run that measured the
split and found a residue knows something a run with no event log does not, and the old sentence
answered confidently in both. The live feed is in the no-split state today, so what the page will
say when this lands is that it cannot tell — which is correct, and is the first time it has been.

Order became load-bearing in `method_skill`: the split is computed *before* the funnel, because
the funnel reads it. Passing `None` is what makes the funnel withhold, and that is the default —
a caller with nothing to give withholds rather than asserts.

## The battery — 6 mutations, 6 killed

Run in a clean `git archive HEAD` extract with only the five changed files copied in, **not** in
the shared working tree: an A/B run was in flight against this same module, and a mutation live
for thirty seconds could have been picked up by a forkserver re-import.

| # | mutation | outcome |
|---|---|---|
| 1 | runner: remedy always gives the conditioned answer | killed (2 controls) |
| 2 | runner: funnel never receives the split (`None`) | killed |
| 3 | runner: eligibility class prose reverts to the promise | killed |
| 4 | generator: clause always says "not established" | killed (5 controls) |
| 5 | generator: consequence ignores the split it was handed | killed |
| 6 | generator: the old promise comes back verbatim | killed (7 controls) |

M2 and M5 are the ones worth having: they are the **wiring**, and a composer that is right while
nothing hands it the split is exactly how the funnel and the survivorship block came to disagree
on one page in the first place. Both door controls drive the real producer rather than typing a
sentence into a fixture, and both states are driven — whichever the published feed is in, the
other is locally unreachable.

## What is NOT claimed

**The rendered value has not moved yet.** `site/data/value_arms.json` still carries the old
`consequence` string; regenerating it was not done here because another lane holds
`site/capabilities/index.html` dirty and has `site/data/*.json` staged, and landing into a file
another lane holds dirty wedges the shared tree. The page will carry the corrected sentence on the
next ordinary publish cycle, which runs this generator. Until then the correction is real in the
producer and not yet in front of a reader, and this document does not claim otherwise.

**Two site-lane controls are red in the shared working tree**
(`test_the_composition_the_page_states_is_the_one_the_feed_established`,
`test_the_figure_from_the_world_that_is_live_reaches_the_reader_and_never_as_resolved`). Both PASS
in a clean HEAD extract, and both still pass in that extract with only my two changed tool modules
copied in — so they are the other lane's uncommitted `index.html`, not this change. Recorded
because the sign-flip direction is the unusual one: green at HEAD, red in the tree.

## What is next

1. **A run is in flight** (`docs/observability/value_cycle_ab_survivorship_2026-09-08.json`,
   `--level-arm`, launched detached at 06:0x). It is the first run whose artefact will carry
   `method_skill.survivorship` — every artefact on disk predates the split, which is why the page
   correctly renders the absence today. When it lands, the funnel's remedy clause and the amber
   line both become the measured sentence, in one regeneration, with no edit.
2. **Then regenerate the feed** — and only then does the reader-facing half of the parent finding
   close. Not before: a claim about a run that run never made is what this page exists to refuse.
3. **Pre-register the replacement estimand** before building it — fixed horizon from term start,
   counting a departure as the small-or-zero value it produced. Unchanged and still owed; the
   parent finding's prediction stands.
