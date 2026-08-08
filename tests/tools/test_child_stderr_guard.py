"""R15 mutation proof for `tools/child_stderr_guard.py` (atom H30).

R15: a control counts as evidence only if a MUTATION TEST proves it fires on
its own named defect. This guard's named defect is "a background process
reports a child's FAILURE to a human while having discarded the child's
stderr", so the tests below reintroduce the exact 2026-08-08 `sim_runner`
shape as source text and assert the guard goes red — then assert it goes
green once the capture is added, which is the half that catches a guard that
can only fail.

The three killer patterns:

  TAUTOLOGY   -- the fixtures are raw source strings written here, not
                 derived from the guard's own tables, and the property under
                 test (a capture argument is present) is not the property
                 that makes a fixture "defective" in the eyes of this file.
  FAIL-OPEN   -- a missing root, an unparseable file, an empty scan, and a
                 declared daemon outside the scanned root must all FAIL
                 (rc 2), never pass as "no violations found".
  FAIL-SILENT -- rc 2 is distinct from rc 0, so "the guard could not run"
                 cannot be read as "the guard passed".

Every fixture lives in tmp_path. A mutation test that edits the real tree and
restores it can wipe an unrelated in-flight edit (this project has done it).
"""
from __future__ import annotations

import textwrap

import pytest

from tools.child_stderr_guard import (
    main,
    scan,
    uncovered_declared_entrypoints,
)


def _write(tmp_path, name, source):
    path = tmp_path / name
    path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


# The defect exactly as it shipped: launch, check the return code, tell a
# human, having thrown away the only thing that says why.
DEFECT_SOURCE = '''
    import subprocess

    def run_simulation():
        result = subprocess.run(
            ["python3", "-m", "saas.reporting.annual_report"],
            cwd="/repo",
            timeout=7200,
        )
        if result.returncode != 0:
            log(f"Run FAILED (rc={result.returncode})")
            notify("[SIM] Run FAILED — check sim-runner-log.md", kind="real_alarm")
            return False
        return True
'''


class TestFiresOnItsOwnDefect:
    """MUTATION: reintroduce the real defect, assert the guard goes red."""

    def test_fires_on_the_2026_08_08_sim_runner_shape(self, tmp_path):
        _write(tmp_path, "mutated.py", DEFECT_SOURCE)
        messages, scanned = scan(tmp_path, tmp_path)
        assert scanned == 1
        assert len(messages) == 1, messages
        assert "run_simulation()" in messages[0]
        assert "stderr" in messages[0], "the message must name the missing capture"

    def test_fires_on_check_true_without_capture(self, tmp_path):
        # The executor_governor shape: no returncode read at all — the failure
        # arrives as CalledProcessError, whose str() names the command and the
        # code and never what the child said.
        _write(tmp_path, "mutated.py", '''
            import subprocess

            def _default_fold():
                try:
                    subprocess.run(["git", "add", "--", "map.yaml"], check=True)
                except Exception as exc:
                    log(f"fold step errored: {exc}")
        ''')
        messages, _ = scan(tmp_path, tmp_path)
        assert len(messages) == 1, messages
        assert "_default_fold()" in messages[0]

    def test_fires_on_explicit_devnull(self, tmp_path):
        """Deliberately discarding the payload is the same defect, not an
        exemption — otherwise the fix for a guard failure is one keyword."""
        _write(tmp_path, "mutated.py", '''
            import subprocess

            def publish():
                r = subprocess.run(["git", "push"], stderr=subprocess.DEVNULL)
                if r.returncode != 0:
                    notify("push failed", kind="real_alarm")
        ''')
        messages, _ = scan(tmp_path, tmp_path)
        assert len(messages) == 1, messages


class TestPassesOnTheFix:
    """The other half of R15: a control that can ONLY fail wedges the gate."""

    def test_clean_once_stderr_is_captured(self, tmp_path):
        _write(tmp_path, "fixed.py", DEFECT_SOURCE.replace(
            "timeout=7200,", "timeout=7200,\n            stderr=subprocess.PIPE,"))
        messages, scanned = scan(tmp_path, tmp_path)
        assert scanned == 1
        assert messages == []

    def test_clean_with_capture_output(self, tmp_path):
        _write(tmp_path, "fixed.py", DEFECT_SOURCE.replace(
            "timeout=7200,", "timeout=7200, capture_output=True,"))
        messages, _ = scan(tmp_path, tmp_path)
        assert messages == []

    def test_the_live_background_tree_is_clean(self):
        """The state this atom leaves the tree in — and the assertion that
        goes red the moment a new daemon reintroduces the class."""
        assert main([]) == 0


class TestScopeIsNotOverreach:
    """A guard that also fires on correct code gets switched off in a week."""

    def test_ignores_a_launch_whose_failure_nobody_reports(self, tmp_path):
        _write(tmp_path, "helper.py", '''
            import subprocess

            def _git_head():
                return subprocess.run(["git", "rev-parse", "HEAD"]).stdout
        ''')
        messages, _ = scan(tmp_path, tmp_path)
        assert messages == []

    def test_ignores_a_reporter_with_no_failure_awareness(self, tmp_path):
        _write(tmp_path, "helper.py", '''
            import subprocess

            def kick_off():
                subprocess.run(["python3", "worker.py"])
                log("worker started")
        ''')
        messages, _ = scan(tmp_path, tmp_path)
        assert messages == []

    def test_ignores_a_non_subprocess_run_method(self, tmp_path):
        _write(tmp_path, "helper.py", '''
            def go(pool):
                result = pool.run(["task"])
                if result.returncode != 0:
                    log("pool task failed")
        ''')
        messages, _ = scan(tmp_path, tmp_path)
        assert messages == []


class TestFailsClosed:
    """FAIL-OPEN / FAIL-SILENT: every way this could pass without checking."""

    def test_missing_root_is_a_failure_not_a_pass(self, tmp_path):
        assert main(["--root", str(tmp_path / "nope")]) == 2

    def test_unparseable_file_is_a_failure_not_a_skip(self, tmp_path):
        _write(tmp_path, "broken.py", "def f(:\n    pass\n")
        assert main(["--root", str(tmp_path)]) == 2

    def test_empty_scan_is_a_failure_vacuity_guard(self, tmp_path):
        (tmp_path / "empty").mkdir()
        assert main(["--root", str(tmp_path / "empty")]) == 2

    def test_could_not_run_is_distinct_from_clean(self, tmp_path):
        _write(tmp_path, "ok.py", "x = 1\n")
        assert main(["--root", str(tmp_path)]) == 0
        assert main(["--root", str(tmp_path / "gone")]) == 2

    def test_violation_code_is_distinct_from_both(self, tmp_path):
        _write(tmp_path, "mutated.py", DEFECT_SOURCE)
        assert main(["--root", str(tmp_path)]) == 1


class TestCoverageIsProvenNotAsserted:
    """The scope must be tied to the declared process set, not to prose."""

    def _manifest(self, tmp_path, command):
        path = tmp_path / "process_manifest.yaml"
        path.write_text(textwrap.dedent("""
            version: 2
            processes:
              - session: some-daemon
                command: %s
                state: enabled
        """ % command), encoding="utf-8")
        return path

    def test_daemon_outside_the_scanned_root_is_a_coverage_hole(self, tmp_path):
        root = tmp_path / "background"
        root.mkdir()
        manifest = self._manifest(tmp_path, "python3 services/new_daemon.py")
        uncovered = uncovered_declared_entrypoints(root, manifest)
        assert uncovered, "a declared daemon outside the root must be reported"
        assert "new_daemon.py" in uncovered[0]

    def test_daemon_inside_the_scanned_root_is_covered(self, tmp_path):
        root = tmp_path / "background"
        root.mkdir()
        manifest = self._manifest(tmp_path, "python3 background/sim_runner.py")
        assert uncovered_declared_entrypoints(root, manifest) == []

    def test_retired_daemon_is_not_required_to_be_covered(self, tmp_path):
        root = tmp_path / "background"
        root.mkdir()
        path = tmp_path / "process_manifest.yaml"
        path.write_text(textwrap.dedent("""
            version: 2
            processes:
              - session: dead
                command: python3 elsewhere/dead.py
                state: retired
        """), encoding="utf-8")
        assert uncovered_declared_entrypoints(root, path) == []

    def test_missing_manifest_raises_rather_than_returning_empty(self, tmp_path):
        """An unavailable coverage check is a FAILED check, never an empty
        list that reads to the caller as 'nothing uncovered'."""
        with pytest.raises(FileNotFoundError):
            uncovered_declared_entrypoints(tmp_path, tmp_path / "absent.yaml")

    def test_the_real_manifest_is_fully_covered_by_the_default_root(self):
        from tools.child_stderr_guard import PROCESS_MANIFEST
        root = PROCESS_MANIFEST.parent
        assert uncovered_declared_entrypoints(root) == []
