"""The guard the 2 Nov UKDS ruling asks for refuses microdata and lets an ordinary commit through.

Defect it names: a UK Data Service file (a download bundle, a study page, a .dta, or anything resolving into
~/ukds/) staged in this public repository and committed.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from tools import ukds_microdata_refusal as guard


def _repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return tmp_path


def _stage(repo: Path, rel: str, body: str = "x\n") -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    subprocess.run(["git", "add", rel], cwd=repo, check=True)


def test_the_guard_refuses_each_signature_and_passes_an_ordinary_commit(tmp_path, monkeypatch):
    repo = _repo(tmp_path)
    monkeypatch.chdir(repo)
    _stage(repo, "docs/market_research/a_page.md", "Cites UKDA-SN-9315 and SN 6614.\n")
    assert guard.main(["--staged"]) == 0, "a page citing a study number is not microdata"

    refused = [
        "data/UKDA-6614-tab/tab/ukhls/a_indresp.tab",
        "data/UKDA_Study_7215_Information.htm",
        "data/was_round_8.dta",
    ]
    for rel in refused:
        _stage(repo, rel)
    found = dict(guard.violations(guard.staged(repo), repo))
    assert set(found) == set(refused)
    assert guard.main(["--staged"]) == 1


def test_a_path_that_resolves_into_the_licensed_store_is_refused(tmp_path, monkeypatch):
    store = tmp_path / "ukds"
    store.mkdir()
    (store / "ukhls_w14.tab").write_text("pidp\n")
    monkeypatch.setattr(guard, "UKDS_HOME", store)
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "linked.tab").symlink_to(store / "ukhls_w14.tab")
    assert guard.reason("linked.tab", repo) is not None
    (repo / "fresh.csv").write_text("factor,loading\n")
    assert guard.reason("fresh.csv", repo) is None


def test_the_shapes_the_real_bundles_unpack_to_are_refused(tmp_path, monkeypatch):
    """The 9 Nov download: SERL ships only as `UKDA-8963-csv`, and every bundle's study page is `read<SN>.htm`.

    Defect it names: a format list that knew tab/stata/spss/sas let a copied SERL bundle through whole, and a
    study-page pattern for the older `UKDA_Study_<n>_Information.htm` name let the real pages through loose.
    """
    repo = _repo(tmp_path)
    monkeypatch.chdir(repo)
    refused = [
        "data/UKDA-8963-csv/csv/serl_daily_aggregated_statistics.csv",
        "read9315.htm",
        "9593_file_information.rtf",
        "was_r7_hhold.tab",
    ]
    for rel in refused:
        _stage(repo, rel)
    _stage(repo, "docs/reports/fitted_loadings.csv", "factor,loading\n")
    found = dict(guard.violations(guard.staged(repo), repo))
    assert set(found) == set(refused), "a fresh aggregate csv passes; every bundle shape is refused"
