"""Run one arm of the reactive save in the settled run, or compare two arms.

REUSE: tools/save_on_loss_notice_arms.py
CLASS: CUSTOM
INDEX: searched "arm", "save offer", "stayer". `tools/_c29_retention_engagement_arm.py` runs one
       policy arm of the settled run per process with a scratch gap ledger; this follows its shape
       (one arm per process, `policy_scope`, the run loop's names rebound on the module) for a
       CURRICULUM switch, which no existing arm runner flips. `tools/grade_save_offer_shapes.py`
       grades the save on the lean decision set; the settled run's pricing loop is what that set
       cannot see, and is the whole point here.

THE DIRECTOR'S CONDITION (2026-10-08): a save must never be paid for by raising the price of
customers who stay. So `compare` reads every account-term both arms priced, drops the households a
save kept (their own price is the save), and lists every remaining price that differs, account by
account. `stayer_price_moves` is that comparison and is what the control is written against.

THE VULNERABILITY CHECK is a twin swap over every save the run offered: the same position offered
as vulnerable and as not (`vulnerable_twin_shortfalls`), with a household the company knew to be
vulnerable (its own disclosure register, `d29dcddc3`) priced at what it was actually offered; and
no known-vulnerable leaver holding an Invitation goes unoffered while plain leavers are offered
(`vulnerable_leavers_not_offered`). `offers_to_known_vulnerable` says the check had a subject.

Usage:
  python3 -m tools.save_on_loss_notice_arms run <off|on|placebo> <out.json> <report_end> [--cut-share S] [--scale K]
  python3 -m tools.save_on_loss_notice_arms compare <off.json> <on.json>
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CSS_GO_LIVE = "2022-07-18"
_STATE_KEYS = ("customer_id", "billing_account", "commodity", "term_start", "tariff_type",
               "unit_rate_gbp_per_mwh", "mean_recent_margin_rate", "portfolio_premium_pct")


def run_arm(arm: str, out: Path, report_end: str, cut: float | None, scale: float) -> dict:
    """`off`: no save. `on`: the save at its price. `placebo`: the same saves, decided by the world
    at the save's price, but billed at the renewal price -- so the book holds the same households
    as `on` and only the save's price differs. `on` against `placebo` is the save's cost alone."""
    import simulation.run_phase2b as rp2b
    from company.policy.decision_policy import CURRENT_POLICY, policy_scope
    from simulation.segment_vocabulary import is_business

    if arm == "placebo":
        rp2b.billed_rate_when_saved = lambda renewal, save: renewal  # noqa: E731
    if arm in ("on", "placebo"):
        if cut is None:
            raise SystemExit("REFUSED: the on arm needs --cut-share; a save's size is a GAP and is "
                             "never defaulted (q4_save_offer_cost_share_of_annual_bill)")
        rp2b.save_offers_active = lambda: True  # noqa: E731 -- the arm's switch, this process only
        rp2b.world_save_response_scale = lambda: scale
    policy = dataclasses.replace(CURRENT_POLICY,
                                 save_offer_cut_share=None if arm == "off" else cut)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    t0 = time.time()
    with tempfile.TemporaryDirectory() as scratch, policy_scope(policy):
        result = rp2b.main(report_end=report_end, policy=policy,
                           gap_ledger_path=Path(scratch) / "gap_ledger.json")
    summary = {
        "arm": arm, "head": head, "report_end": report_end, "cut_share": cut,
        "world_save_response_scale": None if arm == "off" else scale,
        "seconds": round(time.time() - t0, 1),
        "total_gross": result.get("total_gross"), "total_net": result.get("total_net"),
        "final_treasury": result.get("final_treasury"),
        "account_state": [{k: a.get(k) for k in _STATE_KEYS} for a in result["account_state_log"]],
        "renewal_departures": sum(1 for e in result["customer_events"]
                                  if e.get("event_type") == "churned"
                                  and e.get("departure_occasion") == "renewal"),
        # THE PUBLISHED SAVE RATE'S DENOMINATOR (q4_save_rate_on_loss_notice): every domestic
        # switch away, not only the fixed-term leavers a save is offered to. Counted from CSS
        # go-live, the first day this world can send the loser an Invitation at all.
        "domestic_departures_from_css": sum(
            1 for e in result["customer_events"]
            if e.get("event_type") == "churned"
            and str(e.get("event_date", ""))[:10] >= CSS_GO_LIVE
            and not is_business(rp2b._SEGMENT_OF.get(e.get("customer_id")))),
        "save_on_loss_notice_log": result.get("save_on_loss_notice_log", []),
    }
    out.write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")
    return summary


def _key(row: dict) -> tuple:
    return (row["customer_id"], row["commodity"], row["term_start"])


def stayer_price_moves(off_state: list[dict], on_state: list[dict],
                       saved_accounts: set[str]) -> list[dict]:
    """Every account-term priced in both arms, outside a saved household, whose price differs.

    A saved household is excluded from its save onwards only in the sense that matters: all of its
    terms are its own, and the condition is about the customers who stayed without a save."""
    on = {_key(r): r for r in on_state}
    moves = []
    for r in off_state:
        twin = on.get(_key(r))
        if twin is None or r["billing_account"] in saved_accounts:
            continue
        a, b = r["unit_rate_gbp_per_mwh"], twin["unit_rate_gbp_per_mwh"]
        if a != b:
            moves.append({"customer_id": r["customer_id"], "commodity": r["commodity"],
                          "term_start": r["term_start"], "off": a, "on": b,
                          "raised": (a is not None and b is not None and b > a)})
    return moves


def vulnerable_twin_shortfalls(save_log: list[dict], cut: float) -> list[dict]:
    """Every save the run offered, re-offered in the same position as vulnerable and as not; a row
    for each where the vulnerable household is offered more. For a household the company knew to
    be vulnerable (`known_vulnerable`, from its own disclosure register) the price it was ACTUALLY
    offered is the vulnerable side, so a desk that priced the run differently from the function
    is caught too."""
    from company.crm.save_offer import save_offer_rate

    out = []
    for row in save_log:
        rate = row.get("renewal_unit_rate_gbp_per_mwh")
        if row.get("save_unit_rate_gbp_per_mwh") is None or rate is None:
            continue
        plain = save_offer_rate(rate, cut, vulnerable=False)
        vuln = (row["save_unit_rate_gbp_per_mwh"] if row.get("known_vulnerable")
                else save_offer_rate(rate, cut, vulnerable=True))
        if vuln > plain + 1e-9:
            out.append({**row, "vulnerable_rate": vuln, "plain_rate": plain})
    return out


def vulnerable_leavers_not_offered(save_log: list[dict]) -> list[dict]:
    """A known-vulnerable leaver holding an Invitation who was offered nothing while a plain
    leaver in the run was offered something: the other way a vulnerable household gets less."""
    offered_plain = any(r.get("save_unit_rate_gbp_per_mwh") is not None
                        and not r.get("known_vulnerable") for r in save_log)
    return [r for r in save_log if offered_plain and r.get("known_vulnerable")
            and r.get("invitation_held") and r.get("save_unit_rate_gbp_per_mwh") is None]


def implied_save_rate(save_log: list[dict]) -> float | None:
    """Expected saves per expected loss notice at the world's own P(stay) (scale 1 curve)."""
    rows = [r for r in save_log if r.get("p_stay_at_save") is not None]
    leave = sum(1.0 - r["p_stay_at_offer"] for r in rows)
    gain = sum(r["p_stay_at_save"] - r["p_stay_at_offer"] for r in rows)
    return gain / leave if leave else None


def compare(off: dict, on: dict) -> dict:
    log = on["save_on_loss_notice_log"]
    # An arm run before the denominator existed borrows it from the other arm, and says so.
    departures = on.get("domestic_departures_from_css") or off.get("domestic_departures_from_css")
    saved = {r["billing_account"] for r in log if r["saved"]}
    moves = stayer_price_moves(off["account_state"], on["account_state"], saved)
    common = len({_key(r) for r in off["account_state"]} & {_key(r) for r in on["account_state"]})
    return {
        "cut_share": on["cut_share"],
        "world_save_response_scale": on["world_save_response_scale"],
        "loss_notices_answered": len(log),
        "invitations_held": sum(1 for r in log if r["invitation_held"]),
        "offers_made": sum(1 for r in log if r["save_unit_rate_gbp_per_mwh"] is not None),
        "saved": len(saved),
        "realised_save_rate": (len(saved) / len(log)) if log else None,
        "implied_save_rate_world_curve": implied_save_rate(log),
        # Expected saves at the world's own P(stay), over every domestic switch away from CSS on.
        "implied_saves_per_domestic_switch_away_from_css": (
            sum(r["p_stay_at_save"] - r["p_stay_at_offer"] for r in log
                if r.get("p_stay_at_save") is not None) / departures if departures else None),
        "domestic_departures_from_css": departures,
        "departures_counted_on": "on" if on.get("domestic_departures_from_css") else "off",
        "renewal_departures": {"off": off["renewal_departures"], "on": on["renewal_departures"]},
        "total_net_gbp": {"off": off["total_net"], "on": on["total_net"],
                          "on_minus_off": (on["total_net"] - off["total_net"])
                          if None not in (on["total_net"], off["total_net"]) else None},
        "total_gross_gbp": {"off": off["total_gross"], "on": on["total_gross"]},
        "stayer_account_terms_compared": common,
        "stayer_price_moves": len(moves),
        "stayer_prices_raised": sum(m["raised"] for m in moves),
        "stayer_price_move_rows": moves[:50],
        "offers_to_known_vulnerable": sum(1 for r in log if r.get("known_vulnerable")
                                          and r["save_unit_rate_gbp_per_mwh"] is not None),
        "vulnerable_leavers_not_offered": len(vulnerable_leavers_not_offered(log)),
        "vulnerable_twin_shortfalls": len(vulnerable_twin_shortfalls(log, on["cut_share"]))
        if on["cut_share"] is not None else None,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("arm", choices=("off", "on", "placebo"))
    r.add_argument("out", type=Path)
    r.add_argument("report_end")
    r.add_argument("--cut-share", type=float)
    r.add_argument("--scale", type=float, default=1.0)
    c = sub.add_parser("compare")
    c.add_argument("off", type=Path)
    c.add_argument("on", type=Path)
    c.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    if args.cmd == "run":
        s = run_arm(args.arm, args.out, args.report_end, args.cut_share, args.scale)
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
