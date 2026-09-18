**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# A comment asserting which artefact a CONSTANT names is unguarded when the constant moves in the same commit

**Filed:** 2026-09-18 · **Claim id:** `the-arms-producer-asserts-a-promoted-run-stamp-that-a-repromotion-has-already-falsified`
**Found while:** repairing the `:230` census red — see
`docs/staging/SEAT_RESULT_THE_RETRACTED_SENTENCES_CONCLUSION_HAD_INVERTED_AND_ONLY_ONE_OF_ITS_TWO_HALVES_IS_GUARDED_2026-09-18.md`
**Subject:** `tools/promoted_artefact_claim_census.py::_references` / `_constants_bound_to`

---

## The gap, measured

`tools/promoted_artefact_claim_census.py` grades a sentence only when it references a **promote-by-copy
target** — by filename, by stem, or through a module constant bound to that filename:

    _constants_bound_to(generate_value_arms_data, {…noise_floor.json, …three_arm.json})
      → {'THREE_ARM_PATH': 'value_cycle_ab_s1_three_arm.json'}

`NOISE_FLOOR_PATH` is absent, because it resolves to a **dated sibling**
(`…_noise_floor_folded18_single_arm_20260917.json`), not the canonical path. Every sentence in
`generate_value_arms_data.py` that talks about the published floor by its constant name is therefore
invisible to the census — including the correction landed this turn.

## The instance that proves the class is not hypothetical

`5ce5c3c31` (2026-09-17) moved `NOISE_FLOOR_PATH` from the folded eighteen onto the single-arm
eighteen. Four lines above it, a paragraph asserting *"the folded family is stamped
2026-09-17T15:14:19Z"* was left standing, and stayed standing for a day. That falsification is not a
promote-by-copy: it is a **source-line change that leaves a comment about itself behind, in the same
commit and the same file**. The census is built for the empty-diff case and by construction cannot
see this one; nothing else looks.

## Why this is not fixed here, and what would fix it

Widening `_references` to every dated sibling would pull the census out of its own subject — it exists
because a promote-by-copy moves BYTES and no control keyed to a constant can see it. A claim about
which artefact a constant names is the mirror image: it has a diff, so the control that can catch it is
one that reads the diff, not one that reads the artefact. The smallest mechanism that could fail is a
commit-time check that when an assignment to a `*_PATH` constant changes, the comment block attached
to it is either touched in the same commit or named in the message.

**That is a design to price, not a change to make on the way past.** Filed rather than built, and the
instance it was found on is already repaired.

## What is NOT claimed here

That the census is wrong. It refused correctly on the half it can see, and the half it cannot see is
outside the population it defines for itself. This is a gap between two controls, not a defect in
either — which is exactly the interconnection class the seat is the only place able to notice.
