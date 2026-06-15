# NTFY responsiveness & parallelism — what's shipped, what's proposed

## Context

Rich's ask: "I tap send on ntfy, something intelligent responds and acts,
always, regardless of what else is running." Also: GPU re-runs shouldn't
block reasoning/orchestration, and token budget is under-used while waiting
on long local-LLM-bound simulation runs.

## Shipped now (live, reversible)

**`background/ntfy_responder.py`** — new tmux session `ntfy-responder`
(added to `background/start_worker.sh`). Polls the `skynet-synthetic` NTFY
topic on its own watermark (`background/.ntfy_responder_since.json`,
independent of `session_watchdog.py`'s), and for every inbound message not
sent by us, immediately replies (via `send_ntfy`, so the existing
`was_sent_by_us` dedup — fixed earlier this session — covers it too) with a
templated status snapshot:

- Latest background simulation run's progress line (settlement date,
  treasury, risk-committee wake-up count) from whichever `docs/observability/
  *_run.log` was most recently touched (ignored if stale >1h)
- GPU utilisation / VRAM via `nvidia-smi`
- Current git HEAD

No LLM call — pure templating, so it never competes with the simulation for
GPU and replies within ~20s (its poll interval) regardless of what the main
`claude` session is doing. It does not interpret or action messages —
`session_watchdog.py` still relays into the `claude` session exactly as
before, and the Staging Directory Protocol still governs substantial
instructions. 7 new tests in `tests/background/test_ntfy_responder.py`.

This directly addresses "always get *a* response" for the common case (quick
status checks, "how's it going") without any architectural risk — it's an
additive, independently-killable tmux session.

## Proposed next (not built — needs Rich's steer on cost/scope)

The harder part of the ask — "work should proceed in parallel across
simulation, business layer, and anything else unblocked" — has a real option
and a real cost tradeoff:

**Option A — lean on the existing single session more aggressively.**
Within one `claude` session, GPU-bound sim runs already execute as detached
background processes (as with this session's Phase 6c re-run) — the agent
*can* keep doing repo work (lint fixes, backlog items, docs) while a sim
runs, using `ScheduleWakeup`/Monitor to check back. This session did exactly
that for the loopback-bug fix and the report cache-staleness fix while
waiting. The gap isn't capability, it's that the agent sometimes defaults to
"wait and check back" instead of "queue another unit of work" — a behaviour/
prompting fix (e.g. CLAUDE.md note: "while any `*_run.log` is fresh, always
have a non-GPU backlog item in flight"), zero infra cost.

**Option B — a second Claude Code instance for "business layer" work.**
A second tmux session (`claude-business`) running its own Claude Code CLI
instance, fed from a separate staging subdirectory (e.g.
`docs/staging/business/`) and its own NTFY topic or message-prefix
convention to avoid both instances replying to the same message. This gives
genuine two-track parallelism (simulation/orchestration track vs.
reporting/backlog/business-layer track). **Cost**: a second instance consumes
a second usage-window's budget concurrently — roughly doubling frontier token
burn rate during overlap. Given "massively underusing budget" was the
complaint, this may be exactly the right trade — but it's a standing-cost
decision, not a one-off, so flagged rather than built silently.

**Option C — local-Qwen "specialist agents" via `background_worker.py`.**
The existing `background_worker.py`/`run_queued_tasks.py` infra already
delegates mechanical work to local Qwen during off-peak hours. Could extend
its task queue to accept business-layer tasks (e.g. "regenerate report",
"groom REPORTING_BACKLOG") queued by the main session or by
`ntfy_responder.py` itself, executed by Qwen without frontier tokens at all.
Zero marginal frontier cost; bounded by Qwen's capability for the task (per
CLAUDE.md, Qwen handles "code generation, mechanical execution,
self-correction" — design/review stays frontier).

## Recommendation

Ship the responder now (done). For the rest: try Option A first (free,
behavioural) for a session or two; if Rich still finds responsiveness
lacking, Option C (extend the existing queue, no new frontier cost) is the
next-cheapest; Option B (second Claude Code instance) only if the doubled
budget burn is explicitly wanted.
