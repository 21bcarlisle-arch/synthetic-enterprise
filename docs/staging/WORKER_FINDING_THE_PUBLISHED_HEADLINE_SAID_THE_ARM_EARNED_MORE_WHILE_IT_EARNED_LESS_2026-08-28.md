**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `SITE13_the_baseline_comparison_carries_its_bound`

**Discharged:** `tests/tools/test_generate_value_arms_data.py::test_the_headline_says_LESS_when_the_arm_earned_less` — in the commit that files this.

The false clause is gone from the generator and the direction is derived in three cases. The other
direction is driven by `test_the_headline_says_MORE_when_the_arm_earned_more` and the fail-open
killer by `test_an_unreported_advantage_is_its_own_sentence_and_never_the_winning_one`, both in the
same file. BLOCKING is kept as the severity because it describes what was PUBLISHED, not what is
outstanding — the record of a false claim should not be softened by the fact that it was repaired
within the hour.

# The published headline said the per-customer arm earned more than flat rules, on a run where it earned £4,724 less

Found while adding the coverage bound to the same sentence. This is not a mis-divided ratio or a
missing caveat — it is a **statement of fact that was false on the run it described**, on the
comparison the site leads with.

## What was published

`/capabilities/`, headline, generated 2026-08-28T12:42:36Z, verbatim:

> "**Running the same book through the per-customer decision engine earned more than flat rules**
> — but running it through ONE flat margin at the same price LEVEL earned £9,627 more still."

The run it describes:

| arm | net margin |
|---|---|
| flat rules (control) | £159,423.50 |
| per-customer (value arm) | **£154,699.49** |

**The per-customer arm earned £4,724.01 LESS than flat rules.** The page said it earned more.

## Why it happened, and why it is a half-finished repair rather than an oversight

`_selection_sentence` has two branches, one for each sign of `selection_gbp`. **Both open with the
same constant clause.** The direction of the *selection* claim is derived; the direction of the
*arm-vs-control* claim never was.

The function's own docstring already names this exact hazard, about the other half of itself:

> "THIS SENTENCE USED TO BE A CONSTANT (2026-08-28). It asserted that the level arm 'earned as much
> or more again' … and would have gone on being published word-for-word whatever the next run
> returned. **A conclusion that cannot change when its evidence changes is not a reading of the
> evidence**, and this is the one page on the site whose whole purpose is to be able to return an
> unflattering answer (R12)."

That repair was made, correctly, earlier the same day. It fixed one clause of a two-clause sentence
and left the other reading from a run that had already been superseded. **The class was named, the
instance beside it was missed** — which is the R10 shape in miniature: fixing the instance you are
looking at rather than the class you just described.

The figure was not even missing. `level_vs_selection.value_advantage_gbp` was in the artefact
throughout; the site generator's `split` block did not carry it, so the sentence had nothing to be
derived from and nobody noticed because the constant happened to be true when written.

## Why BLOCKING rather than LATENT

Every other defect logged today was a bound, a denominator or a caveat — figures that were correct
and framed wrongly. This one asserted the opposite of what the run measured, on the surface a
reader meets first, about the project's central claim. Nothing downstream could correct it: the
tables below the headline carried the right numbers, so a reader who read on would meet a
contradiction and a reader who did not would leave with the reverse of the result.

## The repair

`_arm_vs_control_clause(advantage)` — three cases, derived:

- **earned more** → "£X MORE than flat rules"
- **earned less** → "£X LESS than flat rules"
- **not reported** → "This run did not report what the per-customer decision engine earned against
  flat rules, so no claim is made about it." **Never the winning clause by default** — defaulting
  to "earned more" is the whole defect in miniature.

`realised.split` now carries `value_advantage_gbp` and `level_advantage_gbp`, so the sentence has
its evidence.

The headline now reads: *"Running the same book through the per-customer decision engine earned
**£4,724 LESS** than flat rules. Running it through ONE flat margin at the same price LEVEL earned
£9,627 more than the per-customer engine did…"*

## And the coverage bound, in the same sentence

Item 1 of `WORKER_FINDING_THE_METHOD_REACHES_TWO_PERCENT_OF_RENEWALS…` is done in the same change:
the headline now ends *"Read all of it against its size: the per-customer arm priced 25 of the
1,209 renewals the world offered, 2.07% of them, so every figure here is those decisions and what
they cascade into."* Derived from the funnel, and **silent when the funnel is absent** — an
invented coverage sentence would be worse than none, because it is the sentence a reader would
trust most.

## R15 — three mutations, each red

| mutation | control that fires |
|---|---|
| re-hardcode the opening clause to the winning one | `test_the_headline_says_LESS_when_the_arm_earned_less` (+2 others) |
| default an unknown advantage to the winning clause | `test_an_unreported_advantage_is_its_own_sentence_and_never_the_winning_one` |
| drop the coverage clause | `test_the_headline_carries_the_coverage_bound` |

And the control is not one-directional: `test_the_headline_says_MORE_when_the_arm_earned_more`
drives the winning case, so this is a check on the sentence's direction and not a machine for
printing bad news.

## WORK THIS CREATES

1. **Sweep the site generators for other constant clauses in derived sentences.** This one survived
   because a half-repair looks exactly like a whole one from the diff. The question to ask of every
   published sentence: *what run was this written against, and what would it say if that run's sign
   flipped?*
2. **The class deserves a control, not just three tests.** A sentence assembled from a constant
   prefix and a derived suffix is a shape, and it is greppable.

## The sweep item 1 asked for, and what it found

Swept every `tools/generate_*_data.py` for the shape — a directional or judgement word inside a
published string that is not built from the figure's own value. 36 candidates, almost all
docstrings. **One real second instance:**

`tools/generate_fidelity_data.py::_mae_reading_block` published

> "structural model beats best-of-naive-family in **only** {N}/{M} years"

with the count derived and **`only` constant**. True at the 4/10 it was written against, and it
would have published *"beats best-of-naive-family in only 9/10 years"* without anything failing —
the same defect pointed the other way, publishing a good result as a poor one.

Repaired the same way: `_beat_qualifier(beaten, total)` derives `"only "` below half, `"a clear "`
at 80% or above, and **the empty string in the middle band**, because a qualifier is a claim and
the honest thing at a near-tie is to make none. Nine tests, mutation-proven — restoring the
constant `only` reds three of them.

**`generate_fidelity_data.py` had no tests at all** before this. The new file covers the one
function this change touched and says so in its own docstring; the wider gap is recorded here
rather than left implied by an empty directory.

**Checked and cleared:** `generate_proof_data.py`'s "Timing beats messaging by enough to matter
commercially" is inside the `_not_proven()` list, explicitly labelled *"hypothesis — the
least-anchored, most likely wrong"*. A directional claim that declares itself unproven is the
opposite of this defect.

## Still live
