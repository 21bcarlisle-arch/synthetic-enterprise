"""A price crosses the VAT line only through a named rate, never a number typed at the call site.

THE DEFECT THIS NAMES. Every rate the world settles and the company strikes is ex-VAT; every
published figure a household compares against (the cap, the SVT, a rival's default, Ofgem's
standing charge) is inc-VAT. Each place that crosses that line is one more implementation of the
VAT rule, and by 2026-10-01 there were at least six. Each one found so far either overstated
company value or understated the household's bill — a renewal ceilinged at the inc-VAT cap, the SVT
segment billed inc-VAT then grossed again, a switching offer compared across bases, Ofgem's
inc-VAT standing charge booked as supplier revenue. That is value transferred being read as value
created, and the next one will not announce itself.

WHAT IS SANCTIONED. A gross-up or de-VAT is `amount * (1 + RATE)` or `amount / (1 + RATE)`, where
RATE resolves to one of `SANCTIONED_RATES`: `simulation.price_cap_enforcement.DOMESTIC_VAT_RATE`
(the world's side, with `household_price_inc_vat` and the `_ex_vat` cap accessor built on it) or
`company.compliance.domain_invariants.vat_rate_for_segment` (the company's). Neither declares the
figure: both read `docs/domain_artefact_library/regulatory/uk_vat_rates.json`, one reader on each
side of the wall because neither tree may import the other. Until 2026-10-01 there were three
literal 0.05s (the third was `tariff_comparison.VAT_RATE_DOMESTIC`, now deleted);
`test_the_rate_is_declared_only_in_the_commons` stops a literal home coming back.

WHAT IS NOT CAUGHT, said so nobody reads more into green than it holds: `x + x * 0.05`; a factor
assembled in one statement and applied in another (`f = 1.05` then `p * f`); invoice VAT LINES
(`vat = subtotal * rate`, which bill VAT rather than restate a price, and read the commons rate
artefact). Those would each need a dataflow reading this file deliberately does not attempt.

EACH TEST NAMES ITS OWN DEFECT:
  * `test_no_price_is_grossed_or_de_vatted_by_a_bare_factor` — `p * 1.05`, `p / (1 + 0.05)`.
  * `test_every_vat_factor_names_a_sanctioned_rate` — `vat = 0.05; p * (1 + vat)`: a seventh home.
  * `test_the_detector_can_fire` — a scan that walks nothing is green; it must flag a known stray
    and must reach real factors in BOTH trees.
  * `test_the_rate_is_declared_only_in_the_commons` — `VAT_RATE_DOMESTIC = 0.05` in a module, or
    `VAT_RESIDENTIAL = RateInvariant(value=0.05)`: a literal home that can drift from the law.

R15 MUTATIONS, each applied to the tree and reverted (2026-10-01):
  * `* 1.05` appended to `simulation/svt_product.py`'s de-VAT line -> the bare-factor test red.
  * `DOMESTIC_VAT_RATE` in `simulation/experienced_bill_shock.py` replaced by a local
    `_VAT = 0.05` -> the sanctioned-rate test red.
  * `_bare_factor` returning False -> `test_the_detector_can_fire` red.
  Merge to the commons (2026-10-01), each applied and reverted:
  * `VAT_RATE_DOMESTIC = 0.05` re-added to `company/pricing/tariff_comparison.py` -> the
    declared-only-in-the-commons test red.
  * `VAT_RESIDENTIAL`'s `value=VAT_RATES["reduced"]` replaced by `value=0.05` -> the same test red.
  * `declared_rates` returning `[]` -> the same test red, on its own can-fire assertions.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
SCOPE = ("simulation", "company")

#: name -> the module that must define it. A factor naming any of these, imported from that module
#: (or used inside it), is the sanctioned route.
SANCTIONED_RATES: dict[str, str] = {
    "DOMESTIC_VAT_RATE": "simulation.price_cap_enforcement",
    "vat_rate_for_segment": "company.compliance.domain_invariants",
}
#: The homes, and modules that take their rate as a parameter (`tariff_comparison`'s `vat_rate=`,
#: defaulted from `vat_rate_for_segment`), may write `(1 + vat_rate)` on a local name.
HOMES = {m.replace(".", "/") + ".py" for m in SANCTIONED_RATES.values()} | {
    "company/pricing/tariff_comparison.py"}
VAT_RATES_COMMONS = PROJECT / "docs/domain_artefact_library/regulatory/uk_vat_rates.json"

_VAT_NAME = re.compile(r"(^|_)vat(_|$)", re.I)
_VAT_FACTOR = 1.05


def _num(node: ast.AST, value: float) -> bool:
    return (isinstance(node, ast.Constant) and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool) and abs(node.value - value) < 1e-9)


def _one_plus(node: ast.AST, operand) -> bool:
    return (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add)
            and ((_num(node.left, 1) and operand(node.right))
                 or (_num(node.right, 1) and operand(node.left))))


def _bare_factor(node: ast.AST) -> bool:
    """1.05, 1/1.05 or (1 + 0.05) written where a price is multiplied or divided."""
    return (_num(node, _VAT_FACTOR) or _num(node, 1 / _VAT_FACTOR)
            or _one_plus(node, lambda n: _num(n, _VAT_FACTOR - 1)))


def _vat_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        node = node.func
    if isinstance(node, ast.Name) and _VAT_NAME.search(node.id):
        return node.id
    if isinstance(node, ast.Attribute) and _VAT_NAME.search(node.attr):
        return node.attr
    return None


def scan_source(source: str, rel: str) -> tuple[list[str], list[str], int]:
    """(bare-factor offences, unsanctioned-rate offences, sanctioned factors seen)."""
    tree = ast.parse(source)
    imported = {alias.asname or alias.name: node.module
                for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                for alias in node.names}
    module = rel[:-3].replace("/", ".")
    bare, unsanctioned, sanctioned = [], [], 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp):
            continue
        if isinstance(node.op, (ast.Mult, ast.Div)):
            for side in (node.left, node.right):
                if _bare_factor(side):
                    bare.append(f"{rel}:{node.lineno}: {ast.unparse(node)[:100]}")
        if isinstance(node.op, (ast.Add, ast.Sub)) and (
                _num(node.left, 1) or _num(node.right, 1)):
            name = _vat_name(node.right if _num(node.left, 1) else node.left)
            if name is None:
                continue
            home = SANCTIONED_RATES.get(name)
            if rel in HOMES or (home and (imported.get(name) == home or module == home)):
                sanctioned += 1
            else:
                unsanctioned.append(
                    f"{rel}:{node.lineno}: `{ast.unparse(node)}` — `{name}` is not one of "
                    f"{sorted(SANCTIONED_RATES)} imported from its home")
    return bare, unsanctioned, sanctioned


def _scan_tree() -> tuple[list[str], list[str], dict[str, int]]:
    bare, unsanctioned, seen = [], [], {root: 0 for root in SCOPE}
    for root in SCOPE:
        for path in sorted((PROJECT / root).rglob("*.py")):
            rel = path.relative_to(PROJECT).as_posix()
            b, u, s = scan_source(path.read_text(encoding="utf-8"), rel)
            bare += b
            unsanctioned += u
            seen[root] += s
    return bare, unsanctioned, seen


def test_no_price_is_grossed_or_de_vatted_by_a_bare_factor():
    bare, _, _ = _scan_tree()
    assert not bare, (
        "a price is grossed up or de-VATed by a literal factor; route it through "
        "`price_cap_enforcement.household_price_inc_vat` / `binding_cap_unit_rate_gbp_per_mwh_ex_vat` "
        "or `(1 + vat_rate_for_segment(segment))`:\n  " + "\n  ".join(bare))


def test_every_vat_factor_names_a_sanctioned_rate():
    _, unsanctioned, _ = _scan_tree()
    assert not unsanctioned, (
        "a VAT factor names a rate that is not one of the sanctioned homes — that is another "
        "implementation of the VAT rule:\n  " + "\n  ".join(unsanctioned))


def test_the_detector_can_fire():
    stray = "def f(p):\n    return p * 1.05\n"
    de_vat = "def f(p):\n    return p / (1.0 + 0.05)\n"
    local = "_VAT = 0.05\ndef f(p):\n    return p * (1.0 + _VAT)\n"
    fine = ("from simulation.price_cap_enforcement import DOMESTIC_VAT_RATE\n"
            "def f(p):\n    return p * (1.0 + DOMESTIC_VAT_RATE)\n")
    assert scan_source(stray, "simulation/x.py")[0]
    assert scan_source(de_vat, "simulation/x.py")[0]
    assert scan_source(local, "simulation/x.py")[1]
    assert scan_source(fine, "simulation/x.py") == ([], [], 1)
    _, _, seen = _scan_tree()
    assert all(seen.values()), f"the scan reached no sanctioned VAT factor in some tree: {seen}"


def _is_rate(node: ast.AST) -> bool:
    return (isinstance(node, ast.Constant) and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool) and 0.0 < node.value < 1.0)


def declared_rates(source: str, rel: str) -> list[str]:
    """`X_VAT_Y = 0.05`, or `VAT_X = SomeInvariant(value=0.05)`: a VAT rate typed as a literal."""
    out = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)) or node.value is None:
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if not any(_vat_name(t) for t in targets):
            continue
        value = node.value
        if _is_rate(value) or (isinstance(value, ast.Call) and any(
                k.arg == "value" and _is_rate(k.value) for k in value.keywords)):
            out.append(f"{rel}:{node.lineno}: {ast.unparse(node)[:100]}")
    return out


def test_the_rate_is_declared_only_in_the_commons():
    import json

    from company.compliance.domain_invariants import vat_rate_for_segment
    from simulation.price_cap_enforcement import DOMESTIC_VAT_RATE
    law = json.loads(VAT_RATES_COMMONS.read_text())["rates"]["reduced"]["rate"]
    assert DOMESTIC_VAT_RATE == vat_rate_for_segment("resi") == law

    assert declared_rates("VAT_RATE_DOMESTIC = 0.05\n", "company/x.py")
    assert declared_rates("VAT_RESIDENTIAL = RateInvariant(id='v', value=0.05)\n", "company/x.py")
    assert not declared_rates("SME_VAT_DE_MINIMIS_KWH_PER_DAY = 33.0\n", "company/x.py")
    declared = [hit for root in SCOPE for path in sorted((PROJECT / root).rglob("*.py"))
                for hit in declared_rates(path.read_text(encoding="utf-8"),
                                          path.relative_to(PROJECT).as_posix())]
    assert not declared, (
        "a VAT rate is typed as a literal; read it from the commons through "
        "`DOMESTIC_VAT_RATE` (world) or `vat_rate_for_segment` (company):\n  "
        + "\n  ".join(declared))
