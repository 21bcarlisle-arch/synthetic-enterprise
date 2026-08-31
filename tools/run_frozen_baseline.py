"""Frozen-policy baseline replay: last-generation vs current company decisions.

FROZEN_POLICY_BASELINE_DESIGN.md option B (WEBSITE_AS_SHOWCASE.md tab 2,
SUPPLIER_TAB_OVERHAUL.md line 26 -- "the value of learning"): replays the
same historical decade twice through the real simulation entry point,
`simulation.run_phase4c_on_phase2b.main()`, once under CURRENT_POLICY (the
live retention/hedging decisions) and once under NAIVE_POLICY (the
superseded pre-Phase-14a/15b/43b decisions company/policy/decision_policy.py
reconstructs) -- everything else (market data, weather, customer roster,
acquisition/churn dice rolls) held identical. Both runs are real executions
of the same decision code, not a recompute from stored records: retention
and hedge decisions change realized settlement outcomes (churn timing,
revenue, margin), so a different policy produces a genuinely different book.

This is deliberately NOT run every sim cycle -- doubling a full-decade
simulation is expensive and "last-generation policy" is a fixed historical
reference point, not something that needs to be live every run. Call
`run_frozen_baseline()` on demand / periodically (see
`should_refresh_baseline()` for the staleness gate process_run_complete.py
uses).
"""

import fcntl
import json
from datetime import datetime, timezone
from pathlib import Path

from company.policy.decision_policy import CURRENT_POLICY, NAIVE_POLICY, policy_scope

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_DIR / "site" / "state" / "frozen_policy_baseline.json"

# Single-writer lock. The refresh is a multi-minute full-decade replay x2 with
# real risk-committee LLM calls; the publish path spawns it out-of-band every
# cycle it sees a stale baseline (see background/process_run_complete.py), so
# without a non-blocking lock overlapping replays would stack. A second caller
# takes the lock's absence as "a refresh is already running" and exits at once.
REFRESH_LOCK_PATH = PROJECT_DIR / "docs" / "observability" / ".frozen_baseline_refresh.lock"

# Refresh at most this often (seconds) -- a full decade replay runs the sim
# entry point twice, so this is a periodic artifact, not a per-cycle one.
REFRESH_INTERVAL_SECONDS = 7 * 24 * 60 * 60  # weekly


def run_phase4c(report_end: str | None = None, policy=None) -> dict:
    """The decade replay, imported at CALL time rather than at module import.

    IMPORTING THIS MODULE USED TO BUILD THE BOOK AND WRITE A PRODUCTION SURFACE.
    `from simulation.run_phase4c_on_phase2b import main` at line 29 pulled in
    `simulation.run_phase2b`, whose module body runs `CUSTOMERS = live_population()`,
    whose `_resolve_campaign` writes `docs/observability/book_growth_campaign.json`.
    So `import tools.run_frozen_baseline` -- an import, not a call -- assembled the whole
    population and stamped the evidence base.

    That was invisible until 2026-08-31, when `docs/observability` became a whole
    PROTECTED_SURFACE in `tests/production_surface_guard.py` (before that the directory was
    guarded file-by-file and this file was not on the list). From that commit every test that
    imported this module raised `ProductionWriteRefused`, which is exactly what the guard is
    for: the write was real and had been happening on every test run for months.

    The cost was not only the test isolation. `process_run_complete.
    _trigger_frozen_baseline_refresh_out_of_band` imports this module every publish cycle to
    ask ONE question -- is the baseline older than a week -- and paid a full population build
    to compare two mtimes.

    Kept as a module-level name, not inlined into `run_frozen_baseline`, because it is the seam
    the arms are faked at: `monkeypatch.setattr(rfb, "run_phase4c", ...)` is how both policy
    arms are driven in the tests without a real decade replay.
    """
    from simulation.run_phase4c_on_phase2b import main
    return main(report_end=report_end, policy=policy)


def _portfolio_metrics(result: dict) -> dict:
    """Extract the headline metrics used for the delta-EV comparison from one
    run_phase4c_on_phase2b.main() result."""
    phase2b = result["phase2b"]
    retention_log = phase2b.get("retention_log", [])
    retained = sum(1 for r in retention_log if r.get("outcome") == "retained")
    # retention_cost_events' amount_gbp is stored negated (cash-out convention,
    # matching saas/ledger.py's other cost events) -- negate back to a positive cost.
    retention_cost_total = -sum(
        e.get("amount_gbp", 0.0) for e in phase2b.get("retention_cost_events", [])
    )
    return {
        "enterprise_value_gbp": result["enterprise_value"]["portfolio"]["enterprise_value_gbp"],
        "account_count": result["enterprise_value"]["portfolio"]["account_count"],
        # BOTH ON `settled-realised`, AND NEITHER WITH A FALLBACK (2026-08-28, class
        # `figures_on_a_superseded_clock`). These were `.get(..., 0.0)`: a run whose output did
        # not carry the key reported GBP 0 for it, and a GBP 0 delta between two arms reads
        # exactly like two arms that performed identically -- R15's fail-open, in the file whose
        # only job is to say which policy did better. `[key]` raises instead, and the raise is
        # the finding. They are on the realised clock because `refresh_settlement_scalars`
        # re-derives these names from `all_records` after the arrears engine has mutated them,
        # so both arms are compared on what the world did rather than on what was provisioned.
        "total_net_gbp": phase2b["total_net"],
        "final_treasury_gbp": phase2b["final_treasury"],
        "retention_offers_made": len(retention_log),
        "retention_offers_retained": retained,
        "retention_cost_gbp": retention_cost_total,
        "churned_accounts": len(phase2b.get("churned_billing_accounts", [])),
    }


def run_frozen_baseline(report_end: str | None = None) -> dict:
    """Run the same historical window under CURRENT_POLICY and NAIVE_POLICY,
    returning both portfolios' headline metrics plus the delta.

    Both runs reuse the identical locally-keyed dice rolls (churn/acquisition
    are keyed by `f"{billing_account}_{term_start_str}"`, not one global
    seed -- see simulation/customer_events.py and run_phase2b.py's
    acquisition roll), so any divergence between the two runs is
    attributable to the policy change alone.

    Each arm runs inside `policy_scope(...)` as well as passing `policy=`
    (2026-08-12, WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10).
    The argument covers every field a consumer is handed; the scope covers the
    one field resolved without an argument -- the collections letter tone,
    which the arrears path reads per bill through the company's published
    seam and which therefore used to come out CURRENT in both arms. The
    sentence above ("attributable to the policy change alone") was false for
    `tone_mode` until the scope existed, and `run_phase2b.main` now refuses a
    policy argument that disagrees with the active scope, so a future arm
    cannot silently reacquire the defect.
    """
    with policy_scope(CURRENT_POLICY):
        current_result = run_phase4c(report_end=report_end, policy=CURRENT_POLICY)
    with policy_scope(NAIVE_POLICY):
        naive_result = run_phase4c(report_end=report_end, policy=NAIVE_POLICY)

    current = _portfolio_metrics(current_result)
    naive = _portfolio_metrics(naive_result)

    delta_ev_gbp = current["enterprise_value_gbp"] - naive["enterprise_value_gbp"]

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "report_end": report_end,
        "current_policy": current,
        "naive_policy": naive,
        "delta_ev_gbp": delta_ev_gbp,
        "delta_net_margin_gbp": current["total_net_gbp"] - naive["total_net_gbp"],
        # Which fields the two arms actually differed on. Present from 2026-08-12;
        # an artefact WITHOUT this key was generated before
        # WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10 was fixed, and
        # its naive arm ran the LIVE collections-letter tone, so its delta carries an
        # uncontrolled variable. That is a provenance fact about the artefact, so it
        # belongs in the artefact rather than only in a commit message.
        "arm_identity": {
            "differing_fields": sorted(
                f
                for f in CURRENT_POLICY.__dataclass_fields__
                if getattr(CURRENT_POLICY, f) != getattr(NAIVE_POLICY, f)
            ),
            "tone_resolved_from": "the run's policy scope (fixed 2026-08-12)",
        },
        "narrative": (
            "Replaying the same decade under the naive pre-learning policy "
            "(flat 5% retention discount, margin-only offer guard, no VaR-constrained "
            "hedge decision -- the pre-Phase-14a/15b/43b state) instead of today's "
            "decisions changes enterprise value by £{:,.0f} ({} offers made under "
            "current policy vs {} under naive, {} vs {} retained)."
        ).format(
            delta_ev_gbp,
            current["retention_offers_made"], naive["retention_offers_made"],
            current["retention_offers_retained"], naive["retention_offers_retained"],
        ),
    }


def should_refresh_baseline(path: Path = OUTPUT_PATH) -> bool:
    """True if no baseline exists yet, or the existing one is older than
    REFRESH_INTERVAL_SECONDS."""
    if not path.exists():
        return True
    try:
        existing = json.loads(path.read_text())
        generated_at = datetime.strptime(existing["generated_at"], "%Y-%m-%dT%H:%M:%SZ")
        generated_at = generated_at.replace(tzinfo=timezone.utc)
    except (json.JSONDecodeError, KeyError, ValueError, OSError):
        return True
    age_seconds = (datetime.now(timezone.utc) - generated_at).total_seconds()
    return age_seconds >= REFRESH_INTERVAL_SECONDS


def generate(path: Path = OUTPUT_PATH, force: bool = False) -> dict | None:
    """Refresh site/state/frozen_policy_baseline.json if stale (or `force`).

    Returns the baseline dict if regenerated, None if skipped as fresh OR if
    another refresh already holds the single-writer lock (REFRESH_LOCK_PATH).
    This is intended to be called OUT OF BAND (a detached subprocess) -- it must
    never run inside the synchronous publish path, whose bound it would blow.
    """
    if not force and not should_refresh_baseline(path):
        return None
    REFRESH_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REFRESH_LOCK_PATH, "w") as lock_fd:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            # Another refresh is already running -- do not stack a second
            # decade replay behind it; the in-flight one will write the file.
            return None
        try:
            baseline = run_frozen_baseline()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(baseline, indent=2))
            return baseline
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)


if __name__ == "__main__":
    import sys
    # `--if-stale` respects the weekly staleness gate (the out-of-band publish
    # trigger uses this); bare invocation forces a refresh (manual/CLI use).
    force = "--if-stale" not in sys.argv
    result = generate(force=force)
    if result is None:
        print(json.dumps({"skipped": True, "reason": "fresh-or-refresh-already-running"}))
    else:
        print(json.dumps(result, indent=2))
