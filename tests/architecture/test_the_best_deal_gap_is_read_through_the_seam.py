"""The published best-deal gap is the company's read of the commons, not a world file's table.

The defects each test names: a supplier observable defined again in the world (the shape
`d06b039e7` extended, docs/staging/SEAT_FINDING_THE_SAVE_THE_MOVER_OFFER_AND_THE_PAYMENT_WORK_AGAINST_
THE_FOUR_PRINCIPLES_2026-10-11.md section 1 P3 (b)); the run loop reading the gap from anywhere but
the company's door; a reader that serves its own copy rather than the publication; and a damaged
artefact read as "no deal beat the default", which silently withdraws every price match.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from company.crm import save_offer

ROOT = Path(__file__).resolve().parents[2]


def _world_definitions_of_the_gap() -> list[str]:
    found = []
    for pkg in ("simulation", "sim"):
        for path in (ROOT / pkg).rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text())):
                names = []
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names = [node.name]
                elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    names = [t.id for t in targets if isinstance(t, ast.Name)]
                found += [f"{path.relative_to(ROOT)}::{n}" for n in names
                          if "best_deal_gap" in n.lower()]
    return found


def test_no_world_module_defines_the_best_deal_gap():
    """MUTATION: put `PUBLISHED_BEST_DEAL_GAP_SHARE = {...}` back in simulation/save_on_loss_notice.py."""
    assert _world_definitions_of_the_gap() == []


def test_the_run_loop_reads_the_gap_from_the_company_door():
    """MUTATION: import `published_best_deal_gap_share` in run_phase2b from anywhere else."""
    tree = ast.parse((ROOT / "simulation" / "run_phase2b.py").read_text())
    sources = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
               and any(a.name == "published_best_deal_gap_share" for a in node.names)}
    assert sources == {"company.interfaces.save_offer"}


@pytest.fixture
def commons(tmp_path, monkeypatch):
    real = json.loads(save_offer._BEST_DEAL_GAP_COMMONS.read_text())
    path = tmp_path / "gap.json"
    monkeypatch.setattr(save_offer, "_BEST_DEAL_GAP_COMMONS", path)
    save_offer._published_best_deal_gaps.cache_clear()
    yield real, path
    save_offer._published_best_deal_gaps.cache_clear()


def test_the_reader_serves_the_publication(commons):
    """MUTATION: hold a literal table in company/crm/save_offer.py and stop reading the file."""
    real, path = commons
    assert any(q["quarter"] == "2024-Q2" for q in real["quarters"])
    for q in real["quarters"]:
        if q["quarter"] == "2024-Q2":
            q["gap_share"] = 0.5
    path.write_text(json.dumps(real))
    assert save_offer.published_best_deal_gap_share("2024-05-01") == 0.5
    assert save_offer.published_best_deal_gap_share("2030-01-01") is None


@pytest.mark.parametrize("damage", ["missing", "empty", "unfetched", "not_a_share"])
def test_a_damaged_artefact_refuses_rather_than_offering_nothing(commons, damage):
    real, path = commons
    if damage != "missing":
        if damage == "empty":
            real["quarters"] = []
        elif damage == "unfetched":
            real["quarters"][0]["provenance"] = "recalled"
        else:
            real["quarters"][0]["gap_share"] = 30.3
        path.write_text(json.dumps(real))
    with pytest.raises((FileNotFoundError, ValueError)):
        save_offer.published_best_deal_gap_share("2016-01-01")
