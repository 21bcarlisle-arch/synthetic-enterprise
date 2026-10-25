"""The map generates its links and gaps from the register, and each finding it exists for can fire.

The defect this names: a hand-matched map (the 24 Oct mock-up) that reads complete while a second
home, a concept sharing a name with another, or an empty layer nobody explained goes unseen. Each
test builds a small tree and says which way it would go red.
"""
from __future__ import annotations

import json

import yaml

from tools import the_map

ROWS = [
    {"module": "simulation.rails", "path": "simulation/rails.py", "status": "wired",
     "callers": ["x"], "evidence": ["t"], "plain_words": "The bank's side of a collection."},
    {"module": "company.billing.desk", "path": "company/billing/desk.py", "status": "wired",
     "callers": ["x"], "evidence": [], "plain_words": "Presents each collection."},
    {"module": "company.billing.old_mandate_register", "path": "company/billing/old_mandate_register.py",
     "status": "orphan", "callers": [], "evidence": [], "plain_words": "Keeps each dd mandate."},
    {"module": "company.billing.unrelated", "path": "company/billing/unrelated.py", "status": "wired",
     "callers": ["x"], "evidence": [], "plain_words": "Prints a bill."},
]


def _tree(tmp_path, concepts):
    (tmp_path / "docs/design/the_map").mkdir(parents=True)
    (tmp_path / "docs/market_research").mkdir(parents=True)
    (tmp_path / "site/data").mkdir(parents=True)
    (tmp_path / the_map.REGISTER).write_text(yaml.safe_dump({"spines": {}, "concepts": concepts}))
    (tmp_path / the_map.PAGES).write_text(json.dumps({"pages": {"debt": {"meta": {"source": "see n2.md"}}}}))
    (tmp_path / the_map.MECHANISMS).write_text("principles: {}\n")
    (tmp_path / "docs/market_research/n1.md").write_text("# n1\n**Knowledge:** debt\n")
    (tmp_path / "docs/market_research/n2.md").write_text("# n2\n")
    (tmp_path / "docs/market_research/n3.md").write_text("# n3\n**Knowledge:** none\n")
    return tmp_path


def _mandate(**over):
    c = {"id": "c.mandate", "prefLabel": "Direct debit mandate", "altLabel": ["dd mandate"],
         "definition": "d", "match": ["Bacs"], "placed": ["supplier/Collect"], "page": "debt",
         "world": ["simulation.rails"], "wall": [], "supplier": ["company.billing.desk"],
         "gap": {"wall": "not observable"}}
    c.update(over)
    return c


def _kinds(m):
    return {f["kind"] for f in m["findings"]}


def test_a_module_carrying_the_concepts_name_is_found_and_its_home_is_not(tmp_path):
    """MUTATION: drop the `any(p.search(...))` term search and `also_named` is empty, so this fires;
    drop the `not in declared` filter and the home is listed against itself, so this fires too."""
    m = the_map.build(_tree(tmp_path, [_mandate()]), rows=ROWS)
    also = [a["module"] for a in m["concepts"][0]["also_named"]]
    assert also == ["company.billing.old_mandate_register"]
    assert "also named, not declared" in _kinds(m)


def test_one_name_on_two_concepts_is_a_finding(tmp_path):
    """MUTATION: remove the `term_owner` collision check and this fires. The control over the whole
    partition: the same register without the collision raises no such finding."""
    twin = _mandate(id="c.twin", prefLabel="Mandate register", altLabel=["dd mandate"])
    assert "one name, two concepts" in _kinds(the_map.build(_tree(tmp_path / "a", [_mandate(), twin]), rows=ROWS))
    assert "one name, two concepts" not in _kinds(the_map.build(_tree(tmp_path / "b", [_mandate()]), rows=ROWS))


def test_an_empty_layer_needs_a_reason_and_a_reason_is_enough(tmp_path):
    """MUTATION: make the `need not in gaps` test always true and the second build fires; make it
    always false and the first one fires."""
    unexplained = _mandate(gap={})
    assert "layer missing, no reason" in _kinds(the_map.build(_tree(tmp_path / "a", [unexplained]), rows=ROWS))
    assert "layer missing, no reason" not in _kinds(the_map.build(_tree(tmp_path / "b", [_mandate()]), rows=ROWS))


def test_a_home_that_is_gone_or_uncalled_or_on_the_wrong_side_is_named(tmp_path):
    """MUTATION: grade every home `wired` and this fires."""
    c = _mandate(world=["company.billing.desk"], supplier=["company.billing.old_mandate_register", "company.gone"])
    kinds = _kinds(the_map.build(_tree(tmp_path, [c]), rows=ROWS))
    assert {"home wrong side", "home orphan", "home gone"} <= kinds


def test_notes_attach_by_their_own_line_or_by_the_pages_citation(tmp_path):
    """MUTATION: drop either route in `notes_by_page` and one of n1, n2 goes missing; read
    `Knowledge: none` as a page and n3 is counted on one."""
    m = the_map.build(_tree(tmp_path, [_mandate()]), rows=ROWS)
    assert m["concepts"][0]["page"]["notes"] == ["n1", "n2"]
    assert m["notes"]["on_no_page"] == ["n3"]


def test_the_real_register_loads_and_every_relation_names_a_concept():
    """The pilot register itself: a relation to an id nobody defined is a link to nothing."""
    reg = the_map.load_register()
    ids = {c["id"] for c in reg["concepts"]}
    assert len(ids) == len(reg["concepts"])
    targets = {t for c in reg["concepts"] for ts in (c.get("relations") or {}).values() for t in ts}
    assert targets <= ids, sorted(targets - ids)
    assert all(c.get("placed") for c in reg["concepts"]), "a concept on no spine"


def _covered(tmp_path, machinery=None, concepts=None):
    root = _tree(tmp_path, concepts or [_mandate()])
    reg = yaml.safe_load((root / the_map.REGISTER).read_text())
    if machinery:
        reg["machinery"] = machinery
    (root / the_map.REGISTER).write_text(yaml.safe_dump(reg))
    return the_map.build(root, rows=ROWS)["coverage"]


def test_coverage_counts_what_attaches_and_what_attaches_to_none(tmp_path):
    """The control over the whole partition: attached, machinery and loose are each non-empty at once.
    MUTATION: count every module as attached and `on_none` is 0; drop the machinery rule and
    `machinery` is 0; count notes by their own Knowledge line only and n2 (cited) drops out."""
    cov = _covered(tmp_path, machinery=[{"prefix": "company.billing.unrelated", "reason": "prints"}])
    assert cov["modules"] == {"total": 4, "on_a_concept": 3, "machinery": 1, "on_none": 0, "sample_on_none": []}
    loose = _covered(tmp_path / "b")
    assert loose["modules"]["on_none"] == 1 and loose["modules"]["sample_on_none"] == ["company.billing.unrelated"]
    assert loose["notes"]["total"] == 3 and loose["notes"]["on_a_concept"] == 2 and loose["notes"]["on_none"] == 1
    assert _covered(tmp_path / "c", concepts=[_mandate(page=None)])["pages"]["on_none"] == ["debt"]


def test_a_machinery_ruling_without_a_reason_rules_nothing(tmp_path):
    """MUTATION: accept a prefix with no reason and the unreasoned prefix hides a loose module."""
    cov = _covered(tmp_path, machinery=[{"prefix": "company.billing.unrelated"}])
    assert cov["modules"]["on_none"] == 1


def _ruled(tmp_path, rulings):
    root = _tree(tmp_path, [_mandate()])
    (root / the_map.RULINGS).write_text(yaml.safe_dump(rulings))
    return the_map.build(root, rows=ROWS)["coverage"]["notes"]


def test_a_ruling_moves_a_note_off_the_unruled_count_by_the_way_it_was_ruled(tmp_path):
    """The control over the partition: attach, owed and dead are each taken at once. n3 sits on no page.
    MUTATION: ignore `attach` and n3 stays on no page; ignore `owed` or `dead` and `unruled` is not 0;
    accept a dead ruling with no reason and n3 is ruled by a row that says nothing."""
    base = _ruled(tmp_path, {})
    assert base["on_no_page"] == 1 and base["unruled"] == 1
    owed = _ruled(tmp_path / "o", {"owed": {"switching": ["n3"]}})
    dead = _ruled(tmp_path / "d", {"dead": [{"reason": "a prediction", "notes": ["n3"]}]})
    attach = _ruled(tmp_path / "a", {"attach": {"debt": ["n3"]}})
    assert (owed["owed"], owed["unruled"]) == (1, 0)
    assert (dead["dead"], dead["unruled"]) == (1, 0)
    assert (attach["on_no_page"], attach["on_a_concept"]) == (0, 3)
    assert _ruled(tmp_path / "r", {"dead": [{"notes": ["n3"]}]})["unruled"] == 1


def test_every_ruling_in_the_register_names_a_real_note_and_the_right_kind_of_page():
    """Key to the property: an attach ruling needs a page that exists, an owed one a page that does not
    yet, and every ruled note must exist. MUTATION: rule `n` for a deleted note, or `owed` a page that
    has since landed, and this fires, which is the signal to move the ruling to `attach`."""
    root = the_map.ROOT
    rulings = the_map.load_rulings(root)
    notes = {p.stem for p in (root / the_map.NOTES_DIR).glob("*.md")}
    pages = {p.name for p in (root / "site/knowledge").iterdir() if p.is_dir() and (p / "index.html").exists()}
    ruled = [n for ns in (rulings.get("attach") or {}).values() for n in ns]
    ruled += [n for ns in (rulings.get("owed") or {}).values() for n in ns]
    ruled += [n for row in rulings.get("dead") or [] for n in row["notes"]]
    assert set(ruled) <= notes, sorted(set(ruled) - notes)
    assert len(ruled) == len(set(ruled)), "a note ruled twice"
    assert set(rulings["attach"]) <= pages, sorted(set(rulings["attach"]) - pages)
    assert not set(rulings["owed"]) & pages, sorted(set(rulings["owed"]) & pages)
    assert all(row.get("reason") for row in rulings["dead"])
