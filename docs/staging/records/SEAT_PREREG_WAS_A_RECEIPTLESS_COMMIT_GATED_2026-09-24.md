# Pre-registration: was a receiptless commit actually ungated?

Filed 2026-09-24, BEFORE the trace measurement below was run. Claim id
`establish-whether-a-receiptless-commit-was-actually-ungated`.

## The question, stated so it can be answered wrong

`promote_worktree_landing` refused a seat landing with *"13203ed91 carries no verifying
surgical_land receipt, **so it was not gated**"*. Two readings:

* **R-BYPASS** — the commit really did skip the hook chain (`--no-verify`, a hand-built
  `commit-tree`, or a producer that unsets `core.hooksPath`). Remedy: tighten the daemon.
* **R-RECEIPTLESS** — the commit ran `tools/git-hooks/pre-commit` in full and simply left no
  receipt, because `RECEIPT_HEADER` is written only by `tools/surgical_land.py`. Remedy: relax the
  door — or rather, make it ask the question it means.

The two imply opposite remedies, so the reading must be measured, not chosen.

## What is ALREADY established by reading, before any trace is consulted

Not a prediction — record of what was read, so that the prediction below is honest about what it
was standing on:

* `13203ed91` is produced by `background/delivery_seat.py:1754` —
  `["git", "commit", "-m", "delivery seat: direction for the next stretch", "--", *present]`.
  No `--no-verify`, no env override.
* `61b67fa0d` is produced by `background/process_run_complete.py:8494`, inside
  `_commit_and_push_paths` — `["git", "commit", "-m", msg, "--"] + paths`, with
  `env=_commit_hook_env()`, which sets `PYTHONUNBUFFERED` **and nothing else**.
* `core.hooksPath` on the shared tree is `/home/rich/synthetic-enterprise/tools/git-hooks` — an
  absolute path in the shared `.git/config`, so linked worktrees inherit it.
* `tools/git-hooks/pre-commit` has no pathspec exemption: `stale_copy_refusal`,
  `pre_commit_test_gate`, `level_promotion_gate`, `site_lane_gate`,
  `startup_anchor_freshness` all run unconditionally on the way to every commit.

## The prediction

Three things are predicted here whose answers I do not have yet. Each can refute
**R-RECEIPTLESS**.

**P1.** There is an independent trace, written by the hook chain rather than by the producer, of a
gate run in the shared tree at or just before **18:26:12 +0100** (`13203ed91`) and at or just
before **18:45:26 +0100** (`61b67fa0d`). *Predicted: present for at least one of the two.*

**P2.** `_record_commit_hook_pass(git_hash)` — called at `process_run_complete.py:8528`,
immediately after the heartbeat's `git commit` returns 0, with the comment *"The liveness commit
runs the SAME hook chain"* — has a ledger row stamped with `git_hash=13203ed91…` around 18:45.
*Predicted: present.* If the ledger is empty or names a different hash, P2 is refuted and the code
comment is a claim nobody checks.

**P3.** No producer in `background/` or `tools/` that can write to `main` uses `--no-verify` or an
unset `core.hooksPath`. The one known `--no-verify` (`background/fork_salvage.py:164`) is scoped
to a fork's own branch. *Predicted: holds; if a second one exists, R-BYPASS is live for some
OTHER commit even if not for these two.*

## ADDENDUM, filed mid-turn: a sharper instrument, and its prediction, written before it returned

P1 turned out to have a better form than "is there a trace". `docs/observability/sim-runner-log.md`
gives a **duration bound** for the heartbeat commit:

* `17:45 UTC` — *"…so this commit cannot conflict with the fork it would widen… **Publishing.**"*,
  logged inside `_commit_and_push_paths` **before** its `git add` and `git commit`.
* `17:45:26 UTC` — the commit object `61b67fa0d` is stamped. `git` writes that stamp **after** the
  pre-commit chain returns.

So the whole chain for that commit completed in **≤26 seconds**. That is a number the two readings
disagree about, which is what makes it worth running.

**P4 (the discriminating test).** Stage `61b67fa0d`'s exact pathspec —
`site/data/tick_heartbeat.json` + `docs/observability/agent_status.json` — in this isolated
worktree and time each link of `tools/git-hooks/pre-commit` by hand.

* If the chain runs in **≲26s**, the ≤26s window is consistent with the hook having run, and
  **R-RECEIPTLESS** stands for this commit.
* If the chain takes **minutes**, the hook chain CANNOT have run inside that window, **R-BYPASS**
  is live, and by a mechanism nobody has named — neither `--no-verify` nor `commit-tree`, since
  the producer uses neither.

*Predicted: ≲26s.* Stated before the probe returned. The reasoning it rests on, which is exactly
the thing that could be wrong: both staged paths are JSON data, `pre_commit_test_gate`'s
changed-file→test map has no entry for a `.json`, and `site_lane_gate`'s own docstring claims
`pytest site/` is *"fast (~6s, ~164 tests)"* — a figure written in July that the probe re-measures
rather than trusts.

**This prediction can be wrong in a way that matters.** If it is, the finding inverts: the remedy
becomes tightening a daemon rather than correcting a message, and the document must say so.

## What the answer changes, decided before it is known

* If **R-RECEIPTLESS** holds: the refusal message is wrong in the strongest place it could be —
  it states a conclusion (`so it was not gated`) that its evidence (`no receipt`) does not reach.
  The remedy is to make the message say what it observes, and to give the door a second question
  it can ask: *was this commit's tree gated by the hook?* That question needs a trace to key on,
  which is what P1/P2 are really measuring the existence of.
* If **R-BYPASS** holds: the daemon is the subject and the door is right.
* **If no trace exists either way** — that is itself the finding, and the honest verdict is
  *cannot tell from the record*, which is NOT the same as R-RECEIPTLESS being true. Recorded here
  in advance so that a null result cannot be read as a confirmation.
