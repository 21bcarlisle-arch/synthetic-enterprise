"""A payload sentence that says "here" may render in ONE region, because its producer cannot count.

THE DEFECT THIS GENERALISES (2026-09-08). `tests/tools/test_generate_value_arms_data.py::
test_a_sentence_pointing_at_the_band_table_is_true_from_EVERY_region_it_renders_in` closed one
instance: `_the_level_legs_family` said the re-draw family was in "the band table HIGHER UP THIS
SECTION", and that sentence had two homes -- `#arms-composition` renders it, and
`_current_world_clause` composes it into the headline that `#arms-headline` renders. `#arms-redraw`
sits below one and above the other, so one of the two readers was sent the wrong way up the page.

The generalisable half, in the finding's own words: **a producer does not know how many homes its
output has, so a sentence that says "here" is unverifiable at the point it is written.** That is
not a fact about `value_arms.json`. It is a fact about every feed on this site, and this file is
the sweep for it: EVERY deployed door, driven through its OWN boot path against the LOCAL feeds,
with each payload string's homes DERIVED from what actually rendered rather than declared by
anybody. A sentence with one home may say "the table above" and be checked by whoever owns that
page. A sentence with two cannot be checked by anyone, including the control that wrote it.

WHAT THE SWEEP FOUND WHEN IT WAS BUILT, and why the rule is worth standing up on a clean page:
31 payload strings render into more than one region, up to SEVEN (a `knowledge_wholesale.json`
topic blurb, in the sidebar of seven knowledge doors). None of them carries here-relative prose
today -- so this control passes on the tree it was written against, and that is the point of a
ratchet. Three producers are one sentence away from the parent defect:

  * `delivery.json .what_it_decided.focus[].what/.why` -> `#delivery-decided` AND `#delivery-next`
    on /harness/. The SAME feed's `what_it_got_wrong.entries[].what` already writes "the row
    above" and "the figure above" freely, and those are single-homed and true. A writer moving a
    sentence between two fields of one producer creates the two-home defect with no other change.
  * `value_arms.json .realised.arms[].what` == `.provisioned.arms[].what` -> `#arms-realised` AND
    `#arms-split`.
  * `knowledge_wholesale.json .topics[].blurb`/`.title` -> the `#sidebar` of every knowledge door.

WHAT THIS CONTROL CANNOT SEE, said on the surface rather than in a footnote. Homes are derived
from a real render against the PUBLISHED feeds, so a producer branch today's data does not drive
renders nowhere and is judged nowhere. The parent defect lived on exactly such a branch: with the
level leg sign-stable, `composition.why_not_readable` never carries the pointer at all. Twelve
here-relative payload strings currently render in zero regions and this file says nothing about
them. Driving every producer's branches is the follow-on; the value_arms rung does it for the one
page where the defect was found, by running the composers instead of reading the feed.

R15 -- the mutations, each run against the real tree and reverted:
  * plant "the re-draw band table higher up this section" into `delivery.json`'s `focus[0].why`,
    which has two homes -> `test_no_here_relative_pointer_is_composed_into_more_than_one_region`
    reds, naming both homes and the field it was written at, and NOTHING else reds.
  * plant the LANDMARK wording "directly below this headline" into that same two-home field ->
    all five stay green. This is the leg that stops the rule refusing its whole partition, and it
    is the repair the parent finding shipped: a control that reds on the fix gets the fix reverted.
  * make `_homes` return the empty set -> the witness and detector legs red, so a normalisation
    that goes blind cannot report a clean site.
  * widen `_LANDMARK` to match every sentence -> the detector leg reds. The landmark clause is an
    exemption, and an exemption nothing measures is the shape that quietly excuses everything.
  * drop every rendered region -> the blindness leg reds first, before the rule waves the site
    through on having seen nothing.
"""
from __future__ import annotations

import html as html_entities
import json
import posixpath
import re
import sys
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE))
sys.path.insert(0, str(SITE.parent))

import live_pixel_verify as lpv  # noqa: E402

from tools import here_relative_vocabulary as vocab  # noqa: E402

HARNESS = SITE / "_live_harness.mjs"

#: The shortest payload string worth judging. Below this a string is a label ("Chose", a date, a
#: units word) and containment matching says nothing -- "above" appears inside a hundred longer
#: sentences. Every pointer the parent finding dealt with is a full clause.
_LONG_ENOUGH = 40

#: WHAT MAKES A SENTENCE A `HERE`-RELATIVE POINTER: it claims a direction and names nothing to
#: take the direction FROM, so its referent is wherever it happens to render. This is a detector
#: over prose and it is honest about being one -- a pointer worded past this vocabulary is not
#: caught, which is why `test_the_here_relative_detector_is_aimed_at_prose_this_site_actually
#: _publishes` requires it to still be finding live sentences.
#:
#: THE VOCABULARY ITSELF NOW LIVES IN `tools/here_relative_vocabulary.py` and is bound back here
#: under the names three other rungs already import off this module. It moved on 2026-09-24 so
#: that `background/direction.py` could refuse a pointer at WRITE time without pulling this
#: module -- and therefore `live_pixel_verify`, which fetches from the live host, and `pytest` --
#: into the draw's import chain. Every word of the measured audit below moved with it; read it
#: there. This file is still the RULE. It is no longer the only place the rule can be asked from.
#:
#: MOVED, NOT COPIED: `tools/here_relative_vocabulary.py` carries the noun audit, the three
#: measured refusals, and the participle branch's own lesson. Two copies of a vocabulary drift,
#: and the drift would show up as the write-time refusal and this sweep judging different sets of
#: sentences -- one passing a page the other refused.
_HERE_RELATIVE = vocab.HERE_RELATIVE
_LANDMARK = vocab.LANDMARK

#: Doors that render nothing by construction. `/privacy/` is deliberately static server-rendered
#: markup with no inline script -- see `_live_harness.mjs`, which reports `static` for exactly
#: this shape. Treating it as blindness would make the blindness leg cry wolf every run.
_STATIC_DOORS = frozenset({"/privacy/"})


def _doors() -> list[str]:
    """Every door ON DISK, which is not the same set as the advertised one.

    NOT `live_pixel_verify.all_doors()`, and the difference matters here. That reads the sitemap
    plus `ia_register.INTERNAL_DOORS`, and the sitemap deliberately omits the sixteen /knowledge/
    topic pages (they carry their own noindex). Six doors against twenty-two deployed -- and the
    knowledge doors are where the multi-home sidebar lives, so sweeping the advertised set would
    have reported a clean site while missing the widest-shared payload strings on it.
    """
    doors = []
    for index in sorted(SITE.rglob("index.html")):
        rel = index.parent.relative_to(SITE).as_posix()
        doors.append("/" if rel == "." else "/" + rel + "/")
    assert doors, "no door was found under site/, so this sweep has no subject at all"
    return doors


def _feed_path(door: str, url: str) -> Path:
    """The LOCAL file behind a page-relative feed url, resolved the way a browser would."""
    resolved = posixpath.normpath(posixpath.join(door, url.split("?")[0]))
    return SITE / resolved.lstrip("/")


def _norm(text: str) -> str:
    """One normal form for both sides of the containment test.

    The doors put payload through `prose()`/`esc()` on the way to the DOM: markdown emphasis
    becomes markup, `&` becomes an entity, and the repo's own em-dashes and curly quotes survive
    in one form on one side and another on the other. Normalising only the rendered side would
    make the match silently miss, and a miss here reports ZERO homes -- the flattering answer.
    """
    text = re.sub(r"<[^>]+>", " ", text)
    text = html_entities.unescape(text)
    text = (text.replace("’", "'").replace("‘", "'")
                .replace("“", '"').replace("”", '"')
                .replace("—", "--").replace("–", "-").replace(" ", " "))
    text = re.sub(r"[*`_]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


#: BOUND, NOT WRAPPED. Three rungs import these off this module by name; a wrapper here would be
#: a second place the landmark rule could be got wrong, which is the whole reason for one home.
_here_relative_phrases = vocab.here_relative_phrases
_here_relative_phrase = vocab.here_relative_phrase


def _payload_strings(path: Path) -> list[tuple[str, str]]:
    """`[(json path, string)]` for every string a feed carries, at any depth."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    out: list[tuple[str, str]] = []

    def walk(node, where: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, "{}.{}".format(where, key))
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, "{}[{}]".format(where, index))
        elif isinstance(node, str) and len(node) >= _LONG_ENOUGH:
            out.append((where, node))

    walk(payload, "")
    return out


def _render(door: str, overrides: dict[str, object] | None = None) -> tuple[dict, dict, dict]:
    """Drive one door's own boot path; return `(regions, feeds, meta)`.

    `overrides` replaces a feed by url, which is what the mutation rung poisons through. Feed
    discovery is two-pass for the reason `live_pixel_verify.verify_door` documents: several doors
    build their feed url at run time, so the first render is what REPORTS which urls the door
    actually asked for.
    """
    if not HARNESS.is_file():
        pytest.fail("site/_live_harness.mjs is missing -- this sweep is UNAVAILABLE, and an "
                    "unavailable check is a FAILED check (R15)")
    index = SITE / door.strip("/") / "index.html" if door.strip("/") else SITE / "index.html"
    markup = index.read_text(encoding="utf-8")
    feeds: dict[str, object] = {}

    def load(url: str) -> None:
        if url in feeds:
            return
        if overrides and url in overrides:
            feeds[url] = overrides[url]
            return
        path = _feed_path(door, url)
        if not path.is_file():
            return
        try:
            feeds[url] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

    for url in lpv.feed_urls(markup):
        load(url)
    try:
        rendered = lpv.run_harness(markup, feeds)
    except lpv.LiveCheckUnavailable as unavailable:
        pytest.fail("the render harness could not run ({}), so every door below would report "
                    "zero homes -- an unavailable check is a FAILED check".format(unavailable))
    asked = [u for u in (rendered.get("_meta") or {}).get("requested", []) if u not in feeds]
    if asked:
        for url in asked:
            load(url)
        rendered = lpv.run_harness(markup, feeds)
    meta = rendered.pop("_meta", {}) or {}

    regions = {}
    for element, content in rendered.items():
        text = _norm("{} {}".format(content.get("innerHTML") or "",
                                    content.get("textContent") or ""))
        if text:
            regions[element] = text
    return regions, {url: _feed_path(door, url).as_posix() for url in feeds}, meta


def _homes(sentence: str, regions_by_door: dict[str, dict[str, str]]) -> set[str]:
    """`{door#element}` for every region whose RENDERED content carries this sentence.

    DERIVED, NEVER DECLARED -- the rule the parent rung established. Composition needs no model
    here: a sentence a producer folds into a headline is found in the headline's region because it
    is there, which is exactly the fact a reader meets and the one the producer cannot see.
    """
    needle = _norm(sentence)
    if len(needle) < _LONG_ENOUGH:
        return set()
    return {"{}#{}".format(door, element)
            for door, regions in regions_by_door.items()
            for element, text in regions.items() if needle in text}


@pytest.fixture(scope="module")
def swept() -> dict:
    """The whole site, rendered once: regions per door, and every payload string's homes."""
    regions_by_door, feeds_by_door, blind = {}, {}, []
    for door in _doors():
        regions, feeds, meta = _render(door)
        assert not meta.get("scriptError"), (
            "{} threw while booting ({}), so whatever it did not render is invisible to this "
            "sweep".format(door, meta.get("scriptError")))
        regions_by_door[door] = regions
        feeds_by_door[door] = feeds
        if not regions and not meta.get("static") and door not in _STATIC_DOORS:
            blind.append(door)

    pointers: dict[str, dict] = {}
    for door, feeds in feeds_by_door.items():
        for url, path in feeds.items():
            for where, sentence in _payload_strings(Path(path)):
                key = _norm(sentence)
                if len(key) < _LONG_ENOUGH:
                    continue
                row = pointers.setdefault(key, {"raw": sentence, "fields": set(), "homes": set()})
                row["fields"].add("{} {}".format(path, where))
                row["homes"] |= _homes(sentence, {door: regions_by_door[door]})
    return {"regions": regions_by_door, "pointers": pointers, "blind": blind}


# ── the rule ─────────────────────────────────────────────────────────────────────────────────

def test_no_here_relative_pointer_is_composed_into_more_than_one_region(swept):
    """A sentence claiming a direction from "here" must have exactly one "here".

    KEYED TO THE PROPERTY, NOT TO TODAY'S PAGE. Nothing here pins a position or a wording. A
    sentence with one home is left alone whatever it says -- the page that owns it can check it.
    A sentence with two is a defect however true it happens to be in both today, because nothing
    that edits either home is looking at the other, and the producer that wrote it can see
    neither.

    Fires on: a producer composing a here-relative sentence into a second region; a door rendering
    an existing here-relative payload field in a second place; a feed field carrying such a
    sentence being copied to a second field that renders elsewhere.
    """
    defects = []
    for key, row in sorted(swept["pointers"].items()):
        if len(row["homes"]) < 2:
            continue
        # ALL OF THEM IN THE MESSAGE, not the first. The rule fires either way -- one direction is
        # enough to refuse -- but a repairer acts on what the refusal NAMES, and naming only the
        # first is how a sentence gets half-repaired and stays false the other way.
        phrases = _here_relative_phrases(key)
        if phrases:
            defects.append(
                "{} claims a direction from wherever it renders, and it renders in {}: {} -- "
                "written at {}. Name the landmark the direction is FROM, which is true from all "
                "of them.".format(", ".join(repr(p) for p in phrases),
                                  len(row["homes"]), sorted(row["homes"]),
                                  sorted(row["fields"])))
    assert not defects, (
        "a payload sentence points a reader somewhere relative to itself and has more than one "
        "self:\n  " + "\n  ".join(defects))


# ── the legs that stop it passing on blindness ───────────────────────────────────────────────

def test_every_deployed_door_rendered_something_or_this_sweep_is_blind(swept):
    """A door that rendered nothing contributes no regions, so every string on it reports zero
    homes and the rule above waves the whole page through. That reads exactly like a clean site."""
    assert not swept["blind"], (
        "these doors rendered NO region, so no payload string on them can be judged and the rule "
        "above passes over them silently: {}".format(swept["blind"]))


def test_the_sweep_can_see_a_string_with_two_homes(swept):
    """THE QUANTIFIER NEEDS A WITNESS. On a corpus where every string renders once, "at most one
    home" is indistinguishable from "at most one home is possible", and the normalisation going
    blind would produce exactly that -- zero homes everywhere and a green run.

    Keyed to the property (some string somewhere is shared), never to which one: the three
    families named in the module docstring are evidence, not the assertion.
    """
    shared = {k: r for k, r in swept["pointers"].items() if len(r["homes"]) > 1}
    assert shared, (
        "no payload string on the whole site reaches two regions, which this site is known not to "
        "be -- the containment match has gone blind and the rule above is judging nothing")
    assert max(len(r["homes"]) for r in shared.values()) >= 2


def test_the_here_relative_detector_is_aimed_at_prose_this_site_actually_publishes(swept):
    """The rule is only as good as the vocabulary, so the vocabulary must still be finding live
    sentences. A registered phrase that matches nothing rendered anywhere is a detector aimed at
    prose nobody writes, and it would pass over a site that had turned entirely here-relative."""
    judged = [k for k, r in swept["pointers"].items()
              if r["homes"] and _here_relative_phrase(k)]
    assert judged, (
        "not one RENDERED payload string carries a registered here-relative phrase. Either the "
        "site stopped writing them -- in which case delete this control rather than keep a green "
        "one that checks nothing -- or the vocabulary has gone stale against how it writes now")


# ── R15: the rule must be failable by the site being wrong ───────────────────────────────────

def test_MUTATION_a_here_relative_pointer_given_a_second_home_is_CAUGHT():
    """Poisoned through the REAL door, and both wordings are driven.

    The subject is `/harness/`, where `what_it_decided.focus[].why` renders in `#delivery-decided`
    and again in `#delivery-next` -- a live two-home payload field, so the poison changes the
    WORDING and nothing about the page. The two wordings are the parent finding's own: the one
    that was live and false, and the landmark that replaced it.

    BOTH LEGS, because a judge that refuses everything passes the first one. If the landmark
    wording also red, this control would red on the repair and the repair would come back out.
    """
    door, url = "/harness/", "../data/delivery.json"
    feed = json.loads((SITE / "data" / "delivery.json").read_text(encoding="utf-8"))
    focus = ((feed.get("what_it_decided") or {}).get("focus") or [])
    assert focus, ("/harness/ publishes no focus item, so the two-home field this rung poisons is "
                   "not on the page and the poison would prove nothing")

    def _poisoned_homes(sentence: str) -> set[str]:
        mutated = json.loads(json.dumps(feed))
        mutated["what_it_decided"]["focus"][0]["why"] = sentence
        regions, _, meta = _render(door, overrides={url: mutated})
        assert not meta.get("scriptError"), meta.get("scriptError")
        return _homes(sentence, {door: regions})

    here = "The re-draw band table higher up this section states what this replaced."
    landmark = "The re-draw band table directly below this headline states what this replaced."

    here_homes = _poisoned_homes(here)
    assert len(here_homes) >= 2, (
        "the poisoned sentence reached {} region(s), so the two-home shape this rung exists to "
        "catch was never built and the assertion below is vacuous: {}".format(
            len(here_homes), sorted(here_homes)))
    assert _here_relative_phrase(_norm(here)) == "higher up", (
        "the retired wording -- live and false in the headline until 2026-09-08 -- is no longer "
        "recognised as a here-relative claim, so the rule would pass over its return")

    landmark_homes = _poisoned_homes(landmark)
    assert len(landmark_homes) >= 2, (
        "the landmark wording did not reach two regions, so its green below is a green over "
        "nothing rather than over a two-home landmark claim")
    assert _here_relative_phrase(_norm(landmark)) is None, (
        "the LANDMARK wording the parent finding shipped is reported as a here-relative claim, so "
        "this control reds on the repair and would get it reverted")


def test_MUTATION_the_2026_09_19_widening_can_still_FIRE_on_the_wordings_it_was_added_for():
    """The vocabulary added on 2026-09-19 must stay able to catch something.

    WHY THIS LEG IS NOT PARANOIA. Two lanes widened `_HERE_RELATIVE` that day -- fourteen nouns
    from the furniture audit, and `published` on the participle branch -- and BOTH lanes repaired
    every live instance they had just exposed. So on the day the widening landed, the words it was
    added for matched nothing anywhere on the site, and every other leg in this file stayed green
    whether the widening was present or not. Delete `run` from the noun branch, or `published` from
    the participle branch, right now: nothing else here notices. That is the exact shape this
    project keeps paying for -- a control extended to cover a class, with the extension made
    unreachable by the very repairs that motivated it.

    KEYED TO THE VOCABULARY, NOT TO THE PAGE, and deliberately so. Asserting these wordings are
    ABSENT from the live site would pin this to today's answer and go red the day someone writes
    one legitimately and repairs it. What is asserted is the thing that must not rot: the detector
    can still RECOGNISE the wordings, so a regression that reintroduces one is caught rather than
    waved through.

    THE SPECIMENS ARE THE RETIRED STRINGS THEMSELVES, quoted from the producer as they stood
    before their repairs, for the same reason the leg above quotes the parent finding's: a wording
    that was live and false is the only specimen that proves the vocabulary would have caught the
    real thing rather than a convenient paraphrase.

    Fires on: any of these words being dropped from `_HERE_RELATIVE`; either branch being rewritten
    into something that no longer reaches them; `_LANDMARK` widening far enough to exempt them.
    """
    retired = {
        # `_population_repair_bias` -- the instance both lanes' items were filed for, live in
        # `site/data/value_arms.json` and certified clean by this very file.
        "20 paths of pricing code away from the run above, so it is the size of the CLASS":
            "run above",
        # `_staleness_caveat`, and this one was a TWO-HOME pointer on the deployed page --
        # `/capabilities/#arms-errorbar` and `#arms-headline` -- so a live instance of the parent
        # defect, not merely an unjudged one. It is the participle branch's witness.
        "re-running the noise floor on the run published above is owed work":
            "published above",
        # `_current_world_contrast`: the noun branch has to reach `below` as well as `above`, or
        # half the vocabulary is decorative.
        "It was taken at then; the run below it was taken at now":
            "run below",
    }
    for sentence, expected in retired.items():
        found = _here_relative_phrase(_norm(sentence))
        assert found is not None, (
            "{!r} was a LIVE published pointer until 2026-09-19 and this vocabulary no longer "
            "recognises it, so the widening landed to catch it has been undone and its return "
            "would be silent".format(sentence))
        assert found.lower() == expected, (
            "{!r} is recognised, but as {!r} rather than {!r} -- a different branch of the "
            "vocabulary is matching it, so the branch this leg exists to hold open is untested "
            "and may already be gone".format(sentence, found.lower(), expected))
