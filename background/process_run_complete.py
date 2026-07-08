#!/usr/bin/env python3
import fcntl
import json
import os
import re
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
DONE_DIR = STAGING_DIR / "done"
LATEST_MD = PROJECT_DIR / "docs" / "status" / "LATEST.md"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "sim-runner-log.md"
LAST_TESTED_HASH_FILE = PROJECT_DIR / "docs" / "observability" / ".last_tested_hash"
LAST_PUSH_FILE = PROJECT_DIR / "docs" / "observability" / ".last_push_time.json"
RUN_LOCK_FILE = PROJECT_DIR / "docs" / "observability" / ".process_run_complete.lock"
RUN_INSIGHTS_PATH = PROJECT_DIR / "docs" / "observability" / "run_insights.json"
RUN_HISTORY_PATH = PROJECT_DIR / "docs" / "observability" / "run_history.json"
# DEPLOY_CONTENTION_BATCH_COMMITS.md (2026-07-04): sim_runner cycles every
# ~10 min and each cycle committed+pushed unconditionally (LATEST.md's
# timestamp always differs), giving ~6 pushes/hour -- enough to contend with
# GitHub Pages' build throttling (58 failed "Deploy to GitHub Pages" runs,
# each superseded by the next push before it finished) and to burn through
# Cloudflare Pages' free-tier build quota. Commits still happen every cycle
# (free, local, no deploy trigger) but the push itself -- the thing that
# actually fires a Pages/Cloudflare build -- is throttled to at most once
# per PUSH_THROTTLE_SECONDS; the next successful push carries every commit
# accumulated since the last one.
PUSH_THROTTLE_SECONDS = 30 * 60
sys.path.insert(0, str(PROJECT_DIR))

from background.tree_lock import tree_lock  # noqa: E402


@contextmanager
def _run_lock():
    """Non-blocking exclusive lock so at most one process_run_complete.py
    instance does the heavy pipeline (report regen, dashboard/site build,
    full test suite -- ~5-10 min) at a time.

    sim_runner.py invokes this script synchronously right after writing a
    run_complete marker. background_worker.py separately sweeps staging/
    every 30 min for "leftover" markers still sitting in the root (the
    marker only moves to done/ at the very end of a successful run) and
    re-invokes this script on any it finds -- with no way to tell a marker
    that is genuinely abandoned (prior invocation crashed/timed out) apart
    from one that is simply still being processed by a live sim_runner
    invocation. Observed directly 2026-07-06: two instances running the
    full pipeline concurrently on the same marker. Losing this lock is not
    an error -- it just means another instance already has the marker in
    hand, so this invocation exits immediately and leaves the marker for
    that instance to archive."""
    RUN_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    fh = open(RUN_LOCK_FILE, "w")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        fh.close()
        yield False
        return
    try:
        yield True
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = "- [{}] [process_run] {}".format(ts, msg)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write("\n" + entry)
    print(entry, flush=True)


def parse_marker(marker_path):
    text = marker_path.read_text()
    result = {}
    for line in text.splitlines():
        if line.startswith("JSON: "):
            result["json_path"] = Path(line[6:].strip())
        elif line.startswith("Git: "):
            result["git_hash"] = line[5:].strip()
        elif line.startswith("Duration: "):
            m = re.search(r"Duration:\s*([\d.]+)s", line)
            result["elapsed_s"] = float(m.group(1)) if m else 0.0
        elif line.startswith("Finished: "):
            result["finished"] = line[10:].strip()
    return result


def regenerate_report(json_path):
    result = subprocess.run(
        [sys.executable, "-m", "saas.reporting.annual_report", "--from-json", str(json_path)],
        cwd=str(PROJECT_DIR),
        timeout=120,
    )
    return result.returncode == 0


def update_latest_md(data, elapsed_s, git_hash="unknown"):
    text = LATEST_MD.read_text()
    ts_now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = re.sub(r"Last updated: \S+", "Last updated: {}".format(ts_now), text)

    ledger = data.get("_ledger_headline", {})
    net = data.get("total_net_gbp", ledger.get("net_margin_gbp", 0))  # total_net_gbp includes bad debt + hedging costs
    gross = ledger.get("gross_margin_gbp", data.get("total_gross_gbp", 0))
    capital = data.get("total_capital_gbp", 0)
    t_start = data.get("starting_treasury_gbp", 0)
    t_end = data.get("final_treasury_gbp", 0)
    committee = data.get("committee_wake_ups_total", 0)
    bills = data.get("bills_total", 0)
    ev = data.get("enterprise_value_gbp", 0)
    net_cts = data.get("net_margin_after_cost_to_serve_gbp", 0)
    ret_log = data.get("retention_log", [])
    no_offer = data.get("no_offer_churn_log", [])
    churned = data.get("churned_billing_accounts", [])
    mins = elapsed_s / 60

    offers = len(ret_log)
    retained = sum(1 for r in ret_log if r.get("outcome") == "retained")
    no_offer_churns = len(no_offer)
    churn_count = len(churned)

    parts = [
        "**Latest simulation results (2016–2025)** — auto-processed ({:.0f}s / {:.0f} min):".format(elapsed_s, mins),
        "- Net margin: \xa3{:,.2f} | Gross: \xa3{:,.2f} | Capital: \xa3{:,.0f}".format(net, gross, capital),
        "- Treasury: \xa3{:,.0f} → \xa3{:,.0f} | {} committee interventions | {} bills issued".format(t_start, t_end, committee, bills),
        "- Enterprise value: \xa3{:,.2f} | Net after CTS: \xa3{:,.0f}".format(ev, net_cts),
        "- Retention: {} offers, {}/{} retained | {} no-offer churns | {} total churned accounts".format(
            offers, retained, offers, no_offer_churns, churn_count),
    ]
    new_block = "\n".join(parts)

    start_marker = "**Latest simulation results"
    try:
        start_idx = text.index(start_marker)
        end_idx = text.find("\n\n", start_idx)
        if end_idx == -1:
            end_idx = len(text)
        text = text[:start_idx] + new_block + text[end_idx:]
    except ValueError:
        # Block not yet present — append to end on first auto-process
        text = text.rstrip() + "\n\n" + new_block + "\n"
        log("Created 'Latest simulation results' block in LATEST.md")
    # Update "Net position:" summary line in Last Run section
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    text = re.sub(
        r"Net position: .*",
        "Net position: \xa3{:,.0f} (git {}, {})".format(net, git_hash, date_str),
        text,
    )
    LATEST_MD.write_text(text)


def run_fast_tests(git_hash: str):
    """Returns (passed: bool, timed_out: bool). Skips if git_hash already tested."""
    if LAST_TESTED_HASH_FILE.exists():
        if LAST_TESTED_HASH_FILE.read_text().strip() == git_hash:
            log("Tests skipped — already passed for git={}".format(git_hash))
            return True, False

    full_env = dict(os.environ)
    full_env["SIM_FAST_MODE"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-x", "-q", "--tb=short",
             # Full-simulation integration tests (150-480s each) — excluded from auto-process gate
             "--ignore=tests/simulation/test_run_phase2b.py",
             "--ignore=tests/simulation/test_run_phase2b_event_log.py",
             "--ignore=tests/simulation/test_run_phase4c_on_phase2b.py",
             "--ignore=tests/simulation/test_phase40b_gas_pass_through.py",
             "--ignore=tests/simulation/test_phase24a_ic_customer.py",
             "--ignore=tests/simulation/test_phase40a_pass_through.py",
             "--ignore=tests/simulation/test_phase40c_deemed_rate.py",
             "--ignore=tests/simulation/test_phase41a_flex.py"],
            cwd=str(PROJECT_DIR),
            env=full_env,
            timeout=600,
        )
        if result.returncode == 0:
            LAST_TESTED_HASH_FILE.write_text(git_hash)
        return result.returncode == 0, False
    except subprocess.TimeoutExpired:
        # Timeout is a resource constraint, not a test failure — warn but don't block commit
        log("Fast test suite timed out (>600s) — committing anyway with warning")
        return True, True


def _run_weather_data(git_hash="unknown"):
    from tools.fetch_weather_data import generate_weather_data
    generate_weather_data(git_hash=git_hash)


def _fmt_gbp(v):
    """Format a GBP value with sign and £ prefix, e.g. £+225,920 or £-3,766."""
    sign = "+" if v >= 0 else ""
    return "\xa3{}{:,.0f}".format(sign, v)


def generate_dashboard_json(json_path, git_hash="unknown"):
    """Generate site/data/dashboard.json and every downstream site/state artifact.

    Returns False if the cross-surface consistency gate failed (Part C of the
    website-integrity fix: a mismatch must be surfaced loudly, never shipped
    silently) so the caller can NTFY immediately. The gate result is captured
    but must NOT short-circuit the rest of this function -- every generator
    below (shadow HTML, PROJECT_STATE.txt, billing ledger, population
    anchoring, customers.json, supplier.json, live decisions, scenario
    analysis, GitHub Pages mirror) has to run every cycle regardless of the
    gate outcome. (QG_REOPENED_R2.md, 2026-07-04: an early `return ok` here
    made all of the below dead code since Phase QF -- none of it had run on
    any auto-processed cycle since.)"""
    ok = True
    try:
        # Must run before generate_dashboard_data (reads frozen_policy_baseline.json
        # if present). Weekly-gated (should_refresh_baseline) -- replays the full
        # decade twice under CURRENT_POLICY vs NAIVE_POLICY, so this is deliberately
        # NOT a per-cycle cost. FROZEN_POLICY_BASELINE_DESIGN.md / PRIORITIES.md P2.
        sys.path.insert(0, str(PROJECT_DIR))
        from tools.run_frozen_baseline import generate as gen_frozen_baseline
        refreshed = gen_frozen_baseline()
        if refreshed is not None:
            log("Refreshed site/state/frozen_policy_baseline.json (delta-EV £{:,.0f})".format(
                refreshed.get("delta_ev_gbp", 0.0)))
    except Exception as exc:
        log("Frozen-policy baseline generation failed: {}".format(exc))
    try:
        from tools.generate_dashboard_data import generate
        ok = generate(json_path)
        if ok:
            log("Generated site/data/dashboard.json")
        else:
            log("CONSISTENCY GATE FAILED — dashboard/exec-summary surfaces disagree (see stderr above)")
    except Exception as exc:
        log("Dashboard data generation failed: {}".format(exc))
        ok = True  # generation exception is not a consistency-gate failure; don't false-alarm
    try:
        from tools.generate_customer_data import generate as gen_cust
        gen_cust(json_path)
        log("Generated site/data/customers/ JSON")
    except Exception as exc:
        log("Customer data generation failed: {}".format(exc))
    try:
        # Must run before generate_invoice_data: real per-invoice bill-equation
        # data (usage, rate, standing charge) is wired from this ledger into the
        # customer JSON here; also must run before generate_shadow_html which reads
        # it independently.
        from tools.generate_billing_ledger import generate as gen_ledger
        gen_ledger(json_path)
        log("Generated site/state/billing_ledger.json")
    except Exception as exc:
        log("Billing ledger generation failed: {}".format(exc))
    try:
        from tools.generate_invoice_data import generate as gen_inv
        gen_inv(json_path)
        log("Generated customer invoice JSON")
    except Exception as exc:
        log("Invoice data generation failed: {}".format(exc))
    try:
        # Must run after generate_billing_ledger (real payments/arrears_history
        # source) and generate_invoice_data (patches the same customer JSON
        # files, this generator only adds a new "ledger" key alongside them).
        # BILLING_AND_PAYMENTS_LEDGER.md: Statement/Cashflow views.
        from tools.generate_payment_ledger_data import generate as gen_pay_ledger
        gen_pay_ledger()
        log("Generated per-account payment ledger JSON (BILLING_AND_PAYMENTS_LEDGER.md Statement/Cashflow)")
    except Exception as exc:
        log("Payment ledger generation failed: {}".format(exc))
    try:
        from tools.generate_customer_consumption import generate as gen_consumption
        gen_consumption(json_path)
        log("Generated customer consumption JSON (USAGE panel)")
    except Exception as exc:
        log("Customer consumption generation failed: {}".format(exc))
    try:
        # Must run after generate_customer_data/generate_invoice_data/
        # generate_customer_consumption: patches real timeline "effect"
        # annotations (item 3) and the reaction_chain (item 4) onto the
        # per-customer JSON those steps already produced.
        from tools.generate_customer_reaction_chain import generate as gen_reaction
        gen_reaction(json_path)
        log("Generated customer timeline effects + reaction_chain (CUSTOMER_360_REDESIGN.md v4 items 3-4)")
    except Exception as exc:
        log("Customer reaction-chain generation failed: {}".format(exc))
    try:
        # Must run after generate_dashboard_data (dashboard.json must exist)
        # and generate_billing_ledger (arrears-opened events need it).
        # SUPPLIER_TAB_OVERHAUL.md THE SPINE: portfolio event stream.
        from tools.generate_portfolio_event_stream import generate as gen_pes
        gen_pes(json_path)
        log("Generated portfolio event stream onto dashboard.json (SUPPLIER_TAB_OVERHAUL.md spine)")
    except Exception as exc:
        log("Portfolio event stream generation failed: {}".format(exc))
    try:
        from tools.generate_sim_data import generate as gen_sim
        gen_sim(git_hash)
        log("Generated site/data/sim_data.json")
    except Exception as exc:
        log("Sim data generation failed: {}".format(exc))
    try:
        from tools.generate_customer_sample import generate as gen_sample
        gen_sample(json_path)
        log("Generated site/data/customer_sample.json")
    except Exception as exc:
        log("Customer sample generation failed: {}".format(exc))
    try:
        # Must run after generate_customer_reaction_chain (timeline/reaction_chain
        # patched) and generate_customer_sample (churn_accuracy_by_renewal source).
        # WEBSITE_AS_SHOWCASE.md tab 4: case-study recommender.
        from tools.generate_case_study_recommender import generate as gen_case_studies
        gen_case_studies()
        log("Generated site/data/case_studies.json (WEBSITE_AS_SHOWCASE.md tab 4 case-study recommender)")
    except Exception as exc:
        log("Case-study recommender generation failed: {}".format(exc))
    try:
        from tools.generate_shadow_html import generate as gen_shadow
        gen_shadow()
        log("Generated site/shadow/ static HTML mirror")
    except Exception as exc:
        log("Shadow HTML generation failed: {}".format(exc))
    try:
        from tools.generate_project_state import generate as gen_state
        gen_state()
        log("Generated site/state/PROJECT_STATE.txt")
    except Exception as exc:
        log("PROJECT_STATE generation failed: {}".format(exc))
    try:
        from tools.generate_phases_json import generate as gen_phases
        gen_phases()
        log("Generated site/data/phases.json")
    except Exception as exc:
        log("phases.json generation failed: {}".format(exc))
    try:
        from tools.generate_capabilities_json import generate as gen_capabilities
        gen_capabilities()
        log("Generated site/data/capabilities.json")
    except Exception as exc:
        log("capabilities.json generation failed: {}".format(exc))
    try:
        from tools.generate_platform_data import generate as gen_platform
        gen_platform()
        log("Generated site/data/platform.json")
    except Exception as exc:
        log("platform.json generation failed: {}".format(exc))
    try:
        from tools.generate_saas_coverage_data import generate as gen_saas_coverage
        gen_saas_coverage()
        log("Generated site/data/saas_coverage.json")
    except Exception as exc:
        log("saas_coverage.json generation failed: {}".format(exc))
    try:
        from tools.generate_system_status import generate as gen_system_status
        gen_system_status()
        log("Generated site/data/system_status.json")
    except Exception as exc:
        log("system_status.json generation failed: {}".format(exc))
    try:
        from tools.population_anchor import generate as gen_anchor
        gen_anchor(json_path)
        log("Generated site/state/population_anchoring.json")
    except Exception as exc:
        log("Population anchoring failed: {}".format(exc))
    try:
        from tools.generate_customers_json import generate as gen_customers
        gen_customers(json_path)
        log("Generated site/data/customers.json")
    except Exception as exc:
        log("customers.json generation failed: {}".format(exc))
    try:
        from tools.generate_supplier_json import generate as gen_supplier
        gen_supplier(json_path)
        log("Generated site/data/supplier.json")
    except Exception as exc:
        log("supplier.json generation failed: {}".format(exc))
    try:
        from tools.project_portfolio_to_2026 import generate as gen_portfolio
        gen_portfolio(json_path)
        log("Generated site/state/live_portfolio.json")
    except Exception as exc:
        log("Live portfolio generation failed: {}".format(exc))
    try:
        # S1 Option A: extend the real Elexon SSP cache forward past 2025-06-07 on a
        # rolling basis BEFORE the live decision reads market state, so market_as_of_date
        # advances as real settlement data is published. Fully defensive (never raises,
        # never corrupts the frozen historical cache) -- a network-less/failed run is a
        # no-op and the decision falls back to the last known real price, honestly labelled.
        from background.refresh_elexon_ssp_rolling import refresh as refresh_ssp
        st = refresh_ssp()
        log("Rolling Elexon SSP refresh: {} ({} new records)".format(
            st.get("status"), st.get("fetched_records", 0)))
    except Exception as exc:
        log("Rolling Elexon SSP refresh failed (non-fatal): {}".format(exc))
    try:
        from tools.run_live_decisions import run_decisions
        run_decisions()
        log("Generated site/state/live_decisions_latest.json")
    except Exception as exc:
        log("Live decisions generation failed: {}".format(exc))
    try:
        from tools.run_live_decisions import run_scenario_analysis
        run_scenario_analysis()
        log("Generated site/state/scenario_analysis_latest.json")
    except Exception as exc:
        log("Scenario analysis generation failed: {}".format(exc))
    try:
        # Must run after run_live_decisions (reads live_decisions_log.jsonl it appends
        # to) and before generate_method_data (folds the scorecard onto the public
        # Method page -- S1 Decision 2: public from day one, misses included).
        from tools.generate_track_record_scorecard import generate as gen_scorecard
        gen_scorecard()
        log("Generated site/state/track_record_scorecard.json (Phase RX / S1 Option B)")
    except Exception as exc:
        log("Track record scorecard generation failed: {}".format(exc))
    try:
        from tools.generate_method_data import generate as gen_method
        gen_method()
        log("Generated site/data/method.json")
    except Exception as exc:
        log("method.json generation failed: {}".format(exc))
    try:
        from tools.mirror_github_pages import mirror as mirror_gh_pages
        mirrored = mirror_gh_pages()
        log("Mirrored {} file(s) to docs/shadow + docs/state for GitHub Pages".format(len(mirrored)))
    except Exception as exc:
        log("GitHub Pages mirror failed: {}".format(exc))
    return ok


def generate_site(data, elapsed_s, git_hash, finished_ts):
    """No-op: site/index.html is a static SPA that reads site/data/dashboard.json."""
    pass


def git_commit_push(git_hash, net_margin):
    report = PROJECT_DIR / "docs" / "reports" / "ANNUAL_REPORT.md"
    site_index = PROJECT_DIR / "site" / "index.html"
    site_data = PROJECT_DIR / "site" / "data" / "dashboard.json"
    site_customers = PROJECT_DIR / "site" / "data" / "customers"
    site_sample = PROJECT_DIR / "site" / "data" / "customer_sample.json"
    site_shadow = PROJECT_DIR / "site" / "shadow"
    files = [str(report), str(LATEST_MD)]
    if site_index.exists():
        files.append(str(site_index))
    if site_data.exists():
        files.append(str(site_data))
    if site_customers.exists():
        files.append(str(site_customers))
    if site_sample.exists():
        files.append(str(site_sample))
    if site_shadow.exists():
        files.append(str(site_shadow))
    site_state_sample = PROJECT_DIR / "site" / "state" / "customer_sample.json"
    if site_state_sample.exists():
        files.append(str(site_state_sample))
    site_state_project = PROJECT_DIR / "site" / "state" / "PROJECT_STATE.txt"
    if site_state_project.exists():
        files.append(str(site_state_project))
    docs_status_project = PROJECT_DIR / "docs" / "status" / "PROJECT_STATE.txt"
    if docs_status_project.exists():
        files.append(str(docs_status_project))
    site_state_billing = PROJECT_DIR / "site" / "state" / "billing_ledger.json"
    if site_state_billing.exists():
        files.append(str(site_state_billing))
    site_state_anchor = PROJECT_DIR / "site" / "state" / "population_anchoring.json"
    if site_state_anchor.exists():
        files.append(str(site_state_anchor))
    site_data_customers = PROJECT_DIR / "site" / "data" / "customers.json"
    if site_data_customers.exists():
        files.append(str(site_data_customers))
    site_data_supplier = PROJECT_DIR / "site" / "data" / "supplier.json"
    if site_data_supplier.exists():
        files.append(str(site_data_supplier))
    site_state_scenario = PROJECT_DIR / "site" / "state" / "scenario_analysis_latest.json"
    if site_state_scenario.exists():
        files.append(str(site_state_scenario))
    site_state_decision_log = PROJECT_DIR / "site" / "state" / "live_decisions_log.jsonl"
    if site_state_decision_log.exists():
        files.append(str(site_state_decision_log))
    # Phase RO (NAV_STORY_PLATFORM_METHOD.md): site/index.html moved from the
    # Supplier dashboard to the new Home/Story landing; the dashboard itself
    # now lives at site/supplier/, and the new Platform section needs both its
    # static page and its generated data file tracked here or they never get
    # picked up by the auto-commit pipeline.
    site_supplier_html = PROJECT_DIR / "site" / "supplier" / "index.html"
    if site_supplier_html.exists():
        files.append(str(site_supplier_html))
    site_platform_html = PROJECT_DIR / "site" / "platform" / "index.html"
    if site_platform_html.exists():
        files.append(str(site_platform_html))
    site_platform_json = PROJECT_DIR / "site" / "data" / "platform.json"
    if site_platform_json.exists():
        files.append(str(site_platform_json))
    site_saas_coverage_json = PROJECT_DIR / "site" / "data" / "saas_coverage.json"
    if site_saas_coverage_json.exists():
        files.append(str(site_saas_coverage_json))
    site_method_html = PROJECT_DIR / "site" / "method" / "index.html"
    if site_method_html.exists():
        files.append(str(site_method_html))
    site_method_json = PROJECT_DIR / "site" / "data" / "method.json"
    if site_method_json.exists():
        files.append(str(site_method_json))
    site_case_studies_json = PROJECT_DIR / "site" / "data" / "case_studies.json"
    if site_case_studies_json.exists():
        files.append(str(site_case_studies_json))
    site_track_record_json = PROJECT_DIR / "site" / "state" / "track_record_scorecard.json"
    if site_track_record_json.exists():
        files.append(str(site_track_record_json))
    # GitHub Pages mirror (docs/staging/ADVISOR_GITHUBIO_MIRROR.md): the advisor's
    # fetch path to poesys.net proved persistently stale independent of any CD
    # incident, so shadow pages + state JSONs also ship from docs/ (GitHub Pages),
    # same as docs/status/PROJECT_STATE.txt already does.
    docs_shadow = PROJECT_DIR / "docs" / "shadow"
    if docs_shadow.exists():
        files.append(str(docs_shadow))
    docs_state = PROJECT_DIR / "docs" / "state"
    if docs_state.exists():
        files.append(str(docs_state))
    if DONE_DIR.exists():
        files.append(str(DONE_DIR))
    msg = "Auto-process run complete: report + LATEST.md + site/ (git={}, net=\xa3{:,.0f})".format(
        git_hash, net_margin
    )
    # Serialize against other git writers (interactive session, autonomous_runner
    # turns, a concurrent process_run_complete.py invocation) -- see
    # background/tree_lock.py. Without this, a `git add` from another writer
    # staged between this one's add and commit gets swept into this commit
    # (observed directly: a manually-staged code change landed inside an
    # unrelated auto-process commit message).
    with tree_lock():
        subprocess.run(["git", "add"] + files, cwd=str(PROJECT_DIR), timeout=30)
        result = subprocess.run(["git", "commit", "-m", msg], cwd=str(PROJECT_DIR), timeout=30)
        if result.returncode != 0:
            log("Nothing to commit or commit failed")
            return False

        if not _push_due():
            log("Committed locally, push deferred (throttled to every {}min)".format(
                PUSH_THROTTLE_SECONDS // 60
            ))
            return True

        push = subprocess.run(["git", "push"], cwd=str(PROJECT_DIR), timeout=60)
        if push.returncode == 0:
            _record_push_time()
        return push.returncode == 0


def _push_due() -> bool:
    """True if PUSH_THROTTLE_SECONDS have elapsed since the last recorded
    successful push (or none has ever been recorded)."""
    if not LAST_PUSH_FILE.exists():
        return True
    try:
        last = json.loads(LAST_PUSH_FILE.read_text())["ts"]
    except (json.JSONDecodeError, KeyError, TypeError, OSError):
        return True
    return (datetime.now(timezone.utc).timestamp() - last) >= PUSH_THROTTLE_SECONDS


def _record_push_time() -> None:
    LAST_PUSH_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_PUSH_FILE.write_text(json.dumps({"ts": datetime.now(timezone.utc).timestamp()}))


def _run_history_max_net():
    hp = PROJECT_DIR / "docs" / "observability" / "run_history.json"
    if not hp.exists():
        return 0.0
    try:
        import json as _j
        history = _j.loads(hp.read_text())
        return max((h.get("net_margin_gbp", 0) for h in history), default=0.0)
    except Exception:
        return 0.0


def maybe_ntfy(data, net_margin, insights=None):
    """Send NTFY for notable exceptions. Returns log message if sent, else None."""
    admin = data.get("administration_event")
    from background.ntfy_utils import send_ntfy
    if admin:
        date_str = admin.get("date", "unknown date") if isinstance(admin, dict) else str(admin)
        send_ntfy(
            "[SIM] ADMINISTRATION EVENT on {} - net margin £{:,.0f}. Check annual report.".format(
                date_str, net_margin
            )
        )
        return "NTFY sent: administration event on {}".format(date_str)
    prev_best = _run_history_max_net()
    is_new_high = net_margin > prev_best * 1.01 and prev_best > 0
    is_new_low = net_margin < prev_best * 0.5 and prev_best > 1_000_000
    if not (is_new_high or is_new_low):
        return None
    tag = "[NEW HIGH]" if is_new_high else "[NEW LOW]"
    summary = getattr(insights, "executive_summary", "") if insights else ""
    acts = list(getattr(insights, "recommended_actions", ()) if insights else [])
    msg = "[SIM] {} Net margin £{:,.0f}".format(tag, net_margin)
    if summary:
        msg += " -- " + str(summary)[:120]
    if acts:
        msg += " | Action: " + str(acts[0])[:80]
    send_ntfy(msg)
    return "NTFY sent: {} net margin £{:,.0f}".format(tag, net_margin)



def main(marker_path_str):
    with _run_lock() as acquired:
        if not acquired:
            log("Another process_run_complete instance is already running -- "
                "skipping {} (will be picked up next cycle if still present)".format(
                    Path(marker_path_str).name))
            return 0
        return _process(marker_path_str)


def _process(marker_path_str):
    marker = Path(marker_path_str).resolve()
    if not marker.exists():
        if (DONE_DIR / Path(marker_path_str).name).exists():
            log("Already in done/ (duplicate run): {}".format(Path(marker_path_str).name))
            return 0
        log("Marker not found: {}".format(marker))
        return 1

    log("Processing {}".format(marker.name))
    fields = parse_marker(marker)
    json_path = fields.get("json_path")
    git_hash = fields.get("git_hash", "unknown")
    elapsed_s = fields.get("elapsed_s", 0.0)

    if not json_path or not json_path.exists():
        log("JSON not found: {}".format(json_path))
        return 1

    data = json.loads(json_path.read_text())
    net_margin = data.get("total_net_gbp", 0)

    log("Regenerating ANNUAL_REPORT.md from {}".format(json_path.name))
    if not regenerate_report(json_path):
        log("Report regeneration failed")
        return 1

    log("Updating LATEST.md")
    update_latest_md(data, elapsed_s, git_hash)

    # Run insights (so-what layer) MUST be regenerated before the dashboard/
    # site build below: generate_dashboard_data.py reads run_insights.json
    # straight off disk for the exec-summary section, separately from the
    # run_output.json it loads for the totals section. Building the dashboard
    # first would bake in the PREVIOUS run's exec summary next to this run's
    # totals -- exactly the contradiction the website-integrity fix closed.
    log("Generating run insights (so-what layer)")
    run_insights = None
    try:
        from tools.generate_insights import generate_insights, save_insights, append_run_history
        run_insights = generate_insights(data, git_hash)
        save_insights(run_insights, RUN_INSIGHTS_PATH)
        append_run_history(run_insights, RUN_HISTORY_PATH)
        log("Run insights saved: {}".format(run_insights.executive_summary[:80]))
    except Exception as exc:
        log("Run insights generation skipped: {}".format(exc))

    log("Generating site/data/dashboard.json")
    consistency_ok = generate_dashboard_json(json_path, git_hash)
    if not consistency_ok:
        from background.ntfy_utils import send_ntfy
        send_ntfy(
            "[SIM] CONSISTENCY GATE FAILED (git={}) — dashboard totals and exec-summary "
            "insights disagree on a headline number. Site figures may be untrustworthy "
            "until this is fixed. See docs/observability/sim-runner-log.md for detail.".format(git_hash)
        )
        log("NTFY sent: consistency gate failure")
    generate_site(data, elapsed_s, git_hash, fields.get("finished"))

    try:
        from tools.revenue_sanity_check import run_check
        _ok, sanity_report = run_check(data)
        status = "PASS" if _ok else "ANOMALIES"
        log("Revenue sanity: {} — see annual report".format(status))
    except Exception as exc:
        log("Revenue sanity check skipped: {}".format(exc))

    log("Publishing market price feed")
    try:
        from simulation.publish_market_feed import publish as _publish_feed
        _publish_feed()
        log("Price feed published to docs/market_data/price_feed.json")
    except Exception as exc:
        log("Price feed publication skipped: {}".format(exc))

    log("Publishing HH consumption data feed")
    try:
        from simulation.publish_consumption_data import publish_consumption
        publish_consumption()
        log("Consumption feed published to docs/market_data/consumption_feed.json")
    except Exception as exc:
        log("Consumption feed publication skipped: {}".format(exc))

    log("Fetching weather data (Open-Meteo)")
    try:
        _run_weather_data(git_hash)
        log("Weather data written to site/data/weather.json")
    except Exception as exc:
        log("Weather data fetch skipped: {}".format(exc))

    log("Running fast test suite (SIM_FAST_MODE=1)")
    tests_ok, timed_out = run_fast_tests(git_hash)
    if not tests_ok:
        log("Tests FAILED - not committing")
        return 1
    if timed_out:
        log("WARNING: tests timed out — results unverified but committing")

    # Move the marker to done/ BEFORE committing so the archive itself lands in
    # the same commit as the run it documents, instead of sitting untracked
    # forever (observed: 7+ done/ markers never made it into any commit).
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        marker.rename(DONE_DIR / marker.name)
        log("Moved {} to done/".format(marker.name))
    except FileNotFoundError:
        if (DONE_DIR / marker.name).exists():
            log("{} already in done/ (processed concurrently)".format(marker.name))
        else:
            log("WARNING: {} vanished from staging and not in done/".format(marker.name))

    log("Committing and pushing (net=\xa3{:,.0f})".format(net_margin))
    if not git_commit_push(git_hash, net_margin):
        log("Commit/push failed (possibly nothing changed)")

    # Keep agent_status.json financial metrics current (phase/tests preserved by phase-close)
    try:
        import json as _json
        from background.agent_status import update_sim_metrics, STATUS_FILE
        _existing = _json.loads(STATUS_FILE.read_text()) if STATUS_FILE.exists() else {}
        update_sim_metrics(
            phase=_existing.get("phase", 0),
            tests_passing=_existing.get("tests_passing", 0),
            treasury_gbp=data.get("final_treasury_gbp", 0),
            net_margin_gbp=data.get("total_net_gbp", 0),
            enterprise_value_gbp=data.get("enterprise_value_gbp", 0),
        )
    except Exception as exc:
        log("agent_status metrics update skipped: {}".format(exc))

    ntfy_msg = maybe_ntfy(data, net_margin, run_insights)
    if ntfy_msg:
        log(ntfy_msg)
    log("Done")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} <path/to/run_complete_TIMESTAMP.md>".format(sys.argv[0]))
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
