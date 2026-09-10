"""The value_arms page's UNDRIVEN pointers, judged by RUNNING the branches that write them.

WHAT THIS EXISTS FOR, and it is a gap two landed controls both name on their own surfaces.
`site/test_a_here_relative_pointer_has_one_home.py` derives a sentence's homes from the PUBLISHED
feed, so a producer branch today's data does not drive renders nowhere and is judged nowhere.
`site/test_a_producers_here_relative_pointer_has_one_home.py` closes half of that from the source
side -- but its rule 3 can only refuse an UNTIED literal when the producer's feed already has some
multi-home field, and `value_arms.json` has none. Thirteen literals were therefore RECORDED AND NOT
JUDGED (measured 2026-09-08): twelve here and one in `generate_proof_data.py`. Its docstring says
so and names the only instrument that closes them -- "a per-page rung that RUNS the producer's
branches" -- which is this file, for the twelve.

THE PARENT DEFECT IS WHY THE INSTRUMENT HAS TO BE THE PRODUCER. `_the_level_legs_family` wrote "the
re-draw band table HIGHER UP THIS SECTION" into `composition.why_not_readable`, a field with TWO
homes on opposite sides of the table it pointed at, so one of two readers was sent the wrong way.
With the level leg sign-stable that field is ABSENT FROM `value_arms.json` ENTIRELY -- not among the
3,712 payload fields the site publishes. No amount of probing the published feed reaches a field
that is not there. Only the producer can create it.

HOW A SENTENCE'S HOMES ARE DERIVED HERE, and every step is a measurement rather than a declaration:

  1. The branch is DRIVEN -- the recipe below patches the one symbol that owns the literal, with
     the branch's own return SHAPE preserved, and `build()` is then run over the SIX REAL
     artefacts `generate()` reads. Not a hand-written payload: a payload the producer composed.
  2. The sentence's LANDING FIELDS are read out of that build by marker, so "which field does this
     branch write into" is answered by the build and never by reading the source.
  3. Its HOMES are the regions of the real `/capabilities/` door that carry the marker when the
     door is driven down its own boot path against that build. A door that stops rendering the
     field loses the home here, without anyone editing a list.
  4. Its REFERENT'S homes are derived the SAME way -- by marking the field the sentence points at
     and re-rendering. So the direction is judged region-against-region, both sides measured, and
     moving either one is what makes this red.

WHAT THE MEASUREMENT FOUND, 2026-09-08, running all twelve for the first time:

  * TEN of the twelve reach EXACTLY ONE region, so the parent defect's shape is not present here.
    That is the answer the published sweep could not get, and it is a result, not a pass.
  * TWO -- both branches of `_decomposition_is_the_same_contrast` -- land in
    `floor_decomposition.different_contrast_caveat`, which NO deployed door renders. They said
    "the figure above" from a place no reader stands. Repaired to name the headline figure, which
    takes them out of the here-relative vocabulary altogether; they are consequently no longer in
    this rung's census, and that is the fix rather than a hole in it.
  * ONE was FALSE. `_departures`' unavailable branch said the accounts the arm drove out "ARE
    named above" -- and `priced_accounts_the_arm_itself_drove_out` renders in `#arms-decisions`,
    the SAME region the sentence lands in, with no region above it naming an account at all.
    Repaired to "beside this", which is true and STAYS in this rung's vocabulary so the claim goes
    on being re-asked.

FAIL CLOSED IN THREE PLACES, because each is a way this could quietly stop measuring:
  * an untied literal whose owning symbol has no recipe is REFUSED, not skipped -- so a new
    here-relative sentence in a new branch cannot arrive unjudged.
  * a driven sentence that reaches no FIELD means the recipe no longer drives the branch, and the
    row is unwitnessed rather than clean.
  * a phrase outside the registered referent table is refused for being unregistered, and the
    refusal says which phrase, so silence is never a pass.

R15 -- the mutations, each run against the real tree and reverted:
  * restore "ARE named above" to `_departures` -> `test_every_undriven_pointer_is_true_from_the_
    region_it_lands_in` reds naming the home, the referent's home and both directions.
  * plant "the figures below" into `_polarity_check`'s reason (home `#arms-decisions`, referent
    `#arms-decisions`) -> reds as a direction that does not hold; the honest "beside this" wording
    in the same place stays green, so the judge is not refusing its whole partition.
  * make `_homes_of` return the empty set -> the witness leg reds, so a probe that goes blind
    cannot report a clean page.
  * drop a recipe -> the census leg reds naming the symbol it can no longer drive.
  * give `_departure_statement` a recipe that does not drive its branch -> the fidelity leg reds
    before any direction is judged.
"""
from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

import pytest

from tools import generate_value_arms_data as gva

PROJECT = Path(__file__).resolve().parent.parent.parent
SITE = PROJECT / "site"
sys.path.insert(0, str(SITE))

import test_a_here_relative_pointer_has_one_home as published  # noqa: E402
import test_a_producers_here_relative_pointer_has_one_home as producers  # noqa: E402

#: REUSED BY IMPORT, never copied. The vocabulary IS the rule, and a second copy of it would drift
#: into this rung quietly judging a different set of sentences than the two sweeps beside it.
_here_relative_phrase = published._here_relative_phrase

PRODUCER = PROJECT / "tools" / "generate_value_arms_data.py"
DOOR_URL = "/capabilities/"
FEED_URL = "../data/value_arms.json"

#: A marker no payload can contain, prefixed so a door that branches on a field's content still
#: takes the branch it really takes -- replacing a value outright would measure a page nobody
#: publishes. Same shape, same reason, as the producer sweep's probe.
_MARK = "Zq{}Zx"


def _real_inputs() -> list:
    """Every artefact `generate()` reads, in its order.

    ALL OF THEM, and the count is load-bearing. Built from three, the decomposition and both
    current-world artefacts are absent, `floor_decomposition` never composes and
    `_current_world_bound`'s refusal reaches no field -- so two recipes would report "this branch
    writes nowhere" when what was missing was an input, and the flattering reading is the one that
    would have been recorded.

    KEYED TO `build`'s ARITY RATHER THAN TO A COUNT TYPED HERE. This list was six paths with
    `RUN_OUTPUT_PATH` third until the published-supplier repair stopped reading that artefact at
    all; the name then vanished from the producer and this fixture raised `AttributeError` at
    SETUP, which reports as four tests erroring rather than as one stale list -- and a whole file
    erroring is how a red gets attributed to whichever lane next touches it. The check below makes
    the next such move a refusal that names itself.
    """
    paths = (gva.THREE_ARM_PATH, gva.NOISE_FLOOR_PATH, gva.DECOMPOSITION_PATH,
             gva.CURRENT_WORLD_THREE_ARM_PATH, gva.CURRENT_WORLD_NOISE_FLOOR_PATH,
             gva.DEPARTURE_TERM_RERUN_PATH)
    wanted = gva.build.__code__.co_argcount
    assert len(paths) == wanted, (
        "`build` reads {} artefacts and this fixture supplies {}, so every recipe below would be "
        "driven over a payload the producer never builds".format(wanted, len(paths)))
    return [gva._read(path) for path in paths]


def _string_fields(payload) -> list[tuple[str, str]]:
    """`[(path, text)]` for every string a built payload carries, at any depth."""
    out: list[tuple[str, str]] = []

    def walk(node, where: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, "{}.{}".format(where, key))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, "{}[{}]".format(where, index))
        elif isinstance(node, str):
            out.append((where, node))

    walk(payload, "")
    return out


def _homes_of(marker: str, built: dict) -> set[str]:
    """The door regions that carry `marker` when the door is driven against this build."""
    regions, _, meta = published._render(DOOR_URL, overrides={FEED_URL: built})
    assert not meta.get("scriptError"), (
        "the door raised {!r} on this build, so every region below is a render that did not "
        "finish and zero homes would be the flattering answer".format(meta.get("scriptError")))
    return {element for element, text in regions.items() if marker in text}


# ── driving the branches ─────────────────────────────────────────────────────────────────────

def _returns_string(sentence, _real):
    return lambda *a, **k: sentence


def _departures_unavailable(sentence, _real):
    # THE BRANCH'S OWN SHAPE, not a merge onto today's result. `available: True` and this reason
    # are different states and the door renders only one of them: merging the reason onto the
    # available block would have written a field nothing reads and reported zero homes.
    return lambda *a, **k: {"available": False, "reason": sentence}


def _no_bound(sentence, _real):
    return lambda *a, **k: {"bound_available": False, "why_no_bound": sentence}


def _polarity_reason(sentence, real):
    # MERGED HERE, and the difference from the two above is the point: `reason` is rendered on
    # every branch of `_polarity_check`, so the honest drive keeps the computed dict and replaces
    # only the sentence. Substituting a bare dict would have taken the page off its own branch.
    return lambda *a, **k: dict(real(*a, **k), reason=sentence)


def _how_to_read_this(sentence, real):
    """MERGED, and for `_polarity_reason`'s reason rather than a new one.

    `_current_world_contrast` returns the whole current-world block; the here-relative sentence is
    one key inside it. Substituting a bare string would take `current_world` off the shape every
    leg below reads -- the bound, the selection leg, the re-draw family -- and the drive would then
    be measuring a page nobody publishes.
    """
    return lambda *a, **k: dict(real(*a, **k), how_to_read_this=sentence)


def _departure_unavailable_constant(sentence, _real):
    """`_DEPARTURE_UNAVAILABLE` is a constant, and patching it does NOT drive its branch.

    The branch is `_world_departure_level`'s `except`, so the drive has to make the measurement
    fail the way a missing commons would. Patching the constant alone left `available: True` and
    the sentence in no field at all -- which read as "this branch writes nowhere" and was wrong.
    """
    return sentence


#: HOW EACH SYMBOL'S UNDRIVEN BRANCH IS REACHED. One row per symbol that owns an untied
#: here-relative literal; the census below REFUSES a literal whose symbol is not here, so this
#: table cannot fall behind the producer without something going red.
_RECIPES = {
    "_departure_statement": _returns_string,
    "_decomposition_is_the_same_contrast": _returns_string,
    "_world_clause": _returns_string,
    "_headline_reading": _returns_string,
    "_departures": _departures_unavailable,
    "_current_world_bound": _no_bound,
    "_polarity_check": _polarity_reason,
    "_DEPARTURE_UNAVAILABLE": _departure_unavailable_constant,
    # THE TWO PANEL SENTENCES. Both return a bare string into one published field, so the generic
    # recipe drives them. They arrived with `_what_differs_between_two_runs` on 2026-09-08 and this
    # rung had been red at HEAD for them since -- picked up here because the 09-08b promotion makes
    # `_against_the_superseded_panel`'s `the_same_run` branch the LIVE one, so its here-relative
    # prose is now what a reader actually meets rather than a branch nobody could reach.
    "_against_the_superseded_panel": _returns_string,
    "_against_the_panels_figure": _returns_string,
    # THE BUCKET TABLE'S READING became a symbol of its own on 2026-09-09 when its direction stopped
    # being written down; its fewer-than-two-bands and flat-ends branches render nowhere today, so
    # the here-relative prose in them is exactly what this rung judges.
    "_bucket_reading": _returns_string,
    # THE LAST TWO UNDRIVEN SYMBOLS, red at HEAD since before either lane in this cluster existed
    # and named as the landable part of the wedge in
    # `docs/staging/SEAT_RESULT_THE_PUBLISHED_SUPPLIER_CHECK_NOW_READS_ONLY_COMMITTED_BYTES_AND_THE_ITEMS_OWN_PAIRING_WOULD_HAVE_REFUSED_ON_EVERY_PUBLISH_2026-09-10.md`.
    # `_publisher_bound_statement` returns a bare string into `bounding_statement`, so the generic
    # recipe drives it; `_current_world_contrast` returns a block and takes the merge above.
    # `_publisher_bound_statement`'s row stays even though its untied sentence was repaired out of
    # the census in the same landing: its lead still says "THE BAND ABOVE IS REFUTED", which is
    # here-relative and TIED today, and the day a re-capture unties it this row is what stops that
    # arriving as a fresh red for whichever lane happens to be in the file.
    "_publisher_bound_statement": _returns_string,
    "_current_world_contrast": _how_to_read_this,
}

#: The symbols whose branch needs something OUTSIDE the producer made to fail. Keyed to the module
#: and attribute so a rename reds here rather than silently stopping the drive.
_ALSO_BREAK = {
    "_DEPARTURE_UNAVAILABLE": ("tools.measure_departure_level", "published_bands"),
}

#: The symbols an UPSTREAM GATE closes off on today's artefacts, and the producer field that opens
#: it. `{symbol: (upstream_symbol, forced_fields)}`.
#:
#: WHY THIS IS NOT AN EXEMPTION, which is the objection it has to survive. `_current_world_clause`
#: returns the empty string outright when `current_world.is_the_later_run` is False -- the state
#: the page entered when the 09-08b re-take was promoted onto the canonical name -- and it composes
#: `_against_the_panels_figure`'s sentence inside an argument it then discards. So the sentence is
#: unpublishable TODAY and publishable the next time a current-world run is the later of the two,
#: which is a fact about the artefacts and not about the recipe. Skipping the symbol would let a
#: here-relative pointer sit unjudged until exactly the publish that puts it back on the page;
#: forcing the gate open drives the real branch of the real function and judges its direction now.
#:
#: FORCED ON THE UPSTREAM PRODUCER, never on the artefact, so the drive still runs the code the
#: publish runs. A fixture that edited `is_the_later_run` in the input would also move the
#: superseded figure the sentence compares against, and the comparison is the thing being judged.
_ALSO_ADMIT = {
    "_against_the_panels_figure": ("_current_world_contrast", {"is_the_later_run": True}),
}


def _drive(symbol: str, sentence: str) -> dict:
    """`build()` over the real artefacts with `symbol`'s undriven branch taken."""
    recipe = _RECIPES[symbol]
    real = getattr(gva, symbol)
    broken = _ALSO_BREAK.get(symbol)
    admit = _ALSO_ADMIT.get(symbol)
    saved_admit = None
    if admit:
        upstream, forced = admit
        saved_admit = getattr(gva, upstream)

        def _open(_real=saved_admit, _forced=forced):
            return lambda *a, **k: dict(_real(*a, **k), **_forced)

        setattr(gva, upstream, _open())
    saved = None
    if broken:
        module = __import__(broken[0], fromlist=["_"])
        saved = getattr(module, broken[1])

        def refuse(*a, **k):
            raise ValueError("driven by the undriven-pointer rung")

        setattr(module, broken[1], refuse)
    setattr(gva, symbol, sentence if isinstance(real, str) else recipe(sentence, real))
    try:
        return gva.build(*_real_inputs())
    finally:
        setattr(gva, symbol, real)
        if broken:
            setattr(__import__(broken[0], fromlist=["_"]), broken[1], saved)
        if admit:
            setattr(gva, admit[0], saved_admit)


# ── the census ───────────────────────────────────────────────────────────────────────────────

def _owning_symbol(source: Path, line: int) -> str | None:
    """The function or module constant a source line belongs to.

    TAKES THE PRODUCER RATHER THAN CLOSING OVER IT, because the proof page's rung
    (`test_the_proof_pages_undriven_pointers.py`) imports this and the one below rather than
    keeping a second copy: two AST censuses of "which untied literals does this producer own"
    would drift, and the drift shows up as one page judging a set the other does not.
    """
    tree = ast.parse(source.read_text(encoding="utf-8"))
    spans = [(node.lineno, node.end_lineno, node.name)
             for node in ast.walk(tree)
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    spans += [(node.lineno, node.end_lineno, node.targets[0].id) for node in tree.body
              if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)]
    owning = sorted(span for span in spans if span[0] <= line <= span[1])
    return owning[-1][2] if owning else None


def _untied_literals(producer: Path) -> list[dict]:
    """Every here-relative literal in `producer` that lands in NO published field today.

    THE UNTIED SET IS DERIVED, not listed. `_producer_literals` is the producer sweep's own AST
    census -- docstrings excluded, because a producer's prose ABOUT this defect is not something
    the page can publish -- and a literal is untied when none of its interpolation-stable
    fragments appears in any string the site currently publishes. Pinning the thirteen as a list
    would key this rung to today's answer: a literal that gains a home would stay in the census
    and one that loses its branch would never enter it.
    """
    published_text = []
    for feed in sorted((SITE / "data").glob("*.json")):
        try:
            payload = json.loads(feed.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        slots: list = []
        producers._slots(payload, "", slots)
        published_text.extend(producers._norm(container[key]) for container, key, _ in slots)

    untied = []
    for literal in producers._producer_literals():
        if literal["producer"] != producer.name:
            continue
        if any(fragment in text for text in published_text
               for fragment in literal["fragments"]):
            continue
        untied.append(dict(literal, symbol=_owning_symbol(producer, literal["line"])))
    return untied


# ── what a pointer claims, and what it points AT ─────────────────────────────────────────────

#: WHAT EACH REGISTERED PHRASE CLAIMS, and the FEED FIELD whose homes are the thing it points at.
#: The referent is a field rather than an anchor id on purpose: an anchor would be this rung's
#: opinion about where the page puts a figure, and a field is the page's own. Both sides are
#: probed the same way, so moving EITHER the sentence or the thing it names is what reds this.
#:
#: `same` is a real claim and not an absence of one. "beside this" says the reader will find the
#: subject where they are standing, and it is false the moment the two land in different regions
#: -- which is precisely the state `_departures` was in when it said "above".
#:
#: KEYED BY (SYMBOL, PHRASE) AND NOT BY PHRASE ALONE, which was the first draft and was wrong in
#: the way this repository names most often: two sentences share the words "beside this" and point
#: at DIFFERENT things -- `_departures` at the accounts the arm drove out, `_polarity_check` at
#: the reading of the AUC. Both happen to render in the same region today, so a phrase-keyed table
#: gives the right answer for the wrong reason and stops giving it the day either one moves.
_REFERENTS = {
    ("_DEPARTURE_UNAVAILABLE", "figure below"): (".realised.clock_means", "below"),
    ("_departure_statement", "figure below"): (".realised.clock_means", "below"),
    ("_departure_statement", "figures below"): (".realised.clock_means", "below"),
    ("_current_world_bound", "figure below"): (".realised.clock_means", "below"),
    ("_world_clause", "figures below"): (".realised.clock_means", "below"),
    # THE DIFFERENT-WORLDS BRANCH, which stopped being driven on 2026-09-09. Promoting the 09-08b
    # pair put the headline and its bound in ONE world, so `world_caveat` is `None` and this
    # sentence became publishable-but-unrendered -- which is exactly the state this rung exists to
    # judge, and it arrived by the page getting BETTER rather than worse.
    ("_world_clause", "figure below"): (".realised.clock_means", "below"),
    ("_headline_reading", "panels below"): (".realised.clock_means", "below"),
    # BOTH PANEL SENTENCES NAME THE SAME THING `_headline_reading` DOES -- the realised split
    # published under the current-world block -- so they take the same referent rather than a
    # second one written down here. Registered 2026-09-09 with their `_RECIPES` rows.
    # `_against_the_superseded_panel` renders in #arms-composition and #arms-realised is ABOVE it,
    # so its four sentences said "the panel below" about a panel a reader has already passed. Found
    # by registering the referent, not by reading the prose: the word was corrected to "above" in
    # the producer and this row is what holds it there.
    ("_against_the_superseded_panel", "panel above"): (".realised.clock_means", "above"),
    ("_against_the_panels_figure", "panel below"): (".realised.clock_means", "below"),
    # THE INSTRUCTION FOR READING TWO PANELS. "the figures above" names the canonical run, whose
    # figures the page states as its `headline` -- so the referent is that field and not the
    # realised split the two rows above point at. Registered 2026-09-10 with the door change that
    # gave the sentence a home at all: it had reached a field NO door rendered since the
    # current-world block was written, so its direction was unjudged rather than wrong.
    ("_current_world_contrast", "figures above"): (".headline", "above"),
    ("_departures", "beside this"): (
        ".decisions.auc_attribution.priced_accounts_the_arm_itself_drove_out", "same"),
    ("_polarity_check", "beside this"): (".decisions.auc_attribution.reading", "same"),
}


def _referent_homes(field: str, built: dict) -> set[str]:
    """The regions the field a pointer names renders in, probed the same way the pointer is."""
    marked = copy.deepcopy(built)
    node = marked
    parts = field.lstrip(".").split(".")
    for part in parts[:-1]:
        node = node[part]
    marker = _MARK.format("Ref")
    subject = node[parts[-1]]
    # A REFERENT CAN BE A LIST -- `priced_accounts_the_arm_itself_drove_out` is the accounts
    # themselves, not prose about them, and marking the container would render nothing. The first
    # element is enough: a region that renders one renders the list.
    if isinstance(subject, list):
        assert subject and isinstance(subject[0], str), (
            "{} is an empty or non-string list on this build, so the thing the pointer names has "
            "no witness and its homes would come back empty".format(field))
        subject[0] = "{} {}".format(marker, subject[0])
    else:
        node[parts[-1]] = "{} {}".format(marker, subject)
    return _homes_of(marker, marked)


def _reading_order() -> dict:
    """`{anchor: position}` for the section, read from the door rather than declared here."""
    import re
    html = (SITE / "capabilities" / "index.html").read_text(encoding="utf-8")
    order, twice = {}, set()
    for position, match in enumerate(re.finditer(r'id="(arms-[a-z-]+)"', html)):
        if match.group(1) in order:
            twice.add(match.group(1))
        else:
            order[match.group(1)] = position
    assert not twice, ("the door declares {} more than once, so 'where it sits' has no answer "
                       "and every direction below is judged against an arbitrary one".format(
                           sorted(twice)))
    return order


def _direction_defects(subject: tuple, homes: set, referent: set, order: dict) -> list[str]:
    """Every way one pointer can be false, asked once per region it renders in."""
    phrase = subject[1]
    if subject not in _REFERENTS:
        return ["{!r} in {} is not a pointer this rung knows what to check, so its direction is "
                "unjudged -- register it in `_REFERENTS` with what it points at".format(
                    phrase, subject[0])]
    _field, claimed = _REFERENTS[subject]
    if not referent:
        return ["{!r} points at something that renders nowhere on this door, so a reader "
                "following it finds nothing".format(phrase)]
    defects = []
    for home in sorted(homes):
        if home not in order:
            defects.append("the sentence renders in #{}, which the door does not declare as part "
                           "of the section this rung reads the order of".format(home))
            continue
        for anchor in sorted(referent):
            if anchor not in order:
                defects.append("{!r} points at #{}, which the door does not declare".format(
                    phrase, anchor))
                continue
            actually = ("below" if order[anchor] > order[home]
                        else "above" if order[anchor] < order[home] else "same")
            if actually != claimed:
                defects.append(
                    "{!r} tells a reader at #{} that what it names is {}, and #{} is {}: the "
                    "pointer misdirects".format(phrase, home, claimed, anchor, actually))
    return defects


# ── the driven census, built once ────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def driven() -> list[dict]:
    """Each untied literal, its branch driven, with its landing fields and its homes.

    ONE BUILD AND ONE RENDER PER SYMBOL, not per literal: four of `_departure_statement`'s
    branches share a return slot, and driving them separately would measure the same field four
    times for the same answer.
    """
    order = _reading_order()
    rows = []
    by_symbol: dict[str, list] = {}
    for literal in _untied_literals(PRODUCER):
        by_symbol.setdefault(literal["symbol"], []).append(literal)

    for index, (symbol, literals) in enumerate(sorted(by_symbol.items())):
        marker = _MARK.format(index)
        sentence = "{} {}".format(marker, literals[0]["literal"].split("{")[0][:200])
        if symbol not in _RECIPES:
            rows.append({"symbol": symbol, "literals": literals, "recipe": False})
            continue
        built = _drive(symbol, sentence)
        fields = [where for where, text in _string_fields(built) if marker in text]
        rows.append({
            "symbol": symbol, "literals": literals, "recipe": True, "fields": fields,
            "homes": _homes_of(marker, built) if fields else set(),
            "built": built,
        })
    return [dict(row, order=order) for row in rows]


def test_every_untied_here_relative_literal_has_a_recipe_that_drives_its_branch(driven):
    """A sentence this page can publish and nothing can drive is a sentence nothing can judge.

    THE FAIL-OPEN THIS CLOSES. The two sweeps beside this file both record an untied literal and
    decline to refuse it; if this rung SKIPPED one it could not drive, the recording would move
    here and nothing would ever refuse it either. So an unrecipe'd symbol is a red that names the
    symbol, and the answer is a recipe rather than an exemption.

    Fires on: a new here-relative sentence added to a branch no recipe reaches; a producer
    function renamed out from under `_RECIPES`; a recipe that stops driving its branch, so the
    sentence reaches no field at all.
    """
    missing = [row["symbol"] for row in driven if not row["recipe"]]
    assert not missing, (
        "these symbols own an untied here-relative sentence and no recipe drives their branch, "
        "so the sentence is published-able and unjudged: {}. Add a row to `_RECIPES`".format(
            sorted(missing)))
    unwitnessed = [row["symbol"] for row in driven if row["recipe"] and not row["fields"]]
    assert not unwitnessed, (
        "these branches were driven and their sentence reached NO field of the build, so the "
        "recipe no longer takes the branch it names and every judgement below skips them: "
        "{}".format(sorted(unwitnessed)))


def test_every_undriven_pointer_is_true_from_the_region_it_lands_in(driven):
    """A here-relative pointer must be true from every region it renders in -- branch or no branch.

    THE DEFECT IT SERVES (2026-09-08, found by building this rung and driving the branches for the
    first time). `_departures`' unavailable branch told a reader the accounts the arm's own price
    drove out "ARE named above". Driven, the sentence lands in
    `decisions.auc_attribution.the_departures.reason` and renders in `#arms-decisions`; the field
    it points at, `priced_accounts_the_arm_itself_drove_out`, renders in `#arms-decisions` too,
    and no region above it names an account at all. A reader sent upwards found nothing. Nothing
    in the tree could see it: the branch is undriven, so the published-feed sweep had no string to
    judge and the producer sweep's own rule 3 is scoped off for this feed.

    KEYED TO BOTH SIDES BEING MEASURED. Neither the sentence's home nor its referent's is written
    down here; both are probed against the real door on a build the producer composed. Moving the
    decisions block above the realised panel reds this; moving the sentence to another region reds
    this; and a page reordered under either reds it without anyone editing a list.

    Fires on: a here-relative pointer landing in a region on the wrong side of what it names; a
    pointer gaining a second home the direction does not hold from; a pointer whose referent stops
    rendering; a pointer reworded past `_REFERENTS`, which is refused for being unjudgeable
    rather than passed on silence.
    """
    defects = []
    for row in driven:
        if not row.get("recipe") or not row.get("fields"):
            continue
        for literal in row["literals"]:
            subject = (row["symbol"], literal["phrase"].lower())
            field = _REFERENTS.get(subject, (None, None))[0]
            referent = _referent_homes(field, row["built"]) if field else set()
            for defect in _direction_defects(subject, row["homes"], referent, row["order"]):
                defects.append("{}:{} {}".format(row["symbol"], literal["line"], defect))
    assert not defects, (
        "the page misdirects a reader on a branch it can take:\n  " + "\n  ".join(defects))


def test_a_sentence_no_door_renders_is_reported_rather_than_read_as_clean(driven):
    """Zero homes is "we cannot tell", and it belongs on the surface rather than in a pass.

    THE FLATTERING SILENCE THIS REFUSES. A sentence that reaches a field and no region reports no
    misdirection, which is indistinguishable from a correct pointer under the leg above. Both
    branches of `_decomposition_is_the_same_contrast` were in exactly that state on 2026-09-08 --
    `floor_decomposition.different_contrast_caveat` is written by the producer and rendered by no
    deployed door -- and they claimed a direction from a place no reader stands. The repair was to
    name the headline figure, which is true from anywhere; the alternative repair is a door that
    renders the field.

    Fires on: a here-relative sentence written into a field no door reads; a door dropping the
    region that used to render one.
    """
    unrendered = ["{}:{}".format(row["symbol"], literal["line"])
                  for row in driven if row.get("fields") and not row["homes"]
                  for literal in row["literals"]]
    assert not unrendered, (
        "these branches write a here-relative pointer into a field NO door renders, so their "
        "direction is taken from a place no reader stands and nothing can check it: {}. Either "
        "a door should render the field or the sentence should name a landmark".format(
            sorted(unrendered)))


def test_MUTATION_a_pointer_that_misdirects_is_CAUGHT_and_both_verdicts_are_reachable(driven):
    """The two legs above must be failable by the page being wrong, not only by it being right.

    A GUARD THAT REFUSES ITS WHOLE PARTITION PASSES EVERY TEST OF ITS REFUSALS, which is this
    project's most-repeated control failure, so each poison is run beside its honest twin. The
    honest twin of the "above" defect is the repair that actually landed -- "beside this" from a
    region that IS the referent's -- and if that reds, the repair gets reverted.

    AND THE PROBE MUST BE SHOWN NOT TO BE BLIND. A rung whose homes are all empty raises no defect
    at all: every direction is vacuous and every leg above passes. The witness is that at least
    one driven sentence really did reach a region on the real door.
    """
    order = _reading_order()
    assert "arms-decisions" in order and "arms-realised" in order, (
        "the door declares neither block this poison is written against, so nothing below is a "
        "witness to anything")

    here, above_it, below_it = {"arms-decisions"}, {"arms-headline"}, {"arms-note"}
    adjacent = ("_departures", "beside this")
    downward = ("_world_clause", "figures below")

    # A. THE SENTENCE IS WRONG, THE PAGE IS NOT -- the defect this rung was written for, restored.
    assert _direction_defects(adjacent, here, here, order) == [], (
        "the landed repair is reported as a misdirection, so this judge refuses correct prose "
        "and every red it raises is uninformative")
    caught = _direction_defects(adjacent, here, above_it, order)
    assert any("misdirects" in defect for defect in caught), (
        "a sentence saying the reader will find its subject where they stand, whose subject "
        "renders in a region ABOVE them, is not caught: " + str(caught))

    # AND THE OTHER HALF OF THE PARTITION. The same phrase must be ALLOWED wherever it is true --
    # a judge that reds on the word rather than the claim says nothing about direction.
    assert _direction_defects(downward, here, below_it, order) == [], (
        "'figures below' is refused from a region above what it names, so this judge rejects a "
        "phrase rather than reading its claim")
    assert any("misdirects" in defect
               for defect in _direction_defects(downward, here, above_it, order)), (
        "'figures below' pointing at a region ABOVE the sentence reads true, so the direction "
        "half of this control is not wired at all")

    # B. AN UNREGISTERED PHRASE FAILS CLOSED, and says so as an unregistered phrase rather than as
    # a misdirection -- a red naming the wrong reason is how a correct fix gets reverted.
    unknown = _direction_defects(("_world_clause", "over that way somewhere"), here, below_it,
                                 order)
    assert any("not a pointer this rung knows" in defect for defect in unknown), (
        "a pointer reworded past the registered vocabulary is waved through, which is the "
        "fail-open the whole rung exists against: " + str(unknown))
    # AND THE SAME PHRASE UNDER A DIFFERENT SYMBOL IS A DIFFERENT SUBJECT. The phrase-keyed first
    # draft answered here from the wrong producer's referent and would have gone on agreeing until
    # one of the two moved.
    assert _direction_defects(("_polarity_check", "figures below"), here, below_it, order), (
        "a registered phrase is accepted from a producer it was never registered for, so the "
        "table is keyed to the words and not to what the sentence points at")

    # C. A REFERENT THAT RENDERS NOWHERE IS A RED, not a vacuous pass over an empty loop.
    assert _direction_defects(downward, here, set(), order), (
        "a pointer whose subject renders in no region at all reads true, so the leg above "
        "passes on having seen nothing")

    # D. THE WITNESS. Everything above is arithmetic over sets; this is the leg that says the sets
    # came from a real render of a real build.
    assert any(row.get("homes") for row in driven), (
        "not one driven branch reached a region on the real door, so every judgement in this "
        "file is vacuous -- either the probe has gone blind or no recipe drives its branch")
