# Routines pilot — first trigger created (2026-07-11)

**Authorized:** director NTFY, "You create it, against poesys... Include the exact prompt +
schedule in your confirmation ntfy — I review after the fact and will say pause if I object."

## Real, live trigger

- `trigger_id`: `trig_01Xj4Xkj7sD5Fmv7nZVzW41c`
- `environment_id`: `poesys` (director-created)
- `cron_expression`: `0 3 * * *` (daily, 03:00 UTC)
- `next_run_at`: `2026-07-12T03:01:31Z` (confirmed via a live `get` call)
- `enabled`: true

## Exact prompt (verbatim, as submitted)

```
You are running as a scheduled, unattended Routine against the synthetic-enterprise
repo. This is a REPORT-ONLY pilot -- you must NEVER commit, push, or merge to main
(or any branch) under any circumstances. Your only allowed output is a GitHub issue.

Task: review the last 24 hours of commits and CLAUDE.md's "Current state" entries.
1. Run `python3 -m tools.epistemic_verifier` -- note PASS/FAIL.
2. Run `python3 -m pytest --collect-only -q` and compare the collected count against
   the most recent "N tests collected" figure in CLAUDE.md -- flag any mismatch or
   unexplained drop.
3. Spot-check whether each new CLAUDE.md Current-state entry cites real evidence (a
   test count, a fetched live-site confirmation, or a named artefact) per this
   project's own "Done = named artifact" rule.
4. If you find anything genuinely concerning (a FAIL, a test-count regression, an
   unevidenced claim, or any other real anomaly), open a GitHub issue titled
   "[ROUTINE ANOMALY -- PLEASE REVIEW]" describing exactly what you found, and
   explicitly ask Rich to pause this Routine from the claude.ai/code UI until it's
   addressed. Do not attempt to fix it yourself. Take no git-write action of any kind.
5. If everything looks clean, open NO issue at all -- silence on a clean day, per
   this project's own R5 alerting discipline.
```

## Real schema found live (previously undocumented in this repo)

`create`'s body is NOT a flat `{name, prompt, schedule, environment}` shape as first
guessed -- a first attempt with that shape returned a clean HTTP 400 ("One of
job_config or session_request must be set"). The real, working shape:

```json
{
  "name": "...",
  "job_config": {
    "prompt": "...",
    "ccr": {"environment_id": "poesys"}
  }
}
```

The schedule is **not** inside `job_config` at all -- it is a **top-level**
`cron_expression` field, set via a separate `update` call after creation (the create
response itself revealed this: it echoed back an empty top-level `cron_expression`
field, which is what exposed the real field name).

## Honest caveats, not glossed over

- **Tool access is broader than originally proposed.** The create/update calls above
  never set an explicit tool restriction, and the response shows
  `session_context.allowed_tools` includes `Edit`/`MultiEdit`/`Write`/`NotebookEdit` --
  the full default preset, not the read-only-only (`Read`/`Bash`/`Grep`/`Glob`) design
  floated in the pre-creation preview. Report-only is therefore enforced entirely by
  the PROMPT's own explicit instructions ("never commit, push, or merge... take no
  git-write action") plus real GitHub branch-protection on `main` as the hard
  backstop -- not by any tool-level restriction. If a tighter `allowed_tools` field is
  found later, tighten this trigger via `update`.
- **No confirmed self-pause API.** The kill switch is the routine itself *asking* Rich
  to pause it via the claude.ai UI (prompt step 4) when it finds something wrong --
  not a self-pause action taken automatically. `RemoteTrigger` exposes
  list/get/create/update/run, no delete; pausing (if needed) would be via `update`
  with whatever field the API uses for enabled/disabled (not yet tested).
- **Repository scope is implicit.** No `repository` field was set or appeared in the
  response -- the `environment_id: "poesys"` binding is assumed to carry the repo
  scope (the director set that environment up specifically for this repo), not
  independently re-verified against a repository-listing endpoint.

## First real run

Not yet observed -- `next_run_at` is 2026-07-12T03:01 UTC. Check back after that time
and record the outcome here (or archive this doc once the pilot has run at least once
successfully).
