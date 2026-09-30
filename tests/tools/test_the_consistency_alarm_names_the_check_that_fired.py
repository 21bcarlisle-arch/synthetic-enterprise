"""H46: the publisher's consistency alarm names the blocker that fired, not a retired one.

THE DEFECT. From 2026-08-20, when the dashboard-vs-exec-summary comparison was retired, to
2026-09-30, every red verdict from `generate()` reached the log and the director's NTFY as
"dashboard/exec-summary surfaces disagree". The 2026-09-05 red was in fact
`_check_population_consistency` (opex household_count 69 != resi households 90), and the
director's ruling quoted the alarm's cause back, because the alarm was all he had.
"""
import ast
import inspect

import background.process_run_complete as prc
import tools.generate_dashboard_data as gdd
from tests.tools.test_publish_blockers_guard_a_reachable_page import _checks_in_the_verdict


def _named_pairs() -> set:
    """The check names generate() can report in LAST_FAILED_CHECKS, read from its AST."""
    tree = ast.parse(inspect.getsource(gdd.generate))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "LAST_FAILED_CHECKS" for t in node.targets
        ):
            for sub in ast.walk(node.value):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str) \
                        and sub.value.startswith("_check_"):
                    names.add(sub.value)
    return names


def test_every_blocker_in_the_verdict_can_be_named_by_the_alarm():
    # Non-vacuous: the verdict has blockers, so equality is not two empty sets agreeing.
    verdict = _checks_in_the_verdict()
    assert verdict, "the verdict holds no blockers -- this control would pass on nothing"
    assert _named_pairs() == verdict, (
        "a blocker in generate()'s verdict is missing from LAST_FAILED_CHECKS's pairs (or a "
        "retired one is still listed); a red from it would reach the alarm unnamed"
    )


def test_the_alarm_names_the_failed_check_and_its_page():
    detail = gdd.consistency_alarm_detail(("_check_population_consistency",))
    assert "_check_population_consistency" in detail
    assert gdd.PUBLISH_VERDICT_CHECKS["_check_population_consistency"][1] in detail


def test_MUTATION_the_alarm_reads_the_recorded_failure_not_a_fixed_cause(monkeypatch):
    # The pre-H46 alarm was a constant; a constant cannot name two different checks.
    monkeypatch.setattr(gdd, "LAST_FAILED_CHECKS", ("_check_front_door_segment_claim",))
    one = gdd.consistency_alarm_detail()
    monkeypatch.setattr(gdd, "LAST_FAILED_CHECKS", ("_check_front_door_selection_draw_count",))
    two = gdd.consistency_alarm_detail()
    assert one != two
    assert "_check_front_door_segment_claim" in one
    assert "_check_front_door_selection_draw_count" in two


def test_an_empty_record_says_the_verdict_was_not_reached_rather_than_guessing():
    assert "did not reach its verdict" in gdd.consistency_alarm_detail(())


def test_both_publisher_alarm_sites_use_the_recorded_detail():
    src = inspect.getsource(prc)
    assert src.count("consistency_alarm_detail()") == 2
