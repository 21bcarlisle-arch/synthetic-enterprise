"""Phase 263 tests: site structure -- the data layer behind the doors, plus the cross-cutting
mobile-pass guard.

THE PAGE-EXISTENCE TESTS WERE REMOVED 2026-08-22. Six tests here asserted that
site/customers/index.html and site/project/index.html exist and carry particular markup. Both were
deleted by the director's ruling in 03dd8c49e (2026-08-20, "eleven pages deleted... no permanent
limbo, no page kept because deleting it feels risky"), so the tests were asserting the exact state
the ruling removed. What survives is the customer/phases DATA layer below, which is still generated
and still read by the live doors."""
import json
from pathlib import Path

SITE = Path(__file__).resolve().parents[2] / "site"


def test_customer_index_json_exists():
    assert (SITE / "data" / "customers" / "_index.json").exists()


def test_customer_json_accounts_present():
    index = json.loads((SITE / "data" / "customers" / "_index.json").read_text())
    assert "C1" in index
    assert "C_IC1" in index


def test_customer_json_c1_valid():
    d = json.loads((SITE / "data" / "customers" / "C1.json").read_text())
    assert d["account_id"] == "C1"
    assert d["segment"] in ("resi", "I&C", "SME")
    assert d["lifetime_revenue_gbp"] > 0


def test_phases_json_exists():
    assert (SITE / "data" / "phases.json").exists()


def test_phases_json_has_test_progression():
    d = json.loads((SITE / "data" / "phases.json").read_text())
    assert len(d["test_progression"]) > 10
    assert d["total_phases"] > 200


def test_main_dashboard_has_site_nav():
    text = (SITE / "index.html").read_text()
    assert "site-nav" in text


def test_generate_customer_data_module():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.generate_customer_data import generate
    assert callable(generate)


# --- Expert-door mobile pass (SITE_CONSTITUTION.md door 8, cross-cutting) ---
# Structural guard so a future edit to a door can't silently drop its phone-legible layout
# (R15: must be able to FAIL -- a page missing the block fails this test, proven by removing the
# block from any one door).
#
# THE DOOR SET IS DERIVED FROM DISK, NOT LISTED (changed 2026-08-22). It used to be the literal
# ["company", "proof", "world", "method", "glossary", "tours"], and every one of those six was
# deleted by 03dd8c49e on 2026-08-20 -- so from that commit until this one the control read six
# missing files and raised FileNotFoundError on the first, which is a control that reports the
# deletion instead of checking the doors that actually shipped. A hand-kept subject list is the
# same defect f5d8ffa96 removed from the R14 basis gate the same week: an allowlist inverts the
# rule, because a door is only checked if somebody remembered to name it.
# Deny-by-default now: every directory under site/ that has an index.html is a door and is
# checked, so a door added tomorrow is covered with nobody editing this file, and a door deleted
# tomorrow simply stops being a subject instead of crashing the control.
def _doors():
    return sorted(p.parent.name for p in SITE.glob("*/index.html"))


def test_site_doors_have_mobile_pass():
    doors = _doors()
    # Not vacuous: an empty or near-empty derivation would make this pass by finding nothing,
    # which is the FAIL-OPEN pattern R15 names. The live set is capabilities/explore/harness/
    # knowledge/privacy, so 4 is a floor that catches a broken glob without pinning the count.
    assert len(doors) >= 4, f"door derivation found only {doors} -- glob is broken, not the site"
    missing = [d for d in doors
               if "@media (max-width: 640px)" not in (SITE / d / "index.html").read_text()]
    assert missing == [], f"doors missing the mobile @media(max-width:640px) pass: {missing}"
