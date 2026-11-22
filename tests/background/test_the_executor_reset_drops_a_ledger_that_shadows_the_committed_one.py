"""The executor's reset drops an ignored plain ledger that is a different book from the gz.

THE DEFECT THIS FAILS ON (2026-11-22): `/var/tmp/se-seat-executor` kept a scratch plain ledger
(source_json /var/tmp/w14/run.json) through every `git clean -qfd`, it shadowed the committed gz,
and `resolve_ledger` reddened three tests/saas/reporting tests on unchanged origin/main.
"""
from __future__ import annotations

import gzip
import json

from background.seat_executor import drop_a_shadowing_ledger
from company.billing.ledger_store import LEDGER_REL, gz_twin, resolve_ledger


def _book(tree, plain_source, gz_source):
    plain = tree / LEDGER_REL
    plain.parent.mkdir(parents=True, exist_ok=True)
    plain.write_text(json.dumps({"meta": {"source_json": plain_source}, "rows": []}))
    gz_twin(plain).write_bytes(gzip.compress(
        json.dumps({"meta": {"source_json": gz_source}, "rows": []}).encode()))
    return plain


def test_only_a_disagreeing_plain_ledger_is_dropped(tmp_path):
    """One control over both partitions: a plain file that agrees with the gz survives, one that
    disagrees is deleted and the reader then reads the gz. A drop-everything or drop-nothing
    version fails a leg."""
    same = _book(tmp_path / "same", "/runs/a.json", "/runs/a.json")
    stale = _book(tmp_path / "stale", "/var/tmp/w14/run.json", "/runs/a.json")

    kept = drop_a_shadowing_ledger(tmp_path / "same")
    dropped = drop_a_shadowing_ledger(tmp_path / "stale")

    assert kept is None and same.is_file()
    assert dropped and "w14" in dropped and not stale.exists()
    assert resolve_ledger(stale) == gz_twin(stale)


def test_a_tree_with_no_ledger_is_untouched(tmp_path):
    assert drop_a_shadowing_ledger(tmp_path) is None
