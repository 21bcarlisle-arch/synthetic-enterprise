"""Site-wide: a feed string that renders in more than one place may not say "above" or "below".

THE DEFECT THIS SERVES, AND WHY IT IS A CLASS AND NOT AN INSTANCE (2026-09-08). On 2026-09-08
`test_a_sentence_pointing_at_the_band_table_is_true_from_EVERY_region_it_renders_in` closed one
live falsehood on the capabilities page: `_the_level_legs_family` said the re-draw family was in
the band table "higher up this section", and that sentence has two homes on opposite sides of the
table, so one of the two readers was sent the wrong way up the page. The cause was not a typo. A
PRODUCER CANNOT KNOW HOW MANY HOMES ITS OUTPUT HAS -- the only thing in the tree with an opinion
about where that sentence rendered was the producer's own docstring, which was true about the one
home it knew and silent about the other. That rung judges three sentences on one page. This one
asks the same question of every payload string the site publishes.

WHAT IT FOUND ON ITS FIRST RUN, which is why it exists rather than being a tidy generalisation.
`_redraw_band_clause` had been given a LANDMARK for the table it points at ("directly below this
headline") hours earlier, and the very next clause of the same sentence still read "the FIGURE
above". That sentence is composed into `#arms-headline` once per leg by `_leg_clause`, so in the
published headline the selection leg's copy sat below £17,739 and told the reader that figure sat
ABOVE the centre of a family spanning -£3,075 to £1,200. Every control over that sentence asked
whether it named the band table; none asked what "above" was measured from. The remedy is the same
one: name the thing ("the published draw"), never the direction.

THE PROPERTY, NOT TODAY'S PAGES. Nothing here enumerates feeds, pages, producers or sentences.
The homes are DERIVED from the published bytes -- a string that occurs at two JSON paths, or
inside a longer string at another path, was composed more than once by construction, and each of
those paths is a place a page can render it. So a producer that gains a home gains it here without
anyone remembering to edit a list, and a feed added tomorrow is swept the day it is written.

IT DOES NOT BAN A WORD. "below the centre of its own family" is not spatial and is not touched:
a phrase is a pointer only when a direction word is paired with a PAGE ELEMENT (a figure, a table,
a panel, a headline). Of those, one with a named anchor -- "below this headline", "under the
headline figure" -- is a LANDMARK and holds from anywhere; one whose anchor is "this section" or
"this page", or which has no anchor at all ("the figure above", "higher up"), is a claim about
wherever it happens to render, and that is the claim a multi-home string cannot make truthfully.

AND IT FAILS CLOSED. A direction word sitting beside a page element in a shape none of the three
classifiers reads is reported as UNCLASSIFIED rather than passed over. Reading silence as a pass is
the fail-open this whole class exists against -- the sentence that broke was, for months, a phrase
no control had an opinion about.

WHY THE PUBLISHED BYTES ARE THE SUBJECT and not the producers. A reader meets the feed, not the
function. A producer fixed on Monday whose feed is republished on Friday is false all week, which
is exactly the state `site/data/value_arms.json` was in when this control was written: the retired
recital was still on the page four commits after the producer stopped emitting it.
"""
import collections
import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent

#: Anything shorter than this is a label or a key, not prose that can point anywhere. Kept low on
#: purpose: the cost of sweeping a short string is nothing, and a heading is exactly the kind of
#: thing that gets composed into two places.
_MIN_PROSE = 30

#: A PAGE ELEMENT -- the noun that makes a direction word spatial. Without one, "above" is a
#: comparison ("above the cap", "above the centre") and none of this applies.
_ELEMENT = (r"(?:figures?|tables?|panels?|headlines?|sections?|pages?|charts?|rows?|columns?|"
            r"lists?|paragraphs?|blocks?|captions?|banners?|tiles?|cards?|diagrams?|graphs?)")

#: An anchor that names no landmark. "This section" is wherever the reader is, so a direction
#: measured from it is re-asked in every home -- which is the shape that cannot be verified where
#: it is written.
_HERE = re.compile(r"^(?:this|the)\s+(?:section|page|panel|block|list|paragraph)$", re.I)

#: "the figure ABOVE" -- element first, direction last, nothing anchoring it.
_BARE_AFTER = re.compile(
    r"\b(?:the|this|that|those|these)\s+(?:[a-z'’-]+\s+){0,3}(?:" + _ELEMENT + r")\s+"
    r"(?:above|below|opposite|beneath|underneath|overleaf|preceding|following|earlier|later)\b",
    re.I)

#: "BELOW this headline" -- direction first, then the thing it is measured from. Whether that is a
#: landmark or a `here` depends on the anchor, which is why the anchor is captured.
_ANCHORED = re.compile(
    r"\b(?:above|below|beneath|underneath|under|higher up|further up|further down|lower down|"
    r"at the top of|at the foot of|at the bottom of)\s+"
    r"((?:this|the|that)\s+(?:[a-z'’-]+\s+){0,2}(?:" + _ELEMENT + r"))\b", re.I)

#: A direction with no object at all. Always `here`-relative -- there is nothing else it could be.
_ADVERB = re.compile(r"\b(?:higher up|further up|further down|lower down|overleaf)\b", re.I)

#: The fail-closed net: a direction word this file has an opinion about, wherever it appears.
_DIRECTION = re.compile(r"\b(?:above|below|beneath|underneath|overleaf|higher up|further up|"
                        r"further down|lower down)\b", re.I)
_ELEMENT_WORD = re.compile(r"\b" + _ELEMENT + r"\b", re.I)

#: How near a direction word an element noun has to sit before the pair is treated as possibly
#: spatial. Wide enough to span a clause, narrow enough that a paragraph mentioning a table and
#: separately comparing two numbers is not dragged in.
_NEARBY_CHARS = 40


def _leaves(node, path=""):
    """Every string the feed publishes, with the path it publishes it at."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _leaves(value, path + "." + str(key))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _leaves(value, path + "[{}]".format(index))
    elif isinstance(node, str):
        yield path, node


def _strings_with_more_than_one_home(doc) -> dict:
    """`{string: [paths]}` for every payload string this feed composed more than once.

    TWO WAYS TO HAVE TWO HOMES, and the second is the one that broke. A string repeated verbatim
    at two paths is the obvious case. The case that produced the live falsehood is a string
    COMPOSED INTO a longer one -- `redraw_band` is its own field and is also inside `headline` --
    because that is what a page does when one panel renders a clause and another renders the
    paragraph it was folded into.
    """
    prose = [(path, text) for path, text in _leaves(doc) if len(text) >= _MIN_PROSE]
    by_string = collections.defaultdict(list)
    for path, text in prose:
        by_string[text].append(path)
    homes = {text: list(paths) for text, paths in by_string.items() if len(paths) > 1}
    # CONTAINMENT, SHORTEST FIRST, so each string is tested against the longer ones only. One
    # containing string is enough to establish a second home; finding every one of them would
    # change no verdict and turns this into a quadratic scan of the whole site.
    shortest_first = sorted(by_string, key=len)
    for index, text in enumerate(shortest_first):
        if len(text) < 40:
            continue
        for longer in shortest_first[index + 1:]:
            if len(longer) > len(text) and text in longer:
                homes[text] = sorted(set(homes.get(text, by_string[text])) | set(by_string[longer]))
                break
    return homes


def pointer_defects(sentence: str) -> list:
    """Every way one string can point somewhere it cannot know it is standing.

    Exported rather than private because the mutation rung below drives it directly: a judge that
    can only be reached through a whole-site sweep can only be poisoned by editing the site.
    """
    defects, read = [], []
    for match in _BARE_AFTER.finditer(sentence):
        read.append(match.span())
        defects.append("points from wherever it renders, with no landmark: " + match.group(0))
    for match in _ANCHORED.finditer(sentence):
        read.append(match.span())
        anchor = re.sub(r"\s+", " ", match.group(1)).strip()
        if _HERE.match(anchor):
            defects.append(
                "measured from {!r}, which is wherever the reader already is: {}".format(
                    anchor, match.group(0)))
    for match in _ADVERB.finditer(sentence):
        if not any(start <= match.start() < end for start, end in read):
            defects.append("a direction with nothing to measure it from: " + match.group(0))
        read.append(match.span())
    # FAIL CLOSED. A direction word beside a page element that none of the three above read is a
    # pointer nobody has an opinion about, and silence is not a pass.
    for match in _DIRECTION.finditer(sentence):
        if any(start <= match.start() < end for start, end in read):
            continue
        window = sentence[max(0, match.start() - _NEARBY_CHARS):match.end() + _NEARBY_CHARS]
        if _ELEMENT_WORD.search(window):
            defects.append(
                "a direction beside a page element in words this control does not classify, so "
                "it is unchecked -- teach the classifier what it claims: " + window.strip())
    return defects


def _every_feed() -> list:
    """`[(name, doc)]` for every JSON the site publishes -- data feeds and state artefacts alike."""
    feeds = []
    for path in sorted(SITE.rglob("*.json")):
        try:
            feeds.append((str(path.relative_to(SITE)), json.loads(path.read_text(encoding="utf-8"))))
        except (ValueError, OSError) as exc:
            feeds.append((str(path.relative_to(SITE)), exc))
    return feeds


def _the_sweep() -> tuple:
    """`(defects, homes_seen, feeds_read)` over the whole published site."""
    defects, homes_seen, feeds_read = [], 0, 0
    for name, doc in _every_feed():
        if isinstance(doc, Exception):
            defects.append("{}: is published and cannot be read, so nothing in it is swept "
                           "({})".format(name, doc))
            continue
        feeds_read += 1
        for sentence, paths in _strings_with_more_than_one_home(doc).items():
            homes_seen += 1
            for defect in pointer_defects(sentence):
                defects.append("{} at {}: {}".format(name, sorted(set(paths)), defect))
    return defects, homes_seen, feeds_read


def test_a_payload_string_with_more_than_one_home_carries_no_here_relative_pointer():
    """No string the site publishes twice may tell a reader which way to look.

    Fires on: a producer composing a `here`-relative pointer into a clause that is also folded
    into a headline; a single-home pointer gaining a second home; a landmark being reworded back
    to a bare direction; or a pointer phrased in words this classifier does not read, which reds as
    unclassified rather than passing.
    """
    defects, homes_seen, feeds_read = _the_sweep()
    assert not defects, (
        "{} published string(s) point somewhere they cannot know they are standing:\n  ".format(
            len(defects)) + "\n  ".join(sorted(defects)))

    # THE SWEEP NEEDS A WITNESS. "No multi-home string points" is satisfied by finding no
    # multi-home strings at all, which is what a broken home-derivation, an empty glob or a
    # renamed feed directory all look like. This rung is uninformative without a population.
    assert feeds_read >= 50, (
        "only {} feed(s) could be read under {}, so this sweep is judging a fraction of the "
        "published site".format(feeds_read, SITE))
    assert homes_seen >= 100, (
        "only {} published string(s) were found to have more than one home, and the site had "
        "2,057 when this control was written -- `_strings_with_more_than_one_home` has gone "
        "blind and every assertion above is passing on an empty set".format(homes_seen))


def test_MUTATION_a_here_relative_pointer_is_CAUGHT_and_a_landmark_is_NOT():
    """The judge above must be failable by prose being wrong, not only by it being right.

    POISONED ON BOTH SIDES, because a judge that refuses everything passes every "does it catch
    the defect" leg and is useless. Each poison must red AND its honest twin must not -- and the
    honest twins are real: both are wordings live in `tools/generate_value_arms_data.py` today.

    R15, run and reverted:
      * restore "the figure above sits {where} the centre" to `_redraw_band_clause` and republish
        -> the rung above reds with four defects over two strings, naming `.headline` and
        `.current_world.redraw_band` among the homes of one and `.current_world.selection_leg.*`
        of the other.
      * with that poison live, drop the containment leg from `_strings_with_more_than_one_home`
        -> one of the two goes green. The surviving catch is a verbatim repeat across the whole
        advantage and the level leg; the SELECTION leg's copy is caught only by containment,
        because its second home is `verdict_withheld_because` folding the clause into a longer
        string. That is the shape the band-table defect had, so the containment leg is the one
        this class turns on rather than a completeness flourish.
    """
    # A. THE WORDING THAT WAS LIVE, and the two wordings that replaced it.
    was_live = ("The re-draws themselves span £17,262 to £20,002 and average £19,015, so the "
                "figure above sits BELOW the centre of its own family.")
    assert pointer_defects(was_live), (
        "the wording that was published in two homes until 2026-09-08 is not caught, so this "
        "control passes on the very defect it was written for")
    fixed = ("The re-draws themselves are set out contrast by contrast in the band table directly "
             "below this headline, lowest, mean and highest; the published draw sits BELOW the "
             "centre of its own family.")
    assert not pointer_defects(fixed), (
        "the landmark wording that replaced it is refused, so this control rejects correct prose "
        "and every red it raises is uninformative: " + str(pointer_defects(fixed)))

    # B. IT IS THE DIRECTION THAT IS JUDGED, NOT THE WORD. The same direction word, anchored to a
    # named landmark, holds from anywhere and must pass; anchored to "this section" it does not.
    assert not pointer_defects("the same three are in the re-draw band table under the headline "
                               "figure, against the same figure this share is a share of"), (
        "a landmark pointer is refused, so the judge bans a word rather than reading a claim")
    caught = pointer_defects("the same three are in the re-draw band table higher up this section")
    assert caught, "the retired `here`-relative wording is not caught: " + str(caught)
    assert not any("does not classify" in defect for defect in caught), (
        "the poison reds as an unrecognised phrase rather than as a `here`-relative claim, so the "
        "direction half of this control is untested: " + str(caught))

    # C. A COMPARISON IS NOT A POINTER. This is the half that decides whether the control is
    # usable at all: "below the centre" appears all over the published feeds and banning it would
    # make this rung a nuisance that gets deleted rather than a control that gets obeyed.
    assert not pointer_defects(
        "the published draw sits BELOW the centre of its own family, and the share is above the "
        "half that separates choosing from charging"), (
        "an ordinary numeric comparison is read as a page pointer, so this control cannot be kept")

    # D. FAIL CLOSED ON A PHRASING NOBODY TAUGHT IT. Silence is the fail-open this class is about.
    unread = pointer_defects("the band table is somewhere over there, below where you are now")
    assert any("does not classify" in defect for defect in unread), (
        "a direction sitting beside a page element in unregistered words passes silently, so a "
        "pointer reworded past this vocabulary is unchecked: " + str(unread))
