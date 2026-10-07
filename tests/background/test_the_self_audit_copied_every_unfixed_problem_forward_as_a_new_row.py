"""The self-audit counted ROWS, and copied every unfixed problem forward forever.

Director, 2026-10-07: *"The 'what it got wrong' list reads 987 open, 82 corrected, and that number
misleads. It counts rows, not problems: each orientation copies every unfixed item forward ...
Count distinct items, not rows. ... Triage every carried item once, and give each a fate ... Then
apply that as a rule: an item carried unchanged across, say, a week of orientations must be
triaged rather than copied forward again."*

Three defects, three controls:
  * the write accepted a `wrong` row the triage had already retired (`background/direction.py::
    wrong_triage_problems`);
  * the write accepted an untriaged row carried past `WRONG_CARRY_TRIAGE_DAYS`;
  * the panel (`tools/generate_delivery_page.py::what_it_got_wrong`) counted one problem listed in
    39 orientations as 39.
Every fixture is built here; none reads the real `docs/direction/wrong_triage.yaml`.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
import yaml

from background import direction as d

NOW = datetime(2026, 10, 7, 12, 0, tzinfo=timezone.utc)

# Each `what` is the seat's real shape: a provenance prefix, the problem, then a growing tail.
# None of them EQUALS its triage entry's `match` phrase or `problem` sentence, so a check that
# compares whole text instead of `match` phrases cannot claim them.
RETIRED = "THE MACHINE'S, CARRIED. The stash-completeness sweep reports a lost file as safe. 08:21: unchanged."
FRESH = "THE MACHINE'S, NEW. A worktree lock outlives its owner."
UNTRIAGED_8D = "THE MACHINE'S, CARRIED. A waiter's deadline is set without pricing the queue. 05:20: unchanged."
UNTRIAGED_3D = "THE MACHINE'S, CARRIED. Nothing checks a long job's worktrees before launch. 05:20: unchanged."
OPEN_FIX_30D = "THE MACHINE'S, CARRIED. One item can land twice, on origin and on the shared HEAD. 08:21: unchanged."

REGISTER = {
    "decided": "2026-10-07",
    "items": [
        {"id": "stash-sweep-lost-file", "problem": "The stash sweep calls a lost file safe.",
         "match": ["stash-completeness sweep", "lost file as safe"], "first_seen": "2026-09-28",
         "times_listed": 39, "fate": "accept",
         "reason": "the sweep is retired with the stash ban; nothing reads its verdict"},
        {"id": "one-item-lands-twice", "problem": "An item can land twice.",
         "match": ["can land twice"], "first_seen": "2026-09-07", "times_listed": 120,
         "fate": "fix", "owner": "docs/staging/land-twice.md", "status": "open"},
    ],
}


def _decisions(tmp_path, carried: dict[str, int]):
    """A decisions.jsonl where each `what` was first listed `days` before NOW (and again since)."""
    path = tmp_path / "decisions.jsonl"
    lines = []
    for what, days in carried.items():
        for back in (days, 1):
            lines.append(json.dumps({"at": (NOW - timedelta(days=back)).isoformat(),
                                     "wrong": [{"what": what.replace("NEW", "CARRIED"),
                                                "corrected": False}]}))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _register(tmp_path, doc=REGISTER):
    path = tmp_path / "wrong_triage.yaml"
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return path


def _refusals(record_whats, tmp_path, *, register=True, carried=None):
    record = {"oriented_at": NOW.isoformat(),
              "wrong": [{"what": w, "corrected": False} for w in record_whats]}
    carried = carried if carried is not None else {
        RETIRED: 12, UNTRIAGED_8D: 8, UNTRIAGED_3D: 3, OPEN_FIX_30D: 30}
    return d.wrong_triage_problems(
        record,
        triage_path=_register(tmp_path) if register else tmp_path / "absent.yaml",
        decisions_path=_decisions(tmp_path, carried), now=NOW)


def test_the_write_refuses_a_retired_or_week_old_untriaged_item_and_accepts_the_rest(tmp_path):
    """THE PARTITION, rare branches first: two refusals that must be REACHABLE, and three
    acceptances that must not be swept up with them. One control over all five, so a check that
    refuses everything and one that refuses nothing both fail here.

    MUTATIONS (each must fire): compare whole `what` text instead of `match` phrases; ignore
    `fate` (treat every triaged item as retired, or none); drop the 7-day check.
    """
    whats = [RETIRED, FRESH, UNTRIAGED_8D, UNTRIAGED_3D, OPEN_FIX_30D]
    refused = _refusals(whats, tmp_path)
    by_index = {i: [p for p in refused if p.startswith(f"wrong[{i}]")] for i in range(5)}

    assert by_index[0] and by_index[2], f"a rare branch was not taken: {refused}"
    assert not by_index[1] and not by_index[3] and not by_index[4], (
        f"an acceptable item was refused: {refused}")

    # THE REASONS, so the seat knows what to do with each.
    assert "'stash-sweep-lost-file'" in by_index[0][0] and "fate accept" in by_index[0][0]
    assert "the sweep is retired with the stash ban" in by_index[0][0]
    assert ("carried 7+ days untriaged" in by_index[2][0]
            and "triage it into docs/direction/wrong_triage.yaml (fix / fold / accept) rather "
                "than copy it forward" in by_index[2][0])


def test_a_retired_FIX_is_retired_only_once_it_is_already_fixed(tmp_path):
    """`fix` is the one fate whose retirement depends on `status`: open keeps it listable."""
    doc = json.loads(json.dumps(REGISTER))
    doc["items"][1].update(status="already_fixed", fixed_by="abc123def")
    record = {"oriented_at": NOW.isoformat(), "wrong": [{"what": OPEN_FIX_30D, "corrected": False}]}
    refused = d.wrong_triage_problems(record, triage_path=_register(tmp_path, doc),
                                      decisions_path=_decisions(tmp_path, {}), now=NOW)
    assert refused and "already_fixed by abc123def" in refused[0], refused


def test_closing_an_untriaged_item_is_not_carrying_it(tmp_path):
    """`corrected: true` on an old untriaged item is its LAST listing, and refusing it would
    force the seat to keep it open to get the record through."""
    record = {"oriented_at": NOW.isoformat(), "wrong": [{"what": UNTRIAGED_8D, "corrected": True}]}
    assert d.wrong_triage_problems(record, triage_path=_register(tmp_path),
                                   decisions_path=_decisions(tmp_path, {UNTRIAGED_8D: 8}),
                                   now=NOW) == []


def test_with_NO_register_nothing_is_refused_and_no_fate_is_invented(tmp_path):
    """Before the register exists the write behaves exactly as it did: the 7-day rule needs a
    register to triage INTO, and retirement needs a fate somebody wrote."""
    assert _refusals([RETIRED, UNTRIAGED_8D, OPEN_FIX_30D], tmp_path, register=False) == []


def test_an_unreadable_register_refuses_with_its_reason_rather_than_grading_nothing(tmp_path):
    bad = tmp_path / "wrong_triage.yaml"
    bad.write_text("items: [unclosed", encoding="utf-8")
    record = {"oriented_at": NOW.isoformat(), "wrong": [{"what": FRESH, "corrected": False}]}
    refused = d.wrong_triage_problems(record, triage_path=bad,
                                      decisions_path=_decisions(tmp_path, {}), now=NOW)
    assert refused and "unreadable" in refused[0]


@pytest.mark.parametrize("broken, says", [
    ({"fate": "accept", "reason": ""}, "accept with no reason"),
    ({"fate": "ignore"}, "not one of fix/fold/accept"),
    ({"match": []}, "no match phrases"),
])
def test_a_register_entry_that_retires_without_saying_why_is_refused(tmp_path, broken, says):
    doc = json.loads(json.dumps(REGISTER))
    doc["items"][0].update(broken)
    record = {"oriented_at": NOW.isoformat(), "wrong": [{"what": FRESH, "corrected": False}]}
    refused = d.wrong_triage_problems(record, triage_path=_register(tmp_path, doc),
                                      decisions_path=_decisions(tmp_path, {}), now=NOW)
    assert any(says in p for p in refused), refused


def test_the_carry_limit_is_the_directors_week():
    """A policy dial with its reason beside it, keyed to the director's words, not a guess."""
    assert d.WRONG_CARRY_TRIAGE_DAYS == 7


def test_identity_strips_the_provenance_prefix_and_the_growing_tail():
    """NEW -> CARRIED and the "08:21: unchanged." tail change every stretch; the problem does not."""
    a = d.wrong_first_sentence("THE MACHINE'S, NEW. A worktree lock outlives its owner.")
    b = d.wrong_first_sentence(
        "THE MACHINE'S, CARRIED. A worktree lock outlives its owner. 23:24: unchanged.")
    c = d.wrong_first_sentence("Still open, fifth stretch. A worktree lock outlives its owner.")
    assert a == b == c == "a worktree lock outlives its owner"
    assert d.wrong_first_sentence("MINE, NEW. Something else.") != a


def _panel(monkeypatch, rows, register):
    from tools import generate_delivery_page as page
    monkeypatch.setattr(page.direction_mod, "read_decisions", lambda limit=50: rows)
    monkeypatch.setattr(d, "WRONG_TRIAGE_PATH", register)
    return page.what_it_got_wrong()


def _rows_of_one_problem(n=39):
    return [{"at": (NOW - timedelta(hours=3 * i)).isoformat(), "wrong": [
        {"what": RETIRED.replace("08:21", f"{i:02d}:00"), "corrected": False}]} for i in range(n)]


def test_the_panel_counts_one_problem_listed_in_39_orientations_as_ONE(monkeypatch, tmp_path):
    """The headline that misled: 39 copies of one problem read as 39 open mistakes.

    MUTATION (must fire): count `len(wrong)` as `distinct`.
    """
    panel = _panel(monkeypatch, _rows_of_one_problem(), _register(tmp_path))
    assert panel["distinct"] == 1 and panel["rows"] == 39
    assert panel["problems"][0]["times_listed"] == 39
    assert panel["triaged_by_fate"] == {"fix": 0, "fold": 0, "accept": 1}
    assert panel["distinct_open"] == 0, "an accepted problem is not open"


def test_with_NO_register_the_panel_still_counts_distinct_by_first_sentence(monkeypatch, tmp_path):
    rows = _rows_of_one_problem()
    rows[0]["wrong"].append({"what": OPEN_FIX_30D, "corrected": False})
    panel = _panel(monkeypatch, rows, tmp_path / "absent.yaml")
    assert panel["distinct"] == 2 and panel["rows"] == 40
    assert panel["triaged"] == 0 and panel["untriaged"] == 2 and panel["distinct_open"] == 2
    assert "no triage register" in panel["triage_register"]
    assert all(p["fate"] is None for p in panel["problems"]), "a fate was invented"


def test_the_seat_is_TOLD_the_rule_and_can_write_the_file_its_refusal_names():
    """A refusal whose remedy is outside the seat's brief or its write scope cannot be obeyed."""
    from background import delivery_seat as seat
    assert "docs/direction/wrong_triage.yaml" in d.WRITE_SCOPE
    assert "7+ days" in seat.CHARTER and "wrong_triage.yaml" in seat.CHARTER


def test_the_seat_RUNS_the_triage_check_at_write_time_and_not_at_read_time():
    """At read time a register edited after the write would silently drop live focus."""
    import inspect

    from background import delivery_seat as seat
    assert "wrong_triage_problems" in inspect.getsource(seat.orient)
    assert "wrong_triage_problems" not in inspect.getsource(d.validate)
