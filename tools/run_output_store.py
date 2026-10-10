"""The published run output is committed gzipped; this is the one place that knows it.

WHY (2026-10-10). The publish commits the run beside the site it feeds, and GitHub refuses any blob
over 100 MiB at push. The run reached 123.5 MB at indent=2; compact JSON bought 91.6 MB, 12.6%
headroom on a book that had just grown 4.6x in a week. gzip of the same run is 11.5 MB. See
docs/staging/SEAT_FINDING_THE_PUBLISHED_RUN_OUTGREW_GITHUBS_FILE_LIMIT_2026-10-10.md.

TWO NAMES, ONE RUN. `sim_runner` still byte-copies each run onto `run_output_latest.json`, and the
shared tree keeps that file on disk (gitignored once retired, by `run_output_*.json`). What is
COMMITTED is `run_output_latest.json.gz`, written from that file by the publish. So:

  * the shared tree has the plain file, possibly NEWER than the committed gz (a run not yet
    published) -- which is exactly what the plain file meant before this change;
  * every other checkout (a worktree, a gate extract, a clone) has only the gz.

`load_run_output(path)` therefore prefers the plain file and falls back to `<path>.gz`, so a reader
that names the old path keeps working in both places. A reader that wants the COMMITTED bytes
(the reproducibility control) asks git for `PUBLISHED_REL` and calls `loads_run_output`.
"""
from __future__ import annotations

import gzip
import json
import os
import subprocess
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]

#: The run file `sim_runner` writes, repo-relative. Not committed once the publish has retired it.
LATEST_REL = "docs/reports/run_output_latest.json"
#: What the publish commits in its place.
PUBLISHED_REL = LATEST_REL + ".gz"

#: gzip's default. The header's mtime is pinned to 0 (below), so the same run always gzips to the
#: same bytes and an unchanged run is not a changed blob on every publish.
_COMPRESSLEVEL = 9


def gz_twin(path: Path | str) -> Path:
    """`<path>.gz` -- where the committed copy of a plain run file lives."""
    path = Path(path)
    return path if path.suffix == ".gz" else path.with_name(path.name + ".gz")


def resolve_run_output(path: Path | str) -> Path | None:
    """The file `load_run_output(path)` would read, or None when neither form exists."""
    path = Path(path)
    if path.is_file():
        return path
    twin = gz_twin(path)
    return twin if twin.is_file() else None


def loads_run_output(raw: bytes | str) -> dict:
    """Parse run-output bytes in either form. gzip is recognised by its magic, not by a name."""
    if isinstance(raw, str):
        return json.loads(raw)
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def load_run_output(path: Path | str) -> dict:
    """Load a run output from `path`, or from `<path>.gz` when the plain file is absent.

    Refuses by name when neither exists, so a reader that used to see a FileNotFoundError on one
    path is told both places that were looked in.
    """
    found = resolve_run_output(path)
    if found is None:
        raise FileNotFoundError(
            "no run output at {} nor at {}".format(path, gz_twin(path)))
    return loads_run_output(found.read_bytes())


def as_plain_file(path: Path | str, scratch_dir: Path | str) -> Path:
    """A plain-JSON path holding the run at `path`: `path` itself when it is on disk, else its gz
    decompressed into `scratch_dir`. For callers that hand a PATH to code which cannot import this
    module -- `company/` reads files and may not reach `tools/`."""
    found = resolve_run_output(path)
    if found is None:
        raise FileNotFoundError("no run output at {} nor at {}".format(path, gz_twin(path)))
    if found.suffix != ".gz":
        return found
    out = Path(scratch_dir) / Path(path).name
    out.write_bytes(gzip.decompress(found.read_bytes()))
    return out


def write_published(plain: Path | str) -> Path:
    """Gzip `plain` to `<plain>.gz` deterministically, atomically. Returns the gz path.

    Rewrites only when the content changed, so an unchanged run leaves the committed blob alone.
    """
    plain = Path(plain)
    twin = gz_twin(plain)
    data = plain.read_bytes()
    if twin.is_file():
        try:
            if gzip.decompress(twin.read_bytes()) == data:
                return twin
        except (OSError, EOFError):
            pass  # a truncated gz is rewritten, not trusted
    packed = gzip.compress(data, compresslevel=_COMPRESSLEVEL, mtime=0)
    fd, tmp = tempfile.mkstemp(prefix=twin.name + ".", dir=str(twin.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(packed)
        os.replace(tmp, twin)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return twin


def plain_copy_is_tracked(root: Path | str = PROJECT) -> bool:
    """Is the plain run file still committed at HEAD? True until the first gz publish retires it.

    The retirement happens INSIDE the shared tree's own publish (a content-None landing, file left
    on disk), never as a deletion landed from elsewhere: the shared tree's copy is routinely dirty,
    and `merge --ff-only` refuses a deletion of a dirty file, which would wedge the reconciler.
    """
    done = subprocess.run(["git", "ls-files", "--error-unmatch", "--", LATEST_REL],
                          cwd=str(root), capture_output=True, text=True, check=False)
    return done.returncode == 0
