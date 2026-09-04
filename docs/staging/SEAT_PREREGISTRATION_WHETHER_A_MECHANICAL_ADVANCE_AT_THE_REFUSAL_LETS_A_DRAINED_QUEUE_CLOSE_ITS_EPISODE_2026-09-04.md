**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# PRE-REGISTRATION: whether a mechanical advance at the refusal lets a drained queue close its episode

**Written 2026-09-04, delivery seat, BEFORE the change is landed and before any cycle has run under
it.** Filed because the answer is not known and a prediction written afterwards is not a prediction.

---

## The state being predicted from

Measured on the shared tree at 2026-09-04, immediately before landing:

```
docs/observability/.publish_gate_state.json
  {"episode_clean_publishes": 0, "episode_failures": 0, "last_clean_publish": null, ...}

docs/observability/.last_publish_cause.json
  {"cause": "behind_origin", "git_hash": "54dfe05b4",
   "evidence": "origin/main is 3 commit(s) AHEAD of HEAD ..."}

git rev-list --count HEAD..origin/main   = 1
git rev-list --count origin/main..HEAD   = 0
origin_reconcile.gate_is_running()       = True
paths_blocking_fast_forward()            = 1 path, untracked here, origin adds its own copy
```

`last_clean_publish` is `null` against a queue that reaches zero. The drain is true and
unrecordable: `record_publish_gate_success` is only reached by a publish that commits.

## The change

`background/process_run_complete.git_commit_push` now calls `_advance_to_origin_or_say_why()` when
`_divergence_refusal()` fires, and RE-READS the refusal afterwards. The advance fast-forwards the
shared tree onto `origin/main` when — and only when — this machine holds no commits of its own and
git raises no collision. It never commits, never forces, and holds `tree_lock` across the move.

## What I predict, and what would refute it

**P1 — the advance fires and clears the refusal at least once within 6 hours of landing.**
Evidence: a `Fork closed by fast-forward` line in `docs/observability/sim-runner-log.md`.
*Refuted by*: no such line, or every occurrence followed by a `Publish commit REFUSED` on the
re-read. I put P1 at likely: `ahead == 0` held at four of the four moments I sampled today, and the
one blocking path was an untracked lossless twin — which is the OTHER lane's repair, not mine, and
if theirs has not landed the ff still refuses and P1 fails on a cause I did not fix. **That is the
most likely way this is refuted and I am saying so in advance.**

**P2 — `last_clean_publish` becomes non-null within 6 hours.** *Refuted by*: it stays `null`. P2 is
strictly weaker than P1 and can fail with P1 true, because the commit's own hook chain (~660s) is a
second race window this change does NOT close: origin can move again between the advance and the
push. If P1 holds and P2 fails, the residue is the push-side race, and the next increment is
`surgical_land`'s bounded re-gate at the push — not more work at the refusal.

**P3 — the fork does NOT get wider.** `origin/main..HEAD` stays at 0 or 1 across the window, never
climbing. *Refuted by*: a rising count, which would mean this path is creating unpushable commits —
exactly the defect `_divergence_refusal` was built to stop, reintroduced by its own repair. This is
the failure I would most regret and the cheapest to check. **If P3 is refuted, revert first and
diagnose second**: `git revert` of the landing commit restores the pure refusal.

## What I am NOT predicting

That the site becomes fresh. Publishing has more than one way to fail and three of them were fixed
today; a stale page after this lands is not evidence about this change until the cause is read off
`.last_publish_cause.json`.

## How it gets checked

Any seat reading this after 2026-09-04 22:00Z: read the three artefacts named above, write the
answer beside each prediction in this file, and file the correction next to the claim rather than
revising it. A refuted prediction kept is worth more than a quiet edit.
