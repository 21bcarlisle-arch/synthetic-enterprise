#!/usr/bin/env python3
"""Generate site/data/activity_cost.json -- the activity-based cost + utilisation
door-section (atom G11_activity_cost_utilisation,
docs/staging/done/ACTIVITY_COST_AND_UTILISATION.md).

Rendering, never authoring (SITE_CONSTITUTION rule 5): every figure is COMPUTED
by tools/activity_cost.py from real repo data (git history, the token log, the
escalation register) -- this script only reshapes that report into the shape the
Method-door section consumes and stamps it with the dashboard's build meta. No
number is transcribed or invented here.

DIAL, NOT TARGET (R12 anti-goal-seek): utilisation is a DIAGNOSTIC, never a
target -- carried through as `guardrail` on the JSON and rendered on the page.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from tools import activity_cost as ac

PROJECT = Path(__file__).resolve().parent.parent
DASHBOARD_PATH = PROJECT / "site" / "data" / "dashboard.json"
OUT_PATH = PROJECT / "site" / "data" / "activity_cost.json"


def _get(d, *path):
    cur = d
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def generate() -> bool:
    try:
        dashboard = json.loads(DASHBOARD_PATH.read_text())
    except Exception:
        dashboard = {}

    report = ac.build_report(PROJECT)
    m = report["metrics"]

    data = dict(
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        git_commit=_get(dashboard, "meta", "git_commit"),
        dashboard_generated_at=_get(dashboard, "meta", "generated_at"),
        phase=_get(dashboard, "build", "current_phase"),
        test_count=_get(dashboard, "build", "test_count"),
        framing=report["framing"],
        guardrail=report["guardrail"],
        generated_from=report["generated_from"],
        taxonomy=report["taxonomy"],
        # The five headline metrics, straight from activity_cost.compute_metrics.
        metrics=m,
        # Supporting breakdowns (for the taxonomy table on the page).
        time_attribution=report["time_attribution"],
        token_attribution=report["token_attribution"],
        commit_classification=report["commit_classification"],
        director_idle=report["director_idle"],
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(data, separators=(",", ":")))
    print("Written: " + str(OUT_PATH))
    return True


if __name__ == "__main__":
    generate()
