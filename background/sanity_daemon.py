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
or the billing ledger.

Alert discipline REDESIGNED 2026-07-11 (director-ordered sanity triage,
docs/design/SANITY_TRIAGE_2026_07_11.md): the audit (Qwen skeptic) stream's
signature was already normalised to 3 known categories specifically to stop
alarm fatigue -- but since only a couple of bills are sampled per cycle, a
DIFFERENT subset of those same known categories gets drawn each time, so the
signature (a set of category strings) still changed cycle to cycle, and it
re-alerted almost every single 30-min cycle for 21h+ (confirmed: ~70 NTFYs
against ~70 cycles). Replaced the in-memory prior-signature comparison with
the durable company/compliance/sanity_adjudication.py ledger: a finding_key
(population check+customer+year, or audit category) already IN the ledger --
whatever its adjudicated state -- is a standing known finding and goes into
ONE daily digest line, never a repeat NTFY; only a finding_key never seen
before (auto-registered as "open" on first sighting) gets an immediate NTFY.
Director's own framing for why this matters: "an alarm that repeats
unactionably trains me to ignore all alarms, which kills the immune system."
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
from company.compliance import sanity_adjudication as adjudication  # noqa: E402

LOG_FILE = PROJECT_DIR / "docs" / "observability" / "sanity-daemon-log.md"
RUN_OUTPUT_PATH = PROJECT_DIR / "docs" / "reports" / "run_output_latest.json"
BILLING_LEDGER_PATH = PROJECT_DIR / "site" / "state" / "billing_ledger.json"
LAST_DIGEST_DATE_FILE = PROJECT_DIR / "docs" / "observability" / ".sanity_daemon_last_digest_date"

POLL_INTERVAL_SECONDS = 1800  # 30 minutes -- detective/sampling cadence, not turn-granting

# Phase 6: how many bills the Qwen skeptic reviews per cycle. Small on
# purpose -- each call takes real wall-clock time (~10-30s) against the
# local model, and this is a sampling control, not a full sweep.
AUDIT_SAMPLES_PER_CYCLE = 2


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n- [{ts}] {msg}"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(entry)
    print(entry)


# 2026-07-10 director observation (from_rich_20260710_135317.md), and
# 2026-07-11's follow-up (docs/design/SANITY_TRIAGE_2026_07_11.md): a naive
# signature keying on (customer_id, period_end) re-fires almost every cycle,
# since `run_internal_audit`'s risk-based RANDOM sample (unseeded -- a fresh
# draw every cycle) is guaranteed to change almost every time, even when the
# underlying finding is the exact same recurring false-positive SHAPE (e.g.
# "gas billed in kWh" -- correct GB practice, adjudicated a false positive,
# see the triage doc). Categorising alone (this dict) was only a PARTIAL fix
# -- a small per-cycle sample still draws a different SUBSET of the same
# known categories each time, so a signature built from that subset still
# changes cycle to cycle. The real fix is _register_if_new()'s ledger-backed
# membership check below: durable, not subset-dependent.
_AUDIT_CATEGORY_RULES = [
    ("gas-kwh-unit", ("gas", "kwh")),
    ("vat-mismatch", ("vat",)),
    ("high-consumption", ("consumption",)),
]


def _categorize_audit_note(note: str) -> str:
    lowered = note.lower()
    for category, keywords in _AUDIT_CATEGORY_RULES:
        if all(kw in lowered for kw in keywords):
            return category
    return f"other:{note.strip()[:40].lower()}"


def _population_finding_key(f: dict) -> str:
    return f"population:{f['check']}:{f.get('customer_id')}:{f.get('year')}"


def _audit_finding_key(category: str) -> str:
    return f"audit:{category}"


def _register_if_new(finding_key: str, evidence: str) -> bool:
    """Auto-register a never-before-seen finding key as 'open' in the
    durable adjudication ledger and return True (genuinely new -- alert the
    caller). A key already in the ledger (whatever its state: open,
    adjudicated-real, or adjudicated-false-positive) is a standing known
    finding -- returns False, folds into the daily digest instead of
    repeating a per-cycle NTFY."""
    if adjudication.is_known(finding_key):
        return False
    adjudication.adjudicate(finding_key, "open", evidence, "sanity-daemon (auto-registered)")
    return True


def _maybe_send_daily_digest(any_new_this_cycle: bool) -> None:
    """Standing open findings get ONE line in a daily digest, not a 30-min
    repeat (director's own framing, 2026-07-11: "an alarm that repeats
    unactionably trains me to ignore all alarms, which kills the immune
    system."). Fires at most once per UTC calendar date. If a genuinely new
    finding already triggered its own fresh NTFY this cycle, that satisfies
    today's notification budget -- skip the digest today rather than
    immediately following a fresh alert with a redundant summary of the
    same information."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    last_sent = LAST_DIGEST_DATE_FILE.read_text().strip() if LAST_DIGEST_DATE_FILE.exists() else None
    if last_sent == today:
        return
    if not any_new_this_cycle:
        open_entries = adjudication.open_findings()
        if open_entries:
            lines = "; ".join(e["finding_key"] for e in open_entries[:8])
            send_ntfy(
                f"Sanity daemon daily digest: {len(open_entries)} standing open finding(s) -- {lines}"
                + (" (+ more, see sanity_adjudication_ledger.json)" if len(open_entries) > 8 else "")
            )
            log(f"Daily digest sent -- {len(open_entries)} standing open finding(s)")
    LAST_DIGEST_DATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_DIGEST_DATE_FILE.write_text(today)


def run_cycle() -> None:
    if not RUN_OUTPUT_PATH.is_file():
        log("No run_output_latest.json -- skipping this cycle")
        return

    try:
        data = json.loads(RUN_OUTPUT_PATH.read_text())
    except (json.JSONDecodeError, OSError) as e:
        log(f"Could not read/parse run_output_latest.json: {e}")
        return

    bills = data.get("bills", [])

    # Payment-channel mix check (2026-07-09) needs the ALREADY-COMPUTED
    # payment records (method field), which only exist in the generated
    # billing ledger, not in run_output_latest.json's raw bills -- read-only,
    # optional (missing/unreadable file just means that one check is skipped
    # this cycle, same graceful-degradation style as the rest of this daemon).
    payments: list = []
    if BILLING_LEDGER_PATH.is_file():
        try:
            ledger = json.loads(BILLING_LEDGER_PATH.read_text())
            for cust in ledger.get("customers", {}).values():
                if cust.get("segment") == "resi":
                    payments.extend(cust.get("payments", []))
        except (json.JSONDecodeError, OSError):
            pass

    findings = run_all_population_checks(bills, data.get("meter_read_log", []), payments)
    new_findings: list[dict] = []

    if not findings:
        log("Clean -- 0 population-sanity findings")
    else:
        log(f"{len(findings)} population-sanity finding(s): " +
            "; ".join(f["detail"] for f in findings[:5]) +
            (" ..." if len(findings) > 5 else ""))

        new_findings = [f for f in findings if _register_if_new(_population_finding_key(f), f["detail"])]
        if new_findings:
            send_ntfy(
                f"Sanity daemon: {len(new_findings)} NEW population-level finding(s) -- "
                + "; ".join(f["detail"] for f in new_findings[:3])
                + (" (+ more, see sanity-daemon-log.md)" if len(new_findings) > 3 else "")
            )
            log(f"NTFY sent ({len(new_findings)} genuinely new finding(s))")

    # Phase 6: internal audit sample. Advisory only -- a live run found the
    # Qwen skeptic can produce false positives on numeric consistency
    # (flagged a bill whose VAT was manually verified exactly correct,
    # 2026-07-09) -- every message here says so explicitly, so a reader
    # never mistakes a flag for a confirmed defect the way Phase 3's
    # deterministic gate's findings are.
    audit_findings = run_internal_audit(bills, n_samples=AUDIT_SAMPLES_PER_CYCLE)
    new_categories: list[str] = []
    if not audit_findings:
        log("Internal audit: 0 flagged in this cycle's sample (advisory, small sample)")
    else:
        categories = sorted({_categorize_audit_note(f["note"]) for f in audit_findings})
        detail = "; ".join(f"{f['customer_id']} ({f['period_end']}): {f['note']}" for f in audit_findings)
        log(f"Internal audit (Qwen skeptic, ADVISORY -- verify before acting): {detail}")
        new_categories = [c for c in categories if _register_if_new(_audit_finding_key(c), detail)]
        if new_categories:
            send_ntfy(
                "Sanity daemon: internal audit (Qwen skeptic, advisory -- verify before "
                f"acting, false positives observed) flagged a NEW category "
                f"({', '.join(new_categories)}): {detail}"
            )
            log(f"NTFY sent (new audit category: {', '.join(new_categories)})")

    _maybe_send_daily_digest(any_new_this_cycle=bool(new_findings) or bool(new_categories))


def main() -> None:
    log("Sanity daemon started -- population-level statistical sampling (Phase 5)")
    update_agent_status(
        "sanity-daemon", status="idle",
        last_action="Sanity daemon started",
        role="Detective/sampling control: population-level consumption/unit-rate/estimated-read checks against domain_invariants.py every 30min",
        produces="sanity-daemon-log.md entries + one NTFY per genuinely new finding + a daily digest of standing open findings",
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
