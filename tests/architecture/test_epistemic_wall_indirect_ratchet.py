"""Epistemic-wall INDIRECT import ratchet (NET tier, STATIC).

WHAT THIS GUARDS THAT THE DIRECT RATCHET CANNOT
------------------------------------------------
`test_epistemic_wall_ratchet.py` asks "does a walled module import across the
wall?". It is blind, by construction, to a route that leaves the wall first:

    simulation.run_phase2b  ->  background.live_payment_triad  ->  company.billing.*

Neither of those two edges has both endpoints on the wall, so neither is a
crossing, and the dependency survives with the instrument looking straight
through it. `tools/epistemic_wall.py`'s own docstring has named this hazard
since the extraction — *"routing a dependency through a package the walker does
not walk (`tools/`) moves the measurement rather than the dependency, and ...
KNIFE pass 1 refused that move"* — and nothing measured whether the tree
already contained one.

It did. THREE, found the moment the question was asked (2026-08-10, KNIFE pass
3 step 7). They were invisible to the ratchet, absent from the KNIFE ledger,
and absent from the disposition register that claims to examine every crossing.
A hazard stated in prose and left unmeasured is the fail-open shape R15 names
third: the check that passes because nobody ran it.

WHY IT LANDS BEFORE THE COMPOSITION LIFT, NOT AFTER
----------------------------------------------------
`A_composition_lift` — the 65-edge bulk of KNIFE pass 3 — moves thin scenario
harnesses OUT of `simulation/` and above both layers, which in this repo means
into `tools/`. That move is only a CUT if nothing walked still reaches the
company through the moved file; otherwise it is the laundering the register
refuses in writing. Pass 3 cannot honestly make that move while `tools/` is an
unmeasured channel, so the instrument lands first, in its own commit, with no
edge cut in it — the same rule this pass applied to the walker extraction.

THE THREE KILLER PATTERNS, ANSWERED
------------------------------------
TAUTOLOGY   — the allowlist below is hand-written; the measurement comes from
              an AST walk of the tree. Neither is derived from the other. The
              mutation proofs additionally build routes on disk in a tmp tree,
              so the WALKER is exercised and not merely the set arithmetic.
FAIL-OPEN   — three separate ways this could report a confident zero are each
              tested: a bridge package missing from the export (asserted
              present), a chain that ends at a name which is not a module
              (symbol imports must not be reported), and a seam-terminated
              route (must be exempt, and proven still VISIBLE to the walker).
FAIL-SILENT — `test_bridge_packages_all_exist` makes an absent bridge a
              FAILURE rather than a silent empty result, because "could not
              look" and "found nothing" are the same number and opposite facts.
"""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tools.epistemic_wall import (  # noqa: E402
    BRIDGE_PACKAGES,
    REPO_ROOT,
    WALL_DIRS,
    build_edges,
    company_reads_sim,
    indirect_crossings,
    live_indirect_crossings,
    module_names,
    sim_reads_company,
)

# --------------------------------------------------------------------------
# The dated, shrink-only allowlist.
#
# Baseline frozen 2026-08-10 by the first run of this checker, on the tree at
# `d76477ad2` (KNIFE3 B4). Every entry is (source_module, target_module) — the
# two WALL endpoints — keyed exactly as a direct crossing is, so the two sets
# union without translation. Same rules as the direct ratchet: the list may
# only SHRINK, a stale entry is a failure, and a NEW indirect crossing must be
# cut rather than added here.
#
# All are class (b) (the world reading the company) and all leave
# `simulation/run_phase2b.py:95` through `background.live_payment_triad`. They
# are ruled in `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md` under
# `A_composition_lift`: run_phase2b is that design's own densest file, and the
# composition lift is the cut that kills these with the other 32 it carries.
#
# SHRUNK 3 -> 2 on 2026-08-10 (the ratchet's first real shrink, and it was not
# this pass's own work): `("simulation.run_phase2b",
# "company.billing.arrears_engine")` is DELETED because the crossing no longer
# exists. It was the one that continued through `tools.couple_w2_11_d5`, whose
# module-scope `from company.billing.arrears_engine import age_bucket` was
# removed by `15125f388` (atom D21, H27 Expert Hour #5) when that dimension's
# truth side stopped being the company organ's own rule. Verified as a real cut
# and not a blind walker: the other two entries are still reported live, from
# the same file and line, by the same walk.
#
# CLASS (a) — company-side reaching SIM through a bridge — is at ZERO, and that
# is a measurement made here for the first time, not an inheritance. The direct
# ratchet drove class (a) to zero in KNIFE pass 1; nothing had checked whether
# it was zero by the indirect route as well.
LEGACY_INDIRECT_CROSSINGS: frozenset[tuple[str, str]] = frozenset({
    ("simulation.run_phase2b", "company.billing.account_ledger"),
    ("simulation.run_phase2b", "company.billing.payment_observation_consumer"),
})


def _live():
    return live_indirect_crossings()


# --------------------------------------------------------------------------
# The ratchet proper.
# --------------------------------------------------------------------------

def test_no_new_indirect_crossings():
    """No walled module may reach across the wall through an unwalked package.

    A new entry here is not a licence to extend the allowlist: it means a
    dependency was routed around the instrument. Cut it, or route it through
    `company.interfaces`, which is exempt here for exactly the reason it is
    exempt in the direct ratchet.
    """
    live = _live()
    new = set(live) - LEGACY_INDIRECT_CROSSINGS
    assert not new, (
        "NEW INDIRECT wall crossing(s) — a walled module now reaches the other "
        "side of the wall through a package the direct ratchet does not walk. "
        "This is the laundering shape KNIFE pass 1 refused and KNIFE pass 3 "
        "measured:\n"
        + "\n".join(
            f"    {live[k].src} -> {live[k].dst}   via "
            + " -> ".join(live[k].hops)
            + f"   [{live[k].path}:{live[k].lineno}]"
            + f"   ALL first hops: {list(live[k].entries)}"
            for k in sorted(new)
        )
    )


def test_indirect_allowlist_has_no_stale_entries():
    """Every allowlist entry must still exist. The ratchet only shrinks."""
    stale = LEGACY_INDIRECT_CROSSINGS - set(_live())
    assert not stale, (
        "STALE allowlist entries — these indirect crossings no longer exist "
        "and must be DELETED from LEGACY_INDIRECT_CROSSINGS:\n"
        + "\n".join(f"    {s} -> {d}" for s, d in sorted(stale))
    )


def test_baseline_census_is_exactly_as_frozen():
    """On today's tree the live set IS the frozen baseline — no more, no less."""
    assert set(_live()) == LEGACY_INDIRECT_CROSSINGS


def test_every_route_is_reported_not_just_the_shortest():
    """A single printed chain is a redundant-channel trap.

    All three live crossings are carried by BOTH declared bridges. A reader
    given only `hops` would cut `background.live_payment_triad`, re-run the
    checker, and find the edge still there — with no hint why. `entries` names
    every first hop, so "cut it" is a complete instruction.

    The assertion is on the PROPERTY, not on today's pair of names: `entries`
    must always contain the shortest chain's own first hop, and must never be
    empty. The concrete redundancy is then asserted separately, because when it
    is finally cut this test should keep guarding the property rather than
    turning red for the right reason at the wrong test.
    """
    live = _live()
    assert live, "vacuity: nothing measured, so nothing was proven"
    for key, edge in live.items():
        assert edge.entries, f"{key} reports no entry point at all"
        assert edge.hops[0] in edge.entries, (
            f"{key}: the shortest chain's first hop {edge.hops[0]} is missing "
            f"from the full entry set {edge.entries}"
        )


def test_the_known_redundancy_is_visible():
    """Today's concrete fact, recorded so its disappearance is a visible event:
    every live indirect crossing is carried by two independent bridges."""
    for key, edge in _live().items():
        assert len(edge.entries) > 1, (
            f"{key} is now single-routed via {edge.entries} — if a bridge was "
            "cut, say so in the register; if the checker stopped seeing one, "
            "that is the defect this test exists for"
        )


def test_the_reported_chain_is_deterministic():
    """Two runs must produce identical chains.

    Not style. The chain is the evidence a reader acts on, and an evidence
    string that changes between identical runs cannot be diffed, cannot be
    quoted in a register row, and hides a real change inside its own noise.
    """
    first, second = _live(), _live()
    assert {k: v.hops for k, v in first.items()} == {k: v.hops for k, v in second.items()}


# --------------------------------------------------------------------------
# FAIL-SILENT — an absent bridge must be a failure, not a quiet zero.
# --------------------------------------------------------------------------

def test_bridge_packages_all_exist():
    """Each declared bridge package must be present in the repo.

    `indirect_crossings` walks only the bridge dirs it finds. If one were
    renamed or removed, every route through it would vanish and the checker
    would return a confident, wrong zero. This test converts that silence into
    a failure that names the missing package.
    """
    missing = [d for d in BRIDGE_PACKAGES if not os.path.isdir(os.path.join(REPO_ROOT, d))]
    assert not missing, (
        f"declared bridge package(s) absent from the repo: {missing}. Either "
        "the census in tools/epistemic_wall.py is stale, or every route "
        "through them is now unmeasured. An unavailable check is a FAILED "
        "check (R15)."
    )


def test_the_bridge_census_still_covers_every_in_repo_import_target():
    """The perimeter is a CENSUS and must be re-taken, not assumed.

    Every top-level name imported by walled code that resolves to an in-repo
    directory must be either a wall side or a declared bridge. A new top-level
    package appearing in the tree and being imported from `simulation/` would
    otherwise be an unmeasured channel from the day it lands — the exact way
    this gap opened in the first place.
    """
    in_repo = {
        e for e in os.listdir(REPO_ROOT)
        if os.path.isdir(os.path.join(REPO_ROOT, e)) and not e.startswith(".")
    }
    known = set(WALL_DIRS) | set(BRIDGE_PACKAGES)
    unclassified = {
        e.dst.split(".", 1)[0]
        for e in build_edges(REPO_ROOT, WALL_DIRS)
        if e.dst and e.dst.split(".", 1)[0] in in_repo - known
    }
    assert not unclassified, (
        f"walled code imports in-repo top-level package(s) that are neither a "
        f"wall side nor a declared bridge: {sorted(unclassified)}. Add them to "
        "BRIDGE_PACKAGES (and re-freeze this baseline) or the wall is "
        "unmeasured through them."
    )


# --------------------------------------------------------------------------
# R15 mutation proofs — built on disk, so the WALKER is what is exercised.
# --------------------------------------------------------------------------

def _tree(tmp_path, files: dict[str, str]) -> str:
    for rel, body in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    for pkg in set(WALL_DIRS) | set(BRIDGE_PACKAGES):
        d = tmp_path / pkg
        d.mkdir(parents=True, exist_ok=True)
        (d / "__init__.py").touch()
    return str(tmp_path)


def test_mutation_a_route_through_a_bridge_is_detected(tmp_path):
    """The named defect: SIM -> bridge -> company, with a vacuity twin."""
    clean = _tree(tmp_path / "clean", {
        "simulation/run_probe.py": "from tools.helper import go\n",
        "tools/helper.py": "VALUE = 1\n",
        "company/billing/secret.py": "SECRET = 2\n",
    })
    assert not indirect_crossings(clean), (
        "VACUITY GUARD: the un-mutated tree must report nothing, or a pass "
        "below would prove only that the checker always fires"
    )

    dirty = _tree(tmp_path / "dirty", {
        "simulation/run_probe.py": "from tools.helper import go\n",
        "tools/helper.py": "from company.billing.secret import SECRET\n",
        "company/billing/secret.py": "SECRET = 2\n",
    })
    found = indirect_crossings(dirty)
    key = ("simulation.run_probe", "company.billing.secret")
    assert key in found, f"the laundered route was not detected: {sorted(found)}"
    assert found[key].hops == ("tools.helper",)

    # And it is invisible to the DIRECT walker — which is the whole point.
    direct = build_edges(dirty, WALL_DIRS)
    assert not sim_reads_company(direct), (
        "the direct ratchet was supposed to be blind to this route; if it is "
        "not, this checker's reason for existing needs restating"
    )


def test_mutation_a_multi_hop_route_is_detected(tmp_path):
    """Two bridge packages in series must not break the chain."""
    root = _tree(tmp_path, {
        "simulation/run_probe.py": "from background.a import go\n",
        "background/a.py": "from tools.b import onward\n",
        "tools/b.py": "from company.billing.secret import SECRET\n",
        "company/billing/secret.py": "SECRET = 2\n",
    })
    found = indirect_crossings(root)
    key = ("simulation.run_probe", "company.billing.secret")
    assert key in found
    assert found[key].hops == ("background.a", "tools.b")


def test_mutation_the_forbidden_direction_is_detected_too(tmp_path):
    """Class (a) — company -> bridge -> SIM — is at zero live, so its guard
    would be vacuous without this. Proven able to fire on its own defect."""
    root = _tree(tmp_path, {
        "saas/rogue.py": "from tools.helper import go\n",
        "tools/helper.py": "from simulation.household import Household\n",
        "simulation/household.py": "class Household: pass\n",
    })
    found = indirect_crossings(root)
    assert ("saas.rogue", "simulation.household") in found, (
        f"the strictly-forbidden direction was missed through a bridge: {sorted(found)}"
    )


def test_a_seam_terminated_route_is_exempt_but_still_walked(tmp_path):
    """Routing THROUGH a bridge INTO the seam is sanctioned, not laundering.

    Anti-fail-open twin: the exemption must come from the shared classifiers,
    so the same tree with a non-seam target must fire. If only the first half
    were asserted, an exemption that swallowed everything would pass.
    """
    exempt = _tree(tmp_path / "exempt", {
        "simulation/run_probe.py": "from tools.helper import go\n",
        "tools/helper.py": "from company.interfaces.supply_book import points\n",
        "company/interfaces/supply_book.py": "points = []\n",
    })
    assert not indirect_crossings(exempt)

    not_exempt = _tree(tmp_path / "not_exempt", {
        "simulation/run_probe.py": "from tools.helper import go\n",
        "tools/helper.py": "from company.billing.direct_debit import Book\n",
        "company/billing/direct_debit.py": "class Book: pass\n",
    })
    assert ("simulation.run_probe", "company.billing.direct_debit") in indirect_crossings(
        not_exempt
    ), "the seam exemption is swallowing non-seam targets — it is not the shared one"


def test_a_symbol_import_is_not_reported_as_a_module(tmp_path):
    """`from x import SomeClass` names a CLASS, not a module.

    Reporting `company.billing.secret.SECRET` alongside `company.billing.secret`
    would triple the count with names that cannot be cut, and would make the
    allowlist un-diffable against the direct one.
    """
    root = _tree(tmp_path, {
        "simulation/run_probe.py": "from tools.helper import go\n",
        "tools/helper.py": "from company.billing.secret import SECRET, OTHER\n",
        "company/billing/secret.py": "SECRET = 2\nOTHER = 3\n",
    })
    found = indirect_crossings(root)
    assert set(found) == {("simulation.run_probe", "company.billing.secret")}, (
        f"symbol names leaked into the crossing set: {sorted(found)}"
    )


def test_a_module_that_imports_nothing_is_still_a_known_module(tmp_path):
    """The re-entry filter reads the FILESYSTEM, not the edge list.

    A module with no imports of its own produces no edges. Deriving the set of
    real module names from `{e.src for e in edges}` would drop it, and a route
    terminating there would silently disappear — fail-open by omission.
    """
    root = _tree(tmp_path, {
        "simulation/run_probe.py": "from tools.helper import go\n",
        "tools/helper.py": "from company.billing.constants import RATE\n",
        "company/billing/constants.py": "RATE = 0.05\n",   # imports nothing
    })
    assert ("simulation.run_probe", "company.billing.constants") in indirect_crossings(root)
    assert "company.billing.constants" in module_names(root, WALL_DIRS)


def test_a_bridge_import_cycle_terminates(tmp_path):
    """A cycle inside the bridge packages must not hang the checker."""
    root = _tree(tmp_path, {
        "simulation/run_probe.py": "from tools.a import go\n",
        "tools/a.py": "from tools.b import x\n",
        "tools/b.py": "from tools.a import go\nfrom company.billing.secret import SECRET\n",
        "company/billing/secret.py": "SECRET = 2\n",
    })
    found = indirect_crossings(root)
    assert ("simulation.run_probe", "company.billing.secret") in found


def test_the_walk_stops_at_re_entry(tmp_path):
    """Once a route lands back inside the wall, the direct walker owns it.

    Without this bound the checker reports the transitive closure of the
    codebase as laundering and the real finding drowns. `run_probe` reaches
    `sim.prices` only by way of a WALLED module, which is a plain sim->sim
    dependency, not a route around the instrument.
    """
    root = _tree(tmp_path, {
        "simulation/run_probe.py": "from tools.helper import go\n",
        "tools/helper.py": "from company.billing.secret import SECRET\n",
        "company/billing/secret.py": "from sim.prices import curve\n",
        "sim/prices.py": "curve = []\n",
    })
    found = indirect_crossings(root)
    assert set(found) == {("simulation.run_probe", "company.billing.secret")}


# --------------------------------------------------------------------------
# The addition to the shared walker must not have moved the DIRECT baseline.
# --------------------------------------------------------------------------

def test_submodule_targets_is_off_by_default_and_does_not_move_the_direct_walk():
    """`build_edges` grew a flag for this checker. The frozen direct census
    rests on that function, so the default path must be byte-identical — and
    the flag must actually do something, or it is decoration."""
    default = build_edges(REPO_ROOT, WALL_DIRS)
    widened = build_edges(REPO_ROOT, WALL_DIRS, submodule_targets=True)
    assert len(widened) > len(default), "the flag changed nothing — it is decoration"
    assert set(default).issubset(set(widened))
    assert company_reads_sim(default) == company_reads_sim(build_edges(REPO_ROOT, WALL_DIRS))
    assert sim_reads_company(default) == sim_reads_company(build_edges(REPO_ROOT, WALL_DIRS))


@pytest.mark.parametrize("bridge", BRIDGE_PACKAGES)
def test_each_declared_bridge_is_reported_on_by_name(bridge):
    """Every bridge gets an explicit verdict, including the clean ones.

    `interface/` is here because the direct ratchet has always CLAIMED it
    "cannot host a wall edge nor launder one". That claim was about direct
    edges and was never tested for indirect ones. It is now, and a silent pass
    for a package nobody names is how the original gap survived.
    """
    routed = {
        k: v for k, v in _live().items()
        if any(h.split(".", 1)[0] == bridge for h in v.entries)
    }
    assert set(routed).issubset(LEGACY_INDIRECT_CROSSINGS), (
        f"unallowlisted crossing(s) route through `{bridge}/`: "
        f"{sorted(set(routed) - LEGACY_INDIRECT_CROSSINGS)}"
    )
