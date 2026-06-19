# Background Task Queue

Tasks in QUEUED status will be picked up by background/background_worker.py
during off-peak hours (not between 16:00-19:00 GMT).
Tasks move to RUNNING then DONE. Worker logs to docs/observability/background-worker-log.md.

---

## QUEUED


### Task: gpu-utilisation-monitor
Add a background process to background/start_worker.sh that samples nvidia-smi
every 30s and appends to logs/gpu_utilisation.log in format:
timestamp, gpu_util_pct, vram_used_mb, vram_total_mb.
Add a summary function reading the last hour of that log (avg/max utilisation)
and include it in NTFY phase completion messages. Write a test. make check,
commit, push, NTFY confirming live.
Promoted from docs/staging/TASK_GPU_MONITOR.md on 2026-06-12.

### Task: token-efficiency-tracking
Add tracking to the Context Handshake mechanism: count frontier calls (Claude
Code invocations) and local model calls (Ollama) per phase, log to
logs/token_efficiency.log (timestamp, phase, frontier_calls, local_calls,
local_pct). Include local vs frontier ratio in every NTFY phase completion
message; flag WARNING if local_pct < 60%. Write a test. make check, commit,
push, NTFY confirming live.
Promoted from docs/staging/TASK_TOKEN_EFFICIENCY.md on 2026-06-12.

### Task: customer-archetype-data-enrichment
Run as a GPU side mission alongside Phase 4c. Build a statistically grounded
synthetic customer population from real UK public datasets to replace
hand-crafted customer definitions.

Sources to acquire and profile:
1. EPC register — DLUHC England/Wales full dataset
   (https://epc.opendatacommunities.org). Download, sample if needed for
   memory, cluster into 8-12 archetypal property types by: property type,
   floor area, EPC rating, heating system, construction era, estimated
   annual consumption.
2. Census 2021 — ONS output area data (https://www.ons.gov.uk/census).
   Extract household composition, tenure, occupation group, car ownership by
   output area. Map to energy demand archetypes.
3. Ofgem vulnerability and debt data — extract payment method distributions,
   debt levels, vulnerability segment sizes from published Ofgem reports.

Deliverable: docs/data/customer_archetypes.md — a parameter file defining
8-12 customer archetypes, each with: property type, EPC rating, heating
system, asset mix, occupancy pattern, socio-demographic profile, estimated
annual consumption (elec/gas), credit risk score, vulnerability flag,
preferred channel, debt risk indicator. This file replaces the hand-crafted
customer definitions in saas/customers.py in a future increment.

Use local models (qwen3:14b) for all data processing. No frontier tokens.
NTFY when complete with archetype summary.
Promoted from docs/staging/TASK_DATA_ENRICHMENT.md on 2026-06-13.




---

## RUNNING
(none)

## DONE

### Task: stack-health-check
Completed: 2026-06-19 06:08 UTC


### Task: downtime-observability-housekeeping
Completed: 2026-06-13 14:21 UTC


### Task: phase4b-4-draft-home-move-win-rate
Completed: 2026-06-13 13:51 UTC


### Task: simulation-sensitivity-experiments
Completed: 2026-06-11 19:00 UTC


### Task: code-quality-audit
Completed: 2026-06-11 15:30 UTC


### Task: pre-fetch-nbp-gas-full
Completed: 2026-06-11 15:00 UTC


### Task: pre-fetch-pc3-profiles
Completed: 2026-06-11 14:30 UTC


### Task: pre-fetch-weather-full
Completed: 2026-06-11 14:00 UTC


### Task: pre-fetch-elexon-full
Completed: 2026-06-11 13:59 UTC


