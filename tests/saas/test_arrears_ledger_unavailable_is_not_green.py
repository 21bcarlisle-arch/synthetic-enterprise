"""R15 mutation proof for the arrears fail-open CLASS (2026-08-12).

Closes `WORKER_FINDING_ARREARS_RAG_IS_FAIL_OPEN_ON_A_MISSING_LEDGER_2026-08-09.md`
as a class rather than an instance (R10). The finding named ONE surface; the census
found THREE, each with its own copy of the same `except: pass` around the billing
ledger read, and two live tests that asserted the fail-open output as correct:

  * `saas/reporting/annual_report.py::_section_population_anchoring`
  * `tools/generate_dashboard_data.py::extract_arrears_case_load`
  * `tools/population_anchor.py::_arrears_check_by_year`

THE MUTATION each test below performs: point the surface at a tree with no billing
ledger (or an unparseable one) and assert it does NOT report green. Before the fix
every one of these assertions failed -- the surfaces printed a confident 0.0% and a
GREEN/`green`/OK verdict over data they had never read. That is what makes these
controls able to fail (R15): the named defect is reproducible on demand, and the
control fires on it.

The distinguishing value is 0.0%, which is ALSO a legitimate reading (2025 genuinely
renders 0.0% with the ledger present), so each test additionally pins the
available-ledger direction -- a control that only ever sees the broken input cannot
tell you it is measuring the right thing.
"""
import json

import pytest

from saas.reporting.arrears_ledger import UNAVAILABLE_NOTE, from_payload, load


# ── the shared reader ────────────────────────────────────────────────────────────
def test_missing_file_is_unavailable_not_empty(tmp_path):
    view = load(tmp_path / "nope.json")
    assert view.available is False
    assert view.unavailable_reason
    assert view.count_for(2020) == 0  # empty AND unavailable -- callers must not conflate


def test_malformed_json_is_unavailable(tmp_path):
    p = tmp_path / "billing_ledger.json"
    p.write_text("not valid json")
    view = load(p)
    assert view.available is False
    assert "not valid JSON" in view.unavailable_reason


def test_ledger_with_no_customers_is_unavailable(tmp_path):
    p = tmp_path / "billing_ledger.json"
    p.write_text(json.dumps({"customers": {}}))
    view = load(p)
    assert view.available is False, (
        "a parsed-but-empty ledger cannot source an arrears numerator either -- "
        "treating it as available leaves the same absurdity reachable"
    )


def test_a_directory_where_the_ledger_should_be_is_unavailable(tmp_path):
    (tmp_path / "billing_ledger.json").mkdir()
    view = load(tmp_path / "billing_ledger.json")
    assert view.available is False


def test_populated_ledger_is_available_and_counts_distinct_customers(tmp_path):
    p = tmp_path / "billing_ledger.json"
    p.write_text(json.dumps({"customers": {
        "C1": {"arrears_history": [{"opened_date": "2020-03-01"},
                                   {"opened_date": "2020-09-01"}]},
        "C2": {"arrears_history": [{"opened_date": "2021-04-01"}]},
    }}))
    view = load(p)
    assert view.available is True
    assert view.unavailable_reason == ""
    assert view.count_for(2020) == 1  # C1 counted once despite two cases
    assert view.count_for(2021) == 1
    assert view.count_for(2019) == 0  # a real zero, on an available ledger


def test_a_genuinely_zero_year_stays_available(tmp_path):
    """The reading that made the bug invisible: 0.0% is legitimate. It must remain
    distinguishable from the unavailable case by `available`, not by the count."""
    p = tmp_path / "billing_ledger.json"
    p.write_text(json.dumps({"customers": {"C1": {"arrears_history": []}}}))
    view = load(p)
    assert view.available is True
    assert view.count_for(2020) == 0


def test_from_payload_asks_the_same_question(tmp_path):
    assert from_payload({}).available is False
    assert from_payload(None).available is False
    assert from_payload({"customers": {"C1": {}}}).available is True


# ── surface 1: the annual report section ─────────────────────────────────────────
_YEARS = {"years": {
    "2020": {"avg_complaint_probability": 0.04,
             "active_customer_ids": ["C%d" % i for i in range(1, 11)]},
    "2021": {"avg_complaint_probability": 0.04,
             "active_customer_ids": ["C%d" % i for i in range(1, 11)]},
}}


def _annual_section(ledger_path):
    from saas.reporting.annual_report import _section_population_anchoring
    return _section_population_anchoring(_YEARS, ledger_path=ledger_path)


def test_report_does_not_print_a_green_arrears_verdict_without_a_ledger(tmp_path):
    """THE original finding's mutation: the renderer pointed at a tree with no
    ledger printed `**Arrears:** 10 of 10 years GREEN`."""
    out = _annual_section(tmp_path / "absent.json")
    assert "years GREEN (DESNZ" not in out
    assert UNAVAILABLE_NOTE in out
    # and no year may carry an arrears RAG flag it could not compute
    arrears_cells = [ln.split("|")[5:8] for ln in out.splitlines() if ln.startswith("| 20")]
    assert arrears_cells, "expected per-year rows to still render"
    for rate, bench, rag in arrears_cells:
        assert rate.strip() == "n/a"
        assert rag.strip() == "n/a"


def test_report_still_prints_a_real_arrears_verdict_with_a_ledger(tmp_path):
    p = tmp_path / "billing_ledger.json"
    p.write_text(json.dumps({"customers": {
        "C1": {"arrears_history": [{"opened_date": "2020-03-01"}]},
    }}))
    out = _annual_section(p)
    assert UNAVAILABLE_NOTE not in out
    assert "years GREEN (DESNZ" in out
    assert "10.0%" in out  # 1 of 10 active customers


def test_report_complaints_verdict_survives_an_absent_ledger(tmp_path):
    """The ledger is the arrears numerator only -- an absent one must not silently
    take the complaints anchoring down with it."""
    out = _annual_section(tmp_path / "absent.json")
    assert "**Complaints:** 2 of 2 years GREEN" in out


# ── surface 2: the dashboard Operations tab ──────────────────────────────────────
def test_dashboard_arrears_status_is_unavailable_not_green(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)  # no site/state/billing_ledger.json
    result = gdd.extract_arrears_case_load(_YEARS)
    assert result["ledger_available"] is False
    for row in result["annual"]:
        assert row["status"] == "unavailable"
        assert row["status"] != "green"
        assert row["arrears_rate_pct"] is None


def test_dashboard_arrears_status_is_unavailable_on_malformed_json(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    d = tmp_path / "site" / "state"
    d.mkdir(parents=True)
    (d / "billing_ledger.json").write_text("not valid json")
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_arrears_case_load(_YEARS)
    assert result["ledger_available"] is False
    assert all(r["status"] == "unavailable" for r in result["annual"])


def test_dashboard_arrears_still_rags_a_present_ledger(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    d = tmp_path / "site" / "state"
    d.mkdir(parents=True)
    (d / "billing_ledger.json").write_text(json.dumps({"customers": {
        "C1": {"arrears_history": [{"opened_date": "2020-03-01"}]},
    }}))
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_arrears_case_load(_YEARS)
    assert result["ledger_available"] is True
    row = next(r for r in result["annual"] if r["year"] == 2020)
    assert row["arrears_rate_pct"] == 10.0
    assert row["status"] == "amber"


def test_dashboard_unavailable_is_distinct_from_unknown(tmp_path, monkeypatch):
    """`unknown` already meant "zero active customers" -- a denominator problem.
    An absent ledger is a NUMERATOR problem and must not borrow that word."""
    import tools.generate_dashboard_data as gdd
    d = tmp_path / "site" / "state"
    d.mkdir(parents=True)
    (d / "billing_ledger.json").write_text(json.dumps({"customers": {"C1": {}}}))
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_arrears_case_load({"years": {"2020": {"active_customer_ids": []}}})
    assert result["annual"][0]["status"] == "unknown"


# ── surface 3: the population-anchoring gate ─────────────────────────────────────
def test_population_anchor_rags_unavailable_not_green(tmp_path):
    from tools.population_anchor import ARREARS_RAG_UNAVAILABLE, generate
    run = tmp_path / "run.json"
    run.write_text(json.dumps({"customer_events": [], "years": {
        "2020": {"avg_complaint_probability": 0.05, "bad_debt_gbp": 1000,
                 "revenue_gbp": 100000, "active_customer_ids": ["C1", "C2"]},
    }}))
    result = generate(run, tmp_path / "out.json",
                      billing_ledger_path=tmp_path / "absent.json")
    assert result["meta"]["arrears_ledger_available"] is False
    for f in result["arrears_vs_benchmark"]:
        assert f["rag"] == ARREARS_RAG_UNAVAILABLE
        assert f["rag"] != "GREEN"
        assert f["ledger_available"] is False


def test_population_anchor_rags_green_on_a_real_clean_ledger(tmp_path):
    from tools.population_anchor import generate
    run = tmp_path / "run.json"
    run.write_text(json.dumps({"customer_events": [], "years": {
        "2020": {"avg_complaint_probability": 0.05, "bad_debt_gbp": 1000,
                 "revenue_gbp": 100000,
                 "active_customer_ids": ["C%d" % i for i in range(1, 21)]},
    }}))
    ledger = tmp_path / "billing_ledger.json"
    ledger.write_text(json.dumps({"customers": {
        "C1": {"arrears_history": [{"opened_date": "2020-03-01"}]},
    }}))
    result = generate(run, tmp_path / "out.json", billing_ledger_path=ledger)
    assert result["meta"]["arrears_ledger_available"] is True
    assert result["arrears_vs_benchmark"][0]["rag"] == "GREEN"  # 5% < 8%
    assert result["arrears_vs_benchmark"][0]["ledger_available"] is True


# ── the class guard ──────────────────────────────────────────────────────────────
# R10: the instance fix is worthless if a fourth surface opens its own `except: pass`
# around the same file. The CLASS is specifically "an arrears count over an
# active-customer denominator" -- a population rate that goes green when its
# numerator's source is absent. That is a structural signature, not a grep
# convenience: every surface in the class reads the ledger AND reads
# `active_customer_ids`; every surface outside it renders one named customer's own
# cases, where an absent ledger yields an empty panel rather than a false all-clear.
_LEDGER = "billing_ledger.json"
_DENOMINATOR = "active_customer_ids"

# Files that read the ledger but are NOT in the class, each with the reason it is
# out. An entry earns its place by not computing a population rate -- asserted
# below, so this list cannot quietly absorb a real instance.
_NOT_A_POPULATION_RATE = {
    "tools/generate_billing_ledger.py": "writes the ledger; it is the source, not a reader of it",
    "tools/generate_shadow_html.py": "renders per-customer case studies + already-RAGged population_anchoring.json",
    "tools/generate_company_data.py": "renders one named account's own arrears cases",
    "tools/generate_payment_ledger_data.py": "builds a per-account chronological ledger",
}


def _ledger_reading_modules():
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent.parent
    reader = root / "saas" / "reporting" / "arrears_ledger.py"
    found = {}
    for path in sorted(list((root / "saas").rglob("*.py")) + list((root / "tools").rglob("*.py"))):
        if path == reader:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if _LEDGER in text or "arrears_history" in text:
            found[str(path.relative_to(root))] = text
    return found


def test_every_population_rate_surface_goes_through_the_shared_reader():
    """The teeth. A surface that divides arrears by an active-customer population
    must ask the availability question, and there is one place that asks it."""
    offenders = [
        rel for rel, text in _ledger_reading_modules().items()
        if _DENOMINATOR in text and "arrears" in text and "arrears_ledger" not in text
    ]
    assert not offenders, (
        "these surfaces derive a population arrears rate without the shared "
        f"availability question: {offenders}"
    )


def test_the_three_known_surfaces_are_still_in_the_class():
    """Vacuity guard. If the discriminator ever stops matching the surfaces the
    finding was about, the test above passes for the wrong reason."""
    found = _ledger_reading_modules()
    for rel in ("saas/reporting/annual_report.py",
                "tools/generate_dashboard_data.py",
                "tools/population_anchor.py"):
        assert rel in found, f"{rel} no longer reads the ledger -- guard subject drifted"
        assert "arrears_ledger" in found[rel], f"{rel} stopped using the shared reader"


def test_the_exemptions_have_not_quietly_become_instances():
    """An allowlist that only ever grows is a fail-open. Each exempt file is
    re-checked against the class signature every run."""
    found = _ledger_reading_modules()
    for rel, reason in _NOT_A_POPULATION_RATE.items():
        assert rel in found, f"{rel} is exempted but no longer reads the ledger -- stale entry"
        assert _DENOMINATOR not in found[rel], (
            f"{rel} was exempted because it {reason}, but it now reads "
            f"{_DENOMINATOR} -- it has joined the class and needs the shared reader"
        )
