# Tier 1 review gate: correct scope for the poesys Routine (Restricted profile)

**Status: CLOSED 2026-07-11.** Director decision received via `docs/staging/done/
ADVISOR_STEER_ROUTINE_SCOPE.md` (advisor-staged, self-identifies as Tier 2, relaying a live
director decision "he has seen and approved this routing"). Resolution: **routine stays
paused/dead** — the read-only tool narrowing landed, but the instructed "open a GitHub issue
only" output channel turned out to be structurally unachievable with a genuinely minimal
read-only tool set, and the doc's own fallback rule governs that exact case.

## Why this is Tier 1

`H5_security_profiles`'s hard rule (CLAUDE.md, 2026-07-11): "Profile changes are
director-console-only -- the agent can NEVER alter its own profile, full stop... this is a
safety-control modification (Tier 1) every time, no exceptions." Deciding what the
"Restricted" profile should actually grant a cloud/Routines lane is exactly that kind of
change. I paused the routine myself (the kill-switch action the director pre-authorized for
an anomaly, 2026-07-11 05:59 UTC directive) but did not touch its scope unilaterally -- that
required this gate.

## What was found (evidence)

`RemoteTrigger get` on `trig_01Xj4Xkj7sD5Fmv7nZVzW41c` ("Daily phase-close health check
(pilot)", `environment_id: poesys`, cron `0 3 * * *`) originally showed full
`Bash/Write/Edit/MultiEdit/Tmux/REPL/SendUserFile` access plus Gmail/Spotify/Claude_Code_Remote
MCP connectors attached -- contradicting the director's 2026-07-11 05:59 UTC binding
constraint ("report-only, issues/PRs, never pushes main").

## Decision received (docs/staging/done/ADVISOR_STEER_ROUTINE_SCOPE.md)

Reconfigure before any re-enable: `allowed_tools` = read/fetch only, all MCP connectors
stripped, output = GitHub-issue-only, re-enable only after a verified (re-fetched, not
trusted-from-response) config is posted in a digest; **if read-only can't be guaranteed,
leave the routine dead.**

## What was actually done, and what was found while doing it

1. **`allowed_tools` narrowed** to `["Read", "Glob", "Grep", "WebFetch", "WebSearch",
   "TodoWrite"]` via `RemoteTrigger update` -- stricter than the doc's own named exclusion
   list (also dropped `preset:default`, `Task`, `NotebookEdit`, `BashOutput`, `KillBash`,
   `Skill`, `Tmux`/`Monitor` for genuine minimality, not just the explicitly-named ones).
   **Verified via a separate, independent `get` call (R1: re-fetch and diff, don't trust the
   update response)** -- confirmed persisted.
2. **MCP connectors could NOT be stripped via the API** -- passing `mcp_connections: []` in
   the update body was silently a no-op; Gmail/Spotify/Claude_Code_Remote all still appear on
   a fresh `get`. Real, honest finding, not glossed over: this environment's connectors may be
   account/environment-level rather than truly per-trigger removable through this endpoint.
   **Correction to my own earlier ACTION-NEEDED NTFY**: I re-checked the VERY FIRST `get`
   response from before any changes -- all three connectors already showed
   `permitted_tools: []` (zero actual tool grants), unchanged before and after. So the
   functional risk these connectors ever posed was zero throughout, not "live Gmail/Spotify
   access" as I characterized it in the original alert -- the real, substantiated risk was
   always the `allowed_tools` local-write grant, which is now fixed. Flagging my own
   overstatement rather than letting it stand uncorrected.
3. **"Output = GitHub issue only" is not achievable with this tool set.** Opening a GitHub
   issue needs *some* write-capable path (`Bash`+`gh`, or a dedicated issue-creation tool);
   none exists in a genuinely minimal read-only set, and none was named as an available
   alternative. This is exactly the case the staged doc's own fallback anticipates: **"If
   read-only cannot be guaranteed on this platform, leave the routine dead -- the pilot is
   not worth the surface."** Read-only IS guaranteed (verified) but the *output channel* the
   pilot exists to produce is not achievable within it -- same practical conclusion.

## Resolution

**Routine stays `enabled: false`.** Not re-enabled. `allowed_tools` is now genuinely minimal
and read-only (verified), which is a real, standing safety improvement over the original
config regardless of whether the pilot itself ever runs again. Re-enabling requires either a
different, write-capable-but-still-narrow output mechanism to be identified and separately
approved (a fresh decision, new gate if it touches scope again), or the pilot being retired
outright -- director's call, not blocking anything else in the meantime.

## Standing rule added (per the staged doc's own instruction)

CLAUDE.md's routines-creation guidance updated: every routine creation must set an explicit
MINIMAL `allowed_tools` and an EMPTY/verified connector list, then re-fetch and diff the
actual persisted config against the binding constraint before first run (R1 applied to
routine configs — the creation/update response is not evidence, only a fresh `get` is).
