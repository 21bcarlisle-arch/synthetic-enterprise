**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# PRE-REGISTRATION: what the live hook chain is missing, before I look
**Written:** 2026-09-25, before running the comparison.
**Claim:** `core-hookspath-points-at-a-working-copy-so-every-gate-can-be-silently-stale`

## The premise, re-measured (NOT spent)

`934343669` is an ancestor of `origin/main`: yes. `4157c8d6b` — the prior invocation's work on this
very claim — is also an ancestor, and it is **a findings document and nothing else** (102 lines,
one file, `docs/staging/`). The claim id was already held in
`docs/observability/.seat_work_in_hand.json` with `"paths": []` — held by that same invocation,
which landed the diagnosis and never built the control. So the duplicate-claim note names my own
predecessor, not a rival, and the WORK the item asks for — "the one-leg control that compares the
live hook files against the index/origin and says so, loudly" — exists in no copy of the tree.
Carrying on rather than releasing.

## What is already measured and is not a prediction

* `core.hooksPath` = `/home/rich/synthetic-enterprise/tools/git-hooks` — the shared tree's
  **working copy**, and it resolves to that same absolute path from inside a linked worktree, so
  every lane's commit runs the shared checkout's hooks regardless of where it commits from.
* That checkout is **7 ahead, 49 behind** `origin/main` (was 48 at the item's writing).
* `grep -c hook_gate_mark` on the live `pre-commit` is **0**; `tools/hook_gate_mark.py` is not on
  disk there.

## The predictions

1. **The live chain is missing exactly ONE invocation the trunk declares, and it is
   `hook_gate_mark --record`.** Basis: `python3 -m` grep gives 12 live vs 13 trunk, differing only
   at that line. This prediction is weak where it matters — I have NOT yet compared the
   script-form (`python3 tools/X.py`) lines, which is most of the chain. If the answer is >1,
   the item's framing ("this is wider than the mark") is confirmed on real bytes rather than by
   argument.
2. **No invocation runs live that the trunk has retired** (the mirror direction is clean).
3. **`tests/tools/test_time_the_commit_hook_chain.py::test_every_step_the_hook_runs_is_timed` is
   RED at HEAD in this worktree**, because `STEPS` has 21 entries and does not list
   `hook_gate_mark`, which `934343669` added to the trunk hook. If it is GREEN, my reading of that
   control is wrong and I must find out why before building on it.

## Why the obvious wiring is the fail-open this repo already has a name for

The natural home for the control is a new line in `tools/git-hooks/pre-commit`. That line is read
from the same stale working copy it exists to grade, so it would be **inert in exactly the outage
it is for** — `a_liveness_signal_delivered_through_the_channel_it_monitors`. The escape has to be a
channel read from the COMMITTING tree rather than from the hooks dir. Two exist: the gate modules
the stale chain invokes by path (`python3 tools/pre_commit_test_gate.py` resolves against the
commit's cwd, not against `core.hooksPath`), and `tools/surgical_land.py`, the sanctioned door
every lane is told to use. Wiring, and its honest labelling, is the design decision this turn owns.
