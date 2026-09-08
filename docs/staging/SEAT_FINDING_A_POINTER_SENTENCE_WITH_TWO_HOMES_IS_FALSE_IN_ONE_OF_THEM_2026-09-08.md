**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — the sentence that sends a reader to the band table has two homes, and it pointed the wrong way in one

LATENT rather than higher: no published figure is wrong, and the branch that carried the false
sentence does not fire on the world `site/data/value_arms.json` currently publishes (the level leg
is sign-stable there, so the refusal is never composed). It is LATENT and not NONE because the
sentence was false *by construction* and not merely at risk of becoming so — the day a world
publishes a sign-straddling level leg, a reader of the page headline is sent the wrong way up the
page, and nothing in the tree would have gone red.

**Filed:** 2026-09-08, delivery seat (isolated worktree).
**Pre-registration:** `SEAT_PREREGISTRATION_THE_BAND_TABLE_POINTERS_CENSUS_2026-09-08.md`, written
before the census ran.

---

## The premise, re-measured at draw time

The drawn item cites `656a45f54` and `ea6101870`. `git merge-base --is-ancestor` says **both are
already ancestors of `origin/main`** — the item's own premise check said so too, and it holds.

**The premise is NOT spent.** Those two commits collapsed the re-draw family's *numbers* into one
home (`#arms-redraw`). The item asks about the *description* of that home, which still had two, in
two producers, untied to the DOM order they each assert. Checked directly before starting: nothing
in `tests/`, `site/` or `tools/` asserts the relative position of `#arms-redraw` against any other
anchor. The existing controls over both sentences ask only whether they say `"band table"`.

---

## What was asked, and what came back

**Q1 — how many literals in `tools/generate_value_arms_data.py` claim a direction to the band
table? Predicted three, no fourth producer. → CORRECT.** An AST census of string literals across
`tools/`, `site/`, `saas/`, `company/` and `background/` returns exactly three, all in the two named
producers: `_redraw_band_clause` (one) and `_the_level_legs_family` (both branches).
`background/band_null_sweep.py` also says "band table" and is a different subject — statistical
bands, not this page.

**Q2 — how many page regions does each sentence render into? Predicted one each. → WRONG, and that
is the finding.**

`_the_level_legs_family`'s sentence lands in `current_world.composition.why_not_readable`, which has
**two** homes:

| Home | Renders it | Position of `#arms-redraw` relative to it |
|---|---|---|
| `#arms-composition` (door line 452) | `$("arms-composition").innerHTML = ... prose(comp.why_not_readable)` | **above** — position 1 against 7 |
| `#arms-headline` (door line 402) | `_current_world_clause()` → `headline` → `$("arms-headline").innerHTML` | **below** — position 1 against 0 |

The sentence said *"the re-draw band table **higher up this section**"*. True from the composition
panel. **False from the headline**, where the table is the very next block down.

The producer's own docstring reasoned from the single home it knew about — *"`#arms-composition`
sits BELOW `#arms-redraw`"* — which is true, and is not the whole truth. That declaration was the
only thing in the tree with an opinion about where the sentence rendered, and it was checking
itself.

---

## Why nothing caught it

Three controls sit directly on this sentence
(`test_the_level_legs_family_is_POINTED_AT_by_the_share_refusal_and_never_recited_beside_it`,
`test_the_shares_refusal_reaches_the_headline_and_not_only_the_payload`, and the door's own band
rungs). Between them they assert: the numbers are *not* recited here, the pointer *is* present, the
numbers it points at are the ones the sign test ran over, and the refusal *reaches the headline*.

Every one of those is about the *content* of the pointer. **None is about where the thing it points
at actually is** — and one of them asserts, approvingly, the very second home that made the sentence
false. This is the R15 shape where a control is aimed at the concept word and blind to the concept:
"it says `band table`" was the whole test.

---

## What was done

1. **The wording is now a LANDMARK, not a direction.** `_the_level_legs_family` says *"the re-draw
   band table **under the headline figure**"* on both branches. A landmark names where the table
   *is*, so it is true from anywhere on the page and cannot rot into a lie by the sentence gaining a
   third home. `_redraw_band_clause` already pointed that way ("directly below this headline"), so
   the two producers now name **one landmark rather than two directions** — which is the same
   collapse `656a45f54` performed on the numbers, one layer along.

2. **Three rungs in `tests/tools/test_generate_value_arms_data.py`:**
   - `test_a_sentence_pointing_at_the_band_table_is_true_from_EVERY_region_it_renders_in` — reads
     the door's own reading order at run time, **derives** each sentence's homes by running the
     composers the door reads from (never a declared list), and judges a landmark claim once
     against its landmark and a `here`-relative claim once **per home**. Fails closed on a pointer
     worded past the registered vocabulary. Carries a witness leg requiring at least one pointer to
     reach two regions, or the "EVERY region" quantifier is never exercised.
   - `test_MUTATION_a_pointer_that_misdirects_is_CAUGHT_and_both_directions_are_reachable` — poisons
     the sentence against the real order and the order against the real sentences, and asserts the
     honest pair of each stays green so the judge cannot pass by refusing everything.
   - `test_every_band_table_pointer_in_the_producer_is_one_this_control_judges` — an AST census, so
     a fourth producer cannot arrive untied. This is the guard written *as* the census, which is how
     Q1 was answered.

**R15 — poisons run against the real tree and reverted:**

| Poison | Result |
|---|---|
| restore `"higher up this section"` to `_the_level_legs_family` | RED, naming `#arms-headline`, the direction claimed and the direction that holds |
| move the `#arms-redraw` div above `#arms-headline` in the door | RED on all three pointers |
| add an unregistered pointer literal to `_redraw_band_clause` | RED on the census, naming the line |

---

## The correction I owe the record

Leg B of the mutation rung was first written to poison the order by moving `#arms-redraw` **below**
`#arms-composition`, asserting the landmark pointer would red. It did not, and the assertion message
said the control was blind. **The control was right and the poison was wrong**: "under the headline
figure" is still true of a table at the foot of the section. The two kinds of claim fail on
*different* moves — a landmark breaks when the table crosses its landmark, a `here`-relative claim
breaks when the table crosses the reader — and the rung now poisons both and asserts each survives
the other's move. Kept here because it is the same class as the defect: a claim about direction is
only checkable against what it is a direction *from*.

---

## The judgement the item asked for

The item's honest alternative was *"not worth a control — a misdirected pointer costs a reader a
scroll, not a number."* **That reasoning was sound and its premise was false.** The cost was not a
scroll on a correct page; it was a sentence that was already wrong. The judgement is only available
after the census, and the census was cheaper than the argument about whether to run it — which is
this project's own rule about preferring measuring to arguing, arriving again by the same door.

## What is next

Nothing blocking. The generalisable half is on the map already as the VAT shape; the new part is
**a producer does not know how many homes its output has, so a sentence that says "here" is
unverifiable at the point it is written.** If another surface composes one payload string into two
regions, the same rung shape transfers: derive the homes by running the composers, judge the claim
in each. `_the_regions_a_sentence_reaches` is the piece to copy.
