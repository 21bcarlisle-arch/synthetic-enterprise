**Severity:** RECORDED · **Lane:** A_strategy_governance · **Priority:** P2 · **Proportionality:** reversible / narrow

**Knowledge:** none newly established. The register PUBLISHES understanding that already
existed in `docs/staging/done/DIRECTOR_RULING_SUPPLIER_USE_CASE_REGISTER_AND_SIM_FIDELITY_2026-09-06.md`;
it establishes no new domain constant and invents no number.

# [SEAT-RESULT] The use-case register is published, and my own reachability control was green with the derivation deleted (2026-09-10)

## What was drawn and what landed

Lane 2 site atom `A50_the_supplier_use_case_register_is_published_with_a_status_per_item`,
level 0 → 2. The 2026-09-06 ruling's decision 4: publish the register to Capabilities as
"what a supplier can do with this world", each item carrying its SIM-native test and a
status of *testable now / waits on [plain-English condition]*, with no internal names on
the page.

Landed: nineteen use cases across the four merit-order gates, in
`tools/generate_capabilities_door.py` (`USE_CASES`, `use_case_entry`, `use_case_register`),
rendered on `site/capabilities/index.html`, under nine new controls in
`site/capabilities/test_capabilities_door.py`.

## The design decision that mattered

The ruling's status vocabulary is binary, but the honest unit is not the item — it is each
piece of world-truth the item's test is scored against. So `needs` is a list of
(plain-English truth, work item) pairs, the verdict is "every truth at target", and the
waiting SENTENCE is assembled from the truths actually below target. A hand-written
condition would still ask for the carbon data the day after the carbon data landed; this
one cannot, because the truth drops out of the sentence when its work reaches target.

At today's record: **1 testable, 18 waiting, 2 truths with no work behind them at all.**
Each row publishes "N of M in place", so the item that is one piece short (3.1, buying
energy against the homes actually supplied — waiting only on published forward prices) is
distinguishable from the item with nothing behind it (4.5, splitting a bill by what used
the energy).

## THE FINDING — a control of mine was green with the thing it tests deleted

I wrote `test_the_register_publishes_both_verdicts_and_not_one_flat_state` as the
partition-reachability leg, on this project's own rule that a guard which refuses
everything passes every test of refusal. Then I ran the poison round.

**Poison: delete the level derivation entirely** (`elif False:` in place of the at-target
test, so no truth is ever recorded as waiting). Expected both reachability and the drop-a-
level mutation to fire. **Only the mutation fired. Reachability stayed GREEN.**

The cause: two of the nineteen items (3.3's board-set risk envelope, 4.7's prospect pool)
are scored against a truth with NO work item at all, and those are blocked by a *different*
branch — the `None` branch, which the poison did not touch. Those two supplied the
"waiting" side of the partition on their own. So the control asserted both verdicts were
reachable while the derivation that produces one of them was dead code.

This is the shape this project files as a control that cannot fail, arrived at from a new
direction: not a tautology, not fail-open on its own terms, but **satisfied through a
second branch that reaches the same verdict for an unrelated reason**. Two branches produce
"waiting"; the control counted verdicts, not branches.

The fix is a second leg requiring a waiting item held back ONLY by work below target — the
path the derivation actually walks. Re-poisoned: both legs now fire.

**Generalisation worth carrying:** when a control asserts a verdict is reachable, and more
than one branch can produce that verdict, the control must name WHICH branch it needs.
Counting outcomes is not counting paths. I would not have found this by review — the first
draft reads correct, and it is correct about verdicts. The poison round found it.

## The second fail-open, closed deliberately

An item scored against an unmodelled truth must never read "testable now", or the page
announces a scorable claim whose hidden truth does not exist — the exact thing the register
exists to make checkable. Proven by promoting the WHOLE record to target and asserting
those two items still wait, **with a control leg** showing a fully-modelled item does flip
under the same mutation. Without that leg the assertion would pass on a register that
simply never says "testable now".

## One more thing that was already wrong

`test_the_rendered_feed_carries_no_internal_vocabulary` (§6.2) read only the world,
supplier and seam prose. Three new prose fields would have shipped unguarded while the
control went on passing. It now reads every published string. This is the "guarded by its
words" shape: a control scoped to the subjects that existed when it was written.

## What is NOT claimed

- No use case is BUILT. The register describes what the world could score, not what the
  company does. The ruling is explicit that it "describes, it does not permit".
- The 18 waiting are waiting on truth, not on a decision. Several are one item short.
- The level move to 2 is recorded separately against the promotion gate, not asserted here.

## Reversal

Revert the landing commit. The register is additive: one new key in the feed, one new
section on the page, nine new tests. Nothing else reads `use_cases`.
