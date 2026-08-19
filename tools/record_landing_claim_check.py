"""Does an atom's OWN STORE RECORD claim a landing that the tree does not carry?

THE CLASS THIS CLOSES, and it is R3 territory -- five consecutive passes.
`WORKER_FINDING_THREE_CONSECUTIVE_PASSES_RECORDED_A_LANDING_THAT_IS_IN_NO_COMMIT_2026-08-19`
records passes 12, 13 and 14 of `EP6_wall_protocol_typing` each writing a store record
asserting that three `include_schema_version` call sites had landed. The finding's own
"what this tick did about the instance" paragraph was a FOURTH such record, and the pass
that read it wrote a fifth. At `d1d1e1fc5`,
`git grep -c include_schema_version HEAD -- simulation/` was still empty.

This is recommendation 1 of that finding, and it is the only one that was left unbuilt:
*"a check that answers 'does this atom's own record claim a landing that HEAD does not
carry?' ... red when a record asserts code that `git grep` at the tree cannot find. That
is the control that would have fired at pass 13 instead of pass 13 having to notice by
hand."*

WHY THE TWO SIBLING CONTROLS ARE BOTH BLIND TO IT, and neither is a near miss:

  * `_symbol_landing_check` resolves references that a commit CHANGES. Passes 12-14
    committed no code at all, so there was no changed reference to resolve.
  * `_landed_manifest_check` reads a staging DOCUMENT's prose and checks the PATHS it
    names exist. Every path EP6 named (`simulation/run_phase2b.py`) exists at HEAD and
    always did; what was missing was a symbol INSIDE it. And the claim did not live in
    `docs/staging/` at all -- it lived in the atom's store record, which is where a
    build pass actually makes its promises.

WHY THE CLAIM CARRIES A LOCATION, which is the design's load-bearing decision and was
measured this tick rather than assumed. `include_schema_version` was present at HEAD the
whole time -- in `tools/meter_read_port.py`, its two sibling ports, and their tests. A
control asking "does the tree carry this symbol?" would have been GREEN through all five
false records. The claim EP6 was making was never "this symbol exists"; it was "this
symbol is at these call sites", and the finding's own admissible query says so by being
path-scoped. So the unit of claim here is the PAIR (symbol, path scope), and a claim that
names no scope is not checkable and is refused as such.

WHY THE SYNTAX IS EXPLICIT rather than parsed from prose. The sibling control's scope was
narrowed after it refused the very report announcing it: reading every backticked token as
a claim cannot tell a claim from a CITATION of someone else's defect, or from an honest
NEGATIVE finding. EP6's own record contains the sentence "`include_schema_version` appears
in ZERO call sites" -- true when written, and a prose parser would have billed the pass
that honestly reported the hole. A control that punishes the record for reporting a defect
is a control that stops defects being recorded. So a claim is made in one fixed form and
nowhere else:

    LANDED: `<symbol>` in `<path-prefix>`

CLAUSE 2 is that claim's verification: the symbol must be findable by `git grep` under the
scope, IN THE TREE THIS COMMIT CREATES. Never the working tree -- the working tree is
exactly what made the failure invisible, and on 2026-08-19 at 22:49:00 a concurrent lane
restored both EP6 files to their HEAD contents while HEAD never moved, so the tree lost the
work too.

CLAUSE 1 is what stops clause 2 being FAIL-OPEN by emptiness. An opt-in syntax nobody uses
is not a control. So a record whose newly-written prose asserts a landing must state at
least one claim in the checkable form.

The sibling's prose predicate is REUSED AND EXTENDED, and the extension was forced by
measurement rather than taste: run against the three sentences the real EP6 records
actually used -- "LANDED VIA A WORKTREE SWAP", "ACTUALLY LANDS PASSES 12-14", "Pass 10
LANDED the L2 that pass 9 earned and never committed" -- `asserts_landing` returns False
on all three. Importing it alone would have been a control that could not fire on its own
originating instance. The extension is the shouted-uppercase LANDED/LANDS a build record
uses when it is asserting rather than discussing; the imported patterns are kept beneath it
so the two surfaces do not drift into two different rules.

SCOPE IS THE LINES THIS COMMIT ADDS, not the whole record, and this is the structural
answer to the false-positive the sibling paid for. Read whole, a record is billed forever
for its own history -- EP6's record must be able to go on quoting "pass 12 claimed it
LANDED" as the evidence it is. Read as a diff, the claim surface is exactly what this
author is asserting NOW, which is the only thing they can be held to. It also means an old
stale claim cannot wedge a later unrelated edit to the same record, which is the sibling
controls' "do not bill this committer for other authors' rot" applied at line granularity.

FAIL-CLOSED at every step (R15): a git plumbing failure raises rather than returning "no
findings". An unavailable check is a FAILED check.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

STORE_PREFIX = "docs/design/simplifications/"

# ARCHIVE ROLLS ARE OUT OF POPULATION, and this was measured, not assumed. `8233f3629`
# created `archive/EP1_clv_three_horizon.004.yaml`, whose five "added" lines are text
# RELOCATED from the live record by `simplifications_store.roll_for_atom` -- a mechanical
# two-file write, not an assertion. Under the added-lines rule every rolled line reads as
# newly authored, so an archived note that once said LANDED would refuse the roll, and the
# committer could not comply: the text is history being moved, and editing it to pass would
# be falsifying the archive. Not a fail-open either -- the roll's source is a live note,
# which faced this control when it was written.
ARCHIVE_PREFIX = STORE_PREFIX + "archive/"

# The one checkable form. Deliberately loud and deliberately not prose: a reader skimming a
# record can see which sentences are falsifiable claims and which are discussion.
_LANDED_CLAIM = re.compile(
    r"LANDED:\s*`([^`\n]+)`\s+in\s+`([^`\n]+)`",
)

# A claim line the author STARTED and left unscopeable. Caught separately so it reaches the
# findings list rather than falling silently out of the population -- an unparsed claim is
# the fail-open this control exists to answer.
_LANDED_PREFIX = re.compile(r"LANDED:")

# A symbol is a bare code identifier. Anything else -- a path, a test node id, a sentence --
# is not something `git grep` can answer a landing question about.
_SYMBOL = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# The assertion voice of a build record, measured off the five real EP6 notes rather than
# imagined: a pass that is CLAIMING shouts LANDED/LANDS, a pass that is discussing does not.
# `landed_manifest_check.asserts_landing` is applied as well, never instead -- see the
# module docstring for why importing it alone is a control that cannot fire on its own
# originating instance.
_RECORD_CLAIM_PATTERNS = (
    re.compile(r"\bLANDED\b"),
    re.compile(r"\bLANDS\b"),
)


def _git(args: list[str], root: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(root), capture_output=True, text=True, check=False,
        env=env if env is not None else os.environ.copy(),
    )


def is_symbol_like(token: str) -> bool:
    """Would `git grep` be answering a landing question about this token?"""
    return bool(_SYMBOL.match(token.strip()))


def landing_claims(text: str) -> tuple[list[tuple[str, str]], int]:
    """Every (symbol, scope) pair the record states, plus the count it left unparseable.

    The second element is the control's own error bar. A `LANDED:` the author wrote in a
    shape this parser cannot read is REPORTED, never dropped: dropping it would make the
    control weakest exactly where the author was least careful.
    """
    claims: list[tuple[str, str]] = []
    unparsed = 0
    for line in text.splitlines():
        if not _LANDED_PREFIX.search(line):
            continue
        found = _LANDED_CLAIM.findall(line)
        usable = [(s.strip(), p.strip()) for s, p in found if is_symbol_like(s)]
        if not usable:
            unparsed += 1
            continue
        for pair in usable:
            if pair not in claims:
                claims.append(pair)
    return claims, unparsed


def asserts_landing_in_record(text: str) -> bool:
    """Is this text a build record ASSERTING a landing?"""
    from tools.landed_manifest_check import asserts_landing

    return any(p.search(text) for p in _RECORD_CLAIM_PATTERNS) or asserts_landing(text)


def added_lines(tree: str, since_tree: str, path: str, root: Path, env: dict) -> str:
    """The text this commit ADDS to one record, as the claim surface.

    A record read whole is billed forever for quoting its own history; read as a diff it is
    held to exactly what its author is asserting now. `-U0` because context lines are the
    neighbouring passes' prose, and attributing those to this author is the defect.
    """
    out = _git(
        ["diff", "-U0", "--no-color", since_tree, tree, "--", path], root, env=env
    )
    if out.returncode != 0:
        raise RuntimeError(
            f"git diff for {path} rc={out.returncode}: {out.stderr.strip()[-200:]}"
        )
    return "\n".join(
        line[1:] for line in out.stdout.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


def changed_store_records(tree: str, since_tree: str, root: Path, env: dict) -> list[str]:
    out = _git(["diff-tree", "-r", "--name-only", "--no-commit-id", since_tree, tree], root, env=env)
    if out.returncode != 0:
        raise RuntimeError(
            f"git diff-tree {since_tree}..{tree} rc={out.returncode}: {out.stderr.strip()[-200:]}"
        )
    return sorted(
        p for p in out.stdout.splitlines()
        if p.startswith(STORE_PREFIX)
        and not p.startswith(ARCHIVE_PREFIX)
        and p.endswith((".yaml", ".yml"))
    )


def symbol_is_in_scope(tree: str, symbol: str, scope: str, root: Path, env: dict) -> bool:
    """Does `git grep` find the symbol under this scope, IN THE TREE THE COMMIT CREATES?

    `-F` because a symbol is a literal, not the author's regex. A non-zero rc from git grep
    means "no match" (1) -- anything above that is a plumbing failure and must not be read
    as a clean absence, or the control fails OPEN on its own breakage.
    """
    out = _git(["grep", "-F", "-l", "--", symbol, tree, "--", scope], root, env=env)
    if out.returncode not in (0, 1):
        raise RuntimeError(
            f"git grep for {symbol!r} under {scope!r} at {tree[:9]} "
            f"rc={out.returncode}: {out.stderr.strip()[-200:]}"
        )
    return out.returncode == 0


def run_at_tree(
    tree: str,
    since_tree: str = "HEAD^{tree}",
    root: Path | None = None,
    env: dict | None = None,
) -> tuple[list[str], dict]:
    root = root or PROJECT_DIR
    env = env if env is not None else os.environ.copy()

    findings: list[str] = []
    report: dict = {
        "records_changed": 0,
        "records_claiming_a_landing": 0,
        "claims_checked": 0,
        "unparsed_claims": 0,
    }

    for path in changed_store_records(tree, since_tree, root, env):
        text = added_lines(tree, since_tree, path, root, env)
        if not text.strip():  # deleted, or changed without adding a line: no new claim
            continue
        report["records_changed"] += 1
        claims, unparsed = landing_claims(text)
        report["unparsed_claims"] += unparsed
        for _ in range(unparsed):
            findings.append(
                f"{path}: a `LANDED:` line states no checkable (symbol, scope) pair. "
                "The form is: LANDED: `symbol` in `path/prefix`."
            )
        # CLAUSE 1 -- the anti-fail-open. Prose asserting a landing with no claim in the
        # checkable form is exactly the shape all five EP6 records took.
        if asserts_landing_in_record(text):
            report["records_claiming_a_landing"] += 1
            if not claims and not unparsed:
                findings.append(
                    f"{path}: the record asserts a landing in prose and states no "
                    "falsifiable claim. Add: LANDED: `symbol` in `path/prefix` -- so the "
                    "NEXT pass can refute it without trusting the prose."
                )
        # CLAUSE 2 -- the claim against the tree this commit creates.
        for symbol, scope in claims:
            report["claims_checked"] += 1
            if not symbol_is_in_scope(tree, symbol, scope, root, env):
                findings.append(
                    f"{path}: claims `{symbol}` landed in `{scope}`, and the tree this "
                    f"commit creates does not carry it there. "
                    f"(git grep -F {symbol} <tree> -- {scope} finds nothing.) "
                    "Land the code in this commit, or do not write the claim."
                )
    return findings, report


def _resolve_tree(ref: str, root: Path, env: dict) -> str:
    out = _git(["rev-parse", f"{ref}^{{tree}}"], root, env=env)
    if out.returncode != 0:
        raise RuntimeError(f"cannot resolve {ref} to a tree: {out.stderr.strip()[-200:]}")
    return out.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(
        prog="record_landing_claim_check",
        description=(
            "Refuse a store record that claims a symbol landed at a location the tree does "
            "not carry."
        ),
    )
    ap.add_argument("--tree", default="HEAD", help="the tree to check (default HEAD)")
    ap.add_argument("--since-tree", default="HEAD^", help="the tree to diff against")
    args = ap.parse_args(argv)

    root = PROJECT_DIR
    env = os.environ.copy()
    tree = _resolve_tree(args.tree, root, env)
    since = _resolve_tree(args.since_tree, root, env)
    findings, report = run_at_tree(tree, since, root, env)
    for f in findings:
        print(f"  - {f}")
    print(
        f"[record-landing-claim] {report['claims_checked']} claim(s) in "
        f"{report['records_changed']} changed record(s); "
        f"{report['records_claiming_a_landing']} assert a landing; "
        f"{report['unparsed_claims']} unparsed."
    )
    return 1 if findings else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
