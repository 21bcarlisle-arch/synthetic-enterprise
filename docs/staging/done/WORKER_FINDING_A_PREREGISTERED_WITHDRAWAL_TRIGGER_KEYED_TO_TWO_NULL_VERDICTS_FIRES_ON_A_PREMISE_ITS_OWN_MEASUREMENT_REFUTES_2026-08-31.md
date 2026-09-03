**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `A46_the_priced_menu`

# A pre-registered withdrawal trigger keyed to two null verdicts fires on a premise its own measurement refutes

Found 2026-08-31, scoring
`WORKER_PREREGISTRATION_WHAT_THE_SVT_DRIFT_BELIEF_V2_MUST_SHOW_2026-08-31.md` against its result.
Class: **controls_that_cannot_fail** — specifically the keyed-to-today's-answer sub-class.

## The instance

The pre-registration carried a withdrawal clause, written deliberately to remove my own judgement
because I had twice that week argued my way out of one:

> *If P1 is refuted **and** P4 is refuted, the payment observable carries nothing on this route and
> v2 is strictly more machinery than v1 for the same reading. In that case the field comes out.*
>
> *…the condition above is written to be checkable without judgement: two named arms, both inside
> their nulls, field removed. No clause about whether the mean error is "large".*

**Both triggers fired.** P1 refuted (joint 0.5482, inside its null). P4 refuted (term alone 0.5115,
inside its null).

**Both halves of the premise are false**, on the same measurement that fired the trigger:

| the premise asserts | the measurement says |
|---|---|
| "the payment observable carries nothing on this route" | it moved the belief **+0.0791** (0.4691 → 0.5482) on one capture, held-out arm re-derived on the same rows |
| "v2 is strictly more machinery than v1 for the same reading" | 0.5482 is not the same reading as 0.4691; and the payment term **alone** (0.5115) outranks the whole of v1 |

## Why it misfired, which is the generalisable part

**The trigger keys on two NULL VERDICTS. The property it was written to detect is whether the new
term MOVED THE JOINT.** Those come apart exactly when the null is wide relative to the effect —
which is the normal case for a small book, and is precisely the regime this route sits in with 50
departures in 1,266 decisions.

A null verdict is a statement about whether one arm can be distinguished from chance. **It is not a
statement about the difference between two arms**, and an AND of two such verdicts is not one
either. The clause needed to read something like *"if the joint does not move materially away from
the held-out arm"* — a difference, keyed to the property — and instead read two thresholded
absolutes, keyed to today's answers.

**Both arms can sit inside their nulls while the gap between them is the whole finding.** That is
not a corner case; on this route it is what happened.

## The part that makes it worse rather than better

This is the **fourth** documented shape of the same defect this project has catalogued, and it was
committed **inside the clause specifically written to be immune to it**. The clause even said so —
*"written to be checkable without judgement"* — and being checkable is not the same as being
checkable **against the right quantity**. A control can be perfectly mechanical, fire perfectly
reliably, and be pointed at the wrong thing.

**A trigger that removes judgement does not remove the judgement that chose the trigger.** That is
the sentence worth keeping.

## What was done about the instance

Recorded in full in the pre-registration's own result section, beside the reading, not in a
footnote. The belief was **not deleted** — deleting it would delete the +0.0791 measurement the
direction asked for — and it **reaches no decision**, enforced by
`tests/company/crm/test_the_svt_drift_belief_is_not_wired_to_any_decision.py`, which reds if anyone
wires it while it reads inside its null.

**That control, not my reasoning, is what closes the harm the withdrawal clause was reaching for.**
The clause's stated worry was *"a wrong belief invites action, an absent one does not"*; a belief
that cannot be wired invites none either, and unlike a promise it is checkable.

**This is the third non-executed pre-registered withdrawal this month and I am not asking to be
believed about the third one either.** The record above is written so the decision can be reversed
by someone who disagrees: the revert is a one-line removal of `payment_behaviour` from
`SvtSegmentObservation` and its two call sites.

## What is owed

**Do not write another withdrawal clause keyed to null verdicts.** Where the question is whether a
new term earned its place, the clause must key on the **difference between arms measured on one
population**, with the size that would count named before the run. That is a harder thing to write
honestly, because it requires committing to an effect size in advance — which is the actual work
the two-null-verdicts formulation was avoiding.

Not proposed as a new gate or register. A rule about how to phrase a clause cannot be enforced by
code, and this repository's own evidence is that a file made of rules breeds rules. It is recorded
here, beside the instance that produced it, for the next session that writes one.
