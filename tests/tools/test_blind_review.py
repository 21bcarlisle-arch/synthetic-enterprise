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

def test_a_blind_safe_description_renders_a_packet_with_no_leaks():
    packet = clean_packet()
    assert packet["leaks"] == []
    assert CLEAN_WORDS in packet["shown"]
    assert packet["plain_words_source"] == "restated"


def test_the_template_itself_is_held_to_the_blindfold():
    """The fixed wording is rendered into the same text the rules run over, so a
    build word smuggled into the template would leak on every single review."""
    assert br.blindfold_leaks(br.render_shown(CLEAN_WORDS, br.DEFAULT_DOMAIN, br.DEFAULT_PERSONA)) == []


def test_the_capability_name_is_kept_out_of_what_the_reviewer_sees():
    """A module path is a map of the implementation. Naming the subject would
    undo the blindfold in the act of applying it."""
    packet = br.build_packet("company.billing.back_billing", plain_words=CLEAN_WORDS)
    assert "back_billing" not in packet["shown"]
    assert "company.billing" not in packet["shown"]
    assert packet["capability"] == "company.billing.back_billing"


# ---------------------------------------------------------------------------
# R15 -- every rule fires on its OWN named defect, and every rule is reachable
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rule,leaky_words", [
    ("SOURCE_CODE", "It bills a household.\ndef compute(reads):\n    return 1"),
    ("FILE_PATH", "It bills a household. The maths lives in engine.py."),
    ("REPO_LOCATION", "It bills a household, alongside the rest of company/ generally."),
    ("PRIOR_JUDGEMENT", "It bills a household. An earlier finding said the rounding was wrong."),
    ("MAP_INTERNALS", "It bills a household. This atom is targeted at epoch 3."),
    ("PHASE_LABEL", "Direct Debit Mandate Register (Phase GD)."),
    ("BUILD_CONTEXT", "It bills a household. We built the rounding fix in the last commit."),
    ("IDENTIFIER", "It bills a household through the back_billing path."),
])
def test_each_blindfold_rule_fires_on_its_own_named_defect(rule, leaky_words):
    packet = br.build_packet("subject", plain_words=leaky_words)
    assert any(leak.startswith(rule + ":") for leak in packet["leaks"]), (
        f"{rule} did not fire on the leak it exists to catch: {packet['leaks']}"
    )


def test_real_domain_language_is_not_flagged_as_a_leak():
    """A blindfold that fires on the domain's own vocabulary gets switched off
    within a week, which is how controls really die. Three-phase supply, meter
    phases and half-hourly settlement are the subject matter, not bookkeeping."""
    words = ("A register of three-phase supply points, settled half-hourly, "
             "covering both the domestic and small-business phases of the market.")
    assert br.blindfold_leaks(br.render_shown(words, br.DEFAULT_DOMAIN, br.DEFAULT_PERSONA)) == []


def test_every_rule_is_reachable():
    """A rule no fixture can trigger is dead code masquerading as coverage."""
    fired = set()
    for words in [
        "def f(x):\n    return x", "engine.py", "company/", "a known defect",
        "this atom", "the last commit", "back_billing", "(Phase GD)",
    ]:
        for leak in br.blindfold_leaks(br.render_shown(words, "d", "p")):
            fired.add(leak.split(":")[0])
    assert {name for name, _, _ in br.LEAK_RULES} <= fired


def test_a_leaky_packet_is_refused_rather_than_flagged_and_shown(capsys):
    """The refusal is the mechanism. Rendering a leaked packet 'with a warning'
    still hands the reviewer the thing it must not see."""
    rc = br.main(["--packet", "subject", "--plain-words", "It bills. See engine.py."])
    err = capsys.readouterr().err
    assert rc == 1
    assert "REFUSED" in err and "FILE_PATH" in err
    assert "engine.py" not in capsys.readouterr().out


def test_a_capability_with_no_description_cannot_be_reviewed():
    """Silently reviewing an empty description would produce a battery about
    nothing and file it as though a capability had been examined."""
    packet = br.build_packet("subject", plain_words="   ")
    assert packet["shown"] is None
    assert any(leak.startswith("NO_DESCRIPTION") for leak in packet["leaks"])


# ---------------------------------------------------------------------------
# the record: transcript and battery are one artefact
# ---------------------------------------------------------------------------

def test_recording_keeps_the_transcript_with_the_battery(ledger):
    br.record_review(clean_packet(), a_battery(), "2026-08-08T20:40:00Z", ledger)
    [record] = br.load_records(ledger)
    assert CLEAN_WORDS in record["shown"]
    assert len(record["battery"]) == 2
    assert record["shown_sha256"] == br.digest(record["shown"])


def test_a_leaked_review_cannot_be_recorded_at_all(ledger):
    packet = br.build_packet("subject", plain_words="It bills. See engine.py.")
    with pytest.raises(ValueError, match="not blind"):
        br.record_review(packet, a_battery(), "2026-08-08T20:40:00Z", ledger)
    assert not ledger.exists(), "a refused review must leave no trace of a verdict"


def test_an_empty_battery_is_refused(ledger):
    with pytest.raises(ValueError, match="empty battery"):
        br.record_review(clean_packet(), [], "2026-08-08T20:40:00Z", ledger)


# ---------------------------------------------------------------------------
# R15 -- the audit re-derives from the transcript, and can DISAGREE with it
# ---------------------------------------------------------------------------

def test_a_leak_is_detectable_from_the_committed_transcript_alone(ledger):
    """The atom's own named mutation: source code reaches the reviewer's context.

    The record is written by hand, as a tampered or hand-rolled record would
    be, and the audit is given nothing but the file. If blindness were only
    provable by watching the packet being built, the committed transcript would
    be decoration and the auditability claim would be false.
    """
    leaked = dict(
        recorded_at="2026-08-08T20:40:00Z", capability="subject",
        domain="d", persona="p", plain_words_source="restated",
        shown="THE CAPABILITY:\ndef compute_bill(reads):\n    return sum(reads)",
        battery=a_battery(), independence=False, honest_limit=br.HONEST_LIMIT,
    )
    leaked["shown_sha256"] = br.digest(leaked["shown"])
    ledger.write_text(json.dumps(leaked) + "\n", encoding="utf-8")

    count, findings = br.audit(ledger)
    assert count == 1
    assert any("SOURCE_CODE" in f for f in findings), findings


def test_the_leak_finding_comes_from_the_named_rule(ledger, monkeypatch):
    """Remove the rule, keep the transcript: the audit must go quiet.

    Without this, 'a finding appeared' is compatible with the finding coming
    from anything at all in the fixture, and the rule under test could be dead.
    """
    leaked = dict(
        recorded_at="t", capability="subject", domain="d", persona="p",
        plain_words_source="restated",
        shown="THE CAPABILITY:\ndef compute(reads):\n    return 1",
        battery=a_battery(), independence=False, honest_limit=br.HONEST_LIMIT,
    )
    leaked["shown_sha256"] = br.digest(leaked["shown"])
    ledger.write_text(json.dumps(leaked) + "\n", encoding="utf-8")
    assert any("SOURCE_CODE" in f for f in br.audit(ledger)[1])

    monkeypatch.setattr(
        br, "LEAK_RULES", tuple(r for r in br.LEAK_RULES if r[0] != "SOURCE_CODE")
    )
    assert not any("SOURCE_CODE" in f for f in br.audit(ledger)[1])


def test_audit_disagrees_with_a_record_that_claims_it_was_clean(ledger):
    """TAUTOLOGY killer. The record asserts its own innocence; the transcript
    contradicts it. A checker that read the assertion would agree with the
    forgery and prove only that a JSON field survives a round trip."""
    forged = dict(
        recorded_at="t", capability="subject", domain="d", persona="p",
        plain_words_source="restated",
        shown="THE CAPABILITY:\nimport company.billing.engine\nself.rate = 1",
        leaks=[],              # <- the lie
        blindness="verified",  # <- and its supporting testimony
        battery=a_battery(), independence=False, honest_limit=br.HONEST_LIMIT,
    )
    forged["shown_sha256"] = br.digest(forged["shown"])
    ledger.write_text(json.dumps(forged) + "\n", encoding="utf-8")

    _, findings = br.audit(ledger)
    assert any("SOURCE_CODE" in f for f in findings), (
        "the audit believed the record's own account of itself"
    )


def test_editing_a_transcript_after_the_fact_is_caught(ledger):
    br.record_review(clean_packet(), a_battery(), "t", ledger)
    record = br.load_records(ledger)[0]
    record["shown"] = record["shown"].replace(CLEAN_WORDS, "Something far more impressive.")
    ledger.write_text(json.dumps(record) + "\n", encoding="utf-8")

    _, findings = br.audit(ledger)
    assert any("TAMPERED" in f for f in findings)


def test_a_transcript_without_a_digest_is_a_finding(ledger):
    record = dict(
        recorded_at="t", capability="subject", domain="d", persona="p",
        plain_words_source="restated", shown=br.render_shown(CLEAN_WORDS, "d", "p"),
        battery=a_battery(), independence=False, honest_limit=br.HONEST_LIMIT,
    )
    ledger.write_text(json.dumps(record) + "\n", encoding="utf-8")
    _, findings = br.audit(ledger)
    assert any("no digest" in f for f in findings)


# ---------------------------------------------------------------------------
# R15 -- FAIL-OPEN: absence must never read as calm
# ---------------------------------------------------------------------------

def test_empty_transcript_is_a_failed_audit_not_a_clean_one(ledger):
    record = dict(recorded_at="t", capability="subject", shown="   ",
                  shown_sha256="x", battery=a_battery(), independence=False,
                  honest_limit=br.HONEST_LIMIT)
    ledger.write_text(json.dumps(record) + "\n", encoding="utf-8")
    _, findings = br.audit(ledger)
    assert any("EMPTY_TRANSCRIPT" in f for f in findings)


def test_missing_transcript_field_is_a_failed_audit(ledger):
    """'We have no record of what the reviewer saw' and 'the reviewer saw
    nothing improper' are opposite states."""
    record = dict(recorded_at="t", capability="subject", battery=a_battery(),
                  independence=False, honest_limit=br.HONEST_LIMIT)
    ledger.write_text(json.dumps(record) + "\n", encoding="utf-8")
    _, findings = br.audit(ledger)
    assert any("EMPTY_TRANSCRIPT" in f for f in findings)


def test_a_recorded_review_with_no_battery_is_a_finding(ledger):
    record = dict(recorded_at="t", capability="subject",
                  shown=br.render_shown(CLEAN_WORDS, "d", "p"),
                  battery=[], independence=False, honest_limit=br.HONEST_LIMIT)
    record["shown_sha256"] = br.digest(record["shown"])
    ledger.write_text(json.dumps(record) + "\n", encoding="utf-8")
    _, findings = br.audit(ledger)
    assert any("no battery" in f for f in findings)


def test_an_empty_ledger_reports_an_empty_pass_not_a_clean_one(ledger, capsys):
    """VACUITY. Zero findings over zero records is indistinguishable from zero
    findings over a hundred unless the count is on the face of the output."""
    rc = br.main(["--audit", "--ledger", str(ledger)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "0 recorded review(s)" in out
    assert "empty pass, not a clean one" in out


# ---------------------------------------------------------------------------
# R15 -- FAIL-SILENT: an unavailable check is a failed check
# ---------------------------------------------------------------------------

def test_unreadable_ledger_returns_rc_2_never_rc_0(ledger, capsys):
    ledger.write_text("{this is not a record\n", encoding="utf-8")
    rc = br.main(["--audit", "--ledger", str(ledger)])
    assert rc == 2, "a ledger that cannot be parsed was reported as clean"
    assert "AUDIT UNAVAILABLE" in capsys.readouterr().err


def test_load_records_raises_rather_than_returning_empty(ledger):
    ledger.write_text("not json\n", encoding="utf-8")
    with pytest.raises(ValueError, match="not readable"):
        br.load_records(ledger)


# ---------------------------------------------------------------------------
# 3c is a WALL -- this mechanism may never be described as independence
# ---------------------------------------------------------------------------

def test_every_record_carries_the_honest_limit_by_construction(ledger):
    record = br.record_review(clean_packet(), a_battery(), "t", ledger)
    assert record["independence"] is False
    assert "NOT INDEPENDENCE" in record["honest_limit"]
    assert "same model family" in record["honest_limit"]


def test_a_record_claiming_independence_fails_the_audit(ledger):
    record = dict(recorded_at="t", capability="subject",
                  shown=br.render_shown(CLEAN_WORDS, "d", "p"),
                  battery=a_battery(), independence=True, honest_limit=br.HONEST_LIMIT)
    record["shown_sha256"] = br.digest(record["shown"])
    ledger.write_text(json.dumps(record) + "\n", encoding="utf-8")
    _, findings = br.audit(ledger)
    assert any("claims independence" in f for f in findings)


def test_a_record_that_drops_the_limit_fails_the_audit(ledger):
    record = dict(recorded_at="t", capability="subject",
                  shown=br.render_shown(CLEAN_WORDS, "d", "p"),
                  battery=a_battery(), independence=False)
    record["shown_sha256"] = br.digest(record["shown"])
    ledger.write_text(json.dumps(record) + "\n", encoding="utf-8")
    _, findings = br.audit(ledger)
    assert any("3c limit is missing" in f for f in findings)


# ---------------------------------------------------------------------------
# ONE MECHANISM -- the reconciliation the atom requires, asserted on disk
# ---------------------------------------------------------------------------

def test_the_cold_eyes_skill_owns_this_tool_rather_than_sitting_beside_it():
    """The director required ONE mechanism. A separate blind-review skill, or a
    cold-eyes skill that never mentions the mechanised blindfold, is two."""
    skill = (REPO / ".claude" / "skills" / "cold-eyes-walk" / "SKILL.md")
    text = skill.read_text(encoding="utf-8")
    assert "tools/blind_review.py" in text, "the skill does not reach the mechanism"
    assert "NOT INDEPENDENCE" in text.upper(), "the 3c limit is missing from the protocol"

    others = [p for p in (REPO / ".claude" / "skills").glob("*/SKILL.md")
              if p != skill and "blind_review.py" in p.read_text(encoding="utf-8")]
    assert not others, f"a second review mechanism exists beside cold-eyes: {others}"


# ---------------------------------------------------------------------------
# the live repo
# ---------------------------------------------------------------------------

def test_the_repo_ledger_audits_clean():
    """Standing check: whatever has been recorded here is still blind."""
    count, findings = br.audit()
    assert findings == [], f"{count} recorded review(s), {len(findings)} finding(s): {findings}"


def test_a_real_derived_description_is_judged_honestly_not_waved_through():
    """Against the live index, the tool must either produce a blind-safe packet
    or name why not -- never quietly show a description full of module names."""
    packet = br.build_packet("company.billing.dd_mandate_register")
    assert packet["plain_words_source"] == "index"
    if packet["leaks"]:
        assert packet["shown"] is None or all(
            leak.split(":")[0] in {n for n, _, _ in br.LEAK_RULES} | {"NO_DESCRIPTION",
                                                                     "EMPTY_TRANSCRIPT"}
            for leak in packet["leaks"]
        )
    else:
        assert br.blindfold_leaks(packet["shown"]) == []


def test_cli_runs_as_a_subprocess():
    proc = subprocess.run(
        [sys.executable, "tools/blind_review.py", "--audit"],
        cwd=REPO, capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "audited" in proc.stdout
