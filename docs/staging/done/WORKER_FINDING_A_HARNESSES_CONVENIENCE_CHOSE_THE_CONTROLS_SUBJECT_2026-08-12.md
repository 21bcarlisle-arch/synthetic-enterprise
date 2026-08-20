# WORKER FINDING — the harness picked the easy subject, and that became the control's blind spot

**Severity:** RECORDED · **Lane:** H_harness
<!-- Severity normalised 2026-08-12 by a worker tick, not by this document's author: it read
     `high`, which OPS9's parser cannot read, and carried no lane, so it was UNCLASSIFIED and
     reddened the staging-root control. BLOCKING by the ruling's own words -- a control in
     this area was untrustworthy: 24/24 green over a page breaking its own printed rule.
     Lane from SITE2_two_sided_wall_exhibit, the atom this Hour walked (map: H_harness). -->
**Class:** R15 — wrong subject (new variant: *the subject was chosen by the harness author's
convenience, and the docstring says so out loud*)
**Found:** 2026-08-12, HARDEN-stage Expert Hour (cold-eyes walk) on `SITE2_two_sided_wall_exhibit`
**Status:** instance fixed; the class is what this document is for

**RECORDED AND ACCEPTED, 2026-08-20 — THE SUBJECT THIS FINDING IS ABOUT NO LONGER EXISTS.**
Taken via clause 2's second route ("or until the limitation is explicitly recorded and
accepted"), NOT by repair, and deliberately not by building a control. Every reading below
is of the committed tree.

**Why the discharge went stale without anyone touching this document.** The three falsifier
nodes it named all lived in `site/customers/test_wall_exhibit.py`. `03dd8c49e` retired eleven
pages by deleting their directories, `site/customers/` among them, so the falsifiers ceased to
exist and this document reverted from RECORDED to BLOCKING on its own. Same mechanism, same
commit, as the sibling blocker in this class — a deletion that COMMITS, which is the case
`parse_discharge` names in its comment as the one its index-OR-HEAD union cannot absorb.

**Why nothing is rebuilt, and why that is the honest answer rather than the cheap one.** This
finding is about a leak check whose subject was narrower than its claim. Both the claim and
its subject are gone:
- The guarded mechanism is absent from the site — `setWallView`, `applyWallViewToOpState`,
  `WALL_VIOLATIONS` and `data-wall-governed` appear in no page, only as a residual string in
  a `site/data/simplified.json` record.
- The printed sentence the defect contradicted ("No company estimate and no simulation ground
  truth is in this view; if one appears, the page is broken") is on **no** current page. A
  sweep of all 14 built pages for that claim and its variants returns nothing.
- `/explore/` supersedes `/customers/` and is not a successor subject: it shows both sides
  **deliberately and simultaneously** ("What the world knew" / "What the supplier believed")
  and carries no view selector at all. There is no side-filtering claim left to violate.

**The control this disposition refuses to build.** The tempting close is a guard asserting no
page reintroduces a side-filtered view without a whole-document subject. That control would
have zero subjects on today's site and would pass unconditionally — a vacuous control, which
is the exact defect `CLASS_CONTROLS_THAT_CANNOT_FAIL` catalogues and this document is filed
under. Closing a controls-that-cannot-fail finding by adding a control that cannot fail would
be self-refuting, so the limitation is recorded instead. If a side-filtered view is ever built
again, the reasoning in "What to do about it" below applies to it from the start, and the guard
becomes buildable because it would finally have a subject.

**What is NOT accepted away:** the class lesson stands and stays live in
`docs/staging/CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md`. What is accepted is only that
this INSTANCE has no live subject and so owes no repair — RECORDED, "known limitation,
accepted, no work owed", not a claim the class is closed.

**Discharged:** `site/customers/test_wall_exhibit.py::test_the_customer_view_of_the_whole_page_contains_no_company_or_sim_panel`, `site/customers/test_wall_exhibit.py::test_mutation_a_view_switch_that_skips_the_op_state_region_kills_a_named_test`, `site/customers/test_wall_exhibit.py::test_the_named_figures_are_visible_to_the_checker_in_the_op_state_exhibit` — the union of op-state and tabs is now the leak checks' subject, the view switch is mutation-proven over the region the old fixtures fell between, and the checker's own sight is pinned. 5 green, 2026-08-12.

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
