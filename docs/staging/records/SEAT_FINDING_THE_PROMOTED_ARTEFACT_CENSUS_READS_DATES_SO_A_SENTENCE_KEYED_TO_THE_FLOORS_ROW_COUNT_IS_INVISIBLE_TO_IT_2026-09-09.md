**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — land the nine-seed floor through the witness path and grade its pre-registration beside it) · **Class:** controls_that_cannot_fail

# The promote-by-copy census reads run IDENTITY, so a published sentence keyed to the floor's ROW COUNT is invisible to it — and this turn's own promotion is what would falsify one

**Written 2026-09-09T14:40Z, while PID 704091 is still in flight.**
`docs/observability/value_cycle_ab_s1_noise_floor_20260909b.json` does not exist yet and no figure
from it has been read. This is a statement about the tree as it stands *before* the promotion, and
it is filed before the promotion for the same reason its two siblings were filed before the run:
a hazard named after you have walked into it is not a finding, it is an excuse.

---

## Why this was looked for at all

`SEAT_FINDING_THE_PRODUCERS_NAMED_WITNESS_AND_THE_CONTROLS_REAL_ONE_DIVERGED_WHEN_A_PROMOTION_OVERWROTE_THE_PATH_2026-09-09.md`
states the general lesson this turn was told to read before promoting:

> **A promotion that moves bytes rather than constants can invert a page's meaning while leaving
> every source file, every constant and every world guard untouched.**

and leaves the census of the rest of the tree as its own next step, with the question a census
should ask stated exactly:

> **"if the bytes at this path were replaced by a newer run of the same shape, would any sentence
> on the page become false?"**

`tools/promoted_artefact_claim_census.py` was built for that question. This turn asked it of the
promotion this turn is about to make — replacing three-seed bytes at `NOISE_FLOOR_PATH` with
nine-seed bytes — and the census returns nothing, because it is not the question the census asks.

## What the census actually asks, quoted from its own output

    CLAIMS ABOUT WHICH RUN IS THERE  14   ordering-only 8   STALE 1

Its subject is **run identity**: a date literal, or an ordering word (`newest`, `sole witness`),
compared against the artefact currently at the promoted path. Every row it emits is of the form
*token `2026-08-31` vs `docs/observability/value_cycle_ab_s1_three_arm.json`*.

That catches the three instances the sibling finding names, and it caught them well: the one live
`STALE` row at `tools/generate_value_arms_data.py:5757` is a comment *narrating* the repaired
defect, which is a false positive of a benign kind and not this document's subject.

**A run's row count is not its identity.** Replacing a three-seed floor with a nine-seed floor of
the same date, same world and same mode changes no token the census reads. Every date literal stays
true. Every ordering word stays true. And a sentence that says *how many seeds* produced the
published bound goes from true to false without a single row moving.

## The instance, in published prose

`tools/generate_value_arms_data.py:963` `_priced_against_which_floor` emits, into
`site/data/value_arms.json`:

> "That price is against the two legs' own total, which came to {:.2f}x the ±figure this page
> states — **within what three seeds alone produce**, and still a real difference to anyone acting
> on it."

`three seeds` is a literal in a `return`. The ±figure the sentence is about is the floor's spread,
which is what `NOISE_FLOOR_PATH` supplies and what this turn's promotion replaces with nine rows.

**It is LATENT and not BLOCKING, and the distinction was checked rather than assumed.** The branch
is gated on `abs(ratio - 1.0) >= 0.1` over `reconciliation_ratio` and on two decomposition keys
being present. `grep -o "within what three seeds alone produce" site/data/value_arms.json` returns
nothing and a JSON-wide search for `three seeds alone` over the current feed returns not found — so
the sentence reaches no reader today. It is a false sentence waiting on a branch, not a false
sentence on the page.

## The part that is NOT a fix, and why it is being left alone

The obvious repair is to derive the count instead of stating it. **It is not obvious which count.**

The sentence sits inside a block whose every other number is read from the *decomposition* artefact
(`DECOMPOSITION_PATH`) — `decomposition.get("seeds")`, `priced_share_of_variance`,
`share_at_which_a_bigger_book_could_resolve_it`. `_priced_against_which_floor` takes
`decomposition` and nothing else. But the quantity its sentence is *about* — "the ±figure this page
states" — comes from the **floor**. Today both artefacts carry three seeds, so the literal is true
either way and the ambiguity costs nothing. After this promotion they differ, and the sentence
means one of two things with two different truth values.

This repository's own rule applies before the repair does: **before measuring a thing, say what it
is.** Threading `floor["seeds"]` into that function would produce a sentence that is derived,
green, and possibly about the wrong artefact — which is strictly worse than a literal, because a
derived figure is read as established. Establishing which artefact the reconciliation ratio's
tolerance belongs to means reading `run_value_cycle_ab.decompose_floor`, and that is more than this
turn holds while the floor it exists to land is still being written.

**So the honest state is recorded and the guess is not made.**

## What is next

1. **Settle the referent, then derive.** Read `decompose_floor` for which artefact
   `reconciliation_ratio`'s tolerance is measured against, then pass that artefact's own row count
   into `_priced_against_which_floor` and delete the literal. One control: drive the branch with a
   floor and a decomposition carrying *different* row counts and assert the emitted sentence names
   the right one — a control keyed to the property, which a matched pair cannot distinguish and so
   cannot be written from today's tree.
2. **The census gains a second question, or it does not and says so.** "Which run is at this path"
   and "how many rows does the run at this path have" are different claims about the same
   promote-by-copy. Widening the existing scanner is *not* obviously right: a row-count literal has
   no fixed token shape the way a date does (`three seeds`, `3 seed re-draws`, `two degrees of
   freedom a side` are all the same claim), and a scanner that matches `three` across this tree
   would drown. The candidate worth costing first is narrower — **flag any integer-word literal in
   a string that a function also reads a row count for**, which is an AST question and not a
   substring one.
3. **Do not read the census's green as coverage of this promotion.** That is the whole finding: the
   control ran, passed on its own terms, and its terms do not include the change being made.

*Filed before the promotion. If the nine-seed floor lands and this sentence is still absent from
the feed, that is this document's LATENT grade holding, not the hazard going away.*
