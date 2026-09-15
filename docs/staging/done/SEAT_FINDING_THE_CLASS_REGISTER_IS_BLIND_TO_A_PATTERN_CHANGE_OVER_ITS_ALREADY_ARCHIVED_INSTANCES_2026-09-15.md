**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the blind pattern must co-occur with a control noun)

# `check()` is blind to a pattern change over the 169 instances it has already archived

**2026-09-15, delivery seat.** Found by trying to verify a claim I had just written into a landed
commit, and discovering the claim was false.

## What I claimed, and what is actually true

Landing `7646e25f0` I wrote — in the commit message, in the corrected entanglement finding, and in
the pre-registration — that the refuted control-noun remedy *"would have dropped the only live root
member of the class, so `--check` would have gone red."*

**Both halves are false.**

- `controls_that_cannot_fail` has **0 live root members**. It has **35 archived** instances and
  **1 refused out-of-lane**. The document I meant
  (`SEAT_RESULT_THE_PROMOTE_BY_COPY_CLASS_…_THE_CENSUS_IS_BLIND_TO_THE_HALF…_2026-09-09`) is LATENT
  but lane `A_strategy_governance`, so the lane guard refuses it consolidation. It is not a member.
- `--check` is **PASS under both patterns**. Measured, not reasoned:

  | | live members | archived | refused out-of-lane | `check()` |
  |---|---|---|---|---|
  | shipped (predicative) | 0 | 35 | 1 | PASS |
  | refuted (control-noun) | 0 | 35 | 0 | PASS |

So `--check` could not have caught the bad narrowing **at all**, and the green I reported as
evidence of safety in prediction P5 was evidence of nothing.

## The defect that sits under my error

`derive_memberships()` re-derives membership by classifying every file — but only over
`classifiable_documents()`, which globs the **staging root**. Archived membership comes from
somewhere else entirely:

```python
def archived_instances(root, finding_class):
    listed = _INSTANCE_LINE_RE.findall(doc.read_text(...))   # names read OUT OF the class document
    return sorted(name for name in listed if (archive / name).exists())
```

It reads the names the class document already lists and checks **only that the file still exists in
`done/`**. It never asks whether those documents still classify into the class that names them.

That matters because the module docstring makes the opposite promise, in bold, as its own design
rationale:

> *"WHY MEMBERSHIP IS DERIVED, never a hand-kept list (exit criterion 3): a list written once stops
> being true the moment a sixteenth sibling is filed, and stops SILENTLY … `check()` re-derives
> membership from the filesystem every time it runs."*

That is true for the **live root** and false for everything else. Across all six classes the live
root currently holds **0** members and the archive holds **169**. So the derived path the docstring
describes governs nothing at all today, and the hand-kept list it refuses governs **every
consolidated instance there is** — which is exactly the population the silence it names applies to.

*(I first wrote "4 live members" here. That was a second unchecked number in the same document as
the correction of the first one; the measured figure is 0. Left visible rather than quietly
replaced — the habit of stating a count I had not run is the thing this finding is about.)*

## Evidence — it is not hypothetical, and one instance is already stranded

Re-classifying every archived instance from its own bytes against the live pattern set:

| class | archived | stranded (listed, no longer classifies) |
|---|---|---|
| `publish_gate_and_wedge` | 76 | 0 |
| `controls_that_cannot_fail` | 35 | 0 |
| `measurements_that_mirror` | 8 | 0 |
| `uncommitted_and_orphaned_work` | 33 | 0 |
| `no_caller_and_never_runs` | 14 | **1** |
| `figures_on_a_superseded_clock` | 3 | 0 |

The stranded one is `WORKER_FINDING_THE_BILL_SHOCK_CHURN_CAP_CANNOT_BE_REACHED_BY_ANY_CALLER_2026-08-…`.
Its title states its class in plain English — *cannot be reached by any caller* — and the class's
patterns are `no[_ ]caller|never[_ ]called|never[_ ]runs?|never[_ ]ran` and `unreachable`. None of
them matches the sentence. It is counted as an instance of a class the classifier cannot put it in,
and nothing has ever said so.

**Had the refuted control-noun remedy shipped, that number would have gone from 1 to 8** — seven
more archived instances silently counted under a class they no longer belong to — and every gate in
this repository would have stayed green.

## What I did about it in the same commit as this finding

A control keyed to the property, not to today's answer: **every archived instance a class document
lists must still classify into that class.** It asserts `stranded ⊆ KNOWN_STRANDED`, so it fails
closed on any NEW stranding and stays green when someone repairs the known one — rather than the
set-equality form, which would go red precisely when the tree became more honest.

Mutation-proven against the refuted remedy itself: substitute the control-noun pattern and the leg
goes red naming seven instances, which is the red that was missing when I landed `7646e25f0`.

## What is still owed, and is NOT fixed here

1. **The one live stranded instance.** Either the `no_caller_and_never_runs` pattern set learns
   *cannot be reached by any caller*, or that instance does not belong in the class. Widening the
   pattern is the likely answer, but it is a pattern change over a 14-instance class and deserves
   the same corpus scoring the `blind` change just got — **not** a guess, which is the mistake this
   whole cluster keeps producing.
2. **The docstring's promise.** It still claims membership is derived and never hand-kept. It should
   say which half of the population that covers. Left undone deliberately: correcting it without
   fixing (1) would put an accurate sentence next to a live exception.

## The general lesson, which is the reason this is filed rather than just fixed

**A green from a control is only evidence about the population that control actually reads.** I
quoted `--check` PASS as proof the narrowing was safe. It was PASS because the 16 documents the bad
rule would have damaged are all in `done/`, and `check()` does not look there for class membership —
so the same PASS would have appeared for a rule that broke the class outright.

This is the `controls_that_cannot_fail` shape applied to the register of
`controls_that_cannot_fail`, and it was found only because a claim I had already landed turned out
to be checkable and wrong.
