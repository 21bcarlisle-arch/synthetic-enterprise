"""What we have learned: each canon principle, and the code that holds it (tools/canon_lessons.py)."""
from __future__ import annotations

from pathlib import Path

from tools import canon_lessons as cl

CANON = """# Canon

## 3. The world and the wall (W)

**W1. The wall and its test.** The company "may only know what a real UK supplier could know". More. *(June; 9 Oct)*

**W2. The gap is the product.**
- First, a list item that carries the words.
- Second.

## 15. The rulings of 12 October, and what is owed

**W9. Not a principle.** It sits under the rulings.
"""


def _root(tmp_path, bindings):
    (tmp_path / "docs" / "design").mkdir(parents=True)
    (tmp_path / cl.CANON).write_text(CANON, encoding="utf-8")
    (tmp_path / cl.BINDINGS).write_text(bindings, encoding="utf-8")
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "held.py").write_text("", encoding="utf-8")
    return tmp_path


def test_every_status_can_be_reached_and_each_is_the_right_one(tmp_path):
    """The partition over the whole: proven, held, gone and unbound each reached.

    MUTATION: `status=` with the GONE branch removed (a vanished path reads as held) -> red here.
    MUTATION: `_shown` returning 0 for a marked test that names the module -> red here."""
    root = _root(tmp_path, "principles:\n  W1:\n    mechanisms: [tools/held.py]\n")
    marked = {"tests/test_held.py": "from tools import held\n"}
    by = {r["id"]: r for r in cl.build(root, marked=marked)["rows"]}
    assert by["W1"]["status"] == cl.HELD_PROVEN and by["W2"]["status"] == cl.UNBOUND
    assert cl.build(root, marked={})["rows"][0]["status"] == cl.HELD
    (root / cl.BINDINGS).write_text("principles:\n  W1:\n    mechanisms: [tools/gone.py]\n")
    assert cl.build(root, marked=marked)["rows"][0]["status"] == cl.GONE


def test_a_principle_is_read_in_its_own_words_and_only_from_the_numbered_areas(tmp_path):
    """A principle whose text runs on below its title is read from the list; s15 holds none.

    MUTATION: drop the continuation-line branch in `principles` -> W2's words are empty, red.
    MUTATION: drop the `n <= LAST_PRINCIPLE_AREA` guard -> W9 is read as a principle, red."""
    rows = cl.principles(_root(tmp_path, "principles: {}\n"))
    assert [r["id"] for r in rows] == ["W1", "W2"]
    assert rows[0]["words"] == 'The company "may only know what a real UK supplier could know".'
    assert rows[0]["when"] == "June; 9 Oct" and rows[0]["area"] == "The world and the wall"
    assert rows[1]["words"].startswith("First, a list item")


def test_check_refuses_a_gone_mechanism_and_a_binding_to_no_principle(tmp_path):
    """MUTATION: `problems` returning [] for gone rows -> red. MUTATION: dropping unknown_ids -> red."""
    root = _root(tmp_path, "principles:\n  W1:\n    mechanisms: [tools/gone.py]\n  Z9: {}\n")
    bad = cl.problems(cl.build(root, marked={}))
    assert any("W1" in b and "tools/gone.py" in b for b in bad)
    assert any(b.startswith("Z9:") for b in bad)
    (root / cl.BINDINGS).write_text("principles:\n  W1:\n    mechanisms: [tools/held.py]\n")
    assert cl.problems(cl.build(root, marked={})) == []


def test_the_headline_counts_an_unbound_principle_as_unbound(tmp_path):
    """The page never counts an unlinked principle as enforced.

    MUTATION: headline's bound = total -> '2 of the canon's 2 principles' -> red."""
    page = cl.render_html(cl.build(_root(tmp_path, "principles:\n  W1:\n    mechanisms: [tools/held.py]\n"),
                                   marked={}))
    assert "1 of the canon's 2 principles name the code" in page
    assert "The other 1 are not yet linked" in page


def test_the_real_binding_file_names_only_code_that_exists():
    """The shipped bindings hold: no gone path, no binding to a principle the canon lacks."""
    root = Path(__file__).resolve().parents[2]
    assert cl.problems(cl.build(root, marked={})) == []
