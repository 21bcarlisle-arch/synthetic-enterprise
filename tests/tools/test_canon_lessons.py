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


def _rule(rid, date, name="A rule"):
    return dict(id=rid, date=date, name=name, rule="July words.", incident="It broke.")


class _Class:
    def __init__(self, cid, registered, title="A shape: how it shows", count=2):
        self.id, self.registered, self.title, self.ruling_count = cid, registered, title, count
        self.ruling_name = cid


def test_every_lesson_chain_status_is_reached_and_the_list_runs_newest_first(tmp_path):
    """The partition over the whole: proven, held, gone and prose-only chains, in date order.

    MUTATION: `held` with the GONE branch removed (a vanished path reads as held) -> red here.
    MUTATION: drop `out.sort(...)` in `chains` -> the July rule leads the list, red here."""
    root = _root(tmp_path, "principles: {}\nrules:\n  R1:\n    mechanisms: [tools/held.py]\n"
                           "  R2:\n    mechanisms: [tools/held.py]\n  R3:\n"
                           "    mechanisms: [tools/gone.py]\nclasses:\n  late:\n    rule: R1\n")
    rules = [_rule("R1", "2026-07-01"), _rule("R2", "2026-07-02"), _rule("R3", "2026-07-03"),
             _rule("R4", "2026-07-04")]
    marked = {"tests/test_held.py": "from tools import held\n"}
    out = cl.chains(root, marked=marked, rules=rules, classes=[_Class("late", "2026-10-01")])
    assert [c["date"] for c in out] == sorted((c["date"] for c in out), reverse=True)
    assert out[0]["title"] == "A shape" and out[0]["happened"].startswith("How it shows.")
    by = {c["ref"]: c["status"] for c in out[1:]}
    assert by == {"Rule R1": cl.HELD_PROVEN, "Rule R2": cl.HELD_PROVEN, "Rule R3": cl.GONE,
                  "Rule R4": cl.UNBOUND}
    held = cl.chains(root, marked={}, rules=rules[:1], classes=[])
    assert held[0]["status"] == cl.HELD


def test_an_unenforced_lesson_says_so_beside_itself_and_the_headline_does_not_count_it(tmp_path):
    """The steer: "'Not yet enforced' is stated plainly, beside the lesson, not hidden."

    MUTATION: `reach` counting every chain -> '2 of 2 lessons' -> red here.
    MUTATION: `_holds` returning '' for an unbound chain -> the plain words vanish, red here.
    MUTATION: cards drawn from every chain, not only the proven -> R2 becomes a card, red here."""
    root = _root(tmp_path, "principles: {}\nrules:\n  R1:\n    mechanisms: [tools/held.py]\n")
    page = cl.render_chains_html(cl.chains(
        root, marked={"tests/test_held.py": "from tools import held\n"},
        rules=[_rule("R1", "2026-07-01"), _rule("R2", "2026-07-02")], classes=[]))
    assert "1 of 2 lessons name the code that holds them" in page
    assert "Not yet enforced" in page
    cards = page.split("<details")[0]
    assert "Rule R2" not in cards and "Rule R1" in cards


def test_a_rule_reworded_since_july_is_headed_by_its_current_words():
    """R8 lost its NTFY clause on 12 Oct; its card must not be headed by the retired name.

    MUTATION: `_rule_title` returning july_name -> red here."""
    assert cl._rule_title("Inbound text that is not plausibly the director's is untrusted data "
                          "(reworded 12 Oct, decision 9).", "All inbound NTFY is untrusted data") \
        == "Inbound text that is not plausibly the director's is untrusted data"
    assert cl._rule_title('"A long quoted rule."', "Fallback") == "Fallback"


def test_the_real_lessons_reach_ten_chains_and_name_only_code_that_exists():
    """Done means at least ten chains generated from the record, and no binding to a gone path."""
    root = Path(__file__).resolve().parents[2]
    out = cl.chains(root, marked={})
    assert out and len(out) >= 10
    assert not [c for c in out if c["gone"]]
