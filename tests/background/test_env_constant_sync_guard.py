"""R15 both-directions proof for the H31 stale-env-constant class guard.

THE NAMED DEFECT. `tests/background/test_model_facing_secret_scrub.py` scrubbed the env,
`importlib.reload`ed `background.ntfy_utils` so `WAKE_HMAC_KEY` went None, then "restored" with a
second reload inside a `finally:` block. A `finally:` runs while the test function is still on the
stack; `monkeypatch` restores os.environ in a fixture FINALIZER that runs afterwards. So the
restoring reload re-read the STILL-SCRUBBED env, restored nothing, and left `WAKE_HMAC_KEY` None
for the rest of the process -- four `test_ntfy_utils.py` signing tests failed purely on collection
order, while the test that broke them stayed green.

R15 doctrine proven here, against all three killer patterns:
  * FIRES ON ITS OWN DEFECT -- the end-to-end test below RE-CREATES the original bug in a scratch
    suite outside the repo tree, runs pytest on it in a subprocess with the REAL guard wired in,
    and asserts the CULPRIT is failed and NAMED while the victim survives. A control run with the
    `monkeypatch.undo()` fix present is green. That is a mutation test of the live mechanism, not
    of a paraphrase of it.
  * NOT A TAUTOLOGY -- expected values come from `os.environ`, the module constants come from
    `sys.modules`. Two independent sources; the guard compares them rather than deriving one from
    the other.
  * NOT FAIL-OPEN / NOT VACUOUS -- `test_registry_is_not_vacuous` asserts the AST-derived registry
    is non-empty AND actually contains the constant from the original incident. A scanner that
    silently matched nothing would make every other assertion here pass while guarding nothing.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from tests.background import env_constant_sync as ecs

REPO_ROOT = Path(__file__).resolve().parents[2]


# ── the registry must not be vacuous ─────────────────────────────────────────────────────────
def test_registry_is_not_vacuous():
    """FAIL-OPEN guard: an AST scan that matches nothing passes every downstream assertion
    while guarding nothing at all. Pin both that it found constants and that it found THE one
    the H31 incident was about."""
    registry = ecs.build_registry()
    assert registry, "the env-constant scan found nothing -- the whole guard would be a no-op"
    dotted = {c.dotted for c in registry}
    assert "background.ntfy_utils.WAKE_HMAC_KEY" in dotted, sorted(dotted)
    wake = next(c for c in registry if c.dotted == "background.ntfy_utils.WAKE_HMAC_KEY")
    assert wake.env_var == "SE_WAKE_HMAC_KEY"


def test_registry_covers_every_grep_visible_env_constant():
    """Independence check on the scanner: a plain textual sweep of the same files must not find
    a top-level env-read assignment the AST scan missed. Guards against the scan quietly
    narrowing (e.g. a form it stops recognising) without anyone noticing."""
    import re

    pattern = re.compile(
        r"^([A-Za-z_][A-Za-z0-9_]*)(?:\s*:[^=]+)?\s*=\s*os\.(?:environ\.get|getenv|environ\[)"
    )
    found_by_grep = set()
    for path in sorted((REPO_ROOT / "background").glob("*.py")):
        if path.name == "__init__.py":
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            m = pattern.match(line)
            if m:
                found_by_grep.add(f"background.{path.stem}.{m.group(1)}")
    missed = found_by_grep - {c.dotted for c in ecs.build_registry()}
    assert not missed, f"AST scan missed env constants a grep can see: {sorted(missed)}"


# ── the scanner recognises the real forms, and refuses the ambiguous ones ─────────────────────
@pytest.mark.parametrize(
    "source,expect",
    [
        ('A = os.environ.get("X")', ("A", "X", None, False)),
        ('B = os.environ.get("X", "dflt")', ("B", "X", "dflt", False)),
        ('C: str | None = os.environ.get("X")', ("C", "X", None, False)),
        ('D = os.getenv("X")', ("D", "X", None, False)),
        ('E = os.getenv("X", "d")', ("E", "X", "d", False)),
        ('F = os.environ["X"]', ("F", "X", None, True)),
    ],
)
def test_scanner_recognises_direct_env_reads(tmp_path, source, expect):
    path = tmp_path / "m.py"
    path.write_text("import os\n" + source + "\n")
    found = ecs._scan_module_file(path, "pkg.m")
    assert len(found) == 1
    c = found[0]
    assert (c.attr, c.env_var, c.default, c.required) == expect


@pytest.mark.parametrize(
    "source",
    [
        'G = Path(os.environ.get("X"))',          # wrapped: expected value not recomputable
        'H = os.environ.get("X", COMPUTED)',      # non-literal default
        'def f():\n    I = os.environ.get("X")',  # not top-level: no import-time snapshot
        'J = os.environ.get(NAME)',               # non-literal var name
    ],
)
def test_scanner_refuses_forms_it_cannot_recompute(tmp_path, source):
    """Narrow-and-true beats broad-and-noisy: a guard that fires on honest code gets silenced."""
    path = tmp_path / "m.py"
    path.write_text("import os\nfrom pathlib import Path\nCOMPUTED='c'\nNAME='X'\n" + source + "\n")
    assert ecs._scan_module_file(path, "pkg.m") == []


# ── divergence detection: fires on the leak, silent when in sync ─────────────────────────────
class _FakeMod:
    pass


def _one_registry(default=None):
    return [ecs.EnvConstant("fake.mod", "KEY", "H31_FAKE_ENV", default, False)]


def test_diverged_is_silent_when_constant_matches_env(monkeypatch):
    monkeypatch.setenv("H31_FAKE_ENV", "value")
    mod = _FakeMod()
    mod.KEY = "value"
    assert ecs.diverged(_one_registry(), {"fake.mod": mod}) == []


def test_diverged_fires_on_the_exact_h31_leak(monkeypatch):
    """THE MUTATION: env holds the key, the module constant is None -- precisely the state the
    finally-reload left behind. The guard must see it."""
    monkeypatch.setenv("H31_FAKE_ENV", "value")
    mod = _FakeMod()
    mod.KEY = None  # leaked stale, as after a reload against a scrubbed env
    hits = ecs.diverged(_one_registry(), {"fake.mod": mod})
    assert len(hits) == 1
    const, actual, expected = hits[0]
    assert (const.dotted, actual, expected) == ("fake.mod.KEY", None, "value")


def test_diverged_ignores_modules_that_were_never_imported(monkeypatch):
    """An unimported module cannot have leaked, and importing it here to check would itself
    change session state."""
    monkeypatch.setenv("H31_FAKE_ENV", "value")
    assert ecs.diverged(_one_registry(), {}) == []


def test_repair_restores_the_fresh_import_value(monkeypatch):
    """Reporting without repairing leaves the cascade intact -- later tests would still inherit
    the stale value and stay collection-order dependent."""
    monkeypatch.setenv("H31_FAKE_ENV", "value")
    mod = _FakeMod()
    mod.KEY = None
    registry = _one_registry()
    ecs.repair(registry[0], {"fake.mod": mod})
    assert mod.KEY == "value"
    assert ecs.diverged(registry, {"fake.mod": mod}) == []


def test_describe_names_the_constant_the_env_var_and_the_fix():
    """R5: the failure carries its diagnostic payload, not just a red mark."""
    const = _one_registry()[0]
    text = ecs.describe(const, None, "value")
    assert "fake.mod.KEY" in text
    assert "H31_FAKE_ENV" in text
    assert "monkeypatch.undo()" in text
    assert "finally" in text


def test_describe_never_prints_the_secret_it_guards():
    """Every constant here is read from the environment, and in this repo those ARE the secrets:
    SE_WAKE_HMAC_KEY signs director-authority wake messages, SE_NTFY_TOPIC buzzes the director's
    phone. A guard whose failure message prints them verbatim writes live secrets into pytest
    output and CI logs -- it would leak precisely what the scrub it protects exists to prevent.
    Caught for real: the first mutation run printed the live SE_NTFY_TOPIC value."""
    const = _one_registry()[0]
    text = ecs.describe(const, "leaked-stale-secret", "the-real-signing-key")
    assert "the-real-signing-key" not in text
    assert "leaked-stale-secret" not in text
    assert "background.ntfy_utils.WAKE_HMAC_KEY" not in text  # sanity: fake const, not the real one


def test_redaction_keeps_values_distinguishable():
    """Redaction must not destroy the signal. The diagnosis is 'is it None / is it a DIFFERENT
    value', so distinct values must render distinctly and equal values identically."""
    assert ecs.redact("alpha") != ecs.redact("bravo")
    assert ecs.redact("alpha") == ecs.redact("alpha")
    assert ecs.redact(None) == "None"          # not a secret, and the commonest leaked value
    assert ecs.redact(True) == "True"
    assert "len=5" in ecs.redact("alpha")      # length survives: a truncation is still visible


# ── END-TO-END: the live hook, against the original bug, in a real pytest run ────────────────
_CULPRIT_SUITE = '''
import importlib, os
import background.ntfy_utils as nu

def test_culprit_leaks_the_wake_key(monkeypatch):
    monkeypatch.delenv("SE_WAKE_HMAC_KEY", raising=False)
    importlib.reload(nu)
    try:
        assert nu.WAKE_HMAC_KEY is None
    finally:
{restore}

def test_victim_needs_the_key():
    assert nu.WAKE_HMAC_KEY == "e2e-key", "victim saw a leaked stale constant"
'''

_BROKEN_RESTORE = "        importlib.reload(nu)  # H31 bug: env not yet restored"
_FIXED_RESTORE = "        monkeypatch.undo()\n        importlib.reload(nu)"

_SCRATCH_CONFTEST = '''
import sys
sys.path.insert(0, {repo!r})
import pytest
from tests.background import env_constant_sync as _env_sync

_REG = _env_sync.build_registry()
_BASE = {{c.dotted for c, _a, _e in _env_sync.diverged(_REG)}}

@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item, nextitem):
    bad = [(c, a, e) for c, a, e in _env_sync.diverged(_REG) if c.dotted not in _BASE]
    if not bad:
        return
    for c, _a, _e in bad:
        _env_sync.repair(c)
    pytest.fail("{{}}\\n\\n{{}}".format(
        item.nodeid, "\\n\\n".join(_env_sync.describe(c, a, e) for c, a, e in bad)),
        pytrace=False)
'''


def _run_scratch_suite(tmp_path: Path, restore: str) -> subprocess.CompletedProcess:
    """Run a two-test suite OUTSIDE the repo tree (so no repo conftest loads) with the REAL
    guard wired in, and report what pytest actually did."""
    tmp_path.joinpath("conftest.py").write_text(
        textwrap.dedent(_SCRATCH_CONFTEST).format(repo=str(REPO_ROOT))
    )
    tmp_path.joinpath("test_leak.py").write_text(_CULPRIT_SUITE.format(restore=restore))
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["SE_WAKE_HMAC_KEY"] = "e2e-key"
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:randomly", "-p", "no:cacheprovider", "-q"],
        cwd=str(tmp_path), env=env, capture_output=True, text=True, timeout=180,
    )


def test_guard_catches_the_real_bug_and_names_the_culprit(tmp_path):
    """MUTATION, end to end: reintroduce the finally-reload and assert the guard fails the
    CULPRIT by name. Without the guard this suite fails the VICTIM and lets the culprit pass --
    the exact misdirection that made H31 read as 'import order'."""
    result = _run_scratch_suite(tmp_path, _BROKEN_RESTORE)
    out = result.stdout + result.stderr
    assert result.returncode != 0, out
    assert "test_culprit_leaks_the_wake_key" in out, out
    assert "STALE ENV CONSTANT" in out, out
    assert "background.ntfy_utils.WAKE_HMAC_KEY" in out, out
    # and the repair worked: the victim did NOT inherit the stale None
    assert "victim saw a leaked stale constant" not in out, out


def test_guard_is_silent_when_the_fix_is_present(tmp_path):
    """The other direction -- a control that can only fail is worthless. With
    `monkeypatch.undo()` before the reload, the same suite is green and the guard says nothing."""
    result = _run_scratch_suite(tmp_path, _FIXED_RESTORE)
    out = result.stdout + result.stderr
    assert result.returncode == 0, out
    assert "STALE ENV CONSTANT" not in out, out
    assert "2 passed" in out, out
