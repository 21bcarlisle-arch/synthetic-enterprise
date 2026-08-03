"""What switching the settlement path to fabric physics would do — measured, per customer.

PURPOSE
-------
`simulation/fabric_demand_path.py` can drive the shipped book's demand from W1_11
fabric physics instead of a rescaled national PC1 shape. Whether to actually make
that switch is a decision about the WORLD's fidelity, and it should be taken on
measured numbers rather than on the plausibility of the mechanism. This tool
produces those numbers: for every customer in the real book, what the fabric world
says the premise consumes, what the company currently believes it consumes, and
whether the fabric level sits inside the company's own published plausibility
envelope.

WHAT IT IS NOT
--------------
Not a tuning loop. Nothing here feeds back into the generator, and the envelope is
read as a DIAGNOSTIC (R12): a premise outside it triggers R4 — diagnose the
mechanism — and never a parameter change to bring the number back inside. The
company's declared AQ/EAC is its BELIEF; a disagreement with the world is the
coupled-triad gap, not an error to be reconciled away.

WHY THE COMPANY'S ENVELOPE IS THE YARDSTICK HERE
------------------------------------------------
`RESI_CONSUMPTION_ENVELOPE_GAS`'s high bound was itself set from the PREVIOUS
generator's observed maximum. So a fabric premise above it is exactly the
interesting case: the company's compliance sense of "what a home can plausibly use"
and the world's physics disagree, and which one is wrong is an empirical question
about the real UK stock — not something either side may settle by adjusting itself.

Usage: python3 -m tools.fabric_settlement_gap [--json] [--write]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from pathlib import Path

from company.compliance.domain_invariants import (
    RESI_CONSUMPTION_ENVELOPE_ELEC,
    RESI_CONSUMPTION_ENVELOPE_GAS,
)
from simulation import fabric_demand_path as fdp
from simulation.household_demand import HouseholdDemandRegister
from simulation.run_phase2b import (
    CUSTOMERS,
    ELEC_CUSTOMERS,
    REPORT_END,
    REPORT_START,
    is_hh_customer,
)
from simulation.weather_inputs import _weather_source_customer_id

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_DIR / "docs" / "observability" / "fabric_settlement_gap.json"
WEATHER_DIR = PROJECT_DIR / "sim" / "weather_data"


def _declared_annual_kwh(customer_id: str) -> dict[str, float]:
    """The company's BELIEF about this premise, from the customer record: the
    declared electricity EAC and (for the paired gas account) the declared AQ."""
    out: dict[str, float] = {}
    for record in CUSTOMERS:
        if record["customer_id"] == customer_id and record.get("eac_kwh"):
            out["electricity"] = float(record["eac_kwh"])
        if record["customer_id"] == f"{customer_id}g" and record.get("aq_kwh"):
            out["gas"] = float(record["aq_kwh"])
    return out


def envelope_breaches(rows: list[dict]) -> list[str]:
    """The customers whose fabric level falls outside the company's plausibility
    envelope, on EITHER commodity.

    Raises on a row missing a verdict rather than treating the absence as a pass —
    an unmeasured premise is not a premise inside the envelope, and defaulting it
    to `True` would report a clear switch on a book nobody checked.
    """
    required = ("customer_id", "inside_envelope_electricity", "inside_envelope_gas")
    for row in rows:
        missing = [key for key in required if row.get(key) is None]
        if missing:
            raise ValueError(f"row {row.get('customer_id')!r} has no verdict for {missing}")
    return [
        row["customer_id"]
        for row in rows
        if not (row["inside_envelope_electricity"] and row["inside_envelope_gas"])
    ]


def measure(seed: int = fdp.DEFAULT_TRACE_SEED) -> dict:
    register = HouseholdDemandRegister(CUSTOMERS)
    start, end = dt.date.fromisoformat(REPORT_START), dt.date.fromisoformat(REPORT_END)
    rows, excluded = [], []
    for customer in ELEC_CUSTOMERS:
        cid = customer["customer_id"]
        site = _weather_source_customer_id(customer)
        verdict = fdp.fabric_eligibility(
            customer,
            register.household_at_date(cid, REPORT_START),
            is_half_hourly_metered=is_hh_customer(customer),
            weather_available=(WEATHER_DIR / f"{site}.csv").exists(),
        )
        if not verdict.is_eligible:
            excluded.append({"customer_id": cid, "reason": verdict.reason})
            continue
        series = fdp.build_fabric_series_for_site(
            customer_id=cid,
            household_at_date=lambda d, cid=cid: register.household_at_date(cid, d),
            weather_site=site,
            latitude_deg=customer.get("location", {}).get("lat") or 53.0,
            start=start,
            end=end,
            seed=seed,
        )
        declared = _declared_annual_kwh(cid)
        intensities = {
            year: round(constraint.rationing_intensity, 4)
            for year, constraint in sorted(series.constraint_by_year.items())
        }
        rows.append(
            {
                "customer_id": cid,
                "heating_commodity": series.heating_commodity,
                "segments": len(series.segments),
                "fabric_annual_electricity_kwh": round(series.annual_electricity_kwh, 1),
                "fabric_annual_gas_kwh": round(series.annual_gas_kwh, 1),
                "declared_annual_electricity_kwh": declared.get("electricity"),
                "declared_annual_gas_kwh": declared.get("gas"),
                "inside_envelope_electricity": RESI_CONSUMPTION_ENVELOPE_ELEC.check(
                    series.annual_electricity_kwh
                ),
                "inside_envelope_gas": RESI_CONSUMPTION_ENVELOPE_GAS.check(
                    series.annual_gas_kwh
                ),
                "prebound_intensity_by_year": intensities,
                "prebound_channel_is_fed": fdp.prebound_channel_is_fed(series),
                "carries_half_hourly_texture": fdp.trace_carries_half_hourly_texture(series),
                "covers_the_window": fdp.series_covers_window(
                    series, [start + dt.timedelta(days=i) for i in range((end - start).days + 1)]
                ),
            }
        )
    breaches = envelope_breaches(rows)
    return {
        "window": {"start": REPORT_START, "end": REPORT_END},
        "seed": seed,
        "envelope": {
            "electricity": [RESI_CONSUMPTION_ENVELOPE_ELEC.low, RESI_CONSUMPTION_ENVELOPE_ELEC.high],
            "gas": [RESI_CONSUMPTION_ENVELOPE_GAS.low, RESI_CONSUMPTION_ENVELOPE_GAS.high],
        },
        "eligible": rows,
        "excluded": excluded,
        "envelope_breaches": breaches,
        "switch_is_clear": not breaches,
    }


def _git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, cwd=str(PROJECT_DIR)
        ).strip()
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=fdp.DEFAULT_TRACE_SEED)
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    parser.add_argument("--write", action="store_true", help=f"persist to {OUTPUT_PATH.name}")
    args = parser.parse_args()

    result = measure(seed=args.seed)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("FABRIC SETTLEMENT GAP — what switching the demand path would do")
        print(f"  window {result['window']['start']} -> {result['window']['end']}"
              f"   seed {result['seed']}")
        print()
        print("  customer  segs   fabric elec   fabric gas   declared elec   declared gas   envelope")
        for row in result["eligible"]:
            inside = "ok" if row["inside_envelope_electricity"] and row["inside_envelope_gas"] else "BREACH"
            print(f"  {row['customer_id']:<8} {row['segments']:>4}   "
                  f"{row['fabric_annual_electricity_kwh']:>11,.0f}   "
                  f"{row['fabric_annual_gas_kwh']:>10,.0f}   "
                  f"{(row['declared_annual_electricity_kwh'] or 0):>13,.0f}   "
                  f"{(row['declared_annual_gas_kwh'] or 0):>12,.0f}   {inside}")
        print()
        for row in result["excluded"]:
            print(f"  {row['customer_id']:<8} not fabric-driven: {row['reason']}")
        print()
        if result["switch_is_clear"]:
            print("  VERDICT: every fabric-driven premise sits inside the company's own")
            print("  plausibility envelope. The settlement switch has no level blocker.")
        else:
            print(f"  VERDICT: envelope BREACH on {result['envelope_breaches']}.")
            print("  R4, not R12: diagnose the mechanism before switching settlement, and do")
            print("  NOT widen the envelope or tune the generator to close this.")

    if args.write:
        payload = dict(result, measured_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                       run_git_commit=_git_head())
        OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"\n  written: {OUTPUT_PATH.relative_to(PROJECT_DIR)}")


if __name__ == "__main__":
    main()
