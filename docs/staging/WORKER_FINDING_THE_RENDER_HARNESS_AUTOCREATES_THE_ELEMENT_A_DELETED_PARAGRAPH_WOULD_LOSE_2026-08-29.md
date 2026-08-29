**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `A46_book_depth_is_a_curriculum_question`

# The render harness auto-creates any element the page asks for, so every `_reaches_the_reader` control is blind to a deleted paragraph

**Found:** 2026-08-29, incidental to the Lane 0 delivery item
`the-settlement-ceilings-basis-stops-being-circular`, while mutation-proving a new door control.
It is not that item's subject and it weakens four existing controls, so it is filed rather than
folded in.

## The mechanism, in one line of the harness

```
site/_live_harness.mjs:104
  getElementById(id) { return (elements[id] ||= stub(id)); },
```

`||=` **creates the element when it is not there.** A page that has lost
`<p id="growth-basis">` therefore renders the sentence perfectly under the harness.

## Why that is a fail-open and not a convenience

In a real browser `document.getElementById` returns `null`, so
`$("growth-basis").textContent = ...` throws a `TypeError`. Every one of these doors does its
assignments inside a `.then()` with no `.catch` on that branch, so the rejection is **swallowed**:
no console error a reader would see, and — the part that matters — **every assignment after the
throw never runs.** On `site/capabilities/` the order is `growth-headline`, `growth-basis`,
`growth-winrate`, then the growth table itself, so losing one paragraph silently takes the curve
and the learned-rate caveat down with it.

So the harness reports GREEN on exactly the change that blanks the page.

## Measured, not reasoned

Driving the real door with the paragraph removed and the assignment kept:

```
META: {"requested": [...], "unresolved": [], "scriptError": null}
HAS growth-basis: True
growth-basis.textContent: "That limit is a COMPUTE budget, not a commercial one. ..."
growth innerHTML len: 8133
```

`scriptError: null`, the text present, the table rendered — with the element deleted from the
door's source. The mutation is invisible.

## Blast radius

Four controls drive this harness and all four share it:

* `site/test_growth_learned_rate_caveat_reaches_the_reader.py`
* `site/test_published_caveat_reaches_the_reader.py`
* `site/test_the_baseline_comparison_reaches_the_reader.py`
* `site/test_the_book_is_bounded_by_compute_reaches_the_reader.py` (new, 2026-08-29)

Each one's docstring claims a mutation of the form *"delete the paragraph → red"*. **That claim
is false for the element half in all four.** The assignment half is caught; the element half is
not. This is the R15 shape "a control whose scope is wider than its claim": the claim was written
from what the control was aimed at rather than from what it was measured to catch.

## What was done about it here, and what is left

**Done, and scoped to the new control only.** The new file asserts on the door's SOURCE as well
as its DOM — `test_the_paragraph_EXISTS_in_the_doors_own_source` — because the two subjects are
each blind to the other's failure: the source cannot tell you the sentence is right, and the DOM
cannot tell you the element is there. Both mutations are now proven red.

**Not done, deliberately.** The systemic repair is in the harness: make `getElementById` return
`null` for an id the DOM does not contain, which is what a browser does. That is one line and it
is not mine to land mid-turn — it will red any door that references an element the harness was
silently inventing for it, across lanes, and the point of the change is to find out which. It
wants its own commit with the whole door suite as the subject.

## WHAT THIS CREATES

1. **One line in `site/_live_harness.mjs`** — `getElementById` fails closed — plus whatever it
   reds. Run the full `site/test_*` selection against it before landing.
2. **Three docstring corrections** once it lands: the mutation lists in the three older controls
   claim a red they do not produce today.
3. **The generalisable half.** A test double that is more permissive than the thing it doubles
   turns every assertion downstream of it into a claim about the double. `||=` in a stub is the
   tell, and it reads as defensive coding right up until it is the control's only failure mode.
