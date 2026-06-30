#!/usr/bin/env python3
"""Generate state snapshot artifact for twice-daily checkpoint reviews."""
import datetime as dt
import json
import os
import subprocess


def generate_snapshot():
    now = dt.datetime.now(dt.timezone.utc)
    timestamp = now.strftime("%Y%m%dT%H%M%SZ")
    
    # Regenerate dashboard data
    result = subprocess.run(["python3", "-m", "tools.generate_dashboard_data"],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print("WARNING: generate_dashboard_data failed:", result.stderr[:200])
    
    # Read current dashboard
    try:
        dashboard = json.load(open("site/data/dashboard.json"))
    except Exception:
        dashboard = {}
    
    # Read agent status
    try:
        agent_status = json.load(open("site/data/agent_status.json"))
    except Exception:
        agent_status = {}
    
    # Read latest run output
    try:
        run_output = json.load(open("docs/reports/run_output_latest.json"))
    except Exception:
        run_output = {}
    
    # Compose snapshot
    snap = {
        "snapshot_ts": now.isoformat(),
        "snapshot_label": timestamp,
        "dashboard": dashboard,
        "agent_status": agent_status,
        "latest_run": run_output,
    }
    
    # Write snapshot JSON
    snap_dir = "site/data/snapshots"
    os.makedirs(snap_dir, exist_ok=True)
    snap_path = f"{snap_dir}/LATEST_{timestamp}.json"
    json.dump(snap, open(snap_path, "w"), indent=2, default=str)
    
    # Also write a stable LATEST.json
    json.dump(snap, open(f"{snap_dir}/LATEST.json", "w"), indent=2, default=str)
    
    print(f"Snapshot written: {snap_path}")
    return snap, timestamp


def write_build_state(snap, timestamp):
    build = snap["dashboard"].get("build", {})
    fin = snap["dashboard"].get("financial", {})
    ann = fin.get("annual", [])
    net_margin = sum(r.get("net_gbp", 0) for r in ann)
    latest_run = snap.get("latest_run", {})
    
    lines = [
        "# BUILD STATE",
        f"",
        f"**Generated:** {timestamp}  ",
        f"**Current Phase:** {build.get('current_phase', 'unknown')}  ",
        f"**Tests Passing:** {build.get('test_suite', 'unknown')}  ",
        f"**Company Modules:** {build.get('company_modules', 'unknown')}+  ",
        f"**Simulation Window:** {build.get('simulation_window', '2016-2025')}  ",
        f"",
        f"## Latest Run Metrics",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Net Margin | £{latest_run.get('net_margin_gbp', 0):,.0f} |",
        f"| Gross Margin | £{latest_run.get('gross_margin_gbp', 0):,.0f} |",
        f"| Enterprise Value | £{latest_run.get('enterprise_value_gbp', 0):,.0f} |",
        f"| Treasury | £{latest_run.get('treasury_gbp', 0):,.0f} |",
        f"",
        f"## Module Status",
        f"",
        f"- Regulatory modules: {build.get('regulatory_modules', 48)}",
        f"- Company modules: {build.get('company_modules', 0)}+",
        f"- All company/ tests: {build.get('test_count', 0):,} passing",
        f"",
        f"## Snapshot Location",
        f"",
        f"- `site/data/snapshots/LATEST_{timestamp}.json` — full dashboard data",
        f"- `site/data/snapshots/LATEST.json` — stable pointer to latest",
    ]
    
    content = "\n".join(lines) + "\n"
    open("docs/BUILD_STATE.md", "w").write(content)
    print("docs/BUILD_STATE.md written")


if __name__ == "__main__":
    snap, ts = generate_snapshot()
    write_build_state(snap, ts)
    
    # Update LATEST.md timestamp
    try:
        latest = open("docs/status/LATEST.md").read()
        now = dt.datetime.now(dt.timezone.utc)
        # Replace timestamp pattern
        import re
        new_ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        latest = re.sub(r"Last updated: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",
                        f"Last updated: {new_ts}", latest)
        open("docs/status/LATEST.md", "w").write(latest)
        print(f"docs/status/LATEST.md updated: {new_ts}")
    except Exception as e:
        print(f"WARNING: Could not update LATEST.md: {e}")
    
    print("Snapshot complete.")
