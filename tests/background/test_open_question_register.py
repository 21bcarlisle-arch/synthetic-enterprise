"""DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED 2026-07-28, deliverable 1 — mechanism self-tests.

Proves `background.open_question_register`:
  - EXTRACTION (the §2 rhetorical-vs-obligation split): the explicit "Seed the register" block yields
    its items; a `?`-sentence in the DECISION section is captured; a rhetorical `?` in a PROBLEM /
    preamble section is NOT (the whole point of the split); a ruling with no block/DECISION-? yields [].
  - DISPOSITION (R15 BOTH WAYS): a question with no register entry is `open` and BLOCKS; recording
    `answered` CLOSES it (unblocks); `carried` is NON-SILENT but still BLOCKS (the ruling archives on
    an ANSWER, not an acknowledgement).
  - FAIL-SAFE (R15 fail-closed direction): a missing / corrupt register makes every question `open`
    (blocking) — an unavailable answer is a FAILED answer, never a silent unblock.
  - KEY STABILITY: cosmetic re-wording (bolding, backticks) keeps the same key, so a disposition
    keeps applying; a genuine wording change does not.
  - LAW-C INDEPENDENCE: no supervisor import; the question SET is derived from the ruling body, so a
    body mutation changes the output (it cannot be a restatement of the tick's belief).
"""
from __future__ import annotations

import json
from pathlib import Path

import background.open_question_register as oqr


def _ruling(dir_: Path, name: str, body: str) -> Path:
    dir_.mkdir(parents=True, exist_ok=True)
    p = dir_ / name
    p.write_text(body, encoding="utf-8")
    return p


_BLOCK_RULING = """# [DIRECTOR-RULING] — sample

## 1. DECISION

We will do the thing. Is this the right seam to build on?

## 2. PROBLEM — the mechanism is yours

How is it extracted (a block? a parser?), and why am I the bottleneck?

## 3. Seed the register with these

1. First question about `merit_order`?
2. Second question about the counter?
"""


def test_extraction_split_block_and_decision_yes_preamble_no():
    qs = oqr.extract_questions(_BLOCK_RULING)
    joined = " ||| ".join(qs)
    # Block items captured.
    assert any("First question about" in q for q in qs), qs
    assert any("Second question about" in q for q in qs), qs
    # DECISION-section `?` sentence captured.
    assert any("right seam to build on" in q for q in qs), qs
    # PROBLEM-section rhetorical `?` NOT captured (the rhetorical-vs-obligation split).
    assert "bottleneck" not in joined, qs
    assert "a parser" not in joined, qs
    assert len(qs) == 3, qs


def test_extraction_empty_when_no_block_or_decision_question():
    body = "# [DIRECTOR-RULING] — x\n\n## PROBLEM\n\nWhy is this hard? Because reasons.\n"
    # A `?` only in a non-DECISION section => not an obligation => no questions.
    assert oqr.extract_questions(body) == []


def test_key_stable_across_cosmetic_edits_but_not_rewording():
    name = "DIRECTOR_RULING_X_2026-07-28.md"
    k1 = oqr.question_key(name, "**Why was `merit_order` drawable only from today?**")
    k2 = oqr.question_key(name, "Why was merit_order drawable only from today?")  # markdown stripped
    assert k1 == k2
    k3 = oqr.question_key(name, "Why was merit_order NEVER drawable?")  # genuine change
    assert k3 != k1


# --------------------------------------------------------------------------- #
# R15 BOTH WAYS on the blocking predicate
# --------------------------------------------------------------------------- #
def _seed(reg: Path, mapping: dict[str, dict]) -> None:
    reg.write_text(json.dumps({"version": 1, "dispositions": mapping}), encoding="utf-8")


def test_open_when_absent_blocks__answered_unblocks__carried_still_blocks(tmp_path):
    root, ip = tmp_path / "root", tmp_path / "ip"
    reg = tmp_path / "reg.json"
    body = "# [DIRECTOR-RULING] — x\n\n## Questions\n\n1. Alpha question here?\n"
    _ruling(root, "DIRECTOR_RULING_X_2026-07-28.md", body)
    name = "DIRECTOR_RULING_X_2026-07-28.md"
    q = oqr.extract_questions(body)[0]
    key = oqr.question_key(name, q)

    # DIRECTION A — no disposition: the question is open (silent) and BLOCKS.
    _seed(reg, {})
    rows = oqr.open_questions(root, ip, reg)
    assert len(rows) == 1 and rows[0]["silent"] and rows[0]["blocks_archive"], rows
    assert oqr.blocking_questions_for_ruling(name, body, reg)

    # DIRECTION B — answered CLOSES it: no longer open, does not block.
    _seed(reg, {key: {"status": "answered", "disposition": "it is because X"}})
    assert oqr.open_questions(root, ip, reg) == []
    assert oqr.blocking_questions_for_ruling(name, body, reg) == []

    # carried is NON-SILENT but still BLOCKS (answered != acknowledged).
    _seed(reg, {key: {"status": "carried", "disposition": "chasing it"}})
    rows = oqr.open_questions(root, ip, reg)
    assert len(rows) == 1 and not rows[0]["silent"] and rows[0]["blocks_archive"], rows
    assert oqr.blocking_questions_for_ruling(name, body, reg)


def test_corrupt_register_fails_closed_all_open(tmp_path):
    root, ip = tmp_path / "root", tmp_path / "ip"
    reg = tmp_path / "reg.json"
    body = "# [DIRECTOR-RULING] — x\n\n## Questions\n\n1. Alpha question here?\n"
    _ruling(root, "DIRECTOR_RULING_X_2026-07-28.md", body)
    reg.write_text("{ this is not valid json ", encoding="utf-8")  # corrupt
    rows = oqr.open_questions(root, ip, reg)
    assert len(rows) == 1 and rows[0]["status"] == "open", rows  # fail-closed => blocking


def test_missing_register_fails_closed(tmp_path):
    root, ip = tmp_path / "root", tmp_path / "ip"
    body = "# [DIRECTOR-RULING] — x\n\n## Questions\n\n1. Alpha question here?\n"
    _ruling(root, "DIRECTOR_RULING_X_2026-07-28.md", body)
    rows = oqr.open_questions(root, ip, tmp_path / "does_not_exist.json")
    assert len(rows) == 1 and rows[0]["blocks_archive"], rows


def test_law_c_independence_no_supervisor_import():
    # IMPORT is the severance breach (prose may reference supervisor.py to explain WHY it doesn't
    # import it). Check import statements only, mirroring test_daily_self_note's severance test.
    import inspect
    import_lines = [ln.strip() for ln in inspect.getsource(oqr).splitlines()
                    if ln.strip().startswith(("import ", "from "))]
    offenders = [ln for ln in import_lines if "supervisor" in ln]
    assert not offenders, f"INDEPENDENCE BREACH: module imports supervisor: {offenders}"


# --------------------------------------------------------------------------- #
# LIVE: the real seeded register + the real ruling cohere as designed.
# --------------------------------------------------------------------------- #
def test_live_no_question_ruling_five_carried_one_answered():
    """The real repo state after this build: NO_QUESTION carries 6 questions, Q3 (cohort) answered,
    the other five carried — so 5 block its archival and 0 are silent."""
    rows = oqr.all_tracked_questions()
    nq = [r for r in rows if "NO_QUESTION_LEFT_UNANSWERED" in r["ruling"]]
    assert len(nq) == 6, [r["question"][:40] for r in nq]
    answered = [r for r in nq if r["status"] == "answered"]
    assert len(answered) == 1 and "Cohort" in answered[0]["question"], answered
    blocking = [r for r in nq if r["blocks_archive"]]
    assert len(blocking) == 5, blocking
    assert sum(1 for r in nq if r["silent"]) == 0, "no seeded question may be silent (deliverable 2)"
