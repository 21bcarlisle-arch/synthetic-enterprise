**PARKED IN PROGRESS (2026-07-11):** items 1(a/b/c), 2, 3, 6 all BUILT this session
(see PRIORITIES.md/CLAUDE.md Current-state). Only item 4 (Routines pilot) remains
genuinely open — blocked on Rich creating the cloud environment in his claude.ai
account and sending back the resulting identifier (real click-path already relayed:
claude.ai/code → cloud icon → Add environment). Moved here (docs/staging/in_progress/,
excluded from supervisor.py's unprocessed-staging scan) rather than left in the
staging root, where a fully-actioned-but-unarchived file re-granted a supervisor
turn every ~2min for hours overnight with nothing new to do (director-caught,
2026-07-11). Move to `done/` once item 4 lands or is otherwise resolved.

---

# HARNESS_BEST_PRACTICE_ADOPTION — borrow from published practice + routines pilot (P2)

**Staged:** 2026-07-10 by advisor, director-decided. **Map cell:** Lane H,
HARDEN stage (dial-1 maintain — this instruction is the sanctioned exception:
a bounded adoption sprint, then H returns to maintenance). **Sequencing:**
must not displace MARGIN_REALISM steps or the sanity-findings triage in the
hot lanes; assessment work is background-eligible; adoption items land as
small scoped commits.

## Context
Advisor research (2026-07-10) found Anthropic's published engineering guidance
on long-running autonomous agents plus community practice. Validation first:
our supervisor (outer loop granting sessions), maturity-map evidence atoms
(default-FAIL contract), and R7/R8 (inter-agent messages as untrusted data)
independently match the published patterns — record that in the casebook.
Below are the candidates we do NOT have. For each: assess fit against this
harness's real constraints (you know them best), adopt / adapt / reject with
one-line reasons, and implement the adoptions. Sources to read first:
- anthropic.com/engineering/effective-harnesses-for-long-running-agents
- anthropic.com/engineering/harness-design-long-running-apps
- github.com/anthropics/cwc-long-running-agents (copyable primitives)
- code.claude.com/docs/en/routines

## Candidates (ranked by advisor's expected value — you may re-rank with reasons)

### 1. Lifecycle hooks as deterministic law enforcement (highest value)
Claude Code exposes hookable lifecycle events (PreToolUse/PostToolUse etc.)
that the model cannot skip. Today our laws live in prompts (forgettable).
Requirement: enforce at hook level at minimum —
(a) point-in-time blindfold: block reads of future-dated market/weather data
    relative to sim decision-time context (kills the hedge-bug class in the
    runtime, complements the planned snapshot object);
(b) sudo ban: block any sudo invocation outright;
(c) pixel rule: block outbound "fixed/live/deployed" claims unless the
    matching evidence artefact exists (wire to the existing pixel-check).
Design the hook set; keep hooks small, logged, and individually removable.

### 2. Fresh-context evaluator subagent at phase close
A separate evaluator with NO Write/Edit tools, fresh context that never saw
the build, grading against the phase's default-FAIL criteria. Sits alongside
(not replacing) the Qwen skeptic: Claude evaluator for judgement-heavy phase
closes and Expert-Hour simulation; Qwen for volume/cheap passes. Study the
cwc repo's evaluator + evidence-reads gate and /goal before building anything
— prefer built-ins over bespoke where they fit.

### 3. Resilience settings (cheap, do first)
fallbackModel chaining (primary overload → ordered fallbacks, auto-retry) —
we ate an API 500 mid-session this week. Also review session-cap +
auto-compaction settings vs our /clear habits, and native parallel subagents
as input to the pending parallel-lanes proposal (prefer first-party over
bespoke lanes where it genuinely fits single-writer discipline).

### 4. Routines pilot (bounded — research preview, no Tier-1 dependence)
Two pilots only: (a) scheduled: the daily Expert-Hour walk as a cloud routine
against the repo (report-only, opens issues/PRs, never pushes main);
(b) GitHub-trigger: on [ADVISOR-STAGED] commits, a cloud desk-work session
for doc-only instructions (charters, gap-checks), proposing via PR — the
local lane remains the only merger to main. Measure for one week against:
doorbell reliability, run caps (Max: 15/day), output quality. Report
keep/kill. Explicitly out: sim runs, GPU/Qwen work, anything needing local
state or secrets.

### 5. Environment hardening — RECOMMENDATION ONLY, director decides
Published full-auto pattern: container, non-privileged user, credentials the
agent cannot read, network egress allowlist, JSONL audit log. We run
bypass-permissions on the host, secrets in env files, public repo, one prior
probe incident. Produce a one-page recommendation: what Pattern-C-style
hardening would cost us (GPU access, File API, tmux workflows all complicate
containerisation), what it buys, and a pragmatic middle step if full
sandboxing is disproportionate. Tier-1 adjacent: no implementation without
the director's explicit call.

### 6. Harness pruning ritual (adopt as standing practice)
After each model upgrade: disable harness pieces one at a time and observe
what is still load-bearing; retire what isn't. Add to the retro cadence.

## DoD
Assessment doc (adopt/adapt/reject per candidate, with reasons) committed;
items 1-3 adoptions implemented, tested, and demonstrated (a blocked
future-read, a blocked sudo, a blocked unevidenced claim — show the logs);
item 4 pilots live with a one-week review date registered; item 5
recommendation filed for the director; item 6 in the retro checklist. Pixel
rule applies to every claim in the close NTFY.
