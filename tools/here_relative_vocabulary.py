"""ONE vocabulary for "this sentence points somewhere relative to where it happens to render".

REHOMED HERE 2026-09-24, FROM `site/test_a_here_relative_pointer_has_one_home.py`, WHICH IS STILL
THE RULE. That module sweeps the deployed doors and is the reason any of this exists; three other
rungs already import the vocabulary off it rather than copy it. The move is not tidying. It is the
only way a FOURTH consumer could exist at all:

    `background/direction.py` must refuse a here-relative pointer AT WRITE TIME, and it cannot
    import the sweep. The sweep imports `site/live_pixel_verify.py`, which fetches from the live
    host, and `direction.py` is imported by `background/supervisor.py` -- the draw. Putting a
    network-fetching module in the draw's import chain to reach fourteen nouns is a worse defect
    than the one being fixed, and importing `pytest` into production is a second one.

So the vocabulary moved down to a module with no dependencies at all, and the sweep imports it
back. The alternative on offer was a second copy of the noun list in `background/`, which is
exactly the drift this vocabulary was consolidated to prevent: two copies would have meant the
write-time refusal and the published-feed sweep quietly judging different sets of sentences, and
the divergence would surface as one of them passing a page the other refused.

WHAT MAKES A SENTENCE A `HERE`-RELATIVE POINTER: it claims a direction and names nothing to take
the direction FROM, so its referent is wherever it happens to render. A producer does not know how
many homes its output has, so a sentence that says "here" is unverifiable at the point it is
written. See the sweep's module docstring for the 2026-09-08 defect this generalises.

THIS MODULE IS NOT IN THE PRODUCER CENSUS POPULATION and that is load-bearing, not luck.
`site/test_a_producers_here_relative_pointer_has_one_home.py` censuses `tools/generate_*.py` and
excludes docstrings, so the specimens quoted below cannot be mistaken for prose this site might
publish. Anything added here that is NOT a docstring must not quote a live pointer.
"""
from __future__ import annotations

import re

#: THE NOUN LIST WAS AUDITED BY MEASUREMENT, 2026-09-19, not by asking what a page is made of.
#: It had been the layout furniture a page is drawn with, and the site does not point that way.
#: `value_arms.json` publishes "20 paths of pricing code away from the RUN above" -- a pointer by
#: any reading, matching nothing here, and so invisible to the sweep and the three rungs that
#: import it. Sweeping every `<noun> above|below` in the published feeds and the producers' own
#: literals (16,083 strings) says the nouns this site actually points with are UNITS OF ITS OWN
#: RECORD -- a run, an entry, a finding, a mutation, a refusal -- and the furniture is the
#: minority. Half of what was here (`chart`, `list`, `box`, `card`) matches nothing published.
#:
#: AND THREE MEASURED CANDIDATES ARE DELIBERATELY NOT HERE, which is the half of the audit worth
#: keeping, because each reads like an obvious omission to whoever comes next:
#:   * `reading` -- "the highest READING BELOW the ceiling is 447" (`simplified.json`) is a
#:     threshold, not a place.
#:   * `line` -- "at least one LINE BELOW zero" (`knowledge_non_commodity_costs.json`) is a cost
#:     stack component going negative.
#:   * `range`/`interval` -- refused before, with its own measurement: see the docstring of
#:     `tests/tools/test_the_proof_pages_undriven_pointers.py`, which found "moves the INTERVAL
#:     ABOVE" and kept the phrase page-scoped in `_EXTRA_PHRASES` rather than widening this.
#: That is the standing rule for this list: a site-wide vocabulary that admits arithmetic starts
#: refusing arithmetic, so a noun earns its place by having NO comparison sense in the live
#: corpus -- measured, not assumed. A noun that only points on one page belongs in that page's
#: own `_EXTRA_PHRASES`.
#:
#: AND THE PARTICIPLE BRANCH HAD THE SAME HOLE, found the same day by a second lane and added
#: in the merge. `published` was missing from the nine beside it while "published above|below"
#: was live SEVEN times in `generate_value_arms_data.py` alone -- one of them, `_staleness_caveat`,
#: a genuine TWO-HOME pointer rendering in `/capabilities/#arms-errorbar` AND `#arms-headline`,
#: i.e. a live instance of the parent defect that all four sweeps passed. THE AUDIT ABOVE COULD
#: NOT HAVE FOUND IT: it censused `<noun> above|below`, and no census of that shape can return a
#: participle. That is the lesson worth more than either word -- an audit is blind along the axis
#: it was cut on, so the next one to run here should ask what SHAPE is unexamined before asking
#: which words are missing from the shapes already known.
HERE_RELATIVE = re.compile(
    r"(higher up|further up|further down|lower down|above this|below this|"
    r"(?:table|panel|chart|figure|row|block|section|list|column|note|box|card|band|"
    r"run|entry|item|record|claim|finding|mutation|refusal|check|measurement|"
    r"sentence|paragraph|summary)s? "
    r"(?:above|below)|"
    r"(?:shown|listed|set out|stated|named|given|described|printed|quoted|published) "
    r"(?:above|below)|"
    r"immediately (?:above|below)|directly (?:above|below)|earlier (?:in|on) this|"
    r"later (?:in|on) this|(?:top|foot|bottom|head) of this (?:page|section)|opposite this|"
    r"beside this|to the (?:left|right) of this|(?:above|below) on this page|"
    r"the (?:one|ones) (?:above|below))",
    re.I)

#: AND WHAT TAKES IT BACK OUT. A LANDMARK names the thing the direction is measured from, so the
#: claim is absolute: "under the headline figure" is true from anywhere on the page and cannot rot
#: into a lie by the sentence gaining a third home. That is the repair the parent finding made, so
#: the repaired wording must not be what any rule here reds on -- a rule that refuses the fix as
#: well as the defect gets the fix reverted.
LANDMARK = re.compile(
    r"((?:above|below|under|over) (?:this |the )?headline(?: figure)?|"
    r"under the headline|in the headline)", re.I)


def here_relative_phrases(sentence: str) -> list[str]:
    """EVERY registered `here`-relative phrase this sentence claims, in the order it claims them.

    `finditer`, NOT `search`, and the difference is a defect this vocabulary grew into. One
    sentence can point twice -- `_current_world_contrast` says "the figures above" and then "the
    run above it" in the same literal -- and a first-match reader registers the first, judges it,
    and reports a clean sentence while the second direction has never been asked about. That was
    survivable while the vocabulary was a handful of fixed phrases; with fourteen nouns and a
    participle branch, a second direction in one sentence is ordinary rather than exotic, so the
    narrow read is now the binding constraint on every rung that imports this census.

    A landmark anywhere in the sentence takes ALL of them out, which is the same rule as before and
    is deliberately not per-match: "the band table directly below this headline" names the headline
    it is below, and that makes the whole sentence a claim checkable once rather than per home.

    DE-DUPLICATED CASE-INSENSITIVELY, because the consumers key `_REFERENTS` on the lowered phrase.
    A sentence saying "the figures above" twice claims one direction, not two, and registering it
    twice would ask the same question twice and print the same defect twice.

    WHITESPACE IS COLLAPSED HERE rather than left to each caller, and that is the one behavioural
    change the rehoming made. The render-side callers normalise before they call and are unaffected
    -- collapsing an already-collapsed string is identity. The write-time caller reads AUTHORED
    prose off a YAML record, where "the run\\nabove" is an ordinary way for a line to wrap, and a
    pointer that survives a line break is still a pointer. Leaving it to the caller would have put
    a second, partial normal form in `background/`, which is how the two-copy drift starts.
    """
    sentence = re.sub(r"\s+", " ", sentence)
    if LANDMARK.search(sentence):
        return []
    found: list[str] = []
    seen: set[str] = set()
    for match in HERE_RELATIVE.finditer(sentence):
        phrase = match.group(0)
        if phrase.lower() not in seen:
            seen.add(phrase.lower())
            found.append(phrase)
    return found


def here_relative_phrase(sentence: str) -> str | None:
    """The FIRST registered `here`-relative phrase this sentence claims, or None if it claims none.

    DEFINED FROM THE PLURAL rather than beside it, so there is one landmark rule and one
    vocabulary. Kept because several callers ask a BOOLEAN of a sentence -- does this claim a
    direction at all -- and the answer to that does not change with how many it claims. A caller
    that judges the direction wants `here_relative_phrases`; this one cannot see a second.
    """
    phrases = here_relative_phrases(sentence)
    return phrases[0] if phrases else None
