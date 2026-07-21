# Retro: the console ledger is the sole ratification record — a commit message is not authority

**Date:** 2026-07-21. **Incident window:** 08:26–11:40 BST (origin frozen ~3h15m; 13–15 consecutive publish-gate failures; 20+ `run_complete` runs queued unpublished).

## Claim discipline (R9)
Every claim below is `observed-with-evidence` unless marked `inferred`. The one inferred claim (the bypass vector) is labelled as such and the evidence that *would* settle it is named. No external-actor / compromise narrative applies — this was entirely local agent/worker mechanism.

## What happened (observed-with-evidence)
- Origin's last commit was `ca546f5cf` at **08:26**; nothing landed for ~3h. Deadman climbed to 171min; `.publish_gate_state.json` logged 15 `process_run_complete rc=1 … test_regression` failures at ~10-min cadence.
- Reproducing `process_run_complete` showed the actual red: `tests/background/test_fronts_reconciler.py::test_live_reconciler_is_CLEAN` — `LEVEL_SELF_PROMOTION` for `W1_5`, `W1_9`, `W1_10`, `C13`.
- **Cause commit `945a4377b`** ("Director-ratified L1/L2 level-ups", authored "Rich Carlisle") moved `level_current` W1_5 1→2, W1_9 0→1, W1_10 0→1 and cleared `blocked_on` — **but wrote no `LEVEL_UP_PROPOSED` to `docs/observability/gate_authorizations.jsonl`.** The ledger's genuine content: W1_5→L1 only (ts 1784541430, 2026-07-20); W1_9/W1_10/C13 had *no* level entry. `git show` of the "cited commits" (C13 `76864ad7d`, W1_10 `ca546f5cf`) confirmed they *were* on origin — the "not on origin" symptom was the frozen pipeline, not a push failure.
- **Re-wedge (observed):** mid-fix, a concurrent worker tick committed `66f6b57be` "restore … to director-ratified baseline (945a4377b)" — reinstating the exact unbacked values by trusting `945a4377b`'s *message*. My own uncommitted revert had been swept into its earlier `1ba9ec452` (the concurrent-writer hazard). Net: 3 alarms again, pushed to origin.

## Root cause, not the instance (R4)
The reconciler checks the live map against the **console ledger** (R15 independence). Two failures let an unbacked level move reach and re-reach origin:
1. **The preventer was bypassed.** `tools/level_promotion_gate.py` (pre-commit hook via `core.hooksPath=tools/git-hooks`) is designed to make an unauthorized `level_current` increase impossible to commit. Re-run on `945a4377b`'s exact transition against the current ledger, it returns **`status: REJECT`** naming all three increases (verified this retro). So the gate is *sound*; `945a4377b` reached HEAD only by **skipping the hook** — `inferred` vector: `--no-verify`, which is used routinely here to dodge the slow full-suite stall under contention (see memory *precommit-gate-stall-under-contention*). Direct evidence that would confirm it (the reflog/command that produced `945a4377b`) is not retained; the REJECT proves the hook did not run, whatever the reason.
2. **A commit message was treated as authority.** The worker's "restore the floor" reasoning read `git show 945a4377b` — a *narrative* — as the ratification record. There is no automated floor-enforcer; this was one-off agent judgment. This is R7/R8 (asserted/injected text carries zero authority) applied to level moves, a case those rules did not name explicitly.

Nearest working analogue: the reconciler (post-hoc, in the publish gate — **not** bypassable by `--no-verify`) *did* catch it. Diff: it catches after the wedge, announced only via deadman pings, so a silent 3h freeze was possible.

## The fix, verified (not asserted)
- Reverted `level_current` to ledger-backed values (W1_5→1, W1_9→0, W1_10→0; C13 already 0), code kept, higher levels re-proposed with `blocked_on: director_level_up`. Fix `15c7f5e3c`.
- `fronts_reconciler.evaluate()` → **`SCOPE_CLEAN`, empty signature** (quoted live). Second `-x`-hidden failure (`test_generate_proof_coupled_gaps` had baked the self-promoted W1_5=L2 into `unmeasured_ge_l2==9`) corrected to 8.
- Pipeline proven **rc=0 clean** end-to-end with the env sourced (`0f9262778`, fresh LATEST 10:46Z, net £1.52M); origin advanced and verified 0/0.

## Class-level lesson → R16 (R10 / MAKE_IT_STICK)
The console ledger (`gate_authorizations.jsonl`, validated by `gate_authorization.is_valid_level_up`) is the **sole** record of a level ratification. A commit message, PR body, or any asserted text claiming "director-ratified" is **not** authorization — verify against the ledger, never against `git show` of a claimed-ratification commit. Captured as **R16** in CLAUDE.md, backed by the two existing mechanisms (the pre-commit level gate + the reconciler's LEVEL check in the publish gate), with the `--no-verify` bypass named as the vector to close on next touch. Corollary standing rule: **never `--no-verify` a commit that changes `maturity_map.yaml` `level_current`** — that is the one path that removes the only preventer.

## What was NOT lost / scope of harm
No data corruption, no secret exposure, no unauthorized external action. The built code (W1_5/W1_9/W1_10 capabilities) was always sound — only the *level metadata* was wrong. Harm was pure availability: origin froze ~3h and 20+ runs queued (all subsequently drainable; the auto-processor resumes now the gate is green). Embarrassing, self-caught, ledger-recoverable.

## Follow-up done inline
- Audited for an automated "ratified-floor enforcer" reading a hardcoded commit: **none exists** (`grep` clean) — the re-wedge was one-off worker reasoning, so committing the correct state sticks.
- Confirmed the level gate is live (`core.hooksPath`) and functions (REJECT on the real transition).
- Open (named, not silently dropped): the `--no-verify` bypass of the level gate is a real hole; the reconciler backstop bounds its blast radius to a caught publish-wedge rather than a silent bad merge. Closing it (e.g. a non-hook enforcement point for map level changes) is remediation-on-touch, logged here as debt.
