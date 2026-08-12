"""ONE way to build a stand-in root the publish gate will actually run against.

WHY THIS MODULE EXISTS (2026-08-12, the eighteenth wedge -- and the seventeenth was the same
defect one file away). `9fbb4dd33` taught `background/publish_scope.py::resolve_scope` to tell
a root that is NOT this repo from a declaration that has rotted, and made the first of those a
REFUSAL: `process_run_complete._run_gate_in` returns `_checkout_unavailable_verdict()` before
argv is ever built. That control is correct. What it also did was silently invalidate every
test fixture that hands the gate a hand-built stand-in tree, because a stand-in tree is, by
construction, exactly the condition the new refusal names.

`2b8a7f0c5` fixed the first such fixture INLINE, in `test_publish_gate_scope.py`. That was an
instance fix, and R10 is explicit that an absurdity-class defect may not be closed with one:
~4 hours later the identical shape reddened HEAD again from `test_publish_gate_subject_is_head
.py`'s `sandbox` fixture, three tests at once, and publishing stayed down. So the shape lives
here now, once, and both fixtures call it.

MATERIALISED FROM THE DECLARATION, never hand-typed: a source added to or moved within
`PUBLISH_PATH_SOURCES`, or a rename of `ROOT_REPO_MARKER`, reaches every stub root through
this function instead of returning one of them to the absent-root branch months later.

`tests/` is created with a FILE inside it. An empty directory is enough for a root built with
`mkdir`, but not for one built the way the real gate builds its subject -- `git archive HEAD`,
which does not carry empty directories -- and both kinds of caller share this helper.
"""
from pathlib import Path

from background.publish_scope import PUBLISH_PATH_SOURCES, ROOT_REPO_MARKER

STUB_SOURCE_TEXT = "# stub of a declared publish-path source\n"
STUB_MARKER_FILE = ".publish-gate-stub-root"


def materialise_repo_shaped_root(root) -> Path:
    """Give `root` the shape `resolve_scope` needs to recognise it as a checkout of this repo.

    Idempotent, and it never overwrites a real file: a caller whose tree already holds one of
    the declared sources (or its own `tests/`) keeps it, so this can be applied to a populated
    stand-in repo as safely as to an empty directory.

    Returns `root` as a Path, so it composes into a fixture's return line.
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    marker_dir = root / ROOT_REPO_MARKER
    marker_dir.mkdir(parents=True, exist_ok=True)
    keep = marker_dir / STUB_MARKER_FILE
    if not keep.exists():
        keep.write_text("stand-in for this repo's `{}/` -- see {}\n".format(
            ROOT_REPO_MARKER, __name__))

    for source in PUBLISH_PATH_SOURCES:
        target = root / source
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text(STUB_SOURCE_TEXT)

    return root
