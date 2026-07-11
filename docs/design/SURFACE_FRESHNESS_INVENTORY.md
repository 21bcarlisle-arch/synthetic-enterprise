# SURFACE_FRESHNESS_INVENTORY — Phase 1 (DISCOVER): full surface inventory + root-cause

**Status:** DISCOVER only, no code changed. Answers `docs/staging/in_progress/SURFACE_FRESHNESS_CLASS_FIX.md`
Phase 1. Read-only investigation, 2026-07-11.

## Headline

- **15 rendered pages, 47 `site/data/*.json` files. Zero of them are covered by any
  freshness-alarming mechanism.** No code anywhere in `tools/` or `background/` reads a
  `generated_at`/`last_updated` field back out of a deployed JSON file and compares it to
  wall-clock time. The things that *look* like freshness checks (`deadmans_switch.py`,
  `health_check.py`, `sanity_daemon.py`) all check something else entirely (see §4).
- Only **6 of 16 top-level `site/data/*.json` files even carry a timestamp field**
  (`agent_status.json`, `capabilities.json`, `method.json`, `platform.json`,
  `saas_coverage.json`, `system_status.json`). The other 10 — including `dashboard.json`,
  `supplier.json`, `customers.json`, `sim_data.json`, `phases.json` — have nothing to check
  even if a detector existed.
- **Two pages are worse than the platform-page incident that triggered this task, and
  neither has a generator at all**: `site/timeline/index.html` and
  `site/staging-status/index.html` are fully static, hand-baked snapshots frozen at
  "Phase 260" / 2026-06-26, never touched since except for unrelated nav/comments-widget
  edits. They are ~15 days stale as of today (2026-07-11) and structurally cannot be
  detected as stale because no generator, trigger, or timestamp exists for them to compare
  against.
- The platform/agent-health miss has a precise, evidenced root cause: see §5. It is a
  **recurrence of the R11 class** (CLAUDE.md), not a new bug — the same
  "release/gate triggers nothing" shape, now hitting a different generator.

---

## 1. Page → data file(s)

| Page | Fetches | Notes |
|---|---|---|
| `site/index.html` | `dashboard.json`, `method.json`, `phases.json`, `supplier.json` | cache-busted (`?t=`) on 3/4 |
| `site/customers/index.html` | `case_studies.json`, `customers.json`, `customers/*.json` (per-record), `weather.json` | |
| `site/method/index.html` | `method.json` | cache-busted |
| `site/platform/index.html` | `capabilities.json`, `platform.json`, `saas_coverage.json` | cache-busted — **does not fetch `agent_status.json` or `system_status.json` directly by this name**; see §5 for where those actually render |
| `site/project/index.html` | `agent_status.json`, `dashboard.json`, `maturity_map.json`, `phases.json`, `system_status.json` | cache-busted on the two status files — **this is the actual agent-health/System-tab page**, not `platform/` |
| `site/sim/index.html` | `customer_sample.json`, `dashboard.json`, `sim_data.json`, `weather.json` | absolute paths (`/data/...`) |
| `site/simplified/index.html` | `simplified.json` | cache-busted |
| `site/supplier/index.html` | `dashboard.json`, external `skynet-1.taila062fa.ts.net/query` (risk-committee live query, out of scope for this doc) | |
| `site/shadow/index.html` | — | **no client fetch.** Server-side baked by `tools/generate_shadow_html.py`; JSON filenames appear only as inert `<a href>` text/citations |
| `site/shadow/customers/index.html` | — | same baked pattern; JSON refs are citation links only |
| `site/shadow/project/index.html` | — | same |
| `site/shadow/sim/index.html` | — | same |
| `site/shadow/supplier/index.html` | — | same |
| `site/timeline/index.html` | **none — data is hardcoded inline** (`const PHASES=[...]` literal array, ends at Phase 259, dated up to 2026-06-26) | **orphaned, see §6** |
| `site/staging-status/index.html` | **none — entire table body is static HTML**, only loads `../shared/director-comments.js` (a comment-*posting* widget that POSTs to ntfy.sh, not a data fetch) | **orphaned, see §6** |

`site/simplified/index.html` and `site/method/index.html` are effectively narrative-with-a-run-data-subobject pages (see tolerance notes in §7).

---

## 2 & 3. Data file → generator → trigger

Trigger legend: **WIRED** = imported and called inside `background/process_run_complete.py`'s
regeneration chain (still subject to the change-detection gate, §5, unless noted).
**DAEMON-LIVE** = written directly and immediately by a running background process, no
generator step. **UNWIRED** = generator exists but nothing calls it automatically.
**NONE** = no generator found; hand-authored or frozen.

| `site/data/*.json` | Generator | Trigger |
|---|---|---|
| `dashboard.json` | `tools/generate_dashboard_data.py` | WIRED |
| `phases.json` | `tools/generate_phases_json.py` | WIRED |
| `supplier.json` | `tools/generate_supplier_json.py` | WIRED |
| `method.json` | `tools/generate_method_data.py` (+ `generate_track_record_scorecard.py` folded in before it) | WIRED |
| `capabilities.json` | `tools/generate_capabilities_json.py` | WIRED |
| `maturity_map.json` | `tools/generate_maturity_map_data.py` | WIRED |
| `simplified.json` | `tools/generate_simplified_data.py` | WIRED |
| `platform.json` | `tools/generate_platform_data.py` | WIRED |
| `saas_coverage.json` | `tools/generate_saas_coverage_data.py` | WIRED |
| `system_status.json` | `tools/generate_system_status.py` | WIRED — but see §5, this is the broken one |
| `customers.json` | `tools/generate_customers_json.py` | WIRED |
| `customers/*.json` (22 files) + `_index.json` | `tools/generate_customer_data.py` | WIRED |
| `case_studies.json` | `tools/generate_case_study_recommender.py` | WIRED |
| `sim_data.json` | `tools/generate_sim_data.py` | WIRED |
| `customer_sample.json` | `tools/generate_customer_sample.py` | WIRED |
| `weather.json` | `tools/fetch_weather_data.py` (`generate_weather_data`) | WIRED (also has an independent rolling-refresh path, `background/refresh_elexon_ssp_rolling.py`, for the underlying Elexon cache it partly draws from — that one **is** in the same pipeline hook too, not a separate cadence) |
| `agent_status.json` | `background/agent_status.py::update_agent_status()` / `update_sim_metrics()` | **DAEMON-LIVE** — every background daemon (`sim_runner`, `staging_watcher`, `session_watchdog`, `supervisor`, `sanity_daemon`, `background_worker`, `dispatcher`, `ntfy_responder`, `director_comments`, `discovery_agent`, `autonomous_runner`) calls this after every meaningful action, writing straight to `site/data/agent_status.json` with no generator step in between |
| `site/data/snapshots/*.json` (8 files) | `tools/generate_snapshot.py` | **UNWIRED** — not imported anywhere, self-contained script only. All 8 existing files are dated 2026-06-30, confirming it hasn't run since |

**Every file above except `agent_status.json` and the snapshots directory shares one trigger:
`background/process_run_complete.py`, invoked by `background/sim_runner.py` after each ~8-minute
simulation run completes.** That single shared trigger, gated the same way for all of them, is
the structural issue — see §5.

---

## 4. Existing "freshness" mechanisms — what they actually cover

Grepped broadly for "stale", "freshness", "CLAIM_EQUALS_PIXEL", "generated_at" comparisons.
Found three mechanisms, none of which check deployed-surface data age:

| Mechanism | What it actually checks | Covers site/data freshness? |
|---|---|---|
| `background/health_check.py::_check_staging_age()` | Age of unactioned `from_rich_*.md` staging messages (>2h warning) | No — staging inbox only |
| `background/deadmans_switch.py` | Idle time since last observability-log activity + unprocessed staging queue depth (90min BLOCKED threshold) | No — agent activity/liveness, not data content |
| `background/sanity_daemon.py` | Qwen-skeptic plausibility audits of rendered content (bills, numbers) — a correctness check, redesigned 2026-07-11 per `SANITY_TRIAGE_2026_07_11.md` | No — correctness of values, not their age |
| `docs/staging/done/CLAIM_EQUALS_PIXEL.md` (R11 in CLAUDE.md) | A **rule**, not running code: "verify to the rendered value," "no orphan transitions." No enforcement mechanism was ever built from it — it's a manual-discipline checklist item, not an automated gate | No — process discipline, not a running check |

**Conclusion: the detector the staging doc describes ("did not alarm on a 1.5-day-old stamp")
does not exist as code anywhere.** It isn't that an existing check has a gap in its coverage
list — there is no check to have a gap. R11 exists as a written rule that a human/agent is
supposed to apply manually at phase close, which is exactly the failure mode it was meant to
prevent recurring.

---

## 5. Root-cause: the platform/agent-health miss

The director's complaint was about `site/project/index.html` (the actual System-tab / agent-health
surface — `site/platform/index.html` is a different page, capability coverage, and was not the
one at issue). It fetches `agent_status.json` and `system_status.json`.

**`agent_status.json` is written correctly and immediately** by every daemon's
`update_agent_status()` call — this file is never more than seconds stale *on disk locally*.
**`system_status.json` (session history, staging queue, commit-cadence chart) is only ever
regenerated inside `process_run_complete.py`'s chain**, which runs after every sim-run
completion — but that whole chain is gated:

```
# background/process_run_complete.py, line ~750
fingerprint = _run_fingerprint(data)      # keys on net_margin, treasury, retention counts, UTC date...
last_fp = _read_last_fingerprint()
if last_fp == fingerprint and not administration_event and not forced:
    _archive_marker(marker)
    log("SKIP (change-detection gate): identical to last processed run ...")
    return 0   # <-- exits BEFORE any of the 20+ generators run, including gen_system_status(),
               #     and BEFORE the git commit/push step that would deploy agent_status.json's
               #     already-fresh local write
```

`_run_fingerprint()` includes the calendar date specifically so at least one run per UTC day is
guaranteed to pass the gate — but that only bounds staleness to <24h *in principle*. In practice,
grepping `docs/observability/sim-runner-log.md` for `Generated site/data/system_status.json`
shows an **18-hour gap with zero regeneration**: last successful run 2026-07-10 06:08 UTC, next
successful run 2026-07-11 00:07 UTC — because the business's headline net margin
(`£1,523,825`) held flat across that entire window, so every run in between hit the SKIP branch.
The log tail as of this investigation (afternoon 2026-07-11) shows the same pattern resuming:
dozens of consecutive `SKIP (change-detection gate): identical ... [net=£1,523,825]` lines from
12:56 UTC onward.

Two compounding effects:

1. **The gate is keyed on financial-result equality, but it blocks unrelated surfaces.**
   `system_status.json`'s content (git commit cadence, session start/stop history, staging
   queue) has nothing to do with `total_net_gbp`. When the sim's outputs are flat — which is
   now common, since the business has converged — the gate silently freezes ~14 unrelated
   generators (customers.json, shadow HTML, capabilities.json, etc., not just system_status)
   for as long as the flat streak lasts.
2. **Even where `agent_status.json` stays fresh locally (daemon-live writes), it never reaches
   the live site during a SKIP streak**, because `_process()` returns before reaching the git
   commit/push step that both `deploy-pages.yml` (Cloudflare Pages, triggers on push to
   `site/**`) and the GitHub Pages mirror depend on. A file can be seconds-fresh on disk and
   still be a day-and-a-half stale on poesys.net, because "committed" — let alone "pushed" — is
   the actual gate, not "generated."

This is **the same failure class CLAUDE.md's R11 already names** ("a release whose effect is
nothing is a defect" — the hedge-fix publish-hold incident, fixed narrowly for that one path
via `FORCE_REPUBLISH_FLAG`). `FORCE_REPUBLISH_FLAG` only fires on a hold *release*; it does
nothing for the much more common case of "N consecutive runs with an unchanged financial
fingerprint." The class was patched at the instance level (one flag, one trigger condition),
not closed structurally — exactly what R10 says not to do, and exactly what has now recurred.

---

## 6. Worse, undetectable-by-construction: two fully orphaned pages

`site/timeline/index.html` and `site/staging-status/index.html` have **no fetch call and no
generator at all**. Both were created in commit `356d984e` ("Phase 260: Strategic Coherence
Infrastructure", ~2026-06-26) and have only been touched since for unrelated nav-bar/
director-comments-widget edits (`git log` confirms no content-regenerating commit since
creation).

- `site/timeline/index.html`: phase-history chart data is a literal JS array,
  `const PHASES=[...]`, hardcoded in the page markup, ending at "Phase 259" / 2026-06-26.
  The project is now far past that (M1/M2/W1-numbered epoch work as of 2026-07-11) — this
  page has been silently wrong for roughly two weeks.
- `site/staging-status/index.html`: entire staging-queue table is static HTML text, header
  literally reads `Generated: 2026-06-26 13:51 UTC — Phase 260`, rows say things like "3m ago"
  for events that are now ~15 days old.

These cannot be caught by *any* freshness mechanism built around comparing a `generated_at`
field, because no such field, generator, or regeneration path exists for either page — the
gap isn't a miss in coverage, it's a total absence of the underlying capability. This is the
single highest-risk item in the inventory: worse staleness (~15 days vs. ~1.5 days) than the
incident that triggered this task, on pages nobody has apparently looked at recently enough to
notice.

`site/data/snapshots/*.json` (8 files, generator `tools/generate_snapshot.py`) is a related but
lower-risk case: the generator exists but is never called automatically (not imported anywhere),
and all 8 existing files are dated the same day, 2026-06-30, confirming it was run by hand a
handful of times and never since. Lower risk because these are explicitly point-in-time
snapshots (their whole purpose is to be a frozen record), not surfaces claiming to show "now" —
but nothing currently distinguishes "intentionally archival" from "silently abandoned" in the
data itself.

---

## 7. Tolerance classification

| Class | Tolerance | Surfaces |
|---|---|---|
| **Live ops** (minutes) | `agent_status.json` (daemon status/heartbeats), `system_status.json`'s `session_history`/`staging_queue`/`commit_burn` sub-objects, `site/staging-status/index.html`'s entire content |
| **Run data** (per sim run, ~8min cadence) | `dashboard.json`, `supplier.json`, `sim_data.json`, `customer_sample.json`, `customers.json` + per-customer files, `case_studies.json`, `weather.json`, `simplified.json`, `maturity_map.json`, `phases.json`, `saas_coverage.json`, `method.json`'s `track_record` sub-object, all shadow-page HTML, `site/timeline/index.html`'s phase-count chart |
| **Narrative/design copy** (days is fine) | `method.json`'s static prose fields, `capabilities.json`'s descriptive text, `platform.json`'s narrative sections |
| **Archival / point-in-time by design** (no tolerance — not "current" data) | `site/data/snapshots/*.json` |

Note the mismatch already flagged in §5/§6: `system_status.json` bundles a live-ops sub-object
(`session_history`, `commit_burn`) inside a file whose only trigger is run-data cadence, and
`site/staging-status/index.html` — pure live-ops content — has no trigger of any tolerance class
at all.

---

## 8. Uncovered surfaces — the explicit list requested by the staging doc

**Zero surfaces currently have a working freshness alarm.** Ranked by evidence of actual harm:

1. `site/staging-status/index.html` — orphaned, no generator, ~15 days stale, live-ops content
2. `site/timeline/index.html` — orphaned, no generator, ~15 days stale, hardcoded phase data
3. `system_status.json` → `site/project/index.html` System tab — wired but gated; proven 18h
   silent staleness window this week alone (the incident that triggered this task)
4. `agent_status.json` deploy lag → same page — daemon-fresh locally, but blocked from
   reaching the live site by the same gate as #3 whenever it's in a SKIP streak
5. `site/data/snapshots/*.json` — generator exists, unwired, last ran 2026-06-30 (lower risk:
   archival by design, but currently indistinguishable from "abandoned")
6. All other 12 WIRED generators (`dashboard.json`, `customers.json`, `phases.json`,
   `capabilities.json`, `maturity_map.json`, `simplified.json`, `platform.json`,
   `saas_coverage.json`, `case_studies.json`, `sim_data.json`, `customer_sample.json`,
   `weather.json`, shadow HTML) — same change-detection gate as #3, so all share the same
   *mechanism* of risk even though none has a proven multi-hour incident on record the way
   `system_status.json` does. They're "currently lucky," not "safe."
7. 10 of 16 top-level JSON files have no timestamp field to check even if a detector existed
   (`dashboard.json`, `phases.json`, `supplier.json`, `customers.json`, `customer_sample.json`,
   `sim_data.json`, `simplified.json`, `maturity_map.json`, `case_studies.json`, `weather.json`)

---

## 9. Recommendation for Phase 2 (build), ordered by risk/impact

1. **Decouple live-ops data from the financial change-detection gate.** The gate's premise
   ("two runs with the same fingerprint would regenerate byte-identical business surfaces") is
   only true for run-data surfaces. `system_status.json` (or a split-out live-ops file covering
   agent/session/commit data) needs its own trigger independent of `total_net_gbp` equality —
   e.g. a short-interval daemon tick, or simply excluding it from the gate and always
   regenerating+committing it on every process_run_complete invocation regardless of fingerprint
   match. This is the direct fix for the incident that opened this task and the highest-recurrence-risk
   item (R10: fix the class, not the instance — the gate's scope, not `system_status.json`
   specifically).
2. **Give `site/timeline/index.html` and `site/staging-status/index.html` real generators wired
   into the pipeline**, replacing the hardcoded/static content. These are currently worse than
   the incident that triggered this task and are invisible to any future detector by
   construction until a generator exists to compare against.
3. **Build the actual freshness-alarm mechanism** (the thing §4 shows doesn't exist): a check —
   daemon or CI step — that reads each surface's `generated_at`, compares to its declared
   tolerance class (§7), and NTFYs (not logs) on breach. Prerequisite: add a `generated_at`
   field to the 10 JSON files that currently lack one, or the alarm has nothing to read for
   60%+ of the top-level surface.
4. Lower priority: wire or explicitly retire `tools/generate_snapshot.py` (currently silently
   abandoned since 2026-06-30) — decide if snapshots are an intentional archival feature (add a
   scheduled trigger) or dead code (remove the unused files/generator).
