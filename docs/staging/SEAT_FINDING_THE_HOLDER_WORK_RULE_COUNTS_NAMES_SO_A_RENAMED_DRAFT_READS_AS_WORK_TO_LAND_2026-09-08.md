**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The Kind-A/Kind-B discriminator counts NAMES, so a renamed draft of a control HEAD already carries reads as holder work to land — and three of the five drawn copies are that

**Filed 2026-09-08 by the delivery seat (lane 0), working the drawn item "five rival working copies
remain on the shared tree, all Kind-B holder work". They are not all holder work. One is.**

## What landed this turn, first, so this is not read as a stall

`tests/tools/test_dd_opening_arms.py` — hunk 3 only, the holder's two substrate controls appended
over HEAD's full symbol set. Verified a strict superset by AST rather than by reading the diff, and
13 tests pass at the real repo depth. That is the one of the five the drawn remedy fits.

## The finding

`tools/stale_copy_refusal.py` grades a rival copy **HOLDER WORK** — and routes it to
`isolate_hunks --keep` + `surgical_land --content` — when it supplies at least one name
`git show HEAD:<path>` does not have. The complement, supplying *no* new name, is graded Kind-A and
routed to `refresh_to_head`.

**That rule counts names. A lane that drafted a control, and then landed a stronger version of the
same control under a different name, leaves a working copy that supplies a name and no work.** The
rule cannot tell it from a genuine addition, because at the level of a symbol set the two are
identical.

Measured on the three:

| copy | name it "supplies" | what HEAD carries for the same property | cost of landing the hunk |
|---|---|---|---|
| `site/test_harness_delivery_record.py` | `test_the_MAGNITUDE_reaches_the_reader_as_a_number_or_as_a_refusal` | `test_the_generator_LIFTS_the_only_rung_that_can_carry_a_magnitude` | **−18 HEAD symbols, +1 weaker** |
| `background/self_clearing_alarm_census.py` | `rows_graded_by_resemblance` (+2 helpers) | `shared_loader_answers`, `_claim_sentences` | **−2 HEAD functions, inseparably** |
| `tests/tools/test_r1_inference_ceiling.py` | 11 names | 20 HEAD names it drops | **references a module that does not exist** |

The first is the clearest, and HEAD's own docstring is the evidence. The working copy's magnitude
control is fixture-fed. HEAD's replacement says, in its own words, why that cannot work:

> *"A fixture-fed render test cannot see that at all: it would supply the field the generator never
> produced and pass on both legs."*

So the copy's one "new" name is precisely the draft whose blindness HEAD's landing exists to fix.
Landing it deletes the fix and re-adds the blind version, and every gate downstream goes green,
because a 70-line file that passes is indistinguishable from a 718-line file that passes.

The second is the same shape with a smaller blast radius: `rows_graded_by_resemblance` and HEAD's
`shared_loader_answers` are two implementations of *"is this row's answer its own, or borrowed from
a sibling"*. HEAD's is the one that landed carrying the fail-open repair, and its docstring already
discusses the resemblance rung the working copy re-implements. The holder's hunks cannot be split
from the hunk that deletes HEAD's two functions — hunks 5, 6 and 7 call `rows_graded_by_resemblance`,
which is defined only in hunk 4, and hunk 4 is the replacement.

## Why `isolate_hunks` cannot catch this and is not at fault

`isolate_hunks` operates on hunks, and a **replacement is one hunk**. `site/test_harness_delivery_record.py`'s
is `@@ -441,728 +440,81 @@` — 718 lines out, 70 in, indivisible. There is no `--keep` selection that
takes the addition without the deletion, because at the diff level they are the same edit.

The tool is right; the *grading* that sent a seat to the tool is what is wrong. And the grading is
wrong in the direction that costs most: it says **land this**, of a copy whose landing is a revert.

## The discriminator that would work, and it is not a bigger census

Not "does this copy supply a name HEAD lacks" but **"does this copy supply a name HEAD lacks, whose
hunk does not also delete a name HEAD has"**. One clause, computable from the same two symbol sets
plus the hunk map that `isolate_hunks` already builds:

    holder work  <=>  exists a hunk H such that  symbols_added(H) - HEAD_symbols  is non-empty
                      AND  symbols_deleted(H) & HEAD_symbols  is empty

Under that rule the five grade one HOLDER WORK and three REPLACEMENT — a third state neither
`refresh_to_head` nor `--content` currently has a door for, and naming it is the point. The
`--content` door lands a revert; the `refresh_to_head` door refuses, because the copy does supply
names. **A REPLACEMENT copy needs a human judgement about which of two implementations of one
property survives, and that judgement is exactly what neither door is allowed to make.**

I am not building that rule this turn. It changes the verdict a wall-adjacent guard prints, the
existing rule is *conservative in the safe direction for the Kind-A leg*, and three of the five are
now decided in writing here — so the next seat starts from the answer rather than from the grading.

## The decision on `tests/tools/test_r1_inference_ceiling.py`, which the drawn item asked for

**It is dead work and no lane can land it.** It calls `tools.r1_inference_ceiling._scores_on_folds`
and `honest_point_estimate`. Grepped across the whole tree, tracked and untracked, committed and
working: the only occurrences of either name anywhere are inside this test file. There is no pair
half to find, because the module half was never written — the tests were authored against a module
that was planned and not built.

So: it has no `--content` route (its hunks reference nothing), and no `refresh_to_head` route (it
supplies 11 names). **The decision is that it is a REPLACEMENT copy whose holder work is
unfinishable, and the bytes should be preserved and the copy refreshed** — which needs the
`refresh_to_head` refusal relaxed to accept a copy whose new names provably do not resolve. That is
one clause, it is the same clause as above, and it is the work this finding creates.

Until then the copy sits on the shared tree as a silent revert of `d7b2a35d4` for anyone who names
it in a pathspec, and that is the live hazard, unchanged by this finding.

## Correction to the drawn item, recorded beside it rather than fixed silently

The item says *"Each is correctly routed by the refusal to `isolate_hunks --survey` then
`surgical_land --content`."* Measured, that is true of one of the five. For three it routes to a
landing that deletes work HEAD carries. I acted on the item's wording for the first part of this
turn and built the isolated content for `background/self_clearing_alarm_census.py` before checking
the symbol set of the *result* — which is what caught it. **Checking the isolated output's symbol
set against HEAD, rather than the copy's, is the cheap step that turns this class up**, and it is
one AST parse.
