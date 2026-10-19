"""A knowledge page's headline figures, stated as claims and checked against the drawn world.

Director steer, 19 Oct 2026 (`docs/staging/advisor/DIRECTOR_STEER_KNOWLEDGE_THAT_CHECKS_THE_WORLD_2026-10-19.md`),
item 2: "A page's headline figures are stated as testable claims about the world or the book, with
their range and source." The single-fuel book was not a gap in knowledge. The page said ~75% dual
fuel and nothing compared the world with it, while the founder draw changed underneath it twice.

THE CLAIM LIVES ON THE PAGE, in a fenced block tagged `world-claims` (a YAML list of `id`,
`measure`, `band: [lo, hi]`, `source`). The page is the one home of the figure. A test band that
copies it is a second home that can drift. The bands are published ranges, widened by the
sampling noise of the pooled draw where the page says so. They are not the draw's own constants, so
moving a constant inside its range stays green and a book that leaves the record goes red.

THE MEASURES ARE HERE, one function per name, over each route into the book (`ROUTES`: the
founders at the production founder count, the trickle, the campaign's winners), pooled over
`SEEDS`. A route's known gap is named in `KNOWN_ROUTE_GAPS`. A claim naming a measure nobody wrote is refused by
name. That is a claim nobody can check, which is the state the 21 June figure sat in for three
months.

WHO RUNS IT. `tests/tools/test_world_claims.py` on every commit that touches a page in `PAGES`, this
module, or a module that decides who is in the world (item 3: `tools/pre_commit_test_gate.py`'s
`SUBJECT_TESTS`); the Monday step prints the table (`background/weekly_rhythm.py`); and
`python3 -m tools.world_claims` exits 1 on a gap.
"""
from __future__ import annotations

import collections
import os
import re
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent

#: The pages that describe the population and its behaviour and carry a `world-claims` block. The
#: steer: "Start with the pages that describe the population and its behaviour, not all 180."
PAGES = (
    "docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md",
    "docs/market_research/gb_payment_method_migration_rates.md",
)

#: Eight seeds pooled (~1,700 homes, ~3,000 accounts). Fewer cannot tell 85% gas homes from 90%.
SEEDS = (20260724, 61101, 61102, 61103, 61104, 61105, 61106, 61107)

_BLOCK = re.compile(r"^```world-claims[ \t]*\n(.*?)^```", re.M | re.S)


def claims(root: Path | None = None) -> list[dict]:
    """Every claim on every page in `PAGES`, each carrying the page it came from."""
    root = PROJECT if root is None else root
    out = []
    for page in PAGES:
        if not page.endswith(".md"):
            raise ValueError(f"{page}: a claim lives on a markdown knowledge page")
        text = (root / page).read_text(encoding="utf-8")
        for block in _BLOCK.findall(text):
            for row in yaml.safe_load(block) or []:
                out.append({**row, "page": page})
    return out


#: The three ways a home enters the book. `founders` is the opening portfolio; `trickle` is the
#: Profile-B arrival stream; `campaign` is the homes the growth campaign wins. Each is measured on
#: its own, because a claim that holds on the pool can fail on one route and be hidden by the others.
ROUTES = ("founders", "trickle", "campaign")


#: A claim that does not hold on one route, named rather than hidden, with the finding that carries
#: it. It may only SHRINK: `tests/tools/test_world_claims.py` reds when a route's gaps differ from
#: this, so fixing one forces its removal and a new one cannot appear unseen. The founders' route is
#: the gate and has no entry. The trickle is about 30 homes over the eight seeds, so a trickle verdict
#: is a coarse check, not a precise one.
KNOWN_ROUTE_GAPS = {
    ("campaign", "dual_share_of_gas_homes"):
        "docs/staging/SEAT_FINDING_THE_FUEL_CLAIMS_ARE_MEASURED_ON_THE_FOUNDERS_ONLY_AND_THE_"
        "CAMPAIGN_ROUTE_WINS_EVERY_GAS_HOME_DUAL_2026-10-19.md -- `_gas_leg_for` makes every won "
        "gas home dual (100.0%), so no campaign win is a split home",
}


def route_gaps(route: str, results: list[dict]) -> set:
    """The claim ids that do not hold on `route`, the set `KNOWN_ROUTE_GAPS` is compared with."""
    return {r["id"] for r in results if r["verdict"] != "holds"}


def _route_pairs(route: str, seed: int, lp) -> list:
    """`(record, premise)` for one route and seed, as the production book assembles it."""
    if route == "founders":
        return list(lp._drawn_founder_pairs(seed))
    if route == "trickle":
        return [(rec, sc.premise) for sc in lp._drawn_trickle(seed) for rec in lp._trickle_records(sc)]
    if route == "campaign":
        outcome = lp._campaign(lp._pre_growth_book(seed), seed)
        winners = {p.customer_id: p for p, _ in outcome["winners"]}
        return [(rec, winners[rec["customer_id"].rstrip("g")].premise)
                for rec in lp._won_customer_dicts(outcome)]
    raise ValueError(f"unknown route {route!r}; routes are {ROUTES}")


def drawn_book(seeds=SEEDS, route: str = "founders") -> list[tuple[dict, object]]:
    """`(record, premise)` pairs of one route into the book, pooled over `seeds`, with ids made
    unique per seed. Draws in-process (founders ~2 s a seed, trickle ~2 s, campaign ~4 s).

    The draw and growth flags are forced on for the call, so each route is the one a production
    run with both activated would assemble, whatever this process's environment says.
    """
    saved = {k: os.environ.get(k) for k in ("SE_DRAW_POPULATION", "SE_GROW_BOOK")}
    os.environ["SE_DRAW_POPULATION"] = "1"
    os.environ["SE_GROW_BOOK"] = "1"
    try:
        from simulation import live_population as lp

        pooled = []
        for seed in seeds:
            pooled += [({**r, "customer_id": f"{seed}:{r['customer_id']}"}, p)
                       for r, p in _route_pairs(route, seed, lp)]
        return pooled
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _homes(book) -> dict:
    """A home is its account id with the gas leg's trailing `g` dropped."""
    homes = collections.defaultdict(list)
    for record, premise in book:
        homes[record["customer_id"].rstrip("g")].append((record["commodity"], premise))
    return homes


def _share(hits, population) -> float | None:
    """A share, or None when there is nothing to take it of. An empty denominator is not 0%."""
    population = list(population)
    return sum(map(bool, (hits(x) for x in population))) / len(population) if population else None


def _fuels(legs) -> list:
    return sorted(f for f, _ in legs)


def _dual_share_of_homes(book) -> float | None:
    return _share(lambda v: _fuels(v) == ["electricity", "gas"], _homes(book).values())


def _dual_share_of_gas_homes(book) -> float | None:
    gas = [v for v in _homes(book).values() if getattr(v[0][1], "commodity", None) == "gas"]
    return _share(lambda v: _fuels(v) == ["electricity", "gas"], gas)


def _gas_home_share(book) -> float | None:
    return _share(lambda v: getattr(v[0][1], "commodity", None) == "gas", _homes(book).values())


def _gas_only_share_of_homes(book) -> float | None:
    return _share(lambda v: _fuels(v) == ["gas"], _homes(book).values())


def _gas_only_homes_without_gas(book) -> float | None:
    """A gas-only account is a split home's gas leg, so it sits on a home with a gas meter."""
    return _share(lambda v: _fuels(v) == ["gas"] and getattr(v[0][1], "commodity", None) != "gas",
                  _homes(book).values())


def _direct_debit_share_of_accounts(book) -> float | None:
    return _share(lambda pair: pair[0].get("payment_method") == "direct_debit", book)


MEASURES = {
    "dual_share_of_homes": _dual_share_of_homes,
    "dual_share_of_gas_homes": _dual_share_of_gas_homes,
    "gas_home_share": _gas_home_share,
    "gas_only_share_of_homes": _gas_only_share_of_homes,
    "gas_only_homes_without_gas": _gas_only_homes_without_gas,
    "direct_debit_share_of_accounts": _direct_debit_share_of_accounts,
}


def check(book, rows: list[dict] | None = None) -> list[dict]:
    """Each claim with its measured value and verdict: `holds`, `GAP` (outside the band) or
    `UNCHECKABLE` (a malformed claim, or a measure nobody wrote). The reason is always named."""
    rows = claims() if rows is None else rows
    out = []
    for c in rows:
        fn = MEASURES.get(c.get("measure"))
        band = c.get("band")
        if fn is None or not (isinstance(band, list) and len(band) == 2):
            why = (f"no measure named {c.get('measure')!r} in tools/world_claims.MEASURES"
                   if fn is None else f"band {band!r} is not [lo, hi]")
            out.append({**c, "value": None, "verdict": "UNCHECKABLE", "why": why})
            continue
        value = fn(book)
        if value is None:
            out.append({**c, "value": None, "verdict": "UNCHECKABLE",
                        "why": f"the book holds nothing for {c['measure']} to take a share of"})
            continue
        lo, hi = band
        ok = lo <= value <= hi
        out.append({**c, "value": value, "verdict": "holds" if ok else "GAP",
                    "why": "" if ok else f"{value:.1%} outside [{lo:.1%}, {hi:.1%}]"})
    return out


def failures(results: list[dict]) -> list[str]:
    return [f"{r['page']} :: {r['id']}: {r['verdict']} -- {r['why']}"
            for r in results if r["verdict"] != "holds"]


def render(results: list[dict]) -> str:
    """The table the Monday step prints: red first, each row naming its page and source."""
    order = {"UNCHECKABLE": 0, "GAP": 1, "holds": 2}
    lines = ["| claim | measured | band | verdict | page | source |", "|---|---|---|---|---|---|"]
    for r in sorted(results, key=lambda r: order[r["verdict"]]):
        value = "—" if r["value"] is None else f"{r['value']:.1%}"
        band = r.get("band")
        band = f"{band[0]:.1%}–{band[1]:.1%}" if isinstance(band, list) and len(band) == 2 else "—"
        verdict = r["verdict"] if r["verdict"] == "holds" else f"**{r['verdict']}** {r['why']}"
        lines.append(f"| `{r['id']}` | {value} | {band} | {verdict} | `{r['page']}` | "
                     f"{r.get('source', '')} |")
    return "\n".join(lines)


def _main() -> int:  # pragma: no cover - operator surface
    rc = 0
    for route in ROUTES:
        results = check(drawn_book(route=route))
        print(f"\n### {route}\n")
        print(render(results))
        known = {cid for (r, cid) in KNOWN_ROUTE_GAPS if r == route}
        new = route_gaps(route, results) - known
        print(f"\n{len(results)} claim(s); {len(route_gaps(route, results))} not holding, "
              f"{len(new)} not in KNOWN_ROUTE_GAPS")
        rc = 1 if new else rc
    return rc


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
