"""Epistemic-wall import ratchet (NET tier, STATIC).

WHY THIS EXISTS
---------------
The project's core law is an epistemic wall (CLAUDE.md, "Architectural Laws —
Epistemic Honesty"): the company/business layer may only know what a real UK
energy supplier could observe, so it must not read simulation internals except
through a sanctioned interface seam. A July 2026 analysis counted on the order
of a hundred import crossings bypassing the seam. Nothing in the tree
PREVENTED crossing #107 — a new crossing could be added and no test would
notice.

This module makes the wall MEASURABLE and UN-REGRESSABLE, using the same
shrink-only ratchet pattern the project already applies elsewhere (a dated
allowlist of grandfathered edges, plus a stale-entry test that forces the
allowlist to shrink as edges are removed and can never silently grow).

  * A NEW crossing (an edge not in the dated allowlist) fails the suite,
    naming the edge and pointing at the wall doctrine.
  * A grandfathered edge later DELETED from the code must be removed from the
    allowlist too, or its stale entry fails the suite. The allowlist is
    therefore a one-way ratchet: it can only shrink.

PHASE-1 RECON — the two sides of the wall, and the seams
--------------------------------------------------------
Read directly from the code layout (evidence quoted in the PR body). The
perimeter was DISCOVERED by census, twice — see the lesson at the bottom.

COMPANY (business) side = {company, saas}. Two sibling top-level packages:
  * `company/` — pricing, billing, CRM, risk, trading, compliance, ...
  * `saas/`    — the business layer proper (customers, CLV/CAC, churn,
                 cost-to-serve, reporting). The July analysis named
                 `saas.customers` the most-depended-on module straddling the
                 wall. Omitting `saas/` would have left the single largest
                 crossing class (simulation->saas) invisible and reported the
                 strictly-forbidden direction (saas->sim) as zero.

SIM (simulated world) side = {sim, simulation}. Two sibling top-level packages:
  * `sim/`        — market/price/weather/forward-curve/risk engine.
  * `simulation/` — population, households, settlement, customer-behaviour
                    engine (household budgets, life events, demand physics,
                    meter reads). This is where the crossing mass lives.

SEAMS (sanctioned crossing surfaces):
  * `company.interfaces` (`company/interfaces/`), fronted by `sim_interface.py`
    whose docstring reads: "The company layer must only access simulation data
    through these methods — it cannot read simulation internals directly." An
    edge is EXEMPT iff its COMPANY-side endpoint module lives under
    `company.interfaces` — that is the single company<->sim crossing surface,
    in BOTH directions.
  * `interface/` (top-level, singular) is a SEPARATE, seam-related package: its
    README calls it "The seam. The *only* channel through which sim/ and saas/
    communicate ... Neither side imports the other directly; both sides depend
    only on what's defined here." It is NEITHER a COMPANY nor a SIM package, so
    no wall edge (company-side <-> sim-side) has an endpoint in it, and it is
    deliberately NOT granted seam-exemption in this checker (conservative — a
    genuine forbidden saas->sim import is a DIRECT edge and is caught
    regardless of whether the module also touches interface/; the two
    saas->simulation edges below prove that). Edges to/from `interface/` are
    therefore simply outside the ratchet's crossing definition and cannot
    launder a crossing.

SCOPE / KNOWN LIMIT (stated honestly)
-------------------------------------
This covers STATIC imports only — `import X` and `from X import Y`, resolved
with the stdlib `ast` module over a pure read of the tree. Dynamic imports
(`__import__`, `importlib.import_module`), `getattr`-driven access, and
string-eval escape it. That is a known, ACCEPTED limit of this (NET, static)
tier: it raises the cost of a static crossing to "you must edit a dated
allowlist and explain it in review", where the overwhelming majority of real
crossings land. A dynamic-import tier would be a separate, heavier instrument.

LESSON (recorded per the amendment that widened this ratchet)
-------------------------------------------------------------
Perimeter assumptions are themselves findings to verify. Both the SIM side
(sim/ + simulation/) and the COMPANY side (company/ + saas/) turned out to be
TWO packages, not one; each was established by an independent AST census, not
assumed from the directory that shares the concept's name. A wall checker is
only as honest as its perimeter.

WHERE THE DEFINITION LIVES (changed 2026-08-09, KNIFE pass 3 first step)
------------------------------------------------------------------------
The perimeter, the AST walker and the two classifiers used to live in THIS
file, and three instruments answered "is this a crossing?" from three private
copies. They now live once, in `tools/epistemic_wall.py`, and this
module imports them — as do `tools/knife_hotspot_measure.py` (the ledger) and
`tools/epistemic_verifier.py` (the phase-close scanner). One definition, three
consumers with different jobs.

What did NOT move, deliberately: the dated allowlists below. They are this
gate's frozen POLICY baseline, reviewed every time they shrink; the shared
module is the DEFINITION, which no pass edits. Keeping them apart is what lets
a pass say "the walker was not edited" and mean it, and it means no tool can
silence this gate by import.

Dependencies: pytest + Python stdlib (`ast`, `os`) only — the shared module is
stdlib-only for exactly this reason, so this suite still runs when the app's
runtime deps are absent.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tools.epistemic_wall import (  # noqa: E402
    COMPANY_PACKAGES,
    REPO_ROOT,
    SEAM_PACKAGE,
    SIM_PACKAGES,
    WALL_DIRS,
    WALL_DOCTRINE,
    RawEdge,
    build_edges,
    company_reads_sim,
    sim_reads_company,
)
from tools.epistemic_wall import (
    top_package as _top,
)
from tools.epistemic_wall import (
    under_seam as _under_seam,
)

__all__ = [
    "COMPANY_PACKAGES",
    "REPO_ROOT",
    "SEAM_PACKAGE",
    "SIM_PACKAGES",
    "WALL_DIRS",
    "WALL_DOCTRINE",
    "RawEdge",
    "build_edges",
    "company_reads_sim",
    "sim_reads_company",
]


# --------------------------------------------------------------------------
# The dated, shrink-only allowlists (the ratchet baseline).
#
# Baseline frozen 2026-08-05 from a pure static walk of the tree on the
# `claude/epistemic-wall-import-ratchet-jnw2dl` branch, over the WIDENED
# perimeter {company, saas} <-> {sim, simulation}. Each tuple is a
# (source_module, target_module) edge grandfathered on that date. Rules:
#   * The lists may only SHRINK. Removing a wall crossing from the code must be
#     matched by deleting its tuple here (enforced by the stale-entry tests).
#   * A NEW crossing must NOT be added here to silence the suite — route it
#     through the seam instead. An addition here is a reviewable, deliberate act
#     that says "this legacy edge is acknowledged and owed a paydown".
# --------------------------------------------------------------------------

# Class (a) — company-side (company/, saas/) importing SIM internals other than
# via the seam. Census on 2026-08-05: 2 edges, BOTH the strictly-forbidden
# `saas -> simulation` direction — the business layer directly importing the
# simulated world's run harness. (`company/` itself read SIM internals only
# inside the seam file, and still does.)
#
# 2026-08-09, KNIFE pass 1 (atom `KNIFE1_reporting_cycle`): both were PAID
# DOWN, and class (a) is now EMPTY. `saas.reporting.annual_report ->
# simulation.run_phase4c_on_phase2b` and `saas.reporting.segment_report ->
# simulation.run_segments` were both CLI composition, not reporting: the run
# entry points moved above both layers to `tools/run_annual_report.py` and
# `tools/run_segment_report.py`. Neither reporting module names `simulation`
# in any form now.
#
# An EMPTY allowlist makes `test_company_reads_sim_allowlist_has_no_stale_
# entries` vacuous for this direction (it has nothing left to find stale) —
# stated rather than glossed, per R15. The live controls for class (a) are
# `test_no_new_company_reads_sim` (any new edge is now a hard failure with no
# grandfathering left to hide behind), its mutation proof, and
# `test_mutation_walker_detects_physical_crossings_on_disk`, all of which still
# fire. The direction is not unmeasured; it is at zero, and the ratchet's
# floor for it is now the floor.
LEGACY_COMPANY_READS_SIM: frozenset[tuple[str, str]] = frozenset()

# Class (b) — sim.*/simulation.* importing company-side internals other than
# via the seam. Census on 2026-08-05: 105 edges (59 simulation->saas from 61
# import statements, + 46 simulation->company); `sim/` itself reads the company
# side zero times. The simulation->saas mass is the largest crossing class in
# the codebase and was invisible before the perimeter was widened to include
# saas/.
#
# 2026-08-09, KNIFE pass 1: 105 -> 104. `simulation.run_phase4c_on_phase2b ->
# saas.reporting.annual_report` deleted — the return edge that closed the
# reporting import cycle. It reduced the run's output through the report's
# `extract_report_data`, a reporting concern the run module had absorbed; that
# code now lives in `tools/run_annual_report.py`.
#
# 2026-08-10, KNIFE pass 3 (atom `KNIFE3_wall_crossing_paydown`, step 11,
# `A_composition_lift`): three edges deleted —
# `simulation.run_phase4c_on_phase2b -> {company.billing.back_billing,
# company.billing.account_adjustment_register, saas.bill_generator}`. Monthly
# bill assembly moved to `company/billing/monthly_bill_assembly.py` behind
# `company.interfaces.bill_assembly`: assembling a bill from settled records,
# deciding estimated-vs-actual, and reconciling a run of estimates under the
# Ofgem SLC 31A cap are the supplier's own routine, not world physics. The world
# now hands over records and a read feed and takes back bills.
#
# The direction the read goes is the reason this is a cut rather than a file
# move. Whether a read ARRIVES is world physics, so the company does not import
# `simulation.meter_reads`; it receives a `ReadArrivalFeed`
# (`simulation.meter_reads.SimulatedReadFeed`). Carrying those imports across
# would have traded three class-(b) edges for three class-(a) ones — the
# forbidden direction, which is at zero and stays there.
#
# 2026-08-11, KNIFE pass 3 step 14, same design: three more deleted —
# `simulation.run_phase4c_on_phase2b -> {company.billing.pre_bill_validation,
# saas.ledger, company.compliance.domain_invariants}`. The supplier's month-end
# CLOSE moved to `company/finance/accounting_close.py` behind
# `company.interfaces.accounting_close`: the Tier-1 issuance gate, the shaping of
# the cost-to-serve schedule into account-6100 events, double-entry posting, the
# P&L derivation and the billed-clock reconciliation are all the supplier's own
# routine, changeable without telling the world anything. The world hands over
# its settled records and the spend schedules as DATA and takes back closed books.
#
# Same inversion test as bill assembly: `company/finance/accounting_close.py`
# imports nothing from `simulation/` or `sim/` — the records arrive through the
# signature — so no class-(a) edge is created. `tests/company/interfaces/
# test_accounting_close_seam.py` proves that BEHAVIOURALLY (a real close in a
# clean interpreter, then which modules loaded), because a lazy in-function
# import is invisible to this file by its own documented limit.
#
# 2026-08-11, KNIFE pass 3 step 15, same design: four more deleted —
# `simulation.run_phase4c_on_phase2b -> saas.{cost_to_serve, churn_model,
# home_move_win_rate, enterprise_value}`. The supplier's CUSTOMER-VALUE layer
# moved to `company/analytics/customer_value_view.py` behind
# `company.interfaces.customer_value`: how it apportions cost to a customer,
# what it believes about who will leave, what it pays to keep a mover and what
# it thinks its book is worth are its own models, wrong or right, and the world
# never sees them. It hands over the settled records and the customer book as
# DATA and takes back a `CustomerValueView`.
#
# Taken as a GROUP, not four items, because the four have a dependency chain
# inside them (home-move needs churn; enterprise value needs churn AND cost to
# serve). Cutting singly would have left the world holding the intermediates and
# threading them back — the count would fall while the coupling stayed.
#
# Same inversion test as the close: `company/analytics/customer_value_view.py`
# imports nothing from `simulation/` or `sim/` — records and customers arrive
# through the signature — so no class-(a) edge is created. The run's market
# position (`PRICE_DIFFERENTIAL_PCT`) is PASSED, so no world constant crosses to
# set it, and `tests/company/interfaces/test_customer_value_seam.py` moves it and
# asserts the view moves rather than trusting that it is read.
#
# 2026-08-09, KNIFE pass 2 (atom `KNIFE2_customer_straddle`): 104 -> 88. All
# SIXTEEN `simulation.* -> saas.customers` edges deleted — the customer module
# straddling the wall, the single most-reached company module in the codebase.
# They now route through `company.interfaces.supply_book`, which IS the
# sanctioned seam and is therefore exempt by the rule at the top of this file,
# not by escaping the walker: `company/interfaces/**` is walked exactly as
# before, and any `simulation -> saas.customers` edge reappearing anywhere in
# the tree is now a HARD failure with no grandfathering left for it to hide
# behind. Note the honest limit — the seam ROUTES the crossing, it does not
# remove the dependency: the same records cross, at one reviewable chokepoint
# instead of sixteen unreviewable ones, and the field-level narrowing a real
# MPAN registration would apply is owed to pass 3 / the Epoch-3 adapters. That
# limit is stated in the seam module's own docstring so it cannot be read as
# a clean break.
LEGACY_SIM_READS_COMPANY: frozenset[tuple[str, str]] = frozenset({
    ("simulation.customer_events", "company.crm.churn_model"),
    ("simulation.customer_events", "saas.churn_model"),
    ("simulation.customer_events", "saas.customer_reaction"),
    ("simulation.customer_events", "saas.home_move_win_rate"),
    # ("simulation.dd_collection_book", "company.billing.direct_debit") — CUT
    # 2026-08-10 by KNIFE pass 3, design B4, the LAST of that design's four edges
    # and the one its block called the hard one: the world was not consulting the
    # supplier's billing module, it was OPERATING the supplier's collection
    # register — opening a `DirectDebitBook`, creating mandates on it, deciding
    # when the standing amount had drifted far enough to amend, and appending
    # `DDPaymentAttempt`s. The supplier now runs its own desk
    # (`company/billing/dd_collections_desk.py`) and ISSUES setup, amendment and
    # collection instructions through `company/interfaces/dd_collection_instructions.py`;
    # the world puts them on the Bacs rails and reports what happened to the money.
    # ("simulation.hedged_settlement", "company.pricing.ofgem_price_cap") — CUT
    # 2026-08-10 by KNIFE pass 3, design B3. The world now enforces the cap from
    # its own reading of the published commons artefact
    # (`simulation/price_cap_enforcement.py`); the company keeps its reading and
    # the two are free to differ.
    # ("simulation.run_phase2b", "company.crm.complaints") — CUT
    # ("simulation.run_phase2b", "company.crm.nps_tracker") — CUT
    # ("simulation.run_phase2b", "company.crm.payment_behaviour_analytics") — CUT
    # ("simulation.run_phase2b", "company.crm.satisfaction_accumulator") — CUT
    # all four 2026-08-13 by KNIFE pass 3, design A_composition_lift step 21
    # (§3p). The run loop was OPENING the supplier's four customer-experience
    # books and making its bookkeeping decisions at nine call sites: that a bill
    # shock costs trust, that a CSAT answer and an NPS answer land in different
    # books, that satisfaction decays twelve months per term, that a complaint
    # about a bill is filed under BILLING. The supplier now runs one desk
    # (`company/crm/customer_experience_desk.py`) behind
    # `company/interfaces/customer_experience.py`; the world reports the term
    # boundary, the answered survey, the contact and the payment outcome.
    # KNIFE pass 3, `A_composition_lift` step 22 (register §3q) removed the last
    # two CRM crossings on this module. `customer_profitability`: the world
    # carried the supplier's own eligibility rule for repricing an unprofitable
    # renewal (first term or later, electricity, fixed or pass-through, a locked
    # rate to adjust) and only then asked for a number; that rule is now behind
    # `company/interfaces/customer_profitability.py`. `tpi_book`: the world
    # registered the supplier's broker, chose its tier, basis, rate and
    # registration date, decided a deal is one customer-year and read the book's
    # PRIVATE `_deals` list to publish a count; all of it is now behind
    # `company/interfaces/tpi_commission.py`. Two doors, not one — an uplift
    # inside the renewal loop and a channel cost booked once at year end do not
    # feed one total, and naming a desk over both would invent an object the
    # business does not have.
    ("simulation.run_phase2b", "company.policy.decision_policy"),
    ("simulation.run_phase2b", "company.pricing.margin_feedback"),
    ("simulation.run_phase2b", "company.pricing.ofgem_price_cap"),
    ("simulation.run_phase2b", "company.pricing.tariff_engine"),
    ("simulation.run_phase2b", "company.risk.hedge_policy"),
    ("simulation.run_phase2b", "company.trading.forward_book"),
    ("simulation.run_phase2b", "company.trading.hedge_decision"),
    ("simulation.run_phase2b", "saas.cost_to_serve"),
    ("simulation.run_phase2b", "saas.customer_reaction"),
    ("simulation.run_phase2b", "saas.demand_response"),
    ("simulation.run_phase2b", "saas.growth_mandate"),
    ("simulation.run_phase2b", "saas.ledger"),
    ("simulation.run_phase2b", "saas.property_model"),
    ("simulation.run_phase2b", "saas.smart_meter_rollout"),
    ("simulation.run_phase2b", "saas.tariff_pricing"),
    ("simulation.run_phase4c_on_phase2b", "company.billing.dd_review_runner"),
    # ("simulation.run_phase4c_on_phase2b", "company.billing.pre_bill_validation")
    # and ("…", "company.compliance.domain_invariants") -- 2 tuples DELETED
    # 2026-08-11 by `A_composition_lift` step 14, with `saas.ledger` below. The
    # supplier's month-end close moved to `company/finance/accounting_close.py`
    # behind `company.interfaces.accounting_close`. See the block comment above.
    # ("simulation.run_phase4c_on_phase2b", "saas.{churn_model,cost_to_serve,
    # enterprise_value,home_move_win_rate}") -- 4 tuples DELETED 2026-08-11 by
    # `A_composition_lift` step 15. See the block comment above.
    # ("simulation.run_phase4c_on_phase2b", "saas.ledger") -- DELETED 2026-08-11,
    # the third of step 14's edges.
    # ("simulation.run_phase4c_on_phase2b", "saas.{contact_model,payment_behaviour}")
    # -- 2 tuples DELETED 2026-08-11 by `A_composition_lift` step 16 (register §3k).
    # The supplier's billing-experience layer moved to
    # `company/analytics/billing_experience_view.py` behind
    # `company.interfaces.billing_experience`. `saas.payment_behaviour` is the edge
    # step 14 explicitly recorded as NOT falling with `saas.ledger`, because
    # `build_payment_behaviour(bills)` was still called world-side for this output;
    # step 16 is the group that was named there, so the debt is now paid rather than
    # restated. `company.billing.dd_review_runner` above is the module's last, and
    # §3h rules it a ROUTING residual rather than a cut still owed.
    # ("simulation.run_segments", "saas.{growth_mandate,ledger,property_model,tariff_pricing}")
    # -- 4 tuples DELETED 2026-08-10 by `A_composition_lift` PART 2. The file moved to
    # `tools/run_segments.py`, where entry points live, having passed the four conditions §3c of
    # the disposition register sets; its condition-4 leak (the world's hedge mandate deciding the
    # company's naked fraction) was REPAIRED by the B7 template in the same commit rather than
    # relocated. The floor moves down with the code: none of the four can return silently.
    #
    # 2026-08-10, KNIFE pass 3 step 12 (`B3_world_needs_its_own_cap_physics`, applied a
    # SECOND time — register §3g): `simulation.satisfaction_churn -> saas.churn_model`
    # deleted. The world was clamping its own ground-truth churn probability at the
    # COMPANY's `MAX_CHURN_PROBABILITY`, so the company's belief about the ceiling
    # constituted the ceiling — B2's inversion at one edge. The world's ceiling now lives
    # in `simulation/churn_ceiling.py`; the company keeps its estimate; both are 0.95, so
    # no simulated outcome moved. Independence is proven by mutation with a vacuity guard
    # in `tests/simulation/test_churn_ceiling.py`, NOT by a test pinning the two equal —
    # that would restore the coupling in the suite (B3's and B7's recorded refusal).
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
# Tests — Phase-1 recon assertions.
# --------------------------------------------------------------------------

def test_seam_package_exists_and_is_the_crossing_surface():
    """The sanctioned company<->sim seam is `company/interfaces/` — verify it.

    Guards the recon finding this whole ratchet rests on: if the seam were
    renamed or removed, the exemption logic would silently mislabel edges.
    """
    seam_dir = os.path.join(REPO_ROOT, *SEAM_PACKAGE.split("."))
    assert os.path.isdir(seam_dir), f"seam package dir missing: {seam_dir}"
    assert os.path.isfile(os.path.join(seam_dir, "sim_interface.py")), (
        "expected the seam front-door module company/interfaces/sim_interface.py"
    )


def test_both_wall_sides_exist():
    """Both packages on each side of the widened perimeter are present."""
    for pkg in SIM_PACKAGES | COMPANY_PACKAGES:
        assert os.path.isdir(os.path.join(REPO_ROOT, pkg)), f"wall-side package missing: {pkg}/"


def test_interface_seam_is_classified_and_not_a_wall_side():
    """`interface/` is the sim<->saas seam, and is neither a COMPANY nor a SIM
    package — so it cannot host a wall edge nor launder one.

    Conservative treatment ("when unsure, non-exempt"): interface/ is NOT in the
    seam-exemption path, and because it is in neither wall side, no
    company-side<->sim-side edge can route an endpoint through it. A real
    forbidden saas->sim import is a DIRECT edge and is caught regardless.
    """
    assert os.path.isdir(os.path.join(REPO_ROOT, "interface")), "interface/ package missing"
    assert "interface" not in COMPANY_PACKAGES
    assert "interface" not in SIM_PACKAGES
    assert not _under_seam("interface.contracts.wall_envelope")
    # Empirically: walking the wall dirs, no classified crossing has an
    # `interface`-package endpoint (interface/ is not even in WALL_DIRS).
    edges = _real_edges()
    for by_key in (company_reads_sim(edges), sim_reads_company(edges)):
        for src, dst in by_key:
            assert _top(src) != "interface" and _top(dst) != "interface"


# --------------------------------------------------------------------------
# Tests — new crossings fail (the wall).
# --------------------------------------------------------------------------

def test_no_new_company_reads_sim():
    """No company-side import of SIM internals outside the seam/allowlist.

    This is the strictly forbidden direction.
    """
    edges = company_reads_sim(_real_edges())
    new = set(edges) - LEGACY_COMPANY_READS_SIM
    assert not new, (
        "NEW epistemic-wall crossing(s) in the FORBIDDEN direction: company-side "
        "internals importing SIM internals outside the seam and not in the dated "
        "allowlist:\n"
        + _fmt(edges, new)
        + "\n\n"
        + WALL_DOCTRINE
    )


def test_no_new_sim_reads_company():
    """No SIM import of company-side internals outside the seam/allowlist."""
    edges = sim_reads_company(_real_edges())
    new = set(edges) - LEGACY_SIM_READS_COMPANY
    assert not new, (
        "NEW epistemic-wall crossing(s): SIM internals importing company-side "
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

# Synthetic edges guaranteed absent from the real tree. The class-(a) probe is
# a SAAS-side crossing (the widened company perimeter's dominant class).
_SYNTH_COMPANY_READS_SIM = RawEdge(
    src="saas.reporting.annual_report",
    dst="sim.weather_engine",
    path="saas/reporting/annual_report.py",
    lineno=1,
)
_SYNTH_SIM_READS_COMPANY = RawEdge(
    src="sim.forward_curve",
    dst="saas.customers",
    path="sim/forward_curve.py",
    lineno=1,
)


def test_mutation_injected_company_reads_sim_reds_only_new_crossing():
    """Inject a saas->SIM crossing in memory; assert precise blast radius."""
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
    """Inject a SIM->saas crossing in memory; assert precise blast radius."""
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


def test_mutation_walker_detects_physical_crossings_on_disk(tmp_path):
    """End-to-end proof the AST WALKER (not just set arithmetic) catches real
    crossings on disk — including a SAAS-side one — from BOTH `company/` and
    `saas/` against BOTH sim packages.

    This closes the fail-open gap where the classifier is correct but the
    walker never produced the edge in the first place.
    """
    # company/rogue.py imports sim.weather_engine
    comp = tmp_path / "company"
    comp.mkdir()
    (comp / "__init__.py").write_text("")
    (comp / "rogue.py").write_text("from sim.weather_engine import secret_internal\n")

    # saas/rogue.py imports simulation.household (the saas-side probe)
    saas = tmp_path / "saas"
    saas.mkdir()
    (saas / "__init__.py").write_text("")
    (saas / "rogue.py").write_text(
        "import simulation.household\n"
        "from sim.forward_curve import build_curve\n"
    )

    for pkg in ("sim", "simulation"):
        d = tmp_path / pkg
        d.mkdir()
        (d / "__init__.py").write_text("")
    (tmp_path / "sim" / "weather_engine.py").write_text("secret_internal = 42\n")

    edges = build_edges(str(tmp_path), WALL_DIRS)
    c2s = company_reads_sim(edges)
    assert ("company.rogue", "sim.weather_engine") in c2s
    assert ("saas.rogue", "simulation.household") in c2s
    assert ("saas.rogue", "sim.forward_curve") in c2s


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
    """On today's tree: class (a) == EMPTY (both saas->simulation edges paid
    down by KNIFE pass 1, 2026-08-09), class (b) == the 104 frozen
    SIM->company-side edges (105 minus the reporting-cycle return edge)."""
    edges = _real_edges()
    assert set(company_reads_sim(edges)) == LEGACY_COMPANY_READS_SIM
    assert set(sim_reads_company(edges)) == LEGACY_SIM_READS_COMPANY
