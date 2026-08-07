"""Seat-guard tests for background/ daemons (background/_seat.py + the per-daemon guard).

WHY THIS EXISTS. The resident seat's daemon stack is brought up by the
ENVIRONMENT that hosts a session, not by the session itself -- the poesys cloud
environment starts it inside every session's freshly-cloned tree. A daemon
launched that way runs against a foreign checkout while keeping every bit of
the resident seat's authority: it commits, it pushes, it stamps observability
files, it drains the instruction channel. Issue #11 is the proven case -- a
liveness daemon sharing a foreign session's tree pushed main.

`.claude/hooks/` was guarded for this exact reason (tests/hooks/test_seat_guard.py).
`background/` is the other half, and it is the half holding push credentials.

This file proves, per R15 (a control must be able to FAIL), both directions:
  * FOREIGN seat  -> the daemon is provably inert: one stderr line, exit 0, and
                     nothing past the guard is reached.
  * RESIDENT seat -> the guard passes through and the daemon proceeds. Proven
                     with a real tmp-HOME marker file and NO SE_SEAT override,
                     so the production discriminator is what is under test.
plus two structural locks: no future daemon ships unguarded silently, and
background/_seat.py can never grow a SECOND copy of the discriminator.

MUTATION PROOF (run by hand, reported in the PR): neutering
`_seat.is_resident_seat()` to `return True` reds every foreign-direction test
here and leaves the resident-direction ones green; neutering it to
`return False` reds the resident-direction tests. Deleting the
`refuse_if_foreign(...)` line from any single guarded module reds
TestStructuralLock::test_every_main_entrypoint_is_guarded naming that module.
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKGROUND = REPO_ROOT / "background"
MANIFEST = BACKGROUND / "process_manifest.yaml"

sys.path.insert(0, str(REPO_ROOT))
from background import _seat  # noqa: E402

# background/_seat.py IS the guard, so it is the one entrypoint that cannot
# guard itself (its __main__ is the shell-facing resident/foreign probe).
GUARD_MODULE = "_seat.py"

# Dated allowlist of background/*.py entrypoints that deliberately run in EVERY
# seat. Shrink-preferred: a module joins this list only with a per-module
# justification in the PR, and the default for anything new is GUARDED.
# Empty as of 2026-08-07 (ccm/seat-guard-daemons) -- every entrypoint in
# background/ is resident-seat machinery, so every one of them is guarded.
UNIVERSAL_MODULES: set[str] = set()

# Dated allowlist of background/*.sh scripts that are deliberately UNGUARDED.
# 2026-08-07 (ccm/seat-guard-daemons): these two launch the DIRECTOR'S OWN
# interactive console, not the daemon stack. A foreign console is a nuisance; a
# director locked out of his console because a marker file went missing is a
# worse failure than the one being guarded against, and the console starts no
# daemon, holds no credentials of its own, and is excluded from reconciliation
# by its G-L1 sanctity marker. Everything that STARTS or INSTALLS the stack is
# guarded.
DIRECTOR_CONSOLE_SCRIPTS = {"console.sh", "director_console.sh"}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _make_marker(home: Path) -> Path:
    """Create the resident-only marker under a throwaway HOME."""
    marker = home / ".config" / "synthetic-enterprise" / ".env.ntfy"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("SE_NTFY_TOPIC=not-a-real-secret\n")
    return marker


def _background_modules() -> list[Path]:
    return sorted(p for p in BACKGROUND.glob("*.py") if not p.name.startswith("__"))


def _main_block(tree: ast.Module) -> ast.If | None:
    """The module-level `if __name__ == "__main__":` block, if any."""
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "__name__"
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value == "__main__"
        ):
            return node
    return None


def _is_import_only(node: ast.stmt) -> bool:
    """True for an import, or a try/except whose every branch is imports only.

    The guard idiom imports `refuse_if_foreign` inside a try/except (the two
    launch forms -- `python3 background/x.py` and `python3 -m background.x` --
    put different directories on sys.path). Imports move no state, so they are
    the only thing allowed to precede the guard call.
    """
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return True
    if isinstance(node, ast.Try):
        branches = [node.body, node.orelse, node.finalbody] + [h.body for h in node.handlers]
        return all(all(_is_import_only(s) for s in b) for b in branches)
    return False


def _guard_call_name(node: ast.stmt) -> str | None:
    """If `node` is `refuse_if_foreign("<literal>")`, return the literal."""
    if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
        return None
    func = node.value.func
    name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
    if name != "refuse_if_foreign" or len(node.value.args) != 1:
        return None
    arg = node.value.args[0]
    return arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, str) else None


def _guarded_name(path: Path) -> str | None:
    """The name a module guards itself under, or None if it is not guarded.

    "Guarded" is strict: the guard call must be the FIRST non-import statement
    of the `__main__` block. A guard that runs after other work is not a guard.
    """
    block = _main_block(ast.parse(path.read_text()))
    if block is None:
        return None
    for stmt in block.body:
        if _is_import_only(stmt):
            continue
        return _guard_call_name(stmt)  # first non-import statement, or None
    return None


def _manifest_modules() -> list[tuple[str, str]]:
    """(session, module stem) for every manifest process backed by background/*.py."""
    manifest = yaml.safe_load(MANIFEST.read_text())
    out = []
    for proc in manifest["processes"]:
        command = proc["command"]
        stem = None
        for token in command.split():
            if token.startswith("background/") and token.endswith(".py"):
                stem = Path(token).stem
            elif token.startswith("background."):
                stem = token.split(".", 1)[1]
        if stem:  # the `claude` tmux seat entry is the CLI itself, not a module
            out.append((proc["session"], stem))
    return out


def _run(argv: list[str], *, home: Path, extra_env: dict[str, str] | None = None,
         seat: str | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a daemon entrypoint as a real subprocess under a controlled HOME."""
    env = {
        "HOME": str(home),
        "PATH": os.environ["PATH"],
        "PYTHONPATH": str(REPO_ROOT),
        # The stack's daemons require this at IMPORT time (ntfy_utils refuses to
        # load without it). Supplying it models the environment that actually
        # succeeds in starting the stack -- i.e. the threat -- so the guard is
        # what stops them, not a missing variable.
        "SE_NTFY_TOPIC": "seat-guard-test-not-a-real-topic",
    }
    if seat is not None:
        env["SE_SEAT"] = seat
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, *argv], capture_output=True, text=True,
        cwd=str(REPO_ROOT), env=env, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# background/_seat.py: delegation, not duplication
# ---------------------------------------------------------------------------


class TestGuardIsNotDuplicated:
    """The discriminator lives in ONE file. Two copies of a security predicate
    drift, and the drift is silent."""

    def test_background_seat_holds_no_second_copy_of_the_discriminator(self):
        src = (BACKGROUND / "_seat.py").read_text()
        tree = ast.parse(src)
        # Strip docstrings: prose may DESCRIBE the marker and the override; only
        # executable code restating them would be a second implementation.
        constants = {
            node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        docstrings = {ast.get_docstring(n) for n in ast.walk(tree)
                      if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef))}
        code_constants = constants - docstrings
        assert ".env.ntfy" not in code_constants, (
            "background/_seat.py names the marker file itself -- that is a SECOND "
            "copy of the discriminator. It must delegate to .claude/hooks/_seat.py."
        )
        imported = {n.names[0].name.split(".")[0] for n in ast.walk(tree)
                    if isinstance(n, ast.Import)}
        assert "os" not in imported, (
            "background/_seat.py imports os -- it must not read SE_SEAT itself; "
            "the override is the canonical guard's to interpret."
        )

    def test_it_loads_the_canonical_hook_guard(self):
        source = _seat._load_seat_source()
        assert Path(source.__file__) == (REPO_ROOT / ".claude" / "hooks" / "_seat.py")

    def test_missing_canonical_guard_is_fatal_not_fail_open(self, monkeypatch):
        """R15 FAIL-SILENT: an unavailable check is a FAILED check. A guard that
        cannot load must be loud, never a silent pass-through."""
        monkeypatch.setattr(_seat, "_HOOK_SEAT", REPO_ROOT / ".claude" / "hooks" / "nope.py")
        monkeypatch.delitem(sys.modules, _seat._SOURCE_MODULE_NAME, raising=False)
        with pytest.raises((ImportError, FileNotFoundError)):
            _seat.is_resident_seat()


class TestResidentDetectionDelegates:
    """The re-export must answer exactly as the canonical guard does."""

    def test_marker_present_no_override_is_resident(self, tmp_path, monkeypatch):
        _make_marker(tmp_path)
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.delenv("SE_SEAT", raising=False)
        assert _seat.is_resident_seat() is True

    def test_marker_absent_no_override_is_foreign(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.delenv("SE_SEAT", raising=False)
        assert _seat.is_resident_seat() is False

    def test_override_foreign_wins_over_present_marker(self, tmp_path, monkeypatch):
        _make_marker(tmp_path)
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("SE_SEAT", "foreign")
        assert _seat.is_resident_seat() is False

    def test_override_resident_wins_over_absent_marker(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("SE_SEAT", "resident")
        assert _seat.is_resident_seat() is True

    def test_marker_path_tracks_home_at_call_time(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        assert _seat.resident_marker_path() == (
            tmp_path / ".config" / "synthetic-enterprise" / ".env.ntfy"
        )


# ---------------------------------------------------------------------------
# refuse_if_foreign(): the daemon-facing guard, both directions
# ---------------------------------------------------------------------------


class TestRefuseIfForeign:
    def test_foreign_exits_zero_with_one_stderr_line(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("SE_SEAT", "foreign")
        with pytest.raises(SystemExit) as exc:
            _seat.refuse_if_foreign("supervisor")
        assert exc.value.code == 0
        out = capsys.readouterr()
        assert out.err == "seat-guard: foreign, supervisor not starting\n"
        assert out.out == ""

    def test_resident_returns_and_says_nothing(self, tmp_path, monkeypatch, capsys):
        _make_marker(tmp_path)
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.delenv("SE_SEAT", raising=False)  # marker alone decides
        assert _seat.refuse_if_foreign("supervisor") is None
        out = capsys.readouterr()
        assert out.out == "" and out.err == ""

    def test_refusal_line_names_the_daemon(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("HOME", str(tmp_path))
        monkeypatch.setenv("SE_SEAT", "foreign")
        with pytest.raises(SystemExit):
            _seat.refuse_if_foreign("deadmans_switch")
        assert "deadmans_switch" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Process-level R15: a real daemon, launched the way the manifest launches it
# ---------------------------------------------------------------------------


class TestRealDaemonBothDirections:
    """token-proxy is a real `enabled` manifest daemon whose entrypoint parses
    argv, so `--help` proves the process got PAST the guard and into its own
    code without ever binding a port or touching the tree."""

    ENTRYPOINT = ["background/token_proxy.py", "--help"]

    def test_foreign_seat_is_inert(self, tmp_path):
        r = _run(self.ENTRYPOINT, home=tmp_path)  # no marker, no override
        assert r.returncode == 0
        assert r.stderr == "seat-guard: foreign, token_proxy not starting\n"
        assert r.stdout == ""  # argparse never ran -> guard came first

    def test_resident_seat_passes_through(self, tmp_path):
        _make_marker(tmp_path)
        r = _run(self.ENTRYPOINT, home=tmp_path)  # marker alone, no override
        assert r.returncode == 0
        assert "seat-guard" not in r.stderr
        assert "usage: token_proxy.py" in r.stdout  # proceeded into its own code

    # These are long-running daemons. A WORKING guard stops them in
    # milliseconds; only a BROKEN one lets them reach their main loop, so the
    # short timeout below is the blast-radius bound on that failure -- it kills
    # the daemon and fails the test loudly instead of letting it run (and write
    # to the seat's observability files) for the suite's full timeout. Observed
    # for real while mutation-testing this guard: with the discriminator
    # neutered, supervisor.py started against this foreign checkout and appended
    # "Supervisor started" to docs/observability/supervisor-log.md.
    DAEMONS = ("supervisor", "staging_watcher")
    START_TIMEOUT_S = 20

    def test_foreign_daemon_writes_nothing_to_the_tree(self, tmp_path):
        """Inertness is about STATE, not just exit codes."""
        before = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT,
                                capture_output=True, text=True).stdout
        for stem in self.DAEMONS:
            try:
                r = _run([f"background/{stem}.py"], home=tmp_path,
                         timeout=self.START_TIMEOUT_S)
            except subprocess.TimeoutExpired:
                pytest.fail(
                    f"{stem} was still running after {self.START_TIMEOUT_S}s in a "
                    "FOREIGN seat -- the guard did not stop it"
                )
            assert r.returncode == 0, f"{stem}: rc={r.returncode} stderr={r.stderr[:400]}"
            assert r.stderr == f"seat-guard: foreign, {stem} not starting\n"
        after = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT,
                               capture_output=True, text=True).stdout
        assert before == after, "a foreign daemon start dirtied the working tree"


# ---------------------------------------------------------------------------
# Structural locks
# ---------------------------------------------------------------------------


class TestStructuralLock:
    def test_every_main_entrypoint_is_guarded(self):
        offenders = []
        for path in _background_modules():
            if path.name == GUARD_MODULE:
                continue
            if _main_block(ast.parse(path.read_text())) is None:
                continue  # library, no entrypoint -- nothing to start
            guarded_as = _guarded_name(path)
            if path.name in UNIVERSAL_MODULES:
                assert guarded_as is None, (
                    f"{path.name} is on UNIVERSAL_MODULES but guards itself"
                )
            elif guarded_as is None:
                offenders.append(path.name)
        assert not offenders, (
            f"background/*.py entrypoints with no seat guard as the FIRST act of "
            f"their __main__ block: {offenders} -- add "
            "`refuse_if_foreign(\"<module>\")` (the default) or justify adding them "
            "to UNIVERSAL_MODULES in the PR"
        )

    def test_guard_name_matches_its_module(self):
        """A copy-pasted guard naming the wrong daemon logs a lie."""
        wrong = []
        for path in _background_modules():
            if path.name == GUARD_MODULE:
                continue
            guarded_as = _guarded_name(path)
            if guarded_as is not None and guarded_as != path.stem:
                wrong.append(f"{path.name} guards as {guarded_as!r}")
        assert not wrong, f"seat-guard name does not match its module: {wrong}"

    def test_every_manifest_daemon_is_guarded(self):
        """The manifest is the declared process set -- every one of its daemons
        must refuse foreign soil."""
        unguarded = [
            f"{session} ({stem}.py)"
            for session, stem in _manifest_modules()
            if f"{stem}.py" not in UNIVERSAL_MODULES
            and _guarded_name(BACKGROUND / f"{stem}.py") != stem
        ]
        assert not unguarded, f"manifest daemons without a seat guard: {unguarded}"

    def test_manifest_coverage_is_not_vacuous(self):
        """The lock above is meaningless if the manifest parse yields nothing."""
        modules = _manifest_modules()
        assert len(modules) >= 10, f"only parsed {len(modules)} manifest modules"
        assert ("supervisor", "supervisor") in modules

    def test_universal_allowlist_entries_exist(self):
        for name in UNIVERSAL_MODULES:
            assert (BACKGROUND / name).is_file(), f"{name} on UNIVERSAL_MODULES but absent"

    def test_there_is_at_least_one_guarded_entrypoint(self):
        guarded = [p.name for p in _background_modules() if _guarded_name(p) is not None]
        assert len(guarded) >= 40, f"only {len(guarded)} guarded entrypoints"

    def test_every_stack_launcher_script_is_guarded(self):
        """The daemons are only half the launch path -- the scripts that START or
        INSTALL the stack must refuse foreign soil too, via the same
        discriminator (`python3 background/_seat.py`)."""
        offenders = [
            p.name for p in sorted(BACKGROUND.glob("*.sh"))
            if p.name not in DIRECTOR_CONSOLE_SCRIPTS and "_seat.py" not in p.read_text()
        ]
        assert not offenders, (
            f"stack launcher scripts with no seat guard: {offenders} -- add the "
            "`python3 \"$(dirname \"$0\")/_seat.py\"` guard or justify adding them "
            "to DIRECTOR_CONSOLE_SCRIPTS in the PR"
        )

    def test_director_console_scripts_exist(self):
        for name in DIRECTOR_CONSOLE_SCRIPTS:
            assert (BACKGROUND / name).is_file(), f"{name} allowlisted but absent"

    def test_guard_must_precede_real_work(self):
        """The strict-ordering rule the lock depends on actually rejects a guard
        that sits after other work -- otherwise the lock is a tautology (R15)."""
        late = ast.parse(
            'if __name__ == "__main__":\n'
            "    start_the_daemon()\n"
            "    from background._seat import refuse_if_foreign\n"
            '    refuse_if_foreign("x")\n'
        )
        block = _main_block(late)
        assert block is not None
        first_non_import = next(s for s in block.body if not _is_import_only(s))
        assert _guard_call_name(first_non_import) is None
