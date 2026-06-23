# background/ — Daemon Process Layer

Always-on background processes that run independently of the Claude Code session.

## Process map

| Script | Role | Heartbeat |
|--------|------|-----------|
| `sim_runner.py` | Runs full 10-year sim in a loop; writes `run_complete_*.md` markers | Per run (~7 min) |
| `autonomous_runner.py` | Polls `docs/staging/` for `run_complete_*.md` and publishes results | Per marker |
| `background_worker.py` | General-purpose background task queue | Per task |
| `dispatcher.py` | Classifies and routes inbound NTFY messages | Per message |
| `ntfy_responder.py` | Writes inbound NTFY (>25 chars) to `docs/staging/from_rich_*.md` | Per message |
| `health_check.py` | Pings all daemons; updates `docs/observability/health-check-log.md` | Every 5 min |
| `session_watchdog.py` | Monitors Claude Code session activity | Continuous |
| `discovery_agent.py` | Background discovery — reads market research, writes findings | On demand |

## Shared infrastructure

- `agent_status.py` — structured status emitter; all daemons call `update_agent_status()` to write to `docs/observability/agent_status.json` and `site/data/agent_status.json`
- `agent_protocol.py` — `AgentMessage` + `IntentType` schema for inter-agent messages (Phase 43b / Architecture Stage 4)
- `ntfy_utils.py` — `send_ntfy(message)` wrapper for outbound NTFY notifications to Rich
- `file_api.py` — serves `docs/status/LATEST.md` at `/ui/status` for mobile checks

## Observability

Live logs in `docs/observability/`. Mirrored to `site/data/agent_status.json` and rendered on the System tab at poesys.net.

## Starting all daemons

```bash
# From repo root (each in its own tmux pane or systemd unit)
python3 background/sim_runner.py
python3 background/autonomous_runner.py
python3 background/ntfy_responder.py
python3 background/health_check.py
python3 background/dispatcher.py
```
