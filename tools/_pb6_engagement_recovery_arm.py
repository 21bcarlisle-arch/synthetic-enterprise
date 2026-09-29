"""Run ONE arm of PB6 EH-2 (plant a channel effect, or plant none) through the real run loop.

The Expert Hour's Q8: "plant 0.5x and plant nothing; does the company recover both?" Its unit
controls feed the ledger synthetic counts. This asks what the company's OWN end-of-run belief
converges to when the world is changed and nothing else is.

Arms, each a separate process, since the override is a module-level table and a second arm in
the same interpreter would inherit the first arm's imports:

* `head`    -- the world as it stands.
* `planted` -- the world's prepayment switching rate halved (CIM 0.031 -> 0.0155) before the run.
* `null`    -- all three channels at one rate, so every world multiplier is exactly 1.0.

The override is asserted to have TAKEN on the world's own multiplier before the run starts. An
override that silently failed would read as "the company recovers nothing", which is the
confident null this whole control exists to rule out.

Usage: python3 -m tools._pb6_engagement_recovery_arm <head|planted|null> <out.json> [report_end]

WHAT IS READ AT THE END is the run's own ledger, captured as the scope closes, and graded as
`payment_method_engagement_reading(<method>, <year after the window>)`, which is the reading
the company would price its next renewal with. The raw counts are written beside it, so the
reading can be re-derived under any other rule without re-running the arm.
"""
from __future__ import annotations

import contextlib
import json
import math
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
METHODS = ("direct_debit", "standard_credit", "prepayment")


def _plant(arm: str) -> dict:
    import simulation.household_segments as hs

    table = hs.CIM_SWITCH_RATE_BY_CHANNEL
    if arm == "planted":
        table[hs.PaymentChannel.PREPAYMENT] = table[hs.PaymentChannel.PREPAYMENT] * 0.5
    elif arm == "null":
        for channel in list(table):
            table[channel] = table[hs.PaymentChannel.DIRECT_DEBIT]
    elif arm != "head":
        raise SystemExit(f"REFUSED: unknown arm {arm!r}; one of head, planted, null")
    return {c.value: hs.engagement_multiplier_for_channel(c) for c in hs.PaymentChannel}


def _raw_rule(prior: float, reading) -> float | None:
    """The pre-EH-1 rule on the same counts: raw channel rate over raw book rate, `prior x ratio**w`.

    Uses the REMEDIED weight, since the weight is not what EH-1 changed about the likelihood. So
    this is the old likelihood and blend at today's precision, not a byte-exact replay of HEAD~1.
    """
    if not reading.decisions or not reading.book_decisions or reading.weight is None:
        return None
    p_m = (reading.observed_losses + 0.5) / (reading.decisions + 1.0)
    p_b = (reading.book_losses + 0.5) / (reading.book_decisions + 1.0)
    return prior * math.exp(reading.weight * math.log(p_m / p_b))


def _grade(active) -> dict:
    """The company's reading per channel off the run's own ledger, at the year after the window."""
    from company.crm.enriched_churn_estimate import payment_method_engagement_reading

    years = sorted(active.decisions_by_year)
    grade_year = (years[-1] + 1) if years else None
    readings = {}
    for method in METHODS:
        r = payment_method_engagement_reading(method, grade_year)
        readings[method] = {
            "prior": r.prior, "factor": r.factor, "ratio": r.ratio,
            "weight": r.weight, "basis": r.basis,
            "decisions": r.decisions, "observed_losses": r.observed_losses,
            "expected_pre_losses": r.expected_losses,
            "book_decisions": r.book_decisions, "book_losses": r.book_losses,
            "book_expected_pre_losses": r.book_expected_losses,
            "raw_rule_factor": _raw_rule(r.prior, r),
        }
    return {
        "grade_year": grade_year,
        "readings": readings,
        "decisions_by_method": {
            f"{m}|{y}": n for (m, y), n in sorted(active.decisions_by_method.items())},
        "losses_by_method": {
            f"{m}|{y}": n for (m, y), n in sorted(active.losses_by_method.items())},
    }


def main() -> int:
    arm, out = sys.argv[1], Path(sys.argv[2])
    report_end = sys.argv[3] if len(sys.argv) > 3 else None
    world_multipliers = _plant(arm)
    print(f"[{arm}] world multipliers {world_multipliers}", flush=True)
    if arm == "null" and any(abs(m - 1.0) > 1e-12 for m in world_multipliers.values()):
        print(f"REFUSED: null arm multipliers are not all 1.0: {world_multipliers}")
        return 2
    if arm == "planted" and not world_multipliers["prepayment"] < 0.4:
        print(f"REFUSED: planted prepayment multiplier did not take: {world_multipliers}")
        return 2

    import simulation.run_phase2b as rp2b

    captured: dict = {}
    original_scope = rp2b.pressure_ledger_scope

    @contextlib.contextmanager
    def observing_scope(ledger=None):
        with original_scope(ledger) as active:
            try:
                yield active
            finally:
                captured.update(_grade(active))

    rp2b.pressure_ledger_scope = observing_scope
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    rp2b.main(report_end=report_end) if report_end else rp2b.main()
    out.write_text(json.dumps({
        "arm": arm, "head": head, "tree": str(REPO), "report_end": report_end,
        "world_multipliers": world_multipliers, **captured,
    }, indent=2, default=str), encoding="utf-8")
    print(f"[{arm}] -> {out}", flush=True)
    for method, r in captured.get("readings", {}).items():
        print(f"[{arm}] {method}: factor {r['factor']:.3f} (prior {r['prior']:.3f}, "
              f"ratio {r['ratio']}, w {r['weight']}) {r['basis']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
