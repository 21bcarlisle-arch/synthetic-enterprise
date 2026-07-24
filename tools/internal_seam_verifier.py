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
The mutation test in tests/tools/test_internal_seam_verifier.py plants a fresh
cross-domain import and asserts this verifier flags it.
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


def _all_domain_files() -> list[Path]:
    files: list[Path] = []
    for sub in ("company/billing", "company/pricing", "company/market"):
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
