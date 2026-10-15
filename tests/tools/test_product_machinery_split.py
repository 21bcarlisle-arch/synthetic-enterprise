"""The product/machinery classifier, each test named by the defect it catches.

Director canon 2026-09-05 §2 supplies the definition and it is about the WORLD, not the folders:
"if a real energy supplier or a real market would have it, it is product"; machinery is "what
exists only because this is built by an autonomous harness".
"""
from __future__ import annotations

from tools import product_machinery_split as pms


def test_the_world_and_the_supplier_are_product():
    for path in ("simulation/population_draw.py", "company/pricing/tariff.py", "saas/opex_ledger.py"):
        assert pms.classify_path(path) == "product", path


def test_the_harness_is_machinery():
    for path in ("background/supervisor.py", "tools/orphan_ratchet.py",
                 "docs/observability/agent_status.json", "docs/staging/SEAT_FINDING_X.md"):
        assert pms.classify_path(path) == "machinery", path


def test_the_website_is_presentation_and_counts_as_neither():
    """Canon §2, an explicit ruling: 'The website is presentation. It publishes product but is not
    product.' Folding it into product would make a busy site week read as product delivery."""
    assert pms.classify_path("site/index.html") == "neither"


def test_a_machinery_path_under_docs_beats_the_broader_docs_rule():
    """THE ORDERING DEFECT. `docs/observability/` and `docs/staging/` are machinery and both sit
    under `docs/`, which is 'neither'. A classifier that tested the broad prefix first would file
    every finding and every status artefact as 'neither' and the machinery count would collapse."""
    assert pms.classify_path("docs/observability/x.json") == "machinery"
    assert pms.classify_path("docs/design/SOME_DESIGN.md") == "neither"


def test_a_test_follows_its_subject_rather_than_being_its_own_category():
    """Otherwise every test in the repo lands in one bucket and the split measures nothing about
    what the work was actually on."""
    assert pms.classify_path("tests/company/test_billing.py") == "product"
    assert pms.classify_path("tests/background/test_supervisor.py") == "machinery"


def test_a_commit_touching_any_product_path_counts_as_product():
    """Deliberately generous to product: the failure being measured is product work not happening,
    and a proportional rule lets a real product change be outvoted by the machinery files its own
    landing touched (an orphan baseline, a status artefact, a finding)."""
    verdict = pms.classify_commit([
        "simulation/population_draw.py",
        "background/supervisor.py", "tools/orphan_ratchet.py",
        "docs/observability/x.json", "docs/staging/f.md",
    ])
    assert verdict == "product"


def test_a_commit_with_no_product_path_is_machinery_so_the_generosity_has_a_limit():
    """The other branch. Without it, `classify_commit` could return 'product' unconditionally and
    the test above would still pass."""
    assert pms.classify_commit(["background/supervisor.py", "docs/design/X.md"]) == "machinery"


def test_a_thin_sample_reports_not_enough_to_judge_rather_than_a_zero_share():
    """FAIL-SILENT GUARD. One machinery commit in a quiet hour is a 0% product share, and a control
    that files a finding on that is a control that cries wolf until it is switched off. 'Not enough
    work to judge' and 'the ratio is fine' must be distinguishable states."""
    thin = pms.split(window=1)
    assert thin["enough_to_judge"] is False
    assert thin["below_floor"] is False, "a thin sample must not trip the floor"


def test_the_floor_is_a_target_and_is_above_everything_the_record_contains():
    """Keyed to the PROPERTY, not to today's answer. Measured over the trailing 2000 commits the
    product share never exceeded 28.74% and its median was 16.03%; a floor drawn from that
    distribution would go green on the pathology the canon exists to stop."""
    assert pms.PRODUCT_SHARE_FLOOR > 0.2074, (
        "the floor must sit above the measured p75 of 20.74%, or it ratifies the standing state"
    )


def _repo_with_commit(tmp_path, rel):
    import subprocess
    env = ["-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)

    def commit(path):
        f = tmp_path / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(path)
        subprocess.run(["git", *env, "add", path], cwd=tmp_path, check=True)
        subprocess.run(["git", *env, "commit", "-q", "-m", path], cwd=tmp_path, check=True)

    commit(rel)
    return commit


def test_the_trailing_log_is_read_once_per_head_so_every_draw_does_not_pay_for_git_log(
        tmp_path, monkeypatch):
    """The supervisor asks the floor on every draw. Re-running `git log --name-only` each time was
    half of a draw's cost and pushed the operational layer past its budget (2026-10-15)."""
    pms._LOG_CACHE.clear()
    _repo_with_commit(tmp_path, "company/a.py")
    first = pms.split(window=5, repo=tmp_path)
    real_run = pms.subprocess.run
    logs = []

    def counting_run(argv, *a, **kw):
        if argv[:2] == ["git", "log"]:
            logs.append(argv)
        return real_run(argv, *a, **kw)

    monkeypatch.setattr(pms.subprocess, "run", counting_run)
    assert pms.split(window=5, repo=tmp_path) == first
    assert logs == [], "a second split at the same HEAD re-ran git log"


def test_a_new_commit_is_read_fresh_so_the_cache_never_serves_a_stale_split(tmp_path):
    """The other side: a cache keyed on anything weaker than HEAD would pass the test above and
    report yesterday's ratio for as long as the process lived."""
    pms._LOG_CACHE.clear()
    commit = _repo_with_commit(tmp_path, "company/a.py")
    before = pms.split(window=5, repo=tmp_path)
    commit("background/b.py")
    after = pms.split(window=5, repo=tmp_path)
    assert (before["product"], before["machinery"]) == (1, 0)
    assert (after["product"], after["machinery"]) == (1, 1)
