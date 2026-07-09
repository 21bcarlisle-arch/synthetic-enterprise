"""Sanity daemon -- Phase 5 of DOMAIN_SENSE_AND_COMPLIANCE.md (harness-side,
background lane).

Continuously samples the latest rendered data surfaces against
company/compliance/domain_invariants.py and runs the population-level
statistical tests named in the doc: consumption distributions vs TDCV,
revenue/customer vs cap-implied bands, estimated-read rates vs industry
norms (all implemented in company/compliance/population_sanity.py). This is
a DETECTIVE, statistical-sample control (obligations_register.py's
RiskTier.TIER_2/3), not a preventive gate like Phase 3's pre-bill
validation -- occasional findings on real edge cases (a successor
account's partial transition year, a fixed-term contract renewed right at
a cap boundary) are expected, legitimate output for human review, not a
sign the check itself is broken.

Runs read-only: never blocks a bill run, never mutates run_output_latest.json
or the billing ledger. Escalates via one NTFY per distinct finding-set (R5:
never repeat an unchanged status) -- a new finding or a changed finding set
gets one NTFY; an unchanged set from the prior cycle stays silent.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from background.agent_status import update_agent_status  # noqa: E402
from background.ntfy_utils import send_ntfy  # noqa: E402
from company.compliance.population_sanity import run_all_population_checks  # noqa: E402
from company.compliance.internal_audit import run_internal_audit  # noqa: E402

LOG_FILE = PROJECT_DIR / "docs" / "observability" / "sanity-daemon-log.md"
RUN_OUTPUT_PATH = PROJECT_DIR / "docs" / "reports" / "run_output_latest.json"

POLL_INTERVAL_SECONDS = 1800  # 30 minutes -- detective/sampling cadence, not turn-granting

# Phase 6: how many bills the Qwen skeptic reviews per cycle. Small on
# purpose -- each call takes real wall-clock time (~10-30s) against the
# local model, and this is a sampling control, not a full sweep.
AUDIT_SAMPLES_PER_CYCLE = 2

_last_finding_signature: str | None = None
_last_audit_signature: str | None = None


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


def _finding_signature(findings: list) -> str:
    return json.dumps(sorted(
        (f["check"], f.get("customer_id"), f.get("year")) for f in findings
    ))


def _audit_signature(findings: list) -> str:
    return json.dumps(sorted((f["customer_id"], f["period_end"]) for f in findings))


def run_cycle() -> None:
    global _last_finding_signature, _last_audit_signature

    if not RUN_OUTPUT_PATH.is_file():
        log("No run_output_latest.json -- skipping this cycle")
        return

    try:
        data = json.loads(RUN_OUTPUT_PATH.read_text())
    except (json.JSONDecodeError, OSError) as e:
        log(f"Could not read/parse run_output_latest.json: {e}")
        return

    bills = data.get("bills", [])

    findings = run_all_population_checks(bills, data.get("meter_read_log", []))

    if not findings:
        log("Clean -- 0 population-sanity findings")
        _last_finding_signature = _finding_signature([])
    else:
        signature = _finding_signature(findings)
        log(f"{len(findings)} population-sanity finding(s): " +
            "; ".join(f["detail"] for f in findings[:5]) +
            (" ..." if len(findings) > 5 else ""))

        if signature != _last_finding_signature:
            send_ntfy(
                f"Sanity daemon: {len(findings)} population-level finding(s) -- "
                + "; ".join(f["detail"] for f in findings[:3])
                + (" (+ more, see sanity-daemon-log.md)" if len(findings) > 3 else "")
            )
            log("NTFY sent (new/changed finding set)")
        _last_finding_signature = signature

    # Phase 6: internal audit sample. Advisory only -- a live run found the
    # Qwen skeptic can produce false positives on numeric consistency
    # (flagged a bill whose VAT was manually verified exactly correct,
    # 2026-07-09) -- every message here says so explicitly, so a reader
    # never mistakes a flag for a confirmed defect the way Phase 3's
    # deterministic gate's findings are.
    audit_findings = run_internal_audit(bills, n_samples=AUDIT_SAMPLES_PER_CYCLE)
    if not audit_findings:
        log("Internal audit: 0 flagged in this cycle's sample (advisory, small sample)")
        _last_audit_signature = _audit_signature([])
    else:
        audit_sig = _audit_signature(audit_findings)
        detail = "; ".join(f"{f['customer_id']} ({f['period_end']}): {f['note']}" for f in audit_findings)
        log(f"Internal audit (Qwen skeptic, ADVISORY -- verify before acting): {detail}")
        if audit_sig != _last_audit_signature:
            send_ntfy(
                "Sanity daemon: internal audit (Qwen skeptic, advisory -- verify before "
                f"acting, false positives observed) flagged: {detail}"
            )
            log("NTFY sent (new/changed audit finding)")
        _last_audit_signature = audit_sig


def main() -> None:
    log("Sanity daemon started -- population-level statistical sampling (Phase 5)")
    update_agent_status(
        "sanity-daemon", status="idle",
        last_action="Sanity daemon started",
        role="Detective/sampling control: population-level consumption/unit-rate/estimated-read checks against domain_invariants.py every 30min",
        produces="sanity-daemon-log.md entries + one NTFY per new/changed finding set",
    )
    while True:
        try:
            run_cycle()
        except Exception as e:
            log(f"Sanity daemon cycle error: {e}")
        try:
            update_agent_status(
                "sanity-daemon", status="idle",
                last_action="Cycle complete",
            )
        except Exception:
            pass
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
