**Severity:** LATENT · **Lane:** H_harness

# The interactive seat stopped mid-work, and this is what it was holding

**Filed automatically by `background/seat_continuity.py`, not by a person.** The seat ran no
tool for **0.4h** and its process is gone. It did not stop on purpose: an
interactive session that finishes says so, and this one just stopped — which is the shape an
Anthropic API error leaves behind, four times now by the director's count.

This document exists so that nobody has to notice. It is a staged doc, so the next worker tick
draws it like any other work.

## What it had claimed

- Nothing was claimed. Whatever it was doing, it did not say.

## What it left in the tree, uncommitted

This is the real state — more reliable than anything the session could have written about
itself, because an API error is precisely the thing that stops it writing.

- `CLAUDE.md`
- `PRIORITIES.md`
- `background/.dispatcher_seen.json`
- `background/.ntfy_responder_rate.json`
- `background/.ntfy_responder_since.json`
- `background/.staging_watcher_seen.json`
- `background/pull_forward_proposal.py`
- `background/seat_work_in_hand.py`
- `company/analytics/customer_value_view.py`
- `company/interfaces/customer_value.py`
- `docs/context-handshake-latest.md`
- `docs/design/maturity_map.yaml`
- `docs/design/simplifications/EP1_clv_three_horizon.yaml`
- `docs/design/simplifications/FUT2_pull_forward_proposal.yaml`
- `docs/design/simplifications/KNIFE3_wall_crossing_paydown.yaml`
- `docs/design/simplifications/archive/EP1_clv_three_horizon.009.yaml`
- `docs/market_data/consumption_feed.json`
- `docs/market_data/price_feed.json`
- `docs/observability/.daily_self_note_last_date`
- `docs/observability/.human_last_input`
- `docs/observability/.last_tested_hash`
- `docs/observability/.operational_layer_signal.json`
- `docs/observability/.product_interleave_state.json`
- `docs/observability/.publish_gate_state.json`
- `docs/observability/.sanity_daemon_last_digest_date`
- `docs/observability/.seat_work_in_hand.json`
- `docs/observability/.supervisor_stuck_state.json`
- `docs/observability/action_needed_register.json`
- `docs/observability/agent_status.json`
- `docs/observability/autonomous-runner-log.md`
- `docs/observability/background-worker-log.md`
- `docs/observability/band_null_sweep.json`
- `docs/observability/build-executor-log.md`
- `docs/observability/cold_eyes_battery_reconciliation.jsonl`
- `docs/observability/coupled_gap_ledger.json`
- `docs/observability/daily-self-note.md`
- `docs/observability/deadmans-switch-log.md`
- `docs/observability/decision_log.jsonl`
- `docs/observability/discovery-log.md`
- `docs/observability/dispatcher-log.md`
- `docs/observability/edge_traffic.jsonl`
- `docs/observability/fabric_settlement_gap.json`
- `docs/observability/fidelity_evidence_ledger.json`
- `docs/observability/health-check-log.md`
- `docs/observability/instructions_loaded_log.jsonl`
- `docs/observability/model_tier_log.jsonl`
- `docs/observability/naive_organ_log.jsonl`
- `docs/observability/ntfy-responder-log.md`
- `docs/observability/publish_gate_red_census.json`
- `docs/observability/pull-loop-log.md`
- `docs/observability/retired_paths_served.json`
- `docs/observability/run_history.json`
- `docs/observability/run_insights.json`
- `docs/observability/sanity-daemon-log.md`
- `docs/observability/sanity_adjudication_ledger.json`
- `docs/observability/self_clearing_alarm_census.json`
- `docs/observability/sim-runner-log.md`
- `docs/observability/size_ratchet_warnings.jsonl`
- `docs/observability/staging-watcher-log.md`
- `docs/observability/supervisor-log.md`

…and 521 more.

## Where it had got to

- Last tools it ran, oldest first: Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Bash, Read
- Tool calls this session: 29
- Last commit on the tree: `4c42f31ec Auto-process run complete: report + LATEST.md + site/ (git=3b25c333f, net=£1,277,721)`

## What to do with it — decide, do not just re-run

**Adopt** if the uncommitted paths above are coherent work part-way to something: read the
diff, finish it, commit it. That is the cheap outcome and the usual one.

**Discard** if the diff is a half-applied edit that no longer makes sense — `git checkout --`
the paths and take the claim from scratch. Say which you did.

Do NOT assume the work is wrong because the session died. The failure was in the transport,
not in the edit; the tree state above is exactly what a healthy session would have had at that
moment.

Archive to `docs/staging/done/` once the paths above are either committed or reverted.
