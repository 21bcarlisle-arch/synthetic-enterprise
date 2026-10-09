"""`tools.run_annual_report.write_json_list_indented` replaced `path.write_text(json.dumps(events,
indent=2))` for the ledger dump on the promise that the file's BYTES do not change -- only the
peak memory of writing it. Each test names the defect it catches.
"""
import json

from tools.run_annual_report import write_json_list_indented

_EVENTS = [
    {"transaction_id": "settlement-C1-2019-01-01-1", "event_type": "settlement_event",
     "amount_gbp": -0.1234567890123, "volume_kwh": 3.5, "settlement_period": 1,
     "nested": {"a": [1, 2, {"b": None}], "c": []}, "empty": {}, "text": 'line\nbreak \u00e9 "q"'},
    {"transaction_id": "billing-C2", "event_type": "billing_event", "amount_gbp": 12.0,
     "flag": True, "list": [], "deep": [[[]]]},
    {},
    [],
    "a string element",
    3.14,
]


def test_the_file_is_byte_identical_to_dumps_with_indent_two(tmp_path):
    """Fires on: any drift in nesting, separators or the closing bracket -- the published
    ledger_latest.json changing shape while every figure in it stays the same."""
    path = tmp_path / "ledger.json"
    write_json_list_indented(path, _EVENTS)
    assert path.read_text(encoding="utf-8") == json.dumps(_EVENTS, indent=2)


def test_an_empty_ledger_is_written_as_dumps_writes_it(tmp_path):
    """Fires on: writing `[\\n\\n]` (or nothing) for an empty run, which `dumps` writes as `[]`."""
    path = tmp_path / "ledger.json"
    write_json_list_indented(path, [])
    assert path.read_text(encoding="utf-8") == json.dumps([], indent=2)
