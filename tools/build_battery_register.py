"""Regenerate tests/domain/battery_register.yaml from the scope briefs.

The AO2 REUSE record for this module is at the end of its COMMIT MESSAGE, not
in this docstring. Not a style choice: AO2's `parse_records` runs a field's
value from its head to the next head, and `INDEX:` is the last head in a CUSTOM
record, so a record placed above code swallows the whole module and G6 then
fires on any later prose containing "no"/"none"/"nothing"
(docs/staging/WORKER_FINDING_WRITE_TIME_GATE_FIELD_SWALLOW_2026-08-08.md).

The battery TEXT is never hand-typed: it is parsed out of the briefs, so the
register cannot drift from the purchased judgement it is supposed to carry.
Only the DISPOSITION of each line is authored here.

Re-run after a brief changes:  python3 tools/build_battery_register.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tests.domain.battery_register import parse_battery_lines  # noqa: E402

BRIEFS = {
    "CARB": "ADVISOR_SCOPE_BRIEF_CARBON_2026-08-04.md",
    "CFD": "ADVISOR_SCOPE_BRIEF_CFD_AND_ASSETS_2026-08-04.md",
    "COT": "ADVISOR_SCOPE_BRIEF_CHANGE_OF_TENANCY_2026-08-07.md",
    "ELEC": "ADVISOR_SCOPE_BRIEF_ELECTRICITY_2026-08-04.md",
    "GAS": "ADVISOR_SCOPE_BRIEF_GAS_2026-08-04.md",
    "IND": "ADVISOR_SCOPE_BRIEF_INDUSTRY_BOUNDARY_2026-08-04.md",
    "NCS": "ADVISOR_SCOPE_BRIEF_NONCOMMODITY_COST_STACK_2026-08-07.md",
    "PPM": "ADVISOR_SCOPE_BRIEF_PREPAYMENT_ESTATE_2026-08-07.md",
}

_M = "mechanised"
_P = "pending_capability"
_N = "not_mechanisable"

_BATTERY = "tests.domain.test_battery_checks"

# id -> (disposition, check-or-reason)
DISPOSITIONS: dict[str, tuple[str, str]] = {
    # ---- CARBON -------------------------------------------------------
    "CARB-1": (_P, "No carbon-intensity series is consumed anywhere in the tree; the NESO half-hourly intensity feed is not ingested. Blocker: a carbon-intensity adapter behind the wall."),
    "CARB-2": (_P, "Depends on CARB-1: with no intensity series there is no loss-correction step to double-apply."),
    "CARB-3": (_P, "Depends on CARB-1; additionally needs a regional (14 DNO) intensity surface, which does not exist."),
    "CARB-4": (_P, "Depends on CARB-1. The forecast/outturn distinction is exactly the kind of clock discipline R14 already enforces for money, so this becomes checkable the moment an intensity feed lands."),
    "CARB-5": (_P, "No time-shifting/flex-benefit accounting surface exists to confuse with consumption reduction."),
    "CARB-6": (_P, "No abatement claim is produced, so there is nothing to demand a holdout of."),
    "CARB-7": (_P, "No efficiency-measure model, therefore no rebound to omit."),
    "CARB-8": (_P, "Depends on CARB-6: no abatement accounting exists."),
    "CARB-9": (_N, "Half of this line is R12 policy, not an invariant: 'used as a target' is a statement about intent behind a number, which no assertion can read. The other half (a published GBP/tonne figure must carry a comparator) is a live obligation on any future carbon surface and is recorded in the delta report so it cannot be lost."),
    "CARB-10": (_P, "Gas carbon content is not modelled at all, so it cannot yet be wrongly modelled as time-varying. Becomes a one-line invariant once a gas emissions factor exists."),
    "CARB-11": (_P, "Generalises R14 (no financial figure without its clock) to carbon figures. No carbon figure is published today; the basis-labels gate in generate_dashboard_data.py is the natural host when one is."),
    "CARB-12": (_P, "Depends on CARB-6/CARB-7: no measures model, so no embodied/operational asymmetry to catch."),
    # ---- CFD AND ASSETS -----------------------------------------------
    "CFD-1": (_P, "Requires a day-ahead series distinct from the settlement series. See ELEC-2 -- one price series is the shared blocker."),
    "CFD-2": (_P, "get_cfd_levy_per_mwh returns a non-negative per-MWh rate by construction. Making it capable of going negative is a model change, not a test; the check lands with that change."),
    "CFD-3": (_P, "No allocation-round dimension exists on any CfD object, so rounds 1-3 and 4+ cannot be distinguished."),
    "CFD-4": (_P, "Only one CfD reference price exists; the intermittent/baseload split is unmodelled."),
    "CFD-5": (_P, "No contracted-plant dispatch model. Depends on the asset-level build."),
    "CFD-6": (_P, "Wind is national in the current generation stack. Duplicate of ELEC-6 from the CfD side -- both close together or neither does."),
    "CFD-7": (_P, "Depends on CFD-6: no per-site wind, so no inter-site correlation structure to assert."),
    "CFD-8": (_P, "Requires a contracted-share time series to test the pass-through relationship against."),
    "CFD-9": (_N, "An anti-over-modelling line. 'Too detailed' has no failing state a test can name -- any threshold would be invented, and a control whose criterion is invented is worse than none (R15). Kept as a design-review lens in the delta report."),
    # ---- CHANGE OF TENANCY ---------------------------------------------
    "COT-B1": (_P, "No void/deemed-occupier ledger exists, so an orphan-supply day cannot yet be detected or excluded. Strongest candidate in this brief -- it is a population invariant over data the settlement layer already holds."),
    "COT-B2": (_P, "CoT does not open a distinct incoming account, so there is no balance-transfer boundary to assert across."),
    "COT-B3": (_P, "Depends on COT-B2: with one account there is no outgoing/incoming read pair."),
    "COT-B4": (_P, "The anniversary invariant on credit balances exists for live accounts; the closed-account arm is not wired. Nearest working analogue: company/compliance credit-balance controls (R4)."),
    "COT-B5": (_P, "Depends on COT-B1: no void ledger to bill the standing charge to."),
    "COT-B6": (_P, "Back-billing windows exist and are tested; the move-in evidence hierarchy that would re-anchor them per person does not."),
    "COT-B7": (_P, "A population/rate check over a decade replay. Depends on COT events existing as a stream at all."),
    # ---- ELECTRICITY ----------------------------------------------------
    "ELEC-1": (_P, "Products exist as prices, not as a ladder of tradeable instruments with horizons and sizes. Depends on the wholesale value-chain build."),
    "ELEC-2": (_P, "The tree carries settlement and forward series but no distinct day-ahead or within-day series. This single gap blocks CFD-1 and ELEC-11 too -- the highest-leverage line in this brief."),
    "ELEC-3": (_P, "The merit-order reconstruction (sim/merit_order_reconstruction.py, W1_6b) is the mechanism that would make this checkable -- assert that raising wind changes WHICH unit is marginal rather than subtracting from price. Wiring that assertion is a real next atom, not a missing capability."),
    "ELEC-4": (_M, f"{_BATTERY}::test_elec_4_negative_prices_are_reachable"),
    "ELEC-5": (_P, "Scarcity is not a separate regime in the price generator; bimodal_generator models two regimes but neither is a scarcity tail."),
    "ELEC-6": (_P, "Wind is a national figure. Capacity-weighting to turbine locations is an unbuilt world capability (see W1_7)."),
    "ELEC-7": (_P, "No interconnector or French nuclear availability input exists in the price formation path."),
    "ELEC-8": (_P, "Carbon is present as a levy on bills but not as a term in marginal cost. Depends on the merit-order path (ELEC-3)."),
    "ELEC-9": (_P, "No liquidity or bid-offer spread model; every product is implicitly tradeable in any size. Depends on ELEC-1."),
    "ELEC-10": (_P, "Regime structure exists in the scenario substrate (SPINE_1) but is not asserted against the decade. Candidate for a population check once regimes are labelled on the replay."),
    "ELEC-11": (_P, "The Point-in-Time Blindfold already forbids reading future data generally, and that IS enforced. What is not enforced is the specific claim that the imbalance price for period P is unavailable until after P closes, because no distinct imbalance series exists (ELEC-2)."),
    "ELEC-12": (_P, "Same line as GAS-1 from the electricity side. The merit-order reconstruction makes gas causal rather than correlated; asserting it is the ELEC-3 wiring job."),
    # ---- GAS -------------------------------------------------------------
    "GAS-1": (_P, "Duplicate of ELEC-12. Closes with the merit-order assertion (ELEC-3)."),
    "GAS-2": (_P, "No gas storage model of any kind."),
    "GAS-3": (_P, "The summer-winter spread is not produced as an emergent quantity, so its capacity to invert cannot be tested. Depends on GAS-2."),
    "GAS-4": (_P, "No linepack model, so no within-day gas flexibility."),
    "GAS-5": (_P, "No LNG cargo model exists, so there is neither LNG supply nor the global cargo competition that sets its availability to GB."),
    "GAS-6": (_P, "Gas cash-out is not modelled; company/market/gas_nominations.py prices imbalance off a spot reference rather than marginal system prices."),
    "GAS-7": (_P, "No gas-day start hour exists anywhere in the tree -- company/market/gas_nomination_register.py carries a bare `gas_day: date` with no 05:00 boundary. The check is trivial ONCE the constant exists; asserting it now would assert nothing, which is the fail-open shape this register refuses."),
    "GAS-8": (_M, f"{_BATTERY}::test_gas_8_therm_conversion_is_single_and_published"),
    "GAS-9": (_P, "Only gas-to-power coupling is modelled; the power-to-gas direction (gas burn responding to power demand) is absent."),
    "GAS-10": (_P, "No gas interconnector flow model, so reversal cannot be represented."),
    "GAS-11": (_P, "Duplicate of ELEC-10 for gas."),
    "GAS-12": (_P, "UKCS domestic production is not a modelled series."),
    # ---- INDUSTRY BOUNDARY -------------------------------------------------
    "IND-1": (_P, "Typed adapters exist (W4_1) and some model failure, but there is no register of adapters against which 'every adapter can fail, delay or error' could be asserted as a CLASS. A per-adapter spot check would be an instance fix and R10 forbids closing a class that way. The adapter register is the real prerequisite."),
    "IND-2": (_P, "This is the Point-in-Time Blindfold itself, which IS enforced by the epistemic verifier and the .claude/rules path hooks. Recorded as pending rather than mechanised because the existing enforcement is a review-time and import-time guard, not a battery check, and claiming it here would double-count an existing control as new coverage."),
    "IND-3": (_P, "Settlement runs exist as a timetable (W3_2) but the company does not hold successive restating figures per period. Closely related to NCS-B6."),
    "IND-4": (_P, "Switching has no objection/refusal/erroneous-transfer paths."),
    "IND-5": (_P, "Meter data gaps exist in the world model; what is missing is the standing assertion that a non-zero fraction of customers are missing reads in any period."),
    "IND-6": (_P, "Payment uncertainty is modelled (the D lane) but not asserted at the billing boundary."),
    "IND-7": (_P, "Network and policy costs are present and time-varying (simulation/policy_costs.py), and are NOT flat-national for DUoS. The line is half-satisfied; the assertion that would prove it is NCS-B2, so it closes there rather than being claimed twice."),
    "IND-8": (_P, "No pre-switch enquiry limit is modelled, so the company's knowledge of prospects is unbounded by industry process."),
    "IND-9": (_P, "Obligations and scheme costs are present (obligations_register, policy_costs). Same double-count reasoning as IND-7: the coverage assertion belongs to NCS-B1."),
    "IND-10": (_P, "The typed-adapter seam is the design (W4_1) and the epistemic verifier polices it at review time. A structural guard that no adapter imports a sim internal is a genuine next atom -- the child_stderr_guard/segment_case_guard source-scan idiom applies directly."),
    # ---- NON-COMMODITY COST STACK -------------------------------------------
    "NCS-B1": (_P, "The build-up exists but is never reconciled to a cap-annex allowance; the annex figures are not held as data. Blocker: the cap annex as a machine-readable anchor."),
    "NCS-B2": (_P, "Domestic TNUoS/BSUoS shape-invariance is the right post-reform behaviour and is probably true of the code, but there is no per-customer peak-shifting lever to perturb, so the test cannot be written as a real perturbation. Writing it as an assertion over constants would be a tautology (R15)."),
    "NCS-B3": (_M, f"{_BATTERY}::test_ncs_b3_fuel_purity_of_the_levy_stack"),
    "NCS-B4": (_P, "LLF/TLM do not appear in the tree; settled volume is not built as metered x LLF x TLM."),
    "NCS-B5": (_P, "Many constants carry provenance comments (policy_costs.py is good about this) but there is no machine-readable provenance field, so 'every constant traces' cannot be asserted -- only spot-checked. A provenance schema on the constant tables is the prerequisite."),
    "NCS-B6": (_P, "R14's billed/settled/banked discipline is live for money; extending it to a settlement rerun restating DUoS/CfD/CM needs the successive-runs capability from IND-3."),
    "NCS-B7": (_P, "get_mutualization_levy_per_mwh exists, so the mechanism is not absent. What is missing is the supplier-failure-year replay that would exercise it, so the battery's actual claim (the 2021-22 cost physics reproduce) cannot be checked."),
    # ---- PREPAYMENT ESTATE ----------------------------------------------------
    "PPM-B1": (_P, "Prepayment appears in tariff and cap logic but there is no self-disconnection event in the model, so it can be neither counted nor dated."),
    "PPM-B2": (_P, "Depends on PPM-B1; additionally needs the protected-window calendar (working_days.py is the nearest working analogue and already handles calendar rules)."),
    "PPM-B3": (_P, "Depends on PPM-B1: with no self-disconnection event there is no dark period during which standing charge could accrue into debt."),
    "PPM-B4": (_P, "No meter debt recovery model or weekly cap; emergency credit is unmodelled."),
    "PPM-B5": (_P, "No vend file or UTRN exists. Note this is an idempotency line and C-S2 already makes idempotency a standing design constraint -- when vends land they inherit that discipline."),
    "PPM-B6": (_P, "PSR flags exist on customers; involuntary mode-switch does not, so there is no act for the gate to block or log."),
    "PPM-B7": (_P, "Cap variant by payment method exists in the cap tables; the estate technology mix and levelisation date do not, so era-truth cannot be asserted as a whole."),
}


def main() -> int:
    lines = []
    out: list[str] = []
    for slug, brief in BRIEFS.items():
        for line in parse_battery_lines(brief):
            lines.append((f"{slug}-{line.label}", brief, line))

    missing = [i for i, _, _ in lines if i not in DISPOSITIONS]
    if missing:
        print(f"ERROR: no disposition authored for: {missing}", file=sys.stderr)
        return 1
    extra = [k for k in DISPOSITIONS if k not in {i for i, _, _ in lines}]
    if extra:
        print(f"ERROR: disposition for unknown line: {extra}", file=sys.stderr)
        return 1

    out.append("# GENERATED by tools/build_battery_register.py -- do not hand-edit the")
    out.append("# `text` fields; they are parsed from the scope briefs so the register")
    out.append("# cannot drift from the purchased judgement. Author dispositions in the")
    out.append("# builder, then re-run it.")
    out.append("briefs:")
    for brief in BRIEFS.values():
        out.append(f"  - {brief}")
    out.append("entries:")
    for entry_id, brief, line in lines:
        disposition, payload = DISPOSITIONS[entry_id]
        out.append(f"  - id: {entry_id}")
        out.append(f"    brief: {brief}")
        out.append(f"    label: {_q(line.label)}")
        out.append(f"    text: {_q(line.text)}")
        out.append(f"    disposition: {disposition}")
        if disposition == "mechanised":
            out.append(f"    check: {_q(payload)}")
        else:
            out.append(f"    reason: {_q(payload)}")
    text = "\n".join(out) + "\n"
    target = ROOT / "tests" / "domain" / "battery_register.yaml"
    target.write_text(text, encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)}: {len(lines)} entries")

    doc = ROOT / "docs" / "design" / "BATTERY_CONVERSION.md"
    if doc.is_file():
        doc.write_text(_splice_status(doc.read_text(encoding="utf-8"), lines), encoding="utf-8")
        print(f"refreshed status block in {doc.relative_to(ROOT)}")
    return 0


BEGIN = "<!-- BEGIN GENERATED STATUS -- regenerate with tools/build_battery_register.py -->"
END = "<!-- END GENERATED STATUS -->"


def render_status(lines) -> str:
    """The status table. Generated, so the doc's counts cannot rot away from the
    register -- a prose inventory with no falsifier is how a stale number ends up
    being quoted as evidence."""
    rows: list[str] = []
    rows.append("| Brief | Lines | Mechanised | Pending capability | Not mechanisable |")
    rows.append("|---|---:|---:|---:|---:|")
    totals = {_M: 0, _P: 0, _N: 0}
    for slug, brief in BRIEFS.items():
        ids = [i for i, b, _ in lines if b == brief]
        counts = {_M: 0, _P: 0, _N: 0}
        for entry_id in ids:
            counts[DISPOSITIONS[entry_id][0]] += 1
            totals[DISPOSITIONS[entry_id][0]] += 1
        rows.append(
            f"| {slug} | {len(ids)} | {counts[_M]} | {counts[_P]} | {counts[_N]} |"
        )
    total = len(lines)
    rows.append(
        f"| **All** | **{total}** | **{totals[_M]}** | **{totals[_P]}** | **{totals[_N]}** |"
    )
    rows.append("")
    rows.append(
        f"**{totals[_M]} of {total} battery lines run with the suite.** "
        f"{totals[_P]} name a blocker; {totals[_N]} are judgements no assertion can carry."
    )
    return "\n".join(rows)


def _splice_status(doc: str, lines) -> str:
    if BEGIN not in doc or END not in doc:
        raise SystemExit("BATTERY_CONVERSION.md lost its generated-status markers")
    head, rest = doc.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{BEGIN}\n{render_status(lines)}\n{END}{tail}"


def _q(value: str) -> str:
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


if __name__ == "__main__":
    raise SystemExit(main())

