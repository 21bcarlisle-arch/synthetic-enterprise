"""PROPOSED (NOT YET WIRED) — phone-native director-authority channels.

DIRECTOR_STEER_PHONE_AUTHORITY_CHANNEL_2026-07-22, Part 2. The director's frustration,
verbatim: *"I don't want stuff in the window ... This is a stupid chicken and egg."* R16 had
narrowed the valid authority channel to the console ledger, forcing tmux attachment from a phone
for every routine ruling — the exact manual-relay mode this architecture exists to eliminate.

This module makes TWO additional channels R16-valid for ROUTINE director authority (ratifications,
level rulings, R13 values, graduation calls, steers, [ACT] answers):

  1. director_ntfy      — a message from the director on the two-way NTFY channel, authenticated by
                          an HMAC signature (background.ntfy_utils.sign/verify_wake_message,
                          key=SE_WAKE_HMAC_KEY held OUTSIDE the working tree per secrets_location.py).
  2. advisor_ruling     — a [DIRECTOR-RULING]-marked doc staged + committed via the advisor bridge
                          (identity 21bcarlisle-arch), carrying the director's ruling verbatim.

=== THE WALL IS UNCHANGED (steer §"What stays personal/console") ===
These channels may carry ONLY the ROUTINE action set below. Everything else — safety-control changes,
authorization-trust changes, Tier-1 approvals, one-way doors (real customer/money/volunteer/account) —
STAYS console-only. This is enforced by an ALLOWLIST (default-deny): an unknown or reserved action is
INVALID on a non-console channel even with a perfect signature.

=== WHY THIS IS PROPOSED, NOT APPLIED ===
Making a non-console channel R16-valid IS an authorization-trust change (one-way door #5/#8). So this
module is deliberately STANDALONE: `background/gate_authorization.py` does NOT import it. The single
console ratification that ends the console era for routine authority is the one-line wiring described in
`docs/design/PHONE_NATIVE_AUTHORITY_CHANNEL_PROPOSAL_2026-07-22.md` §"The one ratification". Until the
director performs that act, these validators exist and are R15-proven both ways, but authorize nothing
live.

=== R15 — the authentication must be able to FAIL (both directions) ===
Proven in tests/background/test_director_authority_channels.py:
  * FAIL-CLOSED  a forged/unsigned/stale/reserved-action message FAILS loudly (returns False).
  * PASS         a genuine HMAC-signed director ruling / marked advisor doc PASSES and carries provenance.
  * FAIL-SILENT guard — an unavailable HMAC key makes a director_ntfy entry INVALID (verify returns None):
    an unavailable check is a FAILED check, never a pass-through (R15 doctrine).
  * TAUTOLOGY guard — the HMAC key lives outside the working TREE (not in git). The design INTENT is
    that the autonomous worker cannot mint a valid director_ntfy entry because it cannot read the key.
    ⚠️ LIVE GAP (found 2026-07-22, flagged to the director, NOT yet closed): out-of-TREE is not the
    same as out-of-worker-ENV. `worker-tick.service` loads EnvironmentFile=.env.ntfy (which carries
    SE_WAKE_HMAC_KEY) and `worker_tick.spawn_invocation` does `os.environ.copy()`, so the spawned
    `claude -p` worker currently INHERITS the key — and HMAC is symmetric, so whoever can verify can
    sign. Until the key is stripped from the worker's spawn env (the fix: pop SE_WAKE_HMAC_KEY there,
    as spawn_invocation already pops ANTHROPIC_BASE_URL — the worker needs SE_NTFY_TOPIC to SEND, not
    the wake key to SIGN), this channel is NOT worker-unforgeable and the gate-wall's deferred
    "prevention layer" is NOT discharged. Severity: no worse than the pre-existing console self-
    declaration residual (the wall is detection-only by design), but a forged director_ntfy carries a
    VALID signature so it is HARDER to detect — director's call whether to strip the key now.
  * REPLAY/REPURPOSE guard — the signed text must bind the (action, atom) it authorizes, so a valid
    signature for one ruling cannot be lifted onto a different ledger record.
"""
from __future__ import annotations

# NOTE: `verify_wake_message` is imported LAZILY inside is_valid_director_ntfy (not at module top).
# background.ntfy_utils RAISES at import if SE_NTFY_TOPIC is unset (the send-path topic), but HMAC
# verification only needs SE_WAKE_HMAC_KEY. A top-level import would make this module — and, since
# the 2026-07-22 wiring, gate_authorization which imports it — hard-fail to import in any process
# lacking the NTFY *send* topic (e.g. the pre-commit import check). Deferring the import decouples
# authority-verification from the send env; the key check itself still fails-closed if the HMAC key
# is unavailable (verify_wake_message returns None).

# ── the ROUTINE allowlist — the ONLY actions a non-console channel may authorize ──────────────
# Mirrors the gate ledger's existing routine action vocabulary + GRADUATE (forward-discovery). A
# reserved action (safety/authz-trust/Tier-1/one-way-door) has no entry here, so default-deny
# refuses it on these channels. Console keeps its full authority via gate_authorization.py unchanged.
ROUTINE_ACTIONS = frozenset({
    "BUILD_OPEN",
    "FRONT_OPEN",
    "FRONT_CLOSE",
    "GATE_CLEAR",
    "LEVEL_UP_PROPOSED",
    "HELD_PENDING_VERIFICATION",
    "GRADUATE",
})

# The two new channels this module authenticates. `console` is intentionally ABSENT — console
# validity is owned by gate_authorization.py and is not re-implemented here.
DIRECTOR_NTFY = "director_ntfy"
ADVISOR_RULING = "advisor_ruling"

# The ruling-doc marker the advisor stamps to distinguish a director ruling from ordinary staging.
RULING_MARKER = "[DIRECTOR-RULING]"

# Max age of a signed NTFY ruling. A directive older than this is stale (replay) — refused.
NTFY_MAX_AGE_SECONDS = 3600


def _routine(action) -> bool:
    """Default-DENY allowlist check: only an action explicitly in ROUTINE_ACTIONS may ride a
    non-console channel. An unknown, reserved, or gate-changing action fails here."""
    return isinstance(action, str) and action in ROUTINE_ACTIONS


def _bound_signed_text(action: str, atom: str) -> str:
    """The canonical signed-message body the director's phone signs. Binding the (action, atom)
    into the signed text is the REPLAY/REPURPOSE guard: a signature valid for `RULING:BUILD_OPEN:X`
    cannot be lifted onto a ledger record claiming a LEVEL_UP for Y — the HMAC would not verify."""
    return f"RULING:{action}:{atom}"


def is_valid_director_ntfy(entry, *, max_age_seconds: int = NTFY_MAX_AGE_SECONDS) -> bool:
    """A director-NTFY authority entry is valid ONLY if EVERY check holds:
      - authorized_by == 'director', channel == 'director_ntfy'
      - a routine (allowlisted) action + a non-empty atom + non-empty provenance
      - `signed_payload` is a `text|ts|hmac` triple that HMAC-verifies (fresh, not stale) against
        SE_WAKE_HMAC_KEY, AND the verified text is EXACTLY _bound_signed_text(action, atom).
    FAIL-CLOSED on any missing/forged/stale/reserved field. FAIL-SILENT-safe: if the key is
    unavailable, verify_wake_message returns None → invalid (an unavailable check is a FAILED check)."""
    if not (isinstance(entry, dict)
            and entry.get("authorized_by") == "director"
            and entry.get("channel") == DIRECTOR_NTFY
            and _routine(entry.get("action"))
            and bool(str(entry.get("atom") or "").strip())
            and bool(str(entry.get("provenance") or "").strip())):
        return False
    signed = entry.get("signed_payload")
    if not isinstance(signed, str) or not signed:
        return False
    try:
        from background.ntfy_utils import verify_wake_message  # lazy: see module-top note
    except Exception:
        # ntfy_utils unavailable (e.g. the send-topic env is unset in this process). An
        # unavailable verification is a FAILED check (R15 fail-silent guard), never a pass —
        # FAIL-CLOSED rather than raise, so a caller evaluating authority in a topic-less process
        # rejects the entry instead of crashing.
        return False
    verified_text = verify_wake_message(signed, max_age_seconds=max_age_seconds)
    if verified_text is None:  # no key, bad signature, or stale — all FAIL-CLOSED
        return False
    return verified_text == _bound_signed_text(entry["action"], entry["atom"])


def is_valid_advisor_ruling(entry) -> bool:
    """An advisor-staged [DIRECTOR-RULING] authority entry is valid ONLY if:
      - authorized_by == 'director', channel == 'advisor_ruling'
      - ruling_marker == RULING_MARKER (the explicit director-ruling stamp)
      - a routine (allowlisted) action + a non-empty atom
      - a non-empty `commit` (the advisor-bridge commit carrying the marked doc) + non-empty provenance.
    FAIL-CLOSED on a missing marker, missing commit, or reserved action. (The wiring step ADDS a
    git-authorship check that `commit` was authored by the advisor bridge identity — see the proposal;
    the pure validator here checks the structural provenance a forger cannot satisfy without the bridge.)"""
    return (
        isinstance(entry, dict)
        and entry.get("authorized_by") == "director"
        and entry.get("channel") == ADVISOR_RULING
        and entry.get("ruling_marker") == RULING_MARKER
        and _routine(entry.get("action"))
        and bool(str(entry.get("atom") or "").strip())
        and bool(str(entry.get("commit") or "").strip())
        and bool(str(entry.get("provenance") or "").strip())
    )


def is_valid_phone_authority(entry, *, max_age_seconds: int = NTFY_MAX_AGE_SECONDS) -> bool:
    """Umbrella predicate: does this entry carry valid ROUTINE director authority via EITHER new
    phone-native channel? A console entry returns False here BY DESIGN — console validity stays owned
    by gate_authorization.py; this module only ever ADDS the two new channels, never re-judges console."""
    return (is_valid_director_ntfy(entry, max_age_seconds=max_age_seconds)
            or is_valid_advisor_ruling(entry))
