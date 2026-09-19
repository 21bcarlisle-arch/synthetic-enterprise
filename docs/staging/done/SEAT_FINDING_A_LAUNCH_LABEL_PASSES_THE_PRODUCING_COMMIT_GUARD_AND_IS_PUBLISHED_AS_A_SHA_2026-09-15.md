**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the published baseline was measured in a world this tree does not have)

# `producing_commit.commit` guards only against the literal string `"unknown"`, so a launch label is stamped as the commit that drew the figures

**Filed 2026-09-15, delivery seat.** Found while stamping the provenance into
`docs/design/blind_envelope_arms_2026-09-11.json` — the direction said the arms' `producing_commit`
values were labels rather than shas and to "stamp the real commit while you are in there". There is
no real commit to stamp, and the reason is a fail-open in the producer.

---

## The mechanism

`tools/run_annual_report._run_identity_header` (line ~264) decides whether a run can name its code:

```python
resolvable = commit and commit != "unknown"
```

and its own docstring says exactly what that is for:

> `commit` MAY BE THE STRING `"unknown"`, which is `_git_commit_hash`'s failure sentinel and is
> truthy. […] A `producing_commit` block may not: every consumer of that shape in this tree keys on
> `commit` being None and reads `unavailable_because` for the reason, and **a placeholder that
> satisfies a presence check is the fail-open the block exists to close.**

The guard closes that fail-open for one value. `commit` arrives as the caller-supplied `code_commit`
argument, and any other truthy string — a branch name, a run label, a typo — passes `resolvable`
and is written into `producing_commit.commit` with `unavailable_because: None`, which is the shape
that says *this is established*.

## The instance, and it is the one the page rests on

The four first-hand blind-envelope arms were launched with labels. Read back out of their own run
outputs on this box today:

```
/var/tmp/p6_arm_cull.json        producing_commit.commit = 'p6-arm-cull'      resolved_at 2026-09-11T00:33:46Z
/var/tmp/p6_armC_cull83.json     producing_commit.commit = 'p6-arm-cull83'    resolved_at 2026-09-11T04:53:43Z
/var/tmp/p6_armD_tenure.json     producing_commit.commit = 'p6-arm-tenure'    resolved_at 2026-09-11T04:53:30Z
/var/tmp/p6_arm_chosen.json      producing_commit.commit = 'p6-arm-chosen'    resolved_at 2026-09-11T00:33:59Z
```

Every one carries `unavailable_because: None` and `resolved_when: "at process start, before the world
ran — this is the commit whose code drew every figure below"`. The sentence is false on all four:
nothing there is a commit. And `run_identity_fields` names `producing_commit.commit` as one of the
four fields that ARE this run's identity, so a census asking which code produced these figures is
told `p6-arm-cull` and has no way to know that is not an answer.

**The sha is not recoverable.** Not from the artefact, not from the run output, and not from
`git log`: four lanes were landing into this tree through the night of 2026-09-11, so the commit at
`00:33:46Z` is not attributable to that process. Picking the nearest commit by timestamp would be a
number chosen because a number was needed, which is the failure the knowledge-first rule names.

## What was done about it here, and what was not

**Done.** `docs/design/blind_envelope_arms_2026-09-11.json` now carries, per arm,
`commit: null` + `launch_label` + `resolved_at` + an `unavailable_because` that names the mechanism,
plus a top-level `artefact_filed_in_commit` (`101244b404633e2ab0be3b9b80a576f3d9ac2342`, a fact from
git) and a `provenance_note` saying what is and is not established. The labels are kept — they are
the only handle the runs left — but under a key that cannot be read as a commit.

**Not done, deliberately.** The producer is unchanged. Tightening `resolvable` to require a hex sha
is two lines, but it changes the header every run in this tree writes, and it would flip
`producing_commit.commit` to `null` on any live launcher that passes a label — which may be several,
and which I cannot enumerate inside this turn without running the full suite. That is a change worth
making and worth making with the suite green around it, not a rider on a different piece of work.

## What would refute this finding

A launcher-side rule showing `code_commit` is only ever passed a sha, making the artefacts above the
product of one retired caller rather than a live fail-open. Four artefacts from one night is an
instance; the guard's own docstring, which reasons about placeholders and then admits exactly one,
is the class.

## What is next

Tighten `resolvable` in `_run_identity_header` to a hex-sha shape, with the label preserved in a
`launch_label` field rather than discarded, and a control that a non-sha `code_commit` produces
`commit: None` and an `unavailable_because` naming the label. The re-run of the five blind-envelope
arms is the natural occasion: those runs need real stamps, and this is what stops them being labels
again.
