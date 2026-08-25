"""B3 — the regulation commons holds the LAW; each lane holds its own READING.

KNIFE pass 3, design block `B3_world_needs_its_own_cap_physics`, 2026-08-10.

The cut removed `simulation.hedged_settlement -> company.pricing.ofgem_price_cap`.
The design block refused to let that happen until three questions were answered,
because the cheap version of this cut is a laundering: relocate the schedule
somewhere the wall walker cannot see, watch the edge count fall by one, and change
nothing about who depends on whom.

  (a) WHERE does the published schedule live, and is that home walked?
  (b) HOW is divergence controlled, without a test that pins the two readings
      equal and thereby restores the coupling in the suite?
  (c) WHAT is each side allowed to get wrong?

This module is the answer to (a) and (b) as MECHANISM. (c) is answered in prose in
`simulation/price_cap_enforcement.py`, and the tests below are what stop that prose
from being decorative.

R15: every control here names the mutation that must make it fire.
"""

from __future__ import annotations

import ast
import importlib
import json
from datetime import date, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
COMMONS_DIR = REPO_ROOT / "docs" / "domain_artefact_library" / "regulatory"
ARTEFACT = COMMONS_DIR / "ofgem_default_tariff_cap_windows.json"

COMPANY_READING = REPO_ROOT / "company" / "pricing" / "ofgem_price_cap.py"
WORLD_READING = REPO_ROOT / "simulation" / "price_cap_enforcement.py"


# ---------------------------------------------------------------------------
# (a) The home is not walked — and cannot launder a dependency, because it is
#     inert. That is the whole difference from the `tools/` move this pass
#     refused, and it is asserted rather than assumed.
# ---------------------------------------------------------------------------

def test_the_commons_home_is_data_only_and_therefore_cannot_hide_a_dependency():
    """MUTATION (must fire): drop any `.py` file into
    `docs/domain_artefact_library/regulatory/` — even an empty one.

    `tools/epistemic_wall.py` does not walk `docs/`. For a CODE home that would be
    fatal: an unwalked module can import from either side of the wall, so routing
    a crossing through it moves the measurement rather than the dependency (the
    same laundering KNIFE pass 1 refused, and the `moving a file past the walker
    is not a cut` class). A DATA home has no such capacity: JSON has no import
    statement. The safety of the unwalked home rests entirely on it staying data,
    so that is what is checked — not the claim, the property.
    """
    assert COMMONS_DIR.is_dir(), f"regulation commons directory missing: {COMMONS_DIR}"
    code = sorted(p.relative_to(REPO_ROOT).as_posix() for p in COMMONS_DIR.rglob("*.py"))
    assert code == [], (
        "The regulation commons must hold DATA ONLY. These Python files make it an "
        f"unwalked code path, which is a laundering channel for wall crossings: {code}"
    )


def test_the_artefact_carries_its_law_and_its_basis():
    """MUTATION (must fire): delete the `basis` block, or the `windows` list.

    R14: a published figure without its clock/basis is a defect, and this artefact
    is read by two independent lanes that would otherwise each have to guess
    whether the levels include VAT and whether the standing charge is in them.
    """
    raw = json.loads(ARTEFACT.read_text())
    assert raw["windows"], "the commons artefact must carry the published windows"
    basis = raw["basis"]
    assert basis["units"] == "GBP per MWh"
    assert "VAT" in basis["vat"]
    assert "EXCLUDED" in basis["standing_charge"]
    # The EPG is published as a SEPARATE overlay, never pre-combined, so that a
    # lane which fails to notice it has MISREAD the law rather than been handed a
    # different law. If this ever becomes zero the artefact has been flattened.
    epg_windows = [w for w in raw["windows"] if "elec_epg" in w or "gas_epg" in w]
    assert len(epg_windows) >= 3, (
        "the EPG overlay has been flattened into the cap levels; the two "
        "instruments must stay separately readable"
    )


# ---------------------------------------------------------------------------
# (b) Divergence control, part 1: THE LAW CANNOT DRIFT, because neither lane is
#     permitted to hand-write a schedule of its own.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("reading", [COMPANY_READING, WORLD_READING], ids=["company", "world"])
def test_neither_lane_hand_writes_the_published_schedule(reading: Path):
    """MUTATION (must fire): paste a literal window table back into either module
    — e.g. `{"from": date(2021, 10, 1), ..., "elec": 208.0}`.

    This is the `one name, two numbers` guard, and it is the reason the readings
    are allowed to diverge freely below: they may differ in how they INTERPRET the
    law, never in what the law SAYS. Two hand-written cap tables drifting apart
    silently would be a fidelity defect in both lanes at once.

    The predicate is the WINDOW BOUNDARIES, and the two rejected alternatives are
    recorded because each failed on this file's real contents rather than in
    theory:

    * A SUBSTRING scan over the text flagged the module for CITING `208.0` in a
      comment explaining the Apr-2022 step. A control that cannot tell an
      explanation from a table forces the reasoning out of the file to stay green
      — the same class as matching on prose that merely mentions a marker.
    * Scanning for published LEVELS as code literals then flagged `35.0` — which
      is `_GAS_CAP_GBP_PER_MWH[2021]`, a value in the company's ANNUAL BLEND, and
      it collides with the Apr-2020 published gas level by coincidence. The
      annual blend is not the law: Ofgem never published annual averages, they
      are this company's own coarse approximation, and §(c) explicitly leaves
      them company-owned. Widening the exemption to `35.0` would have been
      moving the threshold to fit the answer; narrowing the STATISTIC to the
      thing that actually identifies a schedule is the honest repair.

    A boundary cannot collide: `date(2021, 10, 1)` or `"2021-10-01"` in code is a
    cap-window edge and nothing else. A restated schedule needs its boundaries —
    levels alone are not a schedule, they are a lookup nobody can key.
    """
    source = reading.read_text()
    raw_windows = json.loads(ARTEFACT.read_text())["windows"]
    boundaries = {w["from"] for w in raw_windows} | {w["to"] for w in raw_windows}

    # The module must reach the artefact rather than restate it.
    assert "ofgem_default_tariff_cap_windows.json" in source, (
        f"{reading.name} does not read the regulation commons"
    )

    tree = ast.parse(source)
    restated: set[str] = set()
    for node in ast.walk(tree):
        # ISO strings: "2021-10-01"
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in boundaries:
                restated.add(node.value)
        # Constructor form: date(2021, 10, 1)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "date":
            parts = [a.value for a in node.args if isinstance(a, ast.Constant)]
            if len(parts) == 3 and all(isinstance(p, int) for p in parts):
                try:
                    iso = date(*parts).isoformat()
                except ValueError:
                    continue
                if iso in boundaries:
                    restated.add(iso)

    assert sorted(restated) == [], (
        f"{reading.name} restates published cap-window boundaries in code: "
        f"{sorted(restated)}. The law is single-sourced in the commons; only the "
        "READING lives here."
    )


# ---------------------------------------------------------------------------
# (b) Divergence control, part 2: THE READINGS MAY DRIFT, and the harness can
#     SEE it. Deliberately not a test that they agree.
# ---------------------------------------------------------------------------

def _published_span() -> list[date]:
    raw = json.loads(ARTEFACT.read_text())["windows"]
    first = date.fromisoformat(raw[0]["from"])
    last = date.fromisoformat(raw[-1]["to"])
    days, d = [], first - timedelta(days=45)
    while d <= last + timedelta(days=400):
        days.append(d)
        d += timedelta(days=11)
    return days


def cap_reading_divergence() -> list[tuple[date, str, float | None, float | None]]:
    """Every date+fuel where the two lanes' readings of the cap differ.

    A DIAGNOSTIC, not a gate (R12). Nothing asserts this is empty — the readings
    are independently owned and a supplier misreading the cap is a fidelity
    feature. It exists so that divergence is a visible event rather than a silent
    one.

    BOTH SIDES ARE READ INC-VAT, which is the basis the commons publishes, so
    what this reports is a divergence in the READING and never an artefact of
    units. The world's ex-VAT accessor exists for comparison against a settled
    rate, not for comparison against the company's belief.
    """
    from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date
    from simulation.price_cap_enforcement import binding_cap_unit_rate_gbp_per_mwh_inc_vat

    out = []
    for d in _published_span():
        for fuel in ("electricity", "gas"):
            company = get_cap_unit_rate_for_date(fuel, d)
            world = binding_cap_unit_rate_gbp_per_mwh_inc_vat(fuel, d)
            if company != world:
                out.append((d, fuel, company, world))
    return out


def test_the_two_readings_are_independent_and_the_harness_can_prove_it(monkeypatch):
    """ANTI-TAUTOLOGY. The named failure this guards: someone 'simplifies' the
    world's reading back into a call to the company's, the divergence report goes
    permanently empty, and nothing notices — which is the state the cut removed.

    MUTATION (must fire): make `simulation.price_cap_enforcement.
    binding_cap_unit_rate_gbp_per_mwh_inc_vat` delegate to
    `company.pricing.ofgem_price_cap.get_cap_unit_rate_for_date`.

    The mutation is injected on the COMPANY side, and the assertion is that the
    WORLD does not move. Injecting on the company side is what makes this a test
    of independence rather than of arithmetic: if the world still consulted the
    company, the company's misreading would propagate.
    """
    import company.pricing.ofgem_price_cap as company_cap
    from simulation.price_cap_enforcement import binding_cap_unit_rate_gbp_per_mwh_inc_vat

    probe = date(2022, 2, 15)  # inside the Oct-2021 window, the crisis one
    world_before = binding_cap_unit_rate_gbp_per_mwh_inc_vat("electricity", probe)

    # The company misreads the law: it forgets that the cap moved mid-year and
    # falls back to its own annual blend. A real, plausible misreading, and
    # exactly the defect W3_1b was raised to fix.
    monkeypatch.setattr(
        company_cap,
        "get_cap_unit_rate_for_date",
        lambda fuel, on_date: company_cap.get_cap_unit_rate_gbp_per_mwh(fuel, on_date.year),
    )

    # VACUITY GUARD: the mutation must actually change the company's answer,
    # otherwise "the world did not move" proves nothing about independence.
    company_after = company_cap.get_cap_unit_rate_for_date("electricity", probe)
    assert company_after != world_before, (
        "the injected misreading changed nothing on the company side, so this "
        "test would pass even if the world still read the company's answer"
    )

    world_after = binding_cap_unit_rate_gbp_per_mwh_inc_vat("electricity", probe)
    assert world_after == world_before, (
        "the world's enforced ceiling moved when the COMPANY's reading was "
        "mutated — the lanes are still coupled"
    )

    # And the diagnostic can see it. Not asserted to be empty in the clean tree
    # (R12), only asserted to be CAPABLE of reporting — a divergence report that
    # can never be non-empty is as blind as no report at all.
    assert cap_reading_divergence(), (
        "the divergence diagnostic reported nothing while the two readings were "
        "provably disagreeing"
    )


def test_the_divergence_diagnostic_is_reported_not_gated():
    """The clean-tree state, RECORDED rather than enforced.

    Today both lanes read the published law correctly and agree everywhere. That
    is an observation about this commit, not a property anything holds them to —
    pinning it would restore the coupling in the suite that the cut removed from
    the code (the trap B3's design block named, and B7 refused for the hedge
    floor). So this test prints the divergence and asserts only that the
    diagnostic RAN over a real span.
    """
    span = _published_span()
    assert len(span) > 200, "the divergence sweep must cover the published span"
    divergences = cap_reading_divergence()
    print(f"cap reading divergence: {len(divergences)} of {len(span) * 2} (date, fuel) points")
    for row in divergences[:20]:
        print("  ", row)


# ---------------------------------------------------------------------------
# Fail-open and fail-silent (R15's other two killer patterns), both lanes.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "module_name",
    ["company.pricing.ofgem_price_cap", "simulation.price_cap_enforcement"],
    ids=["company", "world"],
)
@pytest.mark.parametrize("breakage", ["missing", "empty", "malformed"])
def test_an_unreadable_commons_is_an_error_never_an_uncapped_market(
    module_name: str, breakage: str, tmp_path, monkeypatch
):
    """MUTATION (must fire): replace either loader's `raise` with `return []`.

    FAIL-OPEN is the pattern with teeth here. Both lookups return `None` to mean
    "no cap applied", and `None` is then used by callers as "do not clamp". A
    loader that swallowed a missing artefact and returned an empty schedule would
    therefore un-cap every domestic customer in the simulation — silently, and in
    the direction that flatters margin. An unreadable law is a failure, not a
    licence.
    """
    module = importlib.import_module(module_name)
    broken = tmp_path / "ofgem_default_tariff_cap_windows.json"
    if breakage == "empty":
        broken.write_text(json.dumps({"windows": []}))
    elif breakage == "malformed":
        broken.write_text("{not json at all")
    # "missing" leaves the path non-existent.

    monkeypatch.setattr(module, "_CAP_WINDOWS_ARTEFACT", broken)
    with pytest.raises((FileNotFoundError, ValueError, json.JSONDecodeError)):
        module._load_published_windows()


@pytest.mark.parametrize(
    "module_name",
    ["company.pricing.ofgem_price_cap", "simulation.price_cap_enforcement"],
    ids=["company", "world"],
)
def test_past_the_published_schedule_the_last_level_still_binds(module_name: str):
    """MUTATION (must fire): return `None` past the last published window.

    Both lanes reach this conclusion INDEPENDENTLY and for the same stated reason
    (the cap is a standing statutory instrument), which is why it is checked on
    both rather than on one. It is the fail-open case that motivated the rule.
    """
    module = importlib.import_module(module_name)
    lookup = (
        module.get_cap_unit_rate_for_date
        if module_name.startswith("company")
        else module.binding_cap_unit_rate_gbp_per_mwh_inc_vat
    )
    far_future = date.today().replace(year=date.today().year + 40)
    assert lookup("electricity", far_future) is not None
    assert lookup("gas", far_future) is not None


# ---------------------------------------------------------------------------
# The cut itself.
# ---------------------------------------------------------------------------

def test_the_world_does_not_import_the_companys_cap_reading():
    """MUTATION (must fire): restore
    `from company.pricing.ofgem_price_cap import get_cap_unit_rate_for_date`
    in `simulation/hedged_settlement.py`.

    Belt to the wall ratchet's braces, and deliberately narrower than it: the
    ratchet enforces a shrinking allowlist across the whole tree, while this names
    the ONE edge B3 cut, so a re-entry says which design block it violated.

    MEASURED WITH THE SHARED WALKER, and the first draft of this control was a
    substring scan that failed on its own subject: the comment recording WHY the
    import went away contains the module's dotted name. `REVIEW_GATE must only
    match on actual idleness, not on prose mentioning the string` is the same
    lesson, and the fix is the same — ask the instrument that defines what an
    import IS, which is also the one this pass extracted as its first step.
    """
    from tools.epistemic_wall import live_crossings

    cut_edge = ("simulation.hedged_settlement", "company.pricing.ofgem_price_cap")
    offending = [edge for edge in live_crossings() if edge == cut_edge]
    assert offending == [], (
        "simulation/hedged_settlement.py imports the company's reading of the "
        "price cap again — B3 cut that edge. The world enforces the cap from "
        "simulation/price_cap_enforcement.py, which reads the published law."
    )
