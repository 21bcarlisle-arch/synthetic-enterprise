# PRE-REGISTRATION — can the advance be judged by origin's rulebook instead of the checkout's?

**Filed** 2026-09-24, BEFORE the measurement. **Severity: MEDIUM** — a mechanism-feasibility
question, not a claim about the world. Written because the answer is not known and a prediction
filed after the answer is not a prediction.

## The established finding this stands on

`SEAT_FINDING_THE_CHECKOUT_ADVANCE_IS_JUDGED_BY_THE_CHECKOUTS_OWN_CODE...` (c72c41e4c, addendum
398040a36) measured a two-arm differential on one path, one working copy, one project, varying ONLY
which `tools/stale_copy_refusal.py` was on `sys.path`: the checkout's copy said *no complaint,
refreshing it would discard an ordinary edit* and origin's said *origin/main strictly supersedes it
[reverts_a_landed_comment_block]*. Opposite remedies from the same bytes.

`deploy_restart.stale_judges` is the landed DETECTOR for that state. It reports; nothing acts on it.

**Re-measured on the live shared tree at 2026-09-24 (this turn, before any build):** HEAD
`61b67fa0d`, **32 behind / 3 ahead** of `origin/main`, and `git diff --name-only HEAD origin/main`
names BOTH `tools/refresh_to_head.py` and `tools/stale_copy_refusal.py`. The defect is live, not
historical.

## What is being measured

Whether `origin/main`'s judge modules can be EXECUTED against the shared tree's real working copies
without the checkout's own copies being on `sys.path` — i.e. whether the remedy is buildable at all.

The route under test: reuse `tools.epistemic_wall.head_export(repo_root, dirs, rev)`, which already
does `git archive <rev> -- <dirs>` into a tmpdir with three fail-closed guards and already takes
`rev` as a parameter; point it at `rev="origin/main"` and `dirs=("tools", "background")`; then run
`judge_copy` in a SUBPROCESS with `PYTHONPATH=<export>` and `cwd=<project>`. A subprocess and not an
in-process import, because `tools.refresh_to_head` and `tools.stale_copy_refusal` are already in
`sys.modules` in every caller and a second copy under the same name cannot be loaded beside them.

## Predictions, written before running anything

**P1 — the first export will NOT import cleanly (60%).** `tools/stale_copy_refusal.py` imports
`background.tree_divergence` and `tools.symbol_landing_check`, both inside the two exported dirs, so
the named imports resolve. I predict a TRANSITIVE import outside `("tools", "background")` — or a
module-level constant derived from `__file__` that walks out of the export — breaks it anyway.
*Refuted if the two-dir export imports and returns a verdict on the first attempt.*

**P2 — on a tree LEVEL with origin, the exported rulebook and the local rulebook return the SAME
verdict for every path (85%).** This is the null arm, and it is the control that makes P3 mean
anything: a mechanism that returns a different answer for a reason unrelated to staleness is not
measuring staleness. *Refuted if verdicts differ where no judge module is in the gap.*

**P3 — on the live shared tree, which IS 32 behind with both judges in the gap, at least one
blocking path grades differently under the two rulebooks (70%).** This is the finding's own
differential, re-run through the new seam rather than through a hand-built `sys.path` injection.
*Refuted if every blocking path agrees across both arms.*

## What I am NOT predicting

Whether the remedy makes the live tree advance. It cannot: the shared tree is **3 ahead**, and
`advance_shared_tree` refuses on DIVERGENCE before it grades a single path. That is a separate wedge
with a separate cause, and attributing any advance to this change would be the multi-variable
attribution error. Done here means *the judgement is origin's*, not *the tree moved*.

## What done means for the work this precedes

1. The stale-copy leg of `advance_shared_tree` — judgement AND refresh, because the refresh re-runs
   its own judgement and a judgement-only change is inert — consults origin's rulebook when any
   `ADVANCE_JUDGE_MODULES` entry is in the gap.
2. It FAILS CLOSED by name: an export that will not build, or a subprocess that will not answer, is
   a refusal for every path with the reason attached, never an empty verdict set. `{}` here means
   "nothing is refreshable", which is what a caller acts on.
3. A control that can fail: the seam is keyed to the PROPERTY (which rulebook answered), not to
   today's verdict text.
