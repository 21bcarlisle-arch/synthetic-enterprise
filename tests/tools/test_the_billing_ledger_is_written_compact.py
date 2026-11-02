"""The committed billing ledger must fit GitHub's per-file push limit.

Defect: both writers used `json.dumps(result, indent=2)`; the 1,293-account book came to 137 MiB
and the 2 Nov publish was refused before staging. Restore indent=2 in `dump_ledger` and the
first test reds (indent adds whitespace); the second reds if a writer bypasses the helper.
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
    assert src.count("write_text(dump_ledger(result))") == 2
