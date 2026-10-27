#!/usr/bin/env python3
"""THE DOMAIN-INVARIANT RUNNER — every account of a book against `DOMAIN_INVARIANTS.yaml`.

Director ruling of 26 Oct (`DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26`), step 4:
two-sided ranges per quantity per period, written from the knowledge pages by an agent that had not
read the code under test, run over every household. The invariants file is that agent's; this
module is the other half. It reads the file and the published raw export and prints, per
invariant, what it checked, what breached, what it only flags, and the unit it counted.

## WHAT IT READS, AND WHY ONLY THAT

The raw export (`company.billing.raw_account_export`): reads, contracted terms, payments, nothing
derived. That module is the runner's only repository import, used only for `--ledger`. A runner
that imported the biller or the pricing tables would share their beliefs and agree with them by
construction, which is how the Explore errors passed every test written by the code's own authors.

## HOW THE FILE'S WORDS ARE READ HERE

Each invariant carries its own predicate in prose, so evaluators are registered by invariant ID.
Five statuses are never "clean":
  UNCHECKABLE    the file says the export cannot answer it, with its reason;
  NOT_IN_EXPORT  the file says it can, but the field it needs is on no period of this export;
  NO_EVALUATOR   an ID this runner has no code for: a new row shows up as unrun, not as passing;
  UNREACHED      an evaluator ran and found nothing it applied to;
  FLAGGED        only the file's `flag` severities fired. A flag is evidence to explain; a
                 BREACH is the file's `breach` severity, and is what the ruling's gate counts.

Readings this runner makes where the file's text leaves a choice, each named where it is used:
  * `tariff_effective_to` is EXCLUSIVE: on the books measured, every successive term starts on the
    previous term's `tariff_effective_to`.
  * an ACCOUNT is one `customer_id`, one fuel. The file's heating-class proxy ("same customer_id
    also holds gas") is read through the export's `billing_account_id`, which both fuels of one
    household share: an electricity account whose billing account also holds gas takes the
    gas-heated band, one whose billing account holds none takes the not-gas-heated band. An
    export without `billing_account_id` falls back to the all-domestic band.
  * the read duty also counts the run from the last actual read to the end of supply: the duty
    runs for as long as the account is supplied.

## THE GATE

The ruling says a breach blocks the publish or is a named, dated exception. `gate` reads the
exceptions register (`DOMAIN_INVARIANT_EXCEPTIONS.yaml`) and names every invariant whose BREACHED
count no valid exception covers. `background/process_run_complete.py` grades every completed run's
book with it and refuses the publish only while the register says `enforce: true`; until the fresh
run's grade lands it is report-only, and the count goes into `docs/reports/DOMAIN_INVARIANTS.md`.
`--strict` returns 1 on any unexcepted BREACH.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
INVARIANTS_PATH = PROJECT / "docs" / "design" / "DOMAIN_INVARIANTS.yaml"
EXCEPTIONS_PATH = PROJECT / "docs" / "design" / "DOMAIN_INVARIANT_EXCEPTIONS.yaml"
#: What an exception must say to lift anything. One missing and it lifts nothing, and says so.
EXCEPTION_FIELDS = ("invariant", "scope", "reason", "filed", "retired_by")

#: How the raw export spells a reading of the register (the read duty counts a customer's own read).
ACTUAL_READ_TYPES = {"A", "actual", "C", "customer"}
OPENING = "carried_forward"
PREPAYMENT, DIRECT_DEBIT = "prepayment", "direct_debit"
DOMESTIC_SEGMENTS = {"resi", "domestic"}
#: The EPG windows the file's cross-fuel invariant excludes, by its own text.
EPG_FROM, EPG_TO = date(2022, 10, 1), date(2023, 6, 30)


def _d(s) -> date:
    return date.fromisoformat(str(s)[:10])


def _num(v):
    return None if v is None or v == "None" else float(v)


def load_invariants(path: Path = INVARIANTS_PATH) -> list[dict]:
    import yaml
    return yaml.safe_load(path.read_text())["invariants"]


def load_book(raw_path: Path | None = None, ledger_path: Path | None = None,
              events_path: Path | None = None) -> dict[str, dict]:
    """customer_id -> raw export, its `events` (the company's dated acts) beside it where known.
    From a bundle the export wrote, or produced from a ledger here."""
    if raw_path is not None:
        book = json.loads(raw_path.read_text())
        if events_path is not None:
            for cid, ev in json.loads(events_path.read_text()).items():
                if book.get(cid) is not None:
                    book[cid]["events"] = ev
        return book
    from company.billing.raw_account_export import account_events, derived_leaks, raw_account
    ledger = json.loads(ledger_path.read_text())
    out = {}
    for cid, rec in (ledger.get("customers") or {}).items():
        r, ev = raw_account(cid, rec), account_events(cid, rec)
        leaks = derived_leaks(r) + derived_leaks(ev)
        if leaks:
            raise ValueError("the raw export for {} carries derived fields: {}".format(cid, leaks[:3]))
        out[cid] = dict(r, events=ev)
    return out


# ── the book, read as accounts ──────────────────────────────────────────────────────────────

class Account:
    def __init__(self, cid: str, raw: dict):
        self.cid, self.segment = cid, raw.get("segment")
        self.billing_account = raw.get("billing_account_id")
        self.periods = sorted(raw.get("periods", ()), key=lambda p: p["period_start"])
        self.fuel = self.periods[0]["commodity"] if self.periods else None
        self.payments = sorted((p for p in raw.get("payments", ()) if p.get("payment_date")),
                               key=lambda p: p["payment_date"])
        self.adjustments = raw.get("adjustments") or ()
        # The company's dated acts (`raw_account_export.account_events`), where the book has them.
        events = raw.get("events") or {}
        self.bills = events.get("bills") or ()
        self.journeys = events.get("collections_journeys") or ()
        self.renewals = events.get("renewal_offers") or ()
        # None, not empty, on a book whose run predates the SLC 22C statement.
        self.notices = events.get("renewal_notices")
        self.registers = {r.get("register_id") for p in self.periods for r in p.get("reads", ())}
        self.start = _d(self.periods[0]["period_start"]) if self.periods else None
        self.end = _d(self.periods[-1]["period_end"]) if self.periods else None

    @property
    def domestic(self) -> bool:
        return self.segment in DOMESTIC_SEGMENTS

    def methods_between(self, a: date, b: date) -> set:
        return {p.get("payment_method") for p in self.payments if a <= _d(p["payment_date"]) <= b}

    @property
    def prepayment(self) -> bool:
        return any(p.get("payment_method") == PREPAYMENT for p in self.payments)

    def terms(self):
        """Each distinct contracted term once, its end exclusive, open terms ending with supply."""
        seen = {}
        for p in self.periods:
            regs = {r.get("register_id") for r in p.get("reads", ())}
            for t in p.get("contracted_terms") or ():
                key = (t["tariff_effective_from"], t.get("tariff_effective_to"), t.get("tariff_type"))
                if key not in seen:
                    end = (_d(t["tariff_effective_to"]) - timedelta(days=1)
                           if t.get("tariff_effective_to") else self.end)
                    seen[key] = dict(t, _from=_d(t["tariff_effective_from"]), _last=end,
                                     _registers=set())
                seen[key]["_registers"] |= regs
        return list(seen.values())


def period_kwh(p: dict) -> float | None:
    """Closing minus opening read, summed over registers; the exported volume where no pair exists."""
    by_reg = defaultdict(list)
    for r in p.get("reads", ()):
        by_reg[r.get("register_id")].append(r)
    total, pairs = 0.0, 0
    for reads in by_reg.values():
        opening = [r for r in reads if r.get("read_type") == OPENING]
        closing = [r for r in reads if r.get("read_type") != OPENING]
        if opening and closing:
            total += float(closing[-1]["read_kwh"]) - float(opening[0]["read_kwh"])
            pairs += 1
    if pairs:
        return total
    return _num(p.get("consumption_kwh"))


class Tally:
    def __init__(self, unit: str):
        self.unit, self.checked, self.unbounded = unit, 0, 0
        self.breaches, self.flags = [], []

    def hit(self, severity: str, where: str, value, bound, side: str):
        (self.breaches if severity == "breach" else self.flags).append(
            {"where": where, "value": value, "bound": bound, "side": side})

    def band(self, where, value, lower, upper, *, below="breach", above="breach",
             tol_rel=0.0, tol_abs=0.0):
        """One two-sided check. A side with no bound is not checked; neither bound is UNBOUNDED."""
        if lower is None and upper is None:
            self.unbounded += 1
            return
        self.checked += 1
        if value is None:
            self.hit("breach", where, None, (lower, upper), "missing")
        elif lower is not None and value < lower - tol_abs:
            self.hit(below, where, value, lower, "below")
        elif upper is not None and value > upper * (1 + tol_rel) + tol_abs:
            self.hit(above, where, value, upper, "above")


def _rows(inv) -> list[dict]:
    return [dict(r, _from=_d(r["from"]), _to=_d(r["to"])) for r in inv.get("rows") or ()
            if r.get("from") and r.get("to")]


def _row_on(rows, on: date):
    return next((r for r in rows if r["_from"] <= on <= r["_to"]), None)


def _tol(inv, key) -> float:
    return float((inv.get("tolerance") or {}).get(key) or 0.0)


def _upper_for_methods(row: dict, methods: set):
    """The file's column rule: any prepayment -> prepayment; all DD -> DD; else standard credit;
    no payments in the window -> the largest of the three."""
    cols = {"dd": _num(row.get("upper")), "sc": _num(row.get("upper_standard_credit")),
            "pp": _num(row.get("upper_prepayment"))}
    methods = methods - {None}
    if not methods:
        known = [v for v in cols.values() if v is not None]
        return max(known) if known else None
    if PREPAYMENT in methods:
        return cols["pp"] if cols["pp"] is not None else cols["dd"]
    if methods == {DIRECT_DEBIT}:
        return cols["dd"]
    return cols["sc"] if cols["sc"] is not None else cols["dd"]


# ── evaluators, by invariant ID ─────────────────────────────────────────────────────────────

def _svt_term_windows(inv, book, fuel, meter):
    """(account, term, row) for every SVT term and every cap-window row the term overlaps."""
    rows = _rows(inv)
    for a in book:
        if a.fuel != fuel or not a.domestic:
            continue
        for t in a.terms():
            if t.get("tariff_type") != "svt" or t["_last"] is None:
                continue
            # The meter class is the term's own: the registers its periods print. A household that
            # changes meter mid-account has an SVT spell of each class (SLC 28AD grades by tariff).
            # A term whose periods print no read has no class of its own; it takes the account's.
            n = len(t["_registers"] or a.registers)
            if meter == "single" and n != 1 or meter == "multi" and n < 2:
                continue
            for row in rows:
                if t["_from"] <= row["_to"] and t["_last"] >= row["_from"]:
                    yield a, t, row


def ev_unit_rate_svt_elec(inv, book):
    tally = Tally("SVT term x cap window it overlaps (single-register electricity)")
    tol = _tol(inv, "upper_relative")
    for a, t, row in _svt_term_windows(inv, book, "electricity", "single"):
        upper = _upper_for_methods(row, a.methods_between(row["_from"], row["_to"]))
        tally.band("{} {} from {}".format(a.cid, row["from"], t["tariff_effective_from"]),
                   _num(t.get("unit_rate_p_per_kwh")), _num(row.get("lower")), upper,
                   below="flag", above="breach", tol_rel=tol)
    return tally


def ev_unit_rate_svt_elec_pre_cap(inv, book):
    tally = Tally("SVT term x pre-cap half-year it overlaps (single-register electricity)")
    for a, t, row in _svt_term_windows(inv, book, "electricity", "single"):
        tally.band("{} {} from {}".format(a.cid, row["from"], t["tariff_effective_from"]),
                   _num(t.get("unit_rate_p_per_kwh")), _num(row.get("lower")), None, below="flag")
    return tally


def ev_unit_rate_svt_gas(inv, book):
    """The electricity column rule, since the commons carries gas per payment method (2026-10-27).
    Under the commodity floor is a flag; a rate that is not positive stays a breach."""
    tally = Tally("SVT term x cap window it overlaps (gas)")
    tol = _tol(inv, "upper_relative")
    for a, t, row in _svt_term_windows(inv, book, "gas", None):
        rate = _num(t.get("unit_rate_p_per_kwh"))
        where = "{} {} from {}".format(a.cid, row["from"], t["tariff_effective_from"])
        if rate is not None and rate <= 0:
            tally.band(where, rate, 0.0, None, tol_abs=-1e-12)
            continue
        upper = _upper_for_methods(row, a.methods_between(row["_from"], row["_to"]))
        tally.band(where, rate, _num(row.get("lower")), upper, below="flag", tol_rel=tol)
    return tally


def ev_unit_rate_svt_gas_pre_cap(inv, book):
    tally = Tally("SVT term x pre-cap half-year it overlaps (gas)")
    for a, t, row in _svt_term_windows(inv, book, "gas", None):
        rate = _num(t.get("unit_rate_p_per_kwh"))
        where = "{} {} from {}".format(a.cid, row["from"], t["tariff_effective_from"])
        if rate is not None and rate <= 0:
            tally.band(where, rate, 0.0, None, tol_abs=-1e-12)
        else:
            tally.band(where, rate, _num(row.get("lower")), None, below="flag")
    return tally


def ev_unit_rate_svt_elec_multi(inv, book):
    """The term's single rate is read as the tariff's assumed-split blend; where the term carries the
    peak/off-peak pair, that pair is weighted 0.58/0.42 as the file says (SLC 28AD.36(a))."""
    tally = Tally("SVT term x cap window it overlaps (multi-register electricity)")
    tol = _tol(inv, "upper_relative")
    for a, t, row in _svt_term_windows(inv, book, "electricity", "multi"):
        rate = _num(t.get("unit_rate_p_per_kwh"))
        pair = {x["register_label"]: x["unit_rate_p_per_kwh"] for x in t.get("tou_unit_rates") or ()}
        if "Peak" in pair and "Off-peak" in pair:
            rate = 0.58 * pair["Peak"] + 0.42 * pair["Off-peak"]
        tally.band("{} {} from {}".format(a.cid, row["from"], t["tariff_effective_from"]),
                   rate, None, _num(row.get("upper")), tol_rel=tol)
    return tally


def ev_unit_rate_fixed(inv, book, pre_cap_rows=()):
    """Electricity: floor of the window the fix was STRUCK in, over the whole term (flag). A fix
    struck before 2019 takes the pre-cap back-cast floor, the same quantity for that window. Gas:
    positive only (the file has no gas floor)."""
    tally = Tally("fixed term, graded once at the window it was struck in")
    rows = _rows(inv) + list(pre_cap_rows)
    for a in book:
        if not a.domestic:
            continue
        for t in a.terms():
            if t.get("tariff_type") != "fixed":
                continue
            rate = _num(t.get("unit_rate_p_per_kwh"))
            where = "{} {} fixed from {}".format(a.cid, a.fuel, t["tariff_effective_from"])
            if a.fuel == "gas":
                tally.band(where, rate, 0.0, None, tol_abs=-1e-12)
                continue
            row = _row_on(rows, t["_from"])
            tally.band(where, rate, None if row is None else _num(row.get("lower")), None,
                       below="flag")
    return tally


def _sc_periods(inv, book, fuel, tariff):
    rows = _rows(inv)
    for a in book:
        if (fuel and a.fuel != fuel) or not a.domestic:
            continue
        for p in a.periods:
            kinds = {t.get("tariff_type") for t in p.get("contracted_terms") or ()}
            if tariff not in kinds:
                continue
            yield a, p, _row_on(rows, _d(p["period_start"]))


def _sc_tol(inv, p) -> float:
    """The per-day tolerance, or a penny over the period where the file gives one: the bill rounds
    the period's charge to the penny and prints the shortest per-day rate that reproduces it."""
    per_period, days = _tol(inv, "upper_absolute_gbp_per_period"), _num(p.get("days_in_period"))
    per_day = _tol(inv, "upper_absolute_gbp_per_day")
    return max(per_day, per_period / days) if per_period and days else per_day


def ev_standing_charge_svt_elec(inv, book):
    tally = Tally("SVT bill period (electricity)")
    for a, p, row in _sc_periods(inv, book, "electricity", "svt"):
        if row is None:
            continue
        upper = _upper_for_methods(row, a.methods_between(row["_from"], row["_to"]))
        tally.band("{} {}".format(a.cid, p["period_start"]), _num(p.get("standing_charge_gbp_per_day")),
                   _num(row.get("lower")), upper, tol_abs=_sc_tol(inv, p))
    return tally


def ev_standing_charge_svt_gas(inv, book):
    tally = Tally("SVT bill period (gas; ceiling in DD-only windows)")
    for a, p, row in _sc_periods(inv, book, "gas", "svt"):
        if row is None:
            continue
        dd_only = a.methods_between(row["_from"], row["_to"]) - {None} == {DIRECT_DEBIT}
        tally.band("{} {}".format(a.cid, p["period_start"]), _num(p.get("standing_charge_gbp_per_day")),
                   _num(row.get("lower")), _num(row.get("upper")) if dd_only else None,
                   tol_abs=_sc_tol(inv, p))
    return tally


def ev_standing_charge_fixed(inv, book):
    tally = Tally("fixed bill period")
    for a in book:
        if not a.domestic:
            continue
        for p in a.periods:
            if "fixed" in {t.get("tariff_type") for t in p.get("contracted_terms") or ()}:
                tally.band("{} {} {}".format(a.cid, a.fuel, p["period_start"]),
                           _num(p.get("standing_charge_gbp_per_day")), _num(inv.get("lower")),
                           _num(inv.get("upper")))
    return tally


def account_years(book, fuel):
    """(account, year, kWh) for calendar years an account was supplied in full with a volume for
    every period. The file asks for complete 365-day runs; a calendar year is one such run."""
    for a in book:
        if a.fuel != fuel or not a.domestic:
            continue
        by_year = defaultdict(lambda: [0, 0.0, True])
        for p in a.periods:
            y = by_year[_d(p["period_start"]).year]
            y[0] += int(p.get("days_in_period") or 0)
            kwh = period_kwh(p)
            if kwh is None:
                y[2] = False
            else:
                y[1] += kwh
        for year, (days, kwh, complete) in sorted(by_year.items()):
            if complete and days >= 365:
                yield a, year, kwh


def _binomial_upper(n: int, p: float, z: float = 3.09) -> float:
    """One-sided 99.9% normal-approximation upper bound on a share, for the file's book-level check."""
    return p + z * math.sqrt(p * (1 - p) / n) if n else 1.0


def _heating_band(inv, a, gas_billing_accounts):
    """The flag band for this account's heating class (the runner's reading, module docstring)."""
    bands = inv.get("flag_bands") or ()

    def starting(prefix):
        return next((b for b in bands if str(b.get("class", "")).startswith(prefix)), None)

    every = starting("all") or {}
    if a.fuel != "electricity" or not a.billing_account:
        return every
    cls = starting("gas-heated") if a.billing_account in gas_billing_accounts else starting("gas not")
    # a class band carries only its own percentiles; the 500 kWh floor is the all-domestic band's
    return dict(every, **(cls or {}))


def _annual_use(inv, book, fuel, hard_flag_upper=None):
    tally = Tally("complete calendar account-year ({})".format(fuel))
    gas_billing_accounts = {a.billing_account for a in book if a.fuel == "gas" and a.billing_account}
    years = list(account_years(book, fuel))
    above_p99 = 0
    for a, year, kwh in years:
        band = _heating_band(inv, a, gas_billing_accounts)
        where = "{} {} {:.0f} kWh".format(a.cid, year, kwh)
        tally.band(where, kwh, _num(inv.get("lower")), _num(inv.get("upper")))
        lo, hi = _num(band.get("flag_lower")), _num(band.get("flag_upper_p99"))
        if lo is not None and kwh < lo:
            tally.hit("flag", where, kwh, lo, "below the flag band")
        if hi is not None and kwh > hi:
            above_p99 += 1
            tally.hit("flag", where, kwh, hi, "above the class p99")
        if hard_flag_upper is not None and kwh > hard_flag_upper:
            tally.hit("flag", where, kwh, hard_flag_upper, "above the hard flag")
    if years and any(b.get("flag_upper_p99") is not None for b in inv.get("flag_bands") or ()):
        share, bound = above_p99 / len(years), _binomial_upper(len(years), 0.01)
        tally.book = {"above_p99": above_p99, "of": len(years), "share": round(share, 4),
                      "upper_999": round(bound, 4), "flag": share > bound}
    return tally


def ev_annual_use_elec(inv, book):
    return _annual_use(inv, book, "electricity")


def ev_annual_use_gas(inv, book):
    return _annual_use(inv, book, "gas",
                       hard_flag_upper=_num((inv.get("hard_flag") or {}).get("upper")))


def ev_annual_use_book_median(inv, book):
    """Per TDCV row: the median of complete account-years whose midpoint (1 July) falls in the
    row, with its order-statistic 95% CI; a breach only if the whole CI lies outside [low, high]."""
    tally = Tally("TDCV row x fuel class (book median)")
    years = {"gas": list(account_years(book, "gas")), "electricity": list(account_years(book, "electricity"))}
    for row in _rows(inv):
        cls = str(row.get("class", ""))
        fuel = "gas" if cls.startswith("gas") else "electricity"
        multi = "multi" in cls
        xs = sorted(kwh for a, y, kwh in years[fuel]
                    if row["_from"] <= date(y, 7, 1) <= row["_to"]
                    and (fuel == "gas" or (len(a.registers) >= 2) == multi))
        where = "{} {}..{} n={}".format(cls, row["from"], row["to"], len(xs))
        if len(xs) < 10:
            tally.unbounded += 1
            continue
        n = len(xs)
        k = max(0, int(n / 2 - 1.96 * math.sqrt(n) / 2))
        ci = (xs[k], xs[min(n - 1, n - 1 - k)])
        lo, hi = _num(row.get("lower")), _num(row.get("upper"))
        tally.checked += 1
        median = xs[n // 2]
        if lo is not None and ci[1] < lo:
            tally.hit("breach", where, median, lo, "below (whole CI {:.0f}-{:.0f})".format(*ci))
        elif hi is not None and ci[0] > hi:
            tally.hit("breach", where, median, hi, "above (whole CI {:.0f}-{:.0f})".format(*ci))
    return tally


def ev_read_duty_annual(inv, book):
    tally = Tally("credit account (prepayment excluded): longest run without an actual read")
    upper = _num(inv.get("upper")) + _tol(inv, "upper_days")
    for a in book:
        if not a.domestic or a.prepayment or not a.periods:
            continue
        actual = sorted({_d(r["read_date"]) for p in a.periods for r in p.get("reads", ())
                         if r.get("read_type") in ACTUAL_READ_TYPES})
        marks = [a.start] + [x for x in actual if a.start <= x <= a.end] + [a.end]
        gap = max((y - x).days for x, y in zip(marks, marks[1:]))
        tally.band("{} {} {}..{}".format(a.cid, a.fuel, a.start, a.end), gap, None, upper, above="flag")
    return tally


def ev_settlement_actual_share(inv, book):
    """Book-level: of electricity kWh in periods ending at least 14 months before the export's end,
    the share in periods ending on or before the account's latest actual read."""
    tally = Tally("book (electricity kWh)")
    ends = [a.end for a in book if a.end]
    if not ends:
        return tally
    cutoff = max(ends) - timedelta(days=426)
    bounded = total = 0.0
    for a in book:
        if a.fuel != "electricity":
            continue
        actual = [_d(r["read_date"]) for p in a.periods for r in p.get("reads", ())
                  if r.get("read_type") in ACTUAL_READ_TYPES]
        last = max(actual) if actual else None
        for p in a.periods:
            if _d(p["period_end"]) > cutoff:
                continue
            kwh = max(0.0, period_kwh(p) or 0.0)
            total += kwh
            if last is not None and _d(p["period_end"]) <= last:
                bounded += kwh
    if not total:
        return tally                                  # no kWh old enough to have settled: unreached
    share = bounded / total
    tally.band("book share {:.4f} of {:.0f} kWh".format(share, total), share,
               _num(inv.get("lower")), _num(inv.get("upper")), below="flag")
    return tally


def ev_bill_twice_yearly(inv, book):
    tally = Tally("bill period of a domestic credit account")
    for a in book:
        if not a.domestic or a.prepayment:
            continue
        for p in a.periods:
            tally.band("{} {} {}".format(a.cid, a.fuel, p["period_start"]), p.get("days_in_period"),
                       _num(inv.get("lower")), _num(inv.get("upper")), above="flag")
    return tally


def ev_opening_read(inv, book):
    tally = Tally("account: days from first period_start to its first read")
    rows = {r.get("commodity"): r for r in inv.get("rows") or ()}
    for a in book:
        row = rows.get(a.fuel)
        reads = [_d(r["read_date"]) for p in a.periods for r in p.get("reads", ())]
        if row is None or not reads:
            continue
        tally.band("{} {}".format(a.cid, a.start), (min(reads) - a.start).days,
                   _num(row.get("lower")), _num(row.get("upper")), below="flag", above="flag")
    return tally


def _months(a: Account):
    by = defaultdict(set)
    for p in a.payments:
        by[p["payment_date"][:7]].add(p.get("payment_method"))
    return by


def ev_ppm_dd_concurrent(inv, book):
    tally = Tally("account")
    for a in book:
        both = sorted(m for m, ms in _months(a).items() if {PREPAYMENT, DIRECT_DEBIT} <= ms)
        tally.checked += 1
        run = best = 0
        prev = None
        for m in both:
            y, mo = map(int, m.split("-"))
            run = run + 1 if prev == (y, mo - 1) or prev == (y - 1, 12) and mo == 1 else 1
            best, prev = max(best, run), (y, mo)
        if best >= 2:
            tally.hit("breach", a.cid, best, 1, "consecutive months paying by both")
        elif best == 1:
            tally.hit("flag", a.cid, best, 0, "a month paying by both")
    return tally


def ev_payment_amount_sign(inv, book):
    """DD and prepayment payments are positive. A payment with no amount is a breach; a negative DD is
    reported as a flag, because the file names the export's encoding of a DD return as unknown."""
    tally = Tally("DD or prepayment payment")
    for a in book:
        for p in a.payments:
            if p.get("payment_method") not in (DIRECT_DEBIT, PREPAYMENT):
                continue
            amt = _num(p.get("payment_amount_gbp"))
            where = "{} {} {}".format(a.cid, p["payment_date"], p.get("payment_method"))
            tally.checked += 1
            if amt is None:
                tally.hit("breach", where, None, 0, "no amount")
            elif amt <= 0:
                tally.hit("flag" if p.get("payment_method") == DIRECT_DEBIT else "breach",
                          where, amt, 0, "not positive")
    return tally


def ev_dd_cadence(inv, book):
    tally = Tally("account-month with a DD payment")
    for a in book:
        counts = defaultdict(int)
        for p in a.payments:
            if p.get("payment_method") == DIRECT_DEBIT:
                counts[p["payment_date"][:7]] += 1
        for m, n in counts.items():
            tally.band("{} {}".format(a.cid, m), n, None, _num(inv.get("upper")), above="flag")
    return tally


def ev_dd_step_change(inv, book):
    tally = Tally("successive pair of positive DD collections")
    for a in book:
        dds = [p for p in a.payments if p.get("payment_method") == DIRECT_DEBIT
               and (_num(p.get("payment_amount_gbp")) or 0) > 0]
        for x, y in zip(dds, dds[1:]):
            ratio = _num(y["payment_amount_gbp"]) / _num(x["payment_amount_gbp"])
            tally.band("{} {}->{}".format(a.cid, x["payment_date"], y["payment_date"]), round(ratio, 3),
                       None, _num(inv.get("upper")), above="flag")
    return tally


def ev_fuel_identifier(inv, book):
    tally = Tally("bill period")
    for a in book:
        for p in a.periods:
            ok = ((p["commodity"] == "electricity" and p.get("mpan") and not p.get("mprn"))
                  or (p["commodity"] == "gas" and p.get("mprn") and not p.get("mpan")))
            tally.checked += 1
            if not ok:
                tally.hit("breach", "{} {}".format(a.cid, p["period_start"]), p["commodity"], None,
                          "wrong supply-point identifier")
    return tally


def ev_gas_single_register(inv, book):
    tally = Tally("gas meter (account x meter_serial)")
    for a in book:
        if a.fuel != "gas":
            continue
        regs = defaultdict(set)
        for p in a.periods:
            regs[p.get("meter_serial")] |= {r.get("register_id") for r in p.get("reads", ())}
        for serial, rs in regs.items():
            tally.band("{} {}".format(a.cid, serial), len(rs), 1, 1)
    return tally


def ev_cross_fuel_price_scale(inv, book, gas_rows=(), elec_rows=()):
    """SVT gas within the gas row's ceiling; SVT electricity above the electricity floor outside the
    EPG windows. The file gives this no severity, so it is read as a breach."""
    tally = Tally("SVT term x cap window it overlaps (both fuels)")
    for a in book:
        if not a.domestic:
            continue
        rows = gas_rows if a.fuel == "gas" else elec_rows
        for t in a.terms():
            if t.get("tariff_type") != "svt" or t["_last"] is None:
                continue
            for row in rows:
                if not (t["_from"] <= row["_to"] and t["_last"] >= row["_from"]):
                    continue
                rate = _num(t.get("unit_rate_p_per_kwh"))
                where = "{} {} {}".format(a.cid, a.fuel, row["from"])
                if a.fuel == "gas":
                    tally.band(where, rate, None, _num(row.get("upper")), tol_rel=0.005)
                elif not (EPG_FROM <= row["_from"] <= EPG_TO):
                    tally.band(where, rate, _num(row.get("lower")), None)
    return tally


def ev_periods_contiguous(inv, book):
    """Inclusive ends, as the export's own days_in_period shows; a gap or overlap is a breach.

    A period a later bill names as taken up by its catch-up (`held_periods_reconciled`) is billed,
    on that later bill, so it is one of the account's periods here."""
    tally = Tally("bill period (day count) and successive pair (contiguity)")
    for a in book:
        for p in a.periods:
            span = (_d(p["period_end"]) - _d(p["period_start"])).days + 1
            tally.band("{} {} days".format(a.cid, p["period_start"]), p.get("days_in_period"), span, span)
        spans = sorted(a.periods + [h for p in a.periods for h in p.get("held_periods_reconciled", ())],
                       key=lambda p: p["period_start"])
        for x, y in zip(spans, spans[1:]):
            step = (_d(y["period_start"]) - _d(x["period_end"])).days
            tally.band("{} {}->{}".format(a.cid, x["period_end"], y["period_start"]), step, 1, 1)
    return tally


def ev_back_billing(inv, book):
    """The file's PROXY, as a flag: (a) a period longer than 365 days; (b) a catch-up period, closed
    by an actual read more than 365 days after the previous one, charging more than its days at the
    account's prior actual-to-actual daily average (the export carries no adjustments to offset)."""
    tally = Tally("bill period of a domestic account from 2018-05-01")
    for a in book:
        if not a.domestic:
            continue
        last_actual, prior_kwh, prior_days = a.start, 0.0, 0
        for p in a.periods:
            ps, pe = _d(p["period_start"]), _d(p["period_end"])
            kwh = period_kwh(p) or 0.0
            actual = any(r.get("read_type") in ACTUAL_READ_TYPES for r in p.get("reads", ()))
            if pe >= date(2018, 5, 1):
                tally.checked += 1
                where = "{} {} {}".format(a.cid, a.fuel, p["period_start"])
                if int(p.get("days_in_period") or 0) > 365:
                    tally.hit("flag", where, p["days_in_period"], 365, "period over a year")
                elif actual and (pe - last_actual).days > 365 and prior_days:
                    expected = (pe - ps).days * prior_kwh / prior_days
                    if kwh > expected:
                        tally.hit("flag", where, round(kwh, 1), round(expected, 1),
                                  "catch-up after {} days unread".format((pe - last_actual).days))
            if actual:
                if (pe - last_actual).days <= 365:
                    prior_kwh += kwh
                    prior_days += (pe - ps).days + 1
                last_actual = pe
    return tally


def ev_consumption_non_negative(inv, book):
    tally = Tally("register-period")
    for a in book:
        for p in a.periods:
            by_reg = defaultdict(list)
            for r in p.get("reads", ()):
                by_reg[(r.get("register_id"), r.get("register_label"))].append(r)
            for (reg, label), reads in by_reg.items():
                if "export" in str(label).lower():
                    continue
                opening = [r for r in reads if r.get("read_type") == OPENING]
                closing = [r for r in reads if r.get("read_type") != OPENING]
                if opening and closing:
                    tally.band("{} {} reg {}".format(a.cid, p["period_start"], reg),
                               round(float(closing[-1]["read_kwh"]) - float(opening[0]["read_kwh"]), 3),
                               0.0, None)
    return tally


def ev_read_monotonic(inv, book):
    tally = Tally("successive pair of actual reads on one register")
    for a in book:
        reads = defaultdict(list)
        for p in a.periods:
            for r in p.get("reads", ()):
                if r.get("read_type") in ACTUAL_READ_TYPES:
                    reads[(p.get("meter_serial"), r.get("register_id"))].append(
                        (r["read_date"], float(r["read_kwh"]), r.get("read_type")))
        for key, rs in reads.items():
            rs = sorted(set(rs))
            for x, y in zip(rs, rs[1:]):
                customer = {x[2], y[2]} & {"C", "customer"}
                tally.band("{} {} {}->{}".format(a.cid, key[1], x[0], y[0]), y[1] - x[1], 0.0, None,
                           below="flag" if customer else "breach")
    return tally


#: The file's total/cumulative labels; every other label is a time band.
TOTAL_LABELS = {"total", "anytime", "single rate", "unrestricted"}


def _serial_runs(a):
    """Consecutive periods on one meter serial. A serial that returns after another is a new life."""
    run = []
    for p in a.periods:
        if run and p.get("meter_serial") != run[-1].get("meter_serial"):
            yield run
            run = []
        run.append(p)
    if run:
        yield run


def _term_changes_between(p1, p2) -> bool:
    """A term begins at the boundary: the two periods print different (type, start) sets."""
    def terms(p):
        return {(t.get("tariff_type"), t.get("tariff_effective_from"))
                for t in p.get("contracted_terms") or ()}
    return terms(p1) != terms(p2)


def _labels(p) -> dict:
    out = defaultdict(set)
    for r in list(p.get("registers") or ()) + list(p.get("reads") or ()):
        out[r.get("register_id")].add(r.get("register_label"))
    return out


def _band_kind(label) -> str:
    return "total" if str(label).strip().lower() in TOTAL_LABELS else "band"


def ev_register_id_one_label(inv, book):
    """(a) two labels on one id inside a period; (b) one id carrying a total label and a band label
    on one serial with its index carried straight across the relabel (one series, two identities);
    (c) a relabel between periods with no tariff change at the boundary, a flag."""
    tally = Tally("register id on one period, and each relabel between periods on one serial")
    for a in book:
        for run in _serial_runs(a):
            for p in run:
                for reg, labels in _labels(p).items():
                    tally.checked += 1
                    if len(labels) > 1:
                        tally.hit("breach", "{} {} reg {}".format(a.cid, p["period_start"], reg),
                                  sorted(map(str, labels)), 1, "two labels in one period")
            for p1, p2 in zip(run, run[1:]):
                l1, l2 = _labels(p1), _labels(p2)
                for reg in set(l1) & set(l2):
                    if l1[reg] == l2[reg] or len(l1[reg]) != 1 or len(l2[reg]) != 1:
                        continue
                    tally.checked += 1
                    (x,), (y,) = l1[reg], l2[reg]
                    closing = [r["read_kwh"] for r in p1.get("reads") or ()
                               if r.get("register_id") == reg and r.get("read_type") != OPENING]
                    opening = [r["read_kwh"] for r in p2.get("reads") or ()
                               if r.get("register_id") == reg and r.get("read_type") == OPENING]
                    where = "{} {} reg {} {}->{}".format(a.cid, p2["period_start"], reg, x, y)
                    if (_band_kind(x) != _band_kind(y) and closing and opening
                            and abs(float(opening[0]) - float(closing[-1])) < 1e-6):
                        tally.hit("breach", where, opening[0], closing[-1], "one series, two identities")
                    elif not _term_changes_between(p1, p2):
                        tally.hit("flag", where, y, x, "relabelled without visible reconfiguration")
    return tally


def ev_serial_register_count_stable(inv, book):
    """(b) the register set changes between read dates inside one period, a breach; (a) the count
    changes between periods on one serial with no tariff change at the boundary, a flag. A count
    change at a tariff change, or across a serial change, passes; the first is counted in `book`."""
    tally = Tally("period, and each successive pair of periods on one serial")
    at_term, serials = 0, set()
    for a in book:
        for run in _serial_runs(a):
            for p in run:
                tally.checked += 1
                by_date = defaultdict(set)
                for r in p.get("reads") or ():
                    by_date[r.get("read_date")].add(r.get("register_id"))
                if len({frozenset(s) for s in by_date.values()}) > 1:
                    tally.hit("breach", "{} {}".format(a.cid, p["period_start"]),
                              sorted(len(s) for s in by_date.values()), 1, "count changes in a period")
            for p1, p2 in zip(run, run[1:]):
                n1, n2 = len(_labels(p1)), len(_labels(p2))
                tally.checked += 1
                if n1 == n2:
                    continue
                if _term_changes_between(p1, p2):
                    at_term += 1
                    serials.add((a.cid, p1.get("meter_serial")))
                else:
                    tally.hit("flag", "{} {} {}".format(a.cid, p1.get("meter_serial"), p2["period_start"]),
                              n2, n1, "count changed without a tariff change")
    tally.book = {"count_changes_at_a_tariff_change": at_term, "serials": len(serials)}
    return tally


def ev_period_matches_reads(inv, book):
    """Billed volume against the advance of the period's own readings, summed over registers."""
    tally = Tally("period billed on reads")
    lo, hi = _num(inv.get("lower")), _num(inv.get("upper"))
    for a in book:
        for p in a.periods:
            if p.get("volume_basis") != "reads":
                continue
            by_reg = defaultdict(list)
            for r in p.get("reads", ()):
                by_reg[r.get("register_id")].append(r)
            pairs = [(o, c) for rs in by_reg.values()
                     for o in [next((r for r in rs if r.get("read_type") == OPENING), None)]
                     for c in [next((r for r in reversed(rs) if r.get("read_type") != OPENING), None)]
                     if o and c]
            billed = _num(p.get("consumption_kwh"))
            if not pairs or billed is None:
                tally.unbounded += 1
                continue
            advance = sum(float(c["read_kwh"]) - float(o["read_kwh"]) for o, c in pairs)
            tally.band("{} {}".format(a.cid, p["period_start"]), round(billed - advance, 3),
                       lo * len(pairs), hi * len(pairs))
    return tally


def _vat_segment(segment) -> str:
    return "domestic" if segment in DOMESTIC_SEGMENTS else "sme/non-domestic"


def _de_minimis_kwh_per_day(rule: str | None) -> float | None:
    """The file writes the business rule as prose: '0.05 if consumption_kwh/days_in_period <= 33 ...'."""
    import re
    m = re.search(r"<=\s*([0-9.]+)", rule or "")
    return float(m.group(1)) if m else None


def ev_vat_rate(inv, book):
    """The statutory rate for the period's segment, fuel and date; a business period by its de
    minimis. A period crossing a row boundary is a flag: the file says it may be split by date."""
    tally = Tally("period")
    rows = _rows(inv)
    for a in book:
        seg = _vat_segment(a.segment)
        for p in a.periods:
            where = "{} {}".format(a.cid, p["period_start"])
            mine = [r for r in rows if r["commodity"] == p.get("commodity") and r["segment"] == seg]
            first, last = _row_on(mine, _d(p["period_start"])), _row_on(mine, _d(p["period_end"]))
            if first is None:
                tally.unbounded += 1
                continue
            rate = _num(p.get("vat_rate"))
            if first is not last:
                tally.checked += 1
                tally.hit("flag", where, rate, None, "period crosses a VAT row boundary")
                continue
            lower, upper = _num(first.get("lower")), _num(first.get("upper"))
            limit = _de_minimis_kwh_per_day(first.get("rule"))
            if limit is not None:
                kwh, days = _num(p.get("consumption_kwh")), _num(p.get("days_in_period"))
                if kwh is None or not days:
                    tally.unbounded += 1
                    continue
                lower = upper = lower if kwh / days <= limit else upper
            tally.band(where, rate, lower, upper, tol_abs=_tol(inv, "absolute"))
    return tally


def ev_non_commodity_within_all_in(inv, book):
    """0 <= non-commodity GBP/MWh <= the all-in unit rate x 10.

    The ALL-IN rate is the contracted term's, not the period's printed `unit_rate_p_per_kwh`: the
    bill prints network and policy as its own line, so the printed rate is the energy line's alone
    (on 4ae8da9b0f, 2,647 periods breached against it and 0 against the terms). A two-rate term is
    graded at the flat rate its pair was struck from; the pass-through is flat per kWh here, so an
    off-peak rate below it is the flat-levy model's, not a pricing error.
    """
    tally = Tally("period")
    for a in book:
        for p in a.periods:
            rates = [_num(t.get("unit_rate_p_per_kwh")) for t in p.get("contracted_terms") or ()]
            rates = [r for r in rates or [_num(p.get("unit_rate_p_per_kwh"))] if r is not None]
            if not rates:
                tally.unbounded += 1
                continue
            tally.band("{} {}".format(a.cid, p["period_start"]),
                       _num(p.get("non_commodity_rate_gbp_per_mwh")), 0.0, min(rates) * 10)
    return tally


#: The export's spelling of a credit bill (`document_type`); a prepayment meter's is a statement.
CREDIT_BILL = "bill"
#: How long after a period its payment can land and still say how that period was paid.
PAYMENT_WINDOW = timedelta(days=60)


def ev_ppm_not_credit_billed(inv, book):
    tally = Tally("period on a prepayment account")
    for a in book:
        for p in a.periods:
            start, end = _d(p["period_start"]), _d(p["period_end"])
            if PREPAYMENT not in a.methods_between(start, end + PAYMENT_WINDOW):
                continue
            tally.checked += 1
            if p.get("document_type") is None:
                tally.hit("breach", "{} {}".format(a.cid, start), None, None, "missing")
            elif p["document_type"] == CREDIT_BILL:
                closing = [r.get("read_type") for r in p.get("reads", ()) if r.get("read_type") != OPENING]
                tally.hit("breach", "{} {} read {}".format(a.cid, start, closing[-1] if closing else "-"),
                          p["document_type"], None, "credit bill to a prepayment account")
    return tally


#: The export's reason for a government credit to the account (`raw_account_export.SCHEME_CREDIT`).
#: From Oct 2022 to Mar 2023 the only such scheme is the EBSS.
SCHEME_CREDIT = "scheme_credit"
#: The row's own figures: £66 in Oct and Nov 2022, £67 from Dec 2022 to Mar 2023 (£400 in all).
EBSS_CREDIT_GBP = ((date(2022, 10, 1), 66.0), (date(2022, 11, 1), 66.0), (date(2022, 12, 1), 67.0),
                   (date(2023, 1, 1), 67.0), (date(2023, 2, 1), 67.0), (date(2023, 3, 1), 67.0))
#: How late a month's credit can be dated and still be that month's: the row's "m end + 31 days".
EBSS_LAG = timedelta(days=31)


def _month_end(m: date) -> date:
    return date(m.year + (m.month == 12), m.month % 12 + 1, 1) - timedelta(days=1)


def ev_ebss_credit(inv, book):
    """Each month's credit once. The row's windows ([m start, m end + 31 days]) overlap, so summing
    every credit in each window would count a December-dated November credit twice. Each credit is
    taken, in date order, by the earliest supplied month whose window holds it and which is still
    owed; a credit no month is owed goes to the earliest window, where it reads as an overpayment.
    A gas account is owed nothing, so any credit on it breaches. A month paid by prepayment is not
    graded: the row's GAP (a traditional meter's voucher may expire unredeemed), and the export
    cannot tell a smart meter from a traditional one."""
    tally = Tally("account-month on supply, Oct 2022 to Mar 2023")
    for a in book:
        if not a.domestic or a.start is None:
            continue
        # Owed to whoever held the account at 00:00 on the 1st (guidance 5.4 and 5.8, as the row
        # now reads): a joiner's first part-month is owed nothing.
        months = [(m, 0.0 if a.fuel == "gas" else amt) for m, amt in EBSS_CREDIT_GBP
                  if a.start <= m <= a.end]
        if not months:
            continue
        got = {m: 0.0 for m, _ in months}
        credits = sorted((_d(x["adjustment_date"]), float(x["adjustment_amount_gbp"]))
                         for x in a.adjustments if x.get("adjustment_reason") == SCHEME_CREDIT
                         and x.get("adjustment_date") and x.get("adjustment_amount_gbp") is not None)
        for when, amount in credits:
            holds = [(m, owed) for m, owed in months if m <= when <= _month_end(m) + EBSS_LAG]
            if not holds:
                continue
            m = next((m for m, owed in holds if got[m] < owed - 1), holds[0][0])
            got[m] += amount
        for m, owed in months:
            where = "{} {} {}".format(a.cid, a.fuel, m.isoformat()[:7])
            if a.fuel != "gas" and PREPAYMENT in a.methods_between(m, _month_end(m) + PAYMENT_WINDOW):
                tally.unbounded += 1
                continue
            tally.band(where, round(got[m], 2), max(owed - 1, 0.0), owed + 1 if owed else 0.0)
    return tally


#: The MPAN core: 13 digits, a distributor ID first (10-23 a DNO, 24 upward an IDNO, with no
#: published upper bound), and a check digit last over the twelve before it, weighted by these
#: primes, sum mod 11 mod 10 (docs/domain_artefact_library/regulatory/mpan_core_structure_and_check_digit.md).
MPAN_CORE = re.compile(r"[1-9][0-9]{12}")
MPAN_WEIGHTS = (3, 5, 7, 13, 17, 19, 23, 29, 31, 37, 41, 43)


def mpan_check_digit(first_twelve: str) -> int:
    return sum(int(c) * w for c, w in zip(first_twelve, MPAN_WEIGHTS)) % 11 % 10


def ev_mpan_core_format(inv, book):
    tally = Tally("electricity supply point (account, MPAN core)")
    for a in book:
        cores = {}
        for p in a.periods:
            if p.get("commodity") == "electricity":
                cores.setdefault(str(p.get("mpan") or "").strip(), p["period_start"])
        for core, first in cores.items():
            tally.checked += 1
            where = "{} {} from {}".format(a.cid, core or "-", first)
            if not MPAN_CORE.fullmatch(core):
                tally.hit("breach", where, core, "13 digits, distributor 10 upward", "format")
            elif int(core[-1]) != mpan_check_digit(core[:12]):
                tally.hit("breach", where, core[-1], mpan_check_digit(core[:12]), "check digit")
    return tally


def _households(book) -> dict:
    """billing account -> its accounts, one per fuel. An export without the id is its own household."""
    out = defaultdict(list)
    for a in book:
        out[a.billing_account or a.cid].append(a)
    return out


def _journeys(accts) -> list[dict]:
    """The billing account's collections journeys, once: each fuel's record carries the same list."""
    return list(next((a.journeys for a in accts if a.journeys), ()))


def _bills(accts) -> list[tuple[date, date | None]]:
    """(due date, the day its collection succeeded or None) for every bill the household was sent."""
    return [(_d(b["due_date"]), _d(b["settled_date"]) if b.get("settled_date") else None)
            for a in accts for b in a.bills if b.get("due_date")]


def _events(journey) -> list[tuple[str, date]]:
    return sorted(((e.get("event"), _d(e["event_date"])) for e in journey.get("events") or ()
                   if e.get("event_date")), key=lambda x: x[1])


#: How the company's collections journey names its steps (`raw_account_export._journey_events`).
OPENING_EVENTS = {"missed_payment"}
REMINDER_EVENTS = {"reminder", "reminder_2"}
PLAN_EVENTS = {"repayment_plan_offer", "repayment_plan_reoffer", "arrangement_offered"}
WRITE_OFF_EVENT = "write_off"


def _opened(events):
    return next((d for k, d in events if k in OPENING_EVENTS), None)


def ev_renewal_notice(inv, book):
    """Each domestic fixed term owed an SLC 22C statement, against the company's statement for it.

    E is the term's `fixed_term_end` where the export has it (the contract's end, which a move or a
    switch can pre-empt), else its `tariff_effective_to`; both exclusive. A statement is owed when
    the account was supplied on E - 42, the window's last day: a term cut short before then is owed
    none (22C.4(a) runs to "the fixed term period [...] is due to end"). 22C binds Domestic
    Customers only, so a non-domestic account is not graded.

    The act graded is the statement (`renewal_notices`). A book whose run predates it carries no
    such key, and there the company's nearest renewal act is its retention offer, as before: an act
    more than 90 days before E or 31 after belongs to no term this row can see, so a term with none
    in that span grades missing. Where the book carries statements, the offer is not read: the text
    dates the statement, and does not date an offer of a new contract (22C.8(c); the tariffs page,
    2026-10-27)."""
    lo, hi = int(inv.get("lower", -49)), int(inv.get("upper", -42))
    tally = Tally("domestic fixed term owed a statement")
    for a in book:
        if a.end is None or not a.domestic:
            continue
        if a.notices is not None:
            acts = sorted(_d(r["notice_date"]) for r in a.notices if r.get("notice_date"))
        else:
            acts = sorted(_d(r["offer_date"]) for r in a.renewals
                          if r.get("offer_date") and r.get("commodity") in (None, a.fuel))
        for t in a.terms():
            if t.get("tariff_type") != "fixed" or not t.get("tariff_effective_to"):
                continue
            end = _d(t.get("fixed_term_end") or t["tariff_effective_to"])
            due = end + timedelta(days=hi)
            supplied_to = min(_d(t["tariff_effective_to"]), a.end + timedelta(days=1))
            if not (a.start <= due < supplied_to):
                continue
            near = [d for d in acts if end - timedelta(days=90) <= d <= end + timedelta(days=31)]
            offset = min(((d - end).days for d in near), key=abs) if near else None
            tally.band("{} {} term to {}".format(a.cid, a.fuel, end), offset, lo, hi)
    return tally


def ev_collections_ordered(inv, book):
    """Each journey once per household: it has an opening event, no step dated before it, and its
    first reminder no later than its first plan offer (the row's order)."""
    tally = Tally("collections journey")
    for ba, accts in _households(book).items():
        for i, j in enumerate(_journeys(accts)):
            ev = _events(j)
            if not ev:
                continue
            tally.checked += 1
            opened = _opened(ev)
            where = "{} journey {} from {}".format(ba, i, ev[0][1])
            first = {kinds: min((d for k, d in ev if k in kinds), default=None)
                     for kinds in (frozenset(REMINDER_EVENTS), frozenset(PLAN_EVENTS))}
            reminder, plan = first[frozenset(REMINDER_EVENTS)], first[frozenset(PLAN_EVENTS)]
            if opened is None:
                tally.hit("breach", where, ev[0][0], "a missed payment opens it", "no opening")
            elif ev[0][1] < opened:
                tally.hit("breach", where, ev[0][1], opened, "before opening")
            elif reminder and plan and plan < reminder:
                tally.hit("breach", where, plan, reminder, "plan before reminder")
    return tally


def ev_overdue_within_balance(inv, book):
    """The row's second leg only: an open debt stage has a bill unpaid past its due date. Read at
    each journey's opening: some bill fell due before that day and no collection for it had
    succeeded by then. A bill whose collection never succeeded stays unpaid to the end, so this
    leg is lenient after a household's first failure. The first leg (overdue within the balance)
    compares two sums the company worked out, which the export does not carry by design."""
    tally = Tally("collections journey opening")
    for ba, accts in _households(book).items():
        bills = _bills(accts)
        if not bills:
            continue
        for i, j in enumerate(_journeys(accts)):
            opened = _opened(_events(j))
            if opened is None:
                continue
            tally.checked += 1
            unpaid = any(due < opened and (settled is None or settled >= opened)
                         for due, settled in bills)
            if not unpaid:
                tally.hit("breach", "{} journey {} opened {}".format(ba, i, opened), opened,
                          "a bill unpaid past its due date", "nothing overdue")
    return tally


def _years_before(d: date, n: int) -> date:
    try:
        return d.replace(year=d.year - n)
    except ValueError:                                  # 29 Feb
        return d.replace(year=d.year - n, day=28)


#: Limitation Act 1980 s.5: six years from the cause of action (England and Wales; the export
#: carries no jurisdiction, so Scotland's five is not applied).
STATUTE_BAR_YEARS = 6


def ev_statute_barred_write_off(inv, book):
    """The row's necessary condition at each statute-barred write-off on W: some bill in it is
    barred, i.e. fell due by W - 6 years, was not collected by W, and no payment received on the
    household's account after its due date is later than W - 6 years (a part-payment restarts the
    clock). The per-bill form, that EVERY bill written off is barred, needs the write-off to name its
    bills; the company's record posts a sum, so that leg is the row's GAP."""
    tally = Tally("statute-barred write-off")
    for ba, accts in _households(book).items():
        bills = _bills(accts)
        paid = sorted(_d(p["payment_date"]) for a in accts for p in a.payments)
        for j in _journeys(accts):
            for e in j.get("events") or ():
                if (e.get("event") != WRITE_OFF_EVENT or not e.get("event_date")
                        or "limitation" not in str(e.get("event_rule") or "")):
                    continue
                when = _d(e["event_date"])
                bar = _years_before(when, STATUTE_BAR_YEARS)
                tally.checked += 1
                restarted = any(bar < d <= when for d in paid)
                barred = not restarted and any(due <= bar and (settled is None or settled > when)
                                               for due, settled in bills)
                if not barred:
                    tally.hit("breach", "{} write-off {}".format(ba, when), when,
                              "a bill due by {} and unpaid since".format(bar),
                              "payment after the bar" if restarted else "no bill old enough")
    return tally


#: invariant ID -> (evaluator, the export field it needs on some period or account, or None)
EVALUATORS = {
    "INV_UNIT_RATE_SVT_ELEC": (ev_unit_rate_svt_elec, None),
    "INV_UNIT_RATE_SVT_ELEC_PRE_CAP": (ev_unit_rate_svt_elec_pre_cap, None),
    "INV_UNIT_RATE_SVT_GAS": (ev_unit_rate_svt_gas, None),
    "INV_UNIT_RATE_SVT_GAS_PRE_CAP": (ev_unit_rate_svt_gas_pre_cap, None),
    "INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER": (ev_unit_rate_svt_elec_multi, None),
    "INV_UNIT_RATE_FIXED": (ev_unit_rate_fixed, None),
    "INV_STANDING_CHARGE_SVT_ELEC": (ev_standing_charge_svt_elec, None),
    "INV_STANDING_CHARGE_SVT_GAS": (ev_standing_charge_svt_gas, None),
    "INV_STANDING_CHARGE_FIXED": (ev_standing_charge_fixed, None),
    "INV_ANNUAL_USE_ELEC_ACCOUNT": (ev_annual_use_elec, None),
    "INV_ANNUAL_USE_GAS_ACCOUNT": (ev_annual_use_gas, None),
    "INV_ANNUAL_USE_BOOK_MEDIAN": (ev_annual_use_book_median, None),
    "INV_READ_DUTY_ANNUAL": (ev_read_duty_annual, None),
    "INV_SETTLEMENT_ACTUAL_SHARE_ELEC": (ev_settlement_actual_share, None),
    "INV_BILL_AT_LEAST_TWICE_YEARLY": (ev_bill_twice_yearly, None),
    "INV_OPENING_READ": (ev_opening_read, None),
    "INV_PAYMENT_PPM_AND_DD_NOT_CONCURRENT": (ev_ppm_dd_concurrent, None),
    "INV_PAYMENT_AMOUNT_SIGN": (ev_payment_amount_sign, None),
    "INV_DD_CADENCE": (ev_dd_cadence, None),
    "INV_DD_STEP_CHANGE": (ev_dd_step_change, None),
    "INV_FUEL_IDENTIFIER": (ev_fuel_identifier, None),
    "INV_GAS_SINGLE_REGISTER": (ev_gas_single_register, None),
    "INV_CROSS_FUEL_PRICE_SCALE": (ev_cross_fuel_price_scale, None),
    "INV_PERIODS_CONTIGUOUS": (ev_periods_contiguous, None),
    "INV_BACK_BILLING_12M": (ev_back_billing, None),
    "INV_PERIOD_CONSUMPTION_NON_NEGATIVE": (ev_consumption_non_negative, None),
    "INV_READ_MONOTONIC": (ev_read_monotonic, None),
    "INV_PERIOD_MATCHES_READS": (ev_period_matches_reads, "consumption_kwh"),
    "INV_VAT_RATE": (ev_vat_rate, "vat_rate"),
    "INV_NON_COMMODITY_WITHIN_ALL_IN": (ev_non_commodity_within_all_in,
                                        "non_commodity_rate_gbp_per_mwh"),
    "INV_PPM_NOT_CREDIT_BILLED": (ev_ppm_not_credit_billed, "document_type"),
    "INV_REGISTER_ID_ONE_LABEL": (ev_register_id_one_label, None),
    "INV_SERIAL_REGISTER_COUNT_STABLE": (ev_serial_register_count_stable, None),
    "INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23": (ev_ebss_credit, None),
    "INV_MPAN_CORE_FORMAT": (ev_mpan_core_format, "mpan"),
    "INV_RENEWAL_NOTICE_42_TO_49_DAYS": (ev_renewal_notice, "bills"),
    "INV_COLLECTIONS_EVENTS_ORDERED": (ev_collections_ordered, "collections_journeys"),
    "INV_OVERDUE_WITHIN_BALANCE": (ev_overdue_within_balance, "bills"),
    "INV_STATUTE_BARRED_WRITE_OFF_AGE": (ev_statute_barred_write_off, "bills"),
}


def run(invariants: list[dict], raw_book: dict[str, dict]) -> list[dict]:
    book = [Account(cid, raw) for cid, raw in raw_book.items()]
    by_id = {i["id"]: i for i in invariants}
    fields = {k for a in raw_book.values() for p in a.get("periods", ()) for k, v in p.items()
              if v is not None}
    fields |= {k for a in raw_book.values() for k, v in (a.get("events") or {}).items() if v}
    extra = {
        "INV_UNIT_RATE_FIXED": {"pre_cap_rows": _rows(by_id.get("INV_UNIT_RATE_SVT_ELEC_PRE_CAP", {}))},
        "INV_CROSS_FUEL_PRICE_SCALE": {"gas_rows": _rows(by_id.get("INV_UNIT_RATE_SVT_GAS", {})),
                                       "elec_rows": _rows(by_id.get("INV_UNIT_RATE_SVT_ELEC", {}))},
    }
    out = []
    for inv in invariants:
        row = {"id": inv["id"], "family": inv.get("family"), "source": inv.get("source")}
        evaluator, needs = EVALUATORS.get(inv["id"], (None, None))
        if not inv.get("checkable", True):
            row.update(status="UNCHECKABLE", reason=inv.get("gap") or "the file marks it uncheckable")
        elif needs and needs not in fields:
            row.update(status="NOT_IN_EXPORT",
                       reason="needs `{}`, which no period of this export carries".format(needs))
        elif evaluator is None:
            row.update(status="NO_EVALUATOR", reason="no evaluator for {}".format(inv["id"]))
        else:
            t = evaluator(inv, book, **extra.get(inv["id"], {}))
            status = ("BREACHED" if t.breaches else "FLAGGED" if t.flags
                      else "CLEAN" if t.checked else "UNREACHED")
            row.update(status=status, unit=t.unit, checked=t.checked, breached=len(t.breaches),
                       flagged=len(t.flags), unbounded=t.unbounded,
                       breach_examples=t.breaches[:5], flag_examples=t.flags[:5],
                       book=getattr(t, "book", None))
        out.append(row)
    return out


def _share(r: dict, key: str) -> str:
    return "{} ({:.1%})".format(r[key], r[key] / r["checked"]) if r["checked"] else str(r[key])


def render(results: list[dict], accounts: int) -> str:
    lines = ["Domain invariants over {} accounts".format(accounts), "",
             "| invariant | status | breached | flagged | checked | unit |", "|---|---|---|---|---|---|"]
    for r in results:
        if "checked" in r:
            lines.append("| {} | {} | {} | {} | {} | {} |".format(
                r["id"], r["status"], _share(r, "breached"), _share(r, "flagged"), r["checked"], r["unit"]))
        else:
            lines.append("| {} | {} | | | | {} |".format(r["id"], r["status"], r["reason"][:140]))
    return "\n".join(lines)


def load_exceptions(path: Path = EXCEPTIONS_PATH) -> dict:
    import yaml
    return yaml.safe_load(path.read_text()) or {}


def gate(results: list[dict], register: dict) -> dict:
    """Which breaches no exception covers. `refuse` is the verdict whatever `enforce` says, so the
    report-only surface prints the refusal the enforced gate would have made.

    An exception lifts one invariant's breaches when it carries every `EXCEPTION_FIELDS` entry and,
    if it names `max_breached`, the count is within it: a ceiling, so an excepted defect that grows
    comes back as a refusal rather than hiding behind the exception filed for its smaller self."""
    valid, invalid = {}, []
    for e in register.get("exceptions") or ():
        missing = [f for f in EXCEPTION_FIELDS if not e.get(f)]
        if missing:
            invalid.append({"invariant": e.get("invariant"), "missing": missing})
        else:
            valid[e["invariant"]] = e
    unexcepted, excepted = [], []
    for r in results:
        n = r.get("breached") or 0
        if not n:
            continue
        e = valid.get(r["id"])
        cap = e.get("max_breached") if e else None
        if e and (cap is None or n <= cap):
            excepted.append({"id": r["id"], "breached": n, "retired_by": e["retired_by"]})
        else:
            why = ("no exception" if e is None else
                   "{} breaches exceed the exception's max_breached {}".format(n, cap))
            unexcepted.append({"id": r["id"], "breached": n, "why": why})
    enforce = register.get("enforce") is True
    refusal = "; ".join("{} {} ({})".format(u["id"], u["breached"], u["why"]) for u in unexcepted)
    return {"enforce": enforce, "refuse": bool(unexcepted), "unexcepted": unexcepted,
            "excepted": excepted, "invalid_exceptions": invalid,
            "report_only_because": None if enforce else register.get("report_only_because"),
            "refusal": refusal or None}


def render_verdict(verdict: dict) -> str:
    n = sum(u["breached"] for u in verdict["unexcepted"])
    mode = (("ENFORCED: the publish is refused" if verdict["refuse"] else
             "ENFORCED: nothing unexcepted, so the publish stands") if verdict["enforce"] else
            "REPORT-ONLY: the publish is not refused ({})".format(
                verdict.get("report_only_because") or "the register does not say enforce: true"))
    lines = ["**{} unexcepted breach(es) across {} invariant(s); {} excepted. {}.**".format(
        n, len(verdict["unexcepted"]), len(verdict["excepted"]), mode)]
    lines += ["- {} {}: {}".format(u["id"], u["breached"], u["why"]) for u in verdict["unexcepted"]]
    lines += ["- {} {}: excepted until {}".format(x["id"], x["breached"], x["retired_by"])
              for x in verdict["excepted"]]
    lines += ["- an exception for {} lifts nothing: it lacks {}".format(
        i["invariant"], ", ".join(i["missing"])) for i in verdict["invalid_exceptions"]]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--raw", type=Path, help="a JSON bundle: customer_id -> raw export")
    src.add_argument("--ledger", type=Path, help="a billing ledger; the raw export is produced from it")
    ap.add_argument("--events", type=Path, help="with --raw: customer_id -> the account's events")
    ap.add_argument("--invariants", type=Path, default=INVARIANTS_PATH)
    ap.add_argument("--json", type=Path, help="also write the full result, examples included")
    ap.add_argument("--strict", action="store_true", help="return 1 on any BREACH")
    ap.add_argument("--exceptions", type=Path, default=EXCEPTIONS_PATH)
    args = ap.parse_args(argv)
    raw = load_book(args.raw, args.ledger, args.events)
    results = run(load_invariants(args.invariants), raw)
    verdict = gate(results, load_exceptions(args.exceptions))
    print(render(results, len(raw)))
    print()
    print(render_verdict(verdict))
    if args.json:
        args.json.write_text(json.dumps(results, indent=1, default=str) + "\n")
    return 1 if args.strict and verdict["refuse"] else 0


if __name__ == "__main__":
    sys.exit(main())
