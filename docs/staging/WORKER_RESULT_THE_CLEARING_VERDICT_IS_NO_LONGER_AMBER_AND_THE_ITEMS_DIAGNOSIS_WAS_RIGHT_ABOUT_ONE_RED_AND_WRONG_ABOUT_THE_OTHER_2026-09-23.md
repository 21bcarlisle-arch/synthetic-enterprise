# The clearing verdict is no longer amber, and the item's diagnosis was right about one red and wrong about the other

**Severity:** RECORDED · **Lane:** A_strategy_governance

The two reds blocking the whole `site/` lane are green. One was the renderer defect the item named.
The other was not a renderer defect at all: a control keyed to paragraph order that a producer
change had falsified, going red on a page that had become more honest.

Claim: `a-clearing-verdict-is-styled-as-a-caveat-so-the-baseline-page-cannot-say-it-won`.
Paths: `site/capabilities/index.html`, `site/test_the_baseline_comparison_reaches_the_reader.py`.

## Premise: spent as written, live in substance

`6e984858f` is already an ancestor of `origin/main`, as the draw said. But the premise that matters
is not the commit — it is whether the two doors are still red. **They were**, both of them,
reproduced on the shared tree before anything was touched. The path check's `already landed` on
`site/test_the_baseline_comparison_reaches_the_reader.py` was also correct and also not the
question: nothing was owed *to* that file, and something turned out to be owed *in* it.

## Red 2 — `test_the_page_tells_WORSE_THAN_CHANCE_apart_from_WE_CANNOT_TELL`

The item's diagnosis was exactly right. `readingOrder` emitted `color:var(--amber);`
unconditionally around the verdict that travels with the lead figure, so `reads BETTER than chance`
— the one state in which a reader may take the figure at face value — wore the same colour as
`we cannot tell` and as the inverted reading.

**The fix is not a new rule; it is the rule that already existed, one render site away.** The
estimand's verdict has two render sites: `readingOrder` when it leads, and `fixedHorizonBlock`'s
`verdict()` when it does not. `verdict()` has carried `r.reading === "better_than_chance"` since it
was written. The lead lost it. So `verdictFor` now resolves the *owner* of the sentence rather than
the sentence alone, and applies the identical expression. It fails closed: only a
`concordance_reading` owner saying `better_than_chance` clears, so a bare `cannot_tell` string, an
unknown reading, or a missing owner is a caveat.

Mutated both ways. Always-amber (the state at HEAD) reds the BETTER leg; always-muted reds the
WORSE leg. Neither leg is the other's.

## Red 1 — `test_a_reading_that_CLEARS_its_null_does_not_say_it`

**The item said this red had the same cause. It does not, and the item never ran the one-variable
control that would have said so.** Its actual failure was `the driven reading did not reach the page
at all` — nothing to do with colour. Two independent things had broken it, and both are the control's,
not the renderer's:

1. **The figure it drove has no reader any more.** The test set `method_skill.concordance = 0.94`.
   Since `_skill_reading_order` landed, the survivor cut's figure reaches the page inside the
   row's *composed sentence*, and `msk.concordance` is only read by the legacy fallback for feeds
   that predate the ordering. Driving it drove nothing.
2. **Its partition was falsified by the same change.** The control split the panel at the
   estimand's own heading and called everything above it "the survivor cut's region". The reading
   order put the **estimand first** — deliberately, because it is the cut the caption's question is
   about — so the estimand's reading *and its own owed `we cannot tell`* now render above that
   heading. Even with (1) fixed, the absence assertion would have failed on a sentence that is
   correctly there.

This is the second time this same leg has been caught keyed to today's layout; its own docstring
records the first (2026-09-18). A region cannot name a population. So the control is now keyed to
the **subject**: `cannot_tell_sentence` composes the phrase *with* its subject, and the sentence
asserted absent is this run's own survivor sentence, verbatim, captured before it is driven away.
The driving goes through `_skill_reading_order` itself, which makes it a control over the producer
and the page together rather than over a field the page stopped reading. A third cut can now take a
place in the ordering without reddening this leg for being third.

The old region split was load-bearing in one way, and that job is kept: a leg asserting the phrase
is absent *everywhere* would go green on a door that rendered nothing. The replacement asserts the
**estimand's** refusal is still present, which is the same partition control keyed to the property.
Mutation-proven: rendering `r.key` instead of the composed sentence reds leg one; rendering no
verdict at all reds the partition leg.

## What I am NOT claiming

I have not established that the reading-order landing was the *only* thing that ever reddened this
leg, only that both causes measured above are sufficient and that neither is in the renderer. And
`site/capabilities/index.html` carried 54 insertions of another lane's churn-belief work before I
touched it; that work is untouched and rides along in the same file, as it must — a pathspec stages
the working-tree copy.

## DONE was "a clean publish", and the publish is now blocked by something else

Stated plainly rather than claimed: **the two doors are green and on origin; the publish has not
completed, and the reason is no longer this item's.** Landed `d08b1b104`, merged `59d87d588`,
pushed — `origin/main` now contains both.

The publisher's *live* refusal field, `liveness_surface_refusal`, reads `behind_origin`, refused by
one path: `tools/run_value_cycle_ab.py`, which is the paired-size-term-floor lane's in-flight work
and is held under a live claim by another writer right now. `background/origin_reconcile` is merging
it in an isolated worktree as this is written. That is their landing to finish, not mine to sweep.

The other refusal field, `blocking_tests`, still cites
`tests/design/test_atom_notes_store.py::test_declarations_match_the_store` — a different subject
again, and the field that readers of this state file have been misled by before. **Neither field
names the two doors any more**, which is the change this item bought. Three state files
(`publish_standing_reds.json`, `.last_gate_blocking_tests.json`, `sim-runner-log.md`) still carry
the two names from earlier runs; they are stale copies and will refresh on the next publisher run,
not evidence the doors are red.

## The class this belongs to

`CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md` has the mirror of this: a control keyed to today's
answer goes red when the code becomes *more* honest and stays green when the claim rots. Both reds
here are that shape from opposite ends — one where the page was wrong and the control was right,
one where the page was right and the control was stale — and an item that inspected neither wrote
one cause for both.
