"""Rebuilding the cap composition artefact must not DELETE the block that makes it askable.

Subject: `tools/ofgem_cap_unit_rate_composition.py::_with_carried_source_check`.

THE DEFECT THIS NAMES, found 2026-09-07 while settling that artefact's `cannot_tell`. `main()` wrote
`measure()` straight over the artefact, and `measure()` reads a workbook rather than visiting a
publisher, so it emits no `source_check`. A re-run therefore took the file from `superseded` to
CARRYING NO BLOCK AT ALL, which is the ASKABLE refusal in
`tools/commons_source_supersession.py` and wedges every lane's commit -- arriving through the one
action a diligent session would take, which is the worst shape a control can have.

KEYED TO THE PROPERTY. Nothing here pins a version, a verdict or a date. Recording `current` is a
green change and so is recording `superseded`; losing the block on rebuild is not.
"""
from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

import pytest

from tools import ofgem_cap_unit_rate_composition as subject
from tools.commons_source_supersession import check_artefact

EXISTING = {
    "publication": "Ofgem Default Tariff Cap level model, Default_tariff_cap_level_v1.19.xlsx",
    "url": "https://example.invalid/energy-price-cap-default-tariff-levels",
    "fetched": "2026-08-31",
    "version_token": "v1.19",
    "version_token_is": "in_filename_only",
    "how_to_recheck": "read the highest version on the version-history page",
    "checked_for_supersession": {
        "on": "2026-09-07",
        "found": "current",
        "note": "fixture",
    },
}

REBUILT = {
    "artefact": "ofgem_cap_unit_rate_composition",
    "source_model": "Default_tariff_cap_level_v1.19.xlsx",
    "headline": {"min_share": 0.4077},
}


def _artefact(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, doc: dict | None) -> Path:
    path = tmp_path / "ofgem_cap_unit_rate_composition.json"
    if doc is not None:
        path.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    monkeypatch.setattr(subject, "OUT_PATH", path)
    return path


def test_a_rebuild_carries_the_existing_block_forward(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _artefact(tmp_path, monkeypatch, {**REBUILT, "source_check": copy.deepcopy(EXISTING)})
    carried = subject._with_carried_source_check(copy.deepcopy(REBUILT))
    assert carried["source_check"] == EXISTING


def test_the_carried_block_is_verbatim_and_the_rebuild_edits_nothing_in_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Everything in the block is a claim about a publisher this module did not visit.

    A rebuild that "helpfully" stamped today's date, or moved the verdict to match the workbook it
    happened to find on disk, would be manufacturing a fetch that never happened -- which is exactly
    the failure the supersession module exists to make impossible.
    """
    _artefact(tmp_path, monkeypatch, {**REBUILT, "source_check": copy.deepcopy(EXISTING)})
    rebuilt = copy.deepcopy(REBUILT)
    rebuilt["source_model"] = "Default-tariff-cap-level-v1.31.xlsx"
    carried = subject._with_carried_source_check(rebuilt)
    assert carried["source_check"]["version_token"] == "v1.19"
    assert carried["source_check"]["checked_for_supersession"]["on"] == "2026-09-07"
    assert carried["source_model"] == "Default-tariff-cap-level-v1.31.xlsx"


def test_without_the_carry_the_rebuilt_artefact_is_refused_as_unaskable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The poison round: the pre-repair behaviour, graded by the gate it used to wedge.

    This is what `main()` wrote before 2026-09-07 -- `measure()`'s output, unmerged -- and it proves
    the consequence rather than asserting it in a comment.
    """
    path = _artefact(tmp_path, monkeypatch, None)
    path.write_text(json.dumps(REBUILT, indent=1), encoding="utf-8")
    refusals = check_artefact(path, date(2026, 9, 7))
    assert [r.leg for r in refusals] == ["ASKABLE"]

    path.write_text(
        json.dumps(
            subject._with_carried_source_check(copy.deepcopy(REBUILT)) | {"source_check": EXISTING},
            indent=1,
        ),
        encoding="utf-8",
    )
    assert check_artefact(path, date(2026, 9, 7)) == []


def test_a_first_build_with_no_artefact_yet_is_not_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """There is nothing to carry, and refusing would make the artefact unbuildable from scratch."""
    _artefact(tmp_path, monkeypatch, None)
    assert "source_check" not in subject._with_carried_source_check(copy.deepcopy(REBUILT))


def test_an_unreadable_artefact_does_not_stop_the_rebuild(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _artefact(tmp_path, monkeypatch, None)
    path.write_text("{not json", encoding="utf-8")
    assert "source_check" not in subject._with_carried_source_check(copy.deepcopy(REBUILT))


def test_the_live_model_index_url_is_the_one_the_artefact_publishes() -> None:
    """The artefact's `source_url` is generated, so the constant and the file cannot drift apart.

    The old value named a policy page that carries no cap level model at all, and that mismatch is
    what let the supersession check report `cannot_tell` indefinitely while looking like it worked.
    """
    doc = json.loads(subject.OUT_PATH.read_text())
    assert doc["source_url"] == subject.MODEL_INDEX_URL
    assert "default-tariff-levels" in subject.MODEL_INDEX_URL
