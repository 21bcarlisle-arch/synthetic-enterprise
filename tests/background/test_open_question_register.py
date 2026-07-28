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
def test_live_no_question_ruling_all_six_answered_and_archived():
    """The real repo state after deliverable 4 (commit 155251dad): all six §3 questions carry an
    ANSWERED disposition, so the archive gate permitted the ruling into done/. Terminal state —
    supersedes the intermediate 'five carried, one answered' snapshot.

    Two invariants, on primary state (R9):
      (1) the ruling is DISCHARGED — no NO_QUESTION row survives in the ACTIVE staging scan
          (all_tracked_questions() excludes done/), so nothing still blocks;
      (2) read directly from the archived body, its six questions are ALL answered, 0 silent, and
          blocking_questions_for_ruling() == 0 — i.e. the archive gate WOULD permit this move
          (the ruling's own acceptance test, satisfied by mechanism not banner)."""
    # (1) discharged out of the active scan
    active_nq = [r for r in oqr.all_tracked_questions() if "NO_QUESTION_LEFT_UNANSWERED" in r["ruling"]]
    assert active_nq == [], [r["question"][:40] for r in active_nq]

    # (2) the archived body itself: six questions, all closed, gate would permit
    done_ruling = oqr.STAGING_DIR / "done" / "DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED_2026-07-28.md"
    assert done_ruling.exists(), f"archived ruling missing: {done_ruling}"
    body = done_ruling.read_text(encoding="utf-8")
    dispositions = oqr.load_dispositions()
    rows = [oqr._row(done_ruling.name, q, dispositions) for q in oqr.extract_questions(body)]
    assert len(rows) == 6, [r["question"][:40] for r in rows]
    assert all(r["status"] == "answered" for r in rows), [(r["question"][:40], r["status"]) for r in rows]
    assert sum(1 for r in rows if r["silent"]) == 0, "no seeded question may be silent (deliverable 2)"
    assert oqr.blocking_questions_for_ruling(done_ruling.name, body) == [], "archive gate must permit a fully-answered ruling"
