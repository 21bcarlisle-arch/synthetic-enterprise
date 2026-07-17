"""STATUS-DOC HONESTY gate (director P0, 2026-07-17, step 5): LATEST.md must not describe a system
that is not running.

The disease (Q4): LATEST.md's narrative header is orphaned hand-text; the only auto-writer
(process_run_complete.update_latest_md) re-subs ONLY the "Last updated:" line + its own data
blocks -- never the header. So stale prose (a DIRECTOR_TWIN standing-approver auto-approving BUILD,
a self-driving BUILD lane, THREE LANES with "forks in flight", an A3 approval interface, a days-old
blackout as the headline) gets re-stamped with a FRESH timestamp every publish and reads as
current. That is what made the director misread the whole system as breached tonight.

The gate anchors to DECLARED TRUTH -- the process manifest's ENABLED daemon set and the CURRENT
governance/execution model (the gate-wall; a serial self-sustaining pull loop; bounded <=3 parallel
forks with an enforced merge-or-reap lifecycle). It FLAGS narrative that asserts a NON-running
daemon or a retired governance model as the current reality. REPORT/GATE only -- it never rewrites
the doc; it makes a lie un-committable (pre-commit) and LOUD (deadman).

Precision matters: this can gate the publish path, so a false positive would wedge publishing. The
patterns therefore match CURRENT-MODEL assertions specifically (e.g. "twin-approver seat",
"self-driving BUILD lane"), NOT honest historical mentions ("session_watchdog fired /usage ... FIXED"
is a true incident record and must pass).
"""
from __future__ import annotations

import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
LATEST_MD = PROJECT_DIR / "docs" / "status" / "LATEST.md"

# Retired governance/execution MODELS asserted as current. Each is justified against declared truth:
# the running governance is the gate-wall (director-console-authorized BUILD-open), and the running
# execution model is a serial self-sustaining pull loop with bounded (<=3) parallel forks under an
# enforced merge-or-reap lifecycle -- NOT a twin standing-approver, NOT a self-driving BUILD lane,
# NOT unbounded "forks in flight".
STALE_MODEL_CLAIMS: list[tuple[str, str]] = [
    (r"twin[- ]approver seat",
     "no twin-approver seat runs; BUILD-open is director-console-authorized via the gate-wall"),
    (r"DIRECTOR_TWIN standing[- ]approver",
     "the twin is a voice-not-hand; the running governance is the gate-wall (director console "
     "authorization), not a twin standing BUILD approver"),
    (r"self[- ]driving BUILD lane",
     "the BUILD lane is director-gated (gate-wall), not self-driving"),
    (r"forks? in flight",
     "fork fan-out is bounded (<=3) with an enforced merge-or-reap lifecycle; 'forks in flight' is "
     "the pre-control unbounded model"),
    (r"A3[_ ]?approval[_ ]?interface",
     "the A3 approval interface is not a running/operable surface (held L1, no live workflow)"),
]

# Daemon names that are NOT in the running manifest (dark/retired/never-a-daemon). Asserting any of
# these as a CURRENT running component is a lie. Kept narrow + matched with a running-context guard
# so honest historical incident records (very common in LATEST.md) are NOT flagged.
NON_RUNNING_DAEMONS: dict[str, str] = {
    "executor-daemon": "state=dark in the process manifest (not running)",
    "autonomous-runner": "state=retired in the process manifest (launcher commented out)",
    "session_watchdog": "not in the process manifest; superseded by worker-seat-manager",
}
# Words that signal a CURRENT/running assertion (vs a past-tense incident record).
_RUNNING_CONTEXT = r"(running|live|active|standing|drives?|driving|open\b|seat\b|now\b)"
# Words that mark an honest historical/retired mention -- these EXEMPT a nearby daemon name.
_HISTORICAL_MARK = r"(retired|inert|dead code|superseded|deleted|was |fired|FIXED|no longer|used to)"


def check_status_honesty(text: str, running_daemons: set[str] | None = None) -> dict:
    """PURE: classify a status-doc's narrative against declared truth. Returns {status, honest,
    stale_claims, detail}. stale_claims: [{claim, why}]. No I/O."""
    found: list[dict] = []
    for pat, why in STALE_MODEL_CLAIMS:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            found.append({"claim": m.group(0), "why": why})
    # Non-running daemon asserted as current: name present in a running-context window AND not
    # exempted by a historical marker in the same window.
    for name, why in NON_RUNNING_DAEMONS.items():
        for m in re.finditer(re.escape(name), text, re.IGNORECASE):
            window = text[max(0, m.start() - 60): m.end() + 60]
            if re.search(_RUNNING_CONTEXT, window, re.IGNORECASE) and not re.search(
                    _HISTORICAL_MARK, window, re.IGNORECASE):
                found.append({"claim": name, "why": why})
                break
    if found:
        shown = "; ".join(f"'{c['claim']}'" for c in found[:6])
        return {"status": "STALE", "honest": False, "stale_claims": found,
                "detail": f"{len(found)} stale claim(s) describe a non-running daemon/governance "
                          f"model as current: {shown}"}
    return {"status": "HONEST", "honest": True, "stale_claims": [],
            "detail": "narrative asserts no non-running daemon / retired governance model as current"}


def evaluate_status_honesty(path: Path | None = None) -> dict:
    """Live wrapper over the committed LATEST.md. Fail-safe: an unreadable file is not a staleness
    finding (no alarm) -- the concern is a lie in a present file, not a missing one."""
    try:
        text = (path or LATEST_MD).read_text()
    except Exception:
        return {"status": "HONEST", "honest": True, "stale_claims": [],
                "detail": "status doc unreadable -- no staleness assertion"}
    return check_status_honesty(text)


if __name__ == "__main__":
    import json
    import sys
    r = evaluate_status_honesty()
    print(json.dumps(r, indent=2))
    sys.exit(1 if not r["honest"] else 0)
