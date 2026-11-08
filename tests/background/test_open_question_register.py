"""DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED 2026-07-28, deliverable 1 — mechanism self-tests.

Proves `background.open_question_register`:
  - EXTRACTION (narrowed 2026-11-08): only `?`-sentences in the director's quoted words are
    questions; the advisor's own headings, lists and `?`-sentences around the quote are not.
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


# The shape of an advisor-channel ruling: his words quoted, the advisor's drafting around them.
_ADVISOR_RULING = """# [DIRECTOR-RULING] The four reserved questions — sample

**Type:** RULING, through the advisor channel. The director's words:

- 13:47 GMT: "Hide the link. Stay on the tier. Do we need HF?"
- 13:50 GMT: “Why did the tests
  not find them? Fix it.”

## The rulings

1. **Is the link needed?** No.
2. Should the advisor recommend more?

## Questions

1. Is this list item a question?
"""


def test_only_questions_in_his_quoted_words_are_extracted():
    qs = oqr.extract_questions(_ADVISOR_RULING)
    # His quoted questions, straight and curly quotes, a curly quote across a line break.
    assert qs == ["Do we need HF?", "Why did the tests not find them?"], qs
    # The advisor's headings and list items are not his words: the 8 Nov false positives.
    joined = " ||| ".join(qs)
    assert "link needed" not in joined and "list item" not in joined, qs


def test_extraction_empty_when_no_quoted_question():
    body = ('# [DIRECTOR-RULING] — x\n\n## DECISION\n\nWhy is this hard? Because reasons.\n\n'
            '- 09:00: "Do it."\n')
    # A `?` outside quotes, and a quote without a `?`, pose no question.
    assert oqr.extract_questions(body) == []


def test_a_quoted_mark_with_no_words_is_not_a_question():
    body = '# [DIRECTOR-RULING] — x\n\n- 09:00 GMT: "Fine. ?"\n'
    assert oqr.extract_questions(body) == []


def test_a_straight_quote_does_not_pair_across_a_paragraph():
    body = '# [DIRECTOR-RULING] — x\n\nA stray " mark.\n\nIs this his question? No " it is not.\n'
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
    body = '# [DIRECTOR-RULING] — x\n\n- 09:00 GMT: "Alpha question here?"\n'
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
    body = '# [DIRECTOR-RULING] — x\n\n- 09:00 GMT: "Alpha question here?"\n'
    _ruling(root, "DIRECTOR_RULING_X_2026-07-28.md", body)
    reg.write_text("{ this is not valid json ", encoding="utf-8")  # corrupt
    rows = oqr.open_questions(root, ip, reg)
    assert len(rows) == 1 and rows[0]["status"] == "open", rows  # fail-closed => blocking


def test_missing_register_fails_closed(tmp_path):
    root, ip = tmp_path / "root", tmp_path / "ip"
    body = '# [DIRECTOR-RULING] — x\n\n- 09:00 GMT: "Alpha question here?"\n'
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
def test_active_rulings_include_the_advisor_channel(tmp_path):
    """The advisor channel's live rulings are active: their questions are surfaced before archival."""
    root, ip = tmp_path / "root", tmp_path / "ip"
    body = '# [DIRECTOR-RULING] — x\n\n- 09:00 GMT: "Alpha question here?"\n'
    _ruling(root / "advisor", "DIRECTOR_RULING_X_2026-11-08.md", body)
    _ruling(root / "advisor" / "done", "DIRECTOR_RULING_Y_2026-11-08.md", body)
    rows = oqr.open_questions(root, ip, tmp_path / "reg.json")
    assert [r["ruling"] for r in rows] == ["DIRECTOR_RULING_X_2026-11-08.md"], rows


def test_live_every_recorded_disposition_names_a_ruling_on_disk():
    """A disposition is a closure of a question in a real ruling. One naming no ruling in staging,
    its advisor channel or either archive is a typo'd or renamed key that closes nothing."""
    dirs = [oqr.STAGING_DIR, oqr.STAGING_DIR / "done", oqr.STAGING_DIR / "advisor",
            oqr.STAGING_DIR / "advisor" / "done", oqr.IN_PROGRESS_DIR]
    names = {p.name for d in dirs if d.is_dir() for p in d.glob("*.md")}
    disp = oqr.load_dispositions()
    assert disp, "the live register must load"
    missing = sorted({r.get("ruling") for r in disp.values()} - names)
    assert not missing, missing
