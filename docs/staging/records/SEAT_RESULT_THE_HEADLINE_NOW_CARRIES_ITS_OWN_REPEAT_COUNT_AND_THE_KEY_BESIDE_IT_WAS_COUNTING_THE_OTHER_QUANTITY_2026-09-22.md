**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# The headline carries its own repeat count, the sign is withheld by a rule keyed to it — and the key that count came from was measuring the other quantity

Pre-registration: `docs/staging/records/PREREG_WHAT_THE_HEADLINE_BLOCKS_OWN_REPEAT_COUNT_WILL_SAY_AND_WHAT_QUALIFYING_IT_COSTS_2026-09-22.md`,
written before either number below was looked at. Drawn as
`the-published-floor-still-states-a-sign-across-five-repeated-draws`.

**Premise re-measured at draw time and it is NOT spent.** Both cited commits (`0cbbf1f88`,
`e5f6ee1a0`) are ancestors of `origin/main`, and what they landed is the census and the per-family
repeat count. What they explicitly handed on — *"the census row that carries the repeat count to the
reader, and the `NOISE_FLOOR_PATH` decision that follows it"* — was outstanding. The duplicate-work
check named one rival claim under this very id; no `.seat_work_in_hand.json` exists on the shared
tree or in this worktree, so it was this draw's own id and not another writer.

## The decision, which is both halves and not either

The item offered a choice: carry the count with a derived caveat, **or** withdraw the sign. Taking
either alone is wrong, and the reason is in the second prediction of the pre-registration.

**The sign was already withheld.** `error_bar.selection_leg.sign_is_stateable` has been `false` and
`sign` `null` since 2026-09-18 — for the BOOK reason: the floor priced 164 settled accounts and the
figure prices 154–155. So "withdraw the sign to we-cannot-tell" **changes nothing a reader sees**,
and a repetition rule written as a tightening of that refusal would be a branch nothing could ever
reach on its own. Green forever. And re-running the floor on the figure's own book is **owed work
named on this page** — the day it lands, the staleness refusal goes quiet and the sign returns with
the repeated draws still underneath it and nothing anywhere able to notice.

So the sign is withdrawn by a **second, independent rule** keyed to the repeat count, and the count
is published beside the figure it qualifies. Both halves, because either alone rots.

`NOISE_FLOOR_PATH` was NOT repointed at a wider family. Choosing an instrument by its answer is what
that block refused once already and the width evidence does not make it legitimate.

## THE FINDING, which is the part nobody asked for and is the second time this week

Carrying `_draw_repetition` up to the headline meant printing it at real inputs, and the number that
came back was **3**. Every sentence about that floor says **5**:

- the landed finding of 2026-09-22: *"5 of its 18 draws are repeats"*
- the staging item that commissioned this work: *"5 of its 18 draws repeat another draw"*
- the function's own docstring, written the same day: *"5 of its 18 draws repeat another draw"*

The key is named `draws_that_repeat_another` and it computed `len(values) - distinct`. The published
floor's repeats are **one value twice and one value three times**: 2 + 3 = **5 draws** each share
their value with another draw; 18 − 15 = **3 draws** added nothing the family did not already hold.

**Both numbers are correct and they count different things, and for weeks one name carried both.**
Under the plain reading of that key's own name the prose was right and the code was wrong. This is
the same failure as *average unit rate*, *net margin* and *bill shock*: a concept nobody defined,
then counted, published, and made load-bearing — here as the evidence behind the page's narrowest
bound.

Both are now published and each is named for what it counts:

| key | published floor | what it counts |
|---|---|---|
| `draws_that_repeat_another` | **5** of 18 | draws implicated — a value returned three times implicates three |
| `redundant_draws` | **3** | draws that added nothing the family did not already hold |

They are zero together and positive together, so **every rule keyed to `> 0` is unmoved** — the
census's repeating/clean split, and the finding that the three repeating families are bounded more
tightly than the two clean ones with no overlap, are all unchanged. Only the printed magnitude
moves, and it moves to the number the page's own prose was already claiming. Per-family rows go
1→2, 2→3, 2→3; the two clean families stay 0.

## What the reader now meets

Where the page said

> The estimate sits 2.5 standard errors from zero against this family's own bar of 2.11…

it now says, in amber, immediately after:

> **5 of those 18 draws repeat another draw.** 5 of this family's 18 re-draws returned a value
> another of its own draws had already returned, so the standard error the estimate is graded in
> units of is partly a count of how often this instrument PINNED rather than a measure of how far
> the quantity moves. Across every family on this disk the ones that repeat a draw are bounded more
> tightly than every one that does not, with no overlap between the two groups — so the narrowness
> that would let this mean clear its bar is the same phenomenon as the repetition, and not evidence
> about the choosing.

Rendered on **every** branch including zero. A qualification that appears only when the news is bad
teaches a reader that its absence means the question was not asked.

## Keyed to the property, and both branches reachable

Nothing here is pinned to 5-of-18. The refusal, the sentence and the door control all read the
feed's own count: the day a floor drawn clean at this book lands, the count goes to zero, the
refusal returns `None` and the page states its side **with nobody editing a string**.

And both branches are reachable from artefacts on disk — the published folded eighteen repeats 5 of
its draws, the 12-seed next12 family of 2026-09-17 repeats none of its twelve — which is asserted by
its own control, because a rule whose passing branch no artefact can reach refuses everything and
passes every test of a refusal.

**Mutation-proven.** Neutering `if stateable and repeats_caveat: stateable = False` reds
`test_the_repetition_rule_walks_its_whole_partition` on the leg written for it, not on a different
one.

## What this does NOT establish

- **Not** that the wide bound is right. Not repeating is not being correct, and no claim is made
  that £5,398.31 or £1,558.36 is the true dispersion of the choosing.
- **Not** that the choosing is worth nothing. The page states no side, which is a different claim
  from stating zero.
- **Not** the code change between `4e7938f673` and `a178b56d6` that removed the lockstep. Still open,
  still the next question.

## The gap this leaves, named rather than quietly widened

`_leg_in_this_world` — the `current_world` panel's leg builder — is a **second home** for the same
verdict and it does not go through `_leg_over_its_own_family`, so the repetition rule does not reach
it. It grades off `CURRENT_WORLD_NOISE_FLOOR_PATH`, a different family. Today that panel's selection
leg is unavailable, so nothing is published wrong; the day it resolves, it will state a side with no
repeat count asked. That is one rule with two implementations, which is this repository's most
expensive shape, and it is handed on rather than fixed here because fixing it is a change to a
second published panel and belongs in its own increment with its own evidence.

**Reversal:** `git revert` of this commit restores the previous `sign_is_stateable` (unchanged in
value today — the book refusal already withheld it), removes two feed keys and one rendered
paragraph, and returns `draws_that_repeat_another` to the redundancy count. No figure on the page
moves.
