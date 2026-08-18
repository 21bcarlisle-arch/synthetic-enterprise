"""R15 proof for the structural-blank class guard, both ways.

The guard is the R10 closure for
`docs/staging/WORKER_FINDING_A_NULL_CLV_ENTERS_THE_PUBLISHED_MEDIAN_AS_THE_NUMBER_ZERO_2026-08-17.md`
(BLOCKING). R15 says no control counts as evidence until a MUTATION TEST proves it fires on its
own named defect, so every arm below is exercised against the exact source shape that shipped,
and every fail-closed path is exercised by removing the thing the guard depends on.

The three killer patterns, each addressed by name:

* TAUTOLOGY -- `NULLABLE_FIELDS` is checked against the AST of the module that CREATES the nulls
  (`test_the_registry_matches_the_producer`), not against itself. If the guard's field list and
  the producer drift apart, the guard fails rather than scanning for a field nobody publishes.
* FAIL-OPEN -- `test_a_missing_package_is_a_coverage_hole` and its siblings prove the guard
  raises rather than reporting clean when it is scanning nothing, when the producer is gone, and
  when the field set is empty.
* FAIL-SILENT -- `test_the_cli_exit_codes_are_distinct` proves an rc=2 coverage hole is not
  indistinguishable from an rc=0 pass at the caller.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import structural_blank_guard as guard  # noqa: E402


# --------------------------------------------------------------------------------------------
# The class closure on the real tree.
# --------------------------------------------------------------------------------------------

def test_the_real_tree_is_clean():
    """No module folds a deliberately-null field into an aggregate as a number.

    This is the class assertion, and it is why this file is in `CONTROL_TESTS` rather than left
    to name-stem selection: the defect can arrive in a BRAND-NEW module under any of seven
    packages, and a stem selector would only ever fire this when the guard itself is edited --
    the case that needs it least. Both shipped instances lived in modules whose own tests would
    not have run the guard.
    """
    violations = guard.scan_tree(root=ROOT)
    assert violations == [], "\n".join(v.render() for v in violations)


def test_the_registry_matches_the_producer():
    """`NULLABLE_FIELDS` is derived from the producer, so it cannot rot behind it.

    A hand-maintained registry that has fallen behind the code passes silently, which is the
    fail-open shape. This re-derives the set from `_round_or_none`'s call sites and keyword
    bindings in `tools/generate_customer_data.py` and requires the guard's declared set to cover
    it. A fifth nullable figure added to the producer REDS this test until it is registered.
    """
    derived = guard.producer_nullable_fields(root=ROOT)
    assert derived, "the producer derivation found nothing -- the guard has no subject"
    missing = derived - set(guard.NULLABLE_FIELDS)
    assert not missing, (
        f"the producer publishes {sorted(missing)} as nullable and NULLABLE_FIELDS does not "
        f"list them"
    )


def test_the_ratchet_has_no_stale_entries():
    """Every `KNOWN_NON_DEFECTS` entry still matches something, so the list can only shrink.

    An exemption that outlives its site is an exemption nobody can see is dead, and a guard whose
    exemption list can grow silently is the fail-open shape. Removing a ratcheted site therefore
    FORCES removing its entry here.
    """
    everything = guard.scan_tree(root=ROOT, include_known=True)
    live_keys = {v.key for v in everything}
    stale = sorted(set(guard.KNOWN_NON_DEFECTS) - live_keys)
    assert not stale, (
        f"{stale} no longer match the guard -- delete them from KNOWN_NON_DEFECTS"
    )


def test_the_ratchet_entries_are_the_documented_name_collision():
    """The two ratcheted keys are both `churn_probability`, and nothing else is ratcheted.

    Stated as an assertion rather than a comment so that widening the ratchet to a DIFFERENT
    field -- which would be exempting the real defect -- cannot happen quietly.
    """
    fields = {key.split("::")[1] for key in guard.KNOWN_NON_DEFECTS}
    assert fields == {"churn_probability"}, (
        f"the ratchet has grown beyond the documented customer_events name collision: {fields}"
    )


# --------------------------------------------------------------------------------------------
# R15 MUTATION: each arm fires on the exact source shape that shipped.
# --------------------------------------------------------------------------------------------

def test_arm_1_fires_on_the_seven_annual_report_sites():
    """`v.get("clv_gbp") or 0.0` -- the shape that moved a board recommendation."""
    source = (
        "def f(elec_accounts):\n"
        "    clvs = sorted((v.get('clv_gbp') or 0.0) for v in elec_accounts.values())\n"
        "    total = sum((v.get('clv_gbp') or 0) for v in elec_accounts.values())\n"
        "    return clvs, total\n"
    )
    violations = guard.scan_source(source, "fake.py")
    assert len(violations) == 2, [v.render() for v in violations]
    assert all(v.arm == "ARM 1 (or-default)" for v in violations)
    assert all(v.field == "clv_gbp" for v in violations)


def test_it_fires_on_all_seven_shipped_annual_report_sites_verbatim():
    """The strongest available R15 evidence: the guard run over the source AS IT SHIPPED.

    These seven lines are copied verbatim out of
    `saas/reporting/annual_report.py::_section_customer_strategic_value` at commit `9718066ce`,
    the tree the finding measured. Confirmed independently by running `scan_source` over
    `git show HEAD:saas/reporting/annual_report.py` at the time of the repair: 7 violations, the
    same seven the finding enumerated by line. Pinned here as a literal rather than read from
    git, because a test that reads HEAD stops testing the historical defect the moment HEAD
    moves -- which is immediately.
    """
    shipped = (
        "def _section_customer_strategic_value(data):\n"
        "    clvs = sorted((v.get('clv_gbp') or 0.0) for v in elec_accounts.values())\n"
        "    churns = sorted((v.get('latest_churn_probability') or 0.0) for v in elec_accounts.values())\n"
        "    for cid, v in sorted(elec_accounts.items(), key=lambda x: -(x[1].get('clv_gbp') or 0)):\n"
        "        clv = v.get('clv_gbp') or 0.0\n"
        "        churn = v.get('latest_churn_probability') or 0.0\n"
        "        periods = v.get('expected_lifetime_periods') or 0.0\n"
        "    total_clv = sum((v.get('clv_gbp') or 0) for v in elec_accounts.values())\n"
    )
    violations = guard.scan_source(shipped, "saas/reporting/annual_report.py")
    assert len(violations) == 7, [v.render() for v in violations]
    assert [v.field for v in violations] == [
        "clv_gbp",                    # the sorted list feeding the median / quadrant boundary
        "latest_churn_probability",   # the churn boundary
        "clv_gbp",                    # the rank key
        "clv_gbp",                    # the per-account value
        "latest_churn_probability",   # the per-account churn
        "expected_lifetime_periods",  # rendered as "0.0 periods" for accounts with no life
        "clv_gbp",                    # the portfolio total (the one harmless case)
    ]


def test_arm_2_fires_on_the_shadow_html_site():
    """`s.get("clv_gbp", 0)` -- the LATENT spelling, and it must be caught anyway.

    This one substitutes on a MISSING KEY, not on a null value, so it had an empty triggering
    population when it was fixed (19 of 19 lifetime accounts were in the sample). The guard
    catches it regardless: `s` is `sample_custs.get(cid, {})`, so the empty-record path is
    reachable, and a class closure that only fires once a defect has published a wrong number
    is not a closure.
    """
    violations = guard.scan_source("def f(s):\n    return s.get('clv_gbp', 0)\n", "fake.py")
    assert len(violations) == 1
    assert violations[0].arm == "ARM 2 (get-default)"
    assert violations[0].field == "clv_gbp"


def test_arm_3_fires_on_the_subscript_spelling():
    """`v["clv_gbp"] or 0` -- not yet seen in the tree, and the same defect if it lands."""
    violations = guard.scan_source("def f(v):\n    return v['clv_gbp'] or 0\n", "fake.py")
    assert len(violations) == 1
    assert violations[0].arm == "ARM 3 (subscript-or)"


def test_it_fires_on_every_registered_field_not_just_clv():
    """The class does not care which field the blank arrived on.

    The finding's own instance was CLV, but `expected_lifetime_periods` was zeroed at the same
    site and rendered as "0.0 periods" for five accounts that have no expected life at all.
    """
    for field in sorted(guard.NULLABLE_FIELDS):
        violations = guard.scan_source(f"def f(v):\n    return v.get('{field}') or 0.0\n", "fake.py")
        assert len(violations) == 1, f"{field} is registered but not detected"
        assert violations[0].field == field


def test_a_chained_or_still_fires():
    """`(a.get("clv_gbp") or b.get("clv_gbp") or 0)` folds into ONE BoolOp with three values.

    Written because a naive `len(values) == 2` reader -- which is what the first census script
    used -- silently misses the chained spelling, and missing it would be a fail-open hole in
    the arm that catches the shipped instances.
    """
    source = "def f(a, b):\n    return a.get('clv_gbp') or b.get('clv_gbp') or 0\n"
    violations = guard.scan_source(source, "fake.py")
    assert len(violations) == 2, [v.render() for v in violations]


# --------------------------------------------------------------------------------------------
# The other half of R15: the guard must be SILENT on correct handling, or it is noise.
# --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("source, why", [
    ("def f(v):\n    return v.get('clv_gbp')\n",
     "a bare .get carries the None through -- correct"),
    ("def f(v):\n    return v.get('clv_gbp') or '\\u2014'\n",
     "a string fallback IS the render of a blank -- correct"),
    ("def f(v):\n    return v.get('clv_gbp') or None\n",
     "a None fallback keeps the blank a blank -- correct"),
    ("def f(v):\n    x = v.get('clv_gbp')\n    return 0.0 if x is None else x\n",
     "an explicit is-None branch handles it -- correct, even though it yields 0"),
    ("def f(v):\n    return v.get('lifetime_revenue_gbp') or 0.0\n",
     "revenue is never published as null -- not this class"),
    ("def f(v):\n    return v.get('clv_gbp', None)\n",
     "an explicit None default is not a numeric fallback"),
])
def test_correct_handling_does_not_fire(source, why):
    assert guard.scan_source(source, "fake.py") == [], why


def test_a_boolean_fallback_does_not_fire():
    """`or False` is a bool, not a number. `isinstance(True, int)` is True in Python, so this
    would fire without the explicit bool exclusion -- and a bool fallback is a flag default,
    not a fabricated financial figure."""
    assert guard.scan_source("def f(v):\n    return v.get('clv_gbp') or False\n", "fake.py") == []


# --------------------------------------------------------------------------------------------
# R15 FAIL-CLOSED: the guard must never report clean when it has lost its subject.
# --------------------------------------------------------------------------------------------

def test_a_missing_package_is_a_coverage_hole(tmp_path):
    """Scanning nothing must raise, not pass. A guard that finds no violations because it
    walked an empty tree has not cleared the class -- it has lost it."""
    (tmp_path / "company").mkdir()
    (tmp_path / "company" / "x.py").write_text("x = 1\n", encoding="utf-8")
    with pytest.raises(guard.CoverageError, match="does not exist"):
        guard.scan_tree(root=tmp_path, packages=("company", "saas"))


def test_an_empty_field_set_is_a_coverage_hole(tmp_path):
    """A registry that has emptied out would make every scan clean, forever."""
    (tmp_path / "company").mkdir()
    (tmp_path / "company" / "x.py").write_text("x = 1\n", encoding="utf-8")
    with pytest.raises(guard.CoverageError, match="empty"):
        guard.scan_tree(root=tmp_path, packages=("company",), fields=frozenset())


def test_a_missing_producer_is_a_coverage_hole(tmp_path):
    """If the module that creates the nulls is gone, 'no violations' means nothing."""
    with pytest.raises(guard.CoverageError, match="is missing"):
        guard.producer_nullable_fields(root=tmp_path)


def test_a_producer_that_stopped_producing_nulls_is_a_coverage_hole(tmp_path):
    """The producer file existing is not enough -- it must still CALL `_round_or_none`.

    This is the case that a `Path.exists()` check would pass: the file is there, the contract it
    encoded is gone, and the guard would go on watching a field set nothing publishes.
    """
    producer = tmp_path / guard.PRODUCER_REL_PATH
    producer.parent.mkdir(parents=True)
    producer.write_text("def build():\n    return {'clv_gbp': round(0.0, 2)}\n", encoding="utf-8")
    with pytest.raises(guard.CoverageError, match="no longer calls"):
        guard.producer_nullable_fields(root=tmp_path)


def test_an_unparseable_module_is_a_coverage_hole(tmp_path):
    """A file the guard cannot read is a file the guard cannot clear."""
    (tmp_path / "company").mkdir()
    (tmp_path / "company" / "broken.py").write_text("def f(:\n", encoding="utf-8")
    with pytest.raises(guard.CoverageError, match="does not parse"):
        guard.scan_tree(root=tmp_path, packages=("company",))


def test_the_cli_exit_codes_are_distinct(monkeypatch, tmp_path, capsys):
    """rc 0 clean / rc 1 violations / rc 2 coverage hole, all three reachable and different.

    FAIL-SILENT is the pattern where an unavailable check reads as a passing one at the caller.
    The gate runs this guard through its test, but the CLI is what a human and a cron run, and
    an rc that cannot distinguish "clean" from "could not look" is not a control.
    """
    assert guard.main([]) == 0

    monkeypatch.setattr(guard, "ROOT", tmp_path)
    assert guard.main([]) == 2
    assert "COVERAGE HOLE" in capsys.readouterr().err
