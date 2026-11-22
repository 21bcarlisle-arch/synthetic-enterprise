"""Every top-level key `run_phase2b` returns reaches the published book, or is dropped BY NAME.

The published `run_output_*.json` is `extract_report_data`'s reduction, and the reducer is a
whitelist. KNIFE3's debt-recovery records (1624411d2), B8's holdout by desk-year (775a3c46c) and the
dual household's riding-leg answers (c41e70832) were each built and tested at the producer, then
dropped by the whitelist for days, because a producer test that calls the run cannot tell a
published record from a dropped one. `test_a_run_level_record_the_runner_returns_is_actually_
published` guarded one naming shape; this guards every key.

A key passes by one of four routes, each read from the code that implements it:
  1. `extract_report_data` reads it off `phase2b` (`phase2b["k"]` or `phase2b.get("k")`);
  2. `run_phase4c_on_phase2b.main` lifts it to the top level under its own name and the reducer
     reads it off `run_output`;
  3. `tools/run_annual_report.WORLD_WALK_TRUTH_KEYS` writes it to the world-truth file;
  4. `annual_report.PHASE2B_KEYS_NOT_PUBLISHED` names it with a reason.

The producer's key set is derived STATICALLY from the dict `_main` returns (a run costs hours), and
never from a list kept here: a list would be updated by the same person who forgot the whitelist.
"""
from __future__ import annotations

import ast
from pathlib import Path

from saas.reporting import annual_report

ROOT = Path(__file__).resolve().parents[3]
PRODUCER = ROOT / "simulation" / "run_phase2b.py"
LIFTER = ROOT / "simulation" / "run_phase4c_on_phase2b.py"
REDUCER = ROOT / "saas" / "reporting" / "annual_report.py"
WORLD_TRUTH = ROOT / "tools" / "run_annual_report.py"


def _function(tree: ast.AST, name: str) -> ast.FunctionDef:
    found = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(found) == 1, f"expected one `def {name}`, found {len(found)}"
    return found[0]


def _own_nodes(fn: ast.FunctionDef):
    """Every node in `fn`'s own body, not descending into the functions it defines."""
    nested = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
    stack = [node for node in fn.body if not isinstance(node, nested)]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(child for child in ast.iter_child_nodes(node)
                     if not isinstance(child, nested))


def _assignments(fn: ast.FunctionDef) -> dict[str, list[ast.expr]]:
    out: dict[str, list[ast.expr]] = {}
    for node in _own_nodes(fn):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out.setdefault(target.id, []).append(node.value)
    return out


def _top_level_keys(expr: ast.expr, assigned: dict, seen: tuple = ()) -> set[str]:
    """Literal keys of the dict an expression builds, through `**name`, `|`, and `a if c else b`.

    Refuses anything it cannot resolve rather than skipping it: a key it cannot see is exactly
    the key this control exists to catch.
    """
    if isinstance(expr, ast.Dict):
        keys: set[str] = set()
        for key, value in zip(expr.keys, expr.values):
            if key is None:
                keys |= _top_level_keys(value, assigned, seen)
            elif isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.add(key.value)
            else:
                raise AssertionError(f"non-literal result key at line {key.lineno}")
        return keys
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.BitOr):
        return (_top_level_keys(expr.left, assigned, seen)
                | _top_level_keys(expr.right, assigned, seen))
    if isinstance(expr, ast.IfExp):
        return (_top_level_keys(expr.body, assigned, seen)
                | _top_level_keys(expr.orelse, assigned, seen))
    if isinstance(expr, ast.Name) and expr.id in assigned and expr.id not in seen:
        return set().union(*(_top_level_keys(v, assigned, seen + (expr.id,))
                             for v in assigned[expr.id]))
    raise AssertionError(f"cannot resolve the keys of {ast.unparse(expr)[:80]!r}")


def producer_keys(source: str) -> set[str]:
    """Every top-level key of the dict `run_phase2b._main` returns, and any `_result[k] = ...`."""
    fn = _function(ast.parse(source), "_main")
    returns = [n.value for n in _own_nodes(fn) if isinstance(n, ast.Return) and n.value is not None]
    assert returns, "_main returns nothing this control can read"
    assigned = _assignments(fn)
    keys: set[str] = set()
    for value in returns:
        keys |= _top_level_keys(value, assigned)
    for node in _own_nodes(fn):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)
                        and isinstance(target.slice, ast.Constant)
                        and target.value.id in {n.id for n in returns if isinstance(n, ast.Name)}):
                    keys.add(target.slice.value)
    return keys


def _reads(fn: ast.AST, var: str) -> set[str]:
    """Literal keys read off `var` by `var["k"]` or `var.get("k", ...)`."""
    keys: set[str] = set()
    for node in ast.walk(fn):
        if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name)
                and node.value.id == var and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)):
            keys.add(node.slice.value)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get" and isinstance(node.func.value, ast.Name)
                and node.func.value.id == var and node.args
                and isinstance(node.args[0], ast.Constant)):
            keys.add(node.args[0].value)
    return keys


def reducer_reads(source: str) -> tuple[set[str], set[str]]:
    """(keys read off `phase2b`, keys read off `run_output`) inside `extract_report_data`."""
    fn = _function(ast.parse(source), "extract_report_data")
    return _reads(fn, "phase2b"), _reads(fn, "run_output")


def lifted_keys(source: str) -> set[str]:
    """Keys `run_phase4c_on_phase2b.main` returns at top level as `"k": phase2b_result.get("k")`."""
    fn = _function(ast.parse(source), "main")
    keys: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            for key, value in zip(node.value.keys, node.value.values):
                if (isinstance(key, ast.Constant) and isinstance(value, (ast.Call, ast.Subscript))
                        and key.value in _reads(value, "phase2b_result")):
                    keys.add(key.value)
    return keys


def world_truth_keys(source: str) -> set[str]:
    for node in ast.walk(ast.parse(source)):
        if (isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "WORLD_WALK_TRUTH_KEYS"
                        for t in node.targets)):
            return {e.value for e in node.value.elts}
    raise AssertionError("WORLD_WALK_TRUTH_KEYS is gone from tools/run_annual_report.py")


def unaccounted(producer_src: str, reducer_src: str, dropped: dict[str, str]) -> list[str]:
    """Producer keys no route carries and no entry names."""
    via_phase2b, via_top = reducer_reads(reducer_src)
    lifted = lifted_keys(LIFTER.read_text()) & via_top
    carried = via_phase2b | lifted | world_truth_keys(WORLD_TRUTH.read_text()) | set(dropped)
    return sorted(producer_keys(producer_src) - carried)


def test_every_key_the_run_returns_is_forwarded_or_dropped_by_name():
    produced = producer_keys(PRODUCER.read_text())
    # Population floor: the run returned 114 top-level keys on 21 Nov 2026. A walk that finds a
    # handful has gone blind to the result's shape, and would pass vacuously.
    assert len(produced) >= 100, f"the producer walk found only {len(produced)} keys"
    missing = unaccounted(PRODUCER.read_text(), REDUCER.read_text(),
                          annual_report.PHASE2B_KEYS_NOT_PUBLISHED)
    assert not missing, (
        f"run_phase2b returns {missing} and nothing carries them to the published book: forward "
        "each in extract_report_data, or name it in PHASE2B_KEYS_NOT_PUBLISHED with its reason. "
        "Returned is not published; a grade that opens the book will find nothing.")


def test_every_dropped_key_has_a_reason_and_is_still_produced():
    """A stale entry hides nothing today but would excuse the key's return under a new meaning."""
    produced = producer_keys(PRODUCER.read_text())
    via_phase2b, _ = reducer_reads(REDUCER.read_text())
    for key, reason in annual_report.PHASE2B_KEYS_NOT_PUBLISHED.items():
        assert key in produced, f"{key!r} is named as dropped but the run no longer returns it"
        assert key not in via_phase2b, f"{key!r} is named as dropped and is also forwarded"
        assert len(reason.split()) >= 4, f"{key!r} is dropped without a reason"


def test_a_new_producer_key_turns_it_red():
    """Mutation one: the run grows a record and nobody touches the reducer."""
    src = PRODUCER.read_text()
    tree = ast.parse(src)
    grown = [node for node in _own_nodes(_function(tree, "_main")) if isinstance(node, ast.Dict)
             and any(isinstance(k, ast.Constant) and k.value == "all_records" for k in node.keys)]
    assert len(grown) == 1, f"the mutation anchor moved: {len(grown)} result dicts"
    grown[0].keys.append(ast.Constant("a_new_grading_record"))
    grown[0].values.append(ast.List(elts=[], ctx=ast.Load()))
    mutated = ast.unparse(tree)
    assert unaccounted(src, REDUCER.read_text(), annual_report.PHASE2B_KEYS_NOT_PUBLISHED) == []
    assert unaccounted(mutated, REDUCER.read_text(),
                       annual_report.PHASE2B_KEYS_NOT_PUBLISHED) == ["a_new_grading_record"]


def test_a_deleted_forward_turns_it_red():
    """Mutation two: a forward line is deleted from the reducer (the 1624411d2 shape)."""
    tree = ast.parse(REDUCER.read_text())
    removed = 0
    for node in ast.walk(_function(tree, "extract_report_data")):
        if isinstance(node, ast.Dict):
            pairs = [(k, v) for k, v in zip(node.keys, node.values)
                     if not (isinstance(k, ast.Constant) and k.value == "company_debt_recovery")]
            removed += len(node.keys) - len(pairs)
            node.keys, node.values = [k for k, _ in pairs], [v for _, v in pairs]
    assert removed == 1, f"the mutation anchor moved: {removed} forwards of company_debt_recovery"
    mutated = ast.unparse(tree)
    assert unaccounted(PRODUCER.read_text(), mutated,
                       annual_report.PHASE2B_KEYS_NOT_PUBLISHED) == ["company_debt_recovery"]


def test_each_route_carries_at_least_one_key():
    """Each of the four routes can be taken, so none of them is a blind spot that passes all."""
    produced = producer_keys(PRODUCER.read_text())
    via_phase2b, via_top = reducer_reads(REDUCER.read_text())
    assert produced & via_phase2b
    assert produced & (lifted_keys(LIFTER.read_text()) & via_top)
    assert produced & world_truth_keys(WORLD_TRUTH.read_text())
    assert produced & set(annual_report.PHASE2B_KEYS_NOT_PUBLISHED)
