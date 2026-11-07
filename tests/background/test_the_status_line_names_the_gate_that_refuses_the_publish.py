"""When the domain-invariant gate refuses a book, the site's status line says which gate and why.

Director, 7 Nov 20:22 (advisor reading, item 3): "If no book can pass the gate by Monday, say on the
site's status line which gate is refusing and why. 'Not updated' should never be silent."

Before this, the refusal reached `publish_provenance.json` only as `paused_reason`, the publisher's
string, which the banner deliberately does not render (director, 2 Nov: a reader's words, never
the internal string). So the line said "did not pass its correctness checks" and nothing more.

MUTATIONS (each must fire):
  * drop the `paused_gate` clause from `banner_line`            -> the banner leg
  * drop `state["paused_gate"] = None` from `record_verified`     -> the clears-on-verify leg
  * write `paused_gate` only `if gate:` in `record_paused`        -> the another-gate leg
  * return `verdict["refusal"]` from `plain_refusal`              -> the reader's-words leg
  * drop the git-hash key from `_domain_invariant_plain`          -> the other-book leg
"""
from __future__ import annotations

import json

from background import process_run_complete as prc
from background import publish_provenance as prov
from tools import domain_invariant_runner as runner

RUN = "run_output_0a6391d186_20261102T212232Z.json"
SHA = "0a6391d186"
POP = {"accounts": 1293, "bills": 52837, "total_revenue_gbp": 2855820.88}

# The fa915ac0d7 book's grade (SEAT_FINDING_A_LEVEL_DIRECT_DEBIT_HOUSEHOLD_IS_DUNNED_PER_BILL..._2026-11-07).
VERDICT = {"refuse": True, "enforce": True, "unexcepted": [
    {"id": "INV_OVERDUE_WITHIN_PAGE_BALANCE", "breached": 1724, "why": "no exception"},
    {"id": "INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE", "breached": 45, "why": "no exception"}]}
RESULTS = [
    {"id": "INV_OVERDUE_WITHIN_PAGE_BALANCE", "checked": 6695,
     "unit": "household collections step printing an overdue figure"},
    {"id": "INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE", "checked": 1139,
     "unit": "account (printed payment counter against collections due)"}]


def test_the_refusal_is_told_in_the_rules_words_with_its_counts():
    """The reader's why is the rule broken, not "no exception". Partition first: the refusing
    branch must produce a sentence at all, and the passing branch must produce none."""
    invariants = runner.load_invariants()
    plain = runner.plain_refusal(VERDICT, RESULTS, invariants)
    assert plain and runner.plain_refusal({"refuse": False}, RESULTS, invariants) is None
    assert plain.startswith("Refused by the domain-invariant check: 2 of its rules are broken")
    for rid, n, of in (("INV_OVERDUE_WITHIN_PAGE_BALANCE", "1,724", "6,695"),
                       ("INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE", "45", "1,139")):
        assert "[{}]: broken on {} of {} checked".format(rid, n, of) in plain, rid
    statement = {i["id"]: i["statement"] for i in invariants}["INV_OVERDUE_WITHIN_PAGE_BALANCE"]
    assert statement.split(",")[0] in plain, "the rule's own words are what the reader is told"
    assert "no exception)" not in plain
    assert len(plain) <= prov.PAUSED_GATE_CHARS


def test_the_banner_prints_the_gate_and_drops_it_on_verify(tmp_path):
    p = tmp_path / "prov.json"
    prov.record_verified(run_id=RUN, git_commit=SHA, population=POP, path=p)
    prov.record_paused(reason="internal string", gate="Refused by the domain-invariant check: X", path=p)
    line = prov.banner_line(prov.read(p))
    assert line.startswith(prov.PAUSED_PLAIN)
    assert "Refused by the domain-invariant check: X" in line
    assert "internal string" not in line
    prov.record_verified(run_id=RUN, git_commit=SHA, population=POP, path=p)
    assert prov.read(p)["paused_gate"] is None
    assert "Refused by" not in prov.banner_line(prov.read(p))


def test_a_later_pause_by_another_gate_does_not_keep_the_last_gates_why(tmp_path):
    p = tmp_path / "prov.json"
    prov.record_verified(run_id=RUN, git_commit=SHA, population=POP, path=p)
    prov.record_paused(reason="inv", gate="Refused by the domain-invariant check: X", path=p)
    prov.record_paused(reason="scoped suite red", path=p)
    assert prov.read(p)["paused_gate"] is None


def test_the_rendered_banner_carries_the_same_clause():
    """Lockstep with `banner_line`, the way the existing provenance test pins the paused sentence."""
    js = (prov.PROJECT_DIR / "site" / "assets" / "freshness-banner.js").read_text()
    assert "d.paused_gate" in js and 'line += " · " + esc(d.paused_gate)' in js


def test_the_publisher_reads_the_sentence_of_this_book_only(tmp_path, monkeypatch):
    table = tmp_path / "domain_invariants.json"
    monkeypatch.setattr(prc, "DOMAIN_INVARIANT_JSON", table)
    assert prc._domain_invariant_plain(SHA) == prc.DOMAIN_INVARIANT_PLAIN_FALLBACK  # no table
    table.write_text(json.dumps({"git": SHA, "plain_refusal": "Refused by the domain-invariant check: Y"}))
    assert prc._domain_invariant_plain(SHA) == "Refused by the domain-invariant check: Y"
    assert prc._domain_invariant_plain("fa915ac0d7") == prc.DOMAIN_INVARIANT_PLAIN_FALLBACK
    assert "domain-invariant check" in prc.DOMAIN_INVARIANT_PLAIN_FALLBACK
