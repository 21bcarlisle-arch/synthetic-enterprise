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


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE UNION, AND WHY IT IS AN ACCOUNT DENOMINATOR AND NOT A BIGGER DECISION COUNT
# ─────────────────────────────────────────────────────────────────────────────────────────────
# The module note above says the two FILES stay two files, and they do -- an SVT decision still
# carries no `sim_price_response` and no mean may be taken across the two. What is unioned here is
# not the rows: it is the DEPARTURES, over a denominator that is neither route's.
#
# Both routes' natural denominators are wrong for the published band, and wrong in opposite
# directions. A renewal-decision denominator counts only households at a decision point, so it
# reads about a third high. An SVT-segment denominator counts cap periods -- roughly eleven per
# account-year on the 2026-08-31 capture -- so it reads an order of magnitude low. The published
# record's denominator is neither: `gb_domestic_switching_rate.json` counts external changes of
# supplier on a domestic electricity MPAN over ALL domestic electricity accounts.
#
# So the union's denominator is ACCOUNTS, and that is the entire reason the union is a repair
# rather than simply a larger number. It is the first denominator in this area that has the same
# shape as the record's.

#: The three properties a capture must have before an ACCOUNT denominator can be read off it, each
#: CHECKED rather than assumed by `account_denominator_refusal`. They held on the two-route capture
#: measured 2026-08-31 (131 accounts, 82 departures) -- but they are properties of the world's
#: departure mechanics, not of that file, and a world where an account can re-join and leave again
#: would break the first two silently while leaving every row well-formed.
ACCOUNT_DENOMINATOR_PROPERTIES = (
    "a departure is terminal: no account departs twice",
    "a departed account takes no further decision on either route",
    "an account on the book is visible every year: no unobserved interior account-year",
)


def _year(row: dict) -> int:
    return int(str(row.get("event_date", "0000"))[:4])


def account_denominator_refusal(
    renewal_rows: list[dict], svt_rows: list[dict] | None
) -> str | None:
    """Why these two routes cannot be read on an account denominator, or `None` if they can.

    A REFUSAL AND NOT A CAVEAT, because every one of the three properties is what makes the
    denominator MEAN something and each fails silently. If an account could depart twice, the
    numerator would count events while the denominator counted accounts, and the ratio would not be
    a quantity -- the class CLAUDE.md names as this project's commonest way to publish something
    misleading. If an account could sit on the book unobserved for a year, the denominator would be
    the accounts that happened to make a decision, which is the selected sub-population this whole
    repair exists to stop being compared against a whole-population rate.

    The interior-gap check is deliberately INTERIOR only. An account absent before its first
    decision or after its last has joined or left, which is the book changing size and not the
    instrument going blind; an account absent BETWEEN two of its own decisions is the instrument
    going blind, and nothing else produces that shape.
    """
    if svt_rows is None:
        return (
            "the SVT route is unreadable, so a whole-book count cannot be taken at all. "
            + SVT_BLIND_WARNING
        )
    departed_year: dict[str, int] = {}
    seen: dict[str, set[int]] = {}
    twice: list[str] = []
    unidentified = 0
    for row in list(renewal_rows) + list(svt_rows):
        acct = row.get("customer_id")
        year = _year(row)
        # A ROW WITHOUT AN ACCOUNT IS REFUSED, NOT SKIPPED, and the first draft skipped it. That
        # skip made the check FAIL-OPEN on precisely the rows that make the denominator
        # uncheckable: with no identifier there is no way to know whether an account departed
        # twice or was invisible for a year, so the three properties below were being certified
        # over the rows that could not violate them. Counted here and refused after the loop.
        if acct is None:
            unidentified += 1
            continue
        if year == 0:
            continue
        seen.setdefault(acct, set()).add(year)
        if _is_departure(row):
            if acct in departed_year:
                twice.append(acct)
            departed_year[acct] = min(departed_year.get(acct, year), year)
    if unidentified:
        return (
            f"{unidentified} decision(s) carry no `customer_id`, so they cannot be attributed to "
            f"an account. An account denominator cannot be counted from rows that do not name "
            f"their account, and the three properties below cannot be checked on them either."
        )
    if twice:
        return (
            f"{len(twice)} account(s) depart more than once in this capture (e.g. {twice[0]}). "
            f"A departure is not terminal here, so a departure COUNT is not an account count and "
            f"dividing one by the other does not give a rate comparable to the published record."
        )
    after = [a for a, y in departed_year.items() if any(v > y for v in seen[a])]
    if after:
        return (
            f"{len(after)} account(s) take a decision in a year AFTER the year they departed "
            f"(e.g. {after[0]}). Either departure is not terminal or the two routes disagree about "
            f"when an account left; a whole-book rate cannot be read until which is established."
        )
    gaps = [
        (a, y) for a, years in seen.items()
        for y in range(min(years), max(years) + 1) if y not in years
    ]
    if gaps:
        return (
            f"{len(gaps)} unobserved interior account-year(s) (e.g. {gaps[0][0]} is absent from "
            f"both routes in {gaps[0][1]} while present either side). The denominator would be the "
            f"accounts that happened to make a decision, which is the selected sub-population this "
            f"reading exists to stop being compared against a whole-population rate."
        )
    return None


def union_by_year(renewal_rows: list[dict], svt_rows: list[dict] | None) -> dict[int, dict]:
    """`{year: whole-book departure reading}` over the ACCOUNT denominator. Fails closed.

    Raises rather than returning a partial answer when `account_denominator_refusal` names a cause:
    a whole-book rate is the figure a reader will quote, and there is no shape of caveat that
    survives being quoted. Callers that want to degrade to a renewal-only reading ask the refusal
    first.

    Two rates per year, and they are different quantities:

      `realised_rate_pct`   departures that HAPPENED over accounts on the book. One draw of a
                            binomial on ~50 accounts, so a year of it carries about 5pp of
                            sampling noise and a single year inside or outside a band says little.
      `expected_rate_pct`   the sum of every decision's own `realized_churn_probability` over the
                            same accounts -- the world's departure LEVEL rather than its roll. This
                            is the quantity a level anchor is fitted onto and the one the published
                            band should be read against, because the band is a population rate and
                            not one country's coin flip.

    `expected_rate_pct` is model-free: it adds up probabilities the world already recorded on each
    row, so it cannot disagree with the run by being a reimplementation of it.
    """
    refusal = account_denominator_refusal(renewal_rows, svt_rows)
    if refusal is not None:
        raise ValueError(f"no account denominator is available for this capture: {refusal}")
    per_year: dict[int, dict] = {}
    for route, rows in ((ROUTE_RENEWAL, renewal_rows), (ROUTE_SVT, svt_rows)):
        for row in rows:
            year = _year(row)
            if year == 0:
                continue
            slot = per_year.setdefault(year, {
                "accounts": set(),
                "decisions": {ROUTE_RENEWAL: 0, ROUTE_SVT: 0},
                "departures": {ROUTE_RENEWAL: 0, ROUTE_SVT: 0},
                "expected_departures": 0.0,
                "unpriced_decisions": 0,
            })
            slot["accounts"].add(row["customer_id"])
            slot["decisions"][route] += 1
            if _is_departure(row):
                slot["departures"][route] += 1
            p = row.get("realized_churn_probability")
            # A DECISION WITHOUT ITS PROBABILITY IS COUNTED, NOT SKIPPED. Skipping it would shrink
            # the expected NUMERATOR while leaving the account DENOMINATOR whole -- a full
            # denominator with an emptied numerator, which reads as a world that departs less
            # rather than as a capture that recorded less. So the year keeps the count and
            # `expected_rate_pct` goes `None` below: an honest absence, which cannot be mistaken
            # for a measurement the way a quietly-low rate can.
            if p is None:
                slot["unpriced_decisions"] += 1
            else:
                slot["expected_departures"] += float(p)
    span = sorted(per_year)
    out: dict[int, dict] = {}
    for year, slot in sorted(per_year.items()):
        accounts = len(slot["accounts"])
        departures = sum(slot["departures"].values())
        out[year] = {
            "year": year,
            "accounts": accounts,
            "decisions": dict(slot["decisions"]),
            "departures": dict(slot["departures"]),
            "departures_total": departures,
            "expected_departures": round(slot["expected_departures"], 4),
            "unpriced_decisions": slot["unpriced_decisions"],
            "realised_rate_pct": round(100.0 * departures / accounts, 4) if accounts else None,
            "expected_rate_pct": (
                round(100.0 * slot["expected_departures"] / accounts, 4)
                if accounts and not slot["unpriced_decisions"] else None
            ),
            "denominator": "accounts with at least one decision on either route in the year",
            # THE CAPTURE'S OWN EDGES, and they are not a rate's business to hide. An account's
            # exposure in the first and last year of the capture is a fraction of a year, so a
            # rate over a full-year account count reads LOW there. Flagged per year rather than
            # excluded by a hand-written year range, because the range would be a fact about the
            # 2026-08-31 run and this is a fact about any capture.
            "partial_year": year in (span[0], span[-1]),
        }
    return out


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
