"""Canon against canon (alignment steer step 6a): each of the three conditions can fail, and the live
pages are checked against a non-zero count of quotes."""
from __future__ import annotations

from pathlib import Path

from tools import canon_against_canon as cac

CANON = """# The Director's Canon

**K4. The practitioner comes last.** "When a question touches regulation, search Ofgem's licence conditions first."

**G8. Authority.** "yes and go are complete, and nothing else is needed"

## 16. Superseded and retired

- **Asking him.** "Say so and ask before you build anything" (1 Sept) → K4.
"""


def _tree(tmp_path: Path, page: str) -> Path:
    (tmp_path / "docs" / "design").mkdir(parents=True)
    (tmp_path / "docs" / "design" / "DIRECTOR_CANON.md").write_text(CANON, encoding="utf-8")
    (tmp_path / "PAGE.md").write_text(page, encoding="utf-8")
    return tmp_path


def _run(tmp_path, page):
    return cac.scan(_tree(tmp_path, page), pages=("PAGE.md",))


def test_a_verbatim_quote_passes_and_is_counted(tmp_path):
    found, checked = _run(tmp_path, '**K4:** "When a question touches regulation, search Ofgem\'s '
                          'licence conditions first." (canon K4)\n')
    assert found == [] and checked == 1


def test_a_reworded_canon_line_is_misquoted(tmp_path):
    found, _ = _run(tmp_path, '(canon K4) "When a question touches regulation, ask the director first."\n')
    assert any("MISQUOTED" in f for f in found), found


def test_a_cited_id_canon_does_not_define_fails(tmp_path):
    found, _ = _run(tmp_path, "As canon K99 says, nothing.\n")
    assert any("NO SUCH ID" in f and "K99" in f for f in found), found


def test_a_superseded_phrase_presented_as_current_fails_and_marked_retired_passes(tmp_path):
    found, _ = _run(tmp_path, '"Say so and ask before you build anything."\n')
    assert any("SUPERSEDED" in f for f in found), found
    found, _ = cac.scan(tmp_path, pages=("PAGE.md",)) if False else _run(
        tmp_path / "b", 'This was retired: "Say so and ask before you build anything."\n')
    assert not any("SUPERSEDED" in f for f in found), found


def test_the_live_standing_pages_hold_against_canon_over_a_real_denominator():
    found, checked = cac.scan()
    assert found == [], found
    assert checked > 0, "no attributed quote was compared, so a clean result would mean nothing"


def test_the_monday_step_carries_the_section_and_says_so_when_it_cannot_read(monkeypatch):
    from background import weekly_rhythm as wr
    assert wr._canon_against_canon_section()[0] == "## Canon against canon"
    monkeypatch.setattr(cac, "scan", lambda *a, **k: (_ for _ in ()).throw(OSError("gone")))
    assert any("UNAVAILABLE" in ln for ln in wr._canon_against_canon_section())
