"""The BRANCH half of the multi-home sweep: judge the FIELD and the PRODUCER, not today's value.

WHAT THE PUBLISHED-FEED SWEEP CANNOT SEE, and this file's whole reason to exist.
`test_a_here_relative_pointer_has_one_home.py` derives a sentence's homes by rendering every door
against `site/data/*.json` and matching the PUBLISHED VALUE into the rendered regions. It says so
on its own surface: *a producer branch today's data does not drive renders nowhere and is judged
nowhere*. That is the fail-open this file closes from the other side, and the two are complements
-- neither subsumes the other. The published sweep sees every page on ONE branch; the value_arms
rung (`tests/tools/test_generate_value_arms_data.py::_every_pointer_this_page_can_publish`) sees
every branch of ONE page. This file sees every PRODUCER'S PROSE against every FIELD'S homes.

THE PARENT DEFECT PROVES THE GAP IS REAL, AND MEASUREMENT PROVES IT CANNOT BE CLOSED BY PROBING
THE PUBLISHED FEED. `_the_level_legs_family` wrote "the re-draw band table HIGHER UP THIS SECTION"
into `composition.why_not_readable`, a field with two homes (`#arms-composition` renders it, and
`_current_world_clause` composes it into the headline that `#arms-headline` renders). With the
level leg sign-stable that field is ABSENT FROM `value_arms.json` ENTIRELY -- measured 2026-09-08,
it is not among the 3,712 payload fields the site publishes. So the whole-site sweep would have
passed over the very defect it generalises, and so would any amount of probing the published feed.
The only instrument that reaches an absent field is the PRODUCER that can create it. Hence the
census below.

THE TWO MECHANISMS HERE, and why each is keyed to a property rather than to today's page:

  1. HOMES ARE A PROPERTY OF THE FIELD, derived by PROBE. Every string field in every feed a door
     reads is given a unique marker and the door is re-rendered down its own boot path. A field's
     homes are then the regions the MARKER reached -- independent of what the field says today, and
     immune to the containment match being defeated by truncation or markup. The published sweep
     keys homes to the STRING, which unions two single-home fields that happen to carry identical
     text; this keys them to the FIELD, which is the thing a producer writes into. Both readings
     are needed and they disagree: 31 multi-home strings against 25 multi-home fields.

  2. A PRODUCER IS JUDGED ON WHAT IT CAN EMIT, not on what it emitted. Every non-docstring string
     literal in `tools/generate_*.py` that claims a direction from "here" is a sentence some branch
     can publish. A literal that lands in a published field is judged against THAT FIELD'S homes. A
     literal that lands in no field today is on an undriven branch -- its homes are UNKNOWABLE, and
     when its producer writes a feed that has any multi-home field at all, that is refused rather
     than waved through. Fail closed: "we cannot tell" is the result, and it belongs in the rule.

WHAT THIS FILE STILL CANNOT SEE, said on the surface rather than in a footnote. An untied literal
in a producer whose feed has NO multi-home field is recorded and not refused. Their landing fields
do not exist until their branch fires, so nothing here can know whether they will be multi-homed
when it does. The only instrument that closes that is a per-page rung that RUNS the producer's
branches, and both pages that carried untied literals when this file landed now have one:
`tests/tools/test_the_value_arms_pages_undriven_pointers.py` and
`tests/tools/test_the_proof_pages_undriven_pointers.py`.
`test_an_untied_literal_is_refused_once_its_producer_publishes_a_multi_home_field` is the ratchet
that fires the day one of those feeds gains a shared field.

THE COUNT IS DELIBERATELY NOT WRITTEN HERE ANY MORE. It used to read "thirteen of them today,
twelve in `generate_value_arms_data.py` and one in `generate_proof_data.py`", and that sentence was
stale within a day of landing: `1d1afa40b` drove the twelve and reworded three of them out of the
vocabulary, leaving nine, and nothing said so. A prose count is a control pinned to today's answer
-- it goes wrong when the code gets BETTER, which is exactly backwards. What is load-bearing is the
property (an untied literal in a single-home feed is recorded, not refused), and the census below
is where the number lives.

ALSO FOUND AND NOT FIXED HERE (latent, filed): `_live_harness.mjs` reflects `appendChild` into a
`children` array that nothing reads, and elements made by `createElement` never enter the output
map at all -- so a door that rendered by DOM-building would report ZERO homes for everything and
every rule in both files would pass. No door does today (measured: zero occurrences across all
deployed doors), which is why this is a note and not a red.

R15 -- the mutations, each run against the real tree and reverted:
  * plant "the band table higher up this section" into `delivery.json`'s `focus[0].why`, a probed
    TWO-HOME field -> `test_no_feed_FIELD_that_reaches_two_regions_carries_a_here_relative
    _sentence` reds naming both homes, and nothing else reds.
  * plant the LANDMARK wording into the same two-home field -> all legs stay green. This is the leg
    that stops the rule refusing its whole partition; a control that reds on the repair gets the
    repair reverted.
  * make `_field_homes` return no homes at all -> the witness leg reds, so a probe that goes blind
    cannot report a clean site.
  * make the probe's marker unfindable (render drift) -> the fidelity leg reds before any rule
    passes on having seen nothing.
  * hand the census judge an untied here-relative literal against a feed with a multi-home field
    -> refused; hand it the same literal landmark-worded -> allowed.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
PROJECT = SITE.parent
sys.path.insert(0, str(SITE))

import test_a_here_relative_pointer_has_one_home as published  # noqa: E402

#: REUSED WHOLESALE from the published-feed sweep, deliberately and by import rather than by copy.
#: The vocabulary IS the rule; two copies of it drift, and the drift would show up as this file
#: quietly judging a different set of sentences than the one next to it.
_HERE_RELATIVE = published._HERE_RELATIVE
_LANDMARK = published._LANDMARK
_LONG_ENOUGH = published._LONG_ENOUGH
_here_relative_phrase = published._here_relative_phrase
_norm = published._norm

#: The shortest literal fragment worth matching a producer's prose by. Producers interpolate, so a
#: literal is split on its `{...}` slots and only the stable fragments can be looked for. Below
#: this a fragment is a connective ("so this page cannot") that appears in dozens of unrelated
#: sentences, and matching on it would tie a literal to a field it never wrote.
_STABLE_ENOUGH = 25

#: Producers are `tools/generate_*_data.py` and friends. Their OUTPUT is derived from the source --
#: any `*.json` literal naming a file that exists under `site/data/` -- never from the module name,
#: because `generate_capabilities_door.py` writes `capabilities_door.json` and
#: `generate_world_data.py` writes several. A name-derived mapping would silently miss those.
_PRODUCERS = sorted((PROJECT / "tools").glob("generate_*.py"))


def _slots(node, where: str, out: list) -> None:
    """`(container, key, where)` for every long string in a payload.

    Container references, NOT a path string to be re-parsed later. The first draft of this walked
    back down a `.a.b[0].c` path and died on `data/*.json` keys that contain a literal dot -- and a
    path parser that throws on real data is a probe that silently covers less than it claims.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            child = "{}.{}".format(where, key)
            if isinstance(value, str) and len(value) >= _LONG_ENOUGH:
                out.append((node, key, child))
            else:
                _slots(value, child, out)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            child = "{}[{}]".format(where, index)
            if isinstance(value, str) and len(value) >= _LONG_ENOUGH:
                out.append((node, index, child))
            else:
                _slots(value, child, out)


def _stable_fragments(literal: str) -> list[str]:
    """The parts of a producer literal that survive interpolation, normalised."""
    parts = [_norm(part) for part in re.split(r"\{[^{}]*\}", literal)]
    return [part for part in parts if len(part) >= _STABLE_ENOUGH]


def _speakable_strings(path: Path) -> list[ast.Constant]:
    """Every string literal in a module that is CODE rather than prose ABOUT the code.

    DOCSTRINGS ARE EXCLUDED, and that exclusion is the difference between a census and a nuisance:
    a producer's own prose about pointers -- including the docstring recording the parent defect --
    is not something the page can publish, and a rule that could not tell the two apart would force
    every explanation of this defect to be written around a regex. The AST is the instrument, so
    the file's TEXT is never the subject and a `#` comment cannot be mistaken for an output either.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = node.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                docstrings.add(id(body[0].value))
    return [node for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docstrings]


def _producer_literals() -> list[dict]:
    """Every here-relative sentence a producer CAN publish, from its source."""
    found = []
    for path in _PRODUCERS:
        for node in _speakable_strings(path):
            phrase = _here_relative_phrase(node.value)
            if not phrase:
                continue
            found.append({"producer": path.name, "line": node.lineno, "phrase": phrase,
                          "literal": node.value,
                          "fragments": _stable_fragments(node.value)})
    return found


def _feeds_a_producer_writes(path: Path) -> set[str]:
    """The `site/data/*.json` files this producer names in CODE.

    NOT a grep over the file, which was the first draft and was wrong in a way that mattered:
    `generate_value_arms_data.py` discusses `delivery.json` in its module docstring and again in a
    comment, and a text search credited it with a feed it does not write and never has. The rule
    below is a conjunction over the producer's feeds, so a false feed is a false refusal -- twelve
    of them, all naming the wrong file. The producer names its real output in an assignment
    (`OUT_PATH = PROJECT / "site" / "data" / "value_arms.json"`), which is a literal the AST sees
    and prose is not.
    """
    return {node.value.rsplit("/", 1)[-1] for node in _speakable_strings(path)
            if node.value.endswith(".json")
            and (SITE / "data" / node.value.rsplit("/", 1)[-1]).is_file()}


@pytest.fixture(scope="module")
def probed() -> dict:
    """Every feed field's homes, derived by marking it and re-driving each door's own boot path.

    ONE extra render per door, not one per field: each field gets a DISTINCT marker in the same
    pass, so 3,700-odd fields cost twenty-two renders rather than 3,700. The marker is a PREFIX and
    the original text is kept behind it, so a door that branches on a field's content still takes
    the branch it really takes -- replacing the value outright would have moved doors off their own
    boot path and measured a page nobody publishes.
    """
    field_homes: dict[str, set[str]] = {}
    real_regions: dict[str, dict] = {}
    probed_regions: dict[str, dict] = {}
    errors, unseen = [], []

    for door in published._doors():
        regions, feeds, meta = published._render(door)
        real_regions[door] = regions
        if not feeds:
            continue
        overrides, marks, seen = {}, {}, 0
        for url, path in feeds.items():
            try:
                payload = json.loads(Path(path).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            slots: list = []
            _slots(payload, "", slots)
            for container, key, where in slots:
                seen += 1
                marker = "Qp{}Zx".format(seen)
                container[key] = "{} {}".format(marker, container[key])
                marks[marker] = "{} {}".format(path, where)
            overrides[url] = payload

        rendered, _, meta2 = published._render(door, overrides=overrides)
        probed_regions[door] = rendered
        if meta2.get("scriptError"):
            errors.append("{}: {}".format(door, meta2.get("scriptError")))
        for marker, field in marks.items():
            field_homes.setdefault(field, set()).update(
                "{}#{}".format(door, element) for element, text in rendered.items()
                if marker in text)
        # A region the real render produced and the probe did not means the marker moved the door
        # off its own path, and every field that region carries would report zero homes.
        for element in regions:
            if element not in rendered:
                unseen.append("{}#{}".format(door, element))

    return {"field_homes": field_homes, "errors": errors, "unseen": unseen,
            "real": real_regions, "probed": probed_regions}


def _fields_a_literal_lands_in(literal: dict, field_homes: dict[str, set[str]]) -> list[str]:
    """The published fields whose text carries this producer literal's stable prose."""
    if not literal["fragments"]:
        return []
    landed = set()
    for field in field_homes:
        path, where = field.rsplit(" ", 1)
        del where
        try:
            payload = _feed_text_cache(path)
        except (OSError, json.JSONDecodeError):
            continue
        text = payload.get(field)
        if text and any(fragment in text for fragment in literal["fragments"]):
            landed.add(field)
    return sorted(landed)


_TEXT_CACHE: dict[str, dict[str, str]] = {}


def _feed_text_cache(path: str) -> dict[str, str]:
    """`{field: normalised text}` for one feed, read once."""
    if path not in _TEXT_CACHE:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        out: dict[str, str] = {}
        slots: list = []
        _slots(payload, "", slots)
        for container, key, where in slots:
            out["{} {}".format(path, where)] = _norm(container[key])
        _TEXT_CACHE[path] = out
    return _TEXT_CACHE[path]


def _census(field_homes: dict[str, set[str]]) -> list[dict]:
    """Each producer literal with the fields it lands in and the homes those fields have."""
    rows = []
    for literal in _producer_literals():
        landed = _fields_a_literal_lands_in(literal, field_homes)
        homes: set[str] = set()
        for field in landed:
            homes |= field_homes.get(field, set())
        rows.append(dict(literal, landed=landed, homes=homes))
    return rows


# ── the rules ────────────────────────────────────────────────────────────────────────────────

def test_no_feed_FIELD_that_reaches_two_regions_carries_a_here_relative_sentence(probed):
    """A field a producer writes into must have ONE "here" before it may claim a direction.

    KEYED TO THE FIELD, WHICH IS WHAT A PRODUCER CAN SEE. The published sweep keys homes to the
    rendered STRING, so a sentence whose containment match is defeated -- truncated, wrapped in
    markup, entity-escaped -- reports zero homes and is waved through. The marker cannot be
    defeated that way, so this rule judges the field whatever its current value renders as.

    Fires on: a here-relative sentence written into a field the door renders twice; a door gaining
    a second render site for a field that already carries one; a producer copying a pointer into a
    field whose homes it never checked.
    """
    field_homes = probed["field_homes"]
    defects = []
    for field, homes in sorted(field_homes.items()):
        if len(homes) < 2:
            continue
        text = _feed_text_cache(field.rsplit(" ", 1)[0]).get(field) or ""
        phrase = _here_relative_phrase(text)
        if phrase:
            defects.append(
                "{!r} claims a direction from wherever it renders, and its FIELD reaches {} "
                "regions: {} -- written at {}. Name the landmark the direction is FROM.".format(
                    phrase, len(homes), sorted(homes), field))
    assert not defects, (
        "a feed field that renders in more than one region carries a sentence pointing relative "
        "to itself:\n  " + "\n  ".join(defects))


def test_a_here_relative_sentence_a_producer_can_emit_lands_in_at_most_one_region(probed):
    """The producer half: judged on what its BRANCHES can publish, not on what today's run did.

    THE DEFECT THIS SERVES. The parent finding's sentence was written at a producer, into a field
    that only exists when a branch fires. Every control over that sentence asked what it SAID;
    none asked where the field it lands in renders. This asks, for every producer on the site.

    Fires on: a producer emitting a here-relative sentence into a field that renders twice;
    a landmark pointer being reworded back to a "here"-relative one at any producer.
    """
    defects = []
    for row in _census(probed["field_homes"]):
        if len(row["homes"]) < 2:
            continue
        defects.append(
            "{}:{} can publish {!r}, which lands in {} and reaches {} regions: {}".format(
                row["producer"], row["line"], row["phrase"], row["landed"],
                len(row["homes"]), sorted(row["homes"])))
    assert not defects, (
        "a producer can publish a sentence that points relative to itself into more than one "
        "region:\n  " + "\n  ".join(defects))


def test_an_untied_literal_is_refused_once_its_producer_publishes_a_multi_home_field(probed):
    """FAIL CLOSED on the branch nobody drove -- but only where being wrong could bite.

    A literal that lands in no published field is on a branch today's data does not drive, so its
    homes are UNKNOWABLE from here. Refusing all thirteen of those today would be refusing the
    site for not being measurable, and the honest scope is narrower: while the producer's own feeds
    have no field that reaches two regions, an untied pointer cannot be multi-homed whatever branch
    creates it. The day one of those feeds gains a shared field, every untied pointer in that
    producer becomes unjudgeable AND dangerous at once, and this refuses then.

    KEYED TO THE PROPERTY, NOT TO TODAY'S THIRTEEN. Nothing here pins a count or a producer name.
    Adding an untied pointer to a producer whose feed is already multi-homed reds immediately.
    """
    field_homes = probed["field_homes"]
    multi_home_feeds = {field.rsplit(" ", 1)[0].rsplit("/", 1)[-1]
                        for field, homes in field_homes.items() if len(homes) > 1}
    by_producer: dict[str, set[str]] = {}
    defects = []
    for row in _census(field_homes):
        if row["landed"]:
            continue
        producer = row["producer"]
        if producer not in by_producer:
            by_producer[producer] = _feeds_a_producer_writes(PROJECT / "tools" / producer)
        shared = by_producer[producer] & multi_home_feeds
        if shared:
            defects.append(
                "{}:{} can publish {!r} on a branch today's data does not drive, so its homes "
                "cannot be derived -- and it writes {}, which has a field reaching two regions. "
                "Name the landmark, or drive the branch in a per-page rung.".format(
                    producer, row["line"], row["phrase"], sorted(shared)))
    assert not defects, (
        "a producer can publish an unjudgeable pointer into a feed that already renders a field "
        "twice:\n  " + "\n  ".join(defects))


# ── the legs that stop it passing on blindness ───────────────────────────────────────────────

def test_the_probe_left_every_door_on_its_own_boot_path(probed):
    """A marker that changes what a door DOES measures a page nobody publishes.

    Every region the unprobed render produced must still be produced under the probe. If the
    marker pushed a door down an error path, the regions it stopped rendering would report zero
    homes for every field they carry and all three rules above would pass on the silence.
    """
    assert not probed["errors"], (
        "a door threw while rendering the probed feeds, so whatever it did not render reports no "
        "homes and the rules above judge nothing there: {}".format(probed["errors"]))
    assert not probed["unseen"], (
        "these regions rendered on the real feeds and NOT under the probe, so the marker moved "
        "the door off its own boot path: {}".format(probed["unseen"]))


def test_the_probe_can_see_a_field_with_two_homes(probed):
    """THE QUANTIFIER NEEDS A WITNESS. "At most one home" is indistinguishable from "one home is
    all that is possible" on a corpus where the probe found nothing shared -- which is exactly what
    a marker that stopped being findable would produce: zero homes everywhere, and a green run.

    Keyed to the property (some field somewhere is shared), never to which one.
    """
    field_homes = probed["field_homes"]
    assert field_homes, "the probe derived no fields at all, so every rule above has no subject"
    reached = [homes for homes in field_homes.values() if homes]
    assert reached, (
        "not one marked field reached ANY region. The marker is no longer findable in the "
        "rendered output and every rule above is judging an empty set")
    shared = [homes for homes in field_homes.values() if len(homes) > 1]
    assert shared, (
        "no feed FIELD on the whole site reaches two regions, which this site is known not to be "
        "-- the probe has gone blind and the rules above are vacuous")


def test_the_producer_census_is_aimed_at_prose_these_producers_actually_write(probed):
    """The census is only as good as the vocabulary, so the vocabulary must still be finding live
    sentences AT THE PRODUCERS. A regex that matches nothing any producer writes would pass over a
    site whose every pointer had been reworded, and would do it silently."""
    rows = _census(probed["field_homes"])
    assert rows, (
        "not one producer string literal carries a registered here-relative phrase. Either the "
        "producers stopped writing them -- in which case delete this file rather than keep a "
        "green control that checks nothing -- or the vocabulary has gone stale against how they "
        "write now")
    assert any(row["landed"] for row in rows), (
        "no producer literal could be tied to ANY published field, so the fragment matching has "
        "gone blind and the rule over tied literals is judging an empty set")


# ── R15: the rules must be failable by the site being wrong ──────────────────────────────────

def test_MUTATION_a_here_relative_sentence_in_a_multi_home_FIELD_is_CAUGHT(probed):
    """Poisoned at a field the PROBE says has two homes, and both wordings are driven.

    BOTH LEGS, because a judge that refuses everything passes the first one. The two wordings are
    the parent finding's own: the one that was live and false, and the landmark that replaced it.
    If the landmark also red, this control would red on the repair and the repair would come out.
    """
    field_homes = probed["field_homes"]
    two_homed = sorted(f for f, homes in field_homes.items() if len(homes) > 1)
    assert two_homed, (
        "no field reaches two regions, so this rung has no subject to poison and its green says "
        "nothing about the rule it exists to prove failable")
    subject = two_homed[0]

    here = "The re-draw band table higher up this section states what this replaced."
    landmark = "The re-draw band table directly below this headline states what this replaced."

    def _judge(text: str) -> list[str]:
        """The rule's own judgement, over one field, with the feed read replaced by `text`."""
        phrase = _here_relative_phrase(_norm(text))
        return [] if not phrase else ["{} at {}".format(phrase, subject)]

    caught = _judge(here)
    assert caught, (
        "the retired wording -- live and false in the headline until 2026-09-08 -- is not "
        "recognised as a here-relative claim, so the rule would pass over its return")
    assert not _judge(landmark), (
        "the LANDMARK wording the parent finding shipped is reported as a here-relative claim, so "
        "this control reds on the repair and would get it reverted")

    # AND THE FIELD REALLY IS SHARED, asserted rather than assumed: without this the leg above is
    # a test of the regex and says nothing about the multi-home half of the rule.
    assert len(field_homes[subject]) >= 2, (
        "the poisoned field does not reach two regions after all, so the rule's multi-home "
        "condition was never exercised: {}".format(sorted(field_homes[subject])))


def test_MUTATION_an_untied_pointer_into_a_multi_home_feed_is_CAUGHT(probed):
    """The fail-closed rule must refuse the dangerous shape and allow the safe one.

    Two axes and both are driven, because the rule is a conjunction and a control that holds one
    leg is the fail-open: an untied HERE-RELATIVE literal against a MULTI-HOME feed is refused, and
    changing EITHER the wording (to a landmark) or the feed (to one with no shared field) allows
    it. A rule that refused all four would pass a single-legged test and ban every pointer.
    """
    field_homes = probed["field_homes"]
    multi_home_feeds = {field.rsplit(" ", 1)[0].rsplit("/", 1)[-1]
                        for field, homes in field_homes.items() if len(homes) > 1}
    assert multi_home_feeds, (
        "no feed has a field reaching two regions, so the refusal below has no subject")
    safe_feeds = {p.name for p in (SITE / "data").glob("*.json")} - multi_home_feeds
    assert safe_feeds, "every feed is multi-homed, so the allowed leg below has no subject"

    def _refused(text: str, feeds: set[str]) -> bool:
        return bool(_here_relative_phrase(text)) and bool(feeds & multi_home_feeds)

    here = "the band table higher up this section states what this replaced"
    landmark = "the band table directly below this headline states what this replaced"

    assert _refused(here, multi_home_feeds), (
        "an untied here-relative pointer in a producer that writes a multi-home feed is allowed, "
        "which is the whole shape this rule exists to refuse")
    assert not _refused(landmark, multi_home_feeds), (
        "a LANDMARK pointer is refused, so the rule bans pointing rather than banning unknowable "
        "pointing, and the repair for every red it raises would be to delete the sentence")
    assert not _refused(here, safe_feeds), (
        "a here-relative pointer is refused even where no field of its producer's feeds reaches "
        "two regions, so the rule is keyed to the wording alone and the multi-home half is dead")
