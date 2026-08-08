#!/usr/bin/env python3
"""Seat identity for background/ daemons -- "whose soil is this daemon on?".

THE VECTOR THIS CLOSES. The resident worker seat's daemon stack is started by
the environment that hosts a session, not by the session itself: the poesys
cloud environment brings the stack up inside EVERY session's freshly-cloned
tree. A daemon booted that way is pointed at a foreign checkout but keeps all
of the resident seat's authority -- it commits, it pushes, it stamps the
seat's observability files, it drains the instruction channel. Issue #11 is
the proven case: a liveness daemon sharing a foreign session's tree pushed
main. `.claude/hooks/` was guarded for exactly this reason (`_seat.py` there);
`background/` was not, and it is the half with the push credentials.

ONE SOURCE OF TRUTH. The discriminator itself is NOT reimplemented here. This
module loads `.claude/hooks/_seat.py` -- the guard that already exists, is
already tested, and is already the thing hooks trust -- and re-exports it. Two
copies of a security predicate drift, and the drift is silent; there is one
copy, and this file is a thin adapter to it.

Loading is by explicit path (importlib), NOT by putting `.claude/hooks/` on
sys.path: hooks are standalone scripts with short generic names (`notify.py`
and friends), and grafting that directory onto a long-lived daemon's import
path would let a hook shadow a real `background/` dependency. The source
module is registered under a private name so it can never collide with the
plain `_seat` that hook processes import.

USAGE -- the first act of every daemon/job entrypoint, inside its
`if __name__ == "__main__":` block, before any other work:

    if __name__ == "__main__":
        from background._seat import refuse_if_foreign
        refuse_if_foreign("supervisor")
        main()

Guarding the ENTRYPOINT rather than import time is deliberate. These modules
are also libraries -- `background/health_check.py` imports
`process_reconciler.evaluate_pull_loop`, `deadmans_switch` imports
`status_honesty.evaluate_status_honesty`, and the test suite imports dozens of
them for their functions. Importing a module has no authority and must stay
free; STARTING one as a process is the act that needs the seat.

Unlike the hook guard, a refusing daemon is NOT silent: it prints one line to
stderr and exits 0. Silence is right for a hook (it is one of many on a hot
path, and stdout is protocol); a daemon that declines to start must leave a
reason in the journal, or its absence reads as a crash. Exit 0, not non-zero,
so a systemd unit or a launcher script records "did not start here" rather
than restart-looping against a machine it will never be resident on.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

# <repo>/background/_seat.py -> parents[1] is <repo>.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_HOOK_SEAT = _REPO_ROOT / ".claude" / "hooks" / "_seat.py"

# Private name: hook processes import the same file as plain `_seat`, and this
# must never be mistaken for (or clobbered by) that entry in sys.modules.
_SOURCE_MODULE_NAME = "_synthetic_enterprise_seat_source"


def _load_seat_source() -> ModuleType:
    """Import the canonical guard from `.claude/hooks/_seat.py`.

    Raises ImportError if it cannot be loaded. That is deliberate and is the
    R15 FAIL-SILENT rule applied to this control: an unavailable check is a
    FAILED check, so a guard that cannot load must be loud and fatal, never a
    silent pass-through that lets a daemon start on foreign soil because its
    seat check was missing. In a git checkout the file is always present --
    reaching this error means the repo is not intact.
    """
    cached = sys.modules.get(_SOURCE_MODULE_NAME)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(_SOURCE_MODULE_NAME, _HOOK_SEAT)
    if spec is None or spec.loader is None:
        raise ImportError(f"seat guard source not loadable: {_HOOK_SEAT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[_SOURCE_MODULE_NAME] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        del sys.modules[_SOURCE_MODULE_NAME]
        raise
    return module


def is_resident_seat() -> bool:
    """True iff this process is running in the resident worker seat.

    Re-export of `.claude/hooks/_seat.py::is_resident_seat` -- see that module
    for the marker file, the SE_SEAT override, and the fail-to-foreign rule.
    Resolved on every call (never bound at import) so a test monkeypatching
    HOME or SE_SEAT controls the answer here exactly as it does there.
    """
    return bool(_load_seat_source().is_resident_seat())


def resident_marker_path() -> Path:
    """Re-export of the canonical resident-marker path, for diagnostics."""
    return Path(_load_seat_source().resident_marker_path())


def refuse_if_foreign(name: str) -> None:
    """Seat guard for a daemon/job entrypoint. Returns only in the resident seat.

    In any foreign seat this prints one line to stderr and exits the process
    with status 0, so the daemon is provably inert: nothing it would have
    done -- no commit, no push, no state write, no channel read -- is reached,
    because this is called before any of it.

    `name` is the module stem (e.g. "supervisor"), passed as a literal so the
    journal line names the daemon that declined. The structural lock test
    asserts the literal matches the file it sits in.
    """
    if is_resident_seat():
        return
    print(f"seat-guard: foreign, {name} not starting", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    # Shell-facing probe, so the launcher SCRIPTS share this one source of
    # truth instead of reimplementing the marker check in sh:
    #   python3 background/_seat.py || { echo "..." >&2; exit 0; }
    # Exit 0 = resident, 1 = foreign. Prints nothing; the caller owns the
    # message so the refusal line names the script that declined.
    #
    # This module is the guard, so it is (necessarily) the one background/*.py
    # entrypoint that does not guard itself -- the structural lock test names
    # it as the sole exemption.
    sys.exit(0 if is_resident_seat() else 1)
