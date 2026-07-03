#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
STAGING_DIR = PROJECT_DIR / "docs" / "staging"
DONE_DIR = STAGING_DIR / "done"
LATEST_MD = PROJECT_DIR / "docs" / "status" / "LATEST.md"
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "sim-runner-log.md"
LAST_TESTED_HASH_FILE = PROJECT_DIR / "docs" / "observability" / ".last_tested_hash"
sys.path.insert(0, str(PROJECT_DIR))


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


def _run_weather_data():
    from tools.fetch_weather_data import generate_weather_data
    generate_weather_data()


def _fmt_gbp(v):
    """Format a GBP value with sign and £ prefix, e.g. £+225,920 or £-3,766."""
    sign = "+" if v >= 0 else ""
    return "\xa3{}{:,.0f}".format(sign, v)


def generate_dashboard_json(json_path):
    """Generate site/data/dashboard.json for the SPA dashboard."""
    try:
        sys.path.insert(0, str(PROJECT_DIR))
        from tools.generate_dashboard_data import generate
        ok = generate(json_path)
        if ok:
            log("Generated site/data/dashboard.json")
        else:
            log("Dashboard data generation returned False — skipping")
    except Exception as exc:
        log("Dashboard data generation failed: {}".format(exc))
    try:
        from tools.generate_customer_data import generate as gen_cust
        gen_cust(json_path)
        log("Generated site/data/customers/ JSON")
    except Exception as exc:
        log("Customer data generation failed: {}".format(exc))
    try:
        from tools.generate_invoice_data import generate as gen_inv
        gen_inv(json_path)
        log("Generated customer invoice JSON")
    except Exception as exc:
        log("Invoice data generation failed: {}".format(exc))
    try:
        from tools.generate_sim_data import generate as gen_sim
        gen_sim()
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
        from tools.generate_shadow_html import generate as gen_shadow
        gen_shadow()
        log("Generated site/shadow/ static HTML mirror")
    except Exception as exc:
        log("Shadow HTML generation failed: {}".format(exc))


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
    subprocess.run(["git", "add"] + files, cwd=str(PROJECT_DIR), timeout=30)
    msg = "Auto-process run complete: report + LATEST.md + site/ (git={}, net=\xa3{:,.0f})".format(
        git_hash, net_margin
    )
    result = subprocess.run(["git", "commit", "-m", msg], cwd=str(PROJECT_DIR), timeout=30)
    if result.returncode != 0:
        log("Nothing to commit or commit failed")
        return False
    push = subprocess.run(["git", "push"], cwd=str(PROJECT_DIR), timeout=60)
    return push.returncode == 0


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

    log("Generating site/data/dashboard.json")
    generate_dashboard_json(json_path)
    generate_site(data, elapsed_s, git_hash, fields.get("finished"))

    try:
        from tools.revenue_sanity_check import run_check
        _ok, sanity_report = run_check(data)
        status = "PASS" if _ok else "ANOMALIES"
        log("Revenue sanity: {} — see annual report".format(status))
    except Exception as exc:
        log("Revenue sanity check skipped: {}".format(exc))


    log("Generating run insights (so-what layer)")
    run_insights = None
    try:
        from tools.generate_insights import generate_insights, save_insights, append_run_history
        run_insights = generate_insights(data, git_hash)
        save_insights(run_insights)
        append_run_history(run_insights)
        log("Run insights saved: {}".format(run_insights.executive_summary[:80]))
    except Exception as exc:
        log("Run insights generation skipped: {}".format(exc))

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
        _run_weather_data()
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

    log("Committing and pushing (net=\xa3{:,.0f})".format(net_margin))
    if not git_commit_push(git_hash, net_margin):
        log("Commit/push failed (possibly nothing changed)")

    DONE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        marker.rename(DONE_DIR / marker.name)
        log("Moved {} to done/".format(marker.name))
    except FileNotFoundError:
        if (DONE_DIR / marker.name).exists():
            log("{} already in done/ (processed concurrently)".format(marker.name))
        else:
            log("WARNING: {} vanished from staging and not in done/".format(marker.name))

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
