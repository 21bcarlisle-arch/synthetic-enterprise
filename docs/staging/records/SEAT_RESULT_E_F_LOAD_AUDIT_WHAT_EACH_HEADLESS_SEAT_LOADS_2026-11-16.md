**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# E-f, the load audit: what each headless seat loads, and what it used in the week (2026-11-16)

*Seat executor, Mon 16 Nov 2026, about 05:00 GMT. The second steer, item 2:
`docs/staging/advisor/DIRECTOR_STEER_TEST_CLAUDE_MD_BY_DELETING_AND_ADDING_BACK_AND_AUDIT_WHAT_EACH_SEAT_LOADS_2026-11-15.md`.
Backlog rows: `docs/operations/EFFICIENCY_BACKLOG.md` E-f, E-f2, E-f3.*

**Two lanes ran this audit at once.** The worker landed the plugin switch-off first (9554dcf49f, 05:11 GMT,
−3,911 tokens by its paired probes). This lane measured the same switch at −3,893 and dropped its own copy
of the change. What this record adds: the census split per seat kind, and the 11 tools no seat called.

## How it was measured

- **What loads:** six `claude -p --model haiku --output-format stream-json --verbose` probes, prompt
  "Reply with the single word ok.", CLI 2.1.319, cwd the seat executor's worktree. The `system/init`
  event lists tools, MCP servers, skills and plugins; the `result` event gives the context tokens in.
  Haiku tokens, so the absolute numbers are approximate for Opus; the differences are what matter.
- **What was used:** every top-level transcript under `~/.claude/projects/` that started between
  9 Nov 03:00 and 16 Nov 03:00 UTC, classed by `tools.tick_burn_rate.kind_of`, counting `tool_use`
  blocks by name and `Skill` calls by skill.

## Who spawns how

| Seat kind | Spawn flags | Turns 9–16 Nov | Tool calls |
|---|---|---|---|
| worker_tick | `HEADLESS_FLAGS` (`--strict-mcp-config`) | 222 | 10,401 |
| seat_executor | `HEADLESS_FLAGS` | 175 | 9,046 |
| delivery_seat | `HEADLESS_FLAGS` | 50 | 654 |
| build_executor | none (loads MCP) | 0 (service inactive) | 0 |
| autonomous_runner | none (loads MCP) | 0 (service inactive) | 0 |

The 51 "other" turns in the window are Fable trials and blind-review readers, with their own configs.

## What loads (context tokens in, first call)

| Probe | Tools | MCP servers | Skills | Plugins | Context in | Against strict |
|---|---|---|---|---|---|---|
| no flags (build_executor, autonomous_runner) | 34 | 42 | 107 | 14 | 39,922 | +2,495 |
| `--strict-mcp-config` (**the three live seats**) | 24 | 0 | 107 | 14 | **37,427** | — |
| + account plugins off (`--settings enabledPlugins`) | 24 | 0 | 36 | 4 | 33,534 | **−3,893** |
| + 11 never-used tools off (`--disallowedTools`) | 13 | 0 | 107 | 14 | 34,584 | **−2,843** |
| + all skills off (`--disable-slash-commands`), bound only | 23 | 0 | 0 | 14 | 32,718 | −4,709 |

The 37,427 includes CLAUDE.md (about 9,900 tokens) and Claude Code's own system prompt. The four
plugins that stay are the CLI's builtin `cc-plugin-*`; they cannot be switched off by settings.

## What the seats used in the week

- **Tools used:** Bash (19,263), Write (209), Edit (177), ToolSearch (151), Monitor (93), Agent (51),
  ScheduleWakeup (42), Read (45), TaskStop (33), WebSearch (26), SendMessage (6), Skill (3), ListAgents (2).
- **Never used by any seat:** CronCreate, CronDelete, CronList, DesignSync, EnterWorktree, ExitWorktree,
  NotebookEdit, PushNotification, RemoteTrigger, ReportFindings, Workflow.
- **Skills used:** 3 calls, all project skills (cold-eyes-walk 2, phase-close 1, all in worker_tick).
  **0 of the 75 plugin skills** were called.
- **MCP servers:** none loaded by the live seats, so none used.

## The switch-offs, proposed as trials with their reversals (one at a time)

| Trial | Change | Saving per call | Evidence it is unused | Reversal |
|---|---|---|---|---|
| E-f (landed by the worker, 9554dcf49f) | account plugins off in `HEADLESS_FLAGS` | ~3,900 (10% of fixed load) | 0 plugin-skill calls in 447 turns | delete the `--settings` pair |
| E-f2 (after E-e, one variable at a time) | `--disallowedTools` for the 11 never-used tools | ~2,800 (8%) | 0 calls in 447 turns, 20,101 calls | delete the flag |
| E-f3 (consistency, zero saving now) | build_executor and autonomous_runner take `HEADLESS_FLAGS` | ~6,400 per turn, if they run | 0 turns this week | remove the splat |

**A prediction for E-f's Friday read**, written before any after-window was read: a seat's first-call context
falls by 3,100–4,700 tokens on Opus, which is 3–5% of all seat context tokens (a seat call averaged about
100k context tokens: 2,162m over ~21k calls). Refuted below 2,000 or above 6,000.

**What this does not settle.** Rule of three: 0 uses in 447 turns bounds the per-turn need below about
0.7% at 95%. A tool a seat needs once in a thousand turns would not have shown, so each trial watches
for a failed call to a removed name, and that is the revert rule. **Worth a look, not a trial:**
ScheduleWakeup was called 42 times by headless seats, where nothing re-invokes a `-p` session; each
call is a turn that may have ended expecting to be woken.

Raw probes: `/tmp/ef_audit/*.jsonl` on this machine (not kept).
