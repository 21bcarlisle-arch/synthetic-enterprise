#!/usr/bin/env python3
"""Explore's cast: one household per supplier feature, chosen by rule at publish, seen three ways.

The director's steer of 23 Oct 2026 (`docs/staging/advisor/done/DIRECTOR_STEER_EXPLORE_IS_A_LIVE_
FEATURE_DEMO_THAT_PROVES_THE_FEATURES_WORK_2026-10-23.md`) asks for Explore to show a handful of
real households from the published run, each at a few moments of its 2016-2025 life, in three
views: what the customer saw, what the supplier held on that date, and what was really true. His
09:30 point is the reason this is a generator and not a page: **each cast rule is also a check that
its feature works end to end in the run.** A rule that finds no household is a finding, and the
slot says so on the page in the words `reason` carries; it is never filled with a near miss.

THE NO-LOOK-AHEAD PROPERTY, and where it is held. Every supplier-side row is built by `_supplier`
from `_known_by(records, iso)` and nothing else, and each row carries `drawn_from`: the latest
record date it read. `tests/tools/test_generate_explore_cast.py` reds if any row's `drawn_from` is
after its moment, and mutation-proves that by swapping `_known_by` for the identity. The beliefs
themselves are the ones the company STORED at decision time (`company_belief` on the reaction
chain), read back, never recomputed.

WHAT THE THREE VIEWS READ. Customer: invoices and the ledger (what a bill and an account page
show). Supplier: invoices, ledger, timeline and the company side of the reaction chain, dated on
or before the moment. Truth: `customer_sample.json` and the simulation side of the reaction chain.

THE COVERAGE CHECKS run over the whole book, not only the cast, so a slot's flag is read against
how often the same breach occurs: a capped standard-variable bill whose all-in unit rate is above
the binding ceiling (Ofgem cap, or the EPG where it was in force, read from the regulation
commons); a debit catch-up reaching back more than 12 months with no back-billing cap applied; a
dual-fuel household whose gas is still billed after its electricity left.

Output: `site/data/explore_cast.json`, read by the cast section of `site/explore/index.html`. The page's
opening moment is also written into that page between `<!--cast:static-->` markers, so it shows
without JavaScript.
"""
from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

from company.compliance.domain_invariants import default_tariff_invoice_excess_p_per_kwh

PROJECT = Path(__file__).resolve().parent.parent
CUSTOMERS_DIR = PROJECT / "site" / "data" / "customers"
SAMPLE_PATH = PROJECT / "site" / "data" / "customer_sample.json"
CAP_WINDOWS = PROJECT / "docs" / "domain_artefact_library" / "regulatory" / "ofgem_default_tariff_cap_windows.json"
OUT_PATH = PROJECT / "site" / "data" / "explore_cast.json"
PAGE_PATH = PROJECT / "site" / "explore" / "index.html"

#: The Ofgem back-billing rule (SLC 21BA): a supplier may not bill for energy used more than 12
#: months before the bill when the delay was its own.
BACKBILL_LIMIT_DAYS = 365

#: A fixed-term renewal is outside the default-tariff cap for its term. The run records each term's
#: `tariff_type` (`account_state_log`) but the published household record does not carry it, so
#: the cap check reads bills dated before the household's first renewal on that fuel. Graded
#: against the recorded type on the 19 Oct run, 4,579 of that population's 4,764 breaches were on
#: `svt` terms, so this is a proxy for the record and not the cause of the count (correction,
#: 23 Oct: this said the run did not record the term).

#: A gas leg billed this long after its electricity leg left is "left behind". One billing month
#: plus a final-bill allowance; anything past it is a bill for a household that has gone.
GAS_LEFT_BEHIND_DAYS = 62


def _fmt_gbp(v) -> str:
    return "£{:,.2f}".format(v) if v is not None else "—"


def _fmt_level(v) -> str:
    return "{:.1f}%".format(100.0 * v) if v is not None else "—"


def _fmt_points(v) -> str:
    return "{:.1f} percentage points".format(100.0 * v)


def _day(iso: str) -> str:
    d = date.fromisoformat(iso[:10])
    return "{} {} {}".format(d.day, d.strftime("%b"), d.year)


# ── Loading ────────────────────────────────────────────────────────────────────────────────────


def _load_customers(customers_dir: Path) -> dict[str, dict]:
    out = {}
    for f in sorted(customers_dir.glob("*.json")):
        try:
            x = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(x, dict) and x.get("account_id"):
            out[x["account_id"]] = x
    return out


def households(customers: dict[str, dict]) -> list[dict]:
    """One entry per household: its electricity account and, when dual fuel, its gas account."""
    gas_ids = {
        (c.get("dual_fuel_combined") or {}).get("gas_account_id")
        for c in customers.values()
    } - {None}
    out = []
    for aid, c in customers.items():
        if aid in gas_ids:
            continue
        legs = {c.get("commodity") or "electricity": c}
        gid = (c.get("dual_fuel_combined") or {}).get("gas_account_id")
        if gid and gid in customers:
            legs["gas"] = customers[gid]
        out.append({"id": aid, "legs": legs})
    return out


def _events(hh: dict) -> dict[str, list[dict]]:
    """Every dated record the household carries, by kind, each tagged with its fuel."""
    ev = defaultdict(list)
    seen_tl = set()
    for fuel, acc in hh["legs"].items():
        for i in acc.get("invoices") or []:
            ev["invoice"].append({**i, "fuel": fuel})
        for e in (acc.get("ledger") or {}).get("entries") or []:
            ev["ledger"].append({**e, "fuel": fuel})
        for e in acc.get("timeline") or []:
            # Life events are the household's and appear on both legs; keep one.
            key = (e.get("date"), e.get("type"), e.get("detail")) if e.get("type") == "life_event" else None
            if key and key in seen_tl:
                continue
            if key:
                seen_tl.add(key)
            if e.get("detail"):
                e = {**e, "detail": re.sub(r"^Ev\b", "EV", e["detail"])}
            ev["timeline"].append({**e, "fuel": fuel})
        for e in acc.get("reaction_chain") or []:
            ev["reaction"].append({**e, "fuel": fuel})
    for k in ev:
        ev[k].sort(key=lambda r: r.get("date") or "")
    return ev


def _known_by(records: list[dict], iso: str) -> list[dict]:
    """The records dated on or before `iso` -- the only door into the supplier view."""
    return [r for r in records if (r.get("date") or "9999") <= iso]


def _is_outcome(r: dict) -> bool:
    return str(r.get("event_type", "")).startswith("outcome_") or r.get("type") in ("renewed", "churned")


def _before_outcome(ev: dict, iso: str) -> dict:
    """The record as it stood at a decision made on `iso`: that day's outcome has not happened yet.

    The run dates a renewal decision and its outcome on the same day, so "dated on or before" alone
    lets the decision moment show the result it was deciding about.
    """
    return {k: [r for r in v if not (r.get("date") == iso and _is_outcome(r))] for k, v in ev.items()}


# ── Coverage checks (the director's 09:30 point) ──────────────────────────────────────────────


def _cap_windows(path: Path = CAP_WINDOWS) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return sorted(raw["windows"], key=lambda w: w["from"])


def binding_ceiling_p_per_kwh(windows: list[dict], fuel: str, iso: str) -> float | None:
    """What a household on a default tariff could be charged per kWh, inc VAT, on `iso`.

    The household paid the EPG rate where it was in force (the Treasury paid the supplier the rest),
    so the household-facing ceiling is the lower of the two. None before the cap existed.
    """
    key = "elec" if fuel == "electricity" else "gas"
    for w in windows:
        if w["from"] <= iso <= w["to"]:
            vals = [w[key]] + ([w[key + "_epg"]] if (key + "_epg") in w else [])
            return min(vals) / 10.0
    if windows and iso > windows[-1]["to"]:
        return binding_ceiling_p_per_kwh(windows, fuel, windows[-1]["to"])
    return None


def _all_in_p_per_kwh(inv: dict) -> float | None:
    kwh = inv.get("consumption_kwh") or 0
    net = (inv.get("amount_gbp") or 0) - (inv.get("vat_gbp") or 0)
    if kwh <= 0 or net <= 0 or inv.get("catchup_applied"):
        return None
    vat_rate = (inv.get("vat_gbp") or 0) / net
    energy = (inv.get("commodity_amount_gbp") or 0) + (inv.get("non_commodity_amount_gbp") or 0)
    return 100.0 * energy * (1 + vat_rate) / kwh


def _first_renewal(timeline: list[dict]) -> dict[str, str]:
    out: dict[str, str] = {}
    for e in timeline:
        if e.get("type") == "renewed":
            out.setdefault(e["fuel"], e["date"])
    return out


def coverage_breaches(hh: dict, ev: dict, windows: list[dict], segment: str) -> list[dict]:
    """The published rules this household's own numbers break, each with the figures that break it."""
    out = []
    fixed_from = _first_renewal(ev["timeline"])
    if segment == "resi":
        for inv in ev["invoice"]:
            iso = inv.get("period_start") or inv["date"]
            if inv["date"] >= fixed_from.get(inv["fuel"], "9999"):
                continue
            # The rule itself is the company's invariant, so the cast and the bill are graded by
            # one implementation of one legal requirement, not two.
            if not default_tariff_invoice_excess_p_per_kwh({**inv, "commodity": inv["fuel"]}, "svt"):
                continue
            ceiling = binding_ceiling_p_per_kwh(windows, inv["fuel"], iso)
            charged = _all_in_p_per_kwh(inv)
            if ceiling is not None and charged is not None:
                out.append({
                    "rule": "above_cap", "date": inv["date"], "fuel": inv["fuel"],
                    "text": "{} bill of {}: {:.2f}p/kWh all-in including VAT, against a ceiling of "
                            "{:.2f}p/kWh for a default tariff then (GB average; the cap is set per region)".format(
                                inv["fuel"].capitalize(), _day(inv["date"]), charged, ceiling),
                })
    for inv in ev["invoice"]:
        start = inv.get("catchup_period_start")
        if not (inv.get("catchup_applied") and start and inv.get("catchup_direction") == "debit"):
            continue
        reach = date.fromisoformat(inv["date"][:10]).toordinal() - date.fromisoformat(start[:10]).toordinal()
        if reach > BACKBILL_LIMIT_DAYS and not inv.get("catchup_back_billing_cap_applied"):
            out.append({
                "rule": "backbill_beyond_12_months", "date": inv["date"], "fuel": inv["fuel"],
                "text": "{} catch-up on {} reaches back {} days to {}, with no back-billing cap "
                        "applied".format(inv["fuel"].capitalize(), _day(inv["date"]), reach, _day(start)),
            })
    left = [e["date"] for e in ev["timeline"] if e.get("type") == "churned" and e["fuel"] == "electricity"]
    if left and hh["legs"].get("gas") is not None:
        gas_left = [e["date"] for e in ev["timeline"] if e.get("type") == "churned" and e["fuel"] == "gas"]
        last_gas = max((i["date"] for i in ev["invoice"] if i["fuel"] == "gas"), default=None)
        lag = (date.fromisoformat(last_gas).toordinal() - date.fromisoformat(left[0]).toordinal()) if last_gas else 0
        if lag > GAS_LEFT_BEHIND_DAYS and not (gas_left and gas_left[0] <= left[0]):
            out.append({
                "rule": "gas_left_behind", "date": last_gas, "fuel": "gas",
                "text": "Electricity left on {}; gas was still billed {} days later, to {}".format(
                    _day(left[0]), lag, _day(last_gas)),
            })
    return out


# ── The three views at one moment ─────────────────────────────────────────────────────────────


def _row(k, v, drawn_from):
    return {"k": k, "v": v, "drawn_from": drawn_from}


def _latest(records, pred=lambda r: True):
    for r in reversed(records):
        if pred(r):
            return r
    return None


def _supplier(hh: dict, ev: dict, iso: str) -> tuple[list[dict], str]:
    acq = min(a.get("acquisition_date") or "9999" for a in hh["legs"].values())
    inv = _known_by(ev["invoice"], iso)
    led = _known_by(ev["ledger"], iso)
    tl = _known_by(ev["timeline"], iso)
    rc = [r for r in _known_by(ev["reaction"], iso) if r.get("event_type") != "journey_state"]
    rows = [_row("Customer since", _day(acq), acq),
            _row("Fuels", " and ".join(f.capitalize() for f in hh["legs"]), acq)]
    pay = _latest(led, lambda r: r.get("method") in ("direct_debit", "standard_credit", "prepayment"))
    rows.append(_row("How they pay", {"direct_debit": "Direct debit", "standard_credit": "Pays each bill on receipt",
                                     "prepayment": "Prepayment"}.get((pay or {}).get("method"), "No payment yet"),
                     (pay or {}).get("date") or acq))
    ren = _latest(tl, lambda r: r.get("type") == "renewed")
    rows.append(_row("Tariff", ("Fixed at {} from {}".format(ren["detail"].replace("Tariff renewed at ", ""), _day(ren["date"]))
                                if ren else "Standard variable"), (ren or {}).get("date") or acq))
    belief = _latest(rc, lambda r: r.get("company_belief") is not None)
    if belief:
        rows.append(_row("Churn risk it held", "{} at the {} renewal".format(_fmt_level(belief["company_belief"]), _day(belief["date"])),
                         belief["date"]))
    paid = [r for r in led if r.get("type") == "payment_received"]
    failed = [r for r in led if r.get("type") == "payment_failed"]
    missed = [r for r in rc if r.get("event_type") == "arrears_payment_missed"]
    last_pay = paid[-1]["date"] if paid else acq
    rows.append(_row("Payment record", "{} payments, {} returned, {} missed".format(len(paid), len(failed), len(missed)),
                     max([last_pay] + [r["date"] for r in failed + missed])))
    actual = [i for i in inv if i.get("read_type") == "A"]
    rows.append(_row("Meter reads", "{} bills, {} on an actual read{}".format(
        len(inv), len(actual), ", last on {}".format(_day(actual[-1]["date"])) if actual else ""),
        inv[-1]["date"] if inv else acq))
    bal = {}
    for r in led:
        bal[r["fuel"]] = (r.get("running_balance_gbp") or 0.0, r["date"])
    owed = sum(v for v, _ in bal.values())
    rows.append(_row("Balance on the books", ("{} owed".format(_fmt_gbp(owed)) if owed > 0.005 else
                                              "{} in credit".format(_fmt_gbp(-owed)) if owed < -0.005 else "Nothing owed"),
                     max([d for _, d in bal.values()] or [acq])))
    debt = _latest(rc, lambda r: str(r.get("event_type", "")).startswith(_DEBT_PREFIXES))
    if debt:
        rows.append(_row("Debt stage", debt.get("description") or debt["event_type"], debt["date"]))
    decision = _latest(rc, lambda r: r.get("event_type") in ("retention_decision", "arrears_second_notice",
                                                            "arrears_first_notice", "arrears_written_off",
                                                            "arrears_placed_with_dca", "outcome_renewed",
                                                            "outcome_churned", *_DESK_DECISIONS))
    line = ("{}: {}".format(_day(decision["date"]), _company_words(decision)) if decision
            else "No decision about this household is on record yet.")
    return rows, line


def _company_words(r: dict) -> str:
    """The company's side of a reaction-chain line: never the simulation's figure."""
    d = re.sub(r"GBP\s?(-?[\d,]+(?:\.\d+)?)", "£\\1", r.get("description") or r.get("event_type"))
    return re.sub(r",? ?-*\s*SIM realized probability was [\d.]+%\.?", "", d).strip()


def _truth(hh: dict, ev: dict, person: dict, iso: str) -> list[dict]:
    y = int(iso[:4])
    rows = []
    occ = (person.get("occupancy") or "").replace("_", " ")
    rows.append({"k": "Household", "v": ", ".join(x for x in [occ, (person.get("tenure") or "").replace("_", " "),
                                                            (person.get("home_type") or "").replace("_", " ")] if x) or "Not recorded"})
    stress = _latest([s for s in person.get("income_stress_trajectory") or [] if s.get("year", 9999) <= y])
    rows.append({"k": "Money", "v": "Income stress {}{}".format(
        (stress or {}).get("stress", "not recorded"), ", in fuel poverty" if person.get("fuel_poverty") else "")})
    life = [e for e in ev["timeline"] if e.get("type") == "life_event" and e["date"] <= iso]
    rows.append({"k": "Life so far", "v": "; ".join("{} ({})".format(e["detail"], e["date"][:7]) for e in life[-3:]) or "Nothing recorded"})
    mood = _latest([r for r in ev["reaction"] if r.get("event_type") == "journey_state" and r["date"] <= iso])
    if mood:
        rows.append({"k": "Hidden mood", "v": re.sub(r"^Hidden churn-journey state advances to ", "", mood["description"])})
    sat = _latest([s for s in person.get("satisfaction_score_trajectory") or [] if s.get("year", 9999) <= y])
    if sat:
        rows.append({"k": "True satisfaction", "v": _fmt_level(sat["satisfaction_score"]) + " in {}".format(sat["year"])})
    truth_p = _latest([r for r in ev["reaction"] if r.get("sim_truth") is not None
                       and str(r.get("event_type", "")).startswith("outcome_") and r["date"] <= iso])
    if truth_p:
        rows.append({"k": "True chance of leaving", "v": "{} at the {} renewal".format(_fmt_level(truth_p["sim_truth"]), _day(truth_p["date"]))})
    rows.append({"k": "Smart meter", "v": "Yes" if person.get("smart_meter") else "No"})
    return rows


def _portal(hh: dict, ev: dict, iso: str, message: str) -> dict:
    inv = _known_by(ev["invoice"], iso)
    led = _known_by(ev["ledger"], iso)
    months = defaultdict(lambda: {"electricity": 0.0, "gas": 0.0})
    for i in inv:
        months[i["date"][:7]][i["fuel"]] += i.get("consumption_kwh") or 0.0
    last12 = sorted(months)[-12:]
    bills = [{"fuel": i["fuel"], "when": _day(i["date"]), "kwh": round(i.get("consumption_kwh") or 0),
              "amount": (_fmt_gbp(i.get("amount_gbp")) if (i.get("amount_gbp") or 0) >= 0
                         else "{} credit".format(_fmt_gbp(-i["amount_gbp"]))),
              "badge": "Actual read" if i.get("read_type") == "A" else "Estimated"} for i in inv[-4:]][::-1]
    bal = {}
    for r in led:
        bal[r["fuel"]] = r.get("running_balance_gbp") or 0.0
    owed = sum(bal.values())
    ren = _latest(_known_by(ev["timeline"], iso), lambda r: r.get("type") == "renewed")
    pay = _latest(led, lambda r: r.get("method") in ("direct_debit", "standard_credit", "prepayment"))
    return {
        "message": message,
        "tariff": "Fixed from {}".format(_day(ren["date"])) if ren else "Standard Variable",
        "pays": {"direct_debit": "Direct debit", "standard_credit": "Pay on receipt of bill",
                 "prepayment": "Prepayment"}.get((pay or {}).get("method"), "Set up at your first bill"),
        "balance": ("{} to pay".format(_fmt_gbp(owed)) if owed > 0.005 else
                    "{} in credit".format(_fmt_gbp(-owed)) if owed < -0.005 else "Nothing owed"),
        "usage": [{"month": m, "e": round(months[m]["electricity"]), "g": round(months[m]["gas"])} for m in last12],
        "bills": bills,
    }


# ── Moments: one plain-English template per event kind, filled with the household's numbers ───


def _moments_for(hh, ev, keys: list[tuple[str, str, dict]]) -> list[dict]:
    """`keys` is (iso, kind, record). The words are templates; no motive the data lacks is stated."""
    out = []
    for iso, kind, rec in keys:
        title, story, msg, why, gap = _template(hh, ev, iso, kind, rec)
        out.append({"iso": iso, "date": _day(iso), "kind": kind, "title": title, "story": story,
                    "portal_message": msg, "why": why, "gap": gap})
    return out


def _template(hh, ev, iso, kind, rec):
    fuels = " and ".join(hh["legs"])
    if kind == "joined":
        return ("Switched in", "The household joins Poesys for {}.".format(fuels),
                "Welcome to Poesys. Your {} supply started on {}.".format(fuels, _day(iso)),
                "The supplier knows the address, the meter points and how it will be paid. It knows nothing else yet.",
                None)
    if kind == "first_bill":
        return ("First bill", "The first {} bill: {} for {:,.0f} kWh, {}.".format(
                    rec["fuel"], _fmt_gbp(rec.get("amount_gbp")), rec.get("consumption_kwh") or 0,
                    "on an actual read" if rec.get("read_type") == "A" else "estimated"),
                "Your first {} bill is ready: {}.".format(rec["fuel"], _fmt_gbp(rec.get("amount_gbp"))),
                "The amount follows from the reading and the tariff; nothing else is behind it.", None)
    if kind == "bill":
        return (rec.get("label") or "A bill", "The {} bill of {}: {} for {:,.0f} kWh, {}.".format(
                    rec["fuel"], _day(rec["date"]), _fmt_gbp(rec.get("amount_gbp")), rec.get("consumption_kwh") or 0,
                    "on an actual read" if rec.get("read_type") == "A" else "estimated"),
                "Your {} bill is ready: {}.".format(rec["fuel"], _fmt_gbp(rec.get("amount_gbp"))),
                "The amount follows from the reading and the tariff then in force.", None)
    if kind == "renewal_decision":
        b, t = rec.get("company_belief"), rec.get("sim_truth")
        offered = rec.get("outcome") == "retained" or bool(re.search(r"\boffer", rec.get("description") or "", re.I))
        on_fix = any(e.get("type") == "renewed" and e["date"] < iso for e in ev["timeline"])
        return ("The renewal decision", _company_words(rec),
                ("Your fixed tariff is ending. " if on_fix else "Your tariff is up for review. ")
                + ("We have an offer for you." if offered else "Here are your options."),
                "The simulation drew this household's real chance of leaving as {}.".format(_fmt_level(t)),
                {"believed": "{} chance it would leave".format(_fmt_level(b)),
                 "truth": "{} chance it would leave".format(_fmt_level(t)),
                 "meant": "{} apart, so the offer {}".format(_fmt_points(abs(b - t)),
                                                             "was spent on a household that was not leaving" if b > t
                                                             else "was sized for a household far less likely to go"),
                 "tone": "bad" if abs(b - t) >= 0.25 else "neutral"})
    if kind == "outcome":
        left = rec.get("event_type") == "outcome_churned"
        return ("Left" if left else "Renewed", _company_words(rec),
                ("Sorry to see you go. Your final bill will follow." if left else "Your new tariff has started."),
                "The true probability on the day was {}; the draw went {}.".format(_fmt_level(rec.get("sim_truth")),
                                                                                 "against staying" if left else "for staying"),
                {"believed": _fmt_level(rec.get("company_belief")) + " chance of leaving",
                 "truth": _fmt_level(rec.get("sim_truth")) + " chance of leaving",
                 "meant": "It " + ("left" if left else "stayed"),
                 "tone": "bad" if left else "good"})
    if kind == "estimate_run":
        return ("Estimated, again", "{} {} bills in a row were estimated.".format(rec["n"], rec["fuel"]),
                "Your {} bill is estimated. Send us a reading to make it accurate.".format(rec["fuel"]),
                "The meter was not read; the bills are the supplier's estimate of use, not the use.",
                {"believed": "{:,.0f} kWh across the estimated bills".format(rec["kwh"]),
                 "truth": "The meter had not been read since {}".format(rec["since"]),
                 "meant": "The difference lands on the next actual read", "tone": "neutral"})
    if kind == "catch_up":
        adj = rec.get("catchup_adjustment_gbp")
        return ("The catch-up", "An actual read on {} corrects the estimates: {} {}.".format(
                    _day(rec["date"]), _fmt_gbp(abs(adj or 0)), "added" if (adj or 0) > 0 else "credited"),
                "We have a meter reading and your bill now reflects what you used.",
                "The estimates were {} the meter by {}.".format("below" if (adj or 0) > 0 else "above", _fmt_gbp(abs(adj or 0))),
                {"believed": "The estimated bills", "truth": "The meter read on {}".format(_day(rec["date"])),
                 "meant": "{} {}".format(_fmt_gbp(abs(adj or 0)), "owed in one bill" if (adj or 0) > 0 else "back to the customer"),
                 "tone": "bad" if (adj or 0) > 0 else "good"})
    if kind == "debt" and rec.get("event_type", "").startswith("collections_"):
        et = rec["event_type"]
        return (_DESK_TITLES.get(et, "Collections"), rec.get("description") or et,
                _DESK_MESSAGES.get(et, "Your account is overdue. Please pay or call us."),
                _debt_why(hh, ev, iso), None)
    if kind == "debt":
        et = rec.get("event_type", "")
        return ({"arrears_payment_missed": "Missed a payment", "arrears_dd_failed": "Direct debit returned",
                 "arrears_first_notice": "First notice", "arrears_second_notice": "Second notice",
                 "arrears_arrears_repaid": "Arrears repaid", "arrears_written_off": "Written off",
                 "arrears_placed_with_dca": "Passed to an agency", "arrears_recovered": "Agency recovery"}.get(et, "Arrears"),
                rec.get("description") or et,
                {"arrears_first_notice": "Your account is overdue. Please pay or call us.",
                 "arrears_second_notice": "Your account is still overdue. We can set up a payment plan.",
                 "arrears_written_off": "Your account has been closed.",
                 "arrears_placed_with_dca": "Your closed account has been passed to a collection agency."}.get(
                    et, "Your payment did not reach us."),
                _debt_why(hh, ev, iso), None)
    if kind == "life_event":
        return (rec["detail"], "{}{}".format(rec["detail"], ": " + rec["effect"] if rec.get("effect") else "."),
                "No message: nothing the supplier can see happened today.",
                "This is in the simulation only. {}".format(rec.get("effect") or ""),
                {"believed": "Nothing changed", "truth": rec["detail"] + (" — " + rec["effect"] if rec.get("effect") else ""),
                 "meant": "The supplier can only learn this from the meter, later", "tone": "neutral"})
    if kind == "shock_2022":
        return ("The 2022 shock", "The {} bill for {} was {}, against {} a year earlier.".format(
                    rec["fuel"], rec["month"], _fmt_gbp(rec["now"]), _fmt_gbp(rec["before"])),
                "Your bill has changed because energy prices have changed.",
                "Wholesale prices rose; the household's use did not explain the change.",
                {"believed": "Bill of " + _fmt_gbp(rec["now"]), "truth": "Billed use {:,.0f} kWh, against {:,.0f} kWh a year before".format(rec["kwh_now"], rec["kwh_before"]),
                 "meant": "{:.0f}% more for the same month".format(100 * (rec["now"] / rec["before"] - 1)) if rec["before"] else "",
                 "tone": "bad"})
    return (kind, "", "", "", None)


def _debt_why(hh, ev, iso):
    tl = [e for e in ev["timeline"] if e.get("type") == "life_event" and e["date"] <= iso]
    return ("The last life event on record before this was {} ({}). The record does not say it caused this.".format(
        tl[-1]["detail"], tl[-1]["date"][:7]) if tl else "No life event is on record before this; the record gives no reason.")


# ── Cast rules ────────────────────────────────────────────────────────────────────────────────


#: One plain line per tab saying what the feature IS, for a reader who does not know the trade
#: (the cold read of 23 Oct asked what an "estimate trap" was). It defines; it does not narrate.
GLOSSARY = {
    "switch_in": "Switching in: a household moves its supply to this supplier, and its first bill is the first test of the new account.",
    "renewal": "Renewal: a fixed-price tariff is ending, and the supplier decides what to offer before the household decides whether to stay.",
    "estimate_trap": "An estimate trap: bills are worked out from guessed meter readings until a real reading arrives and corrects the account in one step.",
    "mover": "A home move: the leaving occupant gets a final bill, and whoever moves in next becomes the supplier's new customer at that address.",
    "debt": "The debt journey: a bill goes unpaid, then reminders and a payment plan follow, and it ends repaid, written off or with a collection agency.",
    "ev": "An EV home: an electric car arrives, and the supplier sees it only as more electricity on the meter.",
    "storage_heating": "Storage heating: heaters that charge overnight on a two-rate meter (such as Economy 7), whose night units are billed cheaper.",
    "shock_2022": "The 2022 shock: wholesale prices rose several times over, and the price cap and then the Energy Price Guarantee set what households paid.",
}


def _cast_rules():
    """(slot id, feature, one-line rule, scorer). A scorer returns (score, keys, opening index) or None."""
    return [
        ("switch_in", "The switch-in", "The household that switched in most recently and holds a full first quarter on record", _score_switch_in),
        ("renewal", "The renewal", "The largest gap between the supplier's stored churn belief and the true probability at a renewal decision", _score_renewal),
        ("estimate_trap", "The estimate trap", "The longest run of estimated bills on one fuel that ends in a catch-up", _score_estimate_trap),
        ("mover", "The mover", "A household that moves out, takes a final bill, and is followed by a new occupant", _score_mover),
        ("debt", "The debt journey", "The arrears journey that goes deepest: missed payment, notices, then repaid, written off or passed to an agency", _score_debt),
        ("ev", "The EV home", "The household whose electric car moved its use the most, with the supplier's inference set against it", _score_ev),
        ("storage_heating", "Storage heating", "A two-rate (profile class 2) home billed on its meter's registers", _score_storage),
        ("shock_2022", "The 2022 shock", "The largest year-on-year rise in one month's bill through the 2022 crisis", _score_shock),
    ]


def _acq(hh):
    return min(a.get("acquisition_date") or "9999" for a in hh["legs"].values())


def _left(ev):
    r = _latest(ev["reaction"], lambda r: r.get("event_type") == "outcome_churned")
    return [(r["date"], "outcome", r)] if r else []


def _score_switch_in(hh, ev, person):
    acq = _acq(hh)
    inv = ev["invoice"]
    pays = [r for r in ev["ledger"] if r.get("type") == "payment_received"]
    if acq < "2016-02-01" or not pays:
        return None
    # A full first quarter: three bills on one fuel, the third at least 80 days after joining.
    per_fuel = defaultdict(list)
    for i in inv:
        per_fuel[i["fuel"]].append(i["date"])
    if not any(len(d) >= 3 and date.fromisoformat(d[2]).toordinal() - date.fromisoformat(acq).toordinal() >= 80
               for d in per_fuel.values()):
        return None
    keys = [(acq, "joined", {}), (inv[0]["date"], "first_bill", inv[0])]
    third = sorted(inv, key=lambda i: i["date"])[min(2, len(inv) - 1)]
    keys.append((third["date"], "bill", {**third, "label": "Three months in"}))
    return (acq, keys, 1)


def _score_renewal(hh, ev, person):
    best = None
    for r in ev["reaction"]:
        if r.get("event_type") == "retention_decision" and r.get("company_belief") is not None and r.get("sim_truth") is not None:
            gap = abs(r["company_belief"] - r["sim_truth"])
            if best is None or gap > best[0]:
                best = (gap, r)
    if not best:
        return None
    r = best[1]
    keys = [(_acq(hh), "joined", {}), (r["date"], "renewal_decision", r)]
    out = next((x for x in ev["reaction"] if x.get("event_type", "").startswith("outcome_") and x["date"] >= r["date"]), None)
    if out:
        keys.append((out["date"], "outcome", out))
    keys += [k for k in _left(ev) if k[0] > keys[-1][0]]
    return (best[0], keys, 1)


def _score_estimate_trap(hh, ev, person):
    best = None
    for fuel in hh["legs"]:
        inv = [i for i in ev["invoice"] if i["fuel"] == fuel]
        run = []
        for i in inv:
            if i.get("read_type") == "E":
                run.append(i)
                continue
            if run and i.get("catchup_applied") and (best is None or len(run) > best[0]):
                prev_a = _latest([x for x in inv if x["date"] < run[0]["date"] and x.get("read_type") == "A"])
                best = (len(run), fuel, run, i, prev_a)
            run = []
    if not best:
        return None
    n, fuel, run, catch, prev_a = best
    since = _day(prev_a["date"]) if prev_a else "the household joined"
    keys = [(_acq(hh), "joined", {}),
            (run[len(run) // 2]["date"], "estimate_run", {"fuel": fuel, "n": n, "since": since,
                                                         "kwh": sum(i.get("consumption_kwh") or 0 for i in run)}),
            (catch["date"], "catch_up", catch)]
    return (n, keys, 2)


def _score_mover(hh, ev, person):
    return None  # see MOVER_EMPTY_REASON; the record carries no move-out


MOVER_EMPTY_REASON = (
    "No household in this run can be shown moving. The published record carries no move-out event and "
    "no final-bill marker, and the new-occupant accounts (OCC-…) are not linked to the household they "
    "replaced, so a rule cannot follow a move from one occupant to the next."
)


def _score_debt(hh, ev, person):
    # The company desk's own journey when the record carries one; the ledger's notices otherwise.
    if any(str(r.get("event_type", "")).startswith("collections_") for r in ev["reaction"]):
        return _score_desk_debt(ev)
    depth = {"arrears_payment_missed": 1, "arrears_dd_failed": 1, "arrears_first_notice": 2, "arrears_second_notice": 3,
             "arrears_arrears_repaid": 4, "arrears_written_off": 5, "arrears_placed_with_dca": 6, "arrears_recovered": 7}
    arr = [r for r in ev["reaction"] if r.get("event_type") in depth]
    if not arr:
        return None
    deepest = max(depth[r["event_type"]] for r in arr)
    if deepest < 4:
        return None
    # One journey: from the first miss before the deepest step, through to that step.
    end = max(arr, key=lambda r: (depth[r["event_type"]], r["date"]))
    start = _latest([r for r in arr if r["date"] <= end["date"] and depth[r["event_type"]] == 1]) or arr[0]
    seq = [r for r in arr if start["date"] <= r["date"] <= end["date"]]
    picked, seen = [], set()
    for r in seq:
        if r["event_type"] not in seen:
            seen.add(r["event_type"])
            picked.append(r)
    picked = picked[:5]
    keys = [(r["date"], "debt", r) for r in picked]
    return (deepest * 1000 + len(seq), keys, len(keys) - 1)


#: The event types the debt rows read: the billing ledger's per-bill notices (`arrears_`) and the
#: company desk's collections journey (`collections_`, company/billing/collections_journey).
_DEBT_PREFIXES = ("arrears_", "collections_")

#: How far into the desk's ladder each stage is. An exit is deeper than any rung it can follow.
_DESK_DEPTH = {"collections_missed_payment": 1, "collections_moratorium_hold": 2,
               "collections_reminder": 2, "collections_reminder_2": 3,
               "collections_repayment_plan_offer": 4, "collections_arrangement_offered": 4,
               "collections_final_notice": 5, "collections_prepayment_or_debt_agency": 6,
               "collections_disconnection_warning_or_agency": 6, "collections_prepayment_offered": 6,
               "collections_statement_of_account": 2, "collections_interest_notice": 3,
               "collections_final_demand": 5, "collections_debt_recovery": 6,
               "collections_commercial_recovery": 6,
               "collections_repayment_plan_reoffer": 7, "collections_cured": 8,
               "collections_arrangement": 8, "collections_prepayment": 8, "collections_write_off": 9}
_DESK_TITLES = {"collections_missed_payment": "Missed a payment", "collections_reminder": "Reminder",
                "collections_reminder_2": "Second reminder",
                "collections_repayment_plan_offer": "Payment plan offered",
                "collections_arrangement_offered": "Arrangement put to the household",
                "collections_final_notice": "Final notice",
                "collections_prepayment_or_debt_agency": "Prepayment or agency",
                "collections_disconnection_warning_or_agency": "Disconnection warning or agency",
                "collections_prepayment_offered": "Prepayment offered",
                "collections_repayment_plan_reoffer": "Payment plan offered again",
                "collections_statement_of_account": "Statement of account",
                "collections_interest_notice": "Interest notice", "collections_final_demand": "Final demand",
                "collections_debt_recovery": "Debt recovery",
                "collections_commercial_recovery": "Commercial recovery",
                "collections_moratorium_hold": "Breathing Space", "collections_cured": "Debt cleared",
                "collections_arrangement": "Arrangement agreed",
                "collections_prepayment": "Moved to prepayment",
                "collections_write_off": "Written off (statute-barred)"}
_DESK_MESSAGES = {
    "collections_reminder": "Your account is overdue. Please pay or call us.",
    "collections_reminder_2": "Your account is still overdue. Please pay or call us.",
    "collections_repayment_plan_offer": "We can set up a payment plan you can afford.",
    "collections_arrangement_offered": "We can set up a payment plan you can afford.",
    "collections_final_notice": "This is our final notice about your overdue account.",
    "collections_prepayment_or_debt_agency": "We may pass your debt to an agency, or offer a prepayment meter.",
    "collections_prepayment_offered": "We can fit a prepayment meter, with your consent.",
    "collections_repayment_plan_reoffer": "Your account is still overdue. Our payment plan offer stands.",
    "collections_moratorium_hold": "We have paused collection while your Breathing Space lasts.",
    "collections_cured": "Thank you: your account is no longer overdue.",
    "collections_arrangement": "Your payment plan is agreed.",
    "collections_write_off": "We have written off the old debt on your account.",
}
#: The desk's stages that are a decision the company took, for the record's last-decision line.
_DESK_DECISIONS = ("collections_repayment_plan_offer", "collections_final_notice",
                   "collections_prepayment_or_debt_agency", "collections_prepayment_offered",
                   "collections_repayment_plan_reoffer", "collections_write_off")


def _score_desk_debt(ev):
    """The deepest of the desk's journeys, from its opening miss to its deepest stage."""
    arr = [r for r in ev["reaction"] if r.get("event_type") in _DESK_DEPTH]
    if not arr:
        return None
    deepest = max(_DESK_DEPTH[r["event_type"]] for r in arr)
    if deepest < 4:
        return None
    end = max(arr, key=lambda r: (_DESK_DEPTH[r["event_type"]], r["date"]))
    start = _latest([r for r in arr if r["date"] <= end["date"]
                     and r["event_type"] == "collections_missed_payment"]) or arr[0]
    seq = [r for r in arr if start["date"] <= r["date"] <= end["date"]]
    picked, seen = [], set()
    for r in seq:
        # A re-offer repeats by design; one is enough to show the step after the top rung exists.
        if r["event_type"] not in seen:
            seen.add(r["event_type"])
            picked.append(r)
    if len(picked) > 5:
        picked = picked[:4] + [picked[-1]]
    keys = [(r["date"], "debt", r) for r in picked]
    return (deepest * 1000 + len(seq), keys, len(keys) - 1)


def _score_ev(hh, ev, person):
    best = None
    for e in ev["timeline"]:
        if e.get("type") == "life_event" and "ev" in e.get("detail", "").lower().split():
            m = re.search(r"([+-]\d+)%", e.get("effect") or "")
            mv = abs(int(m.group(1))) if m else 0
            if best is None or mv > best[0]:
                best = (mv, e)
    if not best:
        return None
    e = best[1]
    keys = [(_acq(hh), "joined", {}), (e["date"], "life_event", e)]
    nxt = next((i for i in ev["invoice"] if i["date"] > e["date"] and i["fuel"] == "electricity"
                and i.get("read_type") == "A"), None)
    if nxt:
        keys.append((nxt["date"], "catch_up" if nxt.get("catchup_applied") else "first_bill", nxt))
    return (best[0], keys, 1)


def _score_storage(hh, ev, person):
    for i in ev["invoice"]:
        if len(i.get("registers") or []) > 1:
            return (1, [(_acq(hh), "joined", {}), (i["date"], "first_bill", i)], 1)
    return None


STORAGE_EMPTY_REASON = (
    "No household in this run has a two-rate meter. Every bill in the published run is a single "
    "'Anytime' register, so there is no profile class 2 home to show."
)


def _score_shock(hh, ev, person):
    best = None
    by = {(i["fuel"], i["date"][:7]): i for i in ev["invoice"] if not i.get("catchup_applied")}
    for (fuel, m), i in by.items():
        if not ("2022-04" <= m <= "2023-03"):
            continue
        prev = by.get((fuel, "{}-{}".format(int(m[:4]) - 1, m[5:])))
        if not prev or not prev.get("amount_gbp") or not i.get("amount_gbp"):
            continue
        rise = i["amount_gbp"] - prev["amount_gbp"]
        if best is None or rise > best[0]:
            best = (rise, i, prev)
    if not best or best[0] <= 0:
        return None
    rise, i, prev = best
    rec = {"fuel": i["fuel"], "month": datetime.strptime(i["date"][:7], "%Y-%m").strftime("%B %Y"),
           "now": i["amount_gbp"], "before": prev["amount_gbp"],
           "kwh_now": i.get("consumption_kwh") or 0, "kwh_before": prev.get("consumption_kwh") or 0}
    keys = [(_acq(hh), "joined", {}), (prev["date"], "bill", {**prev, "label": "A year earlier"}), (i["date"], "shock_2022", rec)]
    return (rise, keys, 2)


EMPTY_REASONS = {"mover": MOVER_EMPTY_REASON, "storage_heating": STORAGE_EMPTY_REASON}


def _story_line(slot_id, hh, keys) -> str:
    k = keys
    return {
        "switch_in": "Joined on {} and was billed from its first month.".format(_day(k[0][0])),
        "renewal": "At renewal the supplier's churn belief and the truth were furthest apart.",
        "estimate_trap": "A long run of estimated bills, ended by a meter read.",
        "debt": "From a missed payment to the end of the debt.",
        "ev": "An electric car arrives; the supplier sees only the meter.",
        "shock_2022": "The 2022 crisis reaches one household's bill.",
    }.get(slot_id, "")


# ── Build ─────────────────────────────────────────────────────────────────────────────────────


def build(customers: dict[str, dict], sample: dict, windows: list[dict], known_by=None) -> dict:
    global _known_by
    saved = _known_by
    if known_by is not None:
        _known_by = known_by
    try:
        return _build(customers, sample, windows)
    finally:
        _known_by = saved


def _build(customers, sample, windows):
    hhs = households(customers)
    people = sample.get("customers") or {}
    events = {hh["id"]: _events(hh) for hh in hhs}
    book_breaches = defaultdict(int)
    hh_breaches = {}
    for hh in hhs:
        seg = hh["legs"][next(iter(hh["legs"]))].get("segment") or "resi"
        b = coverage_breaches(hh, events[hh["id"]], windows, seg)
        hh_breaches[hh["id"]] = b
        for x in {x["rule"] for x in b}:
            book_breaches[x] += 1
    used, slots = set(), []
    for slot_id, feature, rule, scorer in _cast_rules():
        best = None
        for hh in hhs:
            if hh["id"] in used:
                continue
            got = scorer(hh, events[hh["id"]], people.get(hh["id"]) or {})
            if got and (best is None or got[0] > best[0][0]):
                best = (got, hh)
        if not best:
            slots.append({"id": slot_id, "feature": feature, "rule": rule, "filled": False,
                          "glossary": GLOSSARY[slot_id],
                          "reason": EMPTY_REASONS.get(slot_id, "No household in this run qualifies under this rule.")})
            continue
        (score, keys, opening), hh = best
        used.add(hh["id"])
        ev = events[hh["id"]]
        person = people.get(hh["id"]) or {}
        telling = keys[opening]
        keys = sorted({k[0] + k[1]: k for k in keys}.values(), key=lambda k: k[0])[:6]
        moments = _moments_for(hh, ev, keys)
        for m in moments:
            seen = _before_outcome(ev, m["iso"]) if m["kind"] == "renewal_decision" else ev
            m["supplier"], m["decision"] = _supplier(hh, seen, m["iso"])
            m["truth"] = _truth(hh, seen, person, m["iso"])
            m["portal"] = _portal(hh, seen, m["iso"], m.pop("portal_message"))
        # The page opens on the moment the rule chose the household for, not on a free slider.
        opening = next((j for j, k in enumerate(keys) if k[:2] == telling[:2]), 0)
        legs = hh["legs"]
        first = legs[next(iter(legs))]
        span_end = max((i["date"] for i in ev["invoice"]), default=_acq(hh))
        slots.append({
            "id": slot_id, "feature": feature, "rule": rule, "filled": True, "glossary": GLOSSARY[slot_id],
            "household": hh["id"], "fuels": list(legs), "segment": first.get("segment"),
            "span": "{} to {}".format(_day(_acq(hh)), _day(span_end)),
            "story": _story_line(slot_id, hh, keys),
            "opening": opening,
            "moments": moments,
            "breaches": hh_breaches[hh["id"]][:6],
            "breach_count": len(hh_breaches[hh["id"]]),
        })
    meta_src = sample.get("meta") or {}
    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "run_generated_at": meta_src.get("generated_at"),
            "run_git_commit": meta_src.get("git_commit"),
            "household_count": len(hhs),
            "note": "Every household is chosen by the slot's stated rule at publish; nobody is hand-picked. "
                    "The supplier column reads only records dated on or before the moment shown.",
        },
        "slots": slots,
        "coverage": {
            "filled": sum(s["filled"] for s in slots), "of": len(slots),
            "empty": [s["id"] for s in slots if not s["filled"]],
            "book_breaches": {k: {"households": v, "of": len(hhs)} for k, v in sorted(book_breaches.items())},
        },
    }


# ── The Monday verdict (steer item 4, third bullet) ───────────────────────────────────────────

STAGING = PROJECT / "docs" / "staging"
_CAST_FINDING = ("SEAT_FINDING_EXPLORES_CAST_FINDS_STANDARD_VARIABLE_BILLS_ABOVE_THE_CAP_AND_NO_MOVER"
                 "_OR_TWO_RATE_HOME_2026-10-23.md")
#: Each gap the checks find today, and the open finding that accounts for it. A gap with no entry,
#: or whose finding has left the open rooms while the gap remains, is RED: a feature has stopped
#: working and nothing is working on it. An entry whose gap has closed is reported, never red, so
#: the run getting more honest cannot red the build.
ACCOUNTED_BY = {"above_cap": _CAST_FINDING, "mover": _CAST_FINDING, "storage_heating": _CAST_FINDING}


def _open_finding(name: str, staging: Path) -> bool:
    return (staging / name).is_file() or (staging / "in_progress" / name).is_file()


def coverage_verdict(feed: dict | None, staging: Path | None = None) -> dict:
    """Every empty slot and every breached rule in `feed`, graded against `ACCOUNTED_BY`.

    Returns `red` (gaps no open finding accounts for), `accounted` (gaps an open finding names) and
    `spent` (entries whose gap is gone). A feed that is missing or misshapen is red, never clean.
    """
    staging = staging or STAGING
    try:
        cov = feed["coverage"]
        slot_ids = [s["id"] for s in feed["slots"]]
        gaps = [("slot", sid, "no household qualifies") for sid in cov["empty"]]
        gaps += [("rule", r, "{} of {} households".format(v["households"], v["of"]))
                 for r, v in cov["book_breaches"].items() if v["households"]]
    except (KeyError, TypeError, AttributeError) as exc:
        return {"red": ["the cast feed is missing or misshapen ({!r}), so no check ran".format(exc)],
                "accounted": [], "spent": []}
    missing = [sid for sid, *_ in _cast_rules() if sid not in slot_ids]
    red = ["slot {}: the feed has no such slot, so its rule did not run".format(s) for s in missing]
    accounted = []
    for kind, gid, what in gaps:
        name = ACCOUNTED_BY.get(gid)
        if name and _open_finding(name, staging):
            accounted.append("{} {}: {} -- open in {}".format(kind, gid, what, name))
        elif name:
            red.append("{} {}: {} -- and its finding {} is no longer open".format(kind, gid, what, name))
        else:
            red.append("{} {}: {} -- and no open finding accounts for it".format(kind, gid, what))
    live = {g[1] for g in gaps}
    spent = ["{}: its gap has closed; drop the entry".format(k) for k in ACCOUNTED_BY if k not in live]
    return {"red": red, "accounted": accounted, "spent": spent}


# ── Static first render (the page shows without JavaScript) ───────────────────────────────────


def static_html(feed: dict) -> str:
    e = html.escape
    parts = ['<p class="stamp">Run of {} · {} of {} feature slots filled</p>'.format(
        e(_day(feed["meta"]["run_generated_at"] or feed["meta"]["generated_at"])),
        feed["coverage"]["filled"], feed["coverage"]["of"])]
    parts.append('<ul class="static-cast">')
    for s in feed["slots"]:
        if s["filled"]:
            m = s["moments"][s["opening"]]
            parts.append("<li><strong>{}</strong> · household {} · {}: {}</li>".format(
                e(s["feature"]), e(s["household"]), e(m["date"]), e(m["story"])))
        else:
            parts.append("<li><strong>{}</strong> · empty: {}</li>".format(e(s["feature"]), e(s["reason"])))
    parts.append("</ul>")
    return "".join(parts)


def write_static(feed: dict, page: Path = PAGE_PATH) -> bool:
    if not page.is_file():
        return False
    text = page.read_text(encoding="utf-8")
    new = re.sub(r"(<!--cast:static-->)[\s\S]*?(<!--/cast:static-->)",
                 lambda m: m.group(1) + static_html(feed) + m.group(2), text)
    if new != text:
        page.write_text(new, encoding="utf-8")
    return True


def generate(out_path: Path = OUT_PATH) -> dict:
    customers = _load_customers(CUSTOMERS_DIR)
    sample = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    feed = build(customers, sample, _cap_windows())
    out_path.write_text(json.dumps(feed, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    write_static(feed)
    return feed


if __name__ == "__main__":
    f = generate()
    print("explore cast: {}/{} slots filled; empty: {}; book breaches: {}".format(
        f["coverage"]["filled"], f["coverage"]["of"], ", ".join(f["coverage"]["empty"]) or "none",
        json.dumps(f["coverage"]["book_breaches"])))
