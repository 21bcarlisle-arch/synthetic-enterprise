"""Director, 2026-10-10: every stretch's focus carries at least two supplier items, world work
only where it blocks a supplier result, and each stretch log reports the world/supplier/other
split of its commits. Each test names the defect it catches.
"""
from background import delivery_seat as seat
from background import direction


def _item(i, side, **extra):
    return {"id": f"item-{i}", "what": "w", "why": "y", "side": side, **extra}


def _record(*items):
    return {"focus": list(items)}


def test_a_balanced_focus_PASSES_before_anything_is_refused():
    """Fires on: a rule that refuses every record -- it would pass every refusal test below and
    stop the seat from ever writing direction again."""
    record = _record(_item(1, "supplier"), _item(2, "supplier"),
                     _item(3, "world", unblocks="item-1's billing result"), _item(4, "other"))
    assert direction.focus_balance_problems(record) == []


def test_one_supplier_item_is_refused():
    """Fires on: the threshold read as 'any supplier item' -- the 1-3 a day the director named."""
    problems = direction.focus_balance_problems(_record(_item(1, "supplier"), _item(2, "other")))
    assert any("1 supplier item" in p for p in problems)


def test_world_work_that_names_no_supplier_result_is_refused():
    """Fires on: world fidelity admitted for its own sake, which the director ruled out."""
    record = _record(_item(1, "supplier"), _item(2, "supplier"), _item(3, "world"))
    assert any("unblocks" in p for p in direction.focus_balance_problems(record))


def test_an_item_with_no_side_is_refused():
    """Fires on: a missing side counted as nothing, so an unlabelled focus slips the count."""
    record = _record(_item(1, "supplier"), _item(2, "supplier"), {"id": "x", "why": "y"})
    assert any("needs a side" in p for p in direction.focus_balance_problems(record))


def test_the_rule_binds_the_WRITE_and_a_record_on_file_stays_readable_by_the_draw():
    """Fires on: the balance check moved into `validate`, where a record written before this rule
    -- every record on file today -- would read as None and strip every draw of its focus."""
    old = {"version": 1, "oriented_at": "2026-10-09T07:28:19+00:00", "thesis_read": "t",
           "stretch_reviewed": {"since": "s", "commits": 1, "substantive": 1},
           "focus": [{"id": "a", "what": "w", "why": "y"}],
           "not_now": [{"what": "n", "why": "y"}], "wrong": [], "for_the_director": []}
    assert direction.focus_balance_problems(old), "the old record must break the new rule ..."
    assert not any("side" in p or "supplier item" in p for p in direction.validate(old)), (
        "... and validate, which the draw reads through, must not refuse it for that")


def test_a_commit_is_sided_by_ALL_its_paths_and_both_is_not_counted_twice():
    """Fires on: a supplier path hidden behind a dozen other paths being missed, or a commit that
    touches both sides being counted once for each."""
    assert seat.commit_side(["docs/a.md"] * 12 + ["company/billing/x.py"]) == "supplier"
    assert seat.commit_side(["sim/a.py", "saas/b.py"]) == "both"
    assert seat.commit_side(["simulation/run_phase2b.py"]) == "world"
    assert seat.commit_side(["tests/company/x.py", "background/y.py"]) == "other"
    split = seat.commit_split([{"side": "both"}, {"side": "world"}, {"side": "supplier"}, {}])
    assert split == {"supplier": 1, "world": 1, "both": 1, "other": 1}


def test_every_stretch_entry_carries_the_split():
    """Fires on: the split computed and recorded but never rendered where the director reads it."""
    row = {"at": "t", "commits": 3, "substantive": 2, "since": "s", "outcome": "oriented",
           "thesis_read": "A reading. More.",
           "commit_split": {"supplier": 2, "world": 5, "both": 1, "other": 9}}
    line = "2 supplier, 5 world, 1 both, 9 other"
    assert line in seat.stretch_entry_from_row(row)[1]
    assert line in seat.skipped_entry_from_row(row)[1]


def test_the_seat_REFUSES_an_unbalanced_record_at_the_write():
    """Fires on: the balance rule existing and tested while the seat's write never applies it --
    every control above green and the next orientation filed with no supplier item at all."""
    record = {"version": 1, "oriented_at": "2026-10-10T09:00:00+00:00", "thesis_read": "t",
              "stretch_reviewed": {"since": "s", "commits": 1, "substantive": 1},
              "focus": [{"id": "a", "what": "w", "why": "y", "side": "world", "unblocks": "x"}],
              "not_now": [{"what": "n", "why": "y"}], "wrong": [], "for_the_director": []}
    problems = seat.write_time_problems(record, record)
    assert any("supplier item" in p for p in problems)


def test_orient_CALLS_the_write_time_check():
    """Fires on: `orient` refusing by its own inline list again, so the check above tests a
    function the seat no longer reaches. An AST call, not a string: a comment cannot satisfy it."""
    import ast
    import inspect
    import textwrap
    tree = ast.parse(textwrap.dedent(inspect.getsource(seat.orient)))
    calls = {n.func.id for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "write_time_problems" in calls
