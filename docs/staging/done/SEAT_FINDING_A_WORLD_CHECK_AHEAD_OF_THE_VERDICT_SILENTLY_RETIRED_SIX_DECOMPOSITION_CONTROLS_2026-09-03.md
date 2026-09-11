**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# A world check placed ahead of the verdict silently retired six of the decomposition's own controls

**Class:** `controls_that_cannot_fail` (primary)
**Filed:** 2026-09-03, delivery seat, Lane 0, claim
`the-baseline-was-beaten-in-a-world-that-no-longer-exists`
**Subject:** `tools/run_value_cycle_ab.py::decompose_floor`,
`tests/tools/test_value_cycle_ab_noise_floor.py`.

## What

`dda5a27b2` added a correct and necessary refusal to `decompose_floor`: legs that cannot name their
world, or that name different ones, are not a decomposition of anything. It was placed **before** the
mode, seed-agreement, reconciliation and sample-size verdicts.

Every fixture in `tests/tools/test_value_cycle_ab_noise_floor.py` predates the world stamp, so from
that commit onward all six of these returned the world refusal instead of the thing they assert:

```
test_the_verdict_is_the_REST_OF_BOOK_leg_against_the_contrast
test_the_remedy_carries_a_price_against_the_PUBLISHED_floor_too
test_legs_run_on_DIFFERENT_seeds_are_not_a_decomposition
test_the_reconciliation_is_published_even_when_it_disagrees
test_the_decomposition_reads_its_sample_size_off_the_LEG_not_the_funnel
test_the_split_publishes_the_MARGIN_and_the_BAR_not_only_the_boolean
```

Verified pre-existing, not introduced by this lane: a clean `git archive HEAD` extract run in
isolation fails exactly these six.

`test_legs_run_on_DIFFERENT_seeds_are_not_a_decomposition` is the clearest instance. It asserts
`"different seeds" in out["why_not"]`, and what it actually received was *"these legs do not say
which world they ran in"*. It went red — so it was not silent — but it was red **for the wrong
reason**, and its subject, the seed-agreement refusal, had stopped being measured entirely.

## The class

This is R15's *scope-assertion-before-the-verdict* shape: a guard placed ahead of the verdict turns a
substantive red into a procedural one. The register already holds it from the opposite direction —
"a SCOPE guard BEFORE the verdict = true RED for the wrong reason". What this instance adds is that
the damage is not confined to the one control whose subject the guard displaces: **every** control
downstream of the guard, in a file whose fixtures share one constructor, stops measuring at once. Six
at a stroke, from a two-line addition in a different file.

It is also why these did not read as a regression worth chasing: six simultaneous reds in one file
look like one broken fixture, and a broken fixture looks like a chore. The thing to notice is that a
red whose message does not name the subject the test names is a control that has changed what it
measures.

**The production path was never affected.** Real legs have carried `world_identity` since the same
commit, so `decompose_floor` behaves correctly on real artefacts. What was lost was the ability to
tell — which matters now, because the decomposition is leg four of what this lane is about to
publish and its reconciliation check is the only thing standing between "two halves of one variance"
and "two unrelated runs".

## The fix

Landed with this finding. `_leg` and `_three_arm` stamp one world by default (`_ONE_WORLD`), with the
digest a parameter so that fixtures which mean to exercise the world refusal set theirs explicitly
and do not inherit the default. All six now reach their own subject; the file is green at 34.

**Proved restored rather than merely green**, which is the distinction that matters here: with the
seed-agreement refusal removed from `decompose_floor`, `test_legs_run_on_DIFFERENT_seeds_are_not_a_decomposition`
fails. Before the fixture repair the same mutation left it passing-as-red — the test could not tell
the difference between the control being present and absent, which is what "retired" means. A green
achieved by making fixtures satisfy a guard, without that check, would have been indistinguishable
from deleting the six controls.

## What this does not fix

The ordering in `decompose_floor` is unchanged and should be: the world refusal genuinely must
precede the arithmetic, because a variance measured over one departure level is not a component of a
variance measured over another. The defect was never the guard's position — it was that nothing
noticed six controls falling behind it.
