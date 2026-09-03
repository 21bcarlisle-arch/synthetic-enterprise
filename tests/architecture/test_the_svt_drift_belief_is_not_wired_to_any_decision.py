"""A belief that cannot be told from chance may be RECORDED and GRADED, never ACTED ON.

REUSE: tests/architecture/test_the_svt_drift_belief_is_not_wired_to_any_decision.py
CLASS: CUSTOM
INDEX: searched "reachability", "decision surface", "not a target", "diagnostic", "belief",
       "wired", "churn". `tests/company/test_carbon_not_a_target.py` is the nearest organ and its
       import-graph helpers are IMPORTED here rather than re-written -- `_import_edges`,
       `_production_files`, `_module_name`. It is not extended in place because its subject is a
       CONSTRAINT ON A WHOLE LEDGER reached by any import chain, and deny-by-default at module
       granularity is right for that: nothing may touch carbon. This subject is one FUNCTION inside
       `company/crm/churn_desk.py`, a module whose other estimators decision surfaces legitimately
       call every day. Module-level reachability would red on every importer of the churn desk and
       be turned off within a week. So the granularity here is the SYMBOL, and that difference is
       the whole reason for a second file.
       `tests/architecture/test_a_cited_constant_has_a_caller.py` was read and is the OPPOSITE
       claim -- it requires a caller to exist; this requires callers to stay inside a named set.

WHY THIS EXISTS, AND IT REPLACES AN ARGUMENT I MADE
---------------------------------------------------
`docs/staging/WORKER_PREREGISTRATION_WHAT_THE_SVT_DRIFT_BELIEF_MUST_SHOW_2026-08-31.md` pre-
registered a withdrawal condition: if P1 is refuted and the mean error is large, revert, because a
wrong belief invites action and an absent one does not.

P1 WAS REFUTED. `company.crm.churn_desk.estimate_svt_drift` reads 0.6054 uncorrected and 0.4691 per
exposure-day -- inside its null of [0.4164, 0.5834] -- while the world's own ceiling on the same
1,266 decisions still clears at 0.6091. There is per-household signal on the SVT route and this
belief finds none of it; what it orders is how long the cap period ran.

The belief was KEPT anyway, on the argument that the mean error is small (0.6pp) and that nothing
consumes the number. That argument is probably right and it is still only an argument, made by the
same session that wanted the belief to survive. So it is replaced by this control: the number may
be recorded beside the decision and graded against the outcome, and it may not reach anything that
decides. If someone wires it, this reds and names the result.

KEYED TO THE NULL, NOT TO TODAY'S ANSWER
----------------------------------------
The strictness is read from the instrument's own artefact at run time, not hard-coded. While the
belief's per-exposure-day reading sits inside its null, the allowlist is closed. If a later version
of the belief CLEARS that null, this control says so and stops forbidding the wiring -- because at
that point acting on it is a decision to argue about on its merits, not a category error.

That direction matters and it is the direction this project keeps getting wrong: a control pinned
to "estimate_svt_drift must never be called" would go green when the belief was deleted and stay
red when the belief got good. This one tracks the claim.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent.parent

#: WHERE A REFERENCE TO THIS BELIEF COULD LIVE. Deliberately WIDER than the carbon guard's decision
#: tree, and `tools` is the difference. That guard declares `tools/` out of subject because
#: publishing a carbon figure is the point of the mission metric -- and its own declaration says
#: the honest limit out loud: *"a decision surface implemented in tools/ would escape this guard"*.
#: Here the grading instrument IS in `tools/`, so the root has to be in subject or the one module
#: that legitimately reads the belief could not be told from a decision surface hiding beside it.
#: `site` is in for the same reason: a belief that reaches a rendered page has reached a reader.
SCAN_ROOTS = ("company", "saas", "simulation", "background", "tools", "site")

#: The belief under guard, by the two names it can be reached through: the function itself and the
#: field the run stamps. Either one appearing in a module is a reference to this belief.
BELIEF_SYMBOLS = ("estimate_svt_drift", "company_svt_drift_estimate")

#: The artefact carrying the belief's own graded reading. The guard's strictness comes from here.
ARTEFACT = PROJECT / "docs" / "reports" / "ladder_churn_ceiling_vs_belief.json"

#: WHERE THE BELIEF IS ALLOWED TO APPEAR, each with the reason it is not a decision.
#:
#: Deny-by-default: a module not on this list that names either symbol fails, and the failure asks
#: for a reason rather than an addition. Recording and grading are the two legitimate uses and both
#: are named; a third one is the thing this control exists to catch.
DECLARED = {
    "company/crm/churn_desk.py": (
        "the belief's own definition -- it computes the number and consumes nothing"
    ),
    "company/interfaces/churn_estimation.py": (
        "the seam that re-exports it. A pass-through with no logic: it decides nothing and is the "
        "declared door rather than a second one"
    ),
    "simulation/run_phase2b.py": (
        "the RECORDING site. Computed after `_svt_p_depart` and after the roll, stamped on the "
        "event and never read back -- which "
        "`test_the_recording_site_writes_the_belief_and_never_reads_it` checks rather than trusts"
    ),
    "tools/generate_value_arms_data.py": (
        "the PUBLISHING site. It reads the grading instrument's artefact and renders the reading "
        "to /capabilities/ beside the ceiling and the null; it consumes the number into no "
        "decision and nothing downstream reads its output back. Publishing a refusal is as much "
        "the opposite of acting on it as measuring one -- and the block this feeds exists "
        "precisely to put a belief that reads INSIDE ITS NULL in front of a reader as such"
    ),
    "tools/measure_churn_heterogeneity.py": (
        "the GRADING instrument. It scores the belief against the outcome and publishes the "
        "refusal; measuring a belief is the opposite of acting on it"
    ),
}


#: Declared sites that MAY legitimately not exist yet, each with the reason they are pending.
#:
#: THIS EXISTS BECAUSE THE GUARD READS THE WORKING TREE AND THE GATE GRADES HEAD, and on
#: 2026-08-31 those two trees genuinely disagreed about this file. `run_phase2b`'s C1b branch —
#: which stamps the belief on every SVT decision — sat uncommitted in the shared tree carrying
#: twelve reds of its own, so it could not land beside this control. Without this set the guard is
#: red in exactly one of the two trees whatever I choose: undeclared reds in the working tree
#: (where the reference exists), declared reds at HEAD (where it does not).
#:
#: It is NOT a hole. A pending entry still may not be a decision surface — it is exempt only from
#: "a declaration must have a subject", never from the deny-by-default check above, which is what
#: `test_a_pending_declaration_is_still_forbidden_from_deciding` pins.
PENDING_DECLARATIONS = {
    "simulation/run_phase2b.py": (
        "the C1b SVT route was uncommitted in the shared tree when this guard landed, so at HEAD "
        "nothing stamps the belief yet. Remove from this set once the recording site lands."
    ),
}


def _belief_clears_its_null() -> bool:
    """Read the belief's own per-exposure-day verdict out of the published artefact.

    A missing or unreadable artefact returns False -- the STRICT direction. An unavailable check is
    a failed check, and the safe failure here is "keep the belief away from decisions", not "assume
    it got good while nobody was looking".
    """
    try:
        report = json.loads(ARTEFACT.read_text())
    except (OSError, ValueError):
        return False
    svt = report.get("per_route", {}).get("svt_segment", {})
    for belief in svt.get("company_belief", []):
        if belief.get("field") != "company_svt_drift_estimate":
            continue
        offset = belief.get("exposure_offset")
        if not offset:
            return False
        return bool(offset.get("clears_the_null"))
    return False


def _scanned_files() -> tuple[Path, ...]:
    """Every production module under `SCAN_ROOTS`. Deny-by-default needs the whole population."""
    files = []
    for root in SCAN_ROOTS:
        directory = PROJECT / root
        if not directory.is_dir():
            continue
        files.extend(
            p for p in sorted(directory.rglob("*.py")) if "__pycache__" not in p.parts
        )
    return tuple(files)


def test_the_scanned_population_covers_every_root():
    """A root that silently resolves to nothing would make the guard pass by scanning air."""
    by_root = {
        root: sum(1 for p in _scanned_files() if p.is_relative_to(PROJECT / root))
        for root in SCAN_ROOTS
    }
    empty = [root for root, n in by_root.items() if n == 0]
    assert not empty, f"these declared scan roots matched no files: {empty}"


def _modules_naming_the_belief() -> dict[str, set[str]]:
    """Every production module that names either belief symbol, and which ones it names.

    AST-based, not a grep: a symbol inside a string or a comment is not a reference, and this
    control must not be satisfiable by renaming a variable in a docstring.
    """
    found: dict[str, set[str]] = {}
    for path in _scanned_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in BELIEF_SYMBOLS:
                names.add(node.id)
            elif isinstance(node, ast.FunctionDef) and node.name in BELIEF_SYMBOLS:
                # The DEFINITION is a reference too. Without this the detector missed the belief in
                # its own defining module and reported it as measuring something — caught by
                # `test_the_detector_finds_the_belief_where_it_is_known_to_live` on the first run,
                # which is what that test is for.
                names.add(node.name)
            elif isinstance(node, ast.Attribute) and node.attr in BELIEF_SYMBOLS:
                names.add(node.attr)
            elif isinstance(node, ast.alias) and node.name in BELIEF_SYMBOLS:
                names.add(node.name)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                # A dict KEY is how the field is written and read, so string constants count --
                # but only for the field name, never for the function.
                if node.value == "company_svt_drift_estimate":
                    names.add(node.value)
        if names:
            found[str(path.relative_to(PROJECT))] = names
    return found


def test_the_detector_finds_the_belief_where_it_is_known_to_live():
    """The subject set must be non-empty, or every assertion below is vacuously true."""
    found = _modules_naming_the_belief()
    assert "company/crm/churn_desk.py" in found, (
        "the detector cannot find the belief in its own defining module: it is measuring nothing"
    )
    assert "tools/measure_churn_heterogeneity.py" in found, (
        "the detector cannot find the grading instrument, which references the belief by BOTH "
        "names -- so it would not have seen a decision site either"
    )
    # ANCHORED ON TWO ROOTS, NOT ON THE RECORDING SITE. It asserted `simulation/run_phase2b.py`
    # was found, which is true in the working tree and false at HEAD while the C1b route stays
    # uncommitted -- and `surgical_land`, which gates the tree the commit WOULD create, caught it.
    # The durable property is that the scan reaches more than one root and finds the belief under
    # both of the names it can be referenced by.
    roots = {module.split("/", 1)[0] for module in found}
    assert len(roots) >= 2, f"the detector only reached one root ({roots}); the scan is too narrow"
    assert {n for names in found.values() for n in names} == set(BELIEF_SYMBOLS), (
        "the detector never matched one of the two names the belief can be referenced by, so half "
        "of it is unwatched"
    )


def test_no_undeclared_module_names_the_svt_drift_belief():
    """Deny-by-default. A new reference is a decision to justify, not a line to add quietly."""
    if _belief_clears_its_null():
        pytest.skip(
            "the belief now clears its null after the exposure offset; wiring it to a decision is "
            "an argument on the merits rather than a category error, and this guard stands down. "
            "Re-read the artefact's `exposure_offset` before removing anything here."
        )
    undeclared = {
        module: sorted(names)
        for module, names in _modules_naming_the_belief().items()
        if module not in DECLARED
    }
    assert not undeclared, (
        "these modules reference a belief that reads INSIDE ITS NULL after the exposure offset "
        f"(0.4691 against [0.4164, 0.5834], ceiling 0.6091 on the same rows): {undeclared}. It may "
        "be recorded and graded; it may not reach anything that decides. If this is a decision "
        "surface, the belief is not fit to feed it yet -- see the pre-registration's result "
        "section. If it is another recording or grading site, declare it in DECLARED with its "
        "reason."
    )


def test_the_recording_site_writes_the_belief_and_never_reads_it():
    """The claim that the number reaches no hazard, CHECKED rather than asserted in a comment.

    `run_phase2b` computes the belief after the roll and stamps it on the event. If it were ever
    read back -- into a hazard, a cap, a selection -- the belief would be seeding the outcome it is
    graded against, which is exactly the tautology that makes the renewal leg's 0.6815 unquotable.
    """
    # Scanned ONCE. Calling `_modules_naming_the_belief()` inside the comprehension re-parsed the
    # whole tree per file and turned a 5-second control into a multi-minute one.
    named = _modules_naming_the_belief()
    recording_sites = [
        PROJECT / module for module, names in sorted(named.items())
        if "company_svt_drift_estimate" in names and not module.endswith("churn_desk.py")
    ]
    if not recording_sites:
        pytest.skip(
            "nothing stamps `company_svt_drift_estimate` on a decision yet — the C1b recording "
            "site in `run_phase2b` is not committed. There is no write to check, and asserting "
            "over an absent file would be a control passing because its subject is missing."
        )
    tree = ast.parse(recording_sites[0].read_text(encoding="utf-8"))
    reads = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Subscript)
        and isinstance(node.slice, ast.Constant)
        and node.slice.value == "company_svt_drift_estimate"
    ]
    assert not reads, (
        "`company_svt_drift_estimate` is READ BACK in the recording site. A belief the world reads "
        "is a belief that seeds its own grade."
    )
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "estimate_svt_drift"
    ]
    assert len(calls) == 1, (
        f"the belief is computed {len(calls)} times in the recording site; exactly one call, "
        "stamped on the event, is what makes it gradable"
    )


def test_every_declaration_names_a_file_that_exists_and_still_refers_to_the_belief():
    """A stale allowlist entry is a hole nobody is watching."""
    found = _modules_naming_the_belief()
    for module, reason in DECLARED.items():
        assert (PROJECT / module).exists(), f"declared module {module} does not exist"
        assert reason.strip(), f"{module} is declared without a reason"
        if module in PENDING_DECLARATIONS:
            continue
        assert module in found, (
            f"{module} is declared as a place the belief may appear, and it no longer refers to "
            "the belief at all. Remove the declaration: an allowlist entry with no subject widens "
            "the guard for free."
        )


def test_every_pending_declaration_is_declared_and_carries_a_reason():
    """A pending entry must be a real declaration, not a way to name any file at all."""
    for module, reason in PENDING_DECLARATIONS.items():
        assert module in DECLARED, f"{module} is pending but not declared"
        assert reason.strip(), f"{module} is pending without a reason"


def test_a_pending_declaration_is_still_forbidden_from_deciding():
    """Pending exempts a file from needing a subject. It does NOT exempt it from the guard.

    Without this, `PENDING_DECLARATIONS` would be a way to name a decision surface and have the
    deny-by-default check wave it through -- an allowlist growing a second, quieter allowlist.
    """
    for module in PENDING_DECLARATIONS:
        reason = DECLARED[module]
        assert "RECORDING" in reason or "GRADING" in reason or "re-exports" in reason, (
            f"{module} is pending, and its declaration does not say it is a recording or grading "
            f"site: {reason!r}. Only those two uses are legitimate."
        )


def test_the_guard_is_keyed_to_the_null_and_not_to_a_pinned_number(monkeypatch):
    """Both branches are reachable — or the strictness is a constant wearing a condition.

    The failure this pins is the one this project keeps paying for: a control that reads a verdict
    but would behave identically whatever the verdict said.
    """
    monkeypatch.setattr(
        __import__(__name__.rsplit(".", 1)[0] if "." in __name__ else __name__, fromlist=["x"]),
        "_belief_clears_its_null",
        lambda: True,
        raising=False,
    )
    assert _belief_clears_its_null() in (True, False)
    # The artefact really is the source: a belief block with a CLEARING offset must read True.
    payload = {
        "per_route": {"svt_segment": {"company_belief": [
            {"field": "company_svt_drift_estimate",
             "exposure_offset": {"clears_the_null": True}},
        ]}}
    }
    tmp = PROJECT / "docs" / "reports" / ".tmp_svt_guard_probe.json"
    try:
        tmp.write_text(json.dumps(payload))
        monkeypatch.setattr(__import__("tests.architecture."
                                       "test_the_svt_drift_belief_is_not_wired_to_any_decision",
                                       fromlist=["ARTEFACT"]), "ARTEFACT", tmp)
        assert _belief_clears_its_null() is True
        payload["per_route"]["svt_segment"]["company_belief"][0][
            "exposure_offset"]["clears_the_null"] = False
        tmp.write_text(json.dumps(payload))
        assert _belief_clears_its_null() is False
    finally:
        tmp.unlink(missing_ok=True)


def test_an_unreadable_artefact_fails_CLOSED(monkeypatch):
    """No artefact must mean "keep it away from decisions", never "assume it got good"."""
    missing = PROJECT / "docs" / "reports" / ".no_such_artefact_here.json"
    monkeypatch.setattr(__import__("tests.architecture."
                                   "test_the_svt_drift_belief_is_not_wired_to_any_decision",
                                   fromlist=["ARTEFACT"]), "ARTEFACT", missing)
    assert _belief_clears_its_null() is False
