"""R15 mutation tests for the PROPOSED phone-native director-authority channels
(background/director_authority_channels.py, DIRECTOR_STEER_PHONE_AUTHORITY_CHANNEL_2026-07-22 Part 2).

R15 doctrine: a control counts as evidence only if a MUTATION proves it FIRES on its own named defect.
This suite proves BOTH directions the steer demanded:
  * FAIL-CLOSED — a forged / unsigned / stale / reserved-action / non-director message FAILS loudly.
  * PASS        — a genuine HMAC-signed director ruling and a genuine marked advisor doc PASS.
Plus the three killer-pattern guards: FAIL-SILENT (no key ⇒ invalid), TAUTOLOGY (signature bound to a
key the writer can't read), REPLAY/REPURPOSE (a signature for one ruling can't authorize another).
"""
import background.ntfy_utils as ntfy_utils
from background import director_authority_channels as dac

TEST_KEY = "test-hmac-key-for-director-authority-channels"


def _sign(text: str, **kw):
    """Sign `text` with the test key patched into ntfy_utils (both sign+verify read the global)."""
    return ntfy_utils.sign_wake_message(text, **kw)


def _ntfy_entry(action="BUILD_OPEN", atom="F1a_sim_customer_response", *, signed=None,
                provenance="Director NTFY 2026-07-22, HMAC-verified", authorized_by="director",
                channel=dac.DIRECTOR_NTFY):
    if signed is None:
        signed = _sign(dac._bound_signed_text(action, atom))
    return {"atom": atom, "action": action, "authorized_by": authorized_by, "channel": channel,
            "signed_payload": signed, "provenance": provenance}


def _advisor_entry(action="LEVEL_UP_PROPOSED", atom="F1b_company_comms", *,
                   marker=dac.RULING_MARKER, commit="deadbeef1234",
                   provenance="Advisor-staged [DIRECTOR-RULING] doc, 21bcarlisle-arch bridge",
                   authorized_by="director", channel=dac.ADVISOR_RULING):
    return {"atom": atom, "action": action, "authorized_by": authorized_by, "channel": channel,
            "ruling_marker": marker, "commit": commit, "provenance": provenance}


# ── PASS direction — a genuine director ruling authorizes ──────────────────────────────────────
def test_genuine_signed_ntfy_ruling_passes(monkeypatch):
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", TEST_KEY)
    assert dac.is_valid_director_ntfy(_ntfy_entry()) is True
    assert dac.is_valid_phone_authority(_ntfy_entry()) is True


def test_genuine_advisor_ruling_doc_passes():
    assert dac.is_valid_advisor_ruling(_advisor_entry()) is True
    assert dac.is_valid_phone_authority(_advisor_entry()) is True


def test_every_routine_action_accepted_on_a_genuine_ruling(monkeypatch):
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", TEST_KEY)
    for action in dac.ROUTINE_ACTIONS:
        assert dac.is_valid_director_ntfy(_ntfy_entry(action=action)) is True, action
        assert dac.is_valid_advisor_ruling(_advisor_entry(action=action)) is True, action


# ── FAIL-CLOSED direction — forgery must fail loudly ────────────────────────────────────────────
def test_ntfy_bad_signature_fails(monkeypatch):
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", TEST_KEY)
    e = _ntfy_entry(signed="RULING:BUILD_OPEN:F1a_sim_customer_response|9999999999|deadbeefcafe")
    assert dac.is_valid_director_ntfy(e) is False


def test_ntfy_unsigned_fails(monkeypatch):
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", TEST_KEY)
    assert dac.is_valid_director_ntfy(_ntfy_entry(signed="")) is False
    e = _ntfy_entry(); e["signed_payload"] = None
    assert dac.is_valid_director_ntfy(e) is False


def test_ntfy_signed_by_a_DIFFERENT_key_fails(monkeypatch):
    # The worker signs with a key it invented (it cannot read SE_WAKE_HMAC_KEY, held out of tree).
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", "attacker-guessed-key")
    forged = _sign(dac._bound_signed_text("BUILD_OPEN", "F1a_sim_customer_response"))
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", TEST_KEY)  # the REAL key
    assert dac.is_valid_director_ntfy(_ntfy_entry(signed=forged)) is False


def test_ntfy_stale_signature_fails(monkeypatch):
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", TEST_KEY)
    old = _sign(dac._bound_signed_text("BUILD_OPEN", "F1a_sim_customer_response"), timestamp=1)
    assert dac.is_valid_director_ntfy(_ntfy_entry(signed=old)) is False


def test_ntfy_reserved_action_fails_even_with_valid_signature(monkeypatch):
    # THE wall: a perfectly-signed director NTFY cannot ratify an authorization-trust / safety change.
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", TEST_KEY)
    for reserved in ("AUTHZ_TRUST_CHANGE", "SAFETY_CONTROL_CHANGE", "TIER1_APPROVAL",
                     "ONE_WAY_DOOR", "SKIP_PERMISSIONS"):
        e = _ntfy_entry(action=reserved)  # signed_payload binds this reserved action, so HMAC is valid
        assert dac.is_valid_director_ntfy(e) is False, reserved
        assert dac.is_valid_phone_authority(e) is False, reserved


def test_ntfy_signature_repurpose_fails(monkeypatch):
    # A valid signature for ruling A lifted onto a ledger record claiming action/atom B must fail.
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", TEST_KEY)
    sig_for_a = _sign(dac._bound_signed_text("BUILD_OPEN", "atomA"))
    e = _ntfy_entry(action="LEVEL_UP_PROPOSED", atom="atomB", signed=sig_for_a)
    assert dac.is_valid_director_ntfy(e) is False


def test_ntfy_non_director_fails(monkeypatch):
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", TEST_KEY)
    assert dac.is_valid_director_ntfy(_ntfy_entry(authorized_by="worker")) is False
    assert dac.is_valid_director_ntfy(_ntfy_entry(authorized_by="director_twin")) is False


def test_ntfy_empty_provenance_fails(monkeypatch):
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", TEST_KEY)
    assert dac.is_valid_director_ntfy(_ntfy_entry(provenance="")) is False


# ── FAIL-SILENT guard — an unavailable check is a FAILED check ──────────────────────────────────
def test_ntfy_no_key_available_fails_closed(monkeypatch):
    # First build a genuinely-signed entry with a key, then REMOVE the key: verification must
    # now fail-closed (None), never pass through. An unavailable check is a FAILED check (R15).
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", TEST_KEY)
    e = _ntfy_entry()
    monkeypatch.setattr(ntfy_utils, "WAKE_HMAC_KEY", "")
    assert dac.is_valid_director_ntfy(e) is False


# ── advisor-ruling FAIL-CLOSED mutations ────────────────────────────────────────────────────────
def test_advisor_missing_marker_fails():
    assert dac.is_valid_advisor_ruling(_advisor_entry(marker="")) is False
    assert dac.is_valid_advisor_ruling(_advisor_entry(marker="[ADVISOR-STAGED]")) is False


def test_advisor_missing_commit_fails():
    assert dac.is_valid_advisor_ruling(_advisor_entry(commit="")) is False


def test_advisor_reserved_action_fails():
    for reserved in ("AUTHZ_TRUST_CHANGE", "SAFETY_CONTROL_CHANGE", "TIER1_APPROVAL"):
        assert dac.is_valid_advisor_ruling(_advisor_entry(action=reserved)) is False, reserved


def test_advisor_non_director_fails():
    assert dac.is_valid_advisor_ruling(_advisor_entry(authorized_by="advisor")) is False


def test_advisor_empty_provenance_fails():
    assert dac.is_valid_advisor_ruling(_advisor_entry(provenance="")) is False


# ── channel-isolation — this module never re-judges console ─────────────────────────────────────
def test_console_entry_is_not_judged_here():
    # A console BUILD_OPEN is valid via gate_authorization, NOT here — is_valid_phone_authority
    # returns False so the two systems compose additively, never overlap.
    console = {"atom": "X", "action": "BUILD_OPEN", "authorized_by": "director",
               "channel": "console", "provenance": "console act"}
    assert dac.is_valid_phone_authority(console) is False


def test_non_dict_and_junk_fail_closed():
    for junk in (None, "", 42, [], {"channel": dac.DIRECTOR_NTFY}):
        assert dac.is_valid_director_ntfy(junk) is False
        assert dac.is_valid_advisor_ruling(junk) is False
        assert dac.is_valid_phone_authority(junk) is False
