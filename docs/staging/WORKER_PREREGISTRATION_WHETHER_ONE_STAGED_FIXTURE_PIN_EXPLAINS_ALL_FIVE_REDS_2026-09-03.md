# [WORKER PRE-REGISTRATION] Does one staged fixture pin explain all five reds, and is HEAD the reason twenty-six runs never saw it?

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — publish-gate wedge, Rung 1
**Filed** 2026-09-03 by the autonomous worker, **while the twenty-seventh gate run is still in
flight and before its outcome is readable**. Subject: the publish-gate wedge episode, 26
consecutive failures since `wedge_since` 1788333200, and the five reds the report-only census
enumerated at `c04dd0af6`.

Related: `docs/staging/reference/HEAD_RED_REGISTER.md`,
`docs/staging/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`,
`docs/staging/WORKER_FINDING_LANDED_IS_NOT_PUSHED_AND_A_STAGED_DOCUMENT_BLOCKED_EVERY_LANDING_2026-09-02.md`,
`docs/staging/SEAT_FINDING_THE_RECONCILER_MANUFACTURED_THE_FORK_IT_EXISTED_TO_CLOSE_2026-09-02.md`.

---

## 1. What is established by reading, and is NOT in question

Plain reads taken before a word below was written, so that nothing here can be mistaken for a
prediction made after its answer was visible.

**The census names five reds and they are all in one file.**
`docs/observability/.last_gate_blocking_tests.json` — `{"census": "complete", "git_hash":
"c04dd0af6", "total_red": 5}` — and every one of the five `node_ids` is a leg of
`tests/background/test_a_staged_document_no_longer_blocks_every_landing.py`. There is no second
file in the set.

**The subject of the gate is HEAD, not the working tree.** The in-flight run's pytest child (PID
1853707) has cwd `/var/tmp/publish-gate-head-7d6otfqf`, and `git -C` that directory reports
`c1e24f4bb` — a detached checkout of the commit, not this tree.

**The repair for all five legs already exists, and has only ever existed in the index.**
`git status --porcelain` on that test file reports `M ` — staged, working tree clean. The staged
diff is +19/-3 and adds exactly one thing to each of the five legs: `ahead_fn=lambda p: 1`. The
module under test is untouched: `background/origin_reconcile.py` and `background/deadmans_switch.py`
are both clean, and `reconcile()` at HEAD already carries `ahead_fn` in its signature (line 260).

**In the working tree, with the staged repair, the file is green:** `python3 -B -m pytest -q` on it
returns `20 passed in 0.09s`.

**`git log --oneline c04dd0af6..c1e24f4bb` touches neither the test file nor the module.** The
eleven commits in that range leave the red set exactly as the census found it.

**Acts already taken this turn, before this file was written**, recorded here so they are not
mistaken for consequences of anything predicted below: the shared tree was 1 commit behind
`origin/main` (`4e8770f70`), the one untracked local file that would have blocked the advance was
verified **byte-identical** to origin's committed blob, and the tree was advanced by pure
`git merge --ff-only`. Divergence is now `0 0`. No tree was created and no gate was run by that act.

---

## 2. The mechanism this predicts from

The test file's own docstring, as staged, states it: on 2026-09-02 a merge stopped being a function
of `behind` alone. `ahead == 0` became a decision — with nothing of ours to contribute the honest
move is to advance, not to commit — and `reconcile` now returns `NOT_ADVANCED` before the worktree
is built. The five legs pinned only `behind_fn`, so `ahead` fell through to the fixture's
`fork_state` pin of `(0, 0)`: **a value that was a neutral default right up until it became a
decision.** Each leg then asserted a merge against a state that forbids one.

So the claim is two-part, and both parts must hold:

1. **One cause, five symptoms.** Not a stack of five defects. The branch was working correctly and
   the fixtures were stale.
2. **The gate could never have seen the fix.** The repair has lived in the index and nowhere else,
   and the gate's subject is HEAD, so all 26 runs measured a tree that has never contained it. The
   wedge is not self-healing and no number of further runs would have cleared it.

---

## 3. Predictions, filed before the in-flight run's outcome is readable

**P1 — the run now in flight fails, and fails identically.** PID 1848691, at `c1e24f4bb`, returns
rc=1 and is recorded as episode failure **#27**, with **exactly those five `node_ids` and no
others**.
*Refuted by:* rc=0; or a red set that is larger, smaller, or contains any test outside
`test_a_staged_document_no_longer_blocks_every_landing.py`.

**P2 — landing the staged repair turns all five green at HEAD.** After the repair reaches HEAD, a
gate run whose subject is the new HEAD reports `total_red: 0` for that file.
*Refuted by:* any of the five still failing once the fix is in the commit, which would mean the
fixture pin was not the cause.

**P3 — the "STACK, not one defect" framing in the doorbell is wrong for this episode.** The
doorbell warns that repairing the named test and re-running hands the next layer to the next tick.
This predicts there is no next layer *in the census set*: the five are one cause and clearing them
clears the enumerated red.
*Refuted by:* a sixth red appearing at the new HEAD that was not in the census. P1's "and no
others" clause is the leg that catches this, and it is why that clause is stated rather than left
implicit.

---

## 4. What is NOT claimed

- **Not claimed: that the whole suite is green.** The census read `complete` at `c04dd0af6`, which
  is eleven commits behind HEAD. A red introduced by any of those eleven commits would be outside
  this prediction, and P1's "no others" clause is what would expose it.
- **Not claimed: that the mutation is re-proven.** The staged docstring states the mutation for
  each leg, but mutation-proving in the shared tree while another lane's gate is in flight
  manufactures a red in that lane's run. It is deliberately not run in this turn, and this is a
  named gap rather than a silent one.
- **Not claimed: that the FF cured the wedge.** It cured `behind_origin` only. If the gate had been
  failing on divergence rather than on tests, P1 would already be refuted by the run's own record —
  and its recorded `kind` is `test_regression`, not `behind_origin`.
