"""A module-level scalar that equals a row of a published series is a copy of that series.

REUSE: tools/published_row_scalar_census.py
CLASS: CUSTOM
INDEX: searched "census", "constant", "origin", "published", "commons", "artefact", "rate table".
       Three neighbours, and this is none of them.
       * `tests/architecture/test_year_keyed_rate_table_census.py` discovers year-keyed DICTS and
         asks whether each agrees with the published band. Its own comment at the head of
         `_MUST_NOT_BE_LITERALS_CM` says what it cannot see, in as many words: "This census
         discovers year-keyed DICTS, so a single-value copy of one row of a published series is
         invisible to it -- and that copy was the one doing damage, at GBP930/household/year."
         This is that hole, and nothing else.
       * `tools/domain_constant_origins.py` asks whether a constant DECLARES an origin. It is
         keyed to the NAME (the director's five words, plus their unit spellings). A scalar copy
         of a published row can declare an origin perfectly well and still be a stale copy, and a
         copy named nothing like a rate is out of its scope entirely. Origin-declared and
         value-matches-a-published-row are independent questions.
       * `tools/commons_citation_supports_provenance.py` grades a citation against the commons
         artefact it names. It needs the citation to exist. The subject here is the constant that
         names nothing.

WHY IT EXISTS
-------------
`company/market/flexibility_potential._CAPACITY_MARKET_GBP_PER_KW_YR = 75.0` was a scalar copy of
one row of the published Capacity Market auction record. It was the third home of that price, it
disagreed with the other two, and it was doing GBP 930 per household per year of damage. It was
found by a human reading the file. Every census in this repo was blind to it:

  * the year-keyed census, because a scalar is not a dict;
  * the origins ratchet, because it was a question about the NAME, not the VALUE;
  * the citation-provenance check, because there was no citation to grade.

The hole is not "we missed one". The hole is **discovery narrower than the thing it governs, in a
dimension nobody had named** -- and the dimension is the VALUE. This pass names it: walk every
module-level number in the company's own code, walk every number the commons publishes, and say
which ones are the same number.

WHAT A HIT IS AND IS NOT
------------------------
A hit is NOT a defect. It is a QUESTION, and there are exactly three honest answers:

  * **SOURCED** -- the constant is meant to be that published row, and it should LOAD it rather
    than copy it. The copy comes out.
  * **REFUSED** -- the collision is coincidence. Two numbers can be equal without being the same
    quantity, and saying so with a named reason is a result. `0.05` is the reduced rate of VAT
    and it is also five percent of anything.
  * **DELETED** -- the constant should not exist.

The census reports the population. It does not decide. Deciding is a reading and each lane owns
its own -- which is the same rule the commons artefacts state about themselves.

WHAT IT DELIBERATELY CANNOT SEE, so nobody reads a zero as "there are none"
--------------------------------------------------------------------------
  * **Prose.** Only `*.json` under the commons is walked. Three commons artefacts are Markdown
    (`price_cap_ebit_allowance.md`, `pricing_differentiation_permissions.md`,
    `psr_eligibility_and_disconnection_protection.md`) and any series in them is invisible here.
    Extracting numbers from prose would invent rows the publisher never keyed.
  * **A value computed at import.** `_X = 75.0 * 0.92` is not a Constant node and is not matched.
    The de-rating multiply that hid the third CM home for months is exactly this shape, so this
    is a real bound and not a hypothetical one.
  * **A number the commons does not carry.** The commons holds 9 JSON artefacts. A copy of a
    published series that was never brought into the commons cannot collide with anything.

Run:  python3 -m tools.published_row_scalar_census [--list] [--scaled] [--json]
"""
from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
COMMONS = PROJECT / "docs" / "domain_artefact_library"

#: All three packages that hold the company's own numbers. `simulation/` is IN, unlike
#: `domain_constant_origins.SCOPE`, and for a reason that is specific to this question: that
#: ratchet asks whether a number declares an origin, and the world's numbers answer to the
#: baseline/curriculum split instead. This asks whether a number IS a published row, and the
#: world is exactly as capable of holding a stale copy of one as the company is.
SCOPE = ("company", "saas", "simulation")

#: A number that carries no information about its own provenance. `0` and `1` are arithmetic;
#: `-1` is a sentinel. Matching them would report every artefact against every module and the
#: census would be noise rather than a population.
TRIVIAL = frozenset({0.0, 1.0, -1.0})

#: A calendar year is a KEY wearing a value's clothes. Both sides are filtered: a published leaf
#: of 2022 is the year the row is about, and a constant of 2022 is a year the code is about.
#: Reporting `_FIRST_MODELLED_YEAR = 2016` against ten artefacts that each key a row on 2016 is
#: the pure form of a census that measures itself.
YEAR_LO, YEAR_HI = 1900, 2100

#: Published leaves under these key segments are bookkeeping, not series rows: the artefact's own
#: schema version, the count of things in it, and the year keys themselves.
NON_ROW_KEYS = frozenset({"version", "artefact_version", "schema_version"})

#: Unit conversions between the unit a publisher states and the unit a model tabulates. The
#: commons artefacts say this is where the danger is -- `ccl_main_rates.json` publishes GBP/kWh
#: and records that "consumers convert: GBP/kWh x 1000 = GBP/MWh". A scalar copy carrying the
#: converted number is the same defect as one carrying the published number, and a census that
#: only matched the published spelling would be narrow in exactly the way this file exists to
#: stop. Reported SEPARATELY, because a scaled match is weaker evidence than an exact one.
SCALES = (1000.0, 100.0, 10.0, 0.1, 0.01, 0.001)


@dataclass(frozen=True)
class Published:
    """One numeric leaf of one commons artefact -- a row of a published series."""

    artefact: str
    pointer: str
    value: float


@dataclass(frozen=True)
class Constant:
    """One module-level number in the company's own code."""

    module: str
    name: str
    lineno: int
    value: float
    shape: str  # SCALAR, or the container path that holds it


@dataclass(frozen=True)
class Hit:
    constant: Constant
    published: Published
    scale: float  # 1.0 for an exact match; the factor the constant was divided by otherwise


def _numeric(node: ast.AST) -> float | None:
    """The value of a numeric literal, including a negated one. Bools are not numbers here."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            return None
        if isinstance(node.value, (int, float)):
            return float(node.value)
        return None
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _numeric(node.operand)
        return None if inner is None else -inner
    return None


def _is_year(value: float) -> bool:
    return value.is_integer() and YEAR_LO <= value <= YEAR_HI


def _interesting(value: float) -> bool:
    """Does this number carry enough of itself to make a collision mean anything?"""
    return value not in TRIVIAL and not _is_year(value) and abs(value) > 1e-9


def published_rows(root: Path = COMMONS) -> list[Published]:
    """Every numeric leaf of every JSON artefact in the commons, with the pointer that found it."""
    rows: list[Published] = []
    for path in sorted(root.rglob("*.json")):
        artefact = str(path.relative_to(root))
        try:
            payload = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue

        def walk(node: object, pointer: str) -> None:
            if isinstance(node, dict):
                for key, child in node.items():
                    if key in NON_ROW_KEYS:
                        continue
                    walk(child, f"{pointer}/{key}")
            elif isinstance(node, list):
                for index, child in enumerate(node):
                    walk(child, f"{pointer}/{index}")
            elif isinstance(node, bool):
                return
            elif isinstance(node, (int, float)):
                if _interesting(float(node)):
                    rows.append(Published(artefact, pointer.lstrip("/"), float(node)))

        walk(payload, "")
    return rows


def _constants_from_value(
    module: str, name: str, lineno: int, value: ast.AST, container: str
) -> list[Constant]:
    """Numbers under one module-level binding: the scalar itself, or those inside a literal."""
    number = _numeric(value)
    if number is not None:
        return [Constant(module, name, lineno, number, container or "SCALAR")]

    found: list[Constant] = []
    if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
        for index, item in enumerate(value.elts):
            found += _constants_from_value(module, name, lineno, item, f"{container}[{index}]")
    elif isinstance(value, ast.Dict):
        for key, item in zip(value.keys, value.values):
            label = ast.unparse(key) if key is not None else "**"
            found += _constants_from_value(module, name, lineno, item, f"{container}[{label}]")
    return found


def module_constants(packages: tuple[str, ...] = SCOPE) -> list[Constant]:
    """Every module-level number bound to a name in the packages in scope."""
    constants: list[Constant] = []
    for package in packages:
        for path in sorted((PROJECT / package).rglob("*.py")):
            module = str(path.relative_to(PROJECT))
            try:
                tree = ast.parse(path.read_text())
            except SyntaxError:
                continue
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
                    value = node.value
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    targets = [node.target.id]
                    value = node.value
                else:
                    continue
                if value is None:
                    continue
                for target in targets:
                    constants += _constants_from_value(module, target, node.lineno, value, "")
    return [c for c in constants if _interesting(c.value)]


#: Agreement to three significant figures. A copy transcribed to fewer places than the publisher
#: stated -- `0.006948` written down as `0.00695` -- is 2.9e-4 away and is a copy. `3.0` against a
#: published `3.2` is 6.7e-2 away and is a different number.
ROUNDING_REL_TOL = 1e-3


def _within_rounding(candidate: float, published: float) -> bool:
    """Do the two agree to three significant figures?

    TWO DRAFTS OF THIS WERE WRONG AND THE CENSUS CAUGHT BOTH, which is the whole argument for
    running the pass before writing a control over it.

    The first read "within rounding" as half a unit in the last DECIMAL place of the published
    row. A row published as the integer `15` then admitted every constant in [14.5, 15.5], and
    that one row accounted for 4,356 of 14,769 hits.

    The second compared at whichever side claimed fewer decimal places. That is the same defect
    mirrored: a constant written `3.0` claims none, so it matched every published row in
    [2.5, 3.5], and the population went UP to 63,653.

    Decimal places were the wrong dimension both times. What a rounded copy preserves is
    SIGNIFICANT FIGURES -- rounding `0.006948` to `0.00695` keeps three, and no amount of
    rounding turns `3.2` into `3.0` while keeping three. So the comparison is relative, and the
    two failed drafts are recorded here rather than deleted because the shape they share --
    reaching for the absolute dimension when the quantity is relative -- is the one that will be
    reached for again.
    """
    return abs(candidate - published) <= abs(published) * ROUNDING_REL_TOL


#: Unit words, as a publisher's key spells them and as a constant's name spells them, mapped onto
#: the quantity they name. Deliberately small: a token that is not here contributes NOTHING, so an
#: unrecognised spelling makes a pair UNRANKED rather than silently AGREEING. Fail closed.
_UNIT_WORDS = {
    "gbp": "GBP", "pounds": "GBP", "p": "PENCE", "pence": "PENCE",
    "kwh": "KWH", "mwh": "MWH", "kw": "KW", "mw": "MW", "therms": "THERM",
    "day": "DAY", "days": "DAY", "year": "YEAR", "years": "YEAR", "yr": "YEAR",
    "month": "MONTH", "months": "MONTH", "pct": "PCT", "percent": "PCT",
    "share": "SHARE", "fraction": "SHARE", "ratio": "RATIO", "prob": "PROB",
    "probability": "PROB", "roc": "ROC", "tonne": "TONNE", "millions": "MILLIONS",
}
_WORD = re.compile(r"[A-Za-z]+")


def unit_signature(text: str) -> frozenset[str]:
    """What this name says its number COUNTS -- empty when it does not say."""
    return frozenset(
        _UNIT_WORDS[word]
        for word in (match.lower() for match in _WORD.findall(text))
        if word in _UNIT_WORDS
    )


def specificity(value: float, rows: list[Published]) -> int:
    """How many distinct published rows this VALUE collides with, across the whole commons.

    THIS, NOT PRECISION, IS WHAT MAKES A COLLISION EVIDENCE, and the poison round is what settled
    it. `_CAPACITY_MARKET_GBP_PER_KW_YR = 75.0` collides with exactly ONE row in the entire
    commons -- `capacity_market_auction_results#clearing_prices/6/t1_gbp_per_kw_year`. A value of
    `0.9` collides with dozens. The first is a fingerprint; the second is a number people like.

    A SIGNIFICANT-FIGURES RANK WAS TRIED FIRST AND WOULD HAVE BURIED THE CASE THIS FILE EXISTS
    FOR. `75.0` carries two significant figures, so any floor at three hides it -- the census
    would have been narrower than the thing it governs, in a new dimension, which is the exact
    defect being closed. Specificity has no such floor: it ranks the damage case top.
    """
    return sum(1 for row in rows if _within_rounding(value, row.value))


def census(
    constants: list[Constant] | None = None, rows: list[Published] | None = None
) -> list[Hit]:
    """Every module-level number that is, within rounding, a row of a published series."""
    constants = module_constants() if constants is None else constants
    rows = published_rows() if rows is None else rows
    hits: list[Hit] = []
    for constant in constants:
        for row in rows:
            if _within_rounding(constant.value, row.value):
                hits.append(Hit(constant, row, 1.0))
                continue
            for scale in SCALES:
                if _within_rounding(constant.value / scale, row.value):
                    hits.append(Hit(constant, row, scale))
                    break
    return hits


def units_agree(hit: Hit) -> bool:
    """Do the constant and the published row say they count the SAME thing?

    A number is not a quantity. `_MINUTES_RETENTION_YEARS = 10` collides with a published
    `awarded_cmu_years = 10` and the two have nothing to do with each other; `SME_GAS_THRESHOLD_
    KWH_PER_DAY = 145` collides with a published `kwh_per_day = 145` and they are the same law.
    Both are specificity-1 collisions and only the second is a finding, so specificity alone does
    not rank far enough. This is CLAUDE.md's "before dividing two numbers, say out loud what each
    one counts", applied to comparing them.

    REPORTED, NOT FILTERED, and the difference matters. A pair where either side names no unit is
    UNRANKED, not excluded -- `_CAPACITY_MARKET_GBP_PER_KW_YR` against `t1_gbp_per_kw_year` agrees
    here, but a copy named `_X = 75.0` would name nothing and must still reach the reader. Hiding
    the unnamed half is how a census stops being a census.
    """
    left = unit_signature(hit.constant.name)
    right = unit_signature(hit.published.pointer.split("/")[-1])
    return bool(left) and left == right


def _render(hits: list[Hit], rows: list[Published]) -> str:
    lines = []
    ranked = sorted(
        hits,
        key=lambda h: (
            not units_agree(h),
            specificity(h.constant.value, rows),
            h.constant.module,
            h.constant.lineno,
        ),
    )
    for hit in ranked:
        c, p = hit.constant, hit.published
        how = "EXACT" if hit.scale == 1.0 else f"x{hit.scale:g}"
        flag = "UNITS-AGREE" if units_agree(hit) else "unranked  "
        lines.append(
            f"{flag} spec={specificity(c.value, rows):<4} {c.module}:{c.lineno} "
            f"{c.name} = {c.value:g} [{c.shape}]  {how}  {p.artefact}#{p.pointer} = {p.value:g}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true", help="print every hit")
    parser.add_argument("--scaled", action="store_true", help="include unit-scaled matches")
    parser.add_argument("--ranked", action="store_true", help="only hits whose units agree")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    rows = published_rows()
    constants = module_constants()
    hits = census(constants, rows)
    exact = [h for h in hits if h.scale == 1.0]
    scaled = [h for h in hits if h.scale != 1.0]
    shown = hits if args.scaled else exact
    if args.ranked:
        shown = [h for h in shown if units_agree(h)]

    if args.json:
        print(
            json.dumps(
                {
                    "published_rows": len(rows),
                    "module_constants": len(constants),
                    "exact": len(exact),
                    "scaled": len(scaled),
                    "hits": [
                        {
                            "module": h.constant.module,
                            "line": h.constant.lineno,
                            "name": h.constant.name,
                            "shape": h.constant.shape,
                            "value": h.constant.value,
                            "scale": h.scale,
                            "specificity": specificity(h.constant.value, rows),
                            "units_agree": units_agree(h),
                            "artefact": h.published.artefact,
                            "pointer": h.published.pointer,
                            "published": h.published.value,
                        }
                        for h in shown
                    ],
                },
                indent=2,
            )
        )
        return 0

    agreeing = {
        (h.constant.module, h.constant.name, h.constant.lineno) for h in exact if units_agree(h)
    }
    print(
        f"{len(rows)} published rows (JSON only) x {len(constants)} module-level numbers "
        f"in {'/, '.join(SCOPE)}/"
    )
    print(f"  EXACT matches:      {len(exact)}")
    print(f"  SCALED matches:     {len(scaled)}  (a unit conversion away)")
    print(f"  UNITS AGREE:        {len(agreeing)} distinct bindings -- the ranked population")
    if args.list and shown:
        print()
        print(_render(shown, rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
