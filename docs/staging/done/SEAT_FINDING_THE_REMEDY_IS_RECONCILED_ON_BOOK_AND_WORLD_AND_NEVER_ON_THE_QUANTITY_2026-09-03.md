**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The remedy's evidence is reconciled on the book and on the world, and never on the quantity it decomposes

**Class:** `controls_that_cannot_fail` (primary), `figures_on_a_superseded_clock` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0, claim
`the-baseline-was-beaten-in-a-world-that-no-longer-exists`
**Subject:** `tools/generate_value_arms_data.py::_decomposition_is_the_same_book` and the
`floor_decomposition=` block in `build()`.

## What

`site/data/value_arms.json::floor_decomposition` publishes a variance split and a remedy:

```
priced_share_of_variance   0.99999999
irreducible_sd_gbp         0.21
larger_settled_book_would_resolve_it   true
share_is_decisive          true   (bar 0.15, margin 0.753)
```

Every one of those numbers is a decomposition of **`selection_gbp`**. The figure this page
publishes as the company's beat, and the figure `_current_world_contrast` bounds since `a70cc11e1`,
is **`value_advantage_gbp`**. They are different quantities, and the split does not transfer.

**Measured, on one seed family, both contrasts, from the three legs already committed**
(`value_cycle_ab_s1_noise_floor{,_only,_except}_20260829.json` — the only family where all three
legs exist):

| leg | `selection_gbp` sd | `value_advantage_gbp` sd |
|---|---|---|
| `all` (undecomposed) | 2,577.80 | 990.45 |
| `only` (priced roster) | 2,092.29 | 414.85 |
| `except` (rest of book) | **0.21** | **554.21** |

| contrast | `priced_share_of_variance` | `irreducible_sd_gbp` |
|---|---|---|
| `selection_gbp` — **what is published** | 1.000000 | **0.21** |
| `value_advantage_gbp` — **what the page's figure is** | 0.359106 | **554.21** |

The irreducible floor a reader is shown is wrong by a factor of **2,623** for the figure they are
shown it beside. The priced share falls from 1.000000 to 0.359106, and its margin over the
decisive bar from 0.753 to 0.209.

## Why the existing guards do not catch it

Two reconciliations already run against this artefact and both pass a cross-contrast read straight
through:

- `_decomposition_is_the_same_book` asks whether the split was measured on the same **book**
  (`priced_decisions`, `renewals_offered`).
- `_world_provenance` asks whether it was measured in the same **world** (the anchor digest).

Book ✓, world ✓, quantity ✗. Nothing anywhere asks what the split decomposes. The artefact itself
names its contrast in exactly one place — the prose of `what_this_is` ("The selection-figure noise
floor …") — and carries no machine-readable declaration: `value_advantage`, `selection_gbp` and
`level_advantage` each occur **zero** times as data in it.

This is the same mispairing `a70cc11e1` repaired one field along. That commit found the bound being
taken from the floor's published `selection_gbp_spread` when the figure was `value_advantage_gbp`,
and fixed the **bound**. The **decomposition** beside it was left on the old quantity, so the page
now states its bound in one currency and its remedy in another.

## Why it is LATENT today and what arms it

`measured_on_this_page_s_book` is `false` right now, so the book guard is already withholding the
remedy sentence. Nothing a reader sees today is wrong *because of this defect* — the numbers are on
the page as evidence, under a caveat earned for a different reason.

**The book guard is what masks it, and this lane owes the work that clears the book guard.** The
decomposition is due to be re-run on the current book and in the live world — that is the
outstanding half of `c30b98048`. The moment it is, `measured_on_this_page_s_book` becomes `true`,
the different-book caveat lifts, and the remedy publishes — still decomposing `selection_gbp`,
still beside a `value_advantage_gbp` headline, and now with nothing withholding it. A guard whose
clearing arms a second defect is not coverage of that defect.

That is the R15 shape *"a control over a mixed subject reports the OR"*: two reconciliations pass,
their conjunction reads as "this evidence describes this figure", and the third question was never
asked.

## The fix

Landed in the same commit as this finding.

- `_decomposition_contrast()` reads a machine-readable `contrast` declaration off the artefact and
  **fails closed** when there is none — an artefact that cannot say which quantity it decomposes
  cannot be shown to describe the figure published above it. Prose is not parsed: a declaration
  inferred from a sentence is not a declaration, and the producer-side stamp is owed exactly as the
  book-side one is (`_decomposition_is_the_same_book`'s own docstring records the same debt).
- `_decomposition_is_the_same_contrast()` refuses when the declared contrast is not the contrast the
  page states its figure and its bound in, naming both quantities and the measured 2,623× gap.
- The refusal joins the different-book caveat as an independent reason rather than replacing it, so
  clearing the book reconciliation does not clear this one.

**Each guard has a sole witness so neither is an equivalence the other covers** (the fixture whose
subject satisfies two alternations makes each one an equivalence):

- *contrast-missing* — a decomposition on this page's book, in this world, with no `contrast` key.
  Book guard passes; only the declaration guard reds.
- *contrast-mismatched* — the same, declaring `selection_gbp` against a `value_advantage_gbp`
  headline. Book guard passes, declaration exists; only the mismatch guard reds.

## What this does not fix

It does not re-run the decomposition on `value_advantage_gbp`, and it publishes no
`value_advantage_gbp` split. The three-leg family that would supply one is the 08-29 family — a
different book and an unstamped world — and quoting it here would be the identical error this
finding is about, one contrast over. The 2,623× figure above is stated as **evidence that the
transfer is unsafe**, not as the page's new irreducible floor.

The owed work is a decomposition re-run that declares its contrast, on this book, in the live world.
This commit makes the surface refuse to imply it already has one.
