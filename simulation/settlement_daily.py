"""Fold a term's half-hourly settlement into DAILY rows, and keep per-period truth where a
published figure actually depends on it.

STATUS: WIRED (2026-08-24). On a real end-2019 run the retained book goes from 1,909,710 records
to 45,341 (42x), peak RSS from 3,003 MB to 486 MB (84% less) and elapsed from 102.5s to 70.4s.

MEASURED WITH THE FOLD AS THE ONLY VARIABLE — one interpreter, one commit, one minute, with
`fold_to_days` swapped between two full `run_phase4c` + `extract_report_data` passes. That
discipline is not pedantry: every earlier comparison in this work was cross-tree, and two of them
lied in opposite directions. One made a real defect look like £14 of noise; the next made the
same fold look like a £5,347 movement. Both were other lanes' commits landing between the runs.
Never diff a report against a baseline built from a different tree.

The result, same-tree: **the largest financial difference across the whole extract is £0.12**, on
a collections total, and almost every other is under £0.03. All of it traces to one thing —
`bill_generator.generate_bill` rounds the SUM of consumption to 2dp, and the float sum of 1,440
per-period values is not bit-identical to the sum of 30 daily ones, so the penny occasionally
lands the other way.

ONE NON-FINANCIAL DIFFERENCE, AND IT IS NOT A ROUNDING ERROR: the run acquired 2 customers
instead of 1. `growth_mandate` computes `wins_capital_allows = int(committed // all_in_per_win)`,
an integer floor over a money figure, so a two-pence difference in committed capital can flip it
by one and that flips an acquisition. The fold is exact on sums; the RUN is chaotic at that
threshold. "Byte-identical" was therefore never an achievable standard for the whole run, and
claiming it would have been the more dangerous error — what is achievable, and what is measured
here, is exactness on every sum with the sensitivity named.

The two movements that kept this dormant are resolved:

  1. `worst_period` — EXPLAINED, and the old figure is itself suspect: `apply_emergent_bad_debt`
     lands each customer-year's whole bad-debt correction on that year's LAST record, so the
     published "worst half-hour" is wherever that lump fell, not the worst settled half-hour.
     The register folds pre-revision values and so names a different (milder) period.
  2. the ledger-derived cash/equity movement — DIAGNOSED AND REPAIRED 2026-08-24 by the lane
     that built `tools/running_total_order.py`, and it was never the fold's defect. Per-segment gross
     margin, portfolio gross, net margin, capital, bad debt and treasury were all identical to
     the penny because every one of them is a sum of SIGNED record values, and a sum does not
     care what order it was added in. The journal was not: `company/finance/double_entry.
     to_journal_entry` took `abs(amount_gbp)` and chose the account pair by event TYPE, so a
     negatively-priced half-hour (the supplier is PAID to take the energy) was posted as a
     wholesale COST of the same size — and `abs(x + y) != abs(x) + abs(y)`, so netting a day
     before the journal saw it changed the published figure. This run carries 6 such half-hours
     in 2018 (£5.48 of credit, overstating the journal by £10.95) and 2 in 2019 (£1.52, £3.04):
     £13.99, plus pennies from item 3 below, is the £14.08.

     With the sign kept, the same end-2019 comparison moves NO figure by more than £0.02.

  3. what is LEFT is a rounding tie, and it is worth knowing about. `simulation/meter_reads.py`
     estimates an unread month as `round(mean(trailing actual reads), 2)`. Those reads are
     monthly kWh totals — sums of ~1,440 floats — and re-associating the sum moves them by up
     to 5.8e-11 kWh. Physically nothing, and enough to decide a `round(..., 2)` when the mean
     lands on an exact half-penny tie (measured: 428.82500000000005 -> 428.83 per-period versus
     exactly 428.825 -> 428.82 per-day, a difference of 5.7e-14 deciding a penny). 19 of 158
     estimates flipped, worth £0.03 on £3.05M of billing. Not repaired here: the flip is a
     tie-break, both answers are defensible, and the exact-tie value is arguably the truer one.

An unexplained movement in a published balance-sheet figure is not landable (R14) — which is why
the fold sat here with its tests running and its caller absent. What replaced the mystery is a
DIRECTOR RULING that outranks the memory saving (2026-08-24 console, verbatim): "GB settlement is
half-hourly and that is not an implementation detail, it is the market. So the half-hourly spine
stays half-hourly. Aggregate in the reporting and ledger layers if that's where the memory goes,
but the settlement and metering record keeps its grain." The one-line wiring described above
folds the RETAINED book, which is the reporting/ledger side of that line rather than the spine
(the 48-period settlement loop is untouched), and GATE 13 refuses a new half-hourly read
downstream of the fold. The signed journal is the ledger-layer half of the same instruction: an
aggregation there is now safe BY CONSTRUCTION, because the journal is a sum of signed amounts.

WHY, AND WHY THE DAY RATHER THAN THE MONTH (director, 2026-08-24: "make the run incremental …
using the projections store rather than accumulating … then 200 residential isn't a budget
question at all").

`run_phase2b` kept every half-hour of the whole run — 17,520 dicts per customer-year at ~1,410
bytes each, so ~15 GB at the engine's 600-customer-year ceiling and **~49 GB** at 200 residential
accounts over the ten-year window. More than the host has. The instruction was to aggregate, and
the question was at what grain.

THE MONTH IS THE OBVIOUS ANSWER AND IT IS WRONG BY ONE STEP. Bills are monthly and
`build_monthly_bills` partitions per customer per calendar month, so a monthly row looks
sufficient — until `saas/bill_generator.py::consumption_coefficient_of_variation`, which prices
every bill's clarity score off the **population standard deviation of DAILY totals** within the
month. A monthly row cannot produce that number, and a bill's clarity score is published. The
day is the coarsest grain that leaves every bill byte-identical, and it is still a 48x cut:
~15 GB becomes ~310 MB, and 200 accounts becomes ~1 GB.

WHAT A DAY CANNOT CARRY, AND WHAT IS DONE ABOUT IT. Four published figures are computed from the
half-hour itself. Each becomes a REGISTER folded during the run, on the same per-period records,
rather than a rescan of a list afterwards:

  * `worst_period` — the single worst half-hour per year by net margin, its own report section.
    Register: one record per year, replaced when a worse one arrives.
  * `tou_stats` — peak vs off-peak kWh and revenue for half-hourly customers, split by
    `is_peak_period(date, period)`. Register: four running sums per customer. The band comes
    from `simulation/tou_periods.py`, the WORLD's copy, because the world's band is what priced
    the revenue being split. `company/market/tou_periods.py` holds the company's own copy and
    the annual report used that one; the two are independent implementations of a published
    Elexon convention (REGULATION_COMMONS_DOCTRINE — the law is public, each lane reads it for
    itself) and they agree today, which
    `tests/simulation/test_settlement_daily.py::test_the_two_peak_band_definitions_still_agree`
    pins so a future divergence surfaces as a red test rather than as a moved figure.
  * the treasury path — `_drawdown_events` walks the balance after every half-hour, and an
    intra-day dip is invisible in daily closes. Register: the drawdown fold itself, over the
    whole book as ONE path (not per year — see `TreasuryDrawdown`, which says why the year is a
    tag on each point rather than a bucket the points are sorted into).
  * Triad exposure — wants the actual periods, for I&C customers in the Triad season only.
    Register: those records, kept whole. Bounded by construction: Nov–Feb, I&C only.

Everything else downstream is a sum, a min/max date, or a chronological walk, and all three
survive the fold exactly.

WHAT THE DAILY ROW IS. The same keys, summed over the day, with three exceptions stated here so
nothing has to infer them:
  * `settlement_period` is the day's LAST period, so `max(key=(date, period))` still selects the
    day's closing row and `sorted(key=(date, period))` is still chronological.
  * `treasury_cash_balance_gbp` is the balance after the day's LAST period — the day's close,
    not a sum. Summing a running balance would be meaningless.
  * the rate fields (`hedge_price_gbp_per_mwh`, `hedge_fraction`,
    `standing_charge_gbp_per_day`) are carried through unchanged: they are fixed for a term and
    a term begins on a date boundary, so they are constant within any day this folds.
  * `unit_rate_gbp_per_mwh` is the ONE rate that is NOT term-constant, and assuming it was cost
    a real figure. Under a ToU tariff the peak and off-peak halves of the same day carry
    different unit rates, so carrying the day's first record's rate reported every customer's
    peak rate as its off-peak one: `tariff_max_gbp_per_mwh` for C_IC1 in 2018 read £226.14 and
    became £102.36. The day therefore carries the rate it opened on AND
    `unit_rate_min_gbp_per_mwh` / `unit_rate_max_gbp_per_mwh`, which compose — the min of the
    daily minima is the min over every period — so the report's per-year range is exact again.
"""
from __future__ import annotations

#: Fields that are a RATE or a FACT about the term rather than a quantity accrued in the period.
#: Carried from the day's first record instead of summed.
CARRIED_FIELDS = (
    "customer_id", "settlement_date", "commodity", "data_regime",
    "unit_rate_gbp_per_mwh", "hedge_price_gbp_per_mwh", "hedge_fraction",
    "standing_charge_gbp_per_day", "term_start", "tariff_type", "segment",
)

#: Maintained by hand in the fold rather than summed or carried — see the module docstring on
#: `unit_rate_gbp_per_mwh`.
_RATE_EXTREMA = ("unit_rate_min_gbp_per_mwh", "unit_rate_max_gbp_per_mwh")

#: Taken from the day's LAST record: a running balance's daily value is its close, not its sum.
CLOSING_FIELDS = ("treasury_cash_balance_gbp", "settlement_period")

#: Never summed and never carried — it identifies one half-hour and a day is not one.
_DROPPED: tuple[str, ...] = ()


def fold_to_days(records):
    """One term's half-hourly records -> one row per (customer, commodity, settlement_date).

    Order-preserving: the days come back in the order their first record appeared, which for a
    term is chronological, so a caller that extends a list with the result gets the same
    ordering it had before.

    A record with no `settlement_date` is passed through untouched rather than dropped — this
    function's job is to make the book smaller, not to decide what counts as settled.
    """
    out: list[dict] = []
    index: dict[tuple, dict] = {}
    for rec in records:
        day = rec.get("settlement_date")
        if not day:
            out.append(rec)
            continue
        key = (rec.get("customer_id"), rec.get("commodity"), day)
        rate = rec.get("unit_rate_gbp_per_mwh")
        row = index.get(key)
        if row is None:
            row = dict(rec)
            row["settlement_periods_folded"] = 1
            if rate is not None:
                row["unit_rate_min_gbp_per_mwh"] = rate
                row["unit_rate_max_gbp_per_mwh"] = rate
            index[key] = row
            out.append(row)
            continue
        row["settlement_periods_folded"] += 1
        if rate is not None:
            lo = row.get("unit_rate_min_gbp_per_mwh")
            hi = row.get("unit_rate_max_gbp_per_mwh")
            row["unit_rate_min_gbp_per_mwh"] = rate if lo is None else min(lo, rate)
            row["unit_rate_max_gbp_per_mwh"] = rate if hi is None else max(hi, rate)
        for field, value in rec.items():
            if field in CARRIED_FIELDS or field in _RATE_EXTREMA:
                continue
            if field in CLOSING_FIELDS:
                row[field] = value
                continue
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                prior = row.get(field)
                row[field] = value if not isinstance(prior, (int, float)) else prior + value
            else:
                # Non-numeric and not a declared carry: keep the day's LAST, which is what a
                # reader of a daily row expects of a flag that changed mid-day.
                row[field] = value
    return out


class PeriodRegisters:
    """The four things a daily row cannot answer, folded from the same per-period records.

    Deliberately NOT a general-purpose store. Each register exists because one named published
    figure needs the half-hour, and each is bounded: a record per year, four sums per customer,
    a drawdown fold per year, and the Triad season for I&C only.
    """

    def __init__(self, is_peak_period=None, triad_months=(11, 12, 1, 2),
                 triad_segments=("I&C",)) -> None:
        self._is_peak = is_peak_period
        self._triad_months = set(triad_months)
        self._triad_segments = set(triad_segments)
        self.worst_period_by_year: dict[str, dict] = {}
        self.tou_by_customer: dict[str, dict] = {}
        self.triad_records: list[dict] = []
        #: cid -> segment, so the Triad carve-out can be applied without re-reading the book.
        self._segment_of: dict[str, str] = {}

    def add(self, records, segment_of=None) -> None:
        for rec in records:
            day = rec.get("settlement_date")
            if not day:
                continue
            cid = rec.get("customer_id")
            year = day[:4]

            net = rec.get("net_margin_gbp")
            if net is not None:
                worst = self.worst_period_by_year.get(year)
                if worst is None or net < worst["net_margin_gbp"]:
                    self.worst_period_by_year[year] = {
                        "settlement_date": day,
                        "settlement_period": rec.get("settlement_period"),
                        "customer_id": cid,
                        "net_margin_gbp": net,
                    }

            if self._is_peak is not None and rec.get("commodity") == "electricity":
                period = rec.get("settlement_period")
                kwh = rec.get("consumption_kwh") or 0.0
                revenue = rec.get("revenue_gbp") or 0.0
                bucket = self.tou_by_customer.setdefault(
                    cid, {"total_kwh": 0.0, "peak_kwh": 0.0,
                          "peak_revenue_gbp": 0.0, "offpeak_revenue_gbp": 0.0})
                bucket["total_kwh"] += kwh
                if period is not None and self._is_peak(day, period):
                    bucket["peak_kwh"] += kwh
                    bucket["peak_revenue_gbp"] += revenue
                else:
                    bucket["offpeak_revenue_gbp"] += revenue

            segment = (segment_of or {}).get(cid) or self._segment_of.get(cid)
            if segment in self._triad_segments and int(day[5:7]) in self._triad_months:
                self.triad_records.append(rec)


class TreasuryDrawdown:
    """The treasury path's drawdown, folded ONCE over the whole book in accumulation order.

    `annual_report._drawdown_events` walks the balance after EVERY settlement period, so a dip
    that opens and closes inside one day is visible to it and invisible in daily closes. Rather
    than keep 10.5M balances to rediscover that, the peak-and-trough walk happens here, once,
    as the balances are produced.

    The register is a PATH, not a set of per-year paths — `points()` returns every significant
    point in the order the balance took, each tagged with the year of the record that produced
    it. A significant point is every new running peak and every new low beneath the last
    recorded point; a balance between the two moves no drawdown and is dropped, which makes the
    register O(turning points) rather than O(periods) and lossless for a (peak, trough) walk.

    WHY THE YEAR IS A TAG AND NOT A PARTITION (2026-08-24, the residual of
    `docs/staging/WORKER_FINDING_THE_TREASURY_DRAWDOWN_FIGURE_IS_AN_ARTEFACT_OF_SORTING_A_BALANCE_THAT_WAS_NEVER_A_SERIES_2026-08-24.md`).
    This register used to keep a separate peak and a separate point list per year, keyed on
    `settlement_date[:4]`. `treasury_cash_balance_gbp` is a PORTFOLIO running total stamped
    record-by-record during the term loop, so a year's records are a SUBSEQUENCE of it, sampled
    at the moments the loop happened to emit records dated in that year — and between two
    consecutive samples the balance travels through other customers' whole terms. Bucketing it
    is therefore the same defect as re-sorting it, just 2,000x gentler: one stretch of the term
    loop that emitted both 2022- and 2023-dated records showed the SAME swing in both buckets,
    and the report published it as two events with peaks four pence apart.

    The year of a completed drawdown is the year of the record at its TROUGH — the year the
    treasury was actually at its lowest — which the consumer derives from the tags. Every
    published event is therefore an event the portfolio balance genuinely had.
    """

    def __init__(self) -> None:
        self._points: list[list] = []
        self._peak: float | None = None

    def add(self, records) -> None:
        for rec in records:
            balance = rec.get("treasury_cash_balance_gbp")
            day = rec.get("settlement_date")
            if balance is None or not day:
                continue
            year = day[:4]
            if self._peak is None:
                self._points.append([balance, year])
                self._peak = balance
                continue
            if balance > self._peak:
                self._points.append([balance, year])
                self._peak = balance
            elif balance < self._points[-1][0]:
                # A new low since the last recorded point: it can only deepen a drawdown, so it
                # is a turning point. A balance between the last point and the peak changes no
                # drawdown and is dropped.
                self._points.append([balance, year])

    def points(self) -> list[list]:
        """The whole register, for the run to hand to the report. A plain list of `[balance,
        year]` pairs so it survives the JSON round-trip every persisted run output goes
        through (a tuple comes back from JSON as a list, so it is a list here already)."""
        return [list(point) for point in self._points]
