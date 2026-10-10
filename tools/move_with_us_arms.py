"""Run one arm of home-mover retention (the move-with-us offer) in the settled run, or compare two.

REUSE: tools/move_with_us_arms.py
CLASS: CUSTOM
INDEX: searched "move with us arms", "save arms", "stayer". `tools/save_on_loss_notice_arms.py` is the
       template and its `stayer_price_moves` is REUSED, not paralleled; what it cannot do is flip
       this lever's two switches (the company's policy field and the world's curriculum) or run at
       a stated book size, which the identical-book measurements here need.

ARMS. `off`: the company makes no offer (today). `on --k K`: the company offers on every notice its
rule passes, and the world answers at take-up scale K. Same base seed. The book size is patched as
`/var/tmp/m_scale.py` does (founders, settlement budget), so an arm is cheap enough to run at both
ends of K.

WHAT `compare` GRADES (the proposal's P1-P4): whether the two arms' account-terms are identical
(`identical_account_terms`); every stayer price that moved (`stayer_price_moves`, the director's
condition); vulnerable twin shortfalls and known-vulnerable movers left unoffered while others are
offered; the number of move-out notices, offers and movers who would move with us; and on-minus-off
total net.

Usage:
  python3 -m tools.move_with_us_arms run <off|on> <out.json> [--k K] [--founders N] [--budget B] [--report-end D]
  python3 -m tools.move_with_us_arms compare <off.json> <on.json>
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import sys
import time
from pathlib import Path

from tools.save_on_loss_notice_arms import stayer_price_moves

REPO = Path(__file__).resolve().parents[1]
_STATE_KEYS = ("customer_id", "billing_account", "commodity", "term_start", "tariff_type",
               "unit_rate_gbp_per_mwh", "mean_recent_margin_rate", "portfolio_premium_pct")


def run_arm(arm: str, out: Path, k: float | None, founders: int | None, budget: float | None,
            report_end: str | None = None) -> dict:
    import tempfile

    # THE BOOK SIZE IS PATCHED BEFORE THE RUN MODULE IS IMPORTED: `run_phase2b` builds its roster
    # at import, so patching after it draws dwellings for one book and supplies another.
    if founders is not None:
        import simulation.live_population as lp
        lp.founder_accounts = lambda: founders  # noqa: E731 -- this process only
    if budget is not None:
        import simulation.net_new_acquisition as nna
        nna.SETTLEMENT_CUSTOMER_YEAR_BUDGET = budget
    import simulation.run_phase2b as rp2b
    from company.policy.decision_policy import CURRENT_POLICY, policy_scope
    if arm == "on":
        if k is None:
            raise SystemExit("REFUSED: the on arm needs --k; no take-up rate is published (G8.4), "
                             "so k is never defaulted")
        rp2b.move_with_us_active = lambda: True  # noqa: E731 -- the arm's switch, this process only
        rp2b.take_up_scale = lambda: k  # noqa: E731
    policy = dataclasses.replace(CURRENT_POLICY, move_with_us_offers=(arm == "on"))
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    t0 = time.time()
    with tempfile.TemporaryDirectory() as scratch, policy_scope(policy):
        result = rp2b.main(report_end=report_end, policy=policy,
                           gap_ledger_path=Path(scratch) / "gap_ledger.json")
    summary = {
        "arm": arm, "head": head, "take_up_scale": k if arm == "on" else None,
        "founders": founders, "budget": budget, "seconds": round(time.time() - t0, 1),
        "total_net": result.get("total_net"), "total_gross": result.get("total_gross"),
        "final_treasury": result.get("final_treasury"),
        "account_state": [{key: a.get(key) for key in _STATE_KEYS}
                          for a in result["account_state_log"]],
        "home_move_outs": len(result.get("home_move_outs", [])),
        "move_out_notices_filed": result.get("move_out_notices_filed", []),
        "move_with_us_log": result.get("move_with_us_log", []),
    }
    out.write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")
    return summary


def _twin_shortfalls(log: list[dict]) -> list[dict]:
    """Every offer decision re-asked as vulnerable and as not, in the same position; a row where the
    vulnerable side is offered less (no offer where the twin has one, or a dearer carried rate)."""
    import datetime as dt
    from types import SimpleNamespace

    from company.crm.move_with_us_offer import decide_move_with_us
    out = []
    for row in log:
        # The decision reads only these two fields of a notice; a stand-in keeps this harness off
        # the seam (a tools/ import of it is a census crossing with no business on the wall).
        notice = SimpleNamespace(supply_point_id=row["supply_point_id"],
                                 move_out_date=dt.date.fromisoformat(row["move_out_date"]))
        ask = dict(offers_on=True, tariff_type=row["tariff_type"],
                   unit_rate_per_mwh=row["unit_rate_gbp_per_mwh"],
                   cost_per_mwh=row["cost_gbp_per_mwh"], annual_kwh=row["company_eac_kwh"])
        plain, _ = decide_move_with_us(notice, vulnerable=False, **ask)
        vuln, _ = decide_move_with_us(notice, vulnerable=True, **ask)
        if row.get("known_vulnerable"):
            vuln = vuln if row.get("offered") else None
        if plain is not None and (vuln is None or vuln.carried_unit_rate > plain.carried_unit_rate):
            out.append(row)
    return out


def compare(off: dict, on: dict) -> dict:
    log = on["move_with_us_log"]
    retained = {r["billing_account"] for r in log if r.get("moves_with_us")}
    moves = stayer_price_moves(off["account_state"], on["account_state"], retained)
    key = lambda r: (r["customer_id"], r["commodity"], r["term_start"])  # noqa: E731
    offered_plain = any(r.get("offered") and not r.get("known_vulnerable") for r in log)
    return {
        "take_up_scale": on["take_up_scale"],
        "identical_account_terms": (sorted(map(json.dumps, off["account_state"]))
                                    == sorted(map(json.dumps, on["account_state"]))),
        "account_terms": {"off": len(off["account_state"]), "on": len(on["account_state"]),
                          "common": len({key(r) for r in off["account_state"]}
                                        & {key(r) for r in on["account_state"]})},
        "home_move_outs": {"off": off["home_move_outs"], "on": on["home_move_outs"]},
        "move_out_notices_filed": len(on["move_out_notices_filed"]),
        "households_asked": len(log),
        "offers_made": sum(1 for r in log if r.get("offered")),
        "no_offer_reasons": _count(r.get("no_offer_reason") for r in log if not r.get("offered")),
        "answerable": sum(1 for r in log if r.get("offered") and r.get("p_stay_at_carried") is not None),
        "moves_with_us": len(retained),
        "expected_moves_with_us_at_k": round(sum(
            (on["take_up_scale"] or 0.0) * r["p_stay_at_carried"] for r in log
            if r.get("offered") and r.get("p_stay_at_carried") is not None), 3),
        "total_net_gbp": {"off": off["total_net"], "on": on["total_net"],
                          "on_minus_off": (on["total_net"] - off["total_net"])
                          if None not in (on["total_net"], off["total_net"]) else None},
        "stayer_price_moves": len(moves),
        "stayer_prices_raised": sum(m["raised"] for m in moves),
        "stayer_price_move_rows": moves[:50],
        "offers_to_known_vulnerable": sum(1 for r in log if r.get("known_vulnerable") and r.get("offered")),
        "known_vulnerable_movers_not_offered_while_others_are": sum(
            1 for r in log if offered_plain and r.get("known_vulnerable") and not r.get("offered")),
        "vulnerable_twin_shortfalls": len(_twin_shortfalls(log)),
    }


def _count(values) -> dict:
    out: dict = {}
    for v in values:
        out[str(v)] = out.get(str(v), 0) + 1
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("arm", choices=("off", "on"))
    r.add_argument("out", type=Path)
    r.add_argument("--k", type=float)
    r.add_argument("--founders", type=int)
    r.add_argument("--budget", type=float)
    r.add_argument("--report-end")
    c = sub.add_parser("compare")
    c.add_argument("off", type=Path)
    c.add_argument("on", type=Path)
    c.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        s = run_arm(args.arm, args.out, args.k, args.founders, args.budget, args.report_end)
        print(json.dumps({k: s[k] for k in ("arm", "seconds", "total_net")}), flush=True)
        return 0
    with args.off.open(encoding="utf-8") as off, args.on.open(encoding="utf-8") as on:
        res = compare(json.load(off), json.load(on))
    text = json.dumps(res, indent=1, default=str)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
