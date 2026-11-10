"""The billing ledger is committed gzipped, every reader reads either form, and the plain copy is
retired from HEAD by the shared tree's own publish.

THE DEFECT THIS FAILS ON: `docs/state/billing_ledger.json` was 91,168,764 bytes on the 0a6391d186
book, 87% of GitHub's 104,857,600-byte push limit, and growing with every fix. A refused push
stops the publisher. Triage row `the-billing-ledger-outgrows-githubs-file-limit`.
"""
from __future__ import annotations

import gzip
import json
import re
import subprocess
from pathlib import Path

import pytest

import background.process_run_complete as prc
from company.billing import ledger_store as store
from tools.generate_billing_ledger import dump_ledger

#: "No tracked file over 50 MiB from the ledger writer" -- half GitHub's limit, so a book that
#: doubles still pushes.
FIFTY_MIB = 50 * 1024 * 1024


def test_the_reader_takes_the_plain_file_and_falls_back_to_the_gz(tmp_path):
    """Both branches, one control: plain preferred when present, gz when it is not, refusal when
    neither. A reader that only ever read one form fails a leg."""
    plain = tmp_path / "billing_ledger.json"
    plain.write_text(json.dumps({"which": "plain"}))
    store.gz_twin(plain).write_bytes(gzip.compress(json.dumps({"which": "gz"}).encode()))

    taken = {store.load_ledger(plain)["which"]}
    plain.unlink()
    taken.add(store.load_ledger(plain)["which"])
    assert taken == {"plain", "gz"}, taken

    store.gz_twin(plain).unlink()
    with pytest.raises(FileNotFoundError, match=r"billing_ledger\.json\.gz"):
        store.load_ledger(plain)


def test_the_gz_is_deterministic_and_a_changed_ledger_rewrites_it(tmp_path):
    """Same ledger, same bytes -- else every publish commits a changed blob for an unchanged book."""
    plain = tmp_path / "billing_ledger.json"
    text = json.dumps({"customers": {"C%d" % i: {} for i in range(1000)}}, separators=(",", ":"))
    first = store.write_ledger(text, plain).read_bytes()
    store.gz_twin(plain).unlink()
    assert store.write_ledger(text, plain).read_bytes() == first
    # Two writes inside one second agree whatever the header says, so key on the header itself:
    # gzip's MTIME field (bytes 4-7) is zero, not the clock.
    assert first[4:8] == b"\x00\x00\x00\x00", first[4:8]
    store.write_ledger('{"customers":{}}', plain)
    assert store.load_ledger(store.gz_twin(plain)) == {"customers": {}}, (
        "a changed ledger must rewrite the gz, not keep the old one")


def _committed_ledger_bytes() -> bytes:
    """The ledger HEAD carries, plain bytes, in whichever form HEAD carries it."""
    for rel, unpack in ((store.LEDGER_REL, lambda b: b), (store.PUBLISHED_REL, gzip.decompress)):
        done = subprocess.run(["git", "show", "HEAD:" + rel], cwd=store.PROJECT,
                              capture_output=True, check=False)
        if done.returncode == 0:
            return unpack(done.stdout)
    pytest.fail("HEAD carries the billing ledger in neither form ({} nor {})".format(
        store.LEDGER_REL, store.PUBLISHED_REL))


def test_the_committed_book_reassembles_byte_for_byte_and_its_gz_is_under_50_mib(tmp_path):
    """The named book is whatever HEAD commits (0a6391d186's 1,293 accounts when written). Through
    the real writer: the gz decompresses to the plain bytes exactly, a gz-only checkout's reader
    returns a ledger the generator's own serialiser writes back to those same bytes, and the
    committed form is under half GitHub's limit."""
    plain_bytes = _committed_ledger_bytes()
    plain = tmp_path / "billing_ledger.json"
    twin = store.write_ledger(plain_bytes.decode("utf-8"), plain)
    assert gzip.decompress(twin.read_bytes()) == plain_bytes

    plain.unlink()  # a worktree, a gate extract, a clone
    ledger = store.load_ledger(plain)
    book = ledger.get("meta", {}).get("source_json")
    assert dump_ledger(ledger).encode("utf-8") == plain_bytes, book
    assert twin.stat().st_size < FIFTY_MIB, (book, twin.stat().st_size)


def test_the_generator_writes_both_forms_from_the_same_bytes(tmp_path):
    from tools.generate_billing_ledger import generate

    run = tmp_path / "run.json"
    run.write_text(json.dumps({"bills": []}))
    out = tmp_path / "state" / "billing_ledger.json"
    generate(run, out)
    assert gzip.decompress(store.gz_twin(out).read_bytes()) == out.read_bytes()


def test_the_arrears_view_reads_a_gz_only_checkout(tmp_path):
    from saas.reporting.arrears_ledger import load

    plain = tmp_path / "billing_ledger.json"
    store.write_ledger(json.dumps({"customers": {"C1": {"arrears_history": []}}}), plain)
    plain.unlink()
    view = load(plain)
    assert view.available, view.unavailable_reason


def _repo(tmp_path: Path, *, plain_tracked: bool) -> Path:
    root = tmp_path / ("tracked" if plain_tracked else "retired")
    plain = root / store.LEDGER_REL
    plain.parent.mkdir(parents=True)
    store.write_ledger("{}", plain)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    if plain_tracked:
        subprocess.run(["git", "add", "--", store.LEDGER_REL], cwd=root, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x"],
                       cwd=root, check=True)
    return root


@pytest.mark.parametrize("plain_tracked", [True, False])
def test_the_publish_retires_the_plain_ledger_only_while_head_still_carries_it(
        tmp_path, monkeypatch, plain_tracked):
    """The publish stages `docs/state` as a DIRECTORY, so the gz arrives by that and not by name.
    While the plain ledger is at HEAD the landing removes it (content None, declared in `drops`);
    once retired it passes nothing extra. Both arms run, so a retirement that never fires (a
    by-name-only coverage check) or fires every cycle is red."""
    from tools import surgical_land

    root = _repo(tmp_path, plain_tracked=plain_tracked)
    seen = {}

    def fake_land(root_, paths, message, attempts=None, on_lost=None, **kw):
        seen["paths"], seen["kw"] = list(paths), kw
        return "f" * 40

    monkeypatch.setattr(prc, "PROJECT_DIR", root)
    monkeypatch.setattr(prc, "log", lambda *a, **k: None)
    monkeypatch.setattr(prc, "_wait_for_a_quiet_tree", lambda *a, **k: {"waited_seconds": 0})
    monkeypatch.setattr(prc, "_record_commit_hook_duration", lambda *a, **k: None)
    monkeypatch.setattr(surgical_land, "land", fake_land)

    prc._land_publish_commit([str(root / "docs" / "state")], "msg", "abc1234")

    if plain_tracked:
        assert seen["kw"] == {"content": {store.LEDGER_REL: None},
                              "drops": frozenset({store.LEDGER_REL})}, seen
        assert store.LEDGER_REL in seen["paths"]
    else:
        assert seen["kw"] == {}, seen
        assert store.LEDGER_REL not in seen["paths"]
    assert (root / store.LEDGER_REL).is_file(), "the plain file on disk is never touched"


def test_the_plain_ledger_is_gitignored_once_retired():
    """Else the publish's `docs/state` directory add re-commits the plain file the cycle after it
    was retired."""
    done = subprocess.run(["git", "check-ignore", "--no-index", "-q", store.LEDGER_REL],
                          cwd=store.PROJECT, check=False)
    assert done.returncode == 0


_READER_ROOTS = ("tools", "background", "company", "saas")
_LEDGER_CONST = re.compile(r"^\s*(\w+)\s*=\s*.*[\"']billing_ledger\.json[\"']\)?\s*$", re.M)


def test_no_reader_opens_the_plain_ledger_path_itself():
    """Every name bound to the ledger's path is read through `ledger_store`: a direct
    `.read_text()`, `.exists()` or `.is_file()` on it reads nothing (or skips) in a checkout
    that has only the committed gz. Census over the production roots."""
    offenders, constants = [], 0
    for root in _READER_ROOTS:
        for path in sorted((store.PROJECT / root).rglob("*.py")):
            text = path.read_text(encoding="utf-8", errors="replace")
            for name in set(_LEDGER_CONST.findall(text)):
                constants += 1
                hit = re.search(r"\b{}\.(read_text|read_bytes|exists|is_file|open)\(".format(
                    re.escape(name)), text)
                if hit:
                    offenders.append("{}: {}.{}()".format(
                        path.relative_to(store.PROJECT), name, hit.group(1)))
    assert constants >= 10, "the census found {} ledger path names; its pattern has rotted".format(
        constants)
    assert not offenders, offenders
