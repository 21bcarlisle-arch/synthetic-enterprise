"""Each diff-triggered item fires on a real past diff, and each leg of its trigger can refuse.

The steer's failure mode is a trigger too narrow to ever fire; the opposite failure is a trigger
that fires on everything, which is CLAUDE.md again at a higher price. Both are tested.
"""

import re

import pytest

from tools import diff_triggered_checks as d

CHECKLIST = [i for i in d.load() if i.path.parent == d.CHECKLIST_DIR]


def test_the_checklist_is_not_empty_and_is_not_loaded_by_sessions_during_the_trial():
    assert CHECKLIST
    assert d.CHECKLIST_DIR != d.RULES_DIR


@pytest.mark.parametrize("item", CHECKLIST, ids=lambda i: i.name)
def test_an_item_fires_on_the_past_diff_that_touched_what_it_guards(item):
    assert item.fired_on, f"{item.name} names no past diff, so nothing shows its trigger can fire"
    assert d.fires(item, d.changes_from_git([item.fired_on]))


def _item(**kw):
    base = dict(path=d.CHECKLIST_DIR / "x.md", paths=[], symbols=[], added_only=False,
                fired_on=None, claude_md=[], body="")
    base.update(kw)
    return d.Item(**base)


def test_every_leg_of_a_trigger_can_refuse_and_the_whole_can_fire():
    item = _item(paths=["company/**/*.py"], symbols=[re.compile(r"\bvat")], added_only=True)
    hit = d.FileChange("A", "company/billing/x.py", ["rate = vat * 2"])
    assert d.fires(item, [hit])
    assert not d.fires(item, [d.FileChange("A", "saas/x.py", ["vat"])])  # paths refuses
    assert not d.fires(item, [d.FileChange("M", "company/billing/x.py", ["vat"])])  # added_only
    assert not d.fires(item, [d.FileChange("A", "company/billing/x.py", ["rate = 2"])])  # symbols
    assert not d.fires(item, [d.FileChange("D", "company/billing/x.py", ["vat"])])  # deleted


def test_a_diff_touching_nothing_guarded_triggers_no_checklist_item():
    assert d.match(CHECKLIST, [d.FileChange("M", "docs/staging/NOTE.md", ["hold the guard"])]) == []


def test_each_claude_md_phrase_locates_exactly_one_paragraph():
    text = (d.REPO / "CLAUDE.md").read_text()
    for item in CHECKLIST:
        d.paragraphs_for(item, text)  # raises LookupError naming the item and phrase


def test_the_money_formula_item_reaches_the_golden_task_that_tests_its_habit():
    # g08 (EFFICIENCY_E_E_GOLDEN_SET.yaml) writes its formula in tools/; a billing-only path scope missed it.
    item = next(i for i in CHECKLIST if i.name == "a-billing-formula")
    line = "    return pence_per_day * 365 / 12 / 100"
    assert d.fires(item, [d.FileChange("A", "tools/golden_standing_charge.py", [line])])
    assert not d.fires(item, [d.FileChange("A", "tools/golden_standing_charge.py", ["    x = a * b"])])
