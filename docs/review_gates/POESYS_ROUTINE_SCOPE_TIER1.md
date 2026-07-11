# Tier 1 review gate: correct scope for the poesys Routine (Restricted profile)

**Status: BLOCKED awaiting director decision. Not a live risk right now** -- the routine
is paused (`enabled: false`, confirmed via RemoteTrigger), so nothing runs until this
gate clears. This file exists so the block is tracked on disk (health-check/deadman's-switch
visibility), not just sitting in an NTFY. Re-ping daily while blocked per CLAUDE.md's Tier 1
handling; other queue items proceed in the meantime (this is non-blocking to the rest of the build).

## Why this is Tier 1

`H5_security_profiles`'s hard rule (CLAUDE.md, 2026-07-11): "Profile changes are
director-console-only -- the agent can NEVER alter its own profile, full stop... this is a
safety-control modification (Tier 1) every time, no exceptions." Deciding what the
"Restricted" profile should actually grant a cloud/Routines lane is exactly that kind of
change. I paused the routine (the kill-switch action the director himself pre-authorized
for an anomaly, 2026-07-11 05:59 UTC directive) but did not touch its scope -- that's this
gate.

## What was found (evidence)

`RemoteTrigger get` on `trig_01Xj4Xkj7sD5Fmv7nZVzW41c` ("Daily phase-close health check
(pilot)", `environment_id: poesys`, cron `0 3 * * *`) showed:

```
allowed_tools: preset:default, Task, Bash, Glob, Grep, Read, Edit, MultiEdit, Write,
               NotebookEdit, WebFetch, TodoWrite, WebSearch, BashOutput, KillBash,
               Skill, Tmux, Monitor, SendUserFile, REPL
mcp_connections: Gmail (gmailmcp.googleapis.com), Spotify (mcp-gateway-external-pilot.
               spotify.net), Claude_Code_Remote (api.anthropic.com)
```

This directly contradicts the director's own explicit binding constraint from the
2026-07-11 05:59 UTC in-console directive (`docs/observability/session-watchdog-log.md:4354`):
> "Constraints binding: report-only (issues/PRs, never pushes main), daily schedule max,
> pause-on-anomaly as kill switch."

Full write/edit/bash access is the opposite of report-only. The Gmail and Spotify MCP
connectors were never mentioned in either the 05:36 or 05:59 UTC directives at all --
unclear whether they were intentionally attached or are a platform default that came
along with the environment/trigger creation flow.

## Decision needed

What should this routine (and the Restricted profile generally, for future cloud/Routines
lane work) actually be allowed to do?

**Option A (recommended) -- re-create narrow, matching the original intent literally.**
Re-create the trigger (or ask if `update` can narrow `allowed_tools` directly -- untested)
with `allowed_tools` limited to read/report-only primitives (`Read, Glob, Grep, WebFetch,
TodoWrite` -- no `Bash`/`Write`/`Edit`/`MultiEdit`), and the Gmail/Spotify MCP connectors
removed unless the director confirms they were intended. Matches "report-only, issues/PRs,
never pushes main" literally. Loses the ability to actually open a GitHub issue/PR directly
from the routine unless that needs `Bash` (gh CLI) or a dedicated PR-only tool -- flagging
this tension rather than guessing at the resolution.

**Option B -- keep broad access, rely on the routine's own system prompt to self-restrict.**
If the prompt given to the routine already instructs it to stay report-only (I could not see
a `prompt` field via the API to confirm either way), the tool grant is defense-in-depth that
never gets exercised in practice. Weaker: a prompt is not an enforced boundary, and this is
exactly the class of gap (assumed-safe-because-of-intent, not verified) this same investigation
was launched to catch.

**Option C -- narrow scope but keep Gmail/Spotify if intentional (e.g. the routine is meant
to email a digest or similar).** Needs the director to say what the routine is actually for
beyond "phase-close health check" if messaging/external-account reach is wanted.

## Recommendation

Option A. Re-enable only after the scope matches "report-only, issues/PRs, never pushes
main" literally, with Gmail/Spotify removed unless confirmed intentional. I have not
re-enabled the routine and will not until this gate clears.

## What unblocks this

The director confirming intended scope (in-console, or clearing this gate file per the
authentication convention for safety-reducing changes -- not via NTFY/commit alone, since
re-enabling broader-than-report-only access is itself safety-reducing).
