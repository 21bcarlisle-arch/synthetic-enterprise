#!/usr/bin/env python3
"""
REUSE: saas/reporting/compliance_scorecard_population.py
CLASS: CUSTOM
INDEX: searched "compliance scorecard", "populate", "SLC domain", "RAG". Two rows and neither
       is this. `company/regulatory/compliance_scorecard.py` owns the ComplianceScorecard TYPE
       and its RAG rules -- it is IMPORTED here, whole, and nothing about it is reimplemented.
       `company/regulatory/compliance_dashboard.py` renders a scorecard that already exists.
       What had no home at all is the POPULATION step: turning a run's report data into a
       scorecard. It has lived inside the annual report's renderer since it was written, which
       is exactly why the renderer acquired a production importer.
       This is an EXTRACTION, not new code: the function below is moved verbatim.

THE POPULATION STEP, MOVED OUT OF THE RENDERER.

Director instruction, 2026-08-19, narrowing an earlier one on the strength of the measurement:
"Fix the one real production violation and make it impossible for new importers to appear."

THE VIOLATION. `tools/generate_dashboard_data.py::extract_regulatory` imported
`populate_compliance_scorecard` FROM `saas.reporting.annual_report`. A report is a RENDERING;
nothing should read it. The function's own docstring admitted the coupling in writing --
"Shared by _section_compliance_scorecard's markdown table and tools/generate_dashboard_data.py's
Regulatory tab" -- so the renderer had become the home of a computation two surfaces needed, and
the dashboard could only reach it by importing a 9,838-line report module.

WHY EXTRACTION AND NOT DUPLICATION: the two surfaces must agree. A markdown table and a
Regulatory tab that disagree about whether an obligation is GREEN is a worse defect than the
import was, and copying the 146 lines is how that happens six months from now.

MOVED VERBATIM, deliberately. Not one line of the logic is changed in this commit, so the diff
is a MOVE and any behaviour change would have to be a bug rather than a judgement call. The
function was already self-contained: its only free names were the three classes it imports
itself (ComplianceScorecard, ComplianceDomain, RAGStatus).

WHAT IS NOT FIXED HERE, and is now recorded debt rather than drift: 73 test files reach into the
report's PRIVATE `_section_*` functions across 257 distinct sections. That is a rebuild, not a
decoupling, and the director has ruled the cost out of proportion to the harm for now. See
docs/design/ANNUAL_REPORT_IMPORT_DEBT.md for the size, so it is chosen deliberately later
instead of drifted into.
"""
from __future__ import annotations


def populate_compliance_scorecard(data: dict):
    """Populate a ComplianceScorecard from simulation signals already present in the
    report data, one check per SLC domain per year. Returns None when there is no
    yearly data. Shared by _section_compliance_scorecard's markdown table and
    tools/generate_dashboard_data.py's Regulatory tab (SUPPLIER_TAB_OVERHAUL.md)."""
    from company.regulatory.compliance_scorecard import (
        ComplianceScorecard,
        ComplianceDomain,
        RAGStatus,
    )
    import datetime as dt

    years = data.get("years", {})
    ma = data.get("management_accounts") or {}
    fra_series = {r["year"]: r for r in data.get("fra_ratio_series", [])}

    if not years:
        return None

    scorecard = ComplianceScorecard()

    for yr in sorted(years.keys()):
        yd = years[yr]
        yr_int = int(yr)
        as_of = dt.date(yr_int, 12, 31)

        revenue = yd.get("revenue_gbp", 0.0)
        bad_debt = yd.get("bad_debt_gbp", 0.0)
        bad_debt_pct = bad_debt / revenue * 100 if revenue > 0 else 0.0
        avg_clarity = yd.get("avg_clarity", 1.0)
        fra_data = fra_series.get(yr_int, {})
        fra_ratio = fra_data.get("fra_ratio", 10.0) if fra_data else 10.0

        # GOVERNANCE (SLC 0-9): GREEN unless licence health BREACH
        yr_ma = ma.get(yr, {})
        net_assets = yr_ma.get("balance_sheet", {}).get("total_equity_gbp", 1.0)
        gov_rag = RAGStatus.AMBER if net_assets < 0 else RAGStatus.GREEN
        scorecard.record_check(ComplianceDomain.GOVERNANCE, as_of, gov_rag,
                                notes="Net assets positive" if net_assets >= 0 else "Balance sheet insolvency risk")

        # BILLING & METERING (SLC 10-14): bill clarity score
        if avg_clarity >= 0.80:
            bill_rag = RAGStatus.GREEN
        elif avg_clarity >= 0.60:
            bill_rag = RAGStatus.AMBER
        else:
            bill_rag = RAGStatus.RED
        scorecard.record_check(ComplianceDomain.BILLING_METERING, as_of, bill_rag,
                                metric_value=avg_clarity, threshold=0.80,
                                notes=f"Bill clarity score {avg_clarity:.2f}")

        # PAYMENT & DEBT (SLC 15-19): bad debt ratio
        if bad_debt_pct < 1.0:
            pay_rag = RAGStatus.GREEN
        elif bad_debt_pct < 3.0:
            pay_rag = RAGStatus.AMBER
        else:
            pay_rag = RAGStatus.RED
        scorecard.record_check(ComplianceDomain.PAYMENT_DEBT, as_of, pay_rag,
                                metric_value=round(bad_debt_pct, 2), threshold=3.0,
                                notes=f"Bad debt {bad_debt_pct:.2f}% of revenue")

        # INFORMATION & TRANSPARENCY (SLC 20-24): demand estimation accuracy
        dem_log = [e for e in data.get("demand_estimation_log", []) if e.get("term_start", "")[:4] == yr]
        avg_err = abs(sum(abs(e.get("error_pct", 0.0)) for e in dem_log) / len(dem_log)) if dem_log else 0.0
        if avg_err < 10.0:
            info_rag = RAGStatus.GREEN
        elif avg_err < 20.0:
            info_rag = RAGStatus.AMBER
        else:
            info_rag = RAGStatus.RED
        scorecard.record_check(ComplianceDomain.INFORMATION_TRANSPARENCY, as_of, info_rag,
                                metric_value=round(avg_err, 1), threshold=10.0,
                                notes=f"EAC estimation error {avg_err:.1f}%")

        # COMPLAINTS (SLC 25-29, displayed as "SLC 25C: Communication Channel
        # Choice") -- FIXED 2026-07-10 (director page comment: "How do
        # complaints link to channels available?"): this used to key off
        # avg_complaint_probability, a churn-model metric measuring HOW LIKELY
        # a customer is to complain -- nothing to do with whether they had a
        # real channel choice or were served well once they used one. A real
        # domain-sense mismatch (R10 absurdity class), not a tuning issue.
        # simulation/contact_centre.py already models real multi-channel
        # contact (phone/webchat/email, always all three structurally
        # available -- so literal channel AVAILABILITY is guaranteed by
        # construction) with a real per-contact first-response SLA outcome
        # (breached_sla). The meaningful compliance signal for "channel
        # choice" is whether customers are actually served adequately once
        # they pick a channel -- an SLA-breach rate, not complaint volume.
        # docs/design/SLC25C_CHANNEL_CHOICE_FIX.md.
        cc_log = [
            e for e in data.get("contact_centre_log", [])
            if e.get("period_end", "")[:4] == yr
        ]
        breach_count = sum(1 for e in cc_log if e.get("breached_sla"))
        breach_rate = breach_count / len(cc_log) if cc_log else 0.0
        if not cc_log:
            comp_rag = RAGStatus.GREEN
            comp_notes = "No contact-centre events this year"
        elif breach_rate < 0.10:
            comp_rag = RAGStatus.GREEN
            comp_notes = f"First-response SLA breach rate {breach_rate:.1%} ({breach_count}/{len(cc_log)} contacts)"
        elif breach_rate < 0.25:
            comp_rag = RAGStatus.AMBER
            comp_notes = f"First-response SLA breach rate {breach_rate:.1%} ({breach_count}/{len(cc_log)} contacts)"
        else:
            comp_rag = RAGStatus.RED
            comp_notes = f"First-response SLA breach rate {breach_rate:.1%} ({breach_count}/{len(cc_log)} contacts)"
        scorecard.record_check(ComplianceDomain.COMPLAINTS, as_of, comp_rag,
                                metric_value=round(breach_rate, 4), threshold=0.10,
                                notes=comp_notes)

        # VULNERABLE CUSTOMERS (SLC 30-35): always GREEN (not modelled in detail)
        scorecard.record_check(ComplianceDomain.VULNERABLE_CUSTOMERS, as_of, RAGStatus.GREEN,
                                notes="PSR register maintained; no adverse findings modelled")

        # TARIFF & PRICE CAP (SLC 36-40): always GREEN for I&C (cap applies to SVT resi only)
        scorecard.record_check(ComplianceDomain.TARIFF_PRICE_CAP, as_of, RAGStatus.GREEN,
                                notes="I&C supply exempt from SVT cap (bespoke contracts)")

        # ENVIRONMENTAL (SLC 41-50): policy costs modelled; assume compliance
        scorecard.record_check(ComplianceDomain.ENVIRONMENTAL, as_of, RAGStatus.GREEN,
                                notes="RO, CfD, EE obligations modelled as compliant")

        # NETWORK & BALANCING (SLC 51-60): BSC credit cover
        bsc = yd.get("bsc_credit_required_gbp", 0.0)
        treasury = yd.get("treasury_end_gbp", 0.0)
        net_rag = RAGStatus.GREEN if treasury >= bsc else RAGStatus.RED
        scorecard.record_check(ComplianceDomain.NETWORK_BALANCING, as_of, net_rag,
                                metric_value=round(treasury, 0), threshold=bsc,
                                notes=f"BSC credit GBP {bsc:,.0f} vs treasury GBP {treasury:,.0f}")

        # FINANCIAL RESILIENCE (SFR Decision 2023)
        if fra_ratio >= 3.0:
            fin_rag = RAGStatus.GREEN
        elif fra_ratio >= 1.0:
            fin_rag = RAGStatus.AMBER
        else:
            fin_rag = RAGStatus.RED
        scorecard.record_check(ComplianceDomain.FINANCIAL_RESILIENCE, as_of, fin_rag,
                                metric_value=round(fra_ratio, 1), threshold=1.0,
                                notes=f"FRA ratio {fra_ratio:.1f}x monthly revenue")

    return scorecard
