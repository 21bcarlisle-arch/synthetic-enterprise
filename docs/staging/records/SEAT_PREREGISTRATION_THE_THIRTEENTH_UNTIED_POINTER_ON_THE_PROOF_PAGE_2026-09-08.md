# PRE-REGISTRATION — the thirteenth untied pointer, on the proof page

**Filed 2026-09-08, before the branch was driven.** Severity: MINOR (a control gap, not a live
falsehood — unless the measurement says otherwise, which is the point of filing first).

## What is already settled, and is therefore not a prediction

`1d1afa40b` drove twelve of the thirteen untied here-relative producer literals — all of
`generate_value_arms_data.py`'s — and its own commit message states the thirteenth, in
`tools/generate_proof_data.py`, as still recorded and unjudged. Re-measured in this worktree at
`919e600e6`: the producer census now returns **ten** untied literals, nine in
`generate_value_arms_data.py` and one in `generate_proof_data.py`. Twelve minus the three that
`1d1afa40b` reworded out of the vocabulary is nine, so the count reconciles and the residue is
exactly one literal:

```
tools/generate_proof_data.py:1555, inside _why_households_leave, the blind_size fallback:
  "How many departures leave that way is not readable beside this measurement, so what share of
   the book the ranges above describe is itself unknown."
```

`_here_relative_phrase` matches **`beside this`** and nothing else. That is an observation, not a
prediction: `the ranges above` is a here-relative pointer in substance and `range` is not in the
registered noun list, so no landed control judges that half of the sentence.

The prose in two landed files pins **thirteen / twelve / one**, which is today's answer rather than
the property, and it is already stale. That is a defect to repair, not a thing to measure.

## The predictions

**P1 — one landing field.** Driven, the sentence lands in exactly ONE string field of `proof.json`
(expected: the `_why_households_leave` row's `note`, reached through `_not_proven`).

**P2 — one home.** That field renders in exactly ONE region of the `/harness/` door, so the parent
defect's two-homes shape is not present here either.

**P3 — the claim is an ABSENCE, and the value_arms rung's verdict vocabulary cannot say it.**
`_REFERENTS` there admits `above`, `below`, `same` — each asserting the reader WILL find the subject
somewhere. This sentence asserts the reader will NOT: the departure count is *not readable* beside
the measurement. Predicted: judging it needs a fourth verdict whose truth condition is the opposite
one — the named subject must render in NO region the sentence renders in — and a rung that reused
`same` unchanged would report this sentence as true for the wrong reason.

**P4 — the second direction is unreachable at region granularity.** `the ranges above` names the
bill-shock / price-position / service ranges, which the producer composes into the SAME string.
Predicted: a region-granularity judge can only ever call that `same`, so an honest rung must refuse
it as unjudgeable rather than grade it — and saying so on the surface is the result.

## What would refute each

P1 is refuted by two or more landing fields (the note is composed twice), P2 by two or more homes
(which would make this a live misdirection and a MAJOR finding, not a control gap), P3 by the
subject rendering in a region such that `same` is the true and meaningful verdict, P4 by the ranges
landing in a field of their own.

## What gets built either way

A per-page rung for `generate_proof_data.py` in the shape `1d1afa40b` established: the census of
untied literals DERIVED rather than listed, the branch driven through the real `generate()` over the
real artefacts, the marker riding the producer's own interpolation into the sentence, homes taken
from a real `/harness/` render, and fail-closed on an unrecipe'd symbol, an undriven branch, a
sentence that reaches no region, and a phrase outside the referent table.
