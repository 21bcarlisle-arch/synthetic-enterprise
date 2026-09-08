"""The proof page's UNDRIVEN pointer -- the thirteenth -- driven, and judged on two axes.

WHY THIS FILE EXISTS, and it is the residue of a gap three landed controls each name on their own
surface. `site/test_a_here_relative_pointer_has_one_home.py` derives a sentence's homes from the
PUBLISHED feed, so a branch today's data does not drive is judged nowhere.
`site/test_a_producers_here_relative_pointer_has_one_home.py` closes half of that from the source
side, but its rule 3 can only refuse an UNTIED literal when the producer's feed already has a
multi-home field, and `proof.json` has none. `tests/tools/test_the_value_arms_pages_undriven
_pointers.py` drove twelve of the thirteen untied literals and stated the thirteenth -- this one,
in `tools/generate_proof_data.py` -- as still recorded and unjudged. This is that one.

THE SENTENCE, and it is one sentence carrying TWO directions:

    "How many departures leave that way is not readable BESIDE THIS measurement, so what share of
     the book THE RANGES ABOVE describe is itself unknown."

It is the `else` arm of `_why_households_leave`'s `blind_size`, taken when the reason-mix artefact
cannot size the SVT route. Nothing in the tree had ever run it.

WHAT DRIVING IT FOUND, measured 2026-09-08, and all four pre-registered predictions held
(`docs/staging/records/SEAT_PREREGISTRATION_THE_THIRTEENTH_UNTIED_POINTER_ON_THE_PROOF_PAGE
_2026-09-08.md`, filed before the branch was driven):

  * ONE landing field -- `not_proven[0].note` -- and ONE home, `#not-proven` on `/harness/`. The
    parent defect's two-homes shape is not on this page. That is a result, not a pass.
  * "BESIDE THIS" IS AN ABSENCE CLAIM, and the value_arms rung's verdict vocabulary cannot state
    it. Its `_REFERENTS` admit `above`/`below`/`same`, each asserting the reader WILL find the
    subject somewhere; this sentence asserts they will NOT. Graded as `same` it would have read
    true for the wrong reason -- true because its subject renders nowhere, which is exactly the
    vacuous pass. So the verdict here is `absent`, and it carries a WITNESS: the quantity is shown
    to be renderable in that very region on the OTHER arm of the same conditional, and refused on
    this one. Both arms measured; neither declared.
  * "THE RANGES ABOVE" IS INTRA-FIELD, and region granularity is structurally blind to it. The
    ranges are composed into the SAME string by the same f-string, so every region-level judge can
    ever say is `same`. Judged here by TEXT ORDER inside the field -- offset 400 against 1290 on
    the driven build -- which is what "above" means to a reader inside one block of prose. AND SO
    THERE IS NO READING-ORDER JUDGE IN THIS FILE, which is the one way it differs from the
    value_arms rung it copies. Both of this page's directions resolve inside one region, and a
    `{anchor: position}` map read off `/harness/` would have been a component that could never
    change any verdict -- a control over this rung's own controls, which is the shape CLAUDE.md
    says to delete rather than write.
  * AND THE SHARED VOCABULARY MUST NOT BE WIDENED TO REACH IT. Adding `range|interval` to
    `_HERE_RELATIVE` was tried and MEASURED: it picks up `generate_value_arms_data.py:1693`,
    "whether a larger settled book moves the interval above", where "above" is the direction a
    NUMBER moves and not a place on a page. A site-wide vocabulary has to stay conservative or it
    starts refusing arithmetic; a rung that knows its own page's prose does not. Hence
    `_EXTRA_PHRASES`, page-scoped and argued rather than assumed.

HOW A HOME IS DERIVED, and every step is a measurement:

  1. The branch is DRIVEN through the real `generate()` over the real artefacts, with the reason-mix
     artefact patched to the state that takes it -- a population that cannot size the SVT route.
     Not a hand-written payload: a payload the producer composed.
  2. THE MARKER RIDES THE PRODUCER'S OWN INTERPOLATION. `causes_not_in_the_interval`'s keys are
     joined into the same sentence chunk as the untied literal, so marking that input puts a
     findable token inside the exact string under test without anyone editing the producer or
     replacing a value -- the door still takes the branch it really takes.
  3. HOMES are the regions of the real `/harness/` door that carry the marker when the door is
     driven down its own boot path against that build.
  4. The REFERENT of each direction is derived from the producer's own AST -- the other arm of the
     same `IfExp` for the absence claim, the producer's own composed fragment for the intra-field
     one -- so a rewording reds rather than silently stops matching.

FAIL CLOSED IN FIVE PLACES, each a way this could quietly stop measuring: an untied literal whose
symbol has no recipe is REFUSED not skipped; a driven sentence reaching no field means the recipe
stopped driving the branch; a sentence reaching no region is reported rather than read as clean; a
(symbol, phrase) outside `_REFERENTS` is refused for being unjudgeable; and an `absent` claim whose
subject cannot be shown renderable on any branch is refused as untestable rather than passed.

R15 -- the mutations, each run against the real tree and reverted:
  * make both arms of the conditional emit, so the SVT figure renders in the region the sentence
    says it is not readable beside -> the absence leg reds naming the region; the real one-armed
    build stays green, so the judge is not refusing its whole partition.
  * move the ranges after the pointer inside the field -> the intra-field leg reds; the real order
    stays green.
  * reword the pointer past `_REFERENTS` -> refused AS UNREGISTERED, not as a misdirection, so a
    red never names the wrong repair.
  * drop the recipe -> the census leg reds naming the symbol.
  * make `_homes_of` return nothing -> the witness leg reds, so a blind probe cannot report a
    clean page.
"""
from __future__ import annotations

import ast
import json
import sys
import tempfile
from pathlib import Path

import pytest

from tools import generate_proof_data as gpd

PROJECT = Path(__file__).resolve().parent.parent.parent
SITE = PROJECT / "site"
sys.path.insert(0, str(SITE))

import test_a_here_relative_pointer_has_one_home as published  # noqa: E402

#: REUSED BY IMPORT, never copied -- the vocabulary and the census ARE the rule, and a second copy
#: of either drifts into this rung judging a different set of sentences than the three files it
#: completes. `_untied_literals`/`_owning_symbol`/`_string_fields` were parameterised on the
#: producer for this file rather than duplicated.
from tests.tools.test_the_value_arms_pages_undriven_pointers import (  # noqa: E402
    _owning_symbol,
    _string_fields,
    _untied_literals,
)

_here_relative_phrase = published._here_relative_phrase

PRODUCER = PROJECT / "tools" / "generate_proof_data.py"
DOOR_URL = "/harness/"
FEED_URL = "../data/proof.json"

#: A token no payload can contain. Used as a MAP KEY the producer itself joins into the sentence,
#: so nothing here rewrites a value and no door is moved off its own branch.
_MARK = "Zq{}Zx"

#: PAGE-SCOPED additions to the site-wide here-relative vocabulary, and they stay page-scoped for
#: the measured reason in this module's docstring: widening `_HERE_RELATIVE` to admit "ranges
#: above" also admits "moves the interval above", which is a number going up.
_EXTRA_PHRASES = ("ranges above",)


def _phrases(text: str) -> list[str]:
    """Every direction this sentence claims: the registered one, plus this page's own."""
    found = []
    shared = _here_relative_phrase(text)
    if shared:
        found.append(shared.lower())
    lowered = text.lower()
    found.extend(extra for extra in _EXTRA_PHRASES
                 if extra in lowered and extra not in found)
    return found


# ── driving the branch ───────────────────────────────────────────────────────────────────────

def _mix() -> dict:
    """The real reason-mix artefact, which both recipes below start from.

    STARTED FROM THE REAL ONE and not from a hand-built stub: `_why_households_leave` reads the
    interval, the sweep, the declared point and the renewal count as well, and a stub that
    satisfied only the branch condition would compose a sentence the page cannot publish.
    """
    return json.loads(gpd.REASON_MIX_PATH.read_text(encoding="utf-8"))


def _cannot_size_the_route(marker: str) -> dict:
    """THE UNDRIVEN BRANCH: a mix whose population cannot size the SVT route.

    `blind_size`'s `else` arm is taken when the artefact declares no reach, which is the state a
    re-sweep that lost its population block would leave. `causes_not_in_the_interval` carries the
    marker because the producer joins its KEYS into the same sentence -- that is what makes this a
    drive rather than a substitution.
    """
    return dict(_mix(), population={}, causes_not_in_the_interval={marker: None})


def _can_size_the_route(marker: str) -> dict:
    """THE OTHER ARM of the same conditional, which is the witness the absence claim needs."""
    return dict(_mix(), causes_not_in_the_interval={marker: None})


#: HOW EACH SYMBOL'S UNDRIVEN BRANCH IS REACHED, and how its counterpart is. The census leg below
#: REFUSES a literal whose symbol is not here, so this table cannot fall behind the producer
#: without something going red.
_RECIPES = {"_why_households_leave": _cannot_size_the_route}
_COUNTERPARTS = {"_why_households_leave": _can_size_the_route}


def _build(mix: dict) -> dict:
    """`generate()` over the real artefacts with the reason mix replaced, written to a temp path.

    OUT_PATH IS REDIRECTED, and that is not tidiness. `generate()` writes the live feed, so a rung
    that ran it in place would publish a marked payload to `site/data/proof.json` and every other
    control on the site would then be reading this test's scratch.
    """
    scratch = Path(tempfile.mkdtemp(prefix="proof-pointer-"))
    mix_path, out_path = scratch / "mix.json", scratch / "proof.json"
    mix_path.write_text(json.dumps(mix), encoding="utf-8")
    saved = (gpd.REASON_MIX_PATH, gpd.OUT_PATH)
    gpd.REASON_MIX_PATH, gpd.OUT_PATH = mix_path, out_path
    try:
        gpd.generate()
    finally:
        gpd.REASON_MIX_PATH, gpd.OUT_PATH = saved
    return json.loads(out_path.read_text(encoding="utf-8"))


def _homes_of(marker: str, built: dict) -> set[str]:
    """The door regions that carry `marker` when `/harness/` is driven against this build."""
    regions, _, meta = published._render(DOOR_URL, overrides={FEED_URL: built})
    assert not meta.get("scriptError"), (
        "the door raised {!r} on this build, so every region below is a render that did not "
        "finish and zero homes would be the flattering answer".format(meta.get("scriptError")))
    return {element for element, text in regions.items() if marker in text}


# ── what a pointer points AT, taken from the producer's own source ───────────────────────────

def _fragments(node) -> list[str]:
    """The parts of an f-string or plain literal that survive interpolation."""
    if isinstance(node, ast.JoinedStr):
        return [value.value.strip() for value in node.values
                if isinstance(value, ast.Constant) and isinstance(value.value, str)
                and value.value.strip()]
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value.strip()]
    return []


def _the_other_arm(line: int) -> str:
    """The longest stable fragment of the OTHER arm of the conditional this literal is one arm of.

    STRUCTURAL, NOT A LINE NUMBER AND NOT HAND-TYPED PROSE. An absence claim needs a subject, and
    this sentence's subject is precisely the figure the sibling arm would have published. Finding
    it through the `IfExp` means a rewrite of either arm reds here instead of quietly leaving the
    absence claim pointing at a fragment nothing composes any more.
    """
    tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.IfExp):
            continue
        if not (node.lineno <= line <= (node.end_lineno or node.lineno)):
            continue
        for arm, other in ((node.body, node.orelse), (node.orelse, node.body)):
            if not (arm.lineno <= line <= (arm.end_lineno or arm.lineno)):
                continue
            fragments = sorted(_fragments(other), key=len, reverse=True)
            if fragments:
                return fragments[0]
    raise AssertionError(
        "{}:{} is no longer one arm of a conditional, so the quantity this sentence says is NOT "
        "readable has no derivable subject and its claim cannot be checked".format(
            PRODUCER.name, line))


def _composed_fragment(selector: str) -> str:
    """The producer's own composed fragment carrying `selector`, longest first.

    The SELECTOR is this rung's hint about which part of the page a pointer names; the FRAGMENT it
    picks out is the producer's, so rewording the prose stops the match and reds rather than
    quietly comparing offsets of something that is no longer there.
    """
    tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    found = [fragment for node in ast.walk(tree) if isinstance(node, ast.JoinedStr)
             for fragment in _fragments(node) if selector in fragment]
    assert found, (
        "no composed fragment in {} carries {!r} any more, so the thing this pointer names cannot "
        "be located in what the producer writes".format(PRODUCER.name, selector))
    return sorted(found, key=len, reverse=True)[0]


#: WHAT EACH REGISTERED DIRECTION CLAIMS, keyed by (symbol, phrase) for the reason the value_arms
#: rung learned: two sentences can share words and point at different things.
#:
#:   `absent`  -- "the reader will NOT find this beside them". Judged by the subject rendering in
#:                no region the sentence renders in, and only after the subject has been shown
#:                renderable there on the counterpart branch. Without that witness the verdict is
#:                satisfied by the subject not existing, which is a vacuous pass wearing a tick.
#:   `earlier` -- "what I name is above me". The subject is in the SAME feed field, so no
#:                region-level judge can express this; it is judged by text order inside the field.
_REFERENTS = {
    ("_why_households_leave", "beside this"): ("absent", None),
    ("_why_households_leave", "ranges above"): ("earlier", "bill shock"),
}


def _absence_defects(phrase: str, homes: set, subject_homes: set) -> list[str]:
    """A claim that something is NOT readable here is false where it renders here."""
    overlap = sorted(homes & subject_homes)
    if overlap:
        return ["{!r} tells a reader that what it names is not readable where they stand, and it "
                "renders in {}: the sentence is false in its own home".format(phrase, overlap)]
    return []


def _earlier_defects(phrase: str, at: int, subject_at: int) -> list[str]:
    """A claim that something is above this one, judged by order inside the field they share."""
    if at < 0:
        return ["{!r} was not found in the field it lands in, so the order below would be read "
                "off an offset that means nothing".format(phrase)]
    if subject_at < 0:
        return ["{!r} names something the producer does not compose into the field the sentence "
                "lands in, so a reader looking up finds nothing".format(phrase)]
    if subject_at >= at:
        return ["{!r} claims what it names is above it, and it is composed at character {} "
                "against the pointer's {}: the pointer misdirects".format(phrase, subject_at, at)]
    return []


# ── the driven census, built once ────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def driven() -> list[dict]:
    """Each untied literal of this producer, its branch driven, with its fields, homes and twin."""
    rows: list[dict] = []
    by_symbol: dict[str, list] = {}
    for literal in _untied_literals(PRODUCER):
        by_symbol.setdefault(literal["symbol"], []).append(literal)

    for index, (symbol, literals) in enumerate(sorted(by_symbol.items())):
        if symbol not in _RECIPES:
            rows.append({"symbol": symbol, "literals": literals, "recipe": False})
            continue
        marker = _MARK.format(index)
        built = _build(_RECIPES[symbol](marker))
        fields = [(where, text) for where, text in _string_fields(built) if marker in text]
        twin = _build(_COUNTERPARTS[symbol](marker))
        twin_fields = [text for where, text in _string_fields(twin) if marker in text]
        rows.append({
            "symbol": symbol, "literals": literals, "recipe": True, "marker": marker,
            "fields": [where for where, _ in fields],
            "text": fields[0][1] if fields else "",
            "homes": _homes_of(marker, built) if fields else set(),
            "twin_text": twin_fields[0] if twin_fields else "",
            "twin_homes": _homes_of(marker, twin) if twin_fields else set(),
            "built": built,
        })
    return rows


def test_this_producer_still_writes_an_untied_here_relative_pointer(driven):
    """The census, not a memory of one -- and a witness that this file still has a subject.

    If `generate_proof_data.py` stops writing an untied here-relative sentence, this file is a
    green control checking nothing, and the honest move is to delete it rather than keep it. That
    is a different outcome from every leg below passing, so it is asserted rather than assumed.
    """
    assert driven, (
        "no untied here-relative literal remains in {}. Either it was reworded -- in which case "
        "delete this file rather than keep a control with no subject -- or the census has gone "
        "blind against how the producer writes now".format(PRODUCER.name))


def test_every_untied_here_relative_literal_has_a_recipe_that_drives_its_branch(driven):
    """A sentence this page can publish and nothing can drive is a sentence nothing can judge.

    THE FAIL-OPEN THIS CLOSES. The three controls beside this one all record an untied literal and
    decline to refuse it; if this rung SKIPPED one it could not drive, the recording would move
    here and nothing would ever refuse it either.

    Fires on: a new here-relative sentence on a branch no recipe reaches; a producer function
    renamed out from under `_RECIPES`; a recipe that stops driving its branch, so the sentence
    reaches no field at all.
    """
    missing = [row["symbol"] for row in driven if not row["recipe"]]
    assert not missing, (
        "these symbols own an untied here-relative sentence and no recipe drives their branch, so "
        "the sentence is publishable and unjudged: {}. Add a row to `_RECIPES`".format(
            sorted(missing)))
    unwitnessed = [row["symbol"] for row in driven if row["recipe"] and not row["fields"]]
    assert not unwitnessed, (
        "these branches were driven and their sentence reached NO field of the build, so the "
        "recipe no longer takes the branch it names and every judgement below skips them: "
        "{}".format(sorted(unwitnessed)))


def test_a_sentence_no_door_renders_is_reported_rather_than_read_as_clean(driven):
    """Zero homes is "we cannot tell", and it belongs on the surface rather than in a pass.

    A sentence that reaches a field and no region raises no misdirection, which is
    indistinguishable from a correct pointer under the legs below. Two branches on the value_arms
    page were in exactly that state on 2026-09-08.

    Fires on: a here-relative pointer written into a field no door reads; the `/harness/` door
    dropping the region that renders `not_proven`.
    """
    unrendered = ["{}:{}".format(row["symbol"], literal["line"])
                  for row in driven if row.get("fields") and not row["homes"]
                  for literal in row["literals"]]
    assert not unrendered, (
        "these branches write a here-relative pointer into a field NO door renders, so their "
        "direction is taken from a place no reader stands and nothing can check it: {}. Either a "
        "door should render the field or the sentence should name a landmark".format(
            sorted(unrendered)))


def test_the_absence_this_sentence_claims_is_true_where_it_renders(driven):
    """"Not readable beside this" is a claim, and it is false wherever the thing IS readable.

    THE VERDICT THE VALUE_ARMS RUNG COULD NOT STATE. Its `above`/`below`/`same` each assert the
    reader will find the subject somewhere; this sentence asserts they will not, and grading it
    `same` would have called it true because its subject renders nowhere -- true for the wrong
    reason, and it would go on being true after the two arms started co-emitting.

    THE WITNESS IS WHAT MAKES IT NON-VACUOUS. The subject is the figure the OTHER arm of the same
    conditional publishes, and it is measured into the very region the sentence lands in on that
    arm before its absence on this one is called a pass. Both arms built, both rendered.

    Fires on: both arms of the conditional emitting, so the page says a figure is not readable
    beside a figure that is; the counterpart arm ceasing to render, which makes the claim
    untestable rather than true; either arm being reworded past the fragment the AST derives.
    """
    defects = []
    for row in driven:
        if not row.get("recipe") or not row.get("fields"):
            continue
        for literal in row["literals"]:
            for phrase in _phrases(literal["literal"]):
                kind = _REFERENTS.get((row["symbol"], phrase), (None, None))[0]
                if kind != "absent":
                    continue
                subject = _the_other_arm(literal["line"])
                assert subject in row["twin_text"] and row["twin_homes"], (
                    "the figure {}:{} says is not readable is not composed into a rendered region "
                    "on the counterpart branch either, so its absence here is untestable and "
                    "reading it as true would be a vacuous pass".format(
                        row["symbol"], literal["line"]))
                here = row["twin_homes"] if subject in row["text"] else set()
                defects.extend(
                    "{}:{} {}".format(row["symbol"], literal["line"], defect)
                    for defect in _absence_defects(phrase, row["homes"], here))
    assert not defects, (
        "the page tells a reader something is not readable beside them and it is:\n  "
        + "\n  ".join(defects))


def test_a_direction_inside_one_field_is_judged_by_the_order_of_that_field(driven):
    """The direction region granularity is structurally blind to, judged where it lives.

    THE MEASUREMENT THAT FORCED THIS LEG (2026-09-08). "the ranges above" names the bill-shock /
    price-position / service ranges, and the producer composes them into the SAME string by the
    same f-string. Every landed control here judges at REGION granularity, so the best any of them
    can say is `same` -- the claim is not false, it is unreachable. Inside one block of prose
    "above" means "earlier in this block", which is an order the build itself carries.

    KEYED TO THE PRODUCER'S OWN TEXT. The fragment compared is taken from the producer's AST and
    located in the field the build composed, so reordering the sentence reds this and rewording it
    reds this, without anyone editing an offset.

    Fires on: the ranges moving after the pointer in the composed note; the pointer moving above
    the ranges; either being reworded so the derived fragment stops matching.
    """
    defects = []
    for row in driven:
        if not row.get("recipe") or not row.get("text"):
            continue
        for literal in row["literals"]:
            for phrase in _phrases(literal["literal"]):
                kind, selector = _REFERENTS.get((row["symbol"], phrase), (None, None))
                if kind != "earlier":
                    continue
                subject = _composed_fragment(selector)
                assert subject in row["text"], (
                    "{!r} is composed by {} but is not in the field {}:{} lands in, so the two "
                    "are not in one block and this leg is judging across fields".format(
                        selector, PRODUCER.name, row["symbol"], literal["line"]))
                defects.extend(
                    "{}:{} {}".format(row["symbol"], literal["line"], defect)
                    for defect in _earlier_defects(phrase, row["text"].lower().find(phrase),
                                                   row["text"].find(subject)))
    assert not defects, (
        "the page sends a reader the wrong way inside one block of its own prose:\n  "
        + "\n  ".join(defects))


def test_every_direction_this_sentence_claims_is_one_this_rung_judges(driven):
    """A direction nobody registered is unjudged, and unjudged must be a red rather than silence.

    THE FAIL-OPEN THIS CLOSES, and it is the one this sentence itself walked through: "the ranges
    above" was outside the site-wide vocabulary, so three landed controls saw one direction in a
    sentence that claims two. A phrase this rung cannot check is refused, and the refusal says
    which phrase, so a rewording cannot buy silence.
    """
    unjudged = []
    for row in driven:
        if not row.get("recipe"):
            continue
        for literal in row["literals"]:
            phrases = _phrases(literal["literal"])
            assert phrases, (
                "{}:{} entered the census as a here-relative literal and this rung reads no "
                "direction in it, so the two vocabularies disagree".format(
                    row["symbol"], literal["line"]))
            unjudged.extend(
                "{}:{} {!r}".format(row["symbol"], literal["line"], phrase)
                for phrase in phrases if (row["symbol"], phrase) not in _REFERENTS)
    assert not unjudged, (
        "these directions are claimed on a branch this page can take and nothing checks them: "
        "{}. Register each in `_REFERENTS` with what it points at".format(sorted(unjudged)))


def test_MUTATION_both_verdicts_are_reachable_and_the_honest_page_is_not_refused(driven):
    """The legs above must be failable by the page being wrong, not only by it being right.

    A GUARD THAT REFUSES ITS WHOLE PARTITION PASSES EVERY TEST OF ITS REFUSALS, which is this
    repository's most-repeated control failure, so each poison is run beside its honest twin -- and
    the honest twin is the state the page is really in today.

    AND THE PROBE MUST BE SHOWN NOT TO BE BLIND. A rung whose homes are all empty raises no defect
    at all: every judgement is vacuous and every leg above passes on the silence.
    """
    here, elsewhere = {"not-proven"}, {"corrections"}

    # A. THE ABSENCE CLAIM. False exactly where its subject shares a region with it.
    assert _absence_defects("beside this", here, set()) == [], (
        "the real one-armed build is reported as a misdirection, so this judge refuses the page "
        "as it stands and every red it raises is uninformative")
    assert _absence_defects("beside this", here, elsewhere) == [], (
        "a subject rendering in a DIFFERENT region is read as refuting 'not readable beside "
        "this', so the judge is keyed to the subject existing rather than to where it is")
    assert any("false in its own home" in defect
               for defect in _absence_defects("beside this", here, here)), (
        "both arms co-emitting -- the page saying a figure is not readable beside a figure that "
        "renders in the same region -- is not caught, which is the whole shape of this leg")

    # B. THE INTRA-FIELD DIRECTION. Both orders driven, because a judge that reds on the word
    # rather than on the order would refuse the sentence wherever it is true.
    assert _earlier_defects("ranges above", 1290, 400) == [], (
        "the real composition order -- the ranges at 400, the pointer at 1290 -- is reported as a "
        "misdirection, so this judge rejects the phrase rather than reading its claim")
    assert any("misdirects" in defect for defect in _earlier_defects("ranges above", 400, 1290)), (
        "a pointer claiming what it names is above it, composed BELOW it, reads true -- so the "
        "direction half of this leg is not wired at all")
    assert _earlier_defects("ranges above", 400, -1), (
        "a pointer whose subject is composed nowhere in its own field reads true, so the leg "
        "above passes on having seen nothing")

    # C. AN UNREGISTERED DIRECTION FAILS CLOSED, and the two tables are keyed the same way.
    assert ("_why_households_leave", "over that way somewhere") not in _REFERENTS
    assert _phrases("stated over that way somewhere, past the end of it") == [], (
        "an unregistered wording is read as a direction this rung knows, so the refusal above "
        "would name the wrong repair")

    # D. THE WITNESS. Everything above is arithmetic over sets and offsets; this is the leg that
    # says they came from a real render of a real build the producer composed.
    assert any(row.get("homes") for row in driven), (
        "not one driven branch reached a region on the real door, so every judgement in this file "
        "is vacuous -- either the probe has gone blind or no recipe drives its branch")
    assert any(row.get("twin_homes") for row in driven), (
        "the counterpart branch reached no region either, so the absence leg's witness is not a "
        "witness and its pass says nothing")
