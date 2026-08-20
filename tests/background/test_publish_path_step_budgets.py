"""R15 on the bounded STEPS INSIDE the publisher, not on the callers that wrap it.

THE DEFECT THIS PINS (observed 2026-08-20, three times, first at 16:37Z):

    docs/observability/background-worker-log.md
    [2026-08-20 16:37 UTC] TIMED OUT processing run_complete_20260820T090542Z.md after 5400s

That marker's gate had PASSED (`docs/observability/.last_tested_hash` = `43766e01e`, written by
`_run_gate_in` and only on rc=0) and its commit had LANDED (`cd4da3219`, live on
https://poesys.net/data/dashboard.json). The publisher was killed anyway, and a kill routes to
`record_publish_gate_failure(kind="deadline_kill")` -- so a green, published cycle was recorded
as the episode's next failure, `record_publish_gate_success` never ran for it, and the wedge it
would have cleared stayed armed. Three of the last four cycles died this way.

The arithmetic, which is the whole bug:

    PUBLISH_PATH_TIMEOUT_SECONDS = GATE_SUITE_TIMEOUT_SECONDS + PUBLISH_PATH_ALLOWANCE_SECONDS
                                 = 4500 + 900 = 5400

Inside that 5400s the path ran TWO suites bounded at 4500s: the blocking gate, and
`run_remainder_annotation_step` -- whose `_default_remainder_runner` passed
`timeout=GATE_SUITE_TIMEOUT_SECONDS`, five times the entire post-gate allowance it lives in.
The annotation's docstring says it "observes the publish it follows and must never be able to
affect it". It could not red the publish; it killed the process carrying it.

WHY THE CONTROL THAT EXISTED DID NOT CATCH IT.
`test_publisher_deadline_exceeds_its_gate.py` pins the CALLERS (background_worker, sim_runner)
and asserts `slack >= GIT_COMMIT_HOOK_TIMEOUT_SECONDS`. Both inequalities pass. Its docstring
enumerates what follows the gate -- "site regeneration, the report, the mirror, the hook-chain
commit and the push" -- and that enumeration is HAND-WRITTEN and incomplete: the largest
post-gate step is absent from it. The word `annotation` occurs once in that file, as
`from __future__ import annotations`. This is the project's own filed shape (R15 TAUTOLOGY's
cousin): a control whose subject set is an author's list rather than the population, passing
because the thing it does not know about is the thing that breaks it. The 2026-08-10 retro
generalised it once over call SITES; this generalises it over bounded STEPS inside one site.

SO THE POPULATION IS DERIVED, NEVER LISTED. `_publish_path_functions()` walks the call graph
from `main`, which is why `run_operational_layer_signal` (a real 1800s subprocess in this same
module, reached from `deadmans_switch`, NOT from the publish path) is correctly out of scope
while `_default_remainder_runner` -- referenced only as a bare name, never called by name -- is
correctly in it. A hand list would have had to get both of those right by hand, twice, forever.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from background import process_run_complete as prc

MODULE_PATH = Path(prc.__file__).resolve()


# ────────────────────────────────────────────── the derived population

def _module_functions(tree):
    return {n.name: n for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _publish_path_functions():
    """Every module-level function reachable from `main` -- the publish path, derived.

    Reachability is over NAME references, not over Call nodes: `run_remainder_annotation_step`
    invokes the runner as `(runner or _default_remainder_runner)(...)`, so a Call-only walk
    would not see the very function this file exists to bound. Over-approximating makes the
    control STRICTER (more steps in scope), never blinder -- the failure direction that
    matters here is missing a step, not catching an extra one.
    """
    tree = ast.parse(MODULE_PATH.read_text())
    funcs = _module_functions(tree)
    seen, stack = set(), ["main"]
    while stack:
        name = stack.pop()
        if name in seen or name not in funcs:
            continue
        seen.add(name)
        for node in ast.walk(funcs[name]):
            if isinstance(node, ast.Name):
                stack.append(node.id)
            elif isinstance(node, ast.Attribute):
                stack.append(node.attr)
    return {n: funcs[n] for n in seen}


def _timed_spawns():
    """(function, lineno, unparsed timeout expression) for every timed subprocess on the path."""
    out = []
    for name, func in sorted(_publish_path_functions().items()):
        for node in ast.walk(func):
            if not isinstance(node, ast.Call):
                continue
            callee = ast.dump(node.func)
            if "subprocess" not in callee and "Popen" not in callee:
                continue
            for kw in node.keywords:
                if kw.arg == "timeout":
                    out.append((name, node.lineno, ast.unparse(kw.value)))
    return out


# ────────────────────────────────────────────── vacuity guards (R15: a blind control is not one)

def test_the_call_graph_reaches_the_steps_it_claims_to_bound():
    """VACUITY GUARD, and not theoretical -- the sibling control in
    `test_publisher_deadline_exceeds_its_gate.py` shipped with a scan that matched NOTHING in
    either module and passed a deliberately mutated call site. An empty or shallow population
    is a BLIND control, never a clean bill of health."""
    path = _publish_path_functions()
    for anchor in ("_run_gate_in", "git_commit_push", "run_remainder_annotation_step",
                   "_default_remainder_runner", "run_red_census"):
        assert anchor in path, (
            "the publish-path walk lost `{}` -- it is no longer bounding the step it names, "
            "and would pass a mutation there".format(anchor))


def test_the_walk_excludes_what_is_not_on_the_publish_path():
    """The other half of the vacuity guard: a walk that returned EVERY function in the module
    would also contain the anchors above and look healthy, while asserting the 1800s
    operational-layer signal (reached from `deadmans_switch`, never from `main`) must fit a
    budget it has nothing to do with. A control that cannot be wrong about scope cannot be
    right about it either."""
    path = _publish_path_functions()
    assert "run_operational_layer_signal" not in path
    assert "_operational_layer_result_text" not in path


def test_the_scan_finds_the_timed_subprocesses():
    path_names = {name for name, _, _ in _timed_spawns()}
    assert {"_run_gate_in", "_default_remainder_runner"} <= path_names, (
        "the spawn scan cannot see the two steps whose relationship is the whole finding")


# ────────────────────────────────────────────── the invariant

def test_only_the_gate_itself_may_carry_the_gates_own_bound():
    """THE FINDING, as one inequality over the population.

    `GATE_SUITE_TIMEOUT_SECONDS` is affordable exactly once: `PUBLISH_PATH_TIMEOUT_SECONDS` is
    defined as that bound PLUS a 900s allowance for everything else. A second step claiming it
    is not a tight budget -- it is a promise the path cannot keep, and the caller resolves the
    contradiction with SIGKILL against a publish that already succeeded.

    MUTATION: restore `timeout=GATE_SUITE_TIMEOUT_SECONDS` in `_default_remainder_runner` and
    this reds, naming both claimants.
    NULL CONTROL: `test_removing_a_step_does_not_red_this` below -- a control that merely
    COUNTS is satisfied by deleting the step, so the count is pinned to the gate by NAME.
    """
    claimants = [(fn, line) for fn, line, expr in _timed_spawns()
                 if "GATE_SUITE_TIMEOUT_SECONDS" in expr]
    assert [fn for fn, _ in claimants] == ["_run_gate_in"], (
        "{} publish-path step(s) claim the gate's own bound ({}s) while the whole post-gate "
        "allowance is {}s: {}. Only the gate may spend the gate's budget; every other step "
        "must derive from what is LEFT (see `_remaining_path_budget_seconds`). This is the "
        "5400s deadline_kill of 2026-08-20 against a green, published cycle.".format(
            len(claimants), prc.GATE_SUITE_TIMEOUT_SECONDS,
            prc.PUBLISH_PATH_ALLOWANCE_SECONDS, claimants))


def test_no_publish_path_step_carries_a_static_bound_over_the_allowance():
    """The generalisation: a step need not name the gate's constant to overrun the path -- a
    bare `timeout=1800` does it just as well (and there IS an 1800 in this module, off-path).
    Every STATIC bound on the path must fit the post-gate allowance; anything that needs more
    must be DERIVED at runtime, which is what the gate and the census already do.

    MUTATION: add `timeout=1200` to any spawn reachable from `main` and this reds on arrival.
    """
    allowance = prc.PUBLISH_PATH_ALLOWANCE_SECONDS
    over = []
    for fn, line, expr in _timed_spawns():
        try:
            value = ast.literal_eval(expr)
        except (ValueError, SyntaxError):
            continue  # derived at runtime -- bounded by the primitive, not by a literal
        if fn == "_run_gate_in" or "GATE_SUITE_TIMEOUT_SECONDS" in expr:
            continue  # the gate's own bound, asserted by name in the test above
        if value > allowance:
            over.append((fn, line, value))
    assert not over, (
        "publish-path step(s) carry a static bound larger than the {}s the path allows after "
        "the gate: {}".format(allowance, over))


def test_deleting_the_step_cannot_pass_as_a_repair():
    """NULL CONTROL, and it did NOT land where the finding predicted -- recorded rather than
    quietly reshaped to match.

    The finding asked for "removing a bounded step must NOT red it", reasoning that a control
    which only COUNTS is satisfied by deletion. Both halves of that are worth having, and they
    turn out to want opposite things here, so this test pins each to the assertion that owns it:

      * THE INVARIANT DOES NOT MERELY COUNT. `test_only_the_gate_itself_may_carry_the_gates_own
        _bound` asserts the claimant list equals `["_run_gate_in"]` BY NAME. Delete the
        annotation and that assertion is still satisfied -- asserted below -- so it is not a
        counter dressed up as an invariant.
      * DELETION IS STILL NOT A REPAIR. The cheapest wrong fix for a step that overruns its
        budget is to delete the step; the vacuity guard reds on exactly that, because the
        population it needs to see has lost a member. Scope loss scoring GREEN is this
        project's own filed defect (a mutation can delete the subject instead of moving it) --
        so scoring it RED is the direction to keep, and the finding's phrasing of the null
        control is the part that was wrong.
    """
    trimmed = _source_with_step_removed("_default_remainder_runner")
    spawns = _timed_spawns_in(trimmed)

    claimants = [fn for fn, expr in spawns if "GATE_SUITE_TIMEOUT_SECONDS" in expr]
    assert claimants == ["_run_gate_in"], (
        "removing an unrelated step moved the invariant's own verdict -- it is counting "
        "claimants rather than naming the one step entitled to the gate's budget")

    assert "_default_remainder_runner" not in {fn for fn, _ in spawns}, (
        "the vacuity guard would not notice the deleted step, so deleting it would pass as a "
        "repair -- this is scope loss scoring green")


def _source_with_step_removed(func_name):
    """The module source with one bounded step's body replaced by a stub.

    BY AST POSITION, not by matching the spawn's source text: a null control that string-matches
    the very line the mutations rewrite cannot run under those mutations, and reports "I could
    not find my subject" as though it were a verdict. Excising by lineno keeps the null control
    answerable whatever the step's timeout expression currently says."""
    src = MODULE_PATH.read_text()
    lines = src.splitlines(keepends=True)
    for node in ast.parse(src).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            start = node.lineno - 1 + len(node.decorator_list)
            stub = "def {}(*_a, **_k):\n    return None\n".format(func_name)
            return "".join(lines[:start]) + stub + "".join(lines[node.end_lineno:])
    raise AssertionError(
        "the null control cannot find `{}` to remove -- it is asserting nothing".format(
            func_name))


def _timed_spawns_in(source):
    tree = ast.parse(source)
    funcs = _module_functions(tree)
    seen, stack = set(), ["main"]
    while stack:
        name = stack.pop()
        if name in seen or name not in funcs:
            continue
        seen.add(name)
        for node in ast.walk(funcs[name]):
            if isinstance(node, ast.Name):
                stack.append(node.id)
            elif isinstance(node, ast.Attribute):
                stack.append(node.attr)
    out = []
    for name in sorted(seen):
        for node in ast.walk(funcs[name]):
            if isinstance(node, ast.Call) and (
                    "subprocess" in ast.dump(node.func) or "Popen" in ast.dump(node.func)):
                out += [(name, ast.unparse(kw.value))
                        for kw in node.keywords if kw.arg == "timeout"]
    return out


# ────────────────────────────────────────────── the runtime arithmetic

def test_the_remainder_budget_is_what_the_path_has_left():
    """Spend 3000s of the path and the annotation may have the rest, not 4500s."""
    budget = prc.remainder_budget_seconds(now_monotonic=3000.0, started=0.0)
    expected = (prc.PUBLISH_PATH_TIMEOUT_SECONDS - 3000.0
                - prc.REMAINDER_PATH_MARGIN_SECONDS)
    assert budget == expected
    assert budget < prc.GATE_SUITE_TIMEOUT_SECONDS


def test_the_remainder_budget_never_outlives_the_publisher_itself():
    """THE PROPERTY, at every point in the path: finishing the annotation can never take the
    process past the deadline its caller enforces. At 4500s spent -- a gate that used its whole
    bound -- the old code still offered 4500s more."""
    for spent in (0.0, 600.0, 3000.0, 4500.0, 5200.0, 5400.0):
        budget = prc.remainder_budget_seconds(now_monotonic=spent, started=0.0)
        assert spent + budget <= prc.PUBLISH_PATH_TIMEOUT_SECONDS, (
            "at {}s spent the annotation may run {}s, ending {}s past the caller's {}s "
            "deadline -- this is the deadline_kill".format(
                spent, budget, spent + budget - prc.PUBLISH_PATH_TIMEOUT_SECONDS,
                prc.PUBLISH_PATH_TIMEOUT_SECONDS))


def test_an_exhausted_budget_skips_the_suite_rather_than_running_it_unbounded():
    """0 means DO NOT START. The old failure mode was to start anyway and be killed mid-run."""
    assert prc.remainder_budget_seconds(now_monotonic=5400.0, started=0.0) == 0.0
    with pytest.raises(RuntimeError, match="no budget left"):
        prc._default_remainder_runner(["pytest"], timeout=0)


def test_the_exhausted_skip_never_publishes_a_false_all_clear(monkeypatch, tmp_path):
    """FAIL-SILENT guard, and the reason the runner RAISES instead of returning rc=0: an empty
    red list reaches the live page as '0 non-blocking reds' next to a suite that never ran."""
    recorded = {}

    def _boom(_argv):
        raise RuntimeError("no budget left in the publish path's own deadline")

    monkeypatch.setattr(prc, "_open_findings_count", lambda: 7)
    monkeypatch.setattr(prc, "log", lambda *a, **k: None)
    state_file = tmp_path / "remainder.json"
    monkeypatch.setattr(prc, "REMAINDER_ANNOTATION_STATE_FILE", state_file)

    from background import publish_provenance as prov
    monkeypatch.setattr(prov, "record_annotation",
                        lambda **kw: recorded.update(kw) or dict(kw))

    prc.run_remainder_annotation_step("abc123", force=True, runner=_boom)

    assert "nonblocking_reds" not in recorded, (
        "a skipped annotation published a reds list -- an all-clear for a suite that never ran")
    assert not state_file.exists(), (
        "a skipped annotation wrote an annotation state, which the page reads as a result")


# ────────────────────────────────────────────── the shared primitive stayed shared

def test_the_census_and_the_remainder_share_one_definition():
    """SIMPLICITY GUARD as a test: two copies of this arithmetic is exactly how the annotation
    drifted from the census in the first place. Move the path's declared budget and BOTH must
    move -- a copy would hold its old answer."""
    original = prc.PUBLISH_PATH_TIMEOUT_SECONDS
    try:
        prc.PUBLISH_PATH_TIMEOUT_SECONDS = original + 1000
        # 2600s spent, so the REMAINING term binds rather than the cap -- at 1000s spent the
        # cap does, and the assertion would hold for a hard-coded 4500 too.
        assert prc.remainder_budget_seconds(now_monotonic=2600.0, started=0.0) == min(
            prc.GATE_SUITE_TIMEOUT_SECONDS,
            original + 1000 - 2600.0 - prc.REMAINDER_PATH_MARGIN_SECONDS)
        assert prc.red_census_budget_seconds(now_monotonic=1000.0, started=0.0) == min(
            prc.GATE_RED_CENSUS_MAX_SECONDS,
            original + 1000 - 1000.0 - prc.GATE_RED_CENSUS_PATH_MARGIN_SECONDS)
    finally:
        prc.PUBLISH_PATH_TIMEOUT_SECONDS = original
