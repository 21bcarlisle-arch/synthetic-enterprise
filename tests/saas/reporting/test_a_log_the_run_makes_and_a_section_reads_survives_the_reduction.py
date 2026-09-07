"""A log the run computes and a report section reads must survive `extract_report_data`.

THE DEFECT (2026-09-07). `simulation/run_phase2b.py` emits `profitability_uplift_log` -- writer 3's
record of every renewal repriced for unprofitability. `_section_profitability_uplift` reads it.
Between them sits `extract_report_data`, whose forwarding is OPT-IN: a key it does not name is
silently absent from the saved payload, so the section returned "" in every run this repo has ever
produced. On the run committed at `docs/reports/run_output_latest.json` the key was simply not
there, and its absence was indistinguishable from the policy declining to fire.

WHY THIS FILE IS A CENSUS AND NOT A TEST OF THAT ONE KEY. The guard below was written first and run
as the census, and it named THREE dropped logs where one was being chased: `profitability_uplift_log`
(the reported instance), `triad_log` and `volume_tolerance_log` -- two nobody was looking for, each
with a whole section that had never once rendered. A control pinned to writer 3 would have gone
green on the repair and left the other two exactly as they were. So the property, not today's
answer: *the intersection of what the run returns and what a section reads is what the reduction
must carry*, whatever either end grows next.

The reachability floor is asserted before the property, because a census that selects nothing passes
by construction -- an AST walk that quietly stops matching (a renamed parameter, a dict built by
update() instead of a literal) would otherwise read as "nothing is dropped".
"""

import ast
from pathlib import Path

import pytest

from saas.reporting.annual_report import _section_profitability_uplift

_ROOT = Path(__file__).resolve().parents[3]
_RUN = _ROOT / "simulation" / "run_phase2b.py"
_REPORT = _ROOT / "saas" / "reporting" / "annual_report.py"

#: Below this, the census is not measuring anything and its silence means nothing. Eight logs were
#: correctly carried on the day this was written; the floor sits well under that so ordinary
#: retirement of a log does not fail the file, but a walk that stops matching altogether does.
_MIN_LOGS_UNDER_CENSUS = 4


def _returned_dict_keys(tree: ast.AST) -> set[str]:
    """Every string key of every dict literal that is RETURNED anywhere in `tree`."""
    keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            keys |= {
                k.value for k in node.value.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)
            }
    return keys


def _keys_read_off_data(tree: ast.AST) -> set[str]:
    """Every `data.get("...")` key in the module -- what a report section asks the payload for."""
    keys: set[str] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "data"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            keys.add(node.args[0].value)
    return keys


def _extract_report_data_keys(tree: ast.AST) -> set[str]:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "extract_report_data":
            return _returned_dict_keys(node)
    pytest.fail("`extract_report_data` not found in saas/reporting/annual_report.py")


def _census() -> tuple[set[str], set[str]]:
    run_tree = ast.parse(_RUN.read_text())
    report_tree = ast.parse(_REPORT.read_text())
    produced = {k for k in _returned_dict_keys(run_tree) if k.endswith("_log")}
    read = {k for k in _keys_read_off_data(report_tree) if k.endswith("_log")}
    return produced & read, _extract_report_data_keys(report_tree)


def test_the_census_selects_enough_logs_to_be_capable_of_finding_one_dropped():
    """The reachability floor. Run this before believing the control below.

    Both ends are asserted separately, because the intersection going empty has two causes that
    want opposite fixes: the run stopped returning logs, or the report stopped reading them.
    """
    under_census, carried = _census()
    assert len(under_census) >= _MIN_LOGS_UNDER_CENSUS, (
        f"the census selected only {sorted(under_census)} -- under the floor of "
        f"{_MIN_LOGS_UNDER_CENSUS}, so its verdict below is close to vacuous. Either the run's "
        "returned dict or the sections' `data.get` reads stopped matching the AST walk; fix the "
        "walk before trusting a green from this file."
    )
    assert carried, "`extract_report_data` returned no literal dict keys -- the walk is broken"


def test_no_log_the_run_makes_and_a_section_reads_is_dropped_by_extract_report_data():
    """THE PROPERTY. Every log with a producer AND a consumer must be named in the reduction.

    This is the control the finding asked for, keyed to the relationship rather than to the count
    of the day. It goes red the moment a new `*_log` gets a section without getting a forwarding
    line -- which is the only way this defect has ever arrived.
    """
    under_census, carried = _census()
    dropped = sorted(under_census - carried)
    assert not dropped, (
        f"{dropped} -- `simulation/run_phase2b.py` returns each of these and a `_section_*` in "
        "`saas/reporting/annual_report.py` reads it, but `extract_report_data` does not forward "
        "it. Its section renders nothing in every saved payload, and that emptiness is "
        "indistinguishable from the policy never firing. Add a "
        '`"<key>": phase2b.get("<key>", [])` line to the returned dict.'
    )


def test_writer_3s_section_tells_a_missing_log_from_a_log_that_is_empty():
    """The second half of the repair: silence said two opposite things.

    `""` for both "fired on nothing" and "the record was dropped" is what let the defect above sit
    unnoticed through every run. All three states are asserted here in one control, over the whole
    partition, so a section that collapsed any two of them back together cannot pass.
    """
    absent = _section_profitability_uplift({})
    empty = _section_profitability_uplift({"profitability_uplift_log": []})
    fired = _section_profitability_uplift({"profitability_uplift_log": [
        {"customer_id": "C1", "term_start": "2021-04-01",
         "uplift_gbp_per_mwh": 5.0, "unit_rate_after": 142.5},
    ]})

    assert absent and empty and fired, (
        "every state must put something on the page -- an empty string is the silence this "
        f"control exists to forbid (absent={absent!r}, empty={empty!r})"
    )
    assert absent != empty, (
        "a missing log and an empty log render identically, so the page still cannot say which "
        "of the two happened -- that is the defect, not a cosmetic difference"
    )
    assert "cannot" in absent.lower(), "the missing-log state must NAME its reason on the surface"
    assert "C1" in fired and "5.0" in fired.replace("5.00", "5.0"), (
        "the fired state must still publish its rows -- the repair must not have cost the table"
    )
