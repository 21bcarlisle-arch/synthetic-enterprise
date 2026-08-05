"""Epistemic-wall import ratchet (NET tier, STATIC).

WHY THIS EXISTS
---------------
The project's core law is an epistemic wall (CLAUDE.md, "Architectural Laws —
Epistemic Honesty"): the company layer may only know what a real UK energy
supplier could observe, so `company/` code must not read simulation internals
except through the sanctioned interface seam. A July 2026 analysis counted on
the order of a hundred import crossings bypassing the seam. Nothing in the
tree PREVENTED crossing #107 — a new crossing could be added and no test would
notice.

This module makes the wall MEASURABLE and UN-REGRESSABLE, using the same
shrink-only ratchet pattern the project already applies elsewhere (a dated
allowlist of grandfathered edges, plus a stale-entry test that forces the
allowlist to shrink as edges are removed and can never silently grow).

  * A NEW crossing (an edge not in the dated allowlist) fails the suite,
    naming the edge and pointing at the wall doctrine.
  * A grandfathered edge that is later DELETED from the code must be removed
    from the allowlist too, or its stale entry fails the suite. The allowlist
    is therefore a one-way ratchet: it can only shrink.

PHASE-1 RECON — the sanctioned seam and the shape of "SIM"
----------------------------------------------------------
Read directly from the code layout on 2026-08-05 (evidence in the PR body):

  * The sanctioned seam is the `company.interfaces` package
    (`company/interfaces/`), fronted by `sim_interface.py` whose own docstring
    reads: "The company layer must only access simulation data through these
    methods — it cannot read simulation internals directly." An edge is
    SANCTIONED (exempt) iff its COMPANY-side endpoint module lives under
    `company.interfaces` — that is the single crossing surface, in BOTH
    directions.

  * The simulated world is split across TWO sibling top-level packages, not
    one: `sim/` (market/price/weather/forward-curve/risk engine) AND
    `simulation/` (population, households, settlement, customer-behaviour
    engine — household budgets, life events, demand physics, meter reads).
    Both are "SIM internals" for the purposes of the wall, so the SIM side of
    the ratchet is the union {sim, simulation}. Measuring only `company↔sim`
    would freeze an essentially-empty baseline (3 edges, all inside the seam)
    and give false confidence while the real crossing mass sits in
    `simulation↔company`. The per-package census is reported in the PR.

SCOPE / KNOWN LIMIT (stated honestly)
-------------------------------------
This covers STATIC imports only — `import X` and `from X import Y`, resolved
with the stdlib `ast` module over a pure read of the tree. Dynamic imports
(`__import__`, `importlib.import_module`), `getattr`-driven access, and
string-eval escape it. That is a known, ACCEPTED limit of this (NET, static)
tier: the ratchet raises the cost of a static crossing to "you must edit a
dated allowlist and explain it in review", which is where the overwhelming
majority of real crossings would land. A dynamic-import tier would be a
separate, heavier instrument.

Dependencies: pytest + Python stdlib (`ast`, `os`) only. No project imports,
so this suite runs even when the app's runtime deps are absent.
"""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass

# --------------------------------------------------------------------------
# Configuration — the two sides of the wall and the sanctioned seam.
# --------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Company side of the wall.
COMPANY_PACKAGES = frozenset({"company"})
# SIM side of the wall — the simulated world spans BOTH packages (see recon).
SIM_PACKAGES = frozenset({"sim", "simulation"})
# The sanctioned crossing surface. An edge whose COMPANY-side endpoint module
# is under this package is a legitimate seam crossing, not a wall violation.
SEAM_PACKAGE = "company.interfaces"

# Top-level directories walked (all under REPO_ROOT). Kept explicit so the
# walker is deterministic and the mutation fixtures can reuse build_edges().
WALL_DIRS = ("company", "sim", "simulation")

WALL_DOCTRINE = (
    "Epistemic wall (CLAUDE.md, Architectural Laws): the company layer must "
    "only cross the SIM boundary through the sanctioned seam "
    f"`{SEAM_PACKAGE}` ({SEAM_PACKAGE.replace('.', '/')}/). A direct import "
    "between company internals and SIM internals bypasses that seam. If this "
    "crossing is intentional and unavoidable, route it through the seam; if it "
    "is genuinely legacy, add it to the dated allowlist in this file with a "
    "one-line justification — never silently."
)


# --------------------------------------------------------------------------
# Static import extraction (stdlib `ast` only).
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class RawEdge:
    """One import edge: source module imports target module, at file:line."""

    src: str          # dotted module doing the importing
    dst: str          # dotted module being imported
    path: str         # file (repo-relative) where the import statement sits
    lineno: int


def _module_name(root: str, path: str) -> str:
    """Dotted module name for a .py file relative to `root` (drops __init__)."""
    rel = os.path.relpath(path, root)
    parts = rel[: -len(".py")].split(os.sep)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _resolve_relative(src: str, module: str | None, level: int) -> str:
    """Resolve a relative import (`from . import x`) to an absolute dotted name.

    Sibling top-level packages (company / sim / simulation) cannot reach each
    other via a relative import, so relative imports never produce a wall
    crossing — but we resolve them correctly anyway for completeness.
    """
    pkg = src.split(".")
    base = pkg[: len(pkg) - level] if level <= len(pkg) else []
    tail = module.split(".") if module else []
    return ".".join(base + tail)


def build_edges(root: str, dirs: tuple[str, ...]) -> list[RawEdge]:
    """Walk `dirs` under `root` and return every static import edge.

    Pure static read: parses each file with `ast`, extracts `Import` and
    `ImportFrom` nodes. A file that fails to parse is skipped (it cannot import
    anything at runtime either). Parameterised by root so the R15 mutation
    fixtures can point it at a synthetic tmp tree.
    """
    edges: list[RawEdge] = []
    for top in dirs:
        for dirpath, _dirnames, filenames in os.walk(os.path.join(root, top)):
            for fn in filenames:
                if not fn.endswith(".py"):
                    continue
                path = os.path.join(dirpath, fn)
                src = _module_name(root, path)
                try:
                    with open(path, encoding="utf-8") as fh:
                        tree = ast.parse(fh.read(), filename=path)
                except (SyntaxError, UnicodeDecodeError):
                    continue
                relpath = os.path.relpath(path, root)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            edges.append(RawEdge(src, alias.name, relpath, node.lineno))
                    elif isinstance(node, ast.ImportFrom):
                        if node.level:
                            dst = _resolve_relative(src, node.module, node.level)
                        else:
                            dst = node.module or ""
                        edges.append(RawEdge(src, dst, relpath, node.lineno))
    return edges


# --------------------------------------------------------------------------
# Classification — which edges cross the wall.
# --------------------------------------------------------------------------

def _top(module: str) -> str:
    return module.split(".", 1)[0] if module else ""


def _under_seam(module: str) -> bool:
    return module == SEAM_PACKAGE or module.startswith(SEAM_PACKAGE + ".")


def company_reads_sim(edges: list[RawEdge]) -> dict[tuple[str, str], RawEdge]:
    """Class (a): company internals importing SIM internals, NOT via the seam.

    Keyed by (src_module, dst_module) so many import statements collapsing to
    the same module pair count as one edge; value is a representative location.
    """
    out: dict[tuple[str, str], RawEdge] = {}
    for e in edges:
        if _top(e.src) in COMPANY_PACKAGES and _top(e.dst) in SIM_PACKAGES and not _under_seam(e.src):
            out.setdefault((e.src, e.dst), e)
    return out


def sim_reads_company(edges: list[RawEdge]) -> dict[tuple[str, str], RawEdge]:
    """Class (b): SIM internals importing company internals, NOT via the seam.

    Symmetric to class (a): an edge whose company-side endpoint (here the
    TARGET) is under the seam package is a sanctioned crossing and exempt.
    """
    out: dict[tuple[str, str], RawEdge] = {}
    for e in edges:
        if _top(e.src) in SIM_PACKAGES and _top(e.dst) in COMPANY_PACKAGES and not _under_seam(e.dst):
            out.setdefault((e.src, e.dst), e)
    return out


# --------------------------------------------------------------------------
# The dated, shrink-only allowlists (the ratchet baseline).
#
# Baseline frozen 2026-08-05 from a pure static walk of the tree on the
# `claude/epistemic-wall-import-ratchet-jnw2dl` branch. Each tuple is a
# (source_module, target_module) edge grandfathered on that date. Rules:
#   * The lists may only SHRINK. Removing a wall crossing from the code must be
#     matched by deleting its tuple here (enforced by the stale-entry tests).
#   * A NEW crossing must NOT be added here to silence the suite — route it
#     through the seam instead. An addition here is a reviewable, deliberate act
#     that says "this legacy edge is acknowledged and owed a paydown".
# --------------------------------------------------------------------------

# Class (a) — company/* importing sim.*/simulation.* other than via the seam.
# Census on 2026-08-05: ZERO. The company layer does not read SIM internals
# directly today; the only company->SIM edges are the 3 inside the seam file
# `company/interfaces/sim_interface.py`, which are exempt by construction.
LEGACY_COMPANY_READS_SIM: frozenset[tuple[str, str]] = frozenset()

# Class (b) — sim.*/simulation.* importing company.* other than via the seam.
# Census on 2026-08-05: 46 edges, ALL originating in `simulation/` (the
# population/settlement engine wiring the company's own books into a run);
# `sim/` itself reads company zero times. These are the real crossing mass the
# July analysis was pointing at.
LEGACY_SIM_READS_COMPANY: frozenset[tuple[str, str]] = frozenset({
    ("simulation.arrears_engine", "company.policy.decision_policy"),
    ("simulation.churn_journey", "company.core.activation_energy"),
    ("simulation.churn_journey", "company.core.reputation_index"),
    ("simulation.churn_journey", "company.core.resentment_ledger"),
    ("simulation.credit_refund_events", "company.billing.credit_refund"),
    ("simulation.customer_events", "company.crm.churn_model"),
    ("simulation.dd_balance_book", "company.billing.dd_review"),
    ("simulation.dd_collection_book", "company.billing.direct_debit"),
    ("simulation.dd_level_collection_book", "company.billing.direct_debit"),
    ("simulation.feedback_survey", "company.core.reputation_index"),
    ("simulation.hedged_settlement", "company.pricing.ofgem_price_cap"),
    ("simulation.publish_market_feed", "company.market.price_feed"),
    ("simulation.renewals", "company.governance.approval_interface"),
    ("simulation.renewals", "company.governance.decision_rights"),
    ("simulation.renewals", "company.pricing.tariff_engine"),
    ("simulation.run_phase2b", "company.analytics.churn_accuracy_report"),
    ("simulation.run_phase2b", "company.core.reputation_index"),
    ("simulation.run_phase2b", "company.core.resentment_ledger"),
    ("simulation.run_phase2b", "company.crm.churn_model"),
    ("simulation.run_phase2b", "company.crm.complaints"),
    ("simulation.run_phase2b", "company.crm.customer_profitability"),
    ("simulation.run_phase2b", "company.crm.enriched_churn_estimate"),
    ("simulation.run_phase2b", "company.crm.nps_tracker"),
    ("simulation.run_phase2b", "company.crm.payment_behaviour_analytics"),
    ("simulation.run_phase2b", "company.crm.satisfaction_accumulator"),
    ("simulation.run_phase2b", "company.crm.tpi_book"),
    ("simulation.run_phase2b", "company.finance.margin_call_book"),
    ("simulation.run_phase2b", "company.market.flexibility_revenue_book"),
    ("simulation.run_phase2b", "company.market.ic_flexibility_revenue"),
    ("simulation.run_phase2b", "company.policy.decision_policy"),
    ("simulation.run_phase2b", "company.pricing.margin_feedback"),
    ("simulation.run_phase2b", "company.pricing.ofgem_price_cap"),
    ("simulation.run_phase2b", "company.pricing.tariff_engine"),
    ("simulation.run_phase2b", "company.regulatory.ccl_ledger"),
    ("simulation.run_phase2b", "company.regulatory.fit_book"),
    ("simulation.run_phase2b", "company.regulatory.roc_ledger"),
    ("simulation.run_phase2b", "company.risk.collateral_death_test"),
    ("simulation.run_phase2b", "company.risk.hedge_policy"),
    ("simulation.run_phase2b", "company.trading.forward_book"),
    ("simulation.run_phase2b", "company.trading.hedge_decision"),
    ("simulation.run_phase2b", "company.trading.wholesale_credit_exposure"),
    ("simulation.run_phase4c_on_phase2b", "company.billing.account_adjustment_register"),
    ("simulation.run_phase4c_on_phase2b", "company.billing.back_billing"),
    ("simulation.run_phase4c_on_phase2b", "company.billing.dd_review_runner"),
    ("simulation.run_phase4c_on_phase2b", "company.billing.pre_bill_validation"),
    ("simulation.run_phase4c_on_phase2b", "company.compliance.domain_invariants"),
})


# --------------------------------------------------------------------------
# Shared helpers for the tests + mutation fixtures.
# --------------------------------------------------------------------------

def _fmt(edges_by_key: dict[tuple[str, str], RawEdge], keys) -> str:
    lines = []
    for key in sorted(keys):
        e = edges_by_key[key]
        lines.append(f"    {e.src} -> {e.dst}   ({e.path}:{e.lineno})")
    return "\n".join(lines)


def _real_edges() -> list[RawEdge]:
    return build_edges(REPO_ROOT, WALL_DIRS)


# --------------------------------------------------------------------------
# Tests — Phase-1 recon assertion.
# --------------------------------------------------------------------------

def test_seam_package_exists_and_is_the_crossing_surface():
    """The sanctioned seam is `company/interfaces/` — verify it is really there.

    Guards the recon finding this whole ratchet rests on: if the seam were
    renamed or removed, the exemption logic would silently mislabel edges.
    """
    seam_dir = os.path.join(REPO_ROOT, *SEAM_PACKAGE.split("."))
    assert os.path.isdir(seam_dir), f"seam package dir missing: {seam_dir}"
    assert os.path.isfile(os.path.join(seam_dir, "sim_interface.py")), (
        "expected the seam front-door module company/interfaces/sim_interface.py"
    )


def test_sim_side_packages_exist():
    """Both halves of the simulated world are present (sim/ and simulation/)."""
    for pkg in SIM_PACKAGES:
        assert os.path.isdir(os.path.join(REPO_ROOT, pkg)), f"SIM package missing: {pkg}/"


# --------------------------------------------------------------------------
# Tests — new crossings fail (the wall).
# --------------------------------------------------------------------------

def test_no_new_company_reads_sim():
    """No company/* import of SIM internals outside the seam or the allowlist."""
    edges = company_reads_sim(_real_edges())
    new = set(edges) - LEGACY_COMPANY_READS_SIM
    assert not new, (
        "NEW epistemic-wall crossing(s): company internals importing SIM "
        "internals outside the seam and not in the dated allowlist:\n"
        + _fmt(edges, new)
        + "\n\n"
        + WALL_DOCTRINE
    )


def test_no_new_sim_reads_company():
    """No SIM import of company internals outside the seam or the allowlist."""
    edges = sim_reads_company(_real_edges())
    new = set(edges) - LEGACY_SIM_READS_COMPANY
    assert not new, (
        "NEW epistemic-wall crossing(s): SIM internals importing company "
        "internals outside the seam and not in the dated allowlist:\n"
        + _fmt(edges, new)
        + "\n\n"
        + WALL_DOCTRINE
    )


# --------------------------------------------------------------------------
# Tests — the allowlist may only shrink (stale-entry ratchet).
# --------------------------------------------------------------------------

def test_company_reads_sim_allowlist_has_no_stale_entries():
    """Every LEGACY_COMPANY_READS_SIM entry must still exist in the code."""
    edges = company_reads_sim(_real_edges())
    stale = LEGACY_COMPANY_READS_SIM - set(edges)
    assert not stale, (
        "STALE allowlist entries — these grandfathered crossings no longer "
        "exist in the code and must be DELETED from LEGACY_COMPANY_READS_SIM "
        "(the ratchet only shrinks):\n"
        + "\n".join(f"    {s} -> {d}" for s, d in sorted(stale))
    )


def test_sim_reads_company_allowlist_has_no_stale_entries():
    """Every LEGACY_SIM_READS_COMPANY entry must still exist in the code."""
    edges = sim_reads_company(_real_edges())
    stale = LEGACY_SIM_READS_COMPANY - set(edges)
    assert not stale, (
        "STALE allowlist entries — these grandfathered crossings no longer "
        "exist in the code and must be DELETED from LEGACY_SIM_READS_COMPANY "
        "(the ratchet only shrinks):\n"
        + "\n".join(f"    {s} -> {d}" for s, d in sorted(stale))
    )


# --------------------------------------------------------------------------
# Tests — R15 mutation proof (a control must be able to FAIL).
#
# CONTROLS_THAT_CANNOT_FAIL.md: no control counts as evidence unless a mutation
# test proves it fires on its own named defect. We inject a synthetic crossing
# and assert it reds EXACTLY the new-crossing check for that direction and
# nothing else (not the stale-entry check, not the other direction).
# --------------------------------------------------------------------------

# A synthetic edge guaranteed absent from the real tree.
_SYNTH_COMPANY_READS_SIM = RawEdge(
    src="company.pricing.tariff_engine",
    dst="sim.weather_engine",
    path="company/pricing/tariff_engine.py",
    lineno=1,
)
_SYNTH_SIM_READS_COMPANY = RawEdge(
    src="sim.forward_curve",
    dst="company.trading.forward_book",
    path="sim/forward_curve.py",
    lineno=1,
)


def test_mutation_injected_company_reads_sim_reds_only_new_crossing():
    """Inject a company->SIM crossing in memory; assert precise blast radius."""
    real = _real_edges()
    mutated = real + [_SYNTH_COMPANY_READS_SIM]
    key = (_SYNTH_COMPANY_READS_SIM.src, _SYNTH_COMPANY_READS_SIM.dst)

    # Sanity: the synthetic edge is genuinely new.
    assert key not in company_reads_sim(real)

    # 1) The new-crossing check for THIS direction now fires, on exactly this edge.
    c2s = company_reads_sim(mutated)
    new = set(c2s) - LEGACY_COMPANY_READS_SIM
    assert new == {key}, f"expected exactly the injected edge to be new, got {new}"

    # 2) The stale-entry check for this direction is UNAFFECTED (adding an edge
    #    cannot make an allowlist entry stale).
    assert not (LEGACY_COMPANY_READS_SIM - set(c2s))

    # 3) The OTHER direction is UNAFFECTED.
    s2c = sim_reads_company(mutated)
    assert not (set(s2c) - LEGACY_SIM_READS_COMPANY)
    assert not (LEGACY_SIM_READS_COMPANY - set(s2c))


def test_mutation_injected_sim_reads_company_reds_only_new_crossing():
    """Inject a SIM->company crossing in memory; assert precise blast radius."""
    real = _real_edges()
    mutated = real + [_SYNTH_SIM_READS_COMPANY]
    key = (_SYNTH_SIM_READS_COMPANY.src, _SYNTH_SIM_READS_COMPANY.dst)

    assert key not in sim_reads_company(real)

    s2c = sim_reads_company(mutated)
    new = set(s2c) - LEGACY_SIM_READS_COMPANY
    assert new == {key}, f"expected exactly the injected edge to be new, got {new}"

    assert not (LEGACY_SIM_READS_COMPANY - set(s2c))

    c2s = company_reads_sim(mutated)
    assert not (set(c2s) - LEGACY_COMPANY_READS_SIM)
    assert not (LEGACY_COMPANY_READS_SIM - set(c2s))


def test_mutation_walker_detects_a_physical_crossing_on_disk(tmp_path):
    """End-to-end proof the AST WALKER (not just set arithmetic) catches a real
    crossing: write a synthetic company module that imports sim on disk and
    assert build_edges() surfaces it as a company->SIM violation.

    This closes the fail-open gap where the classifier is correct but the
    walker never produced the edge in the first place.
    """
    # Minimal synthetic tree: <root>/company/rogue.py imports sim.weather_engine
    comp = tmp_path / "company"
    comp.mkdir()
    (comp / "__init__.py").write_text("")
    (comp / "rogue.py").write_text(
        "from sim.weather_engine import secret_internal\n"
        "import simulation.household\n"
    )
    sim_dir = tmp_path / "sim"
    sim_dir.mkdir()
    (sim_dir / "__init__.py").write_text("")
    (sim_dir / "weather_engine.py").write_text("secret_internal = 42\n")

    edges = build_edges(str(tmp_path), WALL_DIRS)
    c2s = company_reads_sim(edges)
    assert ("company.rogue", "sim.weather_engine") in c2s
    assert ("company.rogue", "simulation.household") in c2s


def test_mutation_walker_respects_the_seam_exemption(tmp_path):
    """A company->SIM import from WITHIN company/interfaces/ must NOT be flagged
    (proves the seam exemption is real and not vacuous)."""
    interfaces = tmp_path / "company" / "interfaces"
    interfaces.mkdir(parents=True)
    (tmp_path / "company" / "__init__.py").write_text("")
    (interfaces / "__init__.py").write_text("")
    (interfaces / "seam.py").write_text("from sim.system_prices import get_price\n")
    (tmp_path / "sim").mkdir()
    (tmp_path / "sim" / "__init__.py").write_text("")

    edges = build_edges(str(tmp_path), WALL_DIRS)
    c2s = company_reads_sim(edges)
    # The seam import exists as a raw edge but is exempt from the violation set.
    assert ("company.interfaces.seam", "sim.system_prices") not in c2s
    assert any(
        e.src == "company.interfaces.seam" and e.dst == "sim.system_prices"
        for e in edges
    ), "walker should still SEE the seam edge; it is only exempt from classification"


# --------------------------------------------------------------------------
# Census sanity — the allowlists match the frozen baseline exactly. If this
# fails on today's tree the recon (and the PR census) is out of date.
# --------------------------------------------------------------------------

def test_baseline_census_is_exactly_as_frozen():
    """On today's tree: class (a) == 0, class (b) == the 46 frozen edges."""
    edges = _real_edges()
    assert set(company_reads_sim(edges)) == LEGACY_COMPANY_READS_SIM
    assert set(sim_reads_company(edges)) == LEGACY_SIM_READS_COMPANY
