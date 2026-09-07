"""A coverage, ceiling or sufficiency claim declares the dimension it reduces over, or it is refused.

REUSE: tools/reduction_dimension.py
CLASS: CUSTOM
INDEX: searched "coverage", "ceiling", "sufficiency", "dimension", "declare", "population",
       "reduce", "axes".
       `tools/departure_population.py` is the nearest prior art and is the SHAPE this follows -- a
       reading declares the population it was taken on, with a refusal that names its reason. It is
       about WHICH ROWS a reading can see; this is about WHICH AXES a figure varies over, which is
       the orthogonal half and is what the canon names. It is not importable for this: its
       `declare` returns route flags over a departure capture and knows nothing of a subject vector.
       `tools/domain_constant_origins.py` supplies the census-and-refuse shape (a scan, not a
       register) and is followed rather than imported -- it scans NAMES for an origin comment;
       this holds a STRUCTURED declaration a caller builds and the module publishes.
       `tools/demand_vector_coverage.py` names its axes in `AXES` but nothing checks that the axes
       it reduces over account for the vector it claims to be about. Nothing declares a reduction.

WHY THIS EXISTS
---------------
`DIRECTOR_CANON_THE_DEMAND_VECTOR_2026-09-07`, WORK THIS CREATES item 3: *"A control refusing any
coverage, ceiling or sufficiency claim that does not declare the dimension it reduces over."*

The defect it names, in the canon's own section 1: twice in two days a coverage claim was measured
against a single number where the thing being served is several.

  * ON OUTPUTS. Demand coverage was measured on total annual kWh -- 13 cases. A cold-and-insulated
    house and a mild-and-leaky one produce the same annual total and are completely different
    customers. On a scalar they are one case; to a supplier they are several.
  * ON INPUTS. Three weather grids -- 21 temperature, 21 wind, 5 irradiance -- reduce over the three
    drivers ONE AT A TIME. The project's own measurement says the response to each driver depends on
    the fabric, so the marginals are not the joint and the fabric is not in the partition at all.

**Both figures were correct arithmetic.** Neither was wrong in its own terms, and no control could
have gone red on the number. What was missing in both cases is upstream of the arithmetic: nothing
at the site said what the figure varies over, so nothing said what it averages away. The canon:
*"It flatters in a consistent direction -- always making the sample look smaller and the coverage
look better -- which is why it must be looked for rather than waited for."*

WHAT THIS HOLDS, AND IT IS THE PROPERTY AND NOT TODAY'S ANSWER
--------------------------------------------------------------
Not "demand coverage must be measured on five axes" and not "the weather partition must be joint" --
both of those go red when the code becomes MORE honest, and both are the delivery seat's questions
rather than the canon's. The property is:

    *A claim about how much of a population is covered, how high a ceiling is, or whether a sample
    suffices, names the subject vector it is about, names the dimensions it is measured on, and
    accounts for every component of that vector as either reduced over or explicitly blind.*

A claim measured on one axis of a five-component vector is LEGAL here and always will be. What is
refused is a claim that does not say so. The whole mechanism is that the collapse becomes a
declared, readable fact at the site instead of something a reader has to reconstruct.

THE PARTITION MUST BE EXHAUSTIVE, WHICH IS THE ONLY REASON THIS CAN FAIL
------------------------------------------------------------------------
A declaration that merely LISTED its axes would be theatre: an author who forgot the half-hourly
shape would list four axes, and a control counting a non-empty list would pass. So the contract is
a partition. Every component of `of` must be accounted for exactly once -- reduced over directly,
consumed by a named derived dimension, or declared `blind_to`. An unaccounted component is the
refusal, and it names the component.

`derived_from` is what makes an honest scalar declarable. Total annual kWh is not a component of the
demand vector; it is two components summed. So a claim reducing over it says so, and a derived
dimension consuming two or more components IS the collapse -- computed by `collapsed`, not asserted.

`joint` is the input-side half. Three dimensions reduced ONE AT A TIME and three reduced JOINTLY are
different claims that read identically in a list of three names, which is exactly how 21/21/5 was
read as a statement about the weather a household sees. A multi-dimension claim must say which.

Run:  python3 -m tools.reduction_dimension            # the census, and what each claim reduces over
      python3 -m tools.reduction_dimension --undeclared   # exit 1 if any claim in scope is silent
"""
from __future__ import annotations

import argparse
import ast
import importlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

#: The three kinds the canon names, and the set is closed. Each is a claim whose whole content is a
#: reduction: coverage reduces a population to a share, a ceiling reduces it to a maximum, and
#: sufficiency reduces it to a yes. All three are meaningless without the axes they reduce over.
CLAIM_KINDS = ("coverage", "ceiling", "sufficiency")

#: Words that look like a declaration and are not one. A declaration whose axis is "tbd" is worse
#: than none, because it passes a non-empty check and reads as an answer.
PLACEHOLDERS = frozenset({"", "-", "?", "n/a", "na", "tbd", "todo", "unknown", "none", "null"})


#: THE DEMAND VECTOR, verbatim from the canon's section 2 -- the five things the drawn population
#: must reproduce the observed distribution of, per household. It lives here because it is the
#: subject vector that the claims this control covers are claims ABOUT, and a subject vector spelled
#: out separately in each claim is a subject vector that will differ between them within a month.
#:
#: NOT A MEASUREMENT AND NOT A TARGET. It is the canon's list of components, and the whole of what
#: this module knows about it is the NAMES. What any particular claim can see of it is that claim's
#: declaration to make.
DEMAND_VECTOR = (
    "annual_gas_kwh",
    "annual_electricity_kwh",
    "seasonal_gas_shape",
    "half_hourly_electricity_shape",
    "heating_fuel",
)


class UndeclaredReduction(ValueError):
    """A claim that cannot say what it reduces over. The message names which of the legs failed."""


@dataclass(frozen=True)
class Declaration:
    """What one coverage/ceiling/sufficiency claim is about and what it can see."""

    claim: str
    kind: str
    of: tuple[str, ...]
    reduces_over: tuple[str, ...]
    blind_to: tuple[str, ...]
    derived_from: tuple[tuple[str, tuple[str, ...]], ...]
    joint: bool

    @property
    def collapsed(self) -> tuple[str, ...]:
        """The derived dimensions that consume two or more components -- the collapse, computed.

        This is the output-side defect made into a fact. A claim reducing over `total_annual_kwh`
        does not have to confess anything: the confession is arithmetic on its own declaration.
        """
        return tuple(sorted(name for name, parts in self.derived_from if len(parts) > 1))

    @property
    def separable(self) -> bool:
        """Reduced one dimension at a time. The input-side defect, and legal when declared."""
        return len(self.reduces_over) > 1 and not self.joint

    def banner(self) -> str:
        """One line fit to publish beside the figure. A page that carries this cannot mislead by
        omission -- which is the only thing this whole mechanism buys."""
        how = "jointly" if self.joint else "one dimension at a time"
        line = (f"{self.kind} of {self.claim}: measured over "
                f"{', '.join(self.reduces_over)} ({how})")
        if self.blind_to:
            line += f"; blind to {', '.join(self.blind_to)}"
        if self.collapsed:
            made = "; ".join(f"{name} = {' + '.join(parts)}"
                             for name, parts in self.derived_from if len(parts) > 1)
            line += f"; collapses {made}"
        return line


def _clean(label: str, values, *, what: str) -> tuple[str, ...]:
    out = []
    for v in values:
        if not isinstance(v, str):
            raise UndeclaredReduction(f"{label}: {what} must be named in words, got {v!r}")
        if v.strip().lower() in PLACEHOLDERS:
            raise UndeclaredReduction(
                f"{label}: {what} contains the placeholder {v!r}, which declares nothing")
        out.append(v.strip())
    if len(set(out)) != len(out):
        raise UndeclaredReduction(f"{label}: {what} names the same thing twice: {out}")
    return tuple(out)


def declare(claim: str, *, kind: str, of, reduces_over, joint: bool,
            blind_to=(), derived_from=None) -> Declaration:
    """Declare what a claim reduces over, or refuse it with the reason named.

    `claim`         what is being claimed about, in words a director would use.
    `kind`          one of CLAIM_KINDS.
    `of`            the components of the subject vector -- what the thing being served varies over.
    `reduces_over`  the dimensions the figure is actually measured on.
    `joint`         True if those dimensions are reduced together, False if one at a time.
    `blind_to`      components of `of` the figure cannot distinguish. Declared, not discovered.
    `derived_from`  {derived dimension: the components of `of` it is built from}, for any dimension
                    in `reduces_over` that is not itself a component.
    """
    label = claim if isinstance(claim, str) and claim.strip() else "<unnamed claim>"
    if not isinstance(claim, str) or claim.strip().lower() in PLACEHOLDERS:
        raise UndeclaredReduction(f"a claim must say what it is about, got {claim!r}")
    if kind not in CLAIM_KINDS:
        raise UndeclaredReduction(
            f"{label}: kind {kind!r} is not one of {CLAIM_KINDS} -- the set is the canon's and closed")

    of_t = _clean(label, of, what="the subject vector")
    if not of_t:
        raise UndeclaredReduction(
            f"{label}: names no subject vector, so there is nothing for a figure to be a share OF")
    over_t = _clean(label, reduces_over, what="the reduction dimensions")
    if not over_t:
        raise UndeclaredReduction(
            f"{label}: names no reduction dimension -- this is the defect the canon refuses")
    blind_t = _clean(label, blind_to, what="the blind components")

    derived = dict(derived_from or {})
    derived_t: list[tuple[str, tuple[str, ...]]] = []
    for name, parts in derived.items():
        if name not in over_t:
            raise UndeclaredReduction(
                f"{label}: {name!r} is said to be derived but is not a reduction dimension")
        parts_t = _clean(label, parts, what=f"the components of {name!r}")
        if not parts_t:
            raise UndeclaredReduction(f"{label}: {name!r} is derived from nothing")
        unknown = [p for p in parts_t if p not in of_t]
        if unknown:
            raise UndeclaredReduction(
                f"{label}: {name!r} is built from {unknown}, which are not in the subject vector")
        derived_t.append((name, parts_t))

    if not isinstance(joint, bool):
        raise UndeclaredReduction(
            f"{label}: `joint` must say yes or no whether the dimensions are reduced together")
    if len(over_t) == 1 and not joint:
        raise UndeclaredReduction(
            f"{label}: one dimension cannot be reduced separably -- `joint` is not applicable here")

    # Every reduction dimension is either a component of the subject vector or says what it is made
    # of. A dimension that is neither is a name nobody can connect to the thing being served.
    consumed: set[str] = set()
    for name in over_t:
        if name in of_t:
            consumed.add(name)
            continue
        made_of = dict(derived_t).get(name)
        if made_of is None:
            raise UndeclaredReduction(
                f"{label}: reduces over {name!r}, which is not a component of the subject vector "
                f"and nothing says what it is made of")
        consumed.update(made_of)

    both = sorted(consumed & set(blind_t))
    if both:
        raise UndeclaredReduction(
            f"{label}: {both} are declared blind AND reduced over -- one of the two is wrong")

    unaccounted = [c for c in of_t if c not in consumed and c not in blind_t]
    if unaccounted:
        raise UndeclaredReduction(
            f"{label}: {unaccounted} are components of the subject vector that this claim neither "
            f"reduces over nor declares itself blind to. An unaccounted component is the collapse: "
            f"say which it is.")

    return Declaration(claim=claim.strip(), kind=kind, of=of_t, reduces_over=over_t,
                       blind_to=blind_t, derived_from=tuple(derived_t), joint=joint)


# --------------------------------------------------------------------------------------------
# The census. A declaration only binds the claims that call it, so something has to find the
# claims. This is that half, and it is a SCAN and not a register for the reason
# `domain_constant_origins` gives: a hand-kept list of claim sites is another thing to go stale,
# and the first claim written after it was written is the one it misses.
# --------------------------------------------------------------------------------------------

#: Where a claim about the drawn population can live. `company/` and `saas/` are deliberately
#: absent: a coverage figure there is about the BOOK the company happens to hold, which is a
#: different subject with a different owner, and folding them in would answer a question the canon
#: did not ask.
SCOPE = ("tools", "simulation")

#: The seam this control is about: the household stock and the weather cell space. A claim is in
#: class when it is a claim ABOUT THAT POPULATION -- which is what the canon's two named claims have
#: in common and what `INSUFFICIENT_FUNDS` in a payment module does not. Membership is intrinsic
#: (the module reaches these) rather than listed per claim.
STOCK = frozenset({
    "need_stock_joint", "premise_population", "population_coverage",
    "demand_case_coverage", "demand_vector_coverage", "space_filling_sample",
    "weather_cell_drivers", "weather_cell_derivation", "weather_cell_weights",
    "weather_cell_siting",
})

#: A claim, matched on the name of a public symbol OR ON THE MODULE'S OWN FILENAME. The filename leg
#: is not decoration: `tools/r3_carbon_score_ceiling.py` publishes a ceiling and no public symbol in
#: it carries the word, so a symbol-only rule reads it as out of scope. That is the shape that put
#: 67 constants outside a rule aimed at the concept word and not at how it is actually spelled.
#: `accepts` and `smallest_n` are here for the same reason: they are the sufficiency vocabulary
#: `demand_vector_coverage` actually uses, and a set built from the word "sufficiency" misses the
#: only module in the tree that answers a sufficiency question.
CLAIM_NAME = re.compile(
    r"(^|_)(coverage|covered|ceiling|sufficiency|sufficient|accepts|smallest_n)($|_)", re.I)

#: The module-level name a claim publishes its declaration under.
DECLARATION = "REDUCES_OVER"


def _claim_symbols(tree: ast.Module) -> list[str]:
    found = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            if CLAIM_NAME.search(node.name):
                found.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    if CLAIM_NAME.search(target.id):
                        found.append(target.id)
    return found


def claim_modules(root: Path | None = None) -> list[tuple[str, list[str]]]:
    """Every module in scope that makes a claim about the stock or the cell space, and why.

    Returns (dotted module name, the claim symbols or the filename that put it in class), sorted.
    """
    root = root or PROJECT
    out = []
    for package in SCOPE:
        base = root / package
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            if path.name.startswith("test_") or path.name == "__init__.py":
                continue
            try:
                source = path.read_text()
            except OSError:
                continue
            if not (set(re.findall(r"\w+", source)) & STOCK):
                continue
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            reasons = _claim_symbols(tree)
            if CLAIM_NAME.search(path.stem):
                reasons.append(f"<filename {path.name}>")
            if not reasons:
                continue
            dotted = ".".join(path.relative_to(root).with_suffix("").parts)
            out.append((dotted, sorted(reasons)))
    return out


def declaration_of(dotted: str):
    """The module's declaration, or None. Import errors are NOT swallowed: a claim module that
    cannot be imported is a claim nobody can check, which is the same failure wearing a different
    hat."""
    module = importlib.import_module(dotted)
    return getattr(module, DECLARATION, None)


def undeclared(root: Path | None = None) -> list[tuple[str, list[str]]]:
    """Claim modules in scope carrying no valid declaration. Empty is the only passing state."""
    missing = []
    for dotted, reasons in claim_modules(root):
        found = declaration_of(dotted)
        if isinstance(found, Declaration):
            continue
        if isinstance(found, (list, tuple)) and found and all(
                isinstance(d, Declaration) for d in found):
            continue
        missing.append((dotted, reasons))
    return missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--undeclared", action="store_true",
                        help="exit 1 if any claim in scope declares no reduction dimension")
    args = parser.parse_args(argv)

    silent = undeclared()
    if args.undeclared:
        for dotted, reasons in silent:
            print(f"UNDECLARED  {dotted}  ({', '.join(reasons)})")
        print(f"\n{len(silent)} claim module(s) declare no reduction dimension.")
        return 1 if silent else 0

    for dotted, reasons in claim_modules():
        found = declaration_of(dotted)
        decls = ([found] if isinstance(found, Declaration)
                 else list(found) if isinstance(found, (list, tuple)) else [])
        if not decls:
            print(f"{dotted}\n    UNDECLARED ({', '.join(reasons)})")
            continue
        print(dotted)
        for declaration in decls:
            print(f"    {declaration.banner()}")
    return 0


if __name__ == "__main__":
    # THROUGH THE IMPORTED MODULE, NOT THIS ONE. Run as `python3 -m tools.reduction_dimension`,
    # this file is `__main__` and the claim modules import `tools.reduction_dimension` -- two module
    # objects, two `Declaration` classes, and every `isinstance` below false. The census then
    # reports every claim undeclared no matter what it declares, which is a control that cannot pass
    # rather than one that cannot fail, and just as useless.
    sys.exit(importlib.import_module("tools.reduction_dimension").main())
