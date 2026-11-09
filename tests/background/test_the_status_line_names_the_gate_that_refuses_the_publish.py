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
  * ignore `limit` in `plain_refusal`                             -> the fitted-sentence leg
"""
from __future__ import annotations

import json
import re

import pytest

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


#: The first two live refusals, as graded: 9 Nov 04:18 (three rules, the line that ended
#: mid-unit at 900 characters) and 8 Nov 20:48 (seven rules).
LIVE_REFUSALS = {
    "three_rules_9_nov": [
        ("INV_OVERDUE_WITHIN_BALANCE", 57, 1630, "collections journey opening"),
        ("INV_OVERDUE_WITHIN_PAGE_BALANCE", 241, 7857,
         "household collections step printing an overdue figure"),
        ("INV_DD_COLLECTIONS_EQUAL_TO_THE_BILL_WITHIN_THE_VARIABLE_DD_SHARE", 1, 1,
         "book: its successful DD collections, level against variable")],
    "seven_rules_8_nov": [
        ("INV_OVERDUE_WITHIN_PAGE_BALANCE", 1613, 6705,
         "household collections step printing an overdue figure"),
        ("INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE", 663, 1291,
         "account (page revenue against page bills before VAT)"),
        ("INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE", 194, 1139,
         "account (printed payment counter against collections due)"),
        ("INV_METER_TYPE_ONE_VALUE_PER_SUPPLY_POINT", 11, 1291, "supply point"),
        ("INV_HOUSEHOLD_PAGE_MISSED_BILL_WAS_NOT_SETTLED", 5, 1291, "household page"),
        ("INV_DD_COLLECTION_IS_DATED_ON_A_BACS_PROCESSING_DAY", 8624, 40000,
         "successful DD collection"),
        ("INV_FIRST_LEVEL_DD_IS_NOT_COLLECTED_BEFORE_SUPPLY_START", 268, 1200, "level DD mandate")],
}


@pytest.mark.parametrize("case", sorted(LIVE_REFUSALS))
def test_the_sentence_is_fitted_to_the_line_never_cut_by_it(case):
    """DEFECT (9 Nov 04:18, the first live refusal): three rules ran past PAUSED_GATE_CHARS and the
    store's slice ended the line "(unit: book: its successful DD collections,". The sentence must
    fit, end as a sentence, and still account for EVERY rule: each one named with its count, or
    counted in the "and N more" tail.

    MUTATION: pass no `limit` (or ignore it) and the three-rule case runs to ~1,000 characters."""
    rows = LIVE_REFUSALS[case]
    verdict = {"refuse": True, "unexcepted": [
        {"id": rid, "breached": n, "why": "no exception"} for rid, n, _, _ in rows]}
    results = [{"id": rid, "checked": of, "unit": unit} for rid, _, of, unit in rows]
    invariants = runner.load_invariants()
    unbounded = runner.plain_refusal(verdict, results, invariants)
    assert len(unbounded) > prov.PAUSED_GATE_CHARS, \
        "premise: the live refusal does not fit unshortened, or this grades nothing"
    plain = runner.plain_refusal(verdict, results, invariants, limit=prov.PAUSED_GATE_CHARS)
    assert len(plain) <= prov.PAUSED_GATE_CHARS and plain.endswith("."), plain
    named = [rid for rid, n, of, _ in rows
             if "[{}]: broken on {:,} of {:,} checked".format(rid, n, of) in plain]
    more = re.search(r"and (\d+) more", plain)
    assert len(named) + (int(more.group(1)) if more else 0) == len(rows), plain
    assert named == [r[0] for r in rows[:len(named)]], "rules are dropped from the end only"
