"""Management accounts from double-entry journal -- Phase 64 / FI1."""

from company.finance.double_entry import balance_sheet, build_journal, income_statement


def build_monthly_accounts(events, opening_treasury=0.0):
    journal = build_journal(events, opening_treasury)
    by_month = {}
    for je in journal:
        if je["timestamp"] == "0000-00-00":
            continue
        ym = je["timestamp"][:7]
        by_month.setdefault(ym, []).append(je)
    result = {}
    for ym in sorted(by_month):
        year, month = ym[:4], ym[5:7]
        result.setdefault(year, {})[month] = income_statement(by_month[ym])
    return result


def annual_management_pack(events, opening_treasury=0.0):
    journal = build_journal(events, opening_treasury)
    opening_entries = [je for je in journal if je["timestamp"] == "0000-00-00"]
    by_year = {}
    for je in journal:
        if je["timestamp"] == "0000-00-00":
            continue
        year = je["timestamp"][:4]
        by_year.setdefault(year, []).append(je)
    result = {}
    cumulative = list(opening_entries)
    for year in sorted(by_year):
        year_entries = by_year[year]
        cumulative = cumulative + year_entries
        result[year] = {
            "income_statement": income_statement(year_entries),
            "balance_sheet": balance_sheet(cumulative),
        }
    return result


def cross_check(journal_net, ledger_net, tolerance=0.05):
    abs_diff = abs(journal_net - ledger_net)
    if abs(ledger_net) < 1.0:
        passed = abs_diff < 1.0
        variance_pct = 0.0
    else:
        variance_pct = abs_diff / abs(ledger_net) * 100.0
        passed = variance_pct <= tolerance * 100.0
    return {
        "pass": passed,
        "journal_net_gbp": journal_net,
        "ledger_net_gbp": ledger_net,
        "abs_diff_gbp": abs_diff,
        "variance_pct": round(variance_pct, 3),
        "tolerance_pct": tolerance * 100.0,
    }
