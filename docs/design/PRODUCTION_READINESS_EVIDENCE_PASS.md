# Production Readiness — Evidence Pass (Part A)

Generated: 2026-07-11. Companion to `docs/staging/done/PRODUCTION_READINESS_BASELINE.md`.
Read-mostly measurement pass — no application code changed, nothing fixed. Every claim below
is labelled `observed-with-evidence` (measured directly this session) or `inferred` (reasoned
from code/logs without direct execution), per R9. Detailed security findings live in the
PRIVATE ops repo (`~/synthetic-enterprise-ops/production_readiness_security_findings.md`);
this doc and `docs/design/PRODUCTION_READINESS_SECURITY_SUMMARY.md` carry only sanitised
summaries.

**No live risk found matching the immediate-action carve-out** (no exposed credential value,
no about-to-be-committed secret). One genuinely unrecoverable-data finding is reported under
Recoverability below — not imminent-danger tier (nothing is about to be lost), but a real gap.

## 1. Recoverability

**observed-with-evidence.** `git remote -v` confirms this repo IS mirrored to GitHub
(`https://github.com/21bcarlisle-arch/synthetic-enterprise.git`, both fetch and push) — so
everything tracked in git has real off-machine recoverability, not sole-copy-on-Skynet.

**Canonical data that exists ONLY on this machine, no upstream backup (gitignored, confirmed
via `.gitignore` + `git check-ignore -v`, not assumed):**
- `company/data/*.db` — 4 SQLite files (`invoices.db` 24K, `registry.db` 20K,
  `direct_debit.db` 20K, `service_log.db` 2.1M), all under the gitignored `company/data/` rule.
  This is the company's own operational financial/customer state — genuinely local-only.
- `background/.env.ntfy`, `background/.env.file-api` — secret credential files, correctly
  gitignored (see security summary).
- Several `docs/observability/*.json` state files are gitignored too (`.usage_pause.json`,
  `.sent_ntfy_ids.json`, `.last_push_time.json`, etc. — see `.gitignore` lines 8-13) — these are
  low-value transient state, not canonical business data, so their local-only status is a much
  smaller risk than `company/data/`.
- `docs/reports/run_output_*.json` (individual dated run outputs) are gitignored (only
  `run_output_latest.json` — the symlink/copy target — is tracked); `docs/reports/ledger_latest.json`
  is also gitignored. Historical per-run raw output beyond what's mirrored into tracked
  observability JSON is local-only.

**Restore test performed (not simulated):** copied `background/.env.ntfy` (236 bytes) to a
scratch location (`/tmp/.../scratchpad/restore_test/env.ntfy.restored`, never overwriting the
live file) and read it back to confirm byte-for-byte integrity (236 bytes in, 236 bytes read
back). **Measured RTO for this one artefact: copy ~9ms, read-back-confirm ~13ms — under 25ms
total.** This measures local-filesystem copy speed only; it does NOT test recovery from actual
machine loss (there is no off-machine copy of `company/data/*.db` or the two `.env.*` files to
restore FROM in a real Skynet-loss scenario — that is precisely the gap this finding names).

**Verdict:** git-tracked content (code, most docs, most observability JSON) has real
off-machine recoverability via GitHub. `company/data/*.db` (the company's actual operational
DB state) and the two credential files do NOT — a full Skynet loss would lose them with no
recovery path. Not flagged as imminent-danger (nothing about to happen), but a real, named gap
for the orchestrator to weigh (e.g. periodic encrypted backup of `company/data/` to the ops repo
or another off-machine target).

## 2. Security posture

See `docs/design/PRODUCTION_READINESS_SECURITY_SUMMARY.md` for the sanitised summary (secrets
CLEAN, 1 medium-tier stale-server finding, 1 low-tier CORS finding, dependency scan gap —
`pip-audit` not installed). Detailed findings (exact ports/paths) are in the private ops repo
per the security boundary in the staged instructions. `docs/design/HARNESS_BEST_PRACTICE_ASSESSMENT.md`
covers the sandbox/Pattern-C hardening angle — absorbed as input, not re-derived.

## 3. Performance / capacity

**observed-with-evidence.** Current population: 19 customers (`per_customer_lifetime` count in
`docs/reports/run_output_latest.json`). Full-run wall-clock, most recent 6 samples from
`docs/observability/sim-runner-log.md` (2026-07-11 14:51-15:35 UTC window): 462s, 458s, 471s,
470s, 474s — consistent with CLAUDE.md's already-established ~468-484s figure. `run_output_latest.json`
disk footprint: **2,911,045 bytes (~2.9 MB)** for 19 customers.

**Extrapolation (inferred, not measured — no 190- or 1900-customer run exists to measure):**
Two confirmed O(n²)-shaped patterns in `simulation/run_phase2b.py`, found by reading the actual
loop bodies (not guessed):
- Line 1960-1962: `for c in ELEC_CUSTOMERS + GAS_CUSTOMERS: recs = [r for r in all_records if
  r["customer_id"] == cid]` — for every customer, a full linear scan of `all_records` (every
  settlement record for every customer across the whole sim). This is customers × total-records,
  i.e. quadratic in population (since total-records itself scales linearly with population).
- Line 2169-2174 (TRIAD exposure calc): nested `for winter_year in ...: for cid in
  ic_customer_ids: cid_records = [r for r in all_records if r.get("customer_id") == cid]` — same
  full-scan-per-customer pattern, additionally multiplied by number of winters.

At 19 customers this cost is invisible inside a ~470s run dominated by the genuine half-hourly
settlement generation (`simulation/hedged_settlement.py`'s `for period in range(1, 49)`, run
once per customer-period — itself linear, not the risk). At 10x (190 customers) the two
quadratic per-customer-lifetime-summary/TRIAD scans would cost ~100x more than today for that
specific pass (not the whole run) — likely still tolerable. At 100x (1900 customers) that same
piece becomes ~10,000x costlier in isolation and would plausibly dominate total runtime,
independent of the (already-flagged-elsewhere) M1 event-drain scaling concern for the outer
settlement loop. This is a genuine, code-verified risk, not a guess — but it has NOT been
load-tested at either scale; treat the "still tolerable at 10x" claim as inferred, not measured.

**Also observed:** `docs/observability/risk-committee-log.md` has grown to **277 MB**
(unbounded append-only log, largest observability artefact by ~60x over the next-largest,
`sim-runner-log.md` at 4.7 MB). Not a correctness risk, but a real disk-growth trajectory worth
tracking — no rotation/truncation mechanism observed for this file.

## 4. Availability

**observed-with-evidence.** `docs/observability/session-watchdog-log.md` shows real crash/restart
history, not just design intent:
- 2026-07-04 04:16 and 05:41 UTC: "Session watchdog: restart cap reached (3/hour) — pausing 60
  min before resuming" — two genuine crash-loop episodes within a single day.
- 2026-07-05 06:37 UTC: three consecutive "Claude binary not found under
  /home/rich/.nvm/versions/node/*/bin/claude -- cannot restart. Check the nvm install." entries
  — a real ~22-minute outage (06:37 to 06:59 when the watchdog next started successfully) caused
  by an nvm/node-path issue, not application logic.
- `docs/observability/dispatcher-log.md` (9,432 lines) shows **zero** matches for
  error/exception/traceback/fail patterns this session — no dispatcher-level crash history found
  in the log as currently retained (log may have been rotated/truncated at some point; absence
  of evidence here is not strong evidence of zero-ever-crashes).

**Single points of failure (observed-with-evidence unless marked inferred):**
- **The whole stack runs on one physical machine (Skynet) with no redundancy** — confirmed by
  design (CLAUDE.md's own "Technical environment" section), not inferred. Any hardware failure
  takes down sim runner, all background daemons, and both file/DB stores simultaneously.
  Mitigated only for git-tracked content (see Recoverability) — NOT for `company/data/*.db`.
- **NTFY topic env var is a shared dependency for 6 daemons**: `background/staging_watcher.py`,
  `background/ntfy_utils.py`, `background/session_watchdog.py`, `background/ntfy_responder.py`,
  `background/director_comments.py`, `background/director_input_log.py` all reference the
  NTFY topic/env-file mechanism — confirming the CLAUDE.md-referenced risk ("if the NTFY topic
  env var isn't loaded, 6 daemons can't start") is real and currently exactly 6, not a stale
  number.
- **`session_watchdog.py` itself is a single restart authority** — the nvm-path outage above
  shows that when its own restart mechanism's assumption (node/claude binary location) breaks,
  the whole autonomous loop stalls until manually or self-corrected; no secondary watchdog
  exists to catch a watchdog-level failure.

## Summary of measured headline numbers

| Area | Headline figure | Basis |
|---|---|---|
| Recoverability | Restore test: ~22ms total for a 236-byte artefact; `company/data/*.db` (2.1MB+) has NO off-machine copy | measured + confirmed gitignore |
| Security | 2/2 secrets clean (gitignored, 600 perms, never in git history); 1 medium + 1 low finding (stale servers, CORS) | measured |
| Performance | 19 customers, ~470s/run, 2.9MB output; 2 confirmed O(n²) loops in `run_phase2b.py` | measured (runtime/size) + code-verified (loops) |
| Availability | 2 crash-loop episodes + 1 ~22min binary-path outage in the last week; 6 daemons share one NTFY-env SPOF; whole stack single-machine | measured from logs |
