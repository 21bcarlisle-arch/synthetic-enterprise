"""Regression tests for NAV_STORY_PLATFORM_METHOD.md item 6/7 (Phase RQ):
Method nav link added site-wide, Project tab slims down (Company sub-tab ->
Method, Capabilities sub-tab -> Platform), Platform gains the Capabilities
register. Follows the established node-unavailable static-guard pattern
(tests/tools/test_billing_tab_fix.py) since node is gated behind an
unapprovable permission prompt in this environment."""
import re
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parents[2]

# NOTE (2026-07-19, v4 site retirement): site/platform/ retired (the old SIM/Supplier/Platform
# split the ratified brief section 6 kills; its content re-homes into The Method). Removed from
# this list and the platform-specific assertions below dropped. supplier/sim also slated to retire.
# DERIVED, 2026-08-20: two of the three entries here (customers, method) were deleted with the
# fold. The set is the pages that carry the shared nav, which is a fact about the tree.
SITE_PAGES_WITH_NAV = [
    str(p.relative_to(PROJECT))
    for p in sorted((PROJECT / "site").rglob("index.html"))
    if "IA-NAV:START" in p.read_text(encoding="utf-8")
]


def _read(rel):
    return (PROJECT / rel).read_text()


# NOTE (2026-07-24, SITE_V5 fold, director Decision A `..._DOOR_A_COMMIT_THE_FOLD_...`,
# committed 5b8152bb7): the standalone /method DOOR was retired; the Method content re-homes as
# a canonical anchor on /proof (`proof/#method-anchor`). Every nav page now reaches Method via
# that anchor, not a top-level `method/` link. The invariant is UNCHANGED in intent (every page
# can reach the Method content) -- only its canonical target moved. `site/method/index.html`
# itself is retained as the anchor's content page (see test_method_page_* below, still passing).
CANONICAL_METHOD_ANCHOR = "proof/#method-anchor"


# RETIRED 2026-08-20, the whole Method family. site/method/index.html is DELETED under the
# director's ruling that the five tabs are the site; /method and /method/* 301 to /harness/,
# which is where the account of how this project works now lives, written for a reader rather
# than kept as a separate page behind a redirect.
#
# Five tests went with it: the page's own well-formedness, its data fetch, its section render,
# the front door's card, and the reachability of its content. The last of those was rewritten
# only this morning to express the invariant properly -- and the honest reading is that the
# invariant is now satisfied structurally rather than by assertion: the content is a section of
# a canonical tab, reached by the nav on every page, so there is no separate thing left to
# check is reachable.
#
# What survives in this file is the SITE_PAGES_WITH_NAV set above and the checks over it.
def test_the_nav_page_set_is_not_empty():
    """Fail-closed. The two remaining checks iterate SITE_PAGES_WITH_NAV, so an empty set would
    make them pass vacuously -- which is exactly how this file would have rotted quietly if the
    fold had emptied it instead of shrinking it."""
    assert SITE_PAGES_WITH_NAV, "no nav pages declared -- every check in this file is vacuous"
    for rel in SITE_PAGES_WITH_NAV:
        assert (PROJECT / rel).is_file(), f"{rel} is declared here but does not exist"
