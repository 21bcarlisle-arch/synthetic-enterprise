"""A provenance banner pushed alone names the run whose figures are committed, not a refused one.

The defect named: on 26 Nov `record_verified` stamped 76f894811d into the working provenance
ahead of a publish commit that the hook chain then refused (22:42Z). The 2100f84f85 cycle's pause
banner pushed that file alone (0b22846e13). The result was origin saying "showing 76f894811d, 1,382
accounts" beside the 6af7fd0bfd feeds (1,306 accounts) that were still served. Any banner pushed
with a served-run stamp no commit carries fails these tests.
"""
from __future__ import annotations

import json

from background import process_run_complete as prc
from background import publish_provenance as prov

SERVED_SHA, REFUSED_SHA = "6af7fd0bf", "76f894811"
SERVED_RUN = f"run_output_{SERVED_SHA}_20261118T070221Z.json"
REFUSED_RUN = f"run_output_{REFUSED_SHA}_20261126T155009Z.json"
POP = {"accounts": 1306, "bills": 53605, "total_revenue_gbp": 3166717.09}


def _committed_and_refused(tmp_path):
    p = tmp_path / "publish_provenance.json"
    committed = prov.record_verified(run_id=SERVED_RUN, git_commit=SERVED_SHA, population=POP, path=p)
    committed = json.loads(json.dumps(committed))
    # The refused cycle: stamped ahead of its commit, which never landed.
    prov.record_verified(run_id=REFUSED_RUN, git_commit=REFUSED_SHA,
                         population={**POP, "accounts": 1382}, path=p)
    return p, committed


def test_the_banner_pushes_the_committed_run_and_not_a_refused_publishs_stamp(tmp_path, monkeypatch):
    p, committed = _committed_and_refused(tmp_path)
    monkeypatch.setattr(prov, "PROVENANCE_FILE", p)
    monkeypatch.setattr(prc, "_committed_provenance", lambda target: committed)
    import background._seat as seat
    monkeypatch.setattr(seat, "is_resident_seat", lambda: True)
    pushed = []
    monkeypatch.setattr(prc, "_commit_and_push_paths",
                        lambda paths, msg, **kw: pushed.append(json.loads(p.read_text())) or True)

    assert prc._publish_provenance_banner("2100f84f8", reason="domain invariant refused") is True

    assert pushed, "no banner was pushed"
    banner = pushed[-1]
    assert banner["verification_state"] == prov.STATE_PAUSED
    for field in ("showing_run", "last_verified"):
        assert banner[field]["git_commit"] == SERVED_SHA, (field, banner[field])
        assert banner[field]["population"]["accounts"] == 1306, (field, banner[field])


def test_the_withdrawal_only_restores_what_is_committed_and_is_silent_when_they_agree(tmp_path):
    p, committed = _committed_and_refused(tmp_path)
    assert prov.withdraw_unserved_stamp(committed, path=p)["showing_run"]["run_id"] == SERVED_RUN
    # Already in agreement, and unreadable: nothing is written either way.
    assert prov.withdraw_unserved_stamp(committed, path=p) is None
    before = p.read_text()
    assert prov.withdraw_unserved_stamp(None, path=p) is None
    assert p.read_text() == before
