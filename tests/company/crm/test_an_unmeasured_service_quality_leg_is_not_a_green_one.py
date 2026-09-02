"""An unmeasured service-quality leg reports "cannot tell", never the flattering branch.

THE DEFECT THIS EXISTS TO CATCH, and it was live in the tree on 2026-09-02:

    if self.avg_bill_shock_pct is None or self.avg_bill_shock_pct < _BILL_SHOCK_AMBER:
        return ServiceQualityRAG.GREEN

A missing measurement returned GREEN -- the best of the three branches -- and `overall_rag` ORed
that GREEN into the company's overall service-quality verdict. The same shape sat one property
away in `shock_rate_pct`, which returned `0.0` for a book with no bills at all, publishing "no
household had a shock" from a year where incidence was not measurable.

It was a loaded gun rather than a live wrong figure: the one caller
(`saas/reporting/annual_report`) had just stopped reading `bill_shock_rag` / `overall_rag` and
started passing `avg_bill_shock_pct=None` for every year, so this module's shock leg was
unmeasured for the whole book and would have reported GREEN for all ten years of it.

KEYED TO THE PROPERTY, NOT TO TODAY'S ANSWER. Nothing here asserts a particular year is RED or
that the current book looks any particular way. Each test names a relation that must hold for any
input: unmeasured is never GREEN; a verdict that cannot be computed cannot be reported as good;
a band expressed in percentage points must stay in percentage points. A control pinned to the
current state goes red when the code becomes more honest and green when the claim rots.

REUSE: tests/company/crm/test_an_unmeasured_service_quality_leg_is_not_a_green_one.py
CLASS: CUSTOM
INDEX: searched "service_quality", "RAG", "fail closed", "not measured", "bill_shock".
       `tests/company/crm/test_phase_ca_service_quality.py` and
       `test_phase_hm_service_quality_monitor.py` are the two existing files and both are
       BEHAVIOURAL band tests -- they assert that 0.15 is GREEN and 0.35 is RED. Neither could
       hold this property, because the input they never pass is the one that broke it: `None`.
       Four of their assertions were themselves pinning the defect and are rewritten in place.
       `tests/saas/reporting/test_a_rendered_shock_figure_is_in_the_units_of_its_own_percent_sign.py`
       holds the same class of property one layer up, on the RENDERER; this holds it on the
       MONITOR, which that file explicitly stopped reading.
"""
import pytest

from company.crm.service_quality_monitor import (
    _BILL_SHOCK_AMBER_PCT,
    _BILL_SHOCK_RED_PCT,
    ServiceQualityMonitor,
    ServiceQualityRAG,
    ServiceQualitySnapshot,
)

#: A snapshot whose clarity and complaint legs are comfortably GREEN, so that any verdict other
#: than GREEN can only have come from the bill-shock leg. Without this the tests below would pass
#: for the wrong reason -- a RED clarity would carry the assertion on its own.
_GOOD_CLARITY = 0.95
_GOOD_COMPLAINT = 0.01


def _snap(shock, clarity=_GOOD_CLARITY, complaint=_GOOD_COMPLAINT, bills=100, shock_n=10):
    return ServiceQualitySnapshot(
        year=2022,
        avg_clarity=clarity,
        avg_complaint_probability=complaint,
        avg_bill_shock_pct=shock,
        bills_count=bills,
        shock_event_count=shock_n,
    )


def test_an_unmeasured_shock_is_not_measured_and_specifically_is_not_green():
    assert _snap(None).bill_shock_rag == ServiceQualityRAG.NOT_MEASURED
    assert _snap(None).bill_shock_rag != ServiceQualityRAG.GREEN


def test_an_unmeasured_leg_cannot_produce_a_good_overall_verdict():
    """The whole point. Both other legs are GREEN; the verdict must still not be GREEN."""
    snap = _snap(None)
    assert snap.clarity_rag == ServiceQualityRAG.GREEN
    assert snap.complaint_rag == ServiceQualityRAG.GREEN
    assert snap.overall_rag not in (ServiceQualityRAG.GREEN, ServiceQualityRAG.AMBER)
    assert snap.overall_rag == ServiceQualityRAG.NOT_MEASURED


def test_a_known_red_still_outranks_an_unmeasured_leg():
    """Fail closed does not mean lose information: RED is already worse than "cannot tell"."""
    snap = _snap(None, clarity=0.10)
    assert snap.clarity_rag == ServiceQualityRAG.RED
    assert snap.overall_rag == ServiceQualityRAG.RED


def test_an_unmeasured_leg_outranks_amber_because_it_could_have_been_red():
    snap = _snap(None, complaint=0.055)
    assert snap.complaint_rag == ServiceQualityRAG.AMBER
    assert snap.overall_rag == ServiceQualityRAG.NOT_MEASURED


def test_every_rag_state_is_reachable_so_the_verdict_is_not_a_constant():
    """A verdict with an unreachable branch reports a constant, which is not a measurement."""
    reached = {
        _snap(0.0).overall_rag,
        _snap(_BILL_SHOCK_AMBER_PCT + 0.1).overall_rag,
        _snap(_BILL_SHOCK_RED_PCT + 0.1).overall_rag,
        _snap(None).overall_rag,
    }
    assert reached == {
        ServiceQualityRAG.GREEN,
        ServiceQualityRAG.AMBER,
        ServiceQualityRAG.RED,
        ServiceQualityRAG.NOT_MEASURED,
    }


def test_no_bills_is_not_an_incidence_of_nought():
    assert _snap(10.0, bills=0, shock_n=0).shock_rate_pct is None
    assert _snap(10.0, bills=200, shock_n=0).shock_rate_pct == 0.0


def test_the_worst_shock_year_skips_unmeasured_years_rather_than_raising():
    mon = ServiceQualityMonitor()
    mon.record(2021, _GOOD_CLARITY, _GOOD_COMPLAINT, None, 100, 10)
    mon.record(2022, _GOOD_CLARITY, _GOOD_COMPLAINT, 41.0, 100, 10)
    mon.record(2023, _GOOD_CLARITY, _GOOD_COMPLAINT, None, 100, 10)
    assert mon.worst_bill_shock_year.year == 2022


def test_no_worst_shock_year_is_named_when_no_year_was_measured():
    """This is the live shape: the one caller records `None` for every year."""
    mon = ServiceQualityMonitor()
    for yr in (2021, 2022, 2023):
        mon.record(yr, _GOOD_CLARITY, _GOOD_COMPLAINT, None, 100, 10)
    assert mon.worst_bill_shock_year is None


def test_the_summary_says_the_shock_was_unmeasured_rather_than_dropping_the_line():
    """A summary one line shorter reads as "no bad year" -- fail-silent, same family."""
    mon = ServiceQualityMonitor()
    mon.record(2022, _GOOD_CLARITY, _GOOD_COMPLAINT, None, 100, 10)
    summary = mon.quality_summary()
    assert "not measured" in summary
    assert "no bill-shock measurement" in summary


def test_the_bands_are_percentage_points_and_agree_with_the_reports_own():
    """One quantity, one unit, across both layers.

    These constants were `0.20`/`0.30` carrying the comment `# pct` while callers compared a
    FRACTION against them. The renderer one layer up now speaks percentage points, so a
    fraction-valued band here would band 43.5 as RED for every year forever.
    """
    from saas.reporting.annual_report import (
        _SHOCK_BAND_AMBER_PCT,
        _SHOCK_BAND_RED_PCT,
    )

    assert _BILL_SHOCK_AMBER_PCT == pytest.approx(_SHOCK_BAND_AMBER_PCT)
    assert _BILL_SHOCK_RED_PCT == pytest.approx(_SHOCK_BAND_RED_PCT)
    # A percentage-point band sits well above 1.0; a fraction-valued one would not.
    assert _BILL_SHOCK_AMBER_PCT > 1.0


def test_the_bands_are_not_attributed_to_a_regulator():
    """The attribution was withdrawn; this keeps it withdrawn.

    `docs/market_research/BILL_SHOCK_EVENT_TYPES_ANCHORS.md` §3 searched for a formal Ofgem
    definition of bill shock and recorded "Confirmed: no". The docstring may discuss Ofgem --
    it has to, to explain what was withdrawn and why -- but it may not present these bands as
    Ofgem benchmarks.

    A bare `"Ofgem benchmarks:" not in doc` cannot express that, because the honest docstring
    QUOTES the withdrawn sentence in order to withdraw it. The checkable property is ORDER: the
    withdrawal must be announced before the claim is ever repeated, so a future edit that
    reinstates the attribution -- or that deletes the withdrawal and leaves the quote -- fails.
    """
    import company.crm.service_quality_monitor as mod

    doc = mod.__doc__
    assert "Confirmed: no" in doc, "the commons finding that refutes the attribution must be cited"
    withdrawn_at = doc.find("WITHDRAWN")
    assert withdrawn_at != -1, "the withdrawal must be stated, not merely implied"

    claim_at = doc.find("Ofgem benchmarks:")
    if claim_at != -1:
        assert withdrawn_at < claim_at, (
            "the withdrawn attribution is repeated before it is withdrawn -- a reader meeting "
            "it in order reads it as this module's live claim"
        )
