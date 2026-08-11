"""Tests for `tools/build_projections.py` — atom `G12_queryable_projections`.

The three properties the atom's exit tests name, each proven BOTH WAYS per R15: the
control passes on the real mechanism, and a mutation into the mechanism's own named
defect makes it fail. A control that cannot fail is worse than none.

  1. derived from COMMITTED truth   → `test_the_working_tree_does_not_reach_the_store`
  2. REBUILT, not mutated           → `test_a_hand_edit_to_the_store_is_destroyed_...`
                                      mutant: `test_r15_the_rebuild_control_fires_...`
  3. FAIL-CLOSED, never zero rows   → `test_an_unreadable_source_fails_closed_...`
                                      mutant: `test_r15_the_fail_closed_control_fires_...`
  4. envelope READ, not re-derived  → `test_the_scale_envelope_follows_the_artefact`

The envelope tests use a PERTURBATION ORACLE rather than asserting the live numbers: the
probe's figures are changed in the fixture and the store must move with them. A test that
pinned 5144 would pass just as happily against a hardcoded constant, which is the exact
re-derivation the atom forbids.
"""

from __future__ import annotations

import dataclasses
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools import build_projections as bp  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------- fixtures


def _atoms_fixture() -> list[dict]:
    return [
        {
            "id": "Z1_first",
            "title": "the first atom",
            "lane": "G_data_learning",
            "value_stream": "close_to_learn",
            "epoch": 2,
            "level_current": 0,
            "level_target": 2,
            "loop_stage": "build",
            "dial_inherited": 2,
            "provenance": "director_ruling",
            "depends_on": [],
            "couples_with": ["Z2_second"],
            "file_scope": ["tools/x.py"],
            "expert_hour": {"status": "not_attempted"},
            "real_world_twin": "a thing that exists",
        },
        {
            "id": "Z2_second",
            "title": "the second atom",
            "lane": "F_risk",
            "epoch": 1,
            "level_current": 2,
            "level_target": 3,
            "loop_stage": "harden",
            "provenance": "proposal",
        },
    ]


def _runs_fixture() -> list[dict]:
    return [
        {
            "git_hash": "abc123def",
            "generated_at": "2026-08-01T00:00:00+00:00",
            "net_margin_gbp": 1000.5,
            "executive_summary": "a run happened",
            "headline_metrics": {
                "financial": {"revenue_gbp": 9000.0, "gross_margin_gbp": 4000.0, "net_margin_pct": 8.1},
                "customers": {"total_churned": 5, "enterprise_value_gbp": 72.0},
                "operations": {"bills_total": 1557},
                "risk": {"survived": True},
            },
        }
    ]


def _gaps_fixture() -> dict:
    return {
        "W9_example": {
            "twin_atom_id": "C1_example",
            "metric": "prediction",
            "gap": 1.04,
            "raw_gap": 2275.9,
            "g0": 2189.8,
            "baseline": "no-skill",
            "measured_at": "2026-08-11T03:06:27+00:00",
            "run_git_commit": "696dcf06e",
            "note": "a gap",
            "components": {"a": 1},
        }
    }


def _probe_fixture(**overrides) -> dict:
    report = {
        "generated_at": "2026-08-10T17:07:43+00:00",
        "config": {"mem_cap_mb": 2048},
        "analysis": {
            "first_seam_to_tear": "settlement_build",
            "per_stage": {
                "settlement_build": {
                    "survived_max_n": 20,
                    "projected_tear_n": 69,
                    "tear_n": 100,
                    "tear_outcome": "memory_error",
                    "marginal_rss_kb_per_customer": 22928.286,
                },
                "run_output_serialize": {
                    "survived_max_n": 1000,
                    "projected_tear_n": 5144,
                    "tear_n": 10000,
                    "tear_outcome": "memory_error",
                    "marginal_rss_kb_per_customer": 398.543,
                },
            },
        },
    }
    report.update(overrides)
    return report


def _write(repo: Path, relpath: str, payload) -> Path:
    path = repo / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    if relpath.endswith(".yaml"):
        path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    return path


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )
    return proc.stdout


def _commit_all(repo: Path, message: str = "fixture") -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A throwaway git repo carrying the real SOURCES paths, committed."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "test")
    _write(root, "docs/design/maturity_map.yaml", _atoms_fixture())
    _write(root, "docs/observability/run_history.json", _runs_fixture())
    _write(root, "docs/observability/coupled_gap_ledger.json", _gaps_fixture())
    _write(root, bp.SCALE_PROBE_RELPATH, _probe_fixture())
    _commit_all(root, "fixtures")
    return root


def _store(repo: Path) -> sqlite3.Connection:
    return sqlite3.connect(str(repo / bp.STORE_RELPATH))


def _rows(repo: Path, sql: str) -> list[tuple]:
    conn = _store(repo)
    try:
        return list(conn.execute(sql))
    finally:
        conn.close()


def _tables(repo: Path) -> set[str]:
    return {
        name for (name,) in _rows(repo, "SELECT name FROM sqlite_master WHERE type='table'")
    }


# ----------------------------------------------------------- 1. committed truth


def test_the_store_is_built_and_queryable(repo: Path):
    report = bp.build(repo=repo)
    assert report["status"] == "ok", report
    assert (repo / bp.STORE_RELPATH).exists()
    assert _tables(repo) >= {"atoms", "runs", "coupled_gaps", "scale_envelope", "source_status", "build_meta"}
    assert _rows(repo, "SELECT id FROM atoms ORDER BY id") == [("Z1_first",), ("Z2_second",)]
    assert _rows(repo, "SELECT git_hash FROM runs") == [("abc123def",)]
    assert _rows(repo, "SELECT atom_id FROM coupled_gaps") == [("W9_example",)]


def test_the_working_tree_does_not_reach_the_store(repo: Path):
    """An edit that is not committed is not truth, and must not be projected as such."""
    _write(repo, "docs/design/maturity_map.yaml", _atoms_fixture() + [{"id": "Z3_uncommitted"}])
    bp.build(repo=repo)
    assert _rows(repo, "SELECT id FROM atoms WHERE id='Z3_uncommitted'") == []

    _commit_all(repo, "now it is truth")
    bp.build(repo=repo)
    assert _rows(repo, "SELECT id FROM atoms WHERE id='Z3_uncommitted'") == [("Z3_uncommitted",)]


def test_the_store_records_the_commit_it_was_derived_from(repo: Path):
    report = bp.build(repo=repo)
    meta = dict(_rows(repo, "SELECT key, value FROM build_meta"))
    assert meta["head_sha"] == report["head_sha"] == _git(repo, "rev-parse", "HEAD").strip()
    assert meta["rows_total"] == str(report["rows_total"])


# ------------------------------------------------------- 2. rebuilt, not mutated


def _hand_edit(repo: Path) -> None:
    conn = _store(repo)
    try:
        conn.execute("INSERT INTO atoms (id, title) VALUES ('Z9_hand_edited', 'not from any source')")
        conn.commit()
    finally:
        conn.close()


def test_a_hand_edit_to_the_store_is_destroyed_by_the_next_build(repo: Path):
    bp.build(repo=repo)
    _hand_edit(repo)
    assert _rows(repo, "SELECT id FROM atoms WHERE id='Z9_hand_edited'") == [("Z9_hand_edited",)]

    bp.build(repo=repo)

    assert _rows(repo, "SELECT id FROM atoms WHERE id='Z9_hand_edited'") == []
    assert _rows(repo, "SELECT id FROM atoms ORDER BY id") == [("Z1_first",), ("Z2_second",)]


def _mutate_to_in_place_builder(monkeypatch, *, idempotent: bool) -> None:
    """Apply the one named defect this control exists for: a builder that opens the LIVE
    store and writes into it, instead of rebuilding a new file and swapping it in.

    `idempotent=False` is the naive version. `idempotent=True` is the dangerous one —
    somebody makes the in-place builder re-runnable with IF NOT EXISTS / INSERT OR
    REPLACE, and divergent rows then survive every rebuild in silence.
    """

    def in_place(store: Path):
        store.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(store)), store

    monkeypatch.setattr(bp, "_open_new_store", in_place)
    if not idempotent:
        return

    def create(conn, table, columns):
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)})")

    def insert(conn, table, columns, rows):
        placeholders = ", ".join("?" * len(list(columns)))
        conn.executemany(f"INSERT OR REPLACE INTO {table} VALUES ({placeholders})", rows)

    monkeypatch.setattr(bp, "_create", create)
    monkeypatch.setattr(bp, "_insert", insert)


def test_r15_the_rebuild_control_fires_on_the_naive_in_place_builder(repo: Path, monkeypatch):
    bp.build(repo=repo)
    _hand_edit(repo)

    _mutate_to_in_place_builder(monkeypatch, idempotent=False)
    with pytest.raises(sqlite3.OperationalError):
        bp.build(repo=repo)

    # The property the control asserts is FALSE under the defect: the hand-edit is still
    # there, so `test_a_hand_edit_...` would fail. The control discriminates.
    assert _rows(repo, "SELECT id FROM atoms WHERE id='Z9_hand_edited'") == [("Z9_hand_edited",)]


def test_r15_the_rebuild_control_fires_on_the_silent_in_place_builder(repo: Path, monkeypatch):
    bp.build(repo=repo)
    _hand_edit(repo)

    _mutate_to_in_place_builder(monkeypatch, idempotent=True)
    report = bp.build(repo=repo)

    # No error at all this time — the build reports success while a row nobody sourced
    # sits alongside the real ones. This is the divergent second source of truth.
    assert report["status"] == "ok"
    assert _rows(repo, "SELECT id FROM atoms ORDER BY id") == [
        ("Z1_first",),
        ("Z2_second",),
        ("Z9_hand_edited",),
    ]


def test_the_rebuilding_scratch_file_does_not_survive_a_build(repo: Path):
    bp.build(repo=repo)
    scratch = (repo / bp.STORE_RELPATH).with_name(bp.STORE_RELPATH.name + ".rebuilding")
    assert not scratch.exists()


# ----------------------------------------------------------- 3. fail-closed


def test_an_unreadable_source_fails_closed_and_leaves_the_store_untouched(repo: Path):
    bp.build(repo=repo)
    before = (repo / bp.STORE_RELPATH).read_bytes()

    _git(repo, "rm", "-q", "docs/observability/coupled_gap_ledger.json")
    _commit_all(repo, "the ledger is gone")
    report = bp.build(repo=repo)

    assert report["status"] == "failed_closed"
    assert [u["name"] for u in report["unknown"]] == ["coupled_gap_ledger"]
    assert (repo / bp.STORE_RELPATH).read_bytes() == before, "the live store was modified"


def test_an_unreadable_source_publishes_no_table_rather_than_zero_rows(repo: Path):
    """The named fail-open shape: an empty table reads downstream as 'measured: none'."""
    _git(repo, "rm", "-q", "docs/observability/coupled_gap_ledger.json")
    _commit_all(repo, "the ledger is gone")

    assert bp.build(repo=repo)["status"] == "failed_closed"
    assert not (repo / bp.STORE_RELPATH).exists(), "a store was published without the ledger"


def test_a_source_that_parses_to_nothing_is_unknown_not_an_empty_table(repo: Path):
    """Present, readable, well-formed — and empty. Still UNKNOWN, never zero rows."""
    _write(repo, "docs/observability/coupled_gap_ledger.json", {})
    _commit_all(repo, "an empty ledger")

    report = bp.build(repo=repo)
    assert report["status"] == "failed_closed"
    assert "empty ledger" in report["unknown"][0]["reason"]


def test_a_malformed_source_is_unknown_not_a_crash(repo: Path):
    (repo / "docs/observability/run_history.json").write_text("{not json", encoding="utf-8")
    _commit_all(repo, "a malformed history")

    report = bp.build(repo=repo)
    assert report["status"] == "failed_closed"
    assert report["unknown"][0]["name"] == "run_history"


def test_r15_the_fail_closed_control_fires_on_the_fail_open_defect(repo: Path, monkeypatch):
    """Mutate the two guards into the defaults-to-empty variant they exist to prevent."""
    _git(repo, "rm", "-q", "docs/observability/coupled_gap_ledger.json")
    _commit_all(repo, "the ledger is gone")

    real_read = bp.read_committed

    def read_or_empty(repo_, relpath, rev="HEAD"):
        try:
            return real_read(repo_, relpath, rev)
        except bp.SourceUnreadable:
            return b"{}"

    def gaps_without_the_empty_guard(doc):
        return []

    monkeypatch.setattr(bp, "read_committed", read_or_empty)
    monkeypatch.setattr(
        bp,
        "SOURCES",
        tuple(
            dataclasses.replace(s, extract=gaps_without_the_empty_guard)
            if s.name == "coupled_gap_ledger"
            else s
            for s in bp.SOURCES
        ),
    )

    report = bp.build(repo=repo)

    # Under the defect the build reports success and publishes the missing ledger as an
    # empty table — indistinguishable downstream from "we looked, there is nothing".
    assert report["status"] == "ok"
    assert _rows(repo, "SELECT count(*) FROM coupled_gaps") == [(0,)]


def test_source_status_records_the_sha_of_every_blob_it_read(repo: Path):
    bp.build(repo=repo)
    statuses = _rows(repo, "SELECT name, status, sha256, row_count FROM source_status ORDER BY name")
    assert {row[0] for row in statuses} == {
        "coupled_gap_ledger",
        "maturity_map",
        "run_history",
        "scale_probe_10k",
    }
    for name, status, sha, row_count in statuses:
        assert status == "ok"
        assert sha and len(sha) == 64, name
        assert row_count > 0, name


# ------------------------------------------------ 4. the envelope is READ, not derived


def test_the_scale_envelope_is_projected_for_both_seams(repo: Path):
    bp.build(repo=repo)
    rows = _rows(repo, "SELECT seam, role, unit FROM scale_envelope ORDER BY role")
    assert rows == [
        ("settlement_build", "pipeline_first_tear", "customers"),
        ("run_output_serialize", "store_envelope", "customers"),
    ]


def test_the_scale_envelope_follows_the_artefact(repo: Path):
    """The perturbation oracle: change the probe's measured figures, and the store must
    move with them. A hardcoded ceiling passes the equality test and fails this one."""
    bp.build(repo=repo)
    assert _rows(
        repo, "SELECT ceiling_customers, graduation_trigger_customers FROM scale_envelope WHERE role='store_envelope'"
    ) == [(1000, 5144)]

    perturbed = _probe_fixture()
    perturbed["analysis"]["per_stage"]["run_output_serialize"]["survived_max_n"] = 31337
    perturbed["analysis"]["per_stage"]["run_output_serialize"]["projected_tear_n"] = 424242
    _write(repo, bp.SCALE_PROBE_RELPATH, perturbed)
    _commit_all(repo, "a re-measured probe")

    bp.build(repo=repo)
    assert _rows(
        repo, "SELECT ceiling_customers, graduation_trigger_customers FROM scale_envelope WHERE role='store_envelope'"
    ) == [(31337, 424242)]


def test_the_envelope_names_the_seam_the_probe_itself_called_first_to_tear(repo: Path):
    perturbed = _probe_fixture()
    perturbed["analysis"]["first_seam_to_tear"] = "population_draw"
    perturbed["analysis"]["per_stage"]["population_draw"] = {
        "survived_max_n": 1000,
        "projected_tear_n": 1810282,
        "tear_n": 10000,
        "tear_outcome": "error",
        "marginal_rss_kb_per_customer": 1.146,
    }
    _write(repo, bp.SCALE_PROBE_RELPATH, perturbed)
    _commit_all(repo, "a different first tear")

    bp.build(repo=repo)
    assert _rows(repo, "SELECT seam FROM scale_envelope WHERE role='pipeline_first_tear'") == [
        ("population_draw",)
    ]


@pytest.mark.parametrize("field", ["survived_max_n", "projected_tear_n", "tear_outcome"])
def test_an_unmeasured_envelope_field_is_unknown_not_zero(repo: Path, field: str):
    """A stage the probe never reached is an UNKNOWN cost, not a zero."""
    stripped = _probe_fixture()
    del stripped["analysis"]["per_stage"]["run_output_serialize"][field]
    _write(repo, bp.SCALE_PROBE_RELPATH, stripped)
    _commit_all(repo, "an unmeasured field")

    report = bp.build(repo=repo)
    assert report["status"] == "failed_closed"
    assert report["unknown"][0]["name"] == "scale_probe_10k"
    assert field in report["unknown"][0]["reason"]


def test_the_envelope_records_the_probe_artefacts_own_sha(repo: Path):
    bp.build(repo=repo)
    (sha,) = {row[0] for row in _rows(repo, "SELECT source_sha256 FROM scale_envelope")}
    blob_sha = _rows(repo, "SELECT sha256 FROM source_status WHERE name='scale_probe_10k'")[0][0]
    assert sha == blob_sha


# ------------------------------------------------------------ the live repository


def test_the_probe_artefact_the_envelope_reads_is_tracked():
    """The class this atom nearly repeated: a control fail-closed on evidence its own
    producer never lands. `tools/scale_probe_10k.py` writes this report; until it was
    committed, every build of this store failed closed on day one.
    """
    proc = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "--error-unmatch", bp.SCALE_PROBE_RELPATH],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"{bp.SCALE_PROBE_RELPATH} is untracked — the scale envelope's only source is "
        "invisible to a clean checkout"
    )


def test_the_store_is_never_committed():
    """A projection committed into history is the second source of truth this atom exists
    to prevent. It must be rebuildable and ignored, not versioned."""
    ignored = subprocess.run(
        ["git", "-C", str(REPO), "check-ignore", "-q", str(bp.STORE_RELPATH)]
    )
    assert ignored.returncode == 0, f"{bp.STORE_RELPATH} is not gitignored"

    tracked = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "--error-unmatch", str(bp.STORE_RELPATH)],
        capture_output=True,
    )
    assert tracked.returncode != 0, f"{bp.STORE_RELPATH} is tracked"


def test_the_live_repository_builds_from_its_own_committed_truth():
    """The happy path L2 asks for, on the real artefacts rather than a fixture."""
    report = bp.build(repo=REPO)
    assert report["status"] == "ok", report
    assert report["rows_total"] > 0
    assert {s["name"] for s in report["sources"]} == {
        "maturity_map",
        "run_history",
        "coupled_gap_ledger",
    }


def test_the_query_entrypoint_reads_the_live_store_back():
    bp.build(repo=REPO)
    rows = bp.query("SELECT count(*) FROM atoms", repo=REPO)
    assert rows[0][0] > 0
    assert bp.query("SELECT value FROM build_meta WHERE key='derived_from'", repo=REPO)[0][0].startswith(
        "committed blobs only"
    )


def test_the_cli_exits_nonzero_when_the_build_fails_closed(repo: Path, monkeypatch, capsys):
    """rc alone is not evidence a gate ran — so the CLI also says WHICH source was UNKNOWN."""
    monkeypatch.setattr(bp, "REPO_ROOT", repo)
    _git(repo, "rm", "-q", "docs/observability/run_history.json")
    _commit_all(repo, "the history is gone")

    assert bp.main([]) == 2
    err = capsys.readouterr().err
    assert "UNKNOWN source run_history" in err
    assert "FAILED CLOSED" in err


def test_the_cli_builds_and_reports(repo: Path, monkeypatch, capsys):
    monkeypatch.setattr(bp, "REPO_ROOT", repo)

    assert bp.main(["--report"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "ok"
    assert report["rows_total"] > 0

    assert bp.main(["--query", "SELECT id FROM atoms ORDER BY id"]) == 0
    assert capsys.readouterr().out.split() == ["Z1_first", "Z2_second"]
