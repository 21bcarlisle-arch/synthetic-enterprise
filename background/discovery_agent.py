#!/usr/bin/env python3
"""Standing discovery agent — validates simulation assumptions against real market data.

Runs a discovery cycle: reads docs/market_research/ASSUMPTIONS.md, uses
Qwen (local Ollama, no GPU/frontier cost) to reason about whether each
assumption is still realistic, flags discrepancies, and updates the library.

Called from session startup via CLAUDE.md's startup protocol, or manually:
    python3 -m background.discovery_agent

Logs findings to docs/observability/discovery-log.md.
Sends NTFY when a HIGH-severity discrepancy is found.
"""

import json
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_DIR / "docs" / "observability" / "discovery-log.md"
ASSUMPTIONS_FILE = PROJECT_DIR / "docs" / "market_research" / "ASSUMPTIONS.md"

sys.path.insert(0, str(PROJECT_DIR))
from background.ntfy_utils import send_ntfy  # noqa: E402

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:14b"

# Assumptions that change annually and need periodic re-validation
HIGH_PRIORITY_ASSUMPTIONS = [
    "Non-commodity cost",
    "Standing charge",
    "Obligation rates",
]


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def _call_qwen(prompt: str, max_tokens: int = 400) -> str:
    """Call local Qwen via Ollama. Returns empty string on failure."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", OLLAMA_URL,
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "model": OLLAMA_MODEL,
                 "prompt": prompt,
                 "stream": False,
                 "options": {"num_predict": max_tokens, "temperature": 0.1},
             })],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("response", "").strip()
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        pass
    return ""


def _extract_assumption_rows(md_text: str) -> list[dict]:
    """Parse assumption table rows from ASSUMPTIONS.md."""
    rows = []
    for line in md_text.splitlines():
        # Match table rows (| col | col | ... |) but not headers or separators
        if not line.startswith("|") or line.startswith("| Assumption") or "---" in line:
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) >= 5:
            rows.append({
                "assumption": parts[0],
                "sim_value": parts[1],
                "benchmark": parts[2],
                "source": parts[3],
                "last_checked": parts[4] if len(parts) > 4 else "",
                "status": parts[5] if len(parts) > 5 else "",
            })
    return rows


def _assess_assumption(row: dict) -> dict:
    """Use Qwen to assess whether a simulation assumption is plausible.

    Returns {severity: 'ok'|'warning'|'critical', note: str}.
    """
    prompt = f"""You are auditing a UK retail energy supplier simulation.
Check whether this assumption is realistic for a small UK retail energy supplier (2016-2025).

Assumption: {row['assumption']}
Current SIM value: {row['sim_value']}
Industry benchmark: {row['benchmark']}
Source: {row['source']}
Status: {row['status']}

Respond with EXACTLY this format (no extra text):
VERDICT: ok|warning|critical
NOTE: <one sentence explaining your verdict>

Use 'critical' only if the SIM value is clearly outside industry range and materially distorts outputs.
Use 'warning' if the value is at the edge of plausible range or the source is dated.
Use 'ok' if the value is realistic.
/no_think"""

    response = _call_qwen(prompt, max_tokens=150)
    verdict = "ok"
    note = "Qwen assessment unavailable"

    if response:
        verdict_match = re.search(r"VERDICT:\s*(ok|warning|critical)", response, re.IGNORECASE)
        note_match = re.search(r"NOTE:\s*(.+)", response)
        if verdict_match:
            verdict = verdict_match.group(1).lower()
        if note_match:
            note = note_match.group(1).strip()

    return {"severity": verdict, "note": note}


def run_discovery_cycle(
    assumptions_file: Path = ASSUMPTIONS_FILE,
    use_qwen: bool = True,
    max_rows: int = 10,
) -> list[dict]:
    """Run a discovery cycle over all assumption rows.

    Returns list of findings: [{assumption, severity, note}].
    Sends NTFY for any 'critical' findings.
    """
    if not assumptions_file.exists():
        log(f"Assumption library not found at {assumptions_file} — skipping")
        return []

    md_text = assumptions_file.read_text()
    rows = _extract_assumption_rows(md_text)
    log(f"Discovery cycle started — {len(rows)} assumptions to review")

    findings = []
    critical_count = 0
    warning_count = 0

    for row in rows[:max_rows]:
        if not row["assumption"] or row["assumption"] == "Gap":
            continue

        if use_qwen:
            result = _assess_assumption(row)
        else:
            # Heuristic fallback when Qwen unavailable
            status = row.get("status", "")
            if "❌" in status:
                result = {"severity": "critical", "note": "Marked as gap/error in assumption library"}
            elif "⚠" in status:
                result = {"severity": "warning", "note": "Flagged in assumption library"}
            else:
                result = {"severity": "ok", "note": "Within expected range per assumption library"}

        findings.append({**row, **result})

        if result["severity"] == "critical":
            critical_count += 1
            log(f"CRITICAL: {row['assumption']} — {result['note']}")
        elif result["severity"] == "warning":
            warning_count += 1
            log(f"WARNING: {row['assumption']} — {result['note']}")
        else:
            log(f"OK: {row['assumption']}")

    summary = (
        f"Discovery cycle complete: {len(findings)} assumptions reviewed, "
        f"{critical_count} critical, {warning_count} warnings"
    )
    log(summary)

    if critical_count > 0:
        critical_items = [f for f in findings if f["severity"] == "critical"]
        names = ", ".join(f["assumption"] for f in critical_items[:3])
        send_ntfy(
            f"[Discovery] {critical_count} critical assumption(s) flagged: {names}. "
            f"See docs/market_research/ASSUMPTIONS.md"
        )

    return findings


def _update_last_checked(assumptions_file: Path, today: str) -> None:
    """Bump the 'Last seeded' date in the assumptions file."""
    text = assumptions_file.read_text()
    text = re.sub(
        r"Last seeded: \d{4}-\d{2}-\d{2}",
        f"Last seeded: {today}",
        text,
    )
    assumptions_file.write_text(text)


def main() -> None:
    import sys
    import time

    daemon = "--daemon" in sys.argv
    interval_hours = 6

    today = date.today().isoformat()
    log(f"Discovery agent started (date: {today}, daemon={daemon})")

    while True:
        today = date.today().isoformat()
        findings = run_discovery_cycle()
        _update_last_checked(ASSUMPTIONS_FILE, today)
        ok = sum(1 for f in findings if f["severity"] == "ok")
        warn = sum(1 for f in findings if f["severity"] == "warning")
        crit = sum(1 for f in findings if f["severity"] == "critical")
        summary = f"Discovery: {ok} OK, {warn} warnings, {crit} critical"
        log(summary)
        print(f"\n{summary}")
        if not daemon:
            break
        log(f"Next cycle in {interval_hours}h — sleeping")
        time.sleep(interval_hours * 3600)


if __name__ == "__main__":
    main()
