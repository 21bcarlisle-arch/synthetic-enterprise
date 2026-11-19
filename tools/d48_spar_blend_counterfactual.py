"""D48: what the BSC-blend estimate would do to the gap and to E1's run guard, at each SPAR.

HARNESS code, outside the wall. It reads one run book (read-only), re-bills the hold-route
electricity estimates under `EAC <- w*advance/FYC + (1-w)*EAC`, `w = min(1, FYC*SPAR)` (BSC Annex S-2
s4.3.7), and prints at each SPAR:
  - the electricity gap of W2_36 <-> D48 (the residual on runs no actual read closed, over the
    runner's own no-skill denominator, held fixed);
  - C6's |residual|, the calibration account of the D48 route prereg;
  - INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER's breaches and flags, by the runner's own function
    (`ev_estimated_run_vs_meter`) over the book's bills dressed as printed invoices.

SPAR is a GAP (how_a_supplier_shapes_an_estimate_for_an_unread_month.md s8). This sets none: it
sweeps the pre-registered table. Pre-registrations:
docs/staging/records/SEAT_PREREG_D48_THE_ELECTRICITY_RESIDUAL_BY_ESTIMATE_ROUTE_2026-11-19.md and
docs/staging/records/SEAT_PREREG_D48_E1_BREACHES_AT_EACH_SPAR_2026-11-19.md.

What moves: electricity, profile class 1 or 3, estimated bills on the hold route (an actual read
exists and the actual reads span < MIN_ADVANCE_DAYS). Gas, PC2, route 1 and no-read bills are as
billed. The opening EAC is read back off the company's own hold-route bill (kWh / profile weight),
so SPAR 0 is today's book by construction. A zero advance does not move the EAC: the company's own
rule (`estimate_unread_kwh`: a zero advance is a missing measurement).
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import numpy as np

from company.billing.unread_month_estimate import MIN_ADVANCE_DAYS, profile_weight
from tools.couple_w2_36_d48 import account_errors
from tools.domain_invariant_runner import ev_estimated_run_vs_meter

#: The pre-registered table's columns (D48 route prereg). Not a value of SPAR: a sweep over the GAP.
SPAR_SWEEP = (0.0, 0.5, 1.0, 2.0, 3.0, math.inf)
BLENDED_PROFILE_CLASSES = {1, 3}


def _d(s: str) -> date:
    return date.fromisoformat(s[:10])


def _is_actual(b: dict) -> bool:
    return b.get("billing_basis") != "estimated"


def counterfactual_kwh(bills: list[dict], true_kwh: dict, spar: float) -> tuple[dict, dict]:
    """{period_end: re-billed kWh} for one account's hold-route bills, and counters."""
    out, seen = {}, {"zero_advances": 0, "hold_bills": 0}
    if spar == 0 or bills[0].get("commodity") != "electricity":
        return out, seen
    start = _d(bills[0].get("account_held_from") or bills[0]["period_start"])
    eac, prev_read, first_actual, last_actual = None, start, None, None
    pending = []  # true kWh since the last actual read, by period
    for b in bills:
        pend = b["period_end"]
        pending.append(true_kwh.get(pend) or 0.0)
        if _is_actual(b):
            first_actual, last_actual = first_actual or _d(pend), _d(pend)
            if eac is not None:
                advance = sum(pending)
                fyc = profile_weight("electricity", prev_read, _d(pend))
                if advance <= 0:
                    seen["zero_advances"] += 1
                elif fyc > 0:
                    w = 1.0 if math.isinf(spar) else min(1.0, fyc * spar)
                    eac = w * advance / fyc + (1 - w) * eac
            prev_read, pending = _d(pend) + timedelta(days=1), []  # a read closes its own day
            continue
        if first_actual is None or b.get("profile_class") not in BLENDED_PROFILE_CLASSES:
            continue
        if (last_actual - first_actual).days >= MIN_ADVANCE_DAYS:  # the reads span it: route 1
            continue
        w_period = profile_weight("electricity", _d(b["period_start"]), _d(pend))
        if w_period <= 0:
            continue
        if eac is None:
            # The opening figure the company billed on, read back off its own bill. Every advance
            # before this bill is replayed onto it from the account's first read.
            eac = b["total_consumption_kwh"] / w_period
            eac = _replay(bills, true_kwh, start, _d(pend), eac, spar, seen)
        seen["hold_bills"] += 1
        out[pend] = eac * w_period
    return out, seen


def _replay(bills, true_kwh, start, upto, eac, spar, seen) -> float:
    prev, pending = start, []
    for b in bills:
        if _d(b["period_end"]) >= upto:
            break
        pending.append(true_kwh.get(b["period_end"]) or 0.0)
        if _is_actual(b):
            advance, fyc = sum(pending), profile_weight("electricity", prev, _d(b["period_end"]))
            if advance <= 0:
                seen["zero_advances"] += 1
            elif fyc > 0:
                w = 1.0 if math.isinf(spar) else min(1.0, fyc * spar)
                eac = w * advance / fyc + (1 - w) * eac
            prev, pending = _d(b["period_end"]) + timedelta(days=1), []
    return eac


class _Dressed:
    """A run-book account dressed as the invariant runner's Account, printed invoices only."""

    def __init__(self, cid: str, bills: list[dict], rebilled: dict):
        self.cid, self.fuel = cid, bills[0].get("commodity", "electricity")
        invoices = []
        for b in bills:
            kwh = rebilled.get(b["period_end"], b["total_consumption_kwh"])
            invoices.append({
                "period_start": b["period_start"], "period_end": b["period_end"],
                "read_type": "E" if b.get("billing_basis") == "estimated" else "A",
                "closing_read_kwh": b.get("register_closing_kwh"),
                "consumption_kwh": kwh,
                # The runner keys a meter on its serial; the book has none, and an exchange
                # restarts the register, so the meter type stands in for the serial.
                "meter_serial": b.get("meter_type"),
            })
        self.printed = {"invoices": invoices}


def sweep(book: dict, spars=SPAR_SWEEP) -> list[dict]:
    rows, truth, _belief, noskill, _s = account_errors(book)
    elec = np.array([r["fuel"] == "electricity" for r in rows])
    den = float(np.abs(noskill - truth)[elec].sum())
    by_acct = defaultdict(list)
    for b in book["bills"]:
        by_acct[b["customer_id"]].append(b)
    true = defaultdict(dict)
    for r in book["meter_read_log"]:
        true[r["customer_id"]][r["period_end"]] = r["true_consumption_kwh"]
    out = []
    for spar in spars:
        num, c6, accts, zero, hold = 0.0, None, [], 0, 0
        for cid, bills in by_acct.items():
            bills.sort(key=lambda b: b["period_end"])
            rebilled, seen = counterfactual_kwh(bills, true[cid], spar)
            zero, hold = zero + seen["zero_advances"], hold + seen["hold_bills"]
            accts.append(_Dressed(cid, bills, rebilled))
            if bills[0].get("commodity") != "electricity":
                continue
            last = max((i for i, b in enumerate(bills) if _is_actual(b)), default=-1)
            res = sum(rebilled.get(b["period_end"], b["total_consumption_kwh"])
                      - (true[cid].get(b["period_end"]) or 0.0) for b in bills[last + 1:])
            num += abs(res)
            if cid == "C6":
                c6 = abs(res)
        tally = ev_estimated_run_vs_meter({}, accts)
        moved = {a.cid for a in accts if any(
            i["consumption_kwh"] != b["total_consumption_kwh"]
            for i, b in zip(a.printed["invoices"], by_acct[a.cid]))}
        out.append({
            "spar": spar, "elec_gap": num / den, "c6_residual_kwh": c6,
            "runs_checked": tally.checked, "breaches": len(tally.breaches), "flags": len(tally.flags),
            "breaches_on_moved_accounts": [x for x in tally.breaches if x["where"].split()[0] in moved],
            "breach_where": [x["where"] for x in tally.breaches],
            "hold_bills_rebilled": hold, "zero_advances": zero,
        })
    return out


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--book", required=True)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args(argv)
    result = sweep(json.loads(Path(args.book).read_text(encoding="utf-8")))
    for r in result:
        print(f"SPAR {r['spar']:>4}: elec gap {r['elec_gap']:.3f}  C6 |res| {r['c6_residual_kwh']:,.0f} kWh  "
              f"E1 runs {r['runs_checked']} breaches {r['breaches']} "
              f"(on moved accounts {len(r['breaches_on_moved_accounts'])}) flags {r['flags']}  "
              f"hold bills {r['hold_bills_rebilled']} zero advances {r['zero_advances']}")
    if args.json:
        args.json.write_text(json.dumps(result, indent=1, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
