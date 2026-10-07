"""The seat's brief names each unit whose running code lacks an origin commit to a module it loads.

THE DEFECT. 0be518a08 (the direction record re-bases until the unit's budget runs out) reached
origin at 07:41 on 2026-10-07. The shared checkout the seat runs from sat 2 ahead / 20 behind, so
the 09:21 orientation ran the code that fix replaced. The brief said only "this checkout has not
fast-forwarded, so daemons running from it are executing code the branch has moved past" -- true
of every divergence, and naming nobody. `process_reconciler`'s `behind_trunk` leg answers the
question for the manifest's daemons, and the seat and the other timers are not in that population.

The control is a real checkout behind a real origin, with real unit files, and it asserts the
whole partition at once: a unit named for its own module, a unit named only through an import,
an untouched unit left out, and a unit running from a different checkout left out.
"""
from __future__ import annotations

import subprocess

import pytest

from background import delivery_seat as seat


def _run(cwd, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgsign=false", *args],
        cwd=str(cwd), capture_output=True, text=True, check=True).stdout


def _write(repo, rel: str, body: str) -> None:
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")


def _unit(unit_dir, name: str, wd, module: str) -> None:
    (unit_dir / f"{name}.service").write_text(
        f"[Service]\nWorkingDirectory={wd}\nExecStart=/usr/bin/python3 -m {module}\n",
        encoding="utf-8")


@pytest.fixture()
def behind(tmp_path, monkeypatch):
    up = tmp_path / "upstream"
    up.mkdir()
    _run(up, "init", "-q", "-b", "main")
    _write(up, "background/__init__.py", "")
    _write(up, "background/delivery_seat.py", "from background import helper\n")
    _write(up, "background/helper.py", "X = 1\n")
    _write(up, "background/helper_user.py", "from background import helper\n")
    _write(up, "background/untouched.py", "Y = 1\n")
    _run(up, "add", ".")
    _run(up, "commit", "-q", "-m", "base")
    co = tmp_path / "checkout"
    _run(tmp_path, "clone", "-q", str(up), str(co))

    _write(up, "background/delivery_seat.py", "from background import helper\nFIXED = 1\n")
    _run(up, "commit", "-qam", "the seat's own fix")
    seat_fix = _run(up, "rev-parse", "--short", "HEAD").strip()
    _write(up, "background/helper.py", "X = 2\n")
    _run(up, "commit", "-qam", "a module the seat imports")
    helper_fix = _run(up, "rev-parse", "--short", "HEAD").strip()
    _run(co, "fetch", "-q", "origin")

    units = tmp_path / "units"
    units.mkdir()
    _unit(units, "delivery-seat", co, "background.delivery_seat")
    _unit(units, "archive-helper", co, "background.helper_user")
    _unit(units, "untouched", co, "background.untouched")
    _unit(units, "elsewhere", tmp_path / "another-checkout", "background.delivery_seat")

    monkeypatch.setattr(seat, "PROJECT_DIR", co)
    monkeypatch.setattr(seat, "UNIT_DIR", units)
    return co, seat_fix, helper_fix


def test_the_brief_names_exactly_the_units_whose_loaded_code_origin_has_moved(behind):
    co, seat_fix, helper_fix = behind
    rows = seat.units_lacking_origin()
    assert [r["unit"] for r in rows] == ["delivery-seat", "archive-helper"], rows
    by = {r["unit"]: r for r in rows}
    assert by["delivery-seat"]["own_commits"] == [seat_fix]
    assert set(by["delivery-seat"]["commits"]) == {seat_fix, helper_fix}
    assert by["archive-helper"]["own_commits"] == []
    assert by["archive-helper"]["commits"] == [helper_fix]

    says = seat.branch_divergence()["says"]
    assert f"delivery-seat lacks {seat_fix} to background/delivery_seat.py itself" in says
    assert "archive-helper lacks 1 commit(s) to code it imports" in says
    assert "untouched" not in says and "elsewhere" not in says


def test_a_level_checkout_names_no_unit(behind):
    co, _, _ = behind
    _run(co, "merge", "-q", "--ff-only", "origin/main")
    div = seat.branch_divergence()
    assert div["units_lacking_origin"] == []
    assert "UNITS RUNNING" not in div["says"]


def test_an_unreadable_reading_says_so_rather_than_reading_as_a_clean_fleet(behind, monkeypatch):
    def boom(*a, **k):
        raise OSError("no unit dir")
    monkeypatch.setattr(seat, "_units_running_here", boom)
    div = seat.branch_divergence()
    assert div["units_lacking_origin"][0]["unreadable"]
    assert "could not be read" in div["says"]
