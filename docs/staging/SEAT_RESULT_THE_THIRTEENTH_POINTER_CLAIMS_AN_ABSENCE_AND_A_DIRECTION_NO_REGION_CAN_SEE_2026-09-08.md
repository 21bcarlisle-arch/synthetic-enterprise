**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the thirteenth pointer claims an absence and a direction no region can see, and the sweep's own count had already rotted

**Claim:** `per-page-pointer-rungs-for-the-thirteen-untied-producer-literals`. **Filed:** 2026-09-08,
delivery seat, from an isolated worktree at `919e600e6`. Pre-registered before the branch was driven:
`docs/staging/records/SEAT_PREREGISTRATION_THE_THIRTEENTH_UNTIED_POINTER_ON_THE_PROOF_PAGE_2026-09-08.md`.

---

## The premise was two-thirteenths alive

The drawn item asked for all thirteen untied producer literals. Re-measured at draw time: `1d1afa40b`
had already driven the twelve in `generate_value_arms_data.py` and states on its own surface that the
thirteenth, in `generate_proof_data.py`, is *"still recorded and unjudged"*. So the premise was spent
for twelve and live for one, and this turn is the one.

The census also **no longer returns thirteen**. Re-run here: **ten** untied literals, nine in
`generate_value_arms_data.py` and one in `generate_proof_data.py`. Twelve minus the three that
`1d1afa40b` reworded out of the vocabulary is nine, so the count reconciles — but two landed files
carried the string *"thirteen ... twelve ... one"* as live prose about today, and it was **stale within
a day of landing**. That is a control keyed to today's answer: it went wrong because the code got
BETTER. Repaired by deleting the count and stating the property, with the reason kept beside it.

## The sentence, and what driving it found

```
tools/generate_proof_data.py:1555 — the `else` arm of _why_households_leave's blind_size,
taken when the reason-mix artefact cannot size the SVT route. Never run by anything.

  "How many departures leave that way is not readable BESIDE THIS measurement, so what
   share of the book THE RANGES ABOVE describe is itself unknown."
```

All four pre-registered predictions held.

**P1 — one landing field. HELD.** Driven through the real `generate()` over the real artefacts, the
sentence lands in exactly one string field: `not_proven[0].note`.

**P2 — one home. HELD.** That field renders in exactly one region of `/harness/`: `#not-proven`. The
parent defect's two-homes shape is **not** on this page. A result, not a pass.

**P3 — the claim is an ABSENCE, and the value_arms rung's verdicts cannot state it. HELD.** Its
`_REFERENTS` admit `above`/`below`/`same`, each asserting the reader WILL find the subject somewhere.
This sentence asserts they will not. **Graded `same` it would have read true for the wrong reason** —
true because its subject renders nowhere, which is the vacuous pass wearing a tick, and it would have
gone on reading true after the two arms started co-emitting. So the verdict here is `absent`, and it
carries a witness: the figure is measured into `#not-proven` on the OTHER arm of the same `IfExp`
before its absence on this one is allowed to count. Both arms built, both rendered, neither declared.

**P4 — the second direction is unreachable at region granularity. HELD.** `the ranges above` names the
bill-shock / price-position / service ranges, and the producer composes them into the SAME string by
the same f-string. Every landed control judges at REGION granularity, so the best any of them can say
is `same`: the claim is not false, it is **unreachable**. Judged here by text order inside the field —
the ranges at character 400, the pointer at 1290 on the driven build — which is what "above" means to
a reader inside one block of prose.

**And the site-wide vocabulary must NOT be widened to reach it.** Measured rather than assumed: adding
`range|interval` to `_HERE_RELATIVE` picks up `generate_value_arms_data.py:1693`, *"whether a larger
settled book moves the interval above"*, where "above" is the direction a NUMBER moves and not a place
on a page. A site-wide vocabulary that admits that starts refusing arithmetic. Hence `_EXTRA_PHRASES`,
page-scoped, argued from the measurement — and a fail-closed leg that refuses any direction the page
claims and this rung does not judge, because *three landed controls saw one direction in a sentence
that claims two* is exactly how the gap stayed open.

## What was built

`tests/tools/test_the_proof_pages_undriven_pointers.py` — the fourth and last of the family.
The census is DERIVED (`_untied_literals` and `_owning_symbol` were parameterised on the producer and
imported, not copied — two AST censuses would drift). The branch is driven through the real
`generate()` with `OUT_PATH` redirected to scratch, so nothing publishes a marked payload. **The marker
rides the producer's own interpolation**: `causes_not_in_the_interval`'s keys are joined into the same
sentence chunk, so a findable token lands inside the exact string under test without replacing a value
or moving the door off its branch. Both referents come from the producer's AST — the other arm of the
same conditional for the absence claim, the producer's own composed fragment for the intra-field one —
so a rewording reds instead of quietly ceasing to match.

**There is deliberately no reading-order judge in it**, which is the one way it differs from the rung
it copies. Both of this page's directions resolve inside one region; a `{anchor: position}` map read
off `/harness/` would have been a component that could never change a verdict.

Fails closed in five places: an unrecipe'd symbol, a driven branch reaching no field, a sentence
reaching no region, an unregistered direction, and an absence claim whose subject cannot be shown
renderable on any branch.

## R15 — every poison run against the real tree and reverted

| Poison | Result |
|---|---|
| make both arms of the conditional emit | absence leg reds naming `['not-proven']`; nothing else |
| compose the ranges AFTER the pointer in the note | intra-field leg reds, `463` against `422` |
| drop the recipe | census leg reds naming `_why_households_leave` |
| `_homes_of` returns nothing | zero-homes leg, absence leg and the witness all red |
| unregister `ranges above` | the unjudged-direction leg reds naming the phrase |

Both halves of each partition are asserted: the honest wording and the real composition order stay
green in every poisoned position, so the judge is not refusing its whole partition. `site/data/proof.json`
is untouched — the branch is one the current artefacts do not take, and nothing a reader sees moved.

**24 tests pass** across the two site sweeps, the value_arms rung and this one.

## What is next

* **`_EXTRA_PHRASES` is a page-scoped vocabulary and there is now precedent for a second one.** The
  measured refusal to widen `_HERE_RELATIVE` is right, but nothing yet stops a third page inventing its
  own list and disagreeing with these two. Worth one census across the pages that have rungs before it
  becomes three copies.
* **`floor_decomposition.different_contrast_caveat` and `priced_accounts_the_arm_itself_drove_out`**
  remain written-by-a-producer and read-by-no-door, carried over unchanged from the previous result.
* **The intra-field direction class is unmeasured site-wide.** This page has one; nothing has asked how
  many other composed prose blocks carry a direction that resolves inside themselves. The published
  sweep cannot see them by construction — it matches strings into regions, and both ends of an
  intra-field pointer are in the same region.
