"""R15 falsifiers for `tools/symbol_landing_check.py` -- the control must be able to FAIL.

The subject: a commit that lands a CONSUMER of a first-party symbol and leaves its
SUPPLIER uncommitted. `19d8f94da` did exactly that and wedged publishing for ~6,923
minutes across 229 consecutive gate failures, while every tree anyone looked at stayed
green (`WORKER_FINDING_A_PATHSPEC_COMMIT_LANDED_THE_CONSUMER_AND_LEFT_THE_SUPPLIER_STAGED_
2026-08-14`).

The three killer patterns from R15, each with a test below that would go green if the
control stopped working:

  TAUTOLOGY   -> `test_it_judges_the_tree_and_not_the_working_tree`. `atom_name` exists in
                 today's working tree and at today's HEAD. The control must still red on
                 the tree where it did not exist -- if it ever resolves against the
                 running process, this test goes green and the control is worthless.
  FAIL-OPEN   -> `test_an_unparseable_module_is_a_finding_not_a_skip`,
                 `test_a_missing_module_is_a_finding`.
  FAIL-SILENT -> `test_the_gate_step_refuses_when_the_checker_is_unavailable`.

Plus the measured false-positive shapes. Those are not decoration: the first draft of
this control red on 10 of 80 real commits, all noise, and the fix (bind a module alias
only when the imported name IS a module) took it to 1 of 80 -- the true positive. Each
noise shape that fix killed is pinned below, because a later "simplification" that
re-broke any of them would restore a 12.5% false-positive rate and the gate would be
turned off within a day.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import symbol_landing_check as slc  # noqa: E402

# The commit that caused the wedge, and its two real call sites. Read from real history,
# not reconstructed: `git show 19d8f94da:tools/simplifications_store.py | grep -c
# "def atom_name"` is 0, and both files below call `_store.atom_name(...)` in that tree.
WEDGE_COMMIT = "19d8f94da"


def _env():
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _repo(tmp_path: Path, files: dict[str, str]) -> tuple[Path, str]:
    """A throwaway repo containing `files`, returning (root, tree-sha).

    A throwaway repo, not this one: building trees in the shared tree's real index to
    prove a point is the kind of test that becomes an incident.
    """
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=_env())
    for rel, body in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=_env())
    tree = subprocess.run(["git", "write-tree"], cwd=repo, check=True, capture_output=True,
                          text=True, env=_env()).stdout.strip()
    return repo, tree


def _findings(tmp_path: Path, files: dict[str, str]) -> list[slc.Finding]:
    repo, tree = _repo(tmp_path, files)
    found, _ = slc.check_tree(tree, root=repo)
    return found


# --------------------------------------------------------------- the real-history proof


def test_the_commit_that_caused_the_wedge_goes_red():
    """THE falsifier: real history, real commit, both real call sites.

    This is the whole justification for the control. If this test ever passes without
    findings, the control cannot catch the defect it was built for and should be deleted
    rather than trusted.
    """
    findings, _ = slc.run_at_tree(f"{WEDGE_COMMIT}^{{tree}}", f"{WEDGE_COMMIT}^^{{tree}}")
    assert len(findings) == 2, f"expected exactly the two known call sites, got: {findings}"
    assert all("simplifications_store.atom_name" in f for f in findings)
    assert any("test_publish_gate_subject_is_head.py:1326" in f for f in findings)
    assert any("test_maturity_map_facets.py:603" in f for f in findings)


def test_it_judges_the_tree_and_not_the_working_tree():
    """TAUTOLOGY KILLER. `atom_name` exists RIGHT NOW, on disk and at HEAD.

    A resolver that consulted the working tree, `sys.modules`, or an import would find it
    and return green on the tree where it genuinely did not exist. That is the exact
    mechanism by which the original defect survived every control in the repo, so it is
    asserted here from both ends.
    """
    from tools import simplifications_store
    assert hasattr(simplifications_store, "atom_name"), (
        "precondition: the symbol IS importable in this process today"
    )
    assert "def atom_name" in (ROOT / "tools" / "simplifications_store.py").read_text(), (
        "precondition: and it IS present in the working tree today"
    )

    findings, _ = slc.run_at_tree(f"{WEDGE_COMMIT}^{{tree}}", f"{WEDGE_COMMIT}^^{{tree}}")
    assert any("atom_name" in f for f in findings), (
        "the control resolved against the process or the working tree, not the tree under "
        "judgement -- it is a tautology and proves nothing"
    )


def test_the_same_reference_resolves_once_the_supplier_landed():
    """The other direction: at today's HEAD the repaired tree is green on that symbol.

    A control that reds on everything is as useless as one that reds on nothing. `c78b7a118`
    is the commit that actually landed the supplier.
    """
    findings, _ = slc.check_tree("HEAD^{tree}")
    assert not [f for f in findings if f.symbol == "atom_name"], (
        f"atom_name should resolve at HEAD now that the supplier landed: {findings}"
    )


# ------------------------------------------------------------------ fail-open falsifiers


def test_a_missing_attribute_is_a_finding(tmp_path):
    """MUTATION, both ways round, on a tree built for the purpose."""
    consumer = "from tools import supplier as s\n\ndef go():\n    return s.landed()\n"
    broken = _findings(tmp_path / "a", {
        "tools/supplier.py": "def something_else():\n    return 1\n",
        "tools/consumer.py": consumer,
    })
    assert len(broken) == 1
    assert broken[0].kind == "missing-attribute"
    assert broken[0].symbol == "landed"

    whole = _findings(tmp_path / "b", {
        "tools/supplier.py": "def landed():\n    return 1\n",
        "tools/consumer.py": consumer,
    })
    assert whole == [], f"the supplier landed; nothing should red: {whole}"


def test_a_missing_module_is_a_finding(tmp_path):
    findings = _findings(tmp_path, {
        "tools/consumer.py": "from background.never_committed import thing\n",
    })
    assert len(findings) == 1
    assert findings[0].kind == "missing-module"
    assert findings[0].module == "background.never_committed"


def test_an_unparseable_module_is_a_finding_not_a_skip(tmp_path):
    """FAIL-OPEN KILLER. The tempting shape is `except SyntaxError: continue`.

    A module that will not parse is one whose references are UNKNOWN, and unknown is a
    finding, not a pass -- otherwise the cheapest way to defeat this gate is to commit a
    file that does not compile.
    """
    findings = _findings(tmp_path, {"tools/broken.py": "def (((\n"})
    assert len(findings) == 1
    assert findings[0].kind == "unparseable"
    assert "tools/broken.py" in str(findings[0])


def test_a_checker_error_propagates_rather_than_returning_green(tmp_path):
    """A resolver that cannot read its tree must RAISE. The gate step turns that into a
    refusal; swallowing it here would make the gate pass on every broken invocation."""
    repo, _ = _repo(tmp_path, {"tools/a.py": "x = 1\n"})
    with pytest.raises(slc.CheckerError):
        slc.check_tree("not-a-real-tree-sha", root=repo)


# ------------------------------------------------- the measured false-positive shapes


def test_an_enum_member_access_is_not_a_finding(tmp_path):
    """THE MEASURED NOISE FLOOR, and the reason the first draft was unusable.

    `from company.regulatory.compliance_scorecard import ComplianceDomain` binds a CLASS.
    Reading `ComplianceDomain.ENERGY` off it is an enum member access, not a module
    attribute, and the first draft reported every one of them as a missing module -- 10
    of 80 real commits red, all noise. If this test goes red again, the gate's
    false-positive rate returns to 12.5% and it will be switched off.
    """
    findings = _findings(tmp_path, {
        "tools/scorecard.py": "import enum\n\nclass Domain(enum.Enum):\n    ENERGY = 1\n",
        "tools/consumer.py": (
            "from tools.scorecard import Domain\n\n"
            "def go():\n    return Domain.ENERGY\n"
        ),
    })
    assert findings == [], f"an enum member access is not a module reference: {findings}"


def test_a_module_dunder_is_not_a_finding(tmp_path):
    """`mod.__file__` is supplied by the import machinery, never by a blob. The first
    real-history run produced three of these beside its two true positives."""
    findings = _findings(tmp_path, {
        "tools/supplier.py": "x = 1\n",
        "tools/consumer.py": (
            "from tools import supplier\n\ndef go():\n    return supplier.__file__\n"
        ),
    })
    assert findings == []


def test_an_attribute_this_file_assigns_is_not_a_finding(tmp_path):
    """The monkeypatch shape. `mod.thing = ...` CREATES the attribute; reading it back is
    legitimate and extremely common in this repo's tests."""
    findings = _findings(tmp_path, {
        "tools/supplier.py": "x = 1\n",
        "tools/consumer.py": (
            "from tools import supplier\n\n"
            "def go():\n    supplier.injected = 5\n    return supplier.injected\n"
        ),
    })
    assert findings == []


def test_a_conditionally_bound_name_is_not_a_finding(tmp_path):
    """`try: from x import y / except ImportError: y = None` supplies `y`. Counting only
    unconditional top-level statements would red on the repo's own compatibility shims."""
    findings = _findings(tmp_path, {
        "tools/supplier.py": (
            "try:\n    from json import dumps as encode\nexcept ImportError:\n"
            "    encode = None\n"
        ),
        "tools/consumer.py": "from tools import supplier\n\ndef go():\n    return supplier.encode\n",
    })
    assert findings == []


def test_a_module_getattr_supplier_is_not_a_finding(tmp_path):
    """PEP 562: a module defining `__getattr__` can supply anything at runtime, so its
    attributes are unresolvable BY CONSTRUCTION. They are skipped and COUNTED, never
    silently dropped -- the report names the modules so the population stays visible."""
    repo, tree = _repo(tmp_path, {
        "tools/dynamic.py": "def __getattr__(name):\n    return 42\n",
        "tools/consumer.py": "from tools import dynamic\n\ndef go():\n    return dynamic.whatever\n",
    })
    findings, report = slc.check_tree(tree, root=repo)
    assert findings == []
    assert "tools.dynamic" in report["dynamic_modules"], (
        "a skipped population must be reported, not silently dropped"
    )


def test_a_submodule_import_is_not_a_finding(tmp_path):
    """`from pkg import submodule` resolves against the tree's module list, not against
    `pkg`'s top-level names."""
    findings = _findings(tmp_path, {
        "tools/pkg/__init__.py": "",
        "tools/pkg/leaf.py": "value = 1\n",
        "tools/consumer.py": "from tools.pkg import leaf\n\ndef go():\n    return leaf.value\n",
    })
    assert findings == []


def test_third_party_and_stdlib_references_are_out_of_scope(tmp_path):
    """Decided by NAME, never by an import attempt -- an import attempt would consult the
    running process, which is the tautology this control exists to avoid."""
    findings = _findings(tmp_path, {
        "tools/consumer.py": (
            "import json\nimport numpy as np\n\n"
            "def go():\n    return json.dumps(np.zeros(3))\n"
        ),
    })
    assert findings == []


# ----------------------------------------------------------------- the caller (R15 #3)


def test_the_gate_step_refuses_when_the_checker_is_unavailable(monkeypatch):
    """FAIL-SILENT KILLER. An unavailable check is a FAILED check.

    The sibling class one rung up (`THE_CLASS_CHECKER_HAS_NO_AUTOMATED_CALLER`) is what
    happens when nobody asserts this: a control that cannot run is permanently passing.
    """
    from tools import pre_commit_test_gate as gate

    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __import__

    def refuse(name, *a, **kw):
        if name == "tools.symbol_landing_check":
            raise ImportError("pretend it was deleted")
        return real_import(name, *a, **kw)

    monkeypatch.delitem(sys.modules, "tools.symbol_landing_check", raising=False)
    monkeypatch.setattr("builtins.__import__", refuse)
    ok, detail = gate._symbol_landing_check(["tools/whatever.py"])
    assert ok is False
    assert "UNAVAILABLE" in detail


def test_the_gate_step_is_skipped_for_a_pure_docs_commit():
    """It needs a staged `.py` to have a subject at all. A docs-only commit must not be
    refused by a check that has nothing to check."""
    from tools import pre_commit_test_gate as gate

    ok, detail = gate._symbol_landing_check(["docs/staging/SOMETHING.md"])
    assert ok is True and detail == ""


def test_the_gate_wires_this_step_before_the_pure_docs_early_return():
    """The commit that omits a supplier frequently selects NO test targets of its own, so
    a check living downstream of `if not targets: return 0` would never see it."""
    source = (ROOT / "tools" / "pre_commit_test_gate.py").read_text()
    call = source.index("_symbol_landing_check(staged)")
    early_return = source.index("return 0  # pure docs/data commit")
    assert call < early_return, (
        "the symbol-landing step must run BEFORE the pure-docs early return"
    )
