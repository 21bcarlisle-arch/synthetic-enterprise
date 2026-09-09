**Severity:** BLOCKING · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery

# FINDING — a promote-by-copy put a false claim in the page headline, and no world guard could see it

**Filed:** 2026-09-09, delivery seat (isolated worktree `/var/tmp/se-seat-executor`).
**Pre-registration:** `SEAT_PREREG_RECONCILING_THE_TWO_VALUE_ARMS_CONSTANT_SETS_ONTO_THE_PROMOTED_ONE_2026-09-09.md`,
written before any repair was ported. P1–P6 all held; **D2's severity in that document is
corrected in it, beside the claim.**

BLOCKING because the live `site/data/value_arms.json` carried a false statement in its headline
sentence — not a footnote, not a latent branch — and the page is the company's public evidence
that the method works.

---

## What the page said, quoted from the feed built at `9d7cd5e4f`

> "IN THE WORLD AS IT IS NOW, the same comparison gives £17,739, measured **2026-09-08T00:19:54Z**.
> … It is a LARGER advantage than the £17,453 below."

The £17,453 below was measured **2026-09-08T21:01:30Z** — twenty-one hours *later*. The page
presented its older run as the present and its newer run as the history, and told a reader the
present was better.

## Why nothing caught it

`_current_world_contrast` had four guards and **every one of them asks about the WORLD**: does this
run name the live digest, does its floor, is the floor the undecomposed leg. All four passed —
correctly, because both runs name `39a192ce04c1eda8`.

None could ask which of the two runs is the *later* one, because until 2026-09-09 the
current-world run always was: the panel below was the 2026-08-31 canonical run and anything in the
live world postdated it by construction. **The guard nobody wrote was the one for the invariant
that held for free.**

## THE MECHANISM, AND IT IS THE GENERAL LESSON

The 21:01Z re-take reached `THREE_ARM_PATH` by **promote-by-copy** — bytes written onto
`value_cycle_ab_s1_three_arm.json`. No constant moved. No import changed. `git diff` on the
producer was empty.

> **A promotion that moves bytes rather than constants can invert a page's meaning while leaving
> every source file, every constant and every world guard untouched.** Anything keyed to a
> constant is blind to it by construction.

This is the same shape, three times in one file on one day:

1. **The headline's currency claim** — above.
2. **`how_to_read_this`'s date** — the literal `"published beside the 2026-08-31 run"` became false
   the moment the promotion landed, because the run beside it stopped being the 08-31 one. A
   sibling repair on 2026-09-08 had already fixed the *figure* in the neighbouring key
   (`_against_the_panels_figure`) and left the *date* one line down, because that repair was aimed
   at what a constant pointed to.
3. **`_current_world_bound`'s named witness** — the docstring named
   `value_cycle_ab_s1_noise_floor.json` as the sole artefact that satisfies the LEG guard and must
   still fail the WORLD one. That file *is* the promotion target, so it gained
   `world_identity.digest = 39a192ce04c1eda8` and stopped having the property.

**Item 3 is smaller than it first looked, and the correction matters more than the finding.** The
first reading — recorded in unpromoted commit `076664967` and carried into this document's
pre-registration — was that the guard had gone *untestable*. It had not.
`NOISE_FLOOR_NO_WORLD` in `tests/tools/test_generate_value_arms_data.py`, the constant that
actually drives the world leg, **was moved to the dated path the same day by the lane that did the
promoting**, with its own note describing the same hazard. The guard kept its witness. What
diverged is the **producer's prose against the control's subject**: the module's own account of
its guards named one file while the control named another. A path in a comment is a reachability
edge, and an edge pointing at an artefact that no longer refuses is not caught by the control it
purports to describe — but it is a documentation defect, not a dead guard.

## What was already fixed by another lane, and is NOT duplicated here

Two independent lanes repaired the same defect concurrently, twice:

- **`_row`'s rounding.** Python's banker's `round()` against the door's half-up `Math.round`.
  Never fired until the 09-08b run realised 0.625 and 0.525. `origin/main` already carries a
  `decimal.ROUND_HALF_UP` helper with a docstring naming the same date and the same run. No second
  implementation was added.
- **The world-guard witness**, above.

Both were found by this seat *and* by the rival lane, from opposite ends, within one day. Neither
lane could see the other. **This is the cost of concurrent lanes on one surface, and it is paid in
duplicated work rather than in wrong answers — which is the cheaper of the two.**

## The repair

`is_the_later_run` compares the two artefacts' own `generated_at` stamps. When the block is not the
later run:

- `_current_world_clause` **composes nothing** — the currency claim is withdrawn from the headline.
- The block stays `available`, **with every figure and its bound intact**. Refusing the block
  outright was tried first and reverted: `composition` lives inside that payload, so
  `available: False` also takes the census answering the mission's own question — *value made or
  value moved* — off the page, and leaves it saying "THIS PUBLISH STATES NO COMPOSITION OF THE
  ADVANTAGE" under a headline stating the level leg is 98% of the advantage. **What is wrong when
  the runs invert is the CURRENCY CLAIM, not the figures.** They were honestly measured, they name
  this world, and their composition is as readable as it ever was.
- `why_the_headline_omits_it` states both stamps, so the silence is one a reader can tell from
  having nothing to say. `superseded_generated_at` carries the other panel's stamp so the ordering
  is checkable **from the payload**, not from prose — a sentence is not something a control can
  compare.
- `is_the_later_run` is published on the branch where it is **True** as well as where it is False.
  A field that only appears when something is wrong is a field a reader never learns to look for.

**Keyed to the property, not to today's pair.** It is a comparison of two stamps, not a pin on
either constant, so it survives every future move of either path *and* every promote-by-copy, and
goes quiet of its own accord the moment a genuinely later run lands on
`CURRENT_WORLD_THREE_ARM_PATH`.

`sources[]` is now derived from the constants `generate` actually opens. It was four literals of
which two were wrong: it cited `value_cycle_ab_s1_three_arm_20260903.json`, which the page never
reads, and named neither current-world path, which it does — in the one field a reader would use
to check the figures against the artefacts.

## Controls, and the poison round that proves they can fail

`test_which_panel_is_the_LATER_run_decides_whether_the_headline_may_claim_currency` drives **both
sides of the partition** from three real runs differing only in their stamp, and asserts the
positive leg RESOLVES — so a world drift cannot make the negative leg pass vacuously. One control
over the whole partition, not a leg per branch: a field that were always `False` would satisfy
every assertion about the refusal while making the page permanently silent about its own run.

Both subjects are pinned by their **dated** names and `THREE_ARM` — the canonical path — is
deliberately used for neither. That path is the promotion target; which run it holds is a property
of the last release, not of the control.

Poison round, each mutation applied to the producer and reverted:

| Mutation | Result |
|---|---|
| `is_the_later_run = True` hardwired | **killed** |
| stamp comparison reversed (`<` → `>`) | **killed** |
| `_current_world_clause`'s silence deleted | **killed** |
| `why_the_headline_omits_it` forced to `None` | **killed** |
| `sources[]` back to a literal | **killed** |
| site third-state assertion inverted | **killed** (branch is reached, not dead) |
| site fixture re-pinned to the promotion target | **fails loudly**, does not pass vacuously |

## What is next

**The class is not closed, and closing it is not this turn's work.** Three instances of one
mechanism were found in one file by reading it. Nothing censuses the rest of the tree for the same
shape: **a published claim keyed to which artefact sits at a promoted path, where the claim is
stated in prose or a literal rather than derived.** `tools/` has other promote-by-copy targets and
other pages built off them.

The specific question a census should ask is not "does a constant point at the right file" — every
one of these passed that — but **"if the bytes at this path were replaced by a newer run of the
same shape, would any sentence on the page become false?"** Filed as the finding's own next step
rather than minted, because the right scope is a question for the seat's next orientation and the
answer may be that one AST guard over date-literals-beside-artefact-reads covers it.
