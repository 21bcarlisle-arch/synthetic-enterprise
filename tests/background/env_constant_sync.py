"""H31 CLASS FIX (R10): module-level env-derived constants must not be left stale.

THE DEFECT THIS CLOSES. `background/ntfy_utils.py` snapshots its secrets into module-level
constants at import time (`WAKE_HMAC_KEY = os.environ.get("SE_WAKE_HMAC_KEY")`). A test that
scrubs the env, `importlib.reload()`s the module to make the constant go None, and then
"restores" with a second reload in a `finally:` block restores NOTHING -- `monkeypatch` undoes
env changes in a fixture FINALIZER, which runs AFTER the test function returns, while a
`finally:` block runs while the function is still on the stack. The restoring reload therefore
re-reads the still-scrubbed env, `os.environ` is repaired a moment later, and the module
constant stays None for every later test in the same process.

The symptom is maximally misleading: the four `test_ntfy_utils.py` signing tests pass alone and
fail in-suite, which reads as "import order" and sends diagnosis at the wrong target. The
VICTIMS red; the CULPRIT is green.

WHY A SCANNER AND NOT A LIST. The instance fix (`monkeypatch.undo()` before the restoring
reload) is in this change too, but R10 says an absurdity-class defect may not be closed with an
instance fix. A hand-maintained list of (module, attr, envvar) triples decays the moment someone
adds the next `X = os.environ.get("Y")`. So the registry is DERIVED: this module AST-scans
`background/*.py` for top-level assignments whose right-hand side is DIRECTLY an environment
read, and the per-test guard checks every one of them. A constant added tomorrow is covered
without anyone remembering to add it here.

WHAT THE GUARD DOES, AND WHY IT REPAIRS. On divergence it (a) FAILS the test that caused it --
naming the culprit rather than the victims, which is the whole diagnostic value -- and (b)
repairs the constant to the value a fresh import would compute, so a single bad test can no
longer make the rest of the session's results depend on collection order. Reporting without
repairing would leave the cascade intact.

SCOPE DISCIPLINE (fail-open avoidance). Only assignments whose RHS is directly `os.environ.get`
/ `os.getenv` / `os.environ[...]` with a LITERAL default are registered. A wrapped read
(`Path(os.environ.get(...))`) is deliberately NOT registered: the expected value could not be
recomputed without re-running the wrapper, and a guard that compares apples to oranges would
fire on honest code and get silenced. Narrow-and-true beats broad-and-noisy.
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The package(s) whose module-level env constants are guarded. Kept as data so a second
# package can be added without touching the logic.
SCANNED_PACKAGES = ("background",)

_MISSING = object()


class EnvConstant:
    """One registered (module, attribute) <- (env var, literal default) binding."""

    __slots__ = ("module", "attr", "env_var", "default", "required")

    def __init__(self, module: str, attr: str, env_var: str, default, required: bool):
        self.module = module
        self.attr = attr
        self.env_var = env_var
        self.default = default
        self.required = required  # True for os.environ["X"] (no default -> KeyError form)

    @property
    def dotted(self) -> str:
        return f"{self.module}.{self.attr}"

    def expected(self):
        """The value a FRESH import would compute from the CURRENT os.environ."""
        if self.required:
            return os.environ.get(self.env_var, _MISSING)
        return os.environ.get(self.env_var, self.default)

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return f"<EnvConstant {self.dotted} <- ${self.env_var}>"


def _env_read(node: ast.AST):
    """If `node` is DIRECTLY an environment read, return (env_var, default, required).

    Recognised forms (and only these -- see SCOPE DISCIPLINE in the module docstring):
        os.environ.get("X")            -> ("X", None,  False)
        os.environ.get("X", <literal>) -> ("X", lit,   False)
        os.getenv("X"[, <literal>])    -> ("X", ...,   False)
        os.environ["X"]                -> ("X", None,  True)
    Anything else -> None.
    """
    # os.environ["X"]
    if isinstance(node, ast.Subscript):
        value, sl = node.value, node.slice
        if (
            isinstance(value, ast.Attribute)
            and value.attr == "environ"
            and isinstance(value.value, ast.Name)
            and value.value.id == "os"
            and isinstance(sl, ast.Constant)
            and isinstance(sl.value, str)
        ):
            return sl.value, None, True
        return None

    if not isinstance(node, ast.Call):
        return None
    func = node.func
    is_environ_get = (
        isinstance(func, ast.Attribute)
        and func.attr == "get"
        and isinstance(func.value, ast.Attribute)
        and func.value.attr == "environ"
        and isinstance(func.value.value, ast.Name)
        and func.value.value.id == "os"
    )
    is_getenv = (
        isinstance(func, ast.Attribute)
        and func.attr == "getenv"
        and isinstance(func.value, ast.Name)
        and func.value.id == "os"
    )
    if not (is_environ_get or is_getenv):
        return None
    if node.keywords or not node.args:
        return None
    name_node = node.args[0]
    if not (isinstance(name_node, ast.Constant) and isinstance(name_node.value, str)):
        return None
    default = None
    if len(node.args) >= 2:
        try:
            default = ast.literal_eval(node.args[1])
        except (ValueError, SyntaxError):
            return None  # non-literal default: cannot recompute, so do not register
    if len(node.args) > 2:
        return None
    return name_node.value, default, False


def _scan_module_file(path: Path, module_name: str) -> list[EnvConstant]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return []
    found: list[EnvConstant] = []
    for node in tree.body:  # TOP-LEVEL only: an import-time snapshot is the defect class
        if isinstance(node, ast.AnnAssign):
            targets, value = ([node.target] if node.value is not None else []), node.value
        elif isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        else:
            continue
        if value is None:
            continue
        read = _env_read(value)
        if read is None:
            continue
        env_var, default, required = read
        for target in targets:
            if isinstance(target, ast.Name):
                found.append(EnvConstant(module_name, target.id, env_var, default, required))
    return found


def build_registry(repo_root: Path | None = None) -> list[EnvConstant]:
    """AST-derive every guarded module-level env constant. Sorted for stable reporting."""
    root = repo_root or REPO_ROOT
    registry: list[EnvConstant] = []
    for package in SCANNED_PACKAGES:
        pkg_dir = root / package
        if not pkg_dir.is_dir():
            continue
        for path in sorted(pkg_dir.glob("*.py")):
            if path.name == "__init__.py":
                continue
            registry.extend(_scan_module_file(path, f"{package}.{path.stem}"))
    return sorted(registry, key=lambda c: (c.module, c.attr))


def diverged(registry, modules=None) -> list[tuple[EnvConstant, object, object]]:
    """Registered constants whose LIVE value differs from a fresh import's value.

    Only modules ALREADY imported are checked -- importing one here to check it would itself
    change session state, and an unimported module cannot have leaked anything.
    """
    mods = sys.modules if modules is None else modules
    out = []
    for const in registry:
        mod = mods.get(const.module)
        if mod is None:
            continue
        actual = getattr(mod, const.attr, _MISSING)
        if actual is _MISSING:
            continue  # attribute genuinely absent (e.g. os.environ["X"] form, var unset)
        expected = const.expected()
        if expected is _MISSING:
            continue
        if actual != expected:
            out.append((const, actual, expected))
    return out


def repair(const: EnvConstant, modules=None) -> None:
    """Reset one constant to what a fresh import would compute, so the leak stops here."""
    mods = sys.modules if modules is None else modules
    mod = mods.get(const.module)
    expected = const.expected()
    if mod is not None and expected is not _MISSING:
        setattr(mod, const.attr, expected)


def redact(value) -> str:
    """A value's IDENTITY without its content.

    Every constant this guard watches is by construction read from the environment, and in this
    repo those are secrets: `SE_WAKE_HMAC_KEY` is the symmetric key that signs director-authority
    wake messages, `SE_NTFY_TOPIC` is the ability to buzz the director's phone. A failure message
    printing them verbatim would write live secrets into pytest output, CI logs, and any
    transcript that quotes them -- the guard would become a leak of exactly the thing the scrub
    it protects exists to prevent.

    The diagnosis does not need the plaintext. The whole signal is "is it None / is it a
    DIFFERENT value", so strings collapse to length + a short digest: distinct values stay
    visibly distinct, equal values stay visibly equal, and nothing recoverable is printed.
    Non-strings (None, bools, numbers) are not secrets and print as-is.
    """
    if isinstance(value, str):
        import hashlib

        digest = hashlib.sha256(value.encode()).hexdigest()[:8]
        return f"<str len={len(value)} #{digest}>"
    return repr(value)


def describe(const: EnvConstant, actual, expected) -> str:
    """The failure payload (R5): what leaked, from where, and the two fixes that work."""
    return (
        "STALE ENV CONSTANT: {dotted} is {actual} but a fresh import would make it "
        "{expected} (from ${env}).\n"
        "  This test left a module-level env-derived constant desynchronised from os.environ, "
        "so EVERY later test in this process sees the stale value and pass/fail becomes a "
        "function of collection order. The tests that go red will be someone else's.\n"
        "  Almost always: an `importlib.reload(...)` in a `finally:` block. A `finally:` runs "
        "while the test function is still on the stack; monkeypatch undoes env changes in a "
        "FIXTURE FINALIZER, which runs later -- so the restoring reload re-reads the still-"
        "scrubbed env and restores nothing.\n"
        "  Fix by calling `monkeypatch.undo()` BEFORE the restoring reload, or by reloading in "
        "a fixture finalizer. Do not silence this hook.".format(
            dotted=const.dotted,
            actual=redact(actual),
            expected=redact(expected),
            env=const.env_var,
        )
    )
