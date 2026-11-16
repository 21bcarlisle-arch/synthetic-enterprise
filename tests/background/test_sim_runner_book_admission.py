"""The next book is built only on a commit carrying the fixes for what refused the last one, and
never ahead of a long job queued for room (`sim_runner.book_admission`).

Defect each test names: at 07:05Z on 16 Nov sim-runner built a book on f7e17b1316. That commit carried
the fix for none of the rows that had refused the book before it, and the build kept the value-test
twin queued for 6,728 s. The publisher then refused the new book on the same rows.
"""
from pathlib import Path

import yaml

from background import sim_runner


def _spec(tmp_path, expires="2026-11-24", rows=None):
    p = tmp_path / "next_book_requires.yaml"
    rows = rows if rows is not None else [
        {"commit": "aaa", "what": "fix A"}, {"commit": None, "what": "fix D", "owner": "ATOM_D"}]
    p.write_text(yaml.safe_dump({"expires": expires, "requires": rows}))
    return p


def _admit(tmp_path, monkeypatch, *, carried=("aaa",), queued=(), **spec):
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    return sim_runner.book_admission("head1", spec_path=_spec(tmp_path, **spec), today="2026-11-16",
                                     carries=lambda c: c in carried, queued=list(queued))


def test_every_leg_of_the_book_condition_is_reachable(tmp_path, monkeypatch):
    """One control over the partition: admitted, held by an unlanded fix, held by a fix the commit
    lacks, held by a queued long job, held when systemd cannot say, and lapsed past `expires`."""
    landed = [{"commit": "aaa", "what": "fix A"}]
    got = {
        "admit": _admit(tmp_path, monkeypatch, rows=landed),
        "unlanded": _admit(tmp_path, monkeypatch),
        "lacks": _admit(tmp_path, monkeypatch, carried=(), rows=landed),
        "queued": _admit(tmp_path, monkeypatch, rows=landed, queued=["longjob-value-test-twin-queued"]),
        "lapsed": _admit(tmp_path, monkeypatch, expires="2026-11-15"),
    }
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    unknown = sim_runner.book_admission("head1", spec_path=_spec(tmp_path, rows=landed),
                                        today="2026-11-16", carries=lambda c: True, queued=None)
    assert got["admit"]["admitted"] and got["lapsed"]["admitted"]
    assert not any(got[k]["admitted"] for k in ("unlanded", "lacks", "queued")) and not unknown["admitted"]
    assert "fix D has not landed, owner ATOM_D" in got["unlanded"]["reason"]
    assert "head1 does not carry aaa" in got["lacks"]["reason"]
    assert "longjob-value-test-twin-queued" in got["queued"]["reason"]
    assert "cannot tell" in unknown["reason"]


def test_no_declaration_admits_as_before(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    assert sim_runner.book_admission("head1", spec_path=tmp_path / "absent.yaml", today="2026-11-16",
                                     carries=lambda c: False, queued=[])["admitted"]


def test_the_queued_units_are_read_from_systemd_and_a_failure_is_not_an_empty_queue():
    class R:
        def __init__(self, rc, out):
            self.returncode, self.stdout = rc, out
    ok = sim_runner.queued_long_jobs(runner=lambda *a, **k: R(0, "longjob-x-queued.service loaded active running q\n"))
    assert ok == ["longjob-x-queued.service"]
    assert sim_runner.queued_long_jobs(runner=lambda *a, **k: R(1, "")) is None
    assert sim_runner.queued_long_jobs(runner=lambda *a, **k: R(0, "")) == []


def test_the_live_declaration_parses_and_every_row_names_what_it_fixes():
    live = Path(__file__).resolve().parents[2] / "background" / sim_runner.NEXT_BOOK_REQUIRES.name
    spec = yaml.safe_load(live.read_text())
    assert spec["expires"] and spec["requires"]
    assert all(r.get("what") for r in spec["requires"])
