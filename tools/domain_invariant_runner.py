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
  * an ACCOUNT is one `customer_id`. The export carries one fuel per account and no household
    link, so the file's "same customer_id also holds gas" heating-class proxy is never true and
    the all-domestic band is used instead.
  * the read duty also counts the run from the last actual read to the end of supply: the duty
    runs for as long as the account is supplied.

## NOT A GATE YET

The ruling says a breach blocks the publish or is a named, dated exception. Wiring waits until one
book's breaches are each fixed or named (the delivery-lane direction of 26 Oct), so this prints and
returns 0; `--strict` returns 1 on any BREACH for whoever wires it.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
INVARIANTS_PATH = PROJECT / "docs" / "design" / "DOMAIN_INVARIANTS.yaml"

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


def load_book(raw_path: Path | None = None, ledger_path: Path | None = None) -> dict[str, dict]:
    """customer_id -> raw export. From a bundle the export wrote, or produced from a ledger here."""
    if raw_path is not None:
        return json.loads(raw_path.read_text())
    from company.billing.raw_account_export import derived_leaks, raw_account
    ledger = json.loads(ledger_path.read_text())
    out = {}
    for cid, rec in (ledger.get("customers") or {}).items():
        r = raw_account(cid, rec)
        leaks = derived_leaks(r)
        if leaks:
            raise ValueError("the raw export for {} carries derived fields: {}".format(cid, leaks[:3]))
        out[cid] = r
    return out


# ── the book, read as accounts ──────────────────────────────────────────────────────────────

class Account:
    def __init__(self, cid: str, raw: dict):
        self.cid, self.segment = cid, raw.get("segment")
        self.periods = sorted(raw.get("periods", ()), key=lambda p: p["period_start"])
        self.fuel = self.periods[0]["commodity"] if self.periods else None
        self.payments = sorted((p for p in raw.get("payments", ()) if p.get("payment_date")),
                               key=lambda p: p["payment_date"])
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
            for t in p.get("contracted_terms") or ():
                key = (t["tariff_effective_from"], t.get("tariff_effective_to"), t.get("tariff_type"))
                if key not in seen:
                    end = (_d(t["tariff_effective_to"]) - timedelta(days=1)
                           if t.get("tariff_effective_to") else self.end)
                    seen[key] = dict(t, _from=_d(t["tariff_effective_from"]), _last=end)
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
        if meter == "single" and len(a.registers) != 1 or meter == "multi" and len(a.registers) < 2:
            continue
        for t in a.terms():
            if t.get("tariff_type") != "svt" or t["_last"] is None:
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
    """Upper only where every payment in the window is DD; the file names the rest UNCHECKABLE."""
    tally = Tally("SVT term x cap window it overlaps (gas, DD-only windows)")
    tol = _tol(inv, "upper_relative")
    for a, t, row in _svt_term_windows(inv, book, "gas", None):
        methods = a.methods_between(row["_from"], row["_to"]) - {None}
        rate = _num(t.get("unit_rate_p_per_kwh"))
        where = "{} {} from {}".format(a.cid, row["from"], t["tariff_effective_from"])
        if methods != {DIRECT_DEBIT}:
            tally.band(where, rate, 0.0, None, tol_abs=-1e-12)   # still positive; no ceiling
            continue
        tally.band(where, rate, 0.0, _num(row.get("upper")), tol_rel=tol, tol_abs=-1e-12)
    return tally


def ev_unit_rate_svt_gas_pre_cap(inv, book):
    tally = Tally("SVT term x pre-cap span it overlaps (gas)")
    for a, t, row in _svt_term_windows(inv, book, "gas", None):
        tally.band("{} from {}".format(a.cid, t["tariff_effective_from"]),
                   _num(t.get("unit_rate_p_per_kwh")), 0.0, None, tol_abs=-1e-12)
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


def ev_standing_charge_svt_elec(inv, book):
    tally = Tally("SVT bill period (electricity)")
    tol = _tol(inv, "upper_absolute_gbp_per_day")
    for a, p, row in _sc_periods(inv, book, "electricity", "svt"):
        if row is None:
            continue
        upper = _upper_for_methods(row, a.methods_between(row["_from"], row["_to"]))
        tally.band("{} {}".format(a.cid, p["period_start"]), _num(p.get("standing_charge_gbp_per_day")),
                   _num(row.get("lower")), upper, tol_abs=tol)
    return tally


def ev_standing_charge_svt_gas(inv, book):
    tally = Tally("SVT bill period (gas; ceiling in DD-only windows)")
    tol = _tol(inv, "upper_absolute_gbp_per_day")
    for a, p, row in _sc_periods(inv, book, "gas", "svt"):
        if row is None:
            continue
        dd_only = a.methods_between(row["_from"], row["_to"]) - {None} == {DIRECT_DEBIT}
        tally.band("{} {}".format(a.cid, p["period_start"]), _num(p.get("standing_charge_gbp_per_day")),
                   _num(row.get("lower")), _num(row.get("upper")) if dd_only else None, tol_abs=tol)
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


def _annual_use(inv, book, fuel, hard_flag_upper=None):
    tally = Tally("complete calendar account-year ({})".format(fuel))
    band = next((b for b in inv.get("flag_bands") or ()
                 if str(b.get("class", "")).startswith("all")), {})
    years = list(account_years(book, fuel))
    above_p99 = 0
    for a, year, kwh in years:
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
    if years and band.get("flag_upper_p99") is not None:
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
    """Inclusive ends, as the export's own days_in_period shows; a gap or overlap is a breach."""
    tally = Tally("bill period (day count) and successive pair (contiguity)")
    for a in book:
        for p in a.periods:
            span = (_d(p["period_end"]) - _d(p["period_start"])).days + 1
            tally.band("{} {} days".format(a.cid, p["period_start"]), p.get("days_in_period"), span, span)
        for x, y in zip(a.periods, a.periods[1:]):
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


#: invariant ID -> (evaluator, the export field it needs on some period, or None)
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
    "INV_PERIOD_MATCHES_READS": (None, "consumption_kwh"),
    "INV_VAT_RATE": (None, "vat_rate"),
    "INV_NON_COMMODITY_WITHIN_ALL_IN": (None, "non_commodity_rate_gbp_per_mwh"),
}


def run(invariants: list[dict], raw_book: dict[str, dict]) -> list[dict]:
    book = [Account(cid, raw) for cid, raw in raw_book.items()]
    by_id = {i["id"]: i for i in invariants}
    fields = {k for a in raw_book.values() for p in a.get("periods", ()) for k, v in p.items()
              if v is not None}
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--raw", type=Path, help="a JSON bundle: customer_id -> raw export")
    src.add_argument("--ledger", type=Path, help="a billing ledger; the raw export is produced from it")
    ap.add_argument("--invariants", type=Path, default=INVARIANTS_PATH)
    ap.add_argument("--json", type=Path, help="also write the full result, examples included")
    ap.add_argument("--strict", action="store_true", help="return 1 on any BREACH")
    args = ap.parse_args(argv)
    raw = load_book(args.raw, args.ledger)
    results = run(load_invariants(args.invariants), raw)
    print(render(results, len(raw)))
    if args.json:
        args.json.write_text(json.dumps(results, indent=1, default=str) + "\n")
    return 1 if args.strict and any(r.get("breached") for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
