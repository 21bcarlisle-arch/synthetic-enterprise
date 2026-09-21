"""The publish cadence is `publish_freshness.PUBLISH_CADENCE_SECONDS`, and the tree may not grow
a second constant of that name.

WHY THIS EXISTS. On 2026-09-04 the director named the publishing cadence — *"The site publishes
numbers and runs once a week, thoroughly and robustly, not every half hour ... The reason is
cost."* — and `background/publish_freshness.py` recorded it at 604,800s under a comment declaring
itself *"the SINGLE SOURCE OF TRUTH for that cadence"*.

**That sentence was false on the day it was written.** `background/suite_duration_watch.py` already
held a constant with the identical name at 5,400s, and stamped it into
`docs/observability/publish_gate_duration.jsonl` under the same field name `publish_freshness`
uses in its own snapshot, `cadence_seconds`. Two live quantities, one word, **112x apart**, for
seventeen days, with nothing in the tree able to notice — the VAT-rule class CLAUDE.md names: one
rule, several implementations, and no edge between them.

IT WAS NOT COSMETIC. `tools/settlement_ceiling_probe.publisher_context()` read `cadence_seconds`
out of that JSONL and `recommend()` spent it as the publish interval the settlement ceiling is
priced against. Run duration SETS marker inter-arrival, so that bound grows whenever the ceiling it
bounds grows — the exact circularity `net_new_acquisition`'s own note records as removed, re-entered
through a second door nobody re-asked. Against 5,400s the binding leg is TIME; against 604,800s it
is MEMORY. **The two answers differ in kind, not degree.**

WHAT THE REPAIR WAS, because it was not picking a winner. The two numbers were never one quantity:
one is a DECISION (how often we publish, his), the other an OBSERVATION (how often runs arrive,
the book's). `suite_duration_watch`'s is now `MEASURED_RUN_ARRIVAL_SECONDS` writing
`measured_arrival_seconds`. Nothing there was wrong except its name.

WHY A CONTROL AND NOT JUST THE RENAME. The rename fixes today's instance; this file is what makes
the "single source of truth" claim CHECKABLE instead of merely asserted. A comment cannot see a
rival — that is precisely how seventeen days passed — so the claim needs something that reds when a
second home appears. **Keyed to the property (one definition of the name), not to today's two
modules**, so it still fires for a third module nobody has written yet.

R15 — WHAT KILLS IT. Re-add `PUBLISH_CADENCE_SECONDS = 5400` to `suite_duration_watch.py`, or
define it in any new module, and `test_only_one_module_defines_the_publish_cadence` reds naming the
file. Re-add a `"cadence_seconds"` writer to `suite_duration_watch.record()` and
`test_the_gate_duration_series_does_not_write_the_cadence_field` reds. Both mutations were run
against this file before it landed; both kill it.

A DEFINITION, NOT A MENTION, is what is counted — prose discussing the name is how the repair gets
explained, and a control that forbade the words would forbid its own explanation. So the pattern
is an assignment at module scope, and `test_the_control_ignores_a_mere_mention` proves the
distinction can be told apart rather than assuming it.
"""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent

CADENCE_NAME = "PUBLISH_CADENCE_SECONDS"

#: The one legitimate home, relative to the project root. Not an allowlist that grows: the point
#: of the control is that this stays length one, so a second entry is a decision someone has to
#: argue for in a diff rather than a line they can quietly append.
THE_ONE_HOME = "background/publish_freshness.py"


def _tracked_python_files() -> list[Path]:
    """Every tracked `.py` in the tree, asked of git rather than walked.

    ASKED OF GIT ON PURPOSE. A filesystem walk picks up other lanes' untracked scratch and
    `.venv`, so the control's verdict would depend on who else was mid-turn — a red that is
    artefact locality rather than a defect. `git ls-files` answers about the repository.
    """
    out = subprocess.run(
        ["git", "-C", str(PROJECT), "ls-files", "*.py"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [PROJECT / line for line in out.splitlines() if line.strip()]


def _module_scope_assignments(path: Path, name: str) -> bool:
    """Does this file ASSIGN `name` at module scope? Parsed, never grepped.

    READ AS CODE, NOT AS TEXT (the `test_a_control_reads_python_as_code` doctrine). A grep for
    the name matches every comment that explains the rule — including this repair's own notes in
    both modules — so a text control would have to choose between being vacuous and reding on its
    own documentation. The AST can tell an assignment from a sentence.

    FAILS CLOSED: a file that will not parse is REPORTED as a defect rather than skipped, because
    "we could not look" reading as "nothing there" is the fail-open shape this repo keeps paying
    for. An unparseable file is surfaced by raising, so it cannot pass silently.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        for t in targets:
            if isinstance(t, ast.Name) and t.id == name:
                return True
    return False


def test_only_one_module_defines_the_publish_cadence():
    """The property: exactly one definition, and it is the declared one.

    This is the leg that would have fired on 2026-09-04 and did not exist to.
    """
    definers = []
    unparseable = []
    for path in _tracked_python_files():
        try:
            if _module_scope_assignments(path, CADENCE_NAME):
                definers.append(str(path.relative_to(PROJECT)))
        except SyntaxError as exc:  # noqa: PERF203 - the reason belongs to the file
            unparseable.append(f"{path.relative_to(PROJECT)}: {exc}")

    assert not unparseable, (
        "Could not read these files as code, so this control cannot answer for them. An "
        "unavailable check is a FAILED check, never a pass:\n  " + "\n  ".join(unparseable)
    )
    assert definers == [THE_ONE_HOME], (
        f"`{CADENCE_NAME}` must be defined in exactly one place — {THE_ONE_HOME}, which carries "
        f"the director's 2026-09-04 declaration. Found it defined in: {definers}.\n\n"
        "If the new one is the MEASURED interval between sim runs rather than the DECLARED "
        "publishing cadence, it is a different quantity and needs a different name: see "
        "`suite_duration_watch.MEASURED_RUN_ARRIVAL_SECONDS`, which is what that mistake cost "
        "the settlement ceiling for seventeen days. If it genuinely is the publishing cadence, "
        "import it from its home rather than restating it — `background/sim_runner.py` and "
        "`background/supervisor.py` both show the shape."
    )


def test_the_gate_duration_series_does_not_write_the_cadence_field():
    """The FIELD is half the defect, and renaming only the symbol would have left it live.

    Nobody imported `suite_duration_watch.PUBLISH_CADENCE_SECONDS` across a module boundary. The
    probe reached it by reading `cadence_seconds` out of the JSONL the watcher stamps — so the
    collision that actually cost something was between two artefacts' FIELD names, not between
    two symbols. A control over the symbols alone would pass while the damage continued.

    Historical rows keep the old key and must: `row_arrival_seconds()` reads it as DATA, and
    rewriting 5,570 rows to fix a name would destroy the one property that key exists for. What
    is forbidden is a WRITER, and this reads the writer.
    """
    src = (PROJECT / "background" / "suite_duration_watch.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    record = next(
        (n for n in ast.walk(tree)
         if isinstance(n, ast.FunctionDef) and n.name == "record"), None)
    assert record is not None, "suite_duration_watch.record() is gone — this control lost its subject"

    written_keys = {
        k.value for node in ast.walk(record) if isinstance(node, ast.Dict)
        for k in node.keys if isinstance(k, ast.Constant) and isinstance(k.value, str)
    }
    assert "cadence_seconds" not in written_keys, (
        "`suite_duration_watch.record()` writes `cadence_seconds` into "
        "publish_gate_duration.jsonl. `publish_freshness.snapshot()` writes a field of the SAME "
        "name carrying the DECLARED weekly cadence, 112x larger. One field name over two "
        "quantities is how `settlement_ceiling_probe` priced the settlement ceiling on the "
        "circular ruler. Write `measured_arrival_seconds`."
    )
    assert "measured_arrival_seconds" in written_keys, (
        "The arrival interval must still be STORED on the row — a re-measurement must not "
        "silently change what historical rows mean. Only its NAME was the defect."
    )


def test_the_control_ignores_a_mere_mention(tmp_path):
    """A mention is not a definition, and the distinction has to be demonstrable.

    Without this leg the control above could be passing for the wrong reason — a pattern so
    narrow it matches nothing would satisfy it just as well as a correct one. Both arms are
    driven over one synthetic module, which is the whole-partition shape CLAUDE.md asks for
    rather than a leg per branch.

    ON SYNTHETIC INPUT, NOT ON THE REAL FILE, AND THE FIRST DRAFT GOT THIS WRONG. That draft
    asserted the name appeared in `publish_freshness`'s own prose — which meant reading Python
    source as TEXT, and `test_a_control_reads_python_as_code::test_the_floor_holds` refused the
    commit by name. It was right to. The check was also keyed to today's prose, so it would have
    gone red the day someone reworded a comment that the code did not depend on — a control
    pinned to today's answer rather than to the property.

    Synthetic input is strictly stronger anyway: the real file cannot exercise the FALSE arm on
    demand, so a `_module_scope_assignments` that returned True for everything would still have
    to be caught by luck. Here both arms are constructed, and the mention is placed in the three
    shapes that actually occur — a comment, a docstring, and a nested (non-module-scope)
    assignment, which is the one a naive AST walk would report as a definition.
    """
    mod = tmp_path / "synthetic_module.py"
    mod.write_text(
        '"""A docstring naming DECOY_NAME, which this module does not define."""\n'
        "# A comment naming DECOY_NAME too.\n"
        "REAL_NAME = 604800\n"
        "\n"
        "def f():\n"
        "    DECOY_NAME = 5400  # a LOCAL binding, not a module-scope definition\n"
        "    return DECOY_NAME\n",
        encoding="utf-8",
    )
    assert _module_scope_assignments(mod, "REAL_NAME"), (
        "The control misses a plain module-scope assignment, so every 'only one home' verdict it "
        "has ever given was vacuous."
    )
    assert not _module_scope_assignments(mod, "DECOY_NAME"), (
        "The control cannot tell a mention from a definition: it reports a definition for a name "
        "that appears only in a comment, a docstring and a function-local binding. Every verdict "
        "it gives is therefore untrustworthy."
    )
    # And the real home is genuinely the room being guarded, not an empty one.
    assert _module_scope_assignments(PROJECT / THE_ONE_HOME, CADENCE_NAME), (
        "The declared cadence is no longer assigned at module scope in its own home. If it moved, "
        "THE_ONE_HOME above is stale and the control is now guarding an empty room."
    )
