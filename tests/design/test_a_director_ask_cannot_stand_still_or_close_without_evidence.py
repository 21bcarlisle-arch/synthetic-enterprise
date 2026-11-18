"""A director ask cannot stand still unseen, or leave the queue without evidence (tools/director_asks_ledger.py).

Director, 24 Oct 2026 09:45: "Are there other things I've asked for this never finished shipping??"
The defects these name: a director document moved to done/ with no Done section naming a commit or
a path (156 of 159 had none); an open ask that stood still for months while a housekeeping commit to
its document reset any clock read from git; a stale control that refuses everything or nothing.
"""
from __future__ import annotations

from datetime import date, timedelta

from tools import director_asks_ledger as L

TODAY = date(2026, 10, 24)


def _row(status, days_ago, **kw):
    row = {"id": "x{}{}".format(status, days_ago), "status": status,
           "asked": (TODAY - timedelta(days=days_ago)).isoformat(), "last_commit": None}
    row.update(kw)
    return row


def test_the_stale_control_can_both_red_and_pass():
    """The partition, in one assert: an old open ask reds; a young one, a held one and a shipped one
    do not. MUTATION: `stale()` returning every row, or none, fails here."""
    rows = [_row("open", 22), _row("open", 20), _row("partly", 40, held="waits on his values"),
            _row("shipped", 90), _row("not_started", 30), _row("partly", 60, moved=TODAY.isoformat())]
    assert [r["id"] for r in L.stale(rows, TODAY)] == ["xopen22", "xnot_started30"]


def test_a_commit_to_the_document_is_not_movement_on_the_ask():
    """On 13 Oct one banner commit touched all fifteen July documents. MUTATION: putting
    `last_commit` back into `last_movement` lets that commit hide a three-month-old ask."""
    row = _row("open", 97, last_commit=(TODAY - timedelta(days=11)).isoformat())
    assert L.stale([row], TODAY) == [row]


def test_a_done_section_must_name_a_commit_or_a_path():
    """MUTATION: `has_done_evidence` accepting any Done heading passes the first case."""
    assert not L.has_done_evidence("# Ask\n\n## Done\n\nActioned.\n")
    assert not L.has_done_evidence("# Ask\n\nShipped in 3373f3523c.\n")  # no Done section at all
    assert L.has_done_evidence("# Ask\n\n## Done\n\nLanded in 3373f3523c.\n## Later\n")
    assert L.has_done_evidence("# Ask\n\n## Done\n\nSee tools/director_asks_ledger.py.\n")
    # A ruling's own criteria heading is not the Done section, before it or instead of it.
    assert L.has_done_evidence("# Ask\n\n## Done means\n\nIt runs.\n\n## Risk\n\n## Done\n\nLanded in 3373f3523c.\n")
    assert not L.has_done_evidence("# Ask\n\n## Done means\n\nSee tools/director_asks_ledger.py.\n")


def test_no_director_document_has_reached_done_without_evidence_since_the_gate():
    """The live tree: every asking DIRECTOR_* document arriving in a done folder from
    DONE_EVIDENCE_FROM on carries a Done section naming its evidence. Earlier arrivals are counted
    on the ledger as `closed_without_evidence`, by the day they arrived, not by a list of names."""
    late = L.closed_without_evidence_since()
    assert late == [], ("director document(s) moved to done/ with no `## Done` section naming a "
                        "commit or a path: {}".format(late))


def test_the_live_ledger_builds_and_every_ruling_is_one_row():
    ledger = L.build(today=TODAY)
    assert ledger is not None, "docs/direction/director_asks.yaml could not be read"
    ids = [r["id"] for r in L.load_rulings()]
    assert len(ids) == len(set(ids))
    assert all(r["status"] in L.RULED + ("open",) for r in L.load_rulings())
    assert sum(ledger["counts"].values()) == len(ledger["rows"])


def test_the_ledger_tells_superseded_asks_as_history_not_as_the_page_s_framing():
    """A ledger row quoting a superseded ask ("80 founders") is history: the canon site leg must
    not read it as the page's framing. The page's own counts line stays visible to it."""
    from tools import canon_drift_check as C

    row = {"id": "x", "status": "superseded", "asked": "2026-07-12",
           "ask": "take the 80 founders ... a director twin", "evidence": ["a.py"],
           "superseded_by": "canon v4", "next_step": "none"}
    ledger = {"counts": {"superseded": 1}, "rows": [row], "stale": []}
    page = C.visible_text(L.render_html(ledger)).lower()
    assert "80 founders" not in page and "director twin" not in page
    assert "one row of a ledger" in page
