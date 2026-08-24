"""R15 proof for `tools/running_total_order.py`: the control fires on its own named defect.

The defect is real and measured (2026-08-24): sorting `all_records` by
`(settlement_date, settlement_period)` and walking `treasury_cash_balance_gbp` off it turned
0 genuine 2017 treasury drawdowns into 6,747 published ones. A control against that is only
evidence if it can FAIL, so every shape it claims to catch is driven here against a synthetic
tree with a known answer, and the three killer patterns are answered explicitly:

  * TAUTOLOGY  -- the expected answers are written by hand in each test, never derived from
                  the scanner that is under test.
  * FAIL-OPEN  -- `test_a_clean_tree_that_mentions_no_field_is_unavailable_not_clean` and the
                  null controls below: the scanner must stay silent on ORDER-PRESERVING reads
                  and on non-running-total fields, or "green" would mean nothing.
  * FAIL-SILENT -- an empty/misdirected scan raises `OrderCheckUnavailable` rather than
                  returning no violations.
"""
from __future__ import annotations

import pytest

from tools import running_total_order as rto

FIELD = "treasury_cash_balance_gbp"


def _tree(tmp_path, **files):
    """Build a synthetic scan tree: `_tree(tmp_path, **{"saas/reporting/x.py": "..."})`."""
    for rel, source in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
    return str(tmp_path)


# ── the three shapes it claims to catch ────────────────────────────────────────────────────

def test_it_catches_the_comprehension_over_a_reordering():
    """The named instance's exact shape, from `annual_report._drawdown_events`' input."""
    source = (
        "def report(yr_records):\n"
        "    return [\n"
        f"        r[{FIELD!r}]\n"
        "        for r in sorted(yr_records, key=lambda r: (r['settlement_date'], r['settlement_period']))\n"
        "    ]\n"
    )
    found = rto.scan_source(source, "saas/reporting/annual_report.py")
    assert [(v["shape"], v["field"]) for v in found] == [
        ("comprehension-over-reordering", FIELD)
    ]


def test_it_catches_a_subscript_of_a_reordering():
    """`treasury_end`: the latest-dated record's balance is not the year's closing balance."""
    source = (
        "def report(yr_records):\n"
        "    return max(yr_records, key=lambda r: (r['settlement_date'], r['settlement_period']))"
        f"[{FIELD!r}]\n"
    )
    found = rto.scan_source(source, "saas/reporting/annual_report.py")
    assert [(v["shape"], v["field"]) for v in found] == [
        ("subscript-of-reordering", FIELD)
    ]


def test_it_catches_the_bind_then_read_evasion():
    """Zero instances in the tree today -- which is exactly why it needs proving here.

    Splitting the re-order and the read across two statements is the way a future consumer
    walks around the first two shapes without meaning to.
    """
    source = (
        "def report(yr_records):\n"
        "    ordered = sorted(yr_records, key=lambda r: r['settlement_date'])\n"
        f"    return ordered[-1][{FIELD!r}]\n"
    )
    found = rto.scan_source(source, "saas/reporting/segment_report.py")
    assert [(v["shape"], v["field"]) for v in found] == [
        ("read-of-reordered-binding", FIELD)
    ]


# ── null controls: the scanner must stay SILENT on these, or green means nothing ───────────

def test_a_filtered_slice_in_accumulation_order_is_not_flagged():
    """`run_phase2b`'s own correct read. Filtering preserves accumulation order.

    This is the null control that moves the SAMPLE and not the law: same field, same
    subscript, same `[-1]` -- and no reordering. If this were flagged the control would be
    telling every producer in the repo to stop reading its own running total.
    """
    source = (
        "def summarise(all_records, year):\n"
        "    yr = [r for r in all_records if r['settlement_date'][:4] == year]\n"
        f"    return yr[-1][{FIELD!r}]\n"
    )
    assert rto.scan_source(source, "simulation/run_phase2b.py") == []


def test_a_reordered_read_of_a_non_running_total_field_is_not_flagged():
    """Sorting is not itself the defect -- sorting a RUNNING TOTAL is.

    `margin_gbp` is a per-record amount, not a portfolio running total, so sorting the book
    and summing it is correct and common. A control that flagged this would be unusable.
    """
    source = (
        "def report(yr_records):\n"
        "    return [r['margin_gbp'] for r in sorted(yr_records, key=lambda r: r['settlement_date'])]\n"
    )
    assert rto.scan_source(source, "saas/reporting/annual_report.py") == []


def test_declaring_a_field_name_in_a_constant_is_not_a_read():
    """`settlement_daily.CLOSING_FIELDS` names the field without reading anything."""
    source = f"CLOSING_FIELDS = ({FIELD!r}, 'settlement_period')\n"
    assert rto.scan_source(source, "simulation/settlement_daily.py") == []


# ── the gate ratchet: all three directions must be able to fail ────────────────────────────

def test_the_control_can_pass(tmp_path):
    """A tree that mentions the field and never re-sorts it produces no gate problem.

    Without this, every other test here is consistent with a control that always fails.
    """
    root = _tree(tmp_path, **{
        "simulation/run.py": (
            "def summarise(all_records, year):\n"
            "    yr = [r for r in all_records if r['settlement_date'][:4] == year]\n"
            f"    return yr[-1][{FIELD!r}]\n"
        ),
    })
    assert rto.gate_problems(root=root, dirs=("simulation",), known={}) == []


def test_a_new_re_sorted_read_fails_the_gate(tmp_path):
    root = _tree(tmp_path, **{
        "saas/report.py": (
            "def report(yr_records):\n"
            f"    return [r[{FIELD!r}] for r in sorted(yr_records, key=lambda r: r['settlement_date'])]\n"
        ),
    })
    problems = rto.gate_problems(root=root, dirs=("saas",), known={})
    assert len(problems) == 1
    assert "RE-SORTED READ OF A RUNNING TOTAL" in problems[0]
    assert "saas/report.py" in problems[0]


def test_a_second_read_of_an_already_frozen_key_fails_the_gate(tmp_path):
    """The count is what stops a new defect hiding inside an existing baseline entry.

    Same module, same shape, same field as a frozen entry -- so a key-only baseline would
    absorb it silently. That is the dedup-without-a-discriminator failure, and the reason
    `KNOWN_READS` carries counts rather than bare keys.
    """
    source = (
        "def report(yr_records):\n"
        f"    a = [r[{FIELD!r}] for r in sorted(yr_records, key=lambda r: r['settlement_date'])]\n"
        f"    b = [r[{FIELD!r}] for r in sorted(yr_records, key=lambda r: r['settlement_period'])]\n"
        "    return a, b\n"
    )
    root = _tree(tmp_path, **{"saas/report.py": source})
    known = {
        f"saas/report.py::comprehension-over-reordering::{FIELD}": {"count": 1, "why": "frozen"},
    }
    problems = rto.gate_problems(root=root, dirs=("saas",), known=known)
    assert len(problems) == 1
    assert "ANOTHER RE-SORTED READ" in problems[0]
    assert "up from the frozen 1" in problems[0]

    # and the same tree passes once the baseline honestly says there are two
    known[f"saas/report.py::comprehension-over-reordering::{FIELD}"]["count"] = 2
    assert rto.gate_problems(root=root, dirs=("saas",), known=known) == []


def test_a_repaired_read_left_in_the_baseline_fails_the_gate(tmp_path):
    """Shrink-only cuts both ways: a discharged entry must be removed, or the baseline
    stops being countable and the control quietly over-reports its own debt."""
    root = _tree(tmp_path, **{
        "saas/report.py": (
            "def report(yr_records):\n"
            f"    return yr_records[-1][{FIELD!r}]\n"
        ),
    })
    known = {
        f"saas/report.py::comprehension-over-reordering::{FIELD}": {"count": 1, "why": "frozen"},
    }
    problems = rto.gate_problems(root=root, dirs=("saas",), known=known)
    assert len(problems) == 1
    assert "STALE BASELINE" in problems[0]


# ── fail-silent: an unavailable check is a FAILED check ────────────────────────────────────

def test_a_tree_that_mentions_no_running_total_is_unavailable_not_clean(tmp_path):
    """If the scan finds no running-total field anywhere it is pointed at the wrong tree.

    Returning "no violations" there would be the fail-silent pattern: a control that passes
    precisely when it cannot see its subject.
    """
    root = _tree(tmp_path, **{"simulation/run.py": "def f(records):\n    return sum(r['margin_gbp'] for r in records)\n"})
    with pytest.raises(rto.OrderCheckUnavailable):
        rto.scan_tree(root=root, dirs=("simulation",))


def test_a_missing_scan_directory_is_unavailable_not_clean(tmp_path):
    with pytest.raises(rto.OrderCheckUnavailable):
        rto.scan_tree(root=str(tmp_path), dirs=("simulation",))


# ── the live tree ──────────────────────────────────────────────────────────────────────────

def test_the_live_tree_matches_its_frozen_baseline():
    """The gate is green on the real repository -- and green for a stated reason, not by
    accident: exactly the three frozen reads, no more and no fewer."""
    assert rto.gate_problems() == []


def test_the_live_scan_still_finds_the_named_instance():
    """The finding's own instance must still be visible to the default (reporting) mode.

    If a refactor made it invisible without repairing it, the standing red would go quiet
    and the debt would look discharged.
    """
    found = rto.scan_tree()
    keys = {rto._key(v) for v in found}
    assert (f"saas/reporting/annual_report.py::comprehension-over-reordering::{FIELD}") in keys
    assert keys == set(rto.KNOWN_READS)


def test_every_frozen_entry_names_a_repair():
    """A frozen entry without a repair is a permanent exception wearing a ratchet's clothes."""
    for key, entry in rto.KNOWN_READS.items():
        assert "REPAIR" in entry["why"], f"{key} does not name its repair"
        assert entry["count"] >= 1
