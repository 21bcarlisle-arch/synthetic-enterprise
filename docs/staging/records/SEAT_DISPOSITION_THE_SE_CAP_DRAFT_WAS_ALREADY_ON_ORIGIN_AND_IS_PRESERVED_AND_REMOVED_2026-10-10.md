# Disposition: the `/var/tmp/se-cap` draft was already on origin; preserved and removed

*Delivery item `the-week-old-se-cap-draft-is-dispositioned`, 2026-10-10.*

**What it was.** A locked worktree at `10cffe38d` (2026-10-03), owned by worker session pid 2197437,
with 16 modified and 4 untracked paths: the "a stayer pays at most the default" change to the
renewal-rate chain, value renewal, decision policy, `run_phase2b`, `tools/decision_probe.py`, their
tests, three pre-registration/result records, and regenerated observability ledgers.

**Not being edited.** The newest content write was 2026-10-03 19:42 BST, seven days before this
disposition. Only `.se_worktree_owner` had been touched today, a lease renewal with no content.

**Origin had superseded it.** Every line the draft added to a code, test or record path exists on
origin/main, with two exceptions. Both are in `tools/decision_probe.py`, the `RULES` tuple and the
rate dict, and in each case origin's version is the same line extended with a `value_capped_learned`
rule. The draft landed as `3475058ef` ("A stayer pays at most the default…"), was extended by
`c822e470e` and `191448824`, and its stayer test is on origin. Origin's copy of the stayer
pre-registration also holds a v2 grading section that the draft lacks. The observability ledgers
(`coupled_gap_ledger.json`, `fidelity_evidence_ledger.json`, `test_execution_log.jsonl`,
`token-log.md`, the handshake, and the two untracked `book_*` JSONs) are run outputs and nobody
needs to land them.

**Disposition.** The whole working state, untracked files included and the owner marker excluded,
was snapshotted on top of its base as **`refs/preserved/se-cap-2026-10-03`** (20 files). The worktree
was then unlocked and removed. Nothing was landed, because there was nothing novel to land.

**To reverse:** `git worktree add /var/tmp/se-cap refs/preserved/se-cap-2026-10-03`, then
`git reset --soft HEAD~1` to bring the draft back as uncommitted edits on `10cffe38d`.
