"""The shadow page's population-anchoring rows must read keys the producer emits.

WORKER_FINDING_A_PUBLISHED_ARREARS_ROW_READS_A_KEY_THAT_IS_NOT_EMITTED_2026-08-12:
`tools/generate_shadow_html.py` rendered each "Arrears <year>" row from
`check.get("arrears_pct", 0)`, a key `tools/population_anchor.py` has never emitted.
Every year printed 0.00% -- a default dressed as a reading -- beside a genuine
AMBER/RED chip computed from a rate the reader could not see.

R15: each control here is paired with the mutation that must make it fire.

  * test_rendered_arrears_row_carries_the_payloads_own_rate
        <- MUTATION test_..._fires_when_the_producer_renames_its_key
           (rename `new_arrears_rate_pct` in the payload = exactly the producer-side
            rename the old `.get(k, 0)` swallowed)
  * test_every_numeric_key_the_page_reads_is_emitted_by_the_producer
        <- MUTATION test_..._fires_on_a_key_the_producer_does_not_emit
  * test_live_population_anchoring_artefact_carries_every_key_the_page_reads
        (the published artefact, not a fixture -- this is the population the
         finding was found on; a missing file FAILS, it does not skip: an
         unavailable check is a failed check)
  * test_unavailable_ledger_renders_no_rate_at_all
        <- MUTATION test_..._fires_if_the_cell_falls_back_to_a_number
"""
import json

import pytest

from tools.generate_shadow_html import (
    POPULATION_ANCHORING_NUMERICS,
    PROJECT,
    _arrears_value,
    _payload_num,
    _population_anchoring_rag,
)
from tools.population_anchor import _arrears_check_by_year

LIVE_ARTEFACT = PROJECT / "site" / "state" / "population_anchoring.json"

# Two residential customers and two I&C, so `use_ic` is true and the RAG basis is the
# 10-year aggregate I&C rate -- the pairing the finding names as the third mismatch.
_LEDGER = {
    "customers": {
        "C1": {"segment": "residential", "arrears_history": [{"opened_date": "2023-04-01"}]},
        "C2": {"segment": "residential", "arrears_history": []},
        "C_IC1": {"segment": "ic", "arrears_history": [{"opened_date": "2023-06-01"}]},
        "C_IC2": {"segment": "ic", "arrears_history": []},
    }
}
_YEARS = {"2023": {"active_customer_ids": ["C1", "C2", "C_IC1", "C_IC2"]}}


def _produced():
    rows = _arrears_check_by_year(_LEDGER, _YEARS)
    assert rows, "fixture must produce at least one arrears row"
    return rows


def _render(rows):
    return _population_anchoring_rag({"overall_rag": "AMBER", "arrears_vs_benchmark": rows})


def test_rendered_arrears_row_carries_the_payloads_own_rate():
    rows = _produced()
    row = rows[0]
    # 2 of 4 active customers opened arrears in 2023.
    assert row["new_arrears_rate_pct"] == 50.0
    html = _render(rows)
    assert "50.00%" in html
    assert "<td>0.00%</td>" not in html


def test_rendered_arrears_row_fires_when_the_producer_renames_its_key():
    """MUTATION: the producer renames its rate field. The old renderer printed
    0.00% and stayed green; the row must now refuse to print a number."""
    rows = _produced()
    rows[0]["renamed_arrears_rate_pct"] = rows[0].pop("new_arrears_rate_pct")
    html = _render(rows)
    assert "50.00%" not in html
    assert "0.00%" not in html
    assert "&#8212;" in html


def test_the_row_states_the_basis_its_rag_was_computed_from():
    rows = _produced()
    row = rows[0]
    # Per-year overall rate 50.0; RAG basis is the 10yr aggregate I&C rate, 50.0 here
    # only if every I&C customer-year is in arrears -- 1 of 2, so 50.0. Force a
    # divergence to prove the note appears when the two genuinely differ.
    row["rag_basis_pct"] = 13.5
    row["rag_basis_label"] = "10yr aggregate I&C rate"
    html = _render([row])
    assert "RAG basis: 10yr aggregate I&amp;C rate 13.50%" in html or "RAG basis: 10yr aggregate I&C rate 13.50%" in html


def test_the_basis_note_is_absent_when_it_would_restate_the_row():
    rows = _produced()
    row = rows[0]
    row["rag_basis_pct"] = row["new_arrears_rate_pct"]
    assert "RAG basis" not in _render([row])


def test_every_numeric_key_the_page_reads_is_emitted_by_the_producer():
    """The class control: the page's declared numeric reads must exist in what the
    producer writes. Scoped here to the arrears block, which this test can produce
    hermetically; the other blocks are covered against the live artefact below."""
    _declared_keys_are_emitted(POPULATION_ANCHORING_NUMERICS, _produced())


def _declared_keys_are_emitted(declared, rows):
    """The control above, over an INJECTED declaration list. Both the real test and its
    mutation run this same body, so the mutation exercises the shipped logic rather than
    a copy of it -- a mutation that re-asserts inline proves only that `assert` works."""
    wanted = [k for block, k in declared if block == "arrears_vs_benchmark"]
    assert wanted, "the arrears block must declare the keys it reads"
    for row in rows:
        for key in wanted:
            assert key in row, f"page reads {key!r}, producer does not emit it"


def test_the_producer_contract_fires_on_a_key_the_producer_does_not_emit():
    """MUTATION: the exact defect as found -- `arrears_pct` added to the page's DECLARED
    reads (the real tuple, plus the never-emitted key) must red the real control."""
    mutated = POPULATION_ANCHORING_NUMERICS + (("arrears_vs_benchmark", "arrears_pct"),)
    with pytest.raises(AssertionError, match="arrears_pct"):
        _declared_keys_are_emitted(mutated, _produced())
    # ...and the unmutated declaration passes the same body, so the failure above is
    # attributable to the injected key and not to the fixture.
    _declared_keys_are_emitted(POPULATION_ANCHORING_NUMERICS, _produced())


def test_live_population_anchoring_artefact_carries_every_key_the_page_reads():
    """The published population, not a fixture. A missing artefact FAILS: the shadow
    sim page is generated from this file, so an unreadable one is an unanswerable
    question, not a passing one."""
    assert LIVE_ARTEFACT.exists(), f"{LIVE_ARTEFACT} is the shadow page's source and is missing"
    pa = json.loads(LIVE_ARTEFACT.read_text(encoding="utf-8"))
    missing = []
    for block, key in POPULATION_ANCHORING_NUMERICS:
        entries = pa.get(block)
        if isinstance(entries, dict):
            entries = [entries]
        if not entries:
            continue
        for entry in entries:
            if _payload_num(entry, key) is None:
                missing.append((block, key))
                break
    assert not missing, f"page reads keys the live artefact does not carry: {missing}"


def test_rendered_bad_debt_row_carries_the_producers_own_rate():
    """The SECOND instance, found by the census this finding asked for rather than by
    the finding itself: the bad-debt rows read `bad_debt_pct` while the producer emits
    `bad_debt_rate`, so every published bad-debt year also printed 0.00%."""
    from tools.population_anchor import _bad_debt_check

    rows = _bad_debt_check({"2017": {"bad_debt_gbp": 39.0, "revenue_gbp": 195000.0}})
    assert rows[0]["bad_debt_rate"] == 0.02
    html = _population_anchoring_rag({"overall_rag": "AMBER", "bad_debt_vs_benchmark": rows})
    assert "<td>0.02%</td>" in html
    assert "<td>0.00%</td>" not in html


def test_bad_debt_row_fires_when_read_under_the_key_that_was_never_emitted():
    """MUTATION: the defect as it stood -- read `bad_debt_pct`, get an em dash now
    instead of a silent 0.00%."""
    rows = [{"year": 2017, "bad_debt_pct": 0.02, "rag": "AMBER"}]
    html = _population_anchoring_rag({"overall_rag": "AMBER", "bad_debt_vs_benchmark": rows})
    assert "<td>0.02%</td>" not in html
    assert "&#8212;" in html


def test_unavailable_ledger_renders_no_rate_at_all():
    """The sibling fail-open fix makes an absent ledger render UNAVAILABLE. The value
    beside that chip must not be the 0.0 the division guard produces."""
    row = {"year": 2023, "new_arrears_rate_pct": 0.0, "rag": "UNAVAILABLE", "ledger_available": False}
    assert _arrears_value(row) == "&#8212;"


def test_unavailable_cell_fires_if_it_falls_back_to_a_number():
    """MUTATION: drop the availability flag -- the same row then reads as a real 0.00%,
    which is precisely the fail-open shape at the render seam."""
    row = {"year": 2023, "new_arrears_rate_pct": 0.0, "rag": "UNAVAILABLE"}
    assert _arrears_value(row) == "0.00%"


def test_payload_num_never_substitutes_a_number_it_did_not_read():
    assert _payload_num({}, "x") is None
    assert _payload_num({"x": None}, "x") is None
    assert _payload_num({"x": "3.4"}, "x") is None
    assert _payload_num({"x": True}, "x") is None  # a flag is not a percentage
    assert _payload_num({"x": 0}, "x") == 0        # a real zero still renders
    assert _payload_num(None, "x") is None
