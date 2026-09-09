**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — census-the-promote-by-copy-class) · **Class:** controls_that_cannot_fail

# The promote-by-copy census's only refusal is the comment that RECORDS a promote-by-copy defect

**Found 2026-09-09T14:10Z**, running `tools/promoted_artefact_claim_census --check` as the
pre-publish check before moving `value_cycle_ab_s1_three_arm_20260909c.json` onto the canonical
path. Not looked for. The census (`12db4b9df`, 13:01Z) is **red at HEAD**, and its single STALE row
is a false positive:

```
CLAIMS ABOUT WHICH RUN IS THERE  14   ordering-only 8   STALE 1
  STALE tools/generate_value_arms_data.py:5757 (comment) token='2026-08-31'
        vs docs/observability/value_cycle_ab_s1_three_arm.json
REFUSED: a sentence keyed to which run sits at a promoted path is false as the tree stands.
```

The sentence it refuses is this, in full:

> `# THE DATE IS THE OTHER PANEL'S OWN, NEVER A LITERAL. This sentence read "published beside`
> `# the 2026-08-31 run" until 2026-09-09, which was true for as long as THREE_ARM_PATH`
> `# resolved to that run and became false the moment the 21:01Z re-take was promoted onto`
> `# the canonical name -- the same defect _against_the_panels_figure was written for, one`
> `# key down in the same dict, and it survived that repair because the repair was aimed at`
> `# the figure and not at the date. A promote-by-copy moves no constant, so nothing that`
> `# reads a constant could have caught it.`

Every clause is past tense. It is the **repair note for an instance of exactly the class the census
was built to find**, kept beside the code it repaired, which is this project's own rule for how a
correction is recorded. The census reads `2026-08-31` out of it, finds nothing matching in the
artefact now at `THREE_ARM_PATH`, and refuses.

## Why it fires, checked rather than inferred

The STALE rule, in the census's own docstring, is *"a run-identity literal … where that literal
matches NOTHING in the artefact currently at that path and matches no dated sibling the module also
names"*. There is no tense term in it, and none in the matcher: `_module_strings` goes through
`ast`/`tokenize` and `_RUN_IDENTITY` is a bare date/stamp/digest regex. Comments count on purpose —
that decision is right, and is not what is wrong here.

The escape hatch the docstring describes does not reach it either. `generate_value_arms_data.py`
does name a `20260831` sibling, exactly once (`:4572`) — but of the **noise-floor** stem, not the
three-arm one. So for the target it was judged against, the module names no dated sibling and the
row is stale by the rule as written. **The census is behaving correctly and its rule is wrong**, which
is the third cause of a refusal and the one that is never the flattering reading.

## Why this is LATENT and not RECORDED

Nothing is blocked today: the census is a standalone tool, wired to no gate (`grep` over
`tools/git-hooks/`, `background/` and `tests/` outside its own suite returns nothing). No published
figure is wrong. But the census exists to become the thing that refuses a falsifying promotion, and
**it cannot be adopted while it reds on HEAD for a sentence that is true** — its one true-positive
channel is the same channel, so a lane that starts ignoring the red loses both.

## The trap in the obvious fix, stated because it is the expensive half

The cheapest way to clear this red is to delete or reword the comment at `:5757`. **That would
destroy the record of the defect the census was built to catch** — the only place in the tree that
says a promote-by-copy falsified this particular sentence, why the earlier repair to
`_against_the_panels_figure` did not cover it, and why nothing keyed to a constant could have.
Clearing a control by deleting the evidence it is pointed at is the shape already named in
`feedback: committing the thing a refusal names buries the attribution`.

The second-cheapest fix is a tense narrowing — "ignore literals in past-tense prose" — and that is
the asymmetric-narrowing shape: it is added to kill one false positive, only the false positive
gets a comment, and every historical-looking true positive it then swallows is silent. A repair
note and a stale claim are written in almost the same words, which is precisely why the matcher
cannot tell them apart.

**What is not tried here and is offered as the thread to pull:** the census already has a
three-state vocabulary — STALE refuses, UNANCHORED reports, MIXED is dispositioned by hand. A
repair note is a fourth state and the distinguishing property is not its tense but its
**subject**: it makes a claim about what the SOURCE once said, not about what the ARTEFACT now is.
That is checkable without reading tense, and it is a property rather than today's answer. Whoever
takes it should write the poison round first: a real stale claim worded in the past tense must
still refuse, or the narrowing has bought the fix with a fail-open.

## What is next

Not claimed here. This turn's item is the leg-conditioning publish and the census was a check on
the way to it, not the work. Filed for the lane that owns `12db4b9df` — the finding is a day old at
most and that lane is likely still on it.
