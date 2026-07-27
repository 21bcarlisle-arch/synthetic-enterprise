"""Internal Seam Verifier (ARCH1) -- enforces the typed boundary between the
company's PRICING / BILLING / SETTLEMENT / COLLECTIONS domains.

Internal analogue of ``tools/epistemic_verifier.py``. Where the epistemic
verifier guards the SIM/company wall, this guards the wall BETWEEN the company's
four core financial domains: a domain may only cross into another through the
typed seam messages declared in ``company/interfaces/internal_seams.py`` -- it
must not import the other domain's internal modules directly.

Run at phase close:
    python3 -m tools.internal_seam_verifier [--all | --diff | --files f1 f2 ...]

Exit code 0 = PASS, exit code 1 = FAIL (violations found).

Design stance (R15 -- this control must be able to FAIL):
  * FAIL-CLOSED: an import that crosses a domain boundary and is neither the
    approved seam nor a documented baseline entry is a VIOLATION. Unknown =
    violation, not a pass.
  * NOT FAIL-OPEN: a file that cannot be read/parsed raises, it does not
    silently pass.
  * NOT A TAUTOLOGY: the boundary is defined by DOMAIN_PATHS (the spec), and the
    check compares the *importing* file's domain against the *imported* module's
    domain -- two independently-derived facts.
  * BOTH STATIC AND DYNAMIC crossings are covered: static ``import``/``from``
    plus dynamic ``importlib.import_module("...")`` / ``__import__("...")`` with
    a literal target (a domain must not evade the seam by switching one static
    cross-domain import to its dynamic form -- KL-2b class, R15 fail-open fix).
The mutation test in tests/tools/test_internal_seam_verifier.py plants a fresh
cross-domain import (static and dynamic forms) and asserts this verifier flags it.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# Import the seam spec (single source of truth for domains + baseline).
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from company.interfaces.internal_seams import (  # noqa: E402
    APPROVED_SEAM_MODULE,
    BASELINE_ALLOWLIST,
    DOMAIN_PATHS,
    Domain,
    classify_module,
    classify_path,
    module_to_relpath,
)


@dataclass(frozen=True)
class Violation:
    file: str
    lineno: int
    importing_domain: str
    imported_module: str
    imported_domain: str

    def __str__(self) -> str:
        return (
            f"{self.file}:{self.lineno}: {self.importing_domain} imports "
            f"{self.imported_module} ({self.imported_domain} internals) "
            f"-- cross-domain import must go through the typed seam "
            f"({APPROVED_SEAM_MODULE}) or be a documented baseline entry."
        )


def _resolve_relative(
    pkg_parts: tuple[str, ...], level: int, module: str | None
) -> str | None:
    """Resolve a relative ``from ... import`` to its absolute base module.

    ``pkg_parts`` is the importing file's package -- its parent-directory parts,
    e.g. ``('company', 'billing')`` for ``company/billing/collections.py`` (the
    same rule holds for a package ``__init__.py``). ``level`` is the ast dot
    count (1 = current package, 2 = parent, ...). Returns the absolute base
    dotted module, or ``None`` if the relative import escapes above the repo
    root (a runtime ``ImportError`` anyway, nothing to classify).

    WHY this exists (R15 fail-open fix, sibling of the dot-boundary allowlist
    fix): the old code SKIPPED every relative import on the assumption that they
    "stay within a package". That is FALSE for a cross-package relative such as
    ``from ..market import imbalance_ledger`` inside ``company/billing/``, which
    resolves to ``company.market.imbalance_ledger`` (a SETTLEMENT module) and so
    crosses a domain boundary. Skipping it let a domain evade the ENTIRE seam by
    switching one absolute cross-domain import to its relative form -- the check
    could not fire, which is worse than no check.
    """
    anchor_len = len(pkg_parts) - (level - 1)
    if anchor_len < 0:
        return None
    anchor = list(pkg_parts[:anchor_len])
    if module:
        anchor.extend(module.split("."))
    return ".".join(anchor) if anchor else None


def _dynamic_import_target(node: ast.Call) -> str | None:
    """Return the literal module name a dynamic-import CALL targets, or None.

    Detects the two standard dynamic-import forms with a LITERAL string target:
      * ``importlib.import_module("company.billing.payments")`` (attribute form)
        and the bare ``import_module("...")`` name form (``from importlib import
        import_module``);
      * the builtin ``__import__("company.billing.invoice")``.

    WHY this exists (R15 fail-open fix; sibling of the same fix already shipped
    in ``tools/epistemic_verifier`` for the SIM/company wall, KL-2b): the AST
    walk only visits ``ast.Import``/``ast.ImportFrom`` nodes, so a domain could
    reach straight into another domain's internals via a dynamic import and the
    seam could not fire at all -- a domain evading the ENTIRE seam by swapping
    one static cross-domain import for its dynamic form, which is worse than no
    check. Only a literal string first argument is statically resolvable; a
    variable/f-string/concatenation target is a documented heuristic limit (the
    same scope the epistemic verifier declares), not a silent false-clear."""
    func = node.func
    is_import_module = (
        isinstance(func, ast.Attribute)
        and func.attr == "import_module"
        and isinstance(func.value, ast.Name)
        and func.value.id == "importlib"
    ) or (isinstance(func, ast.Name) and func.id == "import_module")
    is_dunder_import = isinstance(func, ast.Name) and func.id == "__import__"
    if not (is_import_module or is_dunder_import):
        return None
    if not node.args:
        return None
    first = node.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    return None


def _iter_import_statements(tree: ast.AST, pkg_parts: tuple[str, ...]):
    """Yield (candidate_modules, lineno) per import STATEMENT.

    ``candidate_modules`` is the tuple of dotted module strings the statement
    could be reaching. For ``from PKG import a, b`` we cannot tell from the
    statement alone whether ``a``/``b`` are submodules or symbols, so we emit
    BOTH the parent ``PKG`` and each ``PKG.a`` candidate and let classification
    pick the most specific guarded match. This is what closes the FAIL-OPEN gap
    where ``from company.billing import invoice`` (module string
    ``company.billing``) previously classified to None and slipped through.

    Relative imports (``level>0``) are RESOLVED to absolute against
    ``pkg_parts`` (the importing file's package) rather than skipped -- a
    cross-package relative import crosses a domain boundary just like an
    absolute one (R15 fail-open fix).

    Dynamic imports (``importlib.import_module("...")``, ``__import__("...")``)
    with a literal string target are also emitted -- a dynamic cross-domain
    import crosses a boundary just like a static one (R15 fail-open fix, sibling
    of the epistemic verifier's KL-2b fix; see ``_dynamic_import_target``).
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield (alias.name,), node.lineno
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                base = _resolve_relative(pkg_parts, node.level, node.module)
                if base is None:
                    continue
            elif node.module:
                base = node.module
            else:
                continue
            candidates = [base]
            for alias in node.names:
                if alias.name and alias.name != "*":
                    candidates.append(f"{base}.{alias.name}")
            yield tuple(candidates), node.lineno
        elif isinstance(node, ast.Call):
            target = _dynamic_import_target(node)
            if target:
                yield (target,), node.lineno


def _module_domain(module: str):
    """Resolve an imported module to (Domain|None, resolved_as_file: bool).

    ``resolved_as_file`` is True when the module matched a domain via its .py
    file path (the most specific signal) and False when it only matched a guarded
    package directory -- used to prefer the specific submodule over its package.
    """
    dom = classify_path(module_to_relpath(module))
    if dom is not None:
        return dom, True
    return classify_module(module), False


def _is_baseline_allowed(file_rel: str, imported_module: str) -> bool:
    """True iff this crossing is a documented pre-seam baseline entry.

    The allowlist key's module is matched on a DOTTED-COMPONENT BOUNDARY, not a
    raw string prefix (R15 fail-open fix): an entry grandfathering
    ``company.billing.contract`` must allow that module and its submodules
    (``company.billing.contract.renewal_summary``) but MUST NOT silently allow a
    sibling that merely shares the string prefix (``company.billing.contract_termination``,
    ``company.billing.contractZZZ``) -- that would widen the seam past the one
    named crossing the baseline documents, re-opening the fail-closed guarantee
    the verifier exists to provide. This mirrors the dot-boundary discipline the
    approved-seam check already uses (``APPROVED_SEAM_MODULE + "."``)."""
    for (allow_file, allow_prefix) in BASELINE_ALLOWLIST:
        if file_rel != allow_file:
            continue
        if imported_module == allow_prefix or imported_module.startswith(
            allow_prefix + "."
        ):
            return True
    return False


def check_file(path: Path) -> list[Violation]:
    """Return the list of seam violations in a single file. Raises on a file
    that cannot be read or parsed (fail-closed -- an unavailable check is a
    failed check, never a silent pass)."""

    file_rel = str(path.resolve().relative_to(_REPO_ROOT)).replace("\\", "/")
    importing_domain = classify_path(file_rel)
    if importing_domain is None:
        return []  # not part of a guarded domain

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    # The importing file's package = its parent-directory parts. Relative
    # imports resolve against this (company/billing/collections.py ->
    # ('company','billing')).
    pkg_parts = Path(file_rel).parent.parts

    violations: list[Violation] = []
    for candidates, lineno in _iter_import_statements(tree, pkg_parts):
        # Resolve every candidate module this statement could reach; keep the
        # foreign, non-baseline ones.
        resolved: list[tuple[str, Domain, bool]] = []
        for module in candidates:
            if module == APPROVED_SEAM_MODULE or module.startswith(
                APPROVED_SEAM_MODULE + "."
            ):
                continue  # the approved seam is always allowed
            imported_domain, as_file = _module_domain(module)
            if imported_domain is None or imported_domain == importing_domain:
                continue  # non-domain import, or same-domain -- fine
            if _is_baseline_allowed(file_rel, module):
                continue  # documented pre-seam debt
            resolved.append((module, imported_domain, as_file))
        if not resolved:
            continue
        # One violation per import STATEMENT. Pick the most specific guarded
        # domain (prefer a submodule matched as a .py file over its package),
        # and report the shortest module string that names it (the statement's
        # own module, not a synthesised submodule candidate).
        pool = [r for r in resolved if r[2]] or resolved
        chosen_domain = max(pool, key=lambda r: len(r[0]))[1]
        report_module = min(
            (r[0] for r in resolved if r[1] == chosen_domain), key=len
        )
        violations.append(
            Violation(
                file=file_rel,
                lineno=lineno,
                importing_domain=importing_domain.value,
                imported_module=report_module,
                imported_domain=chosen_domain.value,
            )
        )
    return violations


def _domain_scan_roots() -> list[str]:
    """Derive the directory roots ``--all`` scans FROM ``DOMAIN_PATHS`` -- the
    single source of truth for where the guarded domains live -- rather than
    hardcoding them.

    WHY this exists (R15 fail-open fix, coverage/scope class): the scan-root list
    used to be a hand-maintained duplicate literal
    ``("company/billing", "company/pricing", "company/market")``. If
    ``DOMAIN_PATHS`` ever gained an entry with a root OUTSIDE those three -- which
    is exactly this module's own declared future work (moving SETTLEMENT to a
    ``company/settlement/`` package, COLLECTIONS to ``company/collections/``) --
    then ``--all`` (the phase-close gate) would silently NOT scan those files, so
    a cross-domain violation in the new domain would go UNDETECTED: the control's
    enforcement SCOPE would drift below the spec it exists to enforce, and a whole
    domain would read as "clean" while unenforced (R15 killer-pattern 2, fail-open
    on missing coverage -- worse than no check). Deriving the roots here means the
    ``--all`` scan can never cover less than ``DOMAIN_PATHS`` declares.

    Each ``DOMAIN_PATHS`` entry is either a directory prefix (``company/billing/``)
    or an exact file (``company/market/imbalance_ledger.py``); its scan root is the
    directory itself or the file's parent. Roots nested under another root are
    dropped (the parent's ``rglob`` already covers them)."""
    roots: set[str] = set()
    for _domain, matcher in DOMAIN_PATHS:
        m = matcher.rstrip("/")
        if matcher.endswith("/"):
            roots.add(m)
        else:  # exact file entry -> its containing directory
            roots.add(m.rsplit("/", 1)[0] if "/" in m else m)
    minimal: list[str] = []
    for r in sorted(roots, key=len):
        if not any(r == p or r.startswith(p + "/") for p in minimal):
            minimal.append(r)
    return sorted(minimal)


def _all_domain_files() -> list[Path]:
    files: list[Path] = []
    for sub in _domain_scan_roots():
        d = _REPO_ROOT / sub
        if d.is_dir():
            files.extend(
                p for p in d.rglob("*.py") if "__pycache__" not in p.parts
            )
    # Keep only files that classify into a guarded domain.
    out = []
    for p in files:
        rel = str(p.resolve().relative_to(_REPO_ROOT)).replace("\\", "/")
        if classify_path(rel) is not None:
            out.append(p)
    return sorted(out)


def _diff_files() -> list[Path]:
    res = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    out = []
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line.endswith(".py"):
            continue
        p = _REPO_ROOT / line
        if p.exists() and classify_path(line) is not None:
            out.append(p)
    return out


def verify(paths: list[Path]) -> list[Violation]:
    violations: list[Violation] = []
    for p in paths:
        violations.extend(check_file(p))
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="scan all domain files")
    group.add_argument("--diff", action="store_true", help="scan files changed vs HEAD")
    group.add_argument("--files", nargs="+", help="scan specific files")
    args = parser.parse_args(argv)

    if args.files:
        paths = [Path(f) for f in args.files]
    elif args.diff:
        paths = _diff_files()
    else:  # default and --all both scan everything
        paths = _all_domain_files()

    violations = verify(paths)
    if violations:
        print(f"INTERNAL SEAM VERIFIER: FAIL -- {len(violations)} violation(s):")
        for v in violations:
            print(f"  {v}")
        return 1
    print(f"INTERNAL SEAM VERIFIER: PASS ({len(paths)} file(s) scanned)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
