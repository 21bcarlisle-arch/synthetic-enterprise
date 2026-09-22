**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The membership claim had no warrant, and two of three callers were safe only by accident

**Filed:** 2026-09-18 · **Claim id:** `republish-the-arms-decomposition-over-one-priced-book`
**Grades:** `8f5c57f8d` (HEAD at draw), `47d3115f7` (the funnel repair the item asked me to verify)

---

## State in one line

Owed item **3** of the five in
`SEAT_RESULT_THE_ARMS_NOW_PRICE_ONE_BOOK_SIX_CONTROLS_REFUSE_THE_REPUBLISH...` is **done and
landed**: the staleness answer is a REQUIRED parameter of `_leg_over_its_own_family` and the
membership claim is withdrawn when it fires. Owed items 1, 2 and 4 are **not mine to have done this
turn** and the reasons are below — one is spent, the rest are a live rival's.

## The drawn item's first clause is SPENT, and I did not take its word for it

The item says *"Merge `origin/main` first (HEAD is one behind `47d3115f7`; verify it really does
repair the three `test_the_renewal_funnel.py` legs rather than taking this line's word)."*

Both halves re-measured:

| the item's claim | measured |
|---|---|
| HEAD is one behind `47d3115f7` | **false** — HEAD is `8f5c57f8d`, a DESCENDANT of it, and `HEAD == origin/main` |
| there is a merge to do | **false** — nothing to merge; `git fetch` moved nothing |
| `47d3115f7` repairs the three funnel legs | **true** — verified, not taken on the line's word |

The verification is the part worth recording, because the item explicitly refused to be trusted on
it. In a clean `git archive` extract of HEAD with none of my changes in it:
`tests/tools/test_the_renewal_funnel.py` → **24 passed**. So owed item 1 is discharged by
`47d3115f7`, which landed by another route after the item was written. The doorbell's own PREMISE
CHECK said as much; this confirms it against the tree rather than against the notice.

## The rival claim, and why I did NOT take the six controls

`the-product-gate-census-answers-per-record-while-the-guard-refuses-per-term` has been live in an
isolated worktree since 09:36 (pid 2158951, still running at the time of writing). Its WORK section
is a **superset of this item's tail**: the six controls, `THREE_ARM_PATH`, and
`site/data/value_arms.json` — and it carries an argument this item does not:

> *"Census the product gate PER TERM ... then repair the six controls and republish — IN THAT
> ORDER. Republishing first entrenches the wrong verdict under a fresh `generated_at`."*

That argument is sound and it outranks this item's ordering, which was written before the census
defect was known. **Promoting the 09-18 artefact this turn would have published
`a_found_account_can_reach_the_product_gate: true` under a fresh stamp** — the field the live
page's sentence turns on, and the one the rival has established is answered on the wrong unit.
Two lanes racing to promote the same artefact would also have been two ids for one piece of work.

So I took the one piece of this item that is **in no other claim**: owed item 3, which the rival's
item never mentions. Disjoint by file region, and it is a precondition of the republish rather
than a competitor for it.

## What was actually wrong, and it is not what the item said

The item names *"the two sentences at :3779 and :3874"*. Those line numbers are stale — the tree
moved to `:3935` and `:4026` — and, more to the point, **there were three published sentences, not
two**. `_selection_leg_reading` composes a fourth from its own assumption:

> *"The one published run is a single member of those {n}"*

That one is the sentence the page actually renders. A remedy that fixed only the two named would
have left the rendered claim false — the shape where a finding's owed remedy is one line short
because the summariser re-draws what the block fixed.

**And the diagnosis of WHERE it fires was available and had not been taken.** `_seed_spreads`
already refuses a stale floor outright (`available: False, reason: stale`). Both
`_legs_on_one_bar` and `_selection_sentence` take their family through it, so **neither could ever
have published this defect**. Only `_error_bar` can: it builds its spread dict inline from the
floor's own seed rows and so never meets that refusal. That is why one artefact said both things —
`error_bar.reading` stating a sign eleven lines above `legs_on_one_bar.why_no_leg_is_graded` saying
no direction could be stated at all.

A guard that two of three callers happen to route through is not a guard. The question is now asked
where the sentence is composed.

## The repair

`_leg_over_its_own_family(spread, single_run, single_run_clock, staleness_caveat)` — four required
positional parameters, **no defaults**. All three call sites pass their own answer:

| call site | what it passes | why |
|---|---|---|
| `_error_bar` | `_staleness_caveat(floor, three_arm or {})` | the only site that builds its family inline; the defect's home |
| `_legs_on_one_bar` | the same derived call | states rather than assumes what `_seed_spreads` already refused |
| `_selection_sentence` | `spreads["staleness_at_admission"]` | holds no floor; **reads** the answer instead of typing `None` |

When the caveat fires, what is withdrawn is every claim **relating** the family to the run —
membership, `single_run_inside_the_family`, `single_run_on_the_other_side_of_zero`, and the SIGN.
What is kept is the family's own arithmetic, which is true of the family whichever book the run came
from; blanking it would trade this defect for the silence R12 refuses.

### A `None` that was checked and a `None` that was never asked are now different

`_seed_spreads` runs its staleness test `if three_arm is not None`. A caller with no point estimate
reaches the admitting return **having tested nothing**, and returned the same empty answer as a pair
it had actually checked. `_selection_sentence` can only get the answer from there, so it would have
taken that silence for a clean bill and claimed membership on it. `staleness_at_admission` now says
*"was never asked"* in words and withdraws the claim exactly as a failed test would.

### The defect I caught by printing the block before writing the test

The unstateable sentence was written when the only way to be unstateable was to sit too FEW errors
from zero, so it read *"short of the {bar}"* unconditionally. A stale family is now also
unstateable — and the family that provoked all of this sits **5.1 errors from zero against a bar of
2.11**, so the page would have told a reader 5.1 was short of 2.11.

**Nothing in the suite would have caught it.** Every assertion was about the verdict, and the
verdict was right. What caught it was printing all four branch combinations at real inputs before
writing the test, per this repository's rule. The first replacement I wrote then said *"past the
bar"* — equally false for a family that is both stale AND short of its bar, so the sentence now
asserts the comparison in neither direction and prints both numbers.

## Mutation-proven — six mutations, six distinct controls

| mutation | fires |
|---|---|
| `staleness_caveat` gains a default | `..._is_REQUIRED_of_every_call_site` |
| `one_book = True` (fail-open) | 3 controls |
| the sign is no longer withheld across books | `..._withdraws_its_membership_claim...` |
| the reading falls back to "short of the bar" | `..._never_tells_a_reader_a_CLEARED_bar_was_short_of_it` |
| never-asked reported as clean | `..._does_not_let_NEVER_ASKED_pass...` |
| the summariser re-decides membership itself | `..._do_not_merely_go_quiet` |

Each control asserts **both** sides of its partition — the clean branch is asserted to still state
its sign and still claim membership over the same inputs, so a leg that withdrew unconditionally
fails rather than passes. The witness caveat is `_staleness_caveat`'s real return on a pair it
refuses, not a typed string: a fabricated one would pass against a leg keyed to nothing at all.

## What this moves on the LIVE feed: six additive keys, and nothing else

A fail-closed control cannot change live bytes on a correct feed, so predicting that it will is
predicting a defect. Measured rather than asserted — the live pair is **not** stale (the folded-18
floor is stamped 2026-09-17T21:39Z, the published run 2026-09-10T14:04Z, so the floor is NEWER than
the figure it bounds and `_staleness_caveat` returns `None`). The 09-18 pair, by contrast, **fires**.

One-variable attribution, HEAD's generator against mine over byte-identical artefacts:

| leaf | HEAD | mine |
|---|---|---|
| `contrast_bounds.staleness_at_admission` | absent | `None` |
| `error_bar.selection_leg.sign_withheld_because` | absent | `None` |
| `error_bar.selection_leg.single_run.is_a_member_of_the_family` | absent | `True` |
| the same two keys on each of the three `legs_on_one_bar` legs | absent | `None` / `True` |

**No existing value moved.** Every other leaf in that comparison is an artefact of the extract
having no `.git` — `publishing_tree_commit`, the objective block and the whole `departure_level`
panel go unavailable in a `git archive` checkout at every commit, which is a known property of this
measurement and not a difference between the two generators.

`site/data/value_arms.json` is **deliberately not in this commit**. Regenerating it now would
republish under a fresh `generated_at`, which is the thing the rival claim's ordering argument
exists to prevent, and the numeric spreads in the committed copy are already stale against the
artefacts on disk — a difference that is another lane's to land, not mine to sweep in.

## Owed, in the order it should be taken

1. ~~The three `test_the_renewal_funnel.py` legs~~ — **discharged by `47d3115f7`**, verified here.
2. **The five keyed-to-today's-answer controls** — the rival claim holds these.
3. ~~Thread staleness into `_leg_over_its_own_family`~~ — **this commit**.
4. **Promote the 09-18 run and republish** — deliberately NOT done; it must follow the rival's
   per-term census fix, or it entrenches `a_found_account_can_reach_the_product_gate: true` under a
   fresh stamp.
5. The folded-eighteen floor on the post-fix tree (~18 hours) — what restores a sign to either leg.
6. The one-variable run that would attribute P2's reversal.

**The page is not yet rendering the 09-18 book**, so this item's "done means" is not met and this
says so rather than reporting the half that worked. What is now true is that when it IS promoted,
the page can no longer call the run a member of a family drawn over another book, and cannot state
a direction off one — which is the refusal the item asked to survive the republish.
