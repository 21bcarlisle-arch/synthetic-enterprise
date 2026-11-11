"""The committed billing ledger must fit GitHub's per-file push limit.

Defect: both writers used `json.dumps(result, indent=2)`; the 1,293-account book came to 137 MiB
and the 2 Nov publish was refused before staging. Restore indent=2 in `dump_ledger` and the
first test reds (indent adds whitespace); the second reds if a writer bypasses the helper,
whatever store it writes to.
"""
import json
import re
from pathlib import Path

from tools import generate_billing_ledger as gbl


def test_dump_ledger_is_compact_and_round_trips():
    result = {"meta": {"invoice_count": 2}, "customers": {"C1": {"bills": [1, 2]}}}
    text = gbl.dump_ledger(result)
    assert "\n" not in text and ": " not in text
    assert json.loads(text) == result


def test_no_writer_in_the_generator_indents_the_ledger():
    src = Path(gbl.__file__).read_text()
    assert not re.search(r"write_text\(json\.dumps\([^)]*indent", src)
    # Keyed to the property, not to the writer's name: d7c214a392 moved both writers to the gzip
    # store (`ledger_store.write_ledger`) and a count of `write_text(dump_ledger(` read 0, red on every
    # lane that touched the generator. Every ledger write goes through the compact helper.
    writes = re.findall(r"(?<!def )write_ledger\(([^,)]*)", src)
    assert writes, "no ledger writer found: the property is no longer being checked"
    assert all(w.startswith("dump_ledger(") for w in writes), writes
    assert not re.search(r"write_text\(json\.dumps", src)
