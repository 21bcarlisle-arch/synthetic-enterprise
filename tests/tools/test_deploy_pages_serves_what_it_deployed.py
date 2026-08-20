"""Guards the post-deploy freshness control in .github/workflows/deploy-pages.yml.

REPLACES tests/tools/test_deploy_pages_cache_purge.py, which guarded a zone cache purge
deleted on 2026-08-20. The ORIGINAL CONCERN survives the replacement intact and is still
asserted here — ADVISOR_STEER_ESTIMATION_GAP.md, 2026-07-11: *"add cache-purge coverage to
the SURFACE_FRESHNESS invariant set so a future hardcoded-path regression fails a test, not
the director's patience."* A deploy must not be able to leave readers on stale content, and
the guard must not depend on a list anyone has to remember to update.

What changed is the mechanism, and why:

  * The purge had NEVER worked. `secrets.CLOUDFLARE_ZONE_ID` is empty, so every call went to
    `/zones//purge_cache`, got code 7003, printed `Purge FAILED` and exited 0. The old test
    asserted the step's TEXT contained `purge_everything` — which it did, faithfully, for
    every one of the months it was purging nothing. A test that reads a workflow's source
    can only ever prove intent; this file now also pins the properties that decide whether
    the step can FAIL when the intent is not met.
  * Purging could not have fixed the incident it was aimed at anyway. On 2026-08-20,
    `purge_everything` returned `success: true` twice while eight deleted pages went on
    being served, `age` climbing through both purges — they sit in Pages' own asset cache
    for the custom domain, which a zone purge does not reach.
  * `site/_headers` now carries the original job: `no-cache, must-revalidate` on `/`,
    `/*.html`, `/*/`, `/data/*.json`, `/state/*`, `/shadow/*`.

So the deploy no longer *acts hopefully*; it *checks*. The checker's own behaviour is proven
in tests/tools/test_assert_deployed_bytes_are_served.py — this file guards its WIRING, which
is the part a future edit can quietly remove.
"""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "deploy-pages.yml"
CHECKER = ROOT / "tools" / "assert_deployed_bytes_are_served.py"


def _load_workflow():
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def _steps():
    return _load_workflow()["jobs"]["deploy"]["steps"]


def _freshness_step():
    for step in _steps():
        if "assert_deployed_bytes_are_served" in step.get("run", ""):
            return step
    return None


def test_workflow_file_exists():
    assert WORKFLOW_PATH.is_file()


def test_the_deploy_verifies_what_a_reader_gets():
    """The property the deleted purge step was there to protect: a deploy may not finish
    without something establishing that readers are on the new content."""
    assert _freshness_step() is not None, (
        "deploy-pages.yml must verify the deployed bytes are what poesys.net serves. "
        "Without it a deploy can succeed while readers stay on a cached copy — which is "
        "exactly what happened for eight pages on 2026-08-20, undetected."
    )


def test_the_checker_it_calls_actually_exists():
    """FAIL-SILENT, R15: a workflow step calling a script that is not in the tree fails the
    deploy for the wrong reason, and a step calling one that was quietly renamed passes the
    wiring test while checking nothing."""
    assert CHECKER.is_file(), f"{CHECKER} is wired into the deploy but not in the tree"


def test_the_checked_set_is_derived_not_a_hardcoded_path_list():
    """The 2026-07-11 regression, restated for the new mechanism. The original incident was
    a purge scoped to a hand-written list that never covered /data/*.json or index.html.
    Any list someone has to remember to extend will go stale the same way, so the checker
    must derive its targets from what the push actually changed."""
    source = CHECKER.read_text()
    assert "git" in source and "diff" in source and "--name-status" in source, (
        "the freshness check must derive its targets from this push's diff. A hardcoded "
        "path list is the 2026-07-11 maintenance gap wearing a different mechanism."
    )


def test_every_fetch_the_deploy_makes_is_cache_busted():
    """A freshness check a stale copy can satisfy is theatre. Measured 2026-08-20: bare
    URLs returned an eight-hour-old ghost while the same URL with `?cb=` returned the truth
    every single time."""
    source = CHECKER.read_text()
    assert "cb=" in source, (
        "the post-deploy fetch must carry a cache-buster, or the check can be answered by "
        "the very cache it exists to see past"
    )


def test_the_purge_that_never_worked_has_not_come_back():
    """It reported success while doing nothing for its whole life, and it cannot reach the
    Pages asset cache where the real ghosts live. Re-adding it would restore a green light
    that means nothing — the FAIL-OPEN shape R15 names."""
    for step in _steps():
        assert "purge_cache" not in step.get("run", ""), (
            "the zone cache purge is deleted (2026-08-20): it never once succeeded "
            "(CLOUDFLARE_ZONE_ID is empty -> code 7003, exit 0) and a ZONE purge cannot "
            "evict Pages' custom-domain asset cache, which is where stale pages actually "
            "survive. Verify freshness instead of purging hopefully."
        )


def test_the_checker_can_see_the_base_of_the_push():
    """A shallow checkout has no base commit, so the diff — and therefore the whole checked
    set — would be empty, and the step would pass by finding nothing to check. That is the
    FAIL-OPEN this control exists to not be."""
    checkout = next(s for s in _steps() if "checkout" in str(s.get("uses", "")))
    assert str(checkout.get("with", {}).get("fetch-depth")) == "0", (
        "the deploy checkout must be unshallow; otherwise the freshness check diffs against "
        "nothing, finds nothing changed, and reports success"
    )


def test_deploy_workflow_triggers_on_site_and_project_state_changes():
    """Sanity-anchor, carried over: the check is only ever reached if the workflow still
    triggers on the paths that matter."""
    # YAML 1.1 parses the bare "on:" key as the boolean True, not the string "on" -- a
    # well-known GitHub Actions workflow YAML gotcha.
    paths = _load_workflow()[True]["push"]["paths"]
    assert "site/**" in paths
