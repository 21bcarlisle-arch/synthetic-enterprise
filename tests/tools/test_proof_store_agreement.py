"""The Proof door's committed-store check (atom `G13_projection_consumers`).

`tools/generate_proof_data.py::_store_agreement` grades the coupled-gap figures the
public door publishes against `docs/observability/projections.sqlite`, which
`tools/build_projections.py` rebuilds from COMMITTED blobs only. The door generates
from the working tree; the store cannot see the working tree. So the check answers a
question the door could not previously ask about itself: **is the number I am
publishing in any commit?**

R15 — a control counts as evidence only if a mutation proves it FIRES on its own
named defect, and only if it is not a tautology, not fail-open and not fail-silent.
The named defects:

  D1  a published gap figure that differs from the committed one   -> disagreement, red.
  D2  a published pair that no commit carries at all               -> named, red.
  D3  a committed pair the door has silently stopped rendering     -> named, red.
  D4  the store is missing/unreadable                              -> available=False,
      `agrees` False, rendered as a FAILED check and never as agreement.

INDEPENDENCE (the tautology guard). The two sides must not be the same arithmetic:
the door side is built by `_coupled_gaps` off `background.coupled_triad.load_gap_ledger`
(the working-tree JSON), the store side by a SQL read of a SQLite file produced by a
separate module from `git cat-file` output. `test_the_two_sides_do_not_share_a_reader`
pins that, because an independence claim nobody exercises is the commonest way this
control could quietly become a mirror.

WHAT THIS CHECK DELIBERATELY DOES NOT COMPARE, and why the omission is itself tested
(`test_a_churning_provenance_stamp_does_not_fire_the_alarm`): `measured_at`,
`run_git_commit` and `components` are rewritten by every re-measurement. Measured on
the live ledger 2026-08-19, the working tree and HEAD differed on exactly one entry and
on exactly those three keys, every figure identical. Including them would have made the
control red once per run for a reason that is not a defect.
"""

from __future__ import annotations

import sqlite3

import pytest

import tools.build_projections as bp
import tools.generate_proof_data as gpd


def _rows(overrides=None):
    """A door-side panel row set shaped exactly like `_coupled_gaps` emits."""
    row = dict(
        world_atom="W2_11_payment_behaviour_source",
        company_atom="D5_ledger",
        metric="missed_failure_rate",
        value=0.42,
        raw_gap=0.0,
        baseline_g0=1.0,
        baseline_desc="blind prior",
        normalisation="reference",
        raw_gap_is="one of two averaged directions",
    )
    row.update(overrides or {})
    return [row]


def _store(tmp_path, rows):
    """Build a minimal store with the columns the check reads."""
    path = tmp_path / "projections.sqlite"
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE coupled_gaps (atom_id TEXT PRIMARY KEY, metric TEXT, gap REAL, "
        "raw_gap REAL, g0 REAL, baseline TEXT, normalisation TEXT, raw_gap_is TEXT)"
    )
    conn.executemany(
        "INSERT INTO coupled_gaps VALUES (?,?,?,?,?,?,?,?)",
        [
            (
                r["atom_id"], r.get("metric"), r.get("gap"), r.get("raw_gap"), r.get("g0"),
                r.get("baseline"), r.get("normalisation"), r.get("raw_gap_is"),
            )
            for r in rows
        ],
    )
    conn.execute("CREATE TABLE build_meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.executemany(
        "INSERT INTO build_meta VALUES (?,?)",
        [("head_sha", "d9a88e9957a6f2e126055fca62c5d059738b862e"), ("schema_version", "2")],
    )
    conn.commit()
    conn.close()
    return path


def _committed(overrides=None):
    row = dict(
        atom_id="W2_11_payment_behaviour_source",
        metric="missed_failure_rate",
        gap=0.42,
        raw_gap=0.0,
        g0=1.0,
        baseline="blind prior",
        normalisation="reference",
        raw_gap_is="one of two averaged directions",
    )
    row.update(overrides or {})
    return [row]


@pytest.fixture()
def point_at(monkeypatch, tmp_path):
    def _point(store_path):
        monkeypatch.setattr(bp, "REPO_ROOT", store_path.parent)
        monkeypatch.setattr(bp, "STORE_RELPATH", type(store_path)(store_path.name))
    return _point


# --------------------------------------------------------------------------- baseline
def test_agrees_when_the_published_figure_is_the_committed_one(point_at, tmp_path):
    point_at(_store(tmp_path, _committed()))
    out = gpd._store_agreement(_rows())
    assert out["available"] is True
    assert out["agrees"] is True, out
    assert out["disagreements"] == []
    assert out["rendered_pairs"] == 1 and out["committed_pairs"] == 1
    # The sha is carried onto the door so a reader can see WHICH commit was checked.
    assert out["store_head_sha"].startswith("d9a88e99")


# --------------------------------------------------------------------------- D1
@pytest.mark.parametrize(
    "field,store_field,mutated",
    [
        ("value", "gap", 0.99),
        ("raw_gap", "raw_gap", 0.5),
        ("baseline_g0", "g0", 2.0),
        ("metric", "metric", "something_else"),
        ("normalisation", "normalisation", "absolute"),
        ("raw_gap_is", "raw_gap_is", "the headline"),
    ],
)
def test_d1_a_published_figure_that_is_not_the_committed_one_fires(
    point_at, tmp_path, field, store_field, mutated
):
    """MUTATION: move the door's figure away from the commit, one field at a time.

    Every checked field is mutated independently — a control tested only on `gap`
    would pass while silently ignoring the five other fields it claims to check.
    """
    point_at(_store(tmp_path, _committed()))
    out = gpd._store_agreement(_rows({field: mutated}))
    assert out["agrees"] is False, f"{field} mutation did not fire"
    assert [d["field"] for d in out["disagreements"]] == [field]
    assert out["disagreements"][0]["published"] == mutated


# --------------------------------------------------------------------------- D2
def test_d2_a_published_pair_in_no_commit_is_named(point_at, tmp_path):
    point_at(_store(tmp_path, _committed()))
    rows = _rows() + _rows({"world_atom": "W9_invented_pair"})
    out = gpd._store_agreement(rows)
    assert out["agrees"] is False
    # Named, not merely counted: the reader needs to know WHICH figure is unbacked.
    assert out["uncommitted_pairs"] == ["W9_invented_pair"]


# --------------------------------------------------------------------------- D3
def test_d3_a_committed_pair_the_door_stopped_rendering_is_named(point_at, tmp_path):
    point_at(_store(tmp_path, _committed() + _committed({"atom_id": "W3_dropped"})))
    out = gpd._store_agreement(_rows())
    assert out["agrees"] is False
    assert out["unrendered_pairs"] == ["W3_dropped"]


# --------------------------------------------------------------------------- D4
def test_d4_an_unreadable_store_is_a_failed_check_never_agreement(point_at, tmp_path):
    """FAIL-SILENT guard: an unavailable check must not read as a clean one."""
    point_at(tmp_path / "does_not_exist.sqlite")
    out = gpd._store_agreement(_rows())
    assert out["available"] is False
    # The sharp assertion: `agrees` is False, so no consumer can treat the absent
    # store as confirmation. A control that reports success when it could not run is
    # the exact fail-silent shape R15 names.
    assert out["agrees"] is False
    assert "unreadable" in out["reason"] or "not importable" in out["reason"]


def test_d4b_a_store_missing_the_table_is_a_failed_check(point_at, tmp_path):
    path = tmp_path / "projections.sqlite"
    sqlite3.connect(path).close()  # a real file, no tables
    point_at(path)
    out = gpd._store_agreement(_rows())
    assert out["available"] is False and out["agrees"] is False


# ------------------------------------------------------- the excluded stamps
def test_a_churning_provenance_stamp_does_not_fire_the_alarm(point_at, tmp_path):
    """The omission is deliberate and is therefore tested.

    `measured_at` / `run_git_commit` / `components` move on every re-measurement. The
    control must stay green when ONLY they differ, or it fires once a run and stops
    being read. This is the one case where "the check does not fire" is the assertion.
    """
    point_at(_store(tmp_path, _committed()))
    out = gpd._store_agreement(_rows({
        "measured_at": "2026-08-19T11:00:00Z",
        "run_git_commit": "deadbeef",
        "components": {"a": 1},
    }))
    assert out["agrees"] is True
    assert set(out["stamps_not_checked"]) == {"measured_at", "run_git_commit", "components"}


# ------------------------------------------------------- independence (tautology)
def test_the_two_sides_do_not_share_a_reader(point_at, tmp_path):
    """INDEPENDENCE. If the door side ever came to be read out of the store, this
    control would compare the store with itself and could never fail. Proven by
    mutating the STORE only and requiring the door side to be unmoved."""
    point_at(_store(tmp_path, _committed({"gap": 0.11})))
    out = gpd._store_agreement(_rows())  # door still says 0.42
    assert out["agrees"] is False
    d = out["disagreements"][0]
    assert d["published"] == 0.42 and d["committed"] == 0.11


# ------------------------------------------------------- the store is lossless
def test_every_ledger_field_is_projected_or_the_build_refuses():
    """R10 — the CLASS fails, not the instance.

    The three fields this atom found missing (`normalisation`, `normalisation_reason`,
    `raw_gap_is`) were each carried by exactly one of fourteen live entries, which is
    how a hand-kept column list loses them. Fixing those three alone would leave the
    next one to be found the same way. So an unprojected key now fails the build.
    """
    doc = {"W1": {"gap": 0.5, "a_field_nobody_added_a_column_for": 1}}
    with pytest.raises(bp.SourceUnreadable) as exc:
        bp._coupled_gaps(doc)
    assert "a_field_nobody_added_a_column_for" in str(exc.value)


def test_the_known_ledger_fields_all_have_columns():
    """The mapping and the table definition must not drift apart — a declared
    projection with no column is the same silent drop, one layer up."""
    source = next(s for s in bp.SOURCES if s.table == "coupled_gaps")
    declared = {c.split()[0] for c in source.columns}
    for field, column in bp.COUPLED_GAP_FIELD_COLUMNS.items():
        assert column in declared, f"{field} maps to {column}, which the table lacks"


def test_the_live_ledger_projects_without_loss():
    """The real artefact, not a fixture: every field the live ledger actually carries
    is projected. This is the assertion that was false before this atom."""
    import background.coupled_triad as ct

    ledger = ct.load_gap_ledger()
    if not ledger:
        pytest.skip("no live ledger on this tree")
    seen = set()
    for entry in ledger.values():
        if isinstance(entry, dict):
            seen.update(entry)
    assert seen - set(bp.COUPLED_GAP_FIELD_COLUMNS) == set()
