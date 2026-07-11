"""Guards the Cloudflare cache-purge fix in .github/workflows/deploy-pages.yml
against the regression that caused it (ADVISOR_STEER_ESTIMATION_GAP.md,
2026-07-11): "add cache-purge coverage to the SURFACE_FRESHNESS invariant set
so a future hardcoded-path regression fails a test, not the director's
patience."

Real incident: the old purge step's file list was hardcoded to /state/* and
/shadow/* only, so a successful deploy touching /data/*.json or index.html
could silently leave stale content behind on Cloudflare's edge -- caught
while chasing an (unrelated) apparent staleness read on the thesis-chart fix.
Fixed to `purge_everything: true`, which is robust against new paths by
construction. This test is the narrow, buildable-now guard for that specific
regression; SURFACE_FRESHNESS_CLASS_FIX.md's Phase 2 (a general freshness-
alarm mechanism across all site surfaces) is the separate, larger follow-on
this belongs alongside once built.
"""
from pathlib import Path

import yaml

WORKFLOW_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / ".github" / "workflows" / "deploy-pages.yml"
)


def _load_workflow():
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def _purge_step(workflow):
    steps = workflow["jobs"]["deploy"]["steps"]
    for step in steps:
        if "purge_cache" in step.get("run", ""):
            return step
    return None


def test_workflow_file_exists():
    assert WORKFLOW_PATH.is_file()


def test_a_purge_cache_step_exists():
    workflow = _load_workflow()
    assert _purge_step(workflow) is not None, (
        "deploy-pages.yml must purge the Cloudflare cache after every deploy "
        "-- a deploy with no purge step can leave stale edge-cached content "
        "on any path indefinitely."
    )


def test_purge_step_purges_everything_not_a_hardcoded_file_list():
    """The regression this guards against: a purge step scoped to an explicit
    file list silently misses any path not on the list (real incident: /data/*
    and index.html were never covered). purge_everything is immune to this by
    construction -- a future edit that reverts to (or adds) a hardcoded
    "files": [...] purge scope should fail this test."""
    workflow = _load_workflow()
    step = _purge_step(workflow)
    run_script = step["run"]
    assert "purge_everything" in run_script, (
        "the purge step must use purge_everything, not a file-scoped purge "
        "-- a hardcoded file list will silently miss future paths (this is "
        "exactly how /data/*.json and index.html went uncovered before)"
    )
    assert '"files":[' not in run_script.replace(" ", ""), (
        "found a hardcoded file list back in the purge step's request body -- "
        "this is the regression the fix removed; every new site path added "
        "in the future would need to be remembered and added here, which is "
        "precisely the maintenance gap that caused the original incident"
    )


def test_deploy_workflow_triggers_on_site_and_project_state_changes():
    """Sanity-anchor: the purge step is only ever reached if the workflow
    still triggers on the paths that matter. Not the focus of this fix, but a
    silent trigger-path regression would make the purge fix moot."""
    workflow = _load_workflow()
    # YAML 1.1 parses the bare "on:" key as the boolean True, not the string
    # "on" -- a well-known GitHub Actions workflow YAML gotcha.
    paths = workflow[True]["push"]["paths"]
    assert "site/**" in paths
