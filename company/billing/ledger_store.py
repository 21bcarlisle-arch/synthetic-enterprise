"""The billing ledger is committed gzipped; this is the one place that knows its two forms.

WHY (2026-11-10). `docs/state/billing_ledger.json` was 91,168,764 bytes compact on the 0a6391d186
book (3 Nov), 87% of GitHub's 104,857,600-byte per-file push limit, and every fix this stretch
adds rows to it. A refused push stops the publisher. gzip -9 of the same bytes is 6,796,846 (6.5%
of the limit). Triage row `the-billing-ledger-outgrows-githubs-file-limit` in
docs/direction/wrong_triage.yaml; the run output took the same road on 2026-10-10
(`tools/run_output_store.py`, which `company/` may not import -- hence this module).

TWO FORMS, ONE LEDGER. The generator writes the plain file AND `<plain>.gz` from the same bytes.
The publish commits the gz and retires the plain file from HEAD (`background.process_run_complete
._land_publish_commit`); the plain file stays on disk in the shared tree, gitignored. So the shared
tree has both, and every other checkout (a worktree, a gate extract, a clone) has only the gz.
`load_ledger` prefers the plain file and falls back to the gz, so a reader works in both places.
"""
from __future__ import annotations

import gzip
import json
import os
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]

#: What the generator writes and the shared tree's readers have always read. Not committed.
LEDGER_REL = "docs/state/billing_ledger.json"
#: What the publish commits in its place.
PUBLISHED_REL = LEDGER_REL + ".gz"
LEDGER_PATH = PROJECT / LEDGER_REL

#: The header's mtime is pinned to 0, so an unchanged ledger gzips to the same bytes and is not a
#: changed blob on every publish.
_COMPRESSLEVEL = 9


def gz_twin(path: Path | str) -> Path:
    """`<path>.gz` -- where the committed copy of a plain ledger lives."""
    path = Path(path)
    return path if path.suffix == ".gz" else path.with_name(path.name + ".gz")


def resolve_ledger(path: Path | str | None = None) -> Path | None:
    """The file `load_ledger(path)` would read, or None when neither form exists."""
    path = Path(path) if path is not None else LEDGER_PATH
    if path.is_file():
        return path
    twin = gz_twin(path)
    return twin if twin.is_file() else None


def loads_ledger(raw: bytes | str) -> dict:
    """Parse ledger bytes in either form. gzip is recognised by its magic, not by a name."""
    if isinstance(raw, bytes) and raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def load_ledger(path: Path | str | None = None) -> dict:
    """Load the ledger at `path` (default: the published one), or `<path>.gz` when the plain file
    is absent. Refuses by name, naming both places it looked."""
    path = Path(path) if path is not None else LEDGER_PATH
    found = resolve_ledger(path)
    if found is None:
        raise FileNotFoundError("no billing ledger at {} nor at {}".format(path, gz_twin(path)))
    return loads_ledger(found.read_bytes())


def _replace_atomically(target: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(prefix=target.name + ".", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_ledger(text: str, path: Path | str | None = None) -> Path:
    """Write the plain ledger at `path` and its gz twin from the same bytes. Returns the gz path.

    The gz is rewritten only when its content changed, so an unchanged ledger leaves the committed
    blob alone."""
    path = Path(path) if path is not None else LEDGER_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode("utf-8")
    path.write_bytes(data)
    twin = gz_twin(path)
    if twin.is_file():
        try:
            if gzip.decompress(twin.read_bytes()) == data:
                return twin
        except (OSError, EOFError):
            pass  # a truncated gz is rewritten, not trusted
    _replace_atomically(twin, gzip.compress(data, compresslevel=_COMPRESSLEVEL, mtime=0))
    return twin
