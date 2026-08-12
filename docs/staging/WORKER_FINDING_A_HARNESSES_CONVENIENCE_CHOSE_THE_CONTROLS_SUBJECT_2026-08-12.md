# WORKER FINDING — the harness picked the easy subject, and that became the control's blind spot

**Severity:** high
**Class:** R15 — wrong subject (new variant: *the subject was chosen by the harness author's
convenience, and the docstring says so out loud*)
**Found:** 2026-08-12, HARDEN-stage Expert Hour (cold-eyes walk) on `SITE2_two_sided_wall_exhibit`
**Status:** instance fixed; the class is what this document is for

## What happened

`site/customers/index.html` renders a three-way wall-view selector. `site/customers/test_wall_exhibit.py`
was **24/24 green**. The live page, with "The customer's side" selected, rendered
`Lifetime net £492.96`, `Cost to serve £329.93`, `Churn risk 23%` and `Satisfaction 65%` on screen —
directly above its own printed sentence *"No company estimate and no simulation ground truth is in
this view; if one appears, the page is broken."*

Three independent cold-eyes personas each led with it. The suite could not see it.

## Why the suite could not see it

The page has two regions: a static `#op-state` exhibit and a scripted drill-down. The view filter
lived only inside `layoutPanels()`, which the drill-down uses and the exhibit does not.

The control had **two disjoint fixtures, and neither one was the page**:

- `rendered` drove `layoutPanels()` directly, so every view-filtering assertion could only ever see
  drill-down panels;
- `op_state_html` was a static slice that asserted side **declaration** and never side **filtering**.

All three mutation tests mutated inside those two subjects, so R15 was satisfied *in form*.

## The sharp part

The harness's own docstring states the choice, as a virtue:

> It **deliberately** calls `layoutPanels(tabPanels())` rather than `renderHousehold()`: the
> structural guard's subject is the panel markup a tab actually produces, and driving the sole
> panel writer directly keeps the harness out of the login/nav chrome.

That is a real engineering reason — driving the whole page needs a DOM, and driving one function
does not. But the region the harness skipped **to stay simple** is exactly the region the defect
lived in. The subject was not reasoned from *"where can this fail?"*; it was reasoned from
*"what is cheap to drive?"*, and then written down as intent.

This is the tell to look for. **A docstring explaining why a control's subject is narrower than its
claim is not a design note — it is the defect, pre-confessed.** The existing catalogued class
("a new layer above a control must inherit its subject") describes a subject that drifts as layers
are added. This variant is worse: the subject was born narrow, on purpose, for good local reasons.

## What to do about it

1. **State the claim, then derive the subject from it.** The claim here was "the customer view
   contains no company or SIM figure". The subject that claim demands is *the document*. If driving
   the document is expensive, that cost is the price of the control — not a reason to shrink the
   claim silently.
2. **When a control has more than one fixture, ask what falls between them.** Two fixtures that
   each cover a region are not a partition unless something asserts the union. Here the union was
   never anyone's subject.
3. **Make the union subject explicit and named.** The fix adds `whole_document(view)`; its docstring
   now records what was missing and why, so the next reader inherits the reasoning rather than the
   convenience.
4. **Check the checker can still see.** In the same tick, fixing a caption renamed a tile to
   `Lifetime net (commodity)` and a `<`-anchored regex went silently blind to it — the
   narrowed-parser class, self-inflicted, minutes after fixing a wrong-subject bug.
   `test_the_named_figures_are_visible_to_the_checker_in_the_op_state_exhibit` now fails if any
   named figure stops matching. A leak checker that can no longer see the figure it hunts reports
   "clean" forever.

## Instance evidence

- Mechanism: `setWallView()` → `applyWallViewToOpState()`, filtering by the same attribute and
  predicate as the drill-down, removing from the DOM rather than hiding, failing closed on an
  unknown side; `window.opStateFind()` keeps detached panels fillable when their async data lands.
- Subject: `_wall_harness.mjs` now drives the page's own `setWallView()` over `#op-state` as real
  DOM children; `whole_document(view)` = op-state + every tab; section (9) of
  `test_wall_exhibit.py` runs the leak checks over that union.
- R15 both ways: reverting `setWallView` to its pre-fix shape **on the file** makes the union guard
  report the leak; an unknown-side block is refused; anti-vacuity in both directions (a filtered
  view that is empty, or identical to `both`, fails).
- `site/customers/` 45 passed; coupled set 106 passed; D36's render path intact (20 passed,
  `verify_printed_bill_render.mjs` PASS, 1557/1557 lines, 0 arithmetic failures).

## Related

- `docs/observability/sanity_adjudication_ledger.json`, 13 keys under `coldwalk:site2_` — 3 fixed,
  10 open, 2 adjudicated REFUTED.
- The 10 open findings are mostly SIM/COMPANY **fidelity** gaps the exhibit surfaced (a churned
  account shown in the present tense; electricity-only money labelled as the household's; a bill
  series with no winter; arrears notices filed as SIM-only). R12 applies: diagnose the mechanism,
  never tune the output. Each needs its own atom.
