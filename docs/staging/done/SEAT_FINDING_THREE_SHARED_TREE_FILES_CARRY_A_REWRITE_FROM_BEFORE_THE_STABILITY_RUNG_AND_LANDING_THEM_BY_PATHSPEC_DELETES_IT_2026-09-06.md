**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# Three shared-tree files carry a rewrite from before the stability rung, and landing them by pathspec deletes it

**Found:** 2026-09-06, delivery seat, while landing the R1 household-key correction. Not my work and
not landed by me — filed because nothing else in the architecture can see it, and the lane holding
it will not find out until after it lands.

---

## The state

`613f9bd17` landed the stability rung — `verdict_across_runs`, its `_reduce_runs` reducer, the
`_redraw_panel` generator block and the `/harness/` markup that renders it. It is at HEAD.

The shared working tree's copies of those same three files do not have it:

| path | at HEAD | in the working tree |
|---|---|---|
| `tools/r1_inference_ceiling.py` | `recent_run_outputs`, `verdict_across_runs`, `_reduce_runs` | absent |
| `tools/generate_delivery_page.py` | `_redraw_panel` | absent |
| `site/harness/index.html` | the redraw block (`coverage_regimes`, the UNKNOWN branch) | absent |

In exchange the working tree carries a magnitude/honest-point-estimate lane that has **never been
committed** — `git log -S "def honest_point_estimate"` on that path returns nothing. So the two
copies have each lost the other's work, in both directions, and the working tree's side is the
uncommitted one.

## Why it is a hazard and not just an in-flight edit

A pathspec stages the **working-tree copy**. Whoever holds the magnitude work will land these three
paths and the diff will read as their own additive change — nothing in `git status`, in the gate, or
in a path-filtered `git log --stat` says that the same commit removes three functions and a rendered
panel that A49's reader depends on. The redraw panel is the answer to "would this be the same number
tomorrow", which is the question A49 gates R3 and R4 on. It would go back to the state
`613f9bd17` was written to fix, silently, with a green gate.

This is the class already in the record — a whole-file rewrite deleting a mechanism the path-scoped
gate never selects tests for — reached this time through a base that predates the mechanism rather
than through a merge.

## What I did about it

Nothing to their work: it is in flight and it is theirs. My own correction to the same instrument was
landed as HEAD-plus-my-hunks via `surgical_land --content`, built outside the repo, so the landing
carries `verdict_across_runs` and the redraw panel intact and adds no third divergent copy. That is
the containment, not the repair.

## What is owed

The two lanes have to be reconciled into one file — magnitude **and** stability, not either. It is a
merge of two additive features and there is no conflict of intent between them, only of bytes. The
lane holding the magnitude work should rebase it onto HEAD rather than land its copy.

**Falsifier, and it is cheap:** after the magnitude work lands, `git show HEAD:tools/r1_inference_ceiling.py
| grep -c "def verdict_across_runs"` must be 1. Zero means this finding was right and unheeded.
