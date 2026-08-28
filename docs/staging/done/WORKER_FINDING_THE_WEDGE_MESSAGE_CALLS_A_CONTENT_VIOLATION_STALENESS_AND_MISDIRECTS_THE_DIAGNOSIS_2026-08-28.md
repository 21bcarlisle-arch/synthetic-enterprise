# WORKER FINDING — the publish wedge reports a content violation as "staleness", and the word sent the diagnosis the wrong way

**Severity:** LATENT · **Lane:** H_harness

LATENT and not BLOCKING: the control itself is correct and fired correctly — it caught a real
defect and refused to publish over it, which is exactly its job. What is owed is the *label*. No
figure is wrong, no lane must stop.

**Filed** 2026-08-28, delivery-lane tick, while unwedging the publisher on
`unwedge-the-publisher-on-the-derived-artefact-repair`.
**Rank:** backlog. It costs wall-clock per incident, not correctness.

## The finding

`background/derived_artefact_register.stale_in()` returns a `DerivedArtefact` whenever that
artefact's `--check` exits non-zero. Two different conditions produce that exit code:

1. **staleness** — the rendering and its sources disagree, and re-running `--write` fixes it;
2. **a content violation** — the SOURCE is illegal, and re-rendering cannot fix it at all.

The function's own docstring already names this honestly ("Do not read *stale* as *regenerating
will fix it*"). The problem is that nothing downstream carries that caveat. `repair_from` reports
`still_stale: ['docs/design/PULL_FORWARD_PROPOSALS.md']`; the test asserts
`"... is not fresh after a repair — cannot mutation-test from here"`; and the publish gate writes
a `paused_reason` naming five red tests. Every one of those messages says *stale* about something
that was never stale.

## The evidence that this is not theoretical

The doorbell that drew this work reasoned, in good faith, from those messages:

> "Read `background/derived_artefact_register.py` and ask why re-rendering
> `PULL_FORWARD_PROPOSALS.md` does not produce a byte-identical result: ... a non-deterministic
> or tree-state-dependent rendering is the first thing to discriminate."

The rendering is perfectly deterministic and byte-identical on every pass — I verified it
(`--write`, copy, `--write` again, `diff` clean). The actual cause was eight
`block_reason_history:` fields in `docs/design/maturity_map*.yaml` tripping
`pull_forward_proposal.discharge_violations` — `population 8, 12 violations` in a HEAD checkout
against `population 0, 0 violations` in the working tree. Nothing to do with rendering.

That is a seat pointed at the wrong file by the control's own vocabulary. It is also the second
time the word has done this: the fixture docstring in
`tests/background/test_derived_artefact_register.py` records an earlier occasion when
`stale_in` "reported all three stale — so the control's message accused three oracles of being
blind when what was actually broken was this fixture's idea of the running code."

## What is owed

`stale_in` already runs the subprocess and already has `proc.stderr` in hand — it currently
discards it. Two changes, both small:

- return the reason alongside the artefact (a `(artefact, stderr_tail)` pair, or a small record),
  so `repair_from`'s `still_stale` can say *why*;
- have `repair_from` distinguish **did not converge because the source is illegal** from **did not
  converge because the renderings oscillate**. Those are genuinely different defects — the module
  docstring's fixed-point discussion is about the second — and only the second is an oscillation
  worth the `MAX_REPAIR_PASSES` machinery.

The publish gate's `paused_reason` then names the violating atom rather than a test id, which is
the sentence a diagnosing seat actually needs.

## What this is NOT

Not an argument for splitting the two conditions at the *gate*. Both are red at the gate and both
must be, and `stale_in` treating them alike as "must not publish" is right. This is about what the
machine says while it is refusing, not about what it refuses.

## Related

- `[[feedback_the_record_can_outrun_the_code]]` — the same shape applied to authority, which is
  what `discharge_violations` was built to catch in the first place.
- R4 (diagnosis discipline): "before fixing a stuck problem, name the nearest working analogue and
  state the diff." The analogue here was the working tree, and the diff was the population count —
  which is the number that resolved it in about four minutes once looked at directly.
