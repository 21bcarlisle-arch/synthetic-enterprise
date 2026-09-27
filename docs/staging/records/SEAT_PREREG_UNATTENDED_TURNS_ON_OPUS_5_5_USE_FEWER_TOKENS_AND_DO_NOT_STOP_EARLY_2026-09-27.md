**Severity:** RECORD · **Lane:** H_harness · the model under every unattended turn

# Pre-registration: unattended turns on Opus 5.5 use fewer tokens and do not stop early

**Filed 2026-09-27 with the switch, before any 5.5 unattended turn has run.**

Every unattended seat now reads `model_tier.OPUS = claude-opus-5-5`, where seven modules each pinned
`claude-opus-5` before. The two headless executors, `seat_executor` and `worker_tick`, carry
Anthropic's documented instruction against Opus 5.5 ending a headless turn with a text-only report.
The attended `worker_seat` does not, because a person answers it.

**How it is measured.** No code is added. Claude Code's own session transcripts
(`~/.claude/projects/*/<session>.jsonl`) record the model and `usage` for every assistant message.
The comparison is the last 10 seat-executor turns on Opus 5 against the first 5 or more on Opus 5.5:
total tokens per turn (input + output + cache writes; cache reads reported separately), and whether
each turn ended having landed something or with a text-only stop while work was still owed.
`token-usage-log.jsonl` cannot be used: it has had no row since 2026-06-25.

**Predictions:**
- **P1** tokens per turn fall by ≥ 15% (Anthropic: 5.5 at default `medium` matches 5 at `high` in fewer tokens).
- **P2** at most 1 of the first 5 turns on 5.5 ends with a text-only stop while its work is still owed.
- **P3** the landing rate does not fall below the Opus 5 baseline's.

**Revert if P3 fails:** set `model_tier.OPUS` and `worker_tick.MODEL` back to `claude-opus-5`, a
two-line change. `SE_EXECUTOR_MODEL` also overrides the executor on its own without a commit.
