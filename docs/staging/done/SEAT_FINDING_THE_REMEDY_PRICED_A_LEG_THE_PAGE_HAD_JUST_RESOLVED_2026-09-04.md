**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The remedy priced a leg the page had just given a direction to, and the fixture that proved it was the defect

**Class:** `controls_that_cannot_fail` (primary), `figures_on_a_superseded_clock` (secondary)
**Filed:** 2026-09-04, delivery seat, Lane 0, claim
`selection-leg-carries-its-live-world-floor`
**Subject:** `tools/generate_value_arms_data.py::_selection_sentence`'s `withheld` flag and
`_what_would_resolve_it`'s quantity guards.
**Pre-registered:** `SEAT_PREREGISTRATION_WHETHER_THE_REMEDY_PRICES_A_LEG_THE_SENTENCE_DID_NOT_WITHHOLD_2026-09-04.md`,
written before the measurement. All four predictions in it held. The tree state at the instant of
writing, pasted as that document's own constraint required:

```
 M docs/observability/.human_last_input
 M docs/observability/.seat_heartbeat.json
 M docs/staging/WORKER_FINDING_REPEATING_ALARM_SEAT_CONTINUITY_2026-08-26.md
?? .se_worktree_owner
?? docs/staging/SEAT_PREREGISTRATION_WHETHER_THE_REMEDY_PRICES_A_LEG_THE_SENTENCE_DID_NOT_WITHHOLD_2026-09-04.md
```

No edit to `tools/generate_value_arms_data.py` preceded the prediction.

## What

`_selection_sentence` appends the book-size remedy when `withheld` is true. That flag was an
`any(...)` over TWO contrasts — `value_advantage_gbp` and `selection_gbp`. The remedy's own
quantity guard, `_decomposition_is_the_same_contrast`, compares the split's declared contrast
against ONE: the module constant `PAGE_FIGURE_CONTRAST`. Nothing compared the two, so the leg the
price is *for* and the leg the page *withheld* did not have to be the same leg.

Measured, on the canonical run, with the decomposition declaring `value_advantage_gbp` and
measured on this page's own book:

| | figure | its own floor | direction earned? |
|---|---|---|---|
| `value_advantage_gbp` | £12,071 | ±£2,578 | **yes — it clears** |
| `selection_gbp` | £1,816 | ±£2,578 | no — withheld |

The page then printed: *"it takes about 54 priced renewals against this book's 120 to bring the bar
under the gap."* The price is derived from a `value_advantage_gbp` split. The only thing withheld
was `selection_gbp`. "The gap" is left for the reader to bind, and the reader has just been told
one figure has no direction — so it binds to the leg the price is not for.

**The scale of the mis-transfer is already measured, in the sibling finding of 2026-09-03**: on the
one seed family where all three floor legs exist, `irreducible_sd_gbp` is 0.21 on `selection_gbp`
and 554.21 on `value_advantage_gbp` — a factor of 2,623. A price quoted across the two legs is not
approximately right.

## Why the existing guards do not catch it

Three reconciliations run against this artefact and all three pass a cross-leg read straight
through:

- `_decomposition_is_the_same_book` — same **book**? ✓
- `_world_provenance` — same **world**? ✓
- `_decomposition_is_the_same_contrast` — the **page's figure**? ✓ (it declares
  `value_advantage_gbp`, which is exactly `PAGE_FIGURE_CONTRAST`)

Book ✓, world ✓, page-figure ✓ — and the leg that was actually withheld was never asked about.
That is the R15 shape *"a control over a mixed subject reports the OR"*: `withheld` ORs two legs
and the guard verifies one.

**It was not a defect when it was written, and that is the whole shape.**
`_decomposition_is_the_same_contrast` landed 2026-09-03 against a page that bounded exactly one
figure, where *"is this the page's figure?"* and *"is this the withheld figure?"* were the same
question and asking either answered both. `5ce6b0f9b` and `074a2c2db` gave the selection and level
legs bounds of their own. The page now states three, each able to be withheld alone. The subject
widened; the control did not move; the conjunction that used to be sound became an OR. Nothing in a
bounded tick can see that — it is only visible from the interconnection question, which is why it
is filed from the seat and not from a lane.

## What made it invisible: the shared fixture WAS the defect

`tests/tools/test_generate_value_arms_data.py::_withheld_headline` — the helper behind **seven**
remedy controls — set `selection_gbp` to £1,816 and left the advantage at the canonical £12,071,
which clears the same floor. So every one of those seven controls asserted its property on a page
in exactly the defective state, and the price each of them checked was for the leg the page had
just resolved. A shared fixture that embeds the defect makes every control keyed to it green for
the wrong reason.

That is why fixing this reddened seven tests at once and why the repair is in the fixture rather
than at the seven call sites.

## The fix

Landed in the same commit as this finding.

- `_selection_sentence` builds the **tuple of legs it withheld** instead of an `any(...)` boolean,
  and passes it down. The flag was destroying the only information the guard below needs.
- `_decomposition_prices_a_withheld_leg()` refuses when the declared contrast is not among the
  legs the sentence withheld, naming both sides. **ANDed with the page-figure guard, never merged**
  — they clear on different work, and merging would let either clear both.
- `_which_leg_this_remedy_prices()` names the leg the price is for, and names the withheld legs it
  does **not** price, in every admitting branch. Silent when there is only one leg to name.
- `_withheld_headline` now puts both legs inside the floor, so the leg the split prices is a leg
  the page withheld.

**Mutation-proved, each run and reverted under `python3 -B`:**

| mutation | result |
|---|---|
| `_decomposition_prices_a_withheld_leg` returns `None` unconditionally (the defect as it shipped) | control reds |
| caller passes `(PAGE_FIGURE_CONTRAST,)` instead of the legs it withheld — the parameter accepted and ignored | control reds |
| drop `_which_leg_this_remedy_prices` from the admitting branches | control reds |

The null rung is `both`, which must KEEP the remedy: a control that only ever demands the remedy be
absent is satisfied by deleting the remedy.

## What a reader sees today: nothing, and that is stated rather than smoothed over

`generate()` was re-run into a scratch path outside the repo and diffed against the committed feed.
`headline` and `floor_decomposition` are **identical**. The only keys that move are `generated_at`,
`book.produced_by`/`producing_commit` (the HEAD pointer, which is supposed to move) and
`realised.is_the_published_supplier` (a scratch-invocation artefact, not this change — nothing in
this diff routes into it).

This is LATENT because today both legs are withheld: `contrast_bounds` refuses for want of a world
on the superseded floor, so neither leg earns a direction and the split does price a withheld leg.
**What arms it is the work this lane owes anyway** — re-running the decomposition on the current
book. The moment the advantage leg clears its floor while the creation leg does not (which is the
live world's actual state: £2,336 against ±£991 clears, £2,177 against ±£5,923 does not), the page
would have priced resolving the leg it had answered and said nothing about the leg it had not.

## What this does not fix

It does not admit a decomposition of `selection_gbp` when the selection leg is the withheld one.
That would be the right reading of the property, and it is deliberately not built: **no such
artefact exists**, and building an admitting branch for a file nobody has produced is how a page
acquires a route it has never exercised. When the owed decomposition is re-run per leg, the guard
must gain that branch and a sole witness with it.

It also does not price resolving the creation leg. `selection_gbp` has no decomposition at all, so
what a larger book would cost to resolve the one figure on this page that could be value *created*
rather than *moved* remains unestablished — and the page now says so in those words instead of
handing over the other leg's number.
