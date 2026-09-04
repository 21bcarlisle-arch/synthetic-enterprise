**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: whether the remedy clause can price a leg the sentence beside it did not withhold

**Filed:** 2026-09-04, delivery seat, Lane 0, claim
`selection-leg-carries-its-live-world-floor`, BEFORE the measurement below was run.
**Subject:** `tools/generate_value_arms_data.py::_selection_sentence`'s `withheld` flag and
`_decomposition_is_the_same_contrast`.

## The question

`_selection_sentence` appends the remedy clause when `withheld` is true, and `withheld` is an
`any(...)` over TWO contrasts — `value_advantage_gbp` and `selection_gbp`. The remedy's own
quantity guard, `_decomposition_is_the_same_contrast`, compares the decomposition's declared
contrast against ONE — the module constant `PAGE_FIGURE_CONTRAST = "value_advantage_gbp"`.

So the question is whether a run in which the ADVANTAGE clears its floor and the SELECTION leg
does not produces a page that states a remedy priced on `value_advantage_gbp` under a sentence
whose only withheld quantity was `selection_gbp`.

## What I predict, before running it

1. The headline WILL contain "larger SETTLED BOOK" — the remedy is stated.
2. It will contain NEITHER "DIFFERENT QUANTITY" nor "WHICH QUANTITY" — the quantity guard passes,
   because the declared contrast equals `PAGE_FIGURE_CONTRAST` and nothing asks whether that is
   the contrast that was actually withheld.
3. The sentence it is appended to will have withheld `selection_gbp` only.
4. The remedy will name no leg at all — its five branches contain no contrast name on the
   admitting path, so a reader cannot tell which of the page's three published legs it prices.

If (1) and (2) hold together with (3), the guard is a control over a mixed subject reporting the
OR, and the price a reader is handed is for a leg that earned its direction.

## What would refute it

Any of: the remedy absent; the quantity guard firing; the remedy naming the withheld leg. Any one
of those means the composition already asks the third question and there is nothing to repair.

## What must NOT happen

No edit to `tools/generate_value_arms_data.py` before this file is written. Verified by
`git status --porcelain` at the instant of writing, pasted into the finding that follows.

## Why this is asked now and not before

It was not a defect when it was written. `_decomposition_is_the_same_contrast` landed on
2026-09-03 against a page that stated ONE bounded figure. `5ce6b0f9b` and `074a2c2db` gave the
selection and level legs bounds of their own, so the page now states three, and a guard that asks
"is this the page's figure?" answers for a third of the page. This is the interconnection
question, not new work: what landed since the last orientation, and does what assumes it still
hold.
