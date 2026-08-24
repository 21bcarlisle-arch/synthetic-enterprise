"""Double-entry ledger for the company layer — F1.

Translates saas.ledger event records into DR/CR journal entries with
account codes. Trial balance, P&L, and balance sheet emerge from this
journal rather than from event-type pattern matching.

Account code ranges:
  1xxx  Assets         (normal balance: debit)
  2xxx  Liabilities    (normal balance: credit)
  3xxx  Equity         (normal balance: credit)
  4xxx  Revenue        (normal balance: credit)
  5xxx  Cost of Sales  (normal balance: debit)
  6xxx  Operating Exp  (normal balance: debit)
  7xxx  Taxation       (normal balance: debit)
"""

import math
from typing import Any

ACCOUNTS: dict[str, dict[str, str]] = {
    "1001": {"name": "Cash and Treasury",                   "type": "asset"},
    "1100": {"name": "Trade Receivables",                   "type": "asset"},
    "2100": {"name": "VAT Payable",                         "type": "liability"},
    "2200": {"name": "Customer Credit Balances Held",       "type": "liability"},
    "3001": {"name": "Opening Capital / Treasury",          "type": "equity"},
    "3900": {"name": "Retained Earnings",                   "type": "equity"},
    "4001": {"name": "Revenue — Energy Supply",             "type": "income"},
    "5001": {"name": "Wholesale Cost",                      "type": "expense"},
    "5100": {"name": "Network and Levy Pass-through",       "type": "expense"},
    "5200": {"name": "Capital Charge (VaR-based)",          "type": "expense"},
    "6001": {"name": "Bad Debt Expense",                    "type": "expense"},
    "6100": {"name": "Cost to Serve",                       "type": "expense"},
    "6200": {"name": "Fixed Overheads",                     "type": "expense"},
    "6300": {"name": "Customer Acquisition and Retention",  "type": "expense"},
    "7001": {"name": "Corporation Tax Expense",             "type": "expense"},
}

# UK Corporation Tax, real rates (docs/design/E1_CORPORATION_TAX_FINDING.md). Flat 19% for
# all financial years up to and including FY2022 (year ending before 1 April 2023). From
# FY2023: small profits rate 19% (profits <= GBP 50,000), main rate 25% (profits >
# GBP 250,000), with marginal relief between the two thresholds using HMRC's own Standard
# Fraction (3/200) -- CT = profit * 0.25 - (upper_limit - profit) * 3/200, which is exactly
# continuous with 19% at GBP 50,000 and 25% at GBP 250,000 by construction.
_CT_SMALL_PROFITS_RATE = 0.19
_CT_MAIN_RATE = 0.25
_CT_SMALL_PROFITS_LIMIT_GBP = 50_000.0
_CT_MAIN_RATE_THRESHOLD_GBP = 250_000.0
_CT_MARGINAL_RELIEF_STANDARD_FRACTION = 3 / 200
_CT_TWO_TIER_RATES_FROM_YEAR = 2023  # FY2023 (year ending on/after 1 April 2023) onward


def uk_corporation_tax_gbp(profit_before_tax_gbp: float, year: int) -> float:
    """UK Corporation Tax due on `profit_before_tax_gbp` for calendar `year`. Returns 0.0 for
    a loss (no negative tax / no loss-relief modelling here -- a real loss-carry-back/forward
    mechanism is a separate, unbuilt feature, not silently assumed). No associated-companies
    adjustment to the GBP 50k/250k thresholds (this simulation has one company)."""
    if profit_before_tax_gbp <= 0:
        return 0.0
    if year < _CT_TWO_TIER_RATES_FROM_YEAR:
        return profit_before_tax_gbp * _CT_SMALL_PROFITS_RATE
    if profit_before_tax_gbp <= _CT_SMALL_PROFITS_LIMIT_GBP:
        return profit_before_tax_gbp * _CT_SMALL_PROFITS_RATE
    if profit_before_tax_gbp >= _CT_MAIN_RATE_THRESHOLD_GBP:
        return profit_before_tax_gbp * _CT_MAIN_RATE
    marginal_relief = (
        (_CT_MAIN_RATE_THRESHOLD_GBP - profit_before_tax_gbp)
        * _CT_MARGINAL_RELIEF_STANDARD_FRACTION
    )
    return profit_before_tax_gbp * _CT_MAIN_RATE - marginal_relief


def _entry(
    event_id: str,
    timestamp: str,
    debit: str,
    credit: str,
    amount: float,
    description: str,
    source: str,
) -> dict[str, Any]:
    return {
        "entry_id": event_id,
        "timestamp": timestamp,
        "debit_account": debit,
        "credit_account": credit,
        "amount_gbp": amount,
        "description": description,
        "source_event_type": source,
    }


def _money_in_is_the_normal_direction(debit_account: str) -> bool:
    """True when this entry's NORMAL direction is money coming IN.

    Derived from the chart, not tabulated: every entry below either debits an asset
    (1001 cash / 1100 receivables), which is money arriving, or credits one, which is
    money leaving. So the debit account's type IS the direction, and a new event type
    cannot forget to register itself in a lookup that would then silently mis-post it.
    """
    return ACCOUNTS.get(debit_account, {}).get("type") == "asset"


def to_journal_entry(event: dict[str, Any]) -> dict[str, Any] | None:
    """Convert one ledger event to a double-entry journal record.

    Returns None for unrecognised event types (forward-compatible).

    A NEGATIVE-VALUED EVENT IS POSTED THE OTHER WAY ROUND (2026-08-24). Every event
    maker in `saas/ledger.py` signs `amount_gbp` the same way — cash out is negative,
    cash in is positive — and the branches below name the account pair for the NORMAL
    sign. The magnitude alone used to be taken (`abs`), so an event whose real value
    was negative was booked as its own opposite: a half-hour of NEGATIVE wholesale
    price (a real and increasingly common UK occurrence — the supplier is paid to
    take the energy) was posted as a wholesale COST of the same size, and a credit
    bill was posted as revenue. The error is twice the credit, every time.

    Measured on a real end-2019 run before this was fixed: 2018's journal wholesale
    cost was overstated, and folding the same settlement book to daily rows — which
    nets a negative half-hour against the day's positive ones BEFORE `abs` sees it —
    moved published cash/equity by £14.08 while every signed figure (portfolio gross,
    net, treasury) stayed identical to the penny. That £14.08 was the last
    unexplained movement blocking `simulation/settlement_daily.py`; keeping the sign
    removes it by construction, because a sum of signed amounts does not care what
    order it was added in and `abs` of a sum does.
    """
    entry = _entry_in_the_normal_direction(event)
    if entry is None:
        return None
    signed = float(event.get("amount_gbp") or 0.0)
    if signed and (signed > 0) != _money_in_is_the_normal_direction(entry["debit_account"]):
        entry["debit_account"], entry["credit_account"] = (
            entry["credit_account"], entry["debit_account"],
        )
    return entry


def _entry_in_the_normal_direction(event: dict[str, Any]) -> dict[str, Any] | None:
    """The account pair this event type takes when its amount carries its usual sign.

    Magnitude only — the direction is decided by the caller above, which is the one
    place that reads the sign.
    """
    et = event["event_type"]
    eid = event.get("transaction_id", f"unknown:{et}")
    ts = event.get("timestamp", "")
    cid = event.get("customer_id", event.get("billing_account", ""))
    amount = abs(event["amount_gbp"])

    if et == "billing_event":
        return _entry(eid, ts, "1100", "4001", amount,
                      f"Customer billed: {cid}", et)

    if et == "vat_remittance_event":
        # VAT was collected inside billing revenue; remittance to HMRC reduces revenue.
        return _entry(eid, ts, "4001", "1001", amount,
                      f"VAT remitted to HMRC: {cid}", et)

    if et == "non_commodity_cost_event":
        return _entry(eid, ts, "5100", "1001", amount,
                      f"Network/levy pass-through remitted: {cid}", et)

    if et == "settlement_event":
        return _entry(eid, ts, "5001", "1001", amount,
                      f"Wholesale settlement: {cid}", et)

    if et == "capital_charge_event":
        return _entry(eid, ts, "5200", "1001", amount,
                      f"Capital charge (VaR): {cid}", et)

    if et == "payment_received_event":
        return _entry(eid, ts, "1001", "1100", amount,
                      f"Payment received: {cid}", et)

    if et == "bad_debt_event":
        return _entry(eid, ts, "6001", "1100", amount,
                      f"Bad debt written off: {cid}", et)

    if et in ("acquisition_spend_event", "retention_cost_event"):
        return _entry(eid, ts, "6300", "1001", amount,
                      f"Acquisition/retention spend: {cid}", et)

    if et == "fixed_cost_event":
        return _entry(eid, ts, "6200", "1001", amount,
                      f"Fixed overheads: {event.get('month', ts)}", et)

    if et == "cost_to_serve_event":
        return _entry(eid, ts, "6100", "1001", amount,
                      f"Cost to serve: {event.get('month', ts)}", et)

    return None


def build_journal(
    events: list[dict[str, Any]],
    opening_treasury: float = 0.0,
) -> list[dict[str, Any]]:
    """Build the full double-entry journal from ledger events.

    Prepends an opening entry for starting treasury capital if non-zero.
    Unrecognised event types are silently skipped.
    """
    entries: list[dict[str, Any]] = []

    if opening_treasury:
        entries.append(_entry(
            "opening-treasury",
            "0000-00-00",
            "1001", "3001",
            opening_treasury,
            "Opening treasury / share capital",
            "opening_entry",
        ))

    for ev in events:
        je = to_journal_entry(ev)
        if je is not None:
            entries.append(je)

    return entries


def account_balances(journal: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Return {account_code: {dr, cr, net}} for every account touched."""
    balances: dict[str, dict[str, float]] = {}

    for je in journal:
        for side, acct in (("dr", je["debit_account"]), ("cr", je["credit_account"])):
            if acct not in balances:
                balances[acct] = {"dr": 0.0, "cr": 0.0, "net": 0.0}
            balances[acct][side] += je["amount_gbp"]

    for acct, b in balances.items():
        acct_type = ACCOUNTS.get(acct, {}).get("type", "")
        if acct_type in ("asset", "expense"):
            b["net"] = b["dr"] - b["cr"]  # normal debit balance
        else:
            b["net"] = b["cr"] - b["dr"]  # normal credit balance

    return balances


def entry_violations(entry: dict[str, Any], entry_ref: str) -> list[str]:
    """Integrity breaches in ONE journal entry, or [] if it is well-formed.

    A well-formed entry names two DISTINCT accounts, both known to ACCOUNTS, and
    carries a finite, non-negative amount. The unknown-account rule matters
    because `account_balances` resolves an unknown code to the empty type and so
    silently books it as credit-normal -- a wrong sign with no signal.
    """
    v: list[str] = []
    dr = entry.get("debit_account")
    cr = entry.get("credit_account")

    for side, acct in (("debit", dr), ("credit", cr)):
        if acct is None:
            v.append(f"{entry_ref}: missing {side}_account")
        elif acct not in ACCOUNTS:
            v.append(f"{entry_ref}: unknown {side} account {acct!r}")
    if dr is not None and dr == cr:
        v.append(f"{entry_ref}: debit and credit are the same account {dr!r}")

    if "amount_gbp" not in entry:
        v.append(f"{entry_ref}: missing amount_gbp")
    else:
        amt = entry["amount_gbp"]
        if isinstance(amt, bool) or not isinstance(amt, (int, float)):
            v.append(f"{entry_ref}: non-numeric amount_gbp {amt!r}")
        elif not math.isfinite(amt):
            v.append(f"{entry_ref}: non-finite amount_gbp {amt!r}")
        elif amt < 0:
            v.append(f"{entry_ref}: negative amount_gbp {amt!r}")
    return v


def journal_violations(journal: list[dict[str, Any]]) -> list[str]:
    """Every integrity breach in `journal`, in entry order."""
    out: list[str] = []
    for i, je in enumerate(journal):
        out.extend(entry_violations(je, str(je.get("entry_id", f"index:{i}"))))
    return out


def trial_balance(journal: list[dict[str, Any]]) -> dict[str, Any]:
    """Check the journal's integrity and total it.

    An entry here carries a SINGLE `amount_gbp` posted to one debit and one
    credit account, so the debit and credit totals are equal BY CONSTRUCTION.
    Summing the two and comparing them -- which this function used to do, on its
    own admission ("always equal by construction") -- is a tautology: it cannot
    fail on any journal, corrupt or not, because the checked value is derived
    from the same source it checks (R15 independence).

    So `balanced` reports the integrity that CAN fail on a record of this shape:
    every entry well-formed per `entry_violations`, AND the totals tying. The
    arithmetic tie is kept because it still catches a future data model that
    records the two sides separately; it is no longer the only thing asserted.
    `violations` names each breach, so a caller sees WHY a journal is unbalanced
    rather than only that it is. Malformed entries are excluded from the totals
    so that one bad row cannot take the whole balance down with a KeyError.
    """
    violations = journal_violations(journal)
    wellformed = [
        je for i, je in enumerate(journal)
        if not entry_violations(je, str(je.get("entry_id", f"index:{i}")))
    ]
    balances = account_balances(wellformed)
    dr_check = sum(b["dr"] for b in balances.values())
    cr_check = sum(b["cr"] for b in balances.values())
    return {
        "total_debit_gbp": dr_check,
        "total_credit_gbp": cr_check,
        "balanced": not violations and abs(dr_check - cr_check) < 0.01,
        "discrepancy_gbp": dr_check - cr_check,
        "violations": violations,
    }


def income_statement(journal: list[dict[str, Any]], year: int | None = None) -> dict[str, float]:
    """P&L that emerges from account balances — not event-type pattern matching.

    `year`: optional calendar year, used ONLY to compute the NEW profit_before_tax_gbp/
    corporation_tax_gbp/profit_for_year_gbp triplet (docs/design/E1_CORPORATION_TAX_FINDING.md).
    When None (the default, and every pre-existing call site unless updated), those three
    fields are None -- NOT silently computed with a guessed year -- and `net_margin_gbp`
    (pre-tax operating profit, unchanged in meaning) remains the only profit figure, exactly as
    before this change. This is a strictly additive change: no existing field's meaning or
    value changes, and MARGIN_REALISM's own EBIT%-anchored comparisons (which are correctly
    pre-tax) continue to read `net_margin_gbp` exactly as they always have.
    """
    b = account_balances(journal)

    def net(code: str) -> float:
        return b.get(code, {}).get("net", 0.0)

    revenue = net("4001")
    wholesale = net("5001")
    non_commodity = net("5100")
    capital = net("5200")
    gross = revenue - wholesale - non_commodity
    bad_debt = net("6001")
    cost_to_serve = net("6100")
    fixed = net("6200")
    acq = net("6300")
    opex = bad_debt + cost_to_serve + fixed + acq
    net_profit = gross - capital - opex

    corporation_tax_gbp = uk_corporation_tax_gbp(net_profit, year) if year is not None else None
    profit_for_year_gbp = (
        net_profit - corporation_tax_gbp if corporation_tax_gbp is not None else None
    )

    return {
        "revenue_gbp": revenue,
        "wholesale_cost_gbp": wholesale,
        "non_commodity_cost_gbp": non_commodity,
        "gross_margin_gbp": gross,
        "capital_cost_gbp": capital,
        "bad_debt_gbp": bad_debt,
        "cost_to_serve_gbp": cost_to_serve,
        "fixed_cost_gbp": fixed,
        "acquisition_spend_gbp": acq,
        "total_opex_gbp": opex,
        "net_margin_gbp": net_profit,
        "profit_before_tax_gbp": net_profit if year is not None else None,
        "corporation_tax_gbp": corporation_tax_gbp,
        "profit_for_year_gbp": profit_for_year_gbp,
    }


def balance_sheet(journal: list[dict[str, Any]]) -> dict[str, Any]:
    """Balance sheet that emerges from account balances.

    Assets = Liabilities + Equity is the reconciliation test.
    Equity includes opening capital plus the current period's net profit.

    A credit balance on Trade Receivables is presented as a liability
    (``customer_accounts_in_credit_gbp``), never as a negative asset -- see the
    comment on the split below for what that is and what it deliberately excludes.
    """
    b = account_balances(journal)

    def net(code: str) -> float:
        return b.get(code, {}).get("net", 0.0)

    cash = net("1001")
    # A CREDIT BALANCE ON TRADE RECEIVABLES IS NOT A NEGATIVE ASSET (2026-08-24).
    # 1100 nets debit-normal, so once the journal keeps its signs a book whose customers
    # have collectively paid ahead of what they were billed nets NEGATIVE -- observed on a
    # real end-2019 run, where receivables close at -£53.47. That is money the company owes
    # its customers, and presenting it as an asset of minus fifty-three pounds both
    # understates assets and hides a liability. Split it: the debit balance stays the
    # receivable, the credit balance is reported as customer accounts in credit and joins
    # total liabilities. No journal entry is posted and no account balance moves -- this is
    # a presentation rule, so `balance_sheet_with_held_credit`'s augmented journal composes
    # unchanged. Assets and liabilities both rise by the same amount, so the equation holds.
    #
    # DELIBERATELY NOT APPLIED TO CASH (1001): a negative cash balance is a real overdraft
    # and its sign is what every consumer of `cash_gbp` (treasury.cash_flow_by_year, the
    # site's cash series) needs to see. Clamping it would report an overdrawn company as
    # holding zero cash. No overdraft facility exists in this model, so there is no observed
    # instance; if one is ever built, it is a bank liability and belongs in the 2xxx chart
    # as a posted entry rather than in this presentation split.
    receivables_net = net("1100")
    receivables = max(receivables_net, 0.0)
    customer_accounts_in_credit = max(-receivables_net, 0.0)
    total_assets = cash + receivables

    vat_payable = net("2100")
    customer_credit_held = net("2200")
    # Sum EVERY liability-type account, not just VAT Payable, so a new liability
    # (DD3's customer-credit-held, account 2200) is reflected in the equation
    # rather than silently omitted. Identical to the old `vat_payable` value for
    # any journal that has never posted to another 2xxx account (the case for
    # every pre-DD3 journal), so no existing published figure changes.
    total_liabilities = sum(
        net(code) for code, info in ACCOUNTS.items() if info["type"] == "liability"
    ) + customer_accounts_in_credit

    opening_capital = net("3001")
    retained = net("3900")
    pnl = income_statement(journal)
    current_profit = pnl["net_margin_gbp"]
    total_equity = opening_capital + retained + current_profit

    equation_holds = abs(total_assets - (total_liabilities + total_equity)) < 0.01

    return {
        "cash_gbp": cash,
        "trade_receivables_gbp": receivables,
        "total_assets_gbp": total_assets,
        "vat_payable_gbp": vat_payable,
        "customer_credit_held_gbp": customer_credit_held,
        # The credit half of 1100, reported separately rather than netted against the
        # debit half. NOT the same figure as `customer_credit_held_gbp`: that one is
        # DD3's positive-balances-only aggregate from the direct-debit balance book,
        # booked by an actual journal entry; this one is whatever 1100 itself owes,
        # derived from billing and payment. They describe overlapping economics from
        # two different books, and a supplier reporting both would say so.
        "customer_accounts_in_credit_gbp": customer_accounts_in_credit,
        "total_liabilities_gbp": total_liabilities,
        "opening_capital_gbp": opening_capital,
        "retained_earnings_gbp": retained,
        "current_period_profit_gbp": current_profit,
        "total_equity_gbp": total_equity,
        "total_liabilities_and_equity_gbp": total_liabilities + total_equity,
        "equation_holds": equation_holds,
    }


# ---------------------------------------------------------------------------
# DD3 (atom DD_seasonal_cashflow_physics) -- book held customer credit as a
# LIABILITY in the double-entry chart.
#
# Under a level (fixed) direct debit a household pays the same amount every
# month while consuming seasonally, so it builds a credit through summer and
# draws it down through winter (instrumented as a portfolio series by DD2,
# simulation/dd_balance_book.py). The positive balance the supplier holds is
# money owed back -- a LIABILITY, not profit. Before this, the ONLY liability
# in the chart was VAT Payable (2100); held customer credit sat implicitly
# inside treasury cash and therefore inflated equity, so the balance sheet
# looked healthier than it was. DD3 makes the reclassification explicit: the
# held credit is moved out of retained earnings and into a customer-credit-held
# liability (2200), leaving assets untouched and the accounting equation intact
# but revealing the "cash-rich but balance-sheet-insolvent" tell.
#
# Wall-clean and dependency-free: these functions take the held-credit figure
# as a plain float (the caller sources it from DD2's company-observable balance
# book), so this company-side module imports no SIM code. Additive: the naive
# balance_sheet() is untouched; balance_sheet_with_held_credit() is a NEW view
# that DD-H (the belief-vs-truth solvency gap organ) and DD5 (the SITE surface)
# consume. Level moves stay director-reserved (R16).
# ---------------------------------------------------------------------------

import math as _math


def _validated_held_credit_gbp(held_credit_gbp: float) -> float:
    """Validate a held-credit figure before it is booked as a liability.

    Fail-CLOSED (R15 FAIL-OPEN guard): a non-finite or negative held credit is a
    DEFECT, never silently coerced to £0. Held credit is a positive-balances-only
    aggregate by construction (``simulation/dd_balance_book.py`` sums only the
    customers whose balance is > 0), so a negative value means the caller passed
    the wrong figure -- e.g. the NET portfolio balance, which can go negative in a
    hard winter draw-down -- and booking that as a £0 liability would hide the
    error and understate what is owed back. Reject it.
    """
    hc = float(held_credit_gbp)
    if not _math.isfinite(hc):
        raise ValueError(f"held_credit_gbp must be finite, got {held_credit_gbp!r}")
    if hc < 0:
        raise ValueError(
            "held_credit_gbp must be >= 0 (held credit is a positive-balances-only "
            f"liability); got {hc}. A negative net balance is not held credit."
        )
    return hc


def held_credit_journal_entries(
    held_credit_gbp: float,
    timestamp: str = "9999-12-31",
    event_id: str = "dd3-held-credit",
) -> list[dict[str, Any]]:
    """The DD3 journal entry that books held customer credit as a liability.

    A single balanced reclassification: DR Retained Earnings (3900), CR Customer
    Credit Balances Held (2200). The held credit already sits inside treasury
    cash (an asset the company genuinely holds), so no asset moves; what changes
    is that this slice of cash is recognised as owed-back rather than earned --
    equity falls by the held credit and liabilities rise by the same amount, so
    the accounting equation still holds.

    Returns ``[]`` for zero held credit (nothing owed back, legitimately nothing
    to book). Rejects a non-finite or negative figure (see
    ``_validated_held_credit_gbp``).
    """
    hc = _validated_held_credit_gbp(held_credit_gbp)
    if hc == 0.0:
        return []
    return [_entry(
        event_id, timestamp, "3900", "2200", hc,
        "Held customer credit reclassified to liability "
        "(level-DD seasonal overpayment owed back to customers)",
        "dd3_held_credit_reclassification",
    )]


def balance_sheet_with_held_credit(
    journal: list[dict[str, Any]],
    held_credit_gbp: float,
    timestamp: str = "9999-12-31",
) -> dict[str, Any]:
    """The insolvency-aware balance sheet: the naive balance sheet with held
    customer credit reclassified from equity to a liability (DD3).

    Every field of the ordinary ``balance_sheet`` is present (computed from the
    journal AUGMENTED with the DD3 reclassification entry, so ``total_liabilities``
    now includes the held credit and ``total_equity`` is net of it), plus:

    * ``customer_credit_held_gbp`` -- the held credit booked as a liability;
    * ``naive_total_equity_gbp`` -- equity BEFORE the reclassification (what the
      un-adjusted books show);
    * ``true_total_equity_gbp`` -- equity AFTER (== naive - held credit);
    * ``cash_rich_but_insolvent`` -- True iff the naive books show positive equity
      while the held-credit-adjusted books show negative equity: the exact tell
      this atom exists to make visible (a supplier sitting on a pile of cash that
      is entirely other people's overpayments).

    Assets are identical to the naive balance sheet; only the liability/equity
    split moves, so ``equation_holds`` stays True.
    """
    hc = _validated_held_credit_gbp(held_credit_gbp)
    naive = balance_sheet(journal)
    augmented = list(journal) + held_credit_journal_entries(hc, timestamp)
    bs = balance_sheet(augmented)
    naive_equity = naive["total_equity_gbp"]
    true_equity = bs["total_equity_gbp"]
    bs["customer_credit_held_gbp"] = round(hc, 2)
    bs["naive_total_equity_gbp"] = round(naive_equity, 2)
    bs["true_total_equity_gbp"] = round(true_equity, 2)
    bs["cash_rich_but_insolvent"] = (naive_equity > 0.0) and (true_equity < 0.0)
    return bs
