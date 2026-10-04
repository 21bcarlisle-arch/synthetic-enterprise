"""`decision_probe --book-seed`: refused without EP17's record, admitted and REBOUND with it.

The defects this names:
  * A probe that ran a non-default book on the seat's say-so would cross the baseline/curriculum
    split (`EP17_varied_population_draw` is the director's).
  * A guard that refuses EVERY seed passes every refusal test, so the admitted branch is asserted
    in the same control, and it must reach the run with the book seed actually rebound.
  * A seed taken but not drawn (the book was already fixed) would publish the default book under
    another seed's name, so a run that did not record the asked-for seed refuses after the run.

No simulation pass runs: `probe` is replaced by a stand-in that does what `live_population()`
does at import -- records the seed it resolves -- so the gate, not the probe, is what is tested.
"""
from __future__ import annotations

import json
import sys

import simulation.live_population as lp
import tools.book_seed_authorisation as auth
from tools import decision_probe as dp

OTHER = 61101


def _record(tmp_path, seeds):
    path = tmp_path / "varied_population_draw_activation.json"
    path.write_text(json.dumps({"_meta": {"authority": "Director console: vary the book."},
                                "activated": {"value": True},
                                "base_seeds": {"value": seeds}}), encoding="utf-8")
    return path


def test_the_book_seed_is_refused_without_the_record_and_admitted_and_drawn_with_it(
        tmp_path, monkeypatch):
    default = lp._DEFAULT_BASE_SEED
    monkeypatch.setattr(lp, "_DEFAULT_BASE_SEED", default)
    monkeypatch.setattr(lp, "_RUN_BASE_SEED", lp._RUN_BASE_SEED)
    monkeypatch.delitem(sys.modules, "simulation.run_phase2b", raising=False)
    seen = []

    def drawn(report_end=None, roll_seed=None):
        seen.append(lp._DEFAULT_BASE_SEED)
        lp._RUN_BASE_SEED = lp._DEFAULT_BASE_SEED
        return []

    monkeypatch.setattr(dp, "probe", drawn)
    out = tmp_path / "probe.json"
    argv = ["--out", str(out), "--book-seed", str(OTHER)]

    # REFUSED: no record exists. Nothing runs, nothing is written, the default book is untouched.
    monkeypatch.setattr(auth, "BOOK_SEED_AUTHORISATION", tmp_path / "absent.json")
    assert dp.main(argv) == 2
    assert seen == [] and not out.exists() and lp._DEFAULT_BASE_SEED == default
    # A record that does not list THIS seed refuses the same way.
    monkeypatch.setattr(auth, "BOOK_SEED_AUTHORISATION", _record(tmp_path, [OTHER + 1]))
    assert dp.main(argv) == 2 and seen == []

    # ADMITTED: the record lists the seed, and the run reaches the probe with the book rebound.
    monkeypatch.setattr(auth, "BOOK_SEED_AUTHORISATION", _record(tmp_path, [OTHER]))
    assert dp.main(argv) == 0
    assert seen == [OTHER]
    assert json.loads(out.read_text(encoding="utf-8"))["book_seed"] == OTHER


def test_a_book_seed_the_run_did_not_draw_refuses_after_the_run(tmp_path, monkeypatch):
    monkeypatch.setattr(lp, "_DEFAULT_BASE_SEED", lp._DEFAULT_BASE_SEED)
    monkeypatch.setattr(lp, "_RUN_BASE_SEED", None)
    monkeypatch.delitem(sys.modules, "simulation.run_phase2b", raising=False)
    monkeypatch.setattr(auth, "BOOK_SEED_AUTHORISATION", _record(tmp_path, [OTHER]))
    monkeypatch.setattr(dp, "probe", lambda report_end=None, roll_seed=None: [])
    out = tmp_path / "probe.json"
    assert dp.main(["--out", str(out), "--book-seed", str(OTHER)]) == 2
    assert not out.exists()


def test_a_book_already_drawn_in_this_process_refuses_a_rebind(tmp_path, monkeypatch):
    monkeypatch.setattr(lp, "_DEFAULT_BASE_SEED", lp._DEFAULT_BASE_SEED)
    monkeypatch.setattr(auth, "BOOK_SEED_AUTHORISATION", _record(tmp_path, [OTHER]))
    monkeypatch.setitem(sys.modules, "simulation.run_phase2b", object())
    refusal = dp.book_seed_refusal(OTHER)
    assert refusal and "already imported" in refusal
    assert dp.book_seed_refusal(None) is None

