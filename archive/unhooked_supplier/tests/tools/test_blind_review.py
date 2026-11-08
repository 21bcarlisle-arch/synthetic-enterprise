# ARCHIVED LEGS of tests/tools/test_blind_review.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/tools/test_blind_review.py.
"""Tests for tools/blind_review.py — AO9, blind review by restricted context.

The claim under test is "the reviewer could not see the code". That claim is
unusually easy to make and unusually hard to check, because the only party who
knows what the reviewer saw is the party asserting it — so the tests below
refuse to take the tool's word for anything and re-derive the verdict from the
stored transcript, which is the only artefact an auditor would actually have.

R15, the three killer patterns, each answered by a named test:

  TAUTOLOGY   -- `test_audit_disagrees_with_a_record_that_claims_it_was_clean`
                 stores `leaks: []` over a transcript full of source. If the
                 audit read the record's own claim it would agree with the
                 forgery, and would have proven only that JSON round-trips.
  FAIL-OPEN   -- `test_empty_transcript_is_a_failed_audit_not_a_clean_one` and
                 `test_missing_transcript_field_is_a_failed_audit`: an absent
                 record of what was shown is the WORST case, not the calmest.
  FAIL-SILENT -- `test_unreadable_ledger_returns_rc_2_never_rc_0`: when the
                 checker cannot run, it says so; it never reports clean.

And the load-bearing check, `test_the_leak_finding_comes_from_the_named_rule`:
the same transcript audits CLEAN once its rule is removed. Without that, a test
asserting "a leak was found" cannot distinguish the guard doing its job from
something incidental in the fixture.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools import blind_review as br

REPO = Path(__file__).resolve().parent.parent.parent

CLEAN_WORDS = "An engine that works out what a household owes for the energy it used."


@pytest.fixture
def ledger(tmp_path):
    return tmp_path / "blind_review_ledger.jsonl"


def clean_packet(capability="billing engine"):
    return br.build_packet(capability, plain_words=CLEAN_WORDS)


def a_battery():
    return [
        {"question": "What happens to a bill when the meter read arrives 40 days late?",
         "class": "DISQUALIFYING"},
        {"question": "Does it price a day that straddles a tariff change at both rates?",
         "class": "DISQUALIFYING"},
    ]


# ---------------------------------------------------------------------------
# the control must be able to PASS -- otherwise it is a wedge, not a check
# ---------------------------------------------------------------------------







# ---------------------------------------------------------------------------
# R15 -- every rule fires on its OWN named defect, and every rule is reachable
# ---------------------------------------------------------------------------











# ---------------------------------------------------------------------------
# the record: transcript and battery are one artefact
# ---------------------------------------------------------------------------







# ---------------------------------------------------------------------------
# R15 -- the audit re-derives from the transcript, and can DISAGREE with it
# ---------------------------------------------------------------------------











# ---------------------------------------------------------------------------
# R15 -- FAIL-OPEN: absence must never read as calm
# ---------------------------------------------------------------------------









# ---------------------------------------------------------------------------
# R15 -- FAIL-SILENT: an unavailable check is a failed check
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
# 3c is a WALL -- this mechanism may never be described as independence
# ---------------------------------------------------------------------------







# ---------------------------------------------------------------------------
# ONE MECHANISM -- the reconciliation the atom requires, asserted on disk
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# the live repo
# ---------------------------------------------------------------------------





