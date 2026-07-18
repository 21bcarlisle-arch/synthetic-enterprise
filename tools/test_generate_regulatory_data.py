"""Independence tests for tools/generate_regulatory_data.py (R15).

The Regulatory tab's build-status claims used to be static HTML that could
silently drift from the real build state. Relocating those literals into a JSON
file would be the SAME unbacked claim in a new place (R15 forbids it), so every
value the generator emits must be DERIVED from an independent real source.

These tests prove the derivation by INJECTING a mutated source and asserting the
emitted value FOLLOWS it -- a relocated hardcode could not do that:

  * module_count follows an injected module_root (count what's on disk, not "62");
  * slc_domain_count follows an injected domain iterable;
  * a scheme's WIRED status flips to NEXT when its calc module is not wired into
    the (injected) report layer, and back to WIRED when it is;
  * an absent calc module derives NEXT (planned-not-built);
  * EXEMPT is derived from the portfolio's domestic count vs the threshold, not
    asserted -- raise the count above the threshold and the same scheme goes WIRED;
  * overall_rag / obligation_count follow the injected compliance source;
  * the freshness stamp is emitted in the expected shape.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))          # so `company.*` imports resolve
sys.path.insert(0, str(PROJECT / "tools"))  # so the generator module imports

import generate_regulatory_data as G  # noqa: E402


def _write(p: Path, text: str = "x = 1\n") -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


# --------------------------------------------------------------------------
# module_count: derived from disk, follows an injected root (not the literal 62)
# --------------------------------------------------------------------------
def test_module_count_follows_injected_root(tmp_path):
    root = tmp_path / "regmods"
    for name in ("a.py", "b.py", "c.py"):
        _write(root / name)
    _write(root / "__init__.py")        # excluded
    _write(root / "test_a.py")          # excluded (test_ prefix)
    _write(root / "sub" / "d.py")       # counted (recursive)
    assert G.count_regulatory_modules(root) == 4

    data = G.derive_regulatory(
        project_root=tmp_path, module_root=root,
        compliance_domains=[1, 2, 3],
        obligations_source=tmp_path / "none.json",
        customers_source=tmp_path / "none.json",
        report_roots=[tmp_path / "noreport"],
        schemes=[],
    )
    assert data["module_count"] == 4, "module_count must track disk, not a literal"


def test_module_count_zero_on_missing_root(tmp_path):
    assert G.count_regulatory_modules(tmp_path / "does_not_exist") == 0


# --------------------------------------------------------------------------
# slc_domain_count: follows the injected domain iterable
# --------------------------------------------------------------------------
def test_slc_domain_count_follows_injected_domains(tmp_path):
    data = G.derive_regulatory(
        project_root=tmp_path, module_root=tmp_path,
        compliance_domains=["one", "two", "three", "four", "five"],
        obligations_source=tmp_path / "none.json",
        customers_source=tmp_path / "none.json",
        report_roots=[tmp_path], schemes=[],
    )
    assert data["slc_domain_count"] == 5


# --------------------------------------------------------------------------
# per-scheme status: WIRED iff calc module present AND wired into report layer
# --------------------------------------------------------------------------
def _scheme_env(tmp_path, wired: bool):
    """A scheme whose calc module exists; the report layer references it iff wired."""
    calc = tmp_path / "company" / "regulatory" / "widget_scheme.py"
    _write(calc, "WIDGET = 1\n")
    report = tmp_path / "saas" / "reporting"
    report.mkdir(parents=True, exist_ok=True)
    if wired:
        # a genuine import of the module's dotted path
        _write(report / "annual_report.py",
               "from company.regulatory.widget_scheme import WIDGET\n")
    else:
        # a coincidentally-named function -- must NOT count as wired (bare-stem trap)
        _write(report / "annual_report.py",
               "def _section_widget_scheme(data):\n    return ''\n")
    scheme = {"key": "WID", "label": "Widget", "applicable": True,
              "calc_module": "company/regulatory/widget_scheme.py"}
    return scheme, report


def test_scheme_wired_when_report_layer_imports_it(tmp_path):
    scheme, report = _scheme_env(tmp_path, wired=True)
    row = G.derive_scheme_status(scheme, tmp_path, [report], 8, 150_000)
    assert row["status"] == "WIRED", row


def test_scheme_next_when_present_but_not_wired(tmp_path):
    # The bare stem "widget_scheme" appears (in a def name) but the module is
    # NOT imported -- the derivation must report NEXT, not a false WIRED.
    scheme, report = _scheme_env(tmp_path, wired=False)
    row = G.derive_scheme_status(scheme, tmp_path, [report], 8, 150_000)
    assert row["status"] == "NEXT", row


def test_scheme_next_when_module_absent(tmp_path):
    report = tmp_path / "saas" / "reporting"
    report.mkdir(parents=True, exist_ok=True)
    _write(report / "annual_report.py", "x = 1\n")
    scheme = {"key": "GHOST", "label": "Ghost", "applicable": True,
              "calc_module": "company/regulatory/not_built_yet.py"}
    row = G.derive_scheme_status(scheme, tmp_path, [report], 8, 150_000)
    assert row["status"] == "NEXT"
    assert row["module_present"] is False


# --------------------------------------------------------------------------
# EXEMPT: derived from domestic count vs threshold, not asserted
# --------------------------------------------------------------------------
def test_exempt_scheme_follows_domestic_count(tmp_path):
    calc = tmp_path / "company" / "regulatory" / "whd.py"
    _write(calc)
    report = tmp_path / "saas" / "reporting"
    _write(report / "annual_report.py", "from company.regulatory.whd import x\n")
    scheme = {"key": "WHD", "label": "WHD", "applicable": False,
              "calc_module": "company/regulatory/whd.py"}
    below = G.derive_scheme_status(scheme, tmp_path, [report], 8, 150_000)
    above = G.derive_scheme_status(scheme, tmp_path, [report], 200_000, 150_000)
    assert below["status"] == "EXEMPT", "below threshold -> genuinely N/A"
    assert above["status"] == "WIRED", "above threshold the exemption no longer holds"


# --------------------------------------------------------------------------
# overall_rag / obligation_count follow the injected compliance source
# --------------------------------------------------------------------------
def test_overall_rag_follows_obligations_source(tmp_path):
    comp = tmp_path / "company.json"
    comp.write_text(json.dumps({"compliance": {"obligations_register": {
        "count": 41, "overall_rag": "RED",
        "status_counts": {"GREEN": 1, "RED": 40}}}}))
    data = G.derive_regulatory(
        project_root=tmp_path, module_root=tmp_path,
        compliance_domains=[1], obligations_source=comp,
        customers_source=tmp_path / "none.json",
        report_roots=[tmp_path], schemes=[],
    )
    assert data["overall_rag"] == "RED"
    assert data["obligation_count"] == 41
    assert data["status_counts"] == {"GREEN": 1, "RED": 40}


def test_domestic_customer_count_from_register(tmp_path):
    cust = tmp_path / "customers.json"
    cust.write_text(json.dumps({"customers": [
        {"segment": "resi"}, {"segment": "resi"}, {"segment": "I&C"},
        {"segment": "SME"}, {"segment": "domestic"}]}))
    assert G._domestic_customer_count(cust) == 3


# --------------------------------------------------------------------------
# freshness stamp
# --------------------------------------------------------------------------
def test_freshness_stamp_shape(tmp_path):
    data = G.derive_regulatory(
        project_root=tmp_path, module_root=tmp_path,
        compliance_domains=[1], obligations_source=tmp_path / "none.json",
        customers_source=tmp_path / "none.json",
        report_roots=[tmp_path], schemes=[],
    )
    assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", data["generated_at"])


# --------------------------------------------------------------------------
# the live emitted cache is self-consistent (defends against a stale commit)
# --------------------------------------------------------------------------
def test_live_cache_matches_regeneration():
    live = json.loads((PROJECT / "site" / "data" / "regulatory.json").read_text())
    fresh = G.derive_regulatory()
    # everything except the timestamp must match a fresh derivation
    for key in ("module_count", "slc_domain_count", "obligation_count",
                "overall_rag", "domestic_customer_count"):
        assert live[key] == fresh[key], f"{key} drifted: cache={live[key]} fresh={fresh[key]}"
    assert [s["status"] for s in live["schemes"]] == [s["status"] for s in fresh["schemes"]]
