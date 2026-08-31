"""The declared denominator for any reading taken off a captured departure table.

Opened by `docs/staging/WORKER_FINDING_C1B_ADDED_A_DEPARTURE_ROUTE_AND_EVERY_INSTRUMENT_MEASURING_DEPARTURES_KEPT_READING_THE_OLD_POPULATION_2026-08-31.md`.

WHAT WENT WRONG, BECAUSE THE SHAPE OF THE DEFECT IS THE SHAPE OF THIS MODULE. C1b (`067a00dfd`)
gave the world a second way to leave: an account on the standard variable product drifts off it at
a segment boundary, with no renewal decision and no rate struck. `tools/capture_departure_factors`
builds its table by wrapping `roll_lifecycle_event` -- the renewal decision -- so from that commit
the captured table stopped being the book and became the renewal-decision SUBSET of it. Measured on
a two-route capture: 144 renewal decisions against 1,266 SVT segment decisions, and 32 departures
by renewal against 50 off SVT. **The renewal table can see 39% of departures.**

**Nothing went red, and nothing could have.** The table kept its rows and every field populated; it
was the SCOPE of the population that moved, not its size, so the population floor that normally
catches this class did not fire. The C1b author wrote the debt down at the site, named both readers
and predicted the staleness -- and a named comment is not a control. It sat across a capture, a fit
and two published readings. This module is the repair the comment could not be: **a reading that
cannot be taken without naming the population it was taken on.**

WHY THIS IS NOT A UNION, AND THE REFUSAL IS DELIBERATE. An SVT segment decision carries no
`churn_probability`, no `sim_price_response` and no `sim_bill_shock_base` -- there was no renewal
for any of them to describe. Appending the two lists hands every existing reader rows of `None` and
lets a mean be taken across two populations, which is the failure this repository has already paid
for. So the two files stay two files, and what is shared is the DECLARATION: which routes a reading
can see, how many decisions and departures are in each, what share of the book's departures the
reading's own population accounts for, and which departure CAUSES are structurally unobservable on
it.

AN UNOBSERVABLE CAUSE IS `None` AND NEVER `0.0`, and that distinction is the whole reason
`causes_not_observable` exists. `simulation.departure_risks.build_departure_risks` defaults
`svt_inertia` to 0.0, so a cause-share decomposition run over renewal rows returns `svt_inertia:
0.0%` -- a number, well-formed, and read by anyone as "almost nobody leaves this way" when the
truth is "this population cannot contain anyone who left this way". That is the fail-open shape:
a missing quantity arriving as a small one.

Usage:
    from tools.departure_population import declare, banner
    decl = declare(table_path)
    print(banner(decl))
"""
from __future__ import annotations

import json
from pathlib import Path

from simulation.departure_risks import (
    CAUSE_BILL_SHOCK,
    CAUSE_DISSATISFACTION,
    CAUSE_PRICE_POSITION,
    CAUSE_SVT_INERTIA,
    ORDERED_CAUSES,
)

PROJECT = Path(__file__).resolve().parent.parent

#: The two ways an account leaves this world. `renewal` is the roll inside `roll_lifecycle_event`;
#: `svt_segment` is C1b's drift off the standard variable product at a segment boundary.
ROUTE_RENEWAL = "renewal"
ROUTE_SVT = "svt_segment"

#: `tools/capture_departure_factors` writes the SVT segment decisions to a SECOND file beside the
#: renewal table, named from its stem. Derived rather than passed, so a reader that opens the
#: renewal table cannot open it without this module being able to find its sibling.
SVT_SUFFIX = "_svt_segment_decisions.json"

#: Which departure causes each route's hazard can express. The renewal route composes the three
#: household families through `build_departure_risks`; the SVT route carries exactly one, and it is
#: the one `departure_risks` calls *"the single largest departure route in a real domestic book"*.
#:
#: Keyed to the CAUSE CONSTANTS and not to strings, so renaming a cause moves this with it rather
#: than leaving a declaration that quietly stops matching anything.
ROUTE_CAUSES: dict[str, tuple[str, ...]] = {
    ROUTE_RENEWAL: (CAUSE_BILL_SHOCK, CAUSE_PRICE_POSITION, CAUSE_DISSATISFACTION),
    ROUTE_SVT: (CAUSE_SVT_INERTIA,),
}

#: Said in one sentence wherever a reading is missing the SVT route, because the reader who needs
#: it is the one who did not go looking.
SVT_BLIND_WARNING = (
    "this reading CANNOT SEE the SVT inertia route (C1b). It is the renewal-decision population "
    "only, which is no longer the whole book, and the cause it cannot see is the one "
    "`departure_risks` calls the single largest departure route in a real domestic book."
)


def svt_sibling(table_path: Path | str) -> Path:
    """The SVT segment-decision file that belongs beside this renewal table."""
    p = Path(table_path)
    return p.with_name(p.stem + SVT_SUFFIX.removesuffix(".json") + p.suffix)


def _is_departure(row: dict) -> bool:
    """One definition of a departure across both routes.

    The two routes label the same outcome the same way -- `event_type == "churned"` -- and that is
    load-bearing enough to be stated once rather than re-derived at four call sites, each of which
    would be free to drift.
    """
    return row.get("event_type") == "churned"


def load_svt_decisions(table_path: Path | str) -> tuple[list[dict] | None, str | None]:
    """`(rows, unreadable_reason)` for the SVT sibling of a renewal table.

    `None` rows with a reason, never an empty list: **"nobody was on SVT" and "the recorder was
    never wired" produce the identical artefact** and a reader must not have to tell them apart by
    inference. An EMPTY sibling that exists is returned as an empty list AND carries its own
    reason, because that too is a claim a reading should be unable to make silently.
    """
    sib = svt_sibling(table_path)
    if not sib.is_file():
        return None, (
            f"no SVT segment-decision file beside this table ({sib.name}). Either the capture "
            f"predates C1b's `_svt_decisions` recorder or it was run against a tree without it."
        )
    try:
        rows = json.loads(sib.read_text())
    except (OSError, ValueError) as exc:
        return None, f"{sib.name} could not be read ({type(exc).__name__}: {exc})"
    if not rows:
        return [], (
            f"{sib.name} is EMPTY. That is not evidence nobody drifted off SVT -- an unwired "
            f"recorder produces the same file."
        )
    return rows, None


def declare_rows(
    renewal_rows: list[dict],
    svt_rows: list[dict] | None,
    *,
    table: str | None = None,
    svt_source: str | None = None,
    svt_unreadable: str | None = None,
) -> dict:
    """The population declaration for a reading over these rows. The core; `declare` is the wrapper.

    Split from the file-loading path because two of the four readers do not read a factor table at
    all: `tools/population_anchor._churn_by_year` takes `customer_events` and `svt_decisions`
    straight off a run output. A declaration that only knew how to open files would have left that
    reader with a hand-rolled second copy, which is how the VAT rule ended up with five.
    """
    covers_svt = svt_rows is not None
    renewal_departures = sum(1 for r in renewal_rows if _is_departure(r))
    svt_departures = sum(1 for r in svt_rows if _is_departure(r)) if covers_svt else None

    decisions = {ROUTE_RENEWAL: len(renewal_rows)}
    departures = {ROUTE_RENEWAL: renewal_departures}
    if covers_svt:
        decisions[ROUTE_SVT] = len(svt_rows)
        departures[ROUTE_SVT] = svt_departures

    total_departures = renewal_departures + (svt_departures or 0)
    observable = set(ROUTE_CAUSES[ROUTE_RENEWAL])
    if covers_svt:
        observable |= set(ROUTE_CAUSES[ROUTE_SVT])

    return {
        "table": table,
        "svt_source": svt_source,
        "routes_readable": sorted(decisions),
        "covers_svt_route": covers_svt,
        "decisions": decisions,
        "departures": departures,
        "total_departures_visible": total_departures,
        # `None` and not 1.0 when the SVT route is unreadable. The share of departures a
        # renewal-only reading can see is exactly the quantity that reading cannot compute: it has
        # no denominator for the route it cannot see, and reporting 100% would be the reading
        # certifying its own blind spot.
        "share_of_departures_visible": (
            (renewal_departures / total_departures) if covers_svt and total_departures else None
        ),
        "population": (
            "renewal decisions + SVT segment decisions" if covers_svt
            else "renewal decisions only"
        ),
        "causes_observable": [c for c in ORDERED_CAUSES if c in observable],
        "causes_not_observable": [c for c in ORDERED_CAUSES if c not in observable],
        "svt_unreadable_reason": svt_unreadable,
        "warning": None if covers_svt else SVT_BLIND_WARNING,
    }


def declare(table_path: Path | str, renewal_rows: list[dict] | None = None) -> dict:
    """The population declaration for a reading taken off a captured renewal factor table."""
    path = Path(table_path)
    rows = renewal_rows if renewal_rows is not None else json.loads(path.read_text())
    svt_rows, reason = load_svt_decisions(path)
    return declare_rows(
        rows,
        svt_rows,
        table=_rel(path),
        svt_source=_rel(svt_sibling(path)) if svt_rows is not None else None,
        svt_unreadable=reason,
    )


def _rel(path: Path) -> str:
    return str(path.relative_to(PROJECT)) if path.is_relative_to(PROJECT) else str(path)


def banner(decl: dict) -> str:
    """The lines every reader prints before its own numbers.

    Printed rather than kept as a caveat in a document, for the reason the finding gives: a verdict
    should be impossible to quote without the population it was taken on. The warning goes LAST so
    it is the line nearest the reader's eye when it fires.
    """
    lines = [f"population: {decl['population']}"]
    if decl.get("table"):
        lines.append(f"  renewal table: {decl['table']}")
    if decl.get("svt_source"):
        lines.append(f"  SVT decisions: {decl['svt_source']}")
    lines.append(
        f"  decisions: {decl['decisions']}   departures: {decl['departures']}"
    )
    share = decl["share_of_departures_visible"]
    if share is not None:
        lines.append(
            f"  this reading's own route accounts for {share:.0%} of the departures in the capture"
        )
    if decl["causes_not_observable"]:
        lines.append(
            f"  causes it CAN see: {', '.join(decl['causes_observable'])}"
            f"   ·   causes it CANNOT: {', '.join(decl['causes_not_observable'])}"
        )
    if decl.get("svt_unreadable_reason"):
        lines.append(f"  ⚠ {decl['svt_unreadable_reason']}")
    if decl.get("warning"):
        lines.append(f"  ⚠ {decl['warning']}")
    return "\n".join(lines)
