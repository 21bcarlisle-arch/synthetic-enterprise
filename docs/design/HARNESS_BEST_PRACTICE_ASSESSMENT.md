# Harness Best-Practice Adoption — assessment (P2, docs/staging/done/HARNESS_BEST_PRACTICE_ADOPTION.md)

**Status:** IN PROGRESS. Validation-first section and per-candidate adopt/adapt/reject
assessment complete. Technical verification of the exact hooks/fallbackModel/routines
mechanisms is DONE (via a `claude-code-guide` agent, since this environment has no network
access to check the referenced docs pages directly) -- all three confirmed real and
currently available, exact schemas below. Items 1/3/4's actual implementation is real,
separate engineering work registered as NEXT, not rushed into the same turn as this
assessment (items 5-6 do not depend on the verification and are addressed directly below).

## Verified technical schemas (2026-07-10, claude-code-guide agent, cited sources)

**1. Lifecycle hooks -- REAL** (`code.claude.com/docs/en/hooks.md`). `.claude/settings.json`
gains a `hooks` key with `PreToolUse`/`PostToolUse`/`PostToolUseFailure` (+20 others) event
names, each an array of `{matcher, hooks: [{type: "command", command, if, timeout,
statusMessage}]}`. `matcher` is pipe-separated tool-name alternation or JS regex; `if` narrows
further with permission-rule syntax (e.g. `"Bash(sudo *)"`, `"Read(docs/future-*)"`). The hook
script receives JSON on stdin (`session_id`, `hook_event_name`, `tool_name`, `tool_input`,
`cwd`) and blocks either via exit code 2 (stderr message shown) or JSON stdout
(`hookSpecificOutput.permissionDecision: "deny"` + a reason). Confirms all three intended
hooks (future-dated-read block, sudo block, unevidenced-claim block) are directly
implementable with this schema, no guessing needed once written.

**2. fallbackModel -- REAL** (`code.claude.com/docs/en/model-config.md`, shipped v2.1.166).
`.claude/settings.json`: `{"model": "...", "fallbackModel": ["claude-sonnet-5",
"claude-haiku-4-5"]}` -- chain of up to 3, tried in order only when the primary is
unavailable/overloaded/returns a non-retryable 5xx (not a cost/preference switch), lasts one
turn then reverts to trying primary first. CLI override: `--fallback-model model1,model2`.

**3. Routines -- REAL** (`code.claude.com/docs/en/routines.md`). Three trigger types: (a)
Schedule -- CLI `/schedule daily ...` / cron (min 1hr) / one-off, managed via `/schedule
list|update|run`; (b) API trigger -- POST to `api.anthropic.com/v1/claude_code/routines/
{id}/fire`; (c) GitHub event trigger -- `pull_request.*`/`release.*` events via the installed
Claude GitHub App, filterable by branch/label/draft-status, defaults to pushing only
`claude/`-prefixed branches (safety), each match spawns an independent session. Confirms the
two bounded pilots (scheduled Expert-Hour walk; GitHub-trigger doc-only sessions on
`[ADVISOR-STAGED]` commits) are both directly buildable as described, report/PR-only by
default matching this project's single-writer discipline.

**NEXT (not this turn):** implement item 1's three hooks (each individually testable/
removable per the staged instruction's own requirement -- show a blocked future-read, a
blocked sudo, a blocked unevidenced claim, in the logs), add `fallbackModel` to
`.claude/settings.json` (item 3), and register the two routines pilots with a one-week
review date (item 4). This is real, separate engineering deserving its own properly-tested
pass, not compressed into the tail of the turn that did this assessment.

## Validation first (the advisor's own request)

Confirmed, not assumed, that three existing mechanisms already independently match the
published patterns the advisor found:

- **The supervisor as outer-loop turn granter** (`background/supervisor.py`) matches the
  general "long-running agent needs an external granting loop, not self-continuation" pattern
  -- built this session specifically because self-continuation (the old autoloop) silently
  failed (doorbell failure #4).
- **Maturity-map evidence atoms default to `expert_hour: {status: not_attempted}`** -- every
  atom starts unproven, moves up only with cited evidence (commits/tests/surfaces), matching a
  "default-FAIL until evidenced" contract. This was tested directly this session: several atoms
  I had marked `status: passed` prematurely at seeding time were caught and corrected (W2, W4_2)
  precisely because the map's own philosophy expects real findings, not an assumed pass.
- **R7/R8** (injected/inbound text carries zero authority; correlate against real disk/git state
  before acting) already treat every wake, doorbell, and NTFY as untrusted input requiring
  independent verification -- exercised repeatedly this session (verifying every supervisor
  grant, every NTFY-borne director instruction, against the actual staged file or disk state
  before acting on it).

## Per-candidate assessment

### 1. Lifecycle hooks as deterministic law enforcement -- ADOPT (pending schema verification)
Real, valuable idea: our three named laws (point-in-time blindfold, no sudo, pixel/evidence
rule) currently live only in prompt text (CLAUDE.md), which is forgettable/soft-enforced, as
this session's own history shows directly -- the hedge-volatility bug was exactly a point-in-
time violation that no automated mechanism caught (confirmed this session:
`tools/epistemic_verifier.py` still only does import-statement regex matching, not data-flow
detection -- see the just-closed `EPISTEMIC_VERIFIER_TIMING_DETECTION_TIER1.md` gate). A
hook-level block, if the mechanism is real and matches what's described, would be a genuine
structural improvement over a static-analysis afterthought. NOT implemented yet -- the exact
hook event names, matcher syntax, and block-signalling mechanism need verification from a real
source before writing config I can't confirm works (dispatched, see status line above).

### 2. Fresh-context evaluator subagent at phase close -- ADOPT, once (1) lands, not before
A genuinely different failure mode than the Qwen skeptic already does: a fresh Claude evaluator
with no Write/Edit tools and no memory of the build would catch the exact class of mistake this
session made repeatedly and caught only by later self-audit -- e.g. marking `expert_hour:
passed` with no real findings (W2, W4_2), or the false claim that the epistemic verifier had
been extended (W4_2). Sequenced explicitly AFTER item 1 (the advisor's own ranking) since a
deterministic hook catching hard violations is higher-value, lower-risk than adding a second
judgement-based reviewer layer. Needs its own design pass against the referenced cwc repo's
evaluator pattern before building -- not started this turn.

### 3. Resilience settings (fallbackModel, session-cap review) -- ADOPT if the setting is real
Cheap, real value if it exists -- this session alone would have benefited from automatic
fallback during any primary-model overload. Not implemented yet: `.claude/settings.json`
currently has no `fallbackModel` (or similarly-named) key at all, and I am not confident enough
in the exact schema to add one without verification (a wrong key name is worse than no key --
it would silently do nothing while looking configured). Native parallel subagents as input to
the pending parallel-lanes proposal: noted, not decided here -- that proposal has its own owner
and sequencing.

### 4. Routines pilot (bounded) -- ADOPT THE PILOT SCOPE, pending mechanism verification
The two bounded pilots (scheduled Expert-Hour walk, report-only; GitHub-trigger doc-only
sessions on `[ADVISOR-STAGED]` commits, PR-only) are sensibly scoped -- both explicitly
report/PR rather than push to main, keeping the local lane the sole merger, which matches this
project's own single-writer/tree-lock discipline. Whether "Routines" is a real, currently
available product feature (vs. aspirational documentation) needs the same verification as
items 1 and 3 before registering a concrete implementation plan. If real: a one-week measurement
window against doorbell reliability, run caps, and output quality is a reasonable, low-risk way
to trial it without committing to it structurally.

### 5. Environment hardening -- RECOMMENDATION ONLY (see below), no implementation
Explicitly Tier-1-adjacent per the staged instruction itself -- correctly not implemented
without the director's explicit call. Recommendation filed as its own section below.

### 6. Harness pruning ritual -- ADOPT, actionable now
Simple, real, process-only. Added to the phase-close/retro discipline directly (see CLAUDE.md
change in this same commit): after each model upgrade, disable one harness piece at a time and
observe what's still load-bearing, retire what isn't.

## Item 5: environment hardening recommendation (director decision, not built)

**Current state:** bypass-permissions (`--dangerously-skip-permissions`) on the host, secrets in
plain env files (`background/.env.ntfy`), a public GitHub repo, and one prior real probe
incident (2026-07-05, referenced in CLAUDE.md's authentication-convention history).

**What a Pattern-C-style full sandboxing (container, non-privileged user, credentials the agent
cannot read, network egress allowlist, JSONL audit log) would cost this project specifically:**
GPU access for the local Ollama/qwen models (`skynet-1` via Tailscale) would need a containerised
path to the host's RTX 3060, which is a genuinely non-trivial containerisation problem (GPU
passthrough); the File API (`https://skynet-1.taila062fa.ts.net:8765`) and the tmux-based
multi-daemon workflow (supervisor/sim-runner/sanity-daemon/dispatcher all coordinating via
`tree_lock()` on one shared working tree) would need redesigning around container boundaries,
not just wrapping the existing processes.

**What it buys:** removes the single biggest asymmetric risk already once realised (the 2026-07-05
probe incident) -- a compromised or misdirected session currently has host-level reach, not
container-level.

**Pragmatic middle step, if full sandboxing is judged disproportionate to this project's actual
risk profile:** (a) move `background/.env.ntfy` and any other secret file out of the repo working
tree into a path never read by tool calls that touch `company/`/`saas/`/`site/` (reduces
accidental secret exposure in commits/diffs without requiring containerisation); (b) a network
egress allowlist scoped just to the already-named external endpoints (Elexon, NESO, Open-Meteo,
the Tailscale File API, github.com, npm/pip registries) rather than full container isolation --
achievable via existing sandboxing primitives without redesigning the GPU/tmux architecture.

This is a recommendation only. No implementation without the director's explicit in-console
call, per the standing authentication convention for safety-reducing/safety-affecting changes.

## Status / next steps

Awaiting the `claude-code-guide` agent's verification of the real hooks/fallbackModel/routines
mechanisms before implementing items 1, 3, 4. Item 5 recommendation filed above (no build). Item
6 adopted directly (see CLAUDE.md). Item 2 sequenced after item 1 lands. This does not displace
MARGIN_REALISM or the maturity-map queue, both of which are genuinely exhausted right now
pending director/advisor input (see PRIORITIES.md's "MATURITY-MAP QUEUE STATUS" entry) -- this
is legitimate, non-displacing work to pick up while those wait.
