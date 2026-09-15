**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, the
blind envelope's world

# The world identity was already widened; what had not moved was the refusal reaching the reader

**Filed 2026-09-15 by the delivery seat**, holding
`the-published-baseline-was-measured-in-a-world-this-tree-does-not-have`. The item said: *"If you
find the identity has already been widened, say so with the measurement and stop; that is a cheap
answer and a good one."* It had been. So this is that answer — and the one thing the item asked for
that was genuinely still missing, which was not the instrument.

## The measurement asked for

`simulation/departure_level_anchor.world_level_identity()` on this tree returns **two** parts:

| part | value | covers |
|---|---|---|
| `digest` | `39a192ce04c1eda8` | the departure LEVEL — `year_level_anchor` over the switching record |
| `homes.digest` | `35f8efe8ff02f245` | the HOME STOCK — 96 homes through `year_premise_stock`, digested as every field of `FabricParameters` |

Both parts carry their own `what_this_identifies` and `what_this_does_not_cover`, and each names the
other, so neither reads as the whole. Landed in `ea9400037`, not by this tick.

**The property, not the instance.** The item warned that the failing case is a home-blind digest
agreeing across two runs whose homes differ, and demanded the control be shown able to reach it.
`tests/simulation/test_the_world_identity_can_tell_two_home_stocks_apart.py` is that pair, and it is
a pair on purpose:

- `test_two_worlds_that_differ_only_in_their_homes_get_different_home_digests` — the new part moves.
- `test_the_departure_digest_cannot_tell_those_same_two_worlds_apart` — the old part provably does
  **not** move over the same two worlds. That is the failing case, exhibited rather than asserted.

Five pass. The envelope's own refusal has both ends too —
`test_arms_with_no_home_stamp_are_refused` and `test_arms_stamped_with_THIS_worlds_homes_do_publish`
— so it is not a guard that refuses everything and passes every test of a guard.

`producing_commit` was likewise already dealt with, and honestly: the labels moved to `launch_label`,
`commit` is `null` with a per-arm reason, and `provenance_note` states what is and is not established.
An honest `null` rather than a plausible sha.

## What was actually still broken

**The instrument was landed and the page was not.** `origin/main:site/data/value_arms.json` still
carried `blind_envelope.available: true` — the full span, positions and percentages — because the
feed had never been regenerated after the refusal went in. Every control in the area was green and
the reader was still being shown a span measured on a housing stock this tree does not have: **105
distinct fabric vectors against the 109 filed, worst-axis KS 1.553x → 1.661x**, arriving through the
fork-closing merge `2212d0eed`.

This is the repository's own named recurring shape, from the other side. The delivery record has
three separate rows scolding this seat for work that landed in HEAD but never reached origin. This
one had reached origin — the *code* had. The *page* had not, and no row noticed, because asking
"did it land" and asking "did the reader's bytes change" are different questions.

## What this tick did

Regenerated `site/data/value_arms.json` at HEAD (so the provenance stamp is the tree it lands in,
not the `acb44a94d` the stale copy on disk carried), landed it as `3d8fbb2a8`, and pushed.

Verified **from `origin/main`'s own bytes**, which is the stronger evidence and the one this seat was
previously corrected into using rather than a clean-extract argument:

```
ORIGIN available: False
ORIGIN why_not: 5 of these 5 books carry no record of which HOUSES they ran on (...)
                The live stock is 35f8efe8ff02f245.
```

`site/capabilities/index.html:1485` renders `be.why_not` directly, so this is in the words a reader
gets and not a footnote. `site/test_the_baseline_comparison_reaches_the_reader.py`: 150 passed.

The item's finish condition was a disjunction — the page *"either shows an envelope whose arms were
measured in the world this tree has, or says plainly that it cannot and why."* The second branch is
now true at origin, which is why the claim is released rather than held.

## What remains, and why it is not held open here

The first branch — re-running the five arms in this world and republishing a live envelope — is
untouched. That is correct sequencing and not an omission: the item was explicit that re-running
first *"produces a second set of figures nobody can prove comparable to anything either, because the
instrument that would prove it is the broken thing."* The instrument now exists, so the re-run is
finally a well-posed piece of work. It is five annual-report runs, which no bounded tick finishes.

**The refusal is what makes it safe to leave.** The page cannot now quietly publish a stale span: it
states it cannot place these books and names both digests. A future re-run is an upgrade from an
honest "we cannot tell" to a figure, which is the direction this codebase wants, rather than a
correction of something misleading that is live.

One thing a re-run must do or it buys nothing: each arm has to be **stamped with
`home_digest`** at run time. `_blind_envelope_homes_refusal` refuses on an unstamped arm exactly as
it refuses on a foreign one, so five fresh runs filed without the stamp would land back on the same
refusal with newer numbers.
