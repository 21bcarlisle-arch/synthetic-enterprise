"""THE READER-SIDE HALF of the deployment door: the sentence is not just composed, it is READ.

`test_the_deployment_reading_reaches_the_reader.py` beside this file grades what the page's own
`renderDeployment` writes into `#deployment`, running it under node's `vm`. Its six legs are good
legs and this file does not repeat one of them. What it cannot do is say whether a person with a
browser meets any of it, and on 2026-09-17 that gap was measured rather than argued -- three
constructed breakages of THIS page, each leaving a reader looking at nothing, passed all six
(`docs/design/WHAT_THE_VM_DOORS_GRADE.md`):

  A  a `#deployment { display: none }` rule in the page's own `<style>`  -- vm parses no CSS
  B  a SECOND inline `<script>` clearing the section                     -- vm reads only the FIRST
  C  the container renamed to `#deployment-panel` in the markup          -- vm MINTS any id asked of it

C is the one that sets the bar. In chromium those bytes killed four sections, published the
sentence "The record behind this page could not be loaded, so no figures are shown" -- which is
false, the feed loaded perfectly -- and raised NO error anywhere, because `$("deployment")` returned
null inside a `.then()` whose `.catch()` swallowed the TypeError. Every committed control was green.

Each leg below names which of those it catches. The subject is the PUBLISHED (index) copy of the
site, served over http -- see `site/test_the_browser_reading.py` for why that, and not the file on
disk, is the only subject that separates "the reader can see this" from "someone in this tree has
fixed it and not landed it". (The vm door beside this one still takes `_HERE / "index.html"`, the
working-tree copy, and so cannot make that separation at all. That is a real gap in that file and
it is recorded in the staging result rather than fixed here, because it belongs to that door.)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
SITE = _HERE.parent
# The same insertion `site/capabilities/test_capabilities_door.py` makes, for the same reason:
# pytest's prepend import mode puts only the TEST FILE'S OWN directory on `sys.path`, so a test in
# `site/harness/` cannot import a module in `site/`. Relying on a sibling suite having been
# collected first would make this import order-dependent, which is a fail-silent waiting to happen.
if str(SITE) not in sys.path:
    sys.path.insert(0, str(SITE))

from test_the_browser_reading import (  # noqa: E402  (must follow the sys.path insertion above)
    assert_visible_reading,
    browser_available,
    published_site_server,
    read_in_browser,
)

_PAGE = "/harness/index.html"


@pytest.fixture(scope="module")
def reading():
    """One browser launch and one server for the whole module -- a chromium start is ~1s and the
    legs below ask about the same page load, so paying it per-test would buy nothing."""
    why = browser_available()
    if why:
        pytest.skip(why)
    with published_site_server() as base:
        yield read_in_browser(
            base + _PAGE, "deployment", "stamp", "corrections", "control-kpis"
        )


def test_the_deployment_section_is_visible_to_a_reader(reading):
    """CATCHES A AND C. The vm door proves the sentence was composed; this proves someone can read
    it. MUTATION (run 2026-09-17): adding `#deployment{display:none}` to the page's `<style>` reds
    this and nothing else in the tree; renaming the container reds it on the `exists` clause."""
    assert_visible_reading(reading, "deployment")


def test_the_visible_section_carries_the_count_a_reader_would_quote(reading):
    """The join between the two halves. The vm door asserts the headline is in the innerHTML it
    captured; this asserts the SAME sentence is in what the layout engine says is shown -- which is
    the only version of the claim that mentions a reader.

    Keyed to the SHAPE, not to today's answer: pinning "All 11 observed daemons..." would go red
    the day a daemon legitimately falls behind, which is exactly backwards (CLAUDE.md: key a
    control to the property, not to today's answer)."""
    el = assert_visible_reading(reading, "deployment")
    text = el["text"]
    assert "observed daemons are running" in text, (
        f"the visible section does not carry the headline reading at all; it reads {text[:200]!r}"
    )
    assert "running age" in text.lower() and "loaded-code age" in text.lower(), (
        "the visible table does not offer both ages, which is the whole instruction"
    )


def test_the_page_does_not_publish_a_failure_it_did_not_have(reading):
    """CATCHES C'S QUIETEST CONSEQUENCE, and the one no control anywhere could see. A throw inside
    the `fetch(...).then(...)` chain is caught by a `.catch()` that writes "The record behind this
    page could not be loaded" into `#stamp` and abandons every render after the one that threw. So
    the page states a load failure that did not happen, and three further sections go empty, in
    silence.

    This leg fires on that whole class -- any exception in that chain, from any cause, not just the
    renamed container that found it."""
    stamp = reading["elements"].get("stamp")
    assert stamp and stamp.get("exists"), "the page has no #stamp, so this reading has no subject"
    assert "could not be loaded" not in stamp["text"], (
        "the page tells the reader its own record could not be loaded. Either that is true -- in "
        "which case this door's feed is broken -- or a render threw and the .catch() published a "
        f"failure the page did not have. #stamp reads {stamp['text'][:200]!r}"
    )
    # THE TEETH: prove the renders that run AFTER renderDeployment in the same callback actually
    # ran. Without this the leg above passes on a page where the chain died before reaching them.
    for later in ("corrections", "control-kpis"):
        el = reading["elements"].get(later)
        assert el and el.get("exists"), f"#{later} is absent from the published page"
        assert el["innerLength"] > 0, (
            f"#{later} rendered nothing. It is filled by the same callback as #deployment and "
            "AFTER it, so an empty one is the signature of that callback having thrown part-way"
        )
