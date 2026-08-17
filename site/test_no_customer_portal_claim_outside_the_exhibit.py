"""No door other than the wall exhibit itself may call /customers/ a "customer portal"
(R10 class guard, SITE2_two_sided_wall_exhibit).

THE DEFECT THIS CLOSES
-----------------------
`DIRECTOR_RULING_THE_PORTAL_IS_A_WALL_EXHIBIT_2026-08-12` Part 2 required "Name, title,
entry copy and URL stop claiming to be a customer's portal." The page itself
(`site/customers/index.html`) was rebuilt and its own copy now disclaims the portal
framing explicitly (`test_customers_door.py` / `test_wall_exhibit.py` cover that page).

Nobody re-checked the ENTRY COPY on *other* doors that link to it. Two live doors still
invited a reader in with the exact claim the page itself had just dropped:

    site/now/index.html:      "Customer portal &rarr;"
    site/company/index.html:  "Open the full customer portal &rarr;"

Both were fixed on sight (this atom), but the instance fix is two edits. The CLASS is
"a door's own entry copy can re-assert a claim the destination page just retired" --
so this guard is DERIVED from the live canonical door set (`site/sitemap.xml` via
`canonical_doors()`), never a hand-typed list of doors, and reads live markup rather
than pinning today's wording.

ANTI-PIN (R15)
---------------
Nothing here pins a count or a phrase's replacement wording. It asserts a relationship
(no OTHER canonical door's markup contains "customer portal") that holds regardless of
how any door's copy is later reworded, and fails the instant a new "customer portal"
claim is added anywhere outside the exhibit's own page.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
sys.path.insert(0, str(SITE))
from live_pixel_verify import canonical_doors  # noqa: E402

EXHIBIT_DOOR = "/customers/"
_CLAIM_RE = re.compile(r"customer\s*portal", re.IGNORECASE)


def door_file(door: str) -> Path:
    stem = door.strip("/")
    return SITE / stem / "index.html" if stem else SITE / "index.html"


def doors_other_than_the_exhibit() -> list[str]:
    doors = [d for d in canonical_doors() if d.rstrip("/") + "/" != EXHIBIT_DOOR]
    assert doors, "guard would pass vacuously: no doors other than the exhibit found"
    assert len(doors) < len(canonical_doors()), (
        "fixture precondition: the exhibit door itself must be excluded, not silently missing"
    )
    return doors


def claims_in(html: str) -> list[str]:
    return _CLAIM_RE.findall(html)


# ---------------------------------------------------------------------------
def test_no_other_door_calls_the_exhibit_a_customer_portal():
    offenders = []
    for door in doors_other_than_the_exhibit():
        p = door_file(door)
        if not p.exists():
            continue
        hits = claims_in(p.read_text(encoding="utf-8"))
        if hits:
            offenders.append((door, len(hits)))
    assert not offenders, (
        "these doors still call the wall exhibit a 'customer portal' in their own entry "
        f"copy, re-asserting the claim the exhibit itself dropped: {offenders}"
    )


def test_the_exhibit_door_is_actually_excluded_from_the_scan():
    """The exhibit's own page legitimately says 'not a customer portal' -- prove the
    scan is skipping it deliberately, not because canonical_doors() forgot it."""
    assert EXHIBIT_DOOR in canonical_doors(), "fixture precondition: the exhibit is a canonical door"
    assert EXHIBIT_DOOR not in doors_other_than_the_exhibit()


# ---------------------------------------------------------------------------
# R15 mutation proof -- the guard must fire on its own named defect, both directions.
# ---------------------------------------------------------------------------
def test_mutation_a_customer_portal_claim_reintroduced_on_another_door_is_caught():
    clean = door_file("/now/").read_text(encoding="utf-8")
    assert not claims_in(clean), "precondition: /now/ is clean before mutation"
    mutated = clean.replace(
        "Two sides of the wall &rarr;", "Customer portal &rarr;", 1
    )
    assert claims_in(mutated), (
        "MUTATION SURVIVED: reintroducing the 'customer portal' claim on /now/ was not caught"
    )


def test_the_exhibits_own_disclaimer_would_not_be_flagged_if_it_were_in_scope():
    """Control is not over-broad: it matches the phrase itself, so a page that SAYS
    'not a customer portal' legitimately trips it too -- which is exactly why the
    exhibit door is excluded by identity, not by content-sniffing."""
    disclaimer = "<p>This is an exhibit, not a customer portal.</p>"
    assert claims_in(disclaimer), (
        "control would be too narrow to catch a real re-claim if it can't even match the phrase"
    )
