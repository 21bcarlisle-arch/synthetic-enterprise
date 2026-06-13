# Design Proposal: Two-Way NTFY Protocol

Status: **proposed, not yet implemented** — written up 2026-06-13 per Rich's
request for (1) visually distinct "done" vs "please review" notifications,
and (2) the ability to respond to a gate directly from the notification
rather than opening the session.

## Part 1 — Distinguish message types (cheap, no code)

ntfy supports a priority level and emoji tags per message via headers:

- `X-Priority: 3` (default) + `X-Tags: white_check_mark` for **FYI/done**
  messages (phase complete, session start, milestone).
- `X-Priority: 4` or `5` (high/urgent) + `X-Tags: warning` for **needs
  input** messages (REVIEW_GATE, permission prompt, error).

Update the NTFY Protocol section of `MASTER_BACKLOG.md` so each of the five
required notification types specifies which header set to use. This alone
lets Rich tell at a glance — different sound/vibration on most ntfy apps —
whether a notification needs action.

## Part 2 — Reply from the notification (new endpoint + watchdog change)

ntfy supports `http` action buttons: tapping one fires an HTTP request
directly from the phone, no app needed. Plan:

1. **New `POST /respond` endpoint on `background/file_api.py`** — body
   `{"gate": "<id>", "decision": "<free text>"}`. Writes to
   `docs/staging/responses/<gate>.json` with a timestamp.

2. **`session_watchdog.py` autoloop** — each polling cycle, also check
   `docs/staging/responses/` for new files. If found, use the `decision`
   text as the continuation instruction (instead of the generic
   `AUTOLOOP_INSTRUCTION`), then archive the response file. This is the
   "reply" landing back in the session.

3. **REVIEW_GATE notifications** include two `http` actions, e.g. "Approve,
   proceed" and "Hold", each POSTing to `/respond` with a pre-filled
   `decision`.

## Security note — do not skip

`http` actions transit ntfy.sh's servers as part of the notification
payload, including any headers (so the real `FILE_API_KEY` would be
visible to anyone who can read the `skynet-synthetic` topic — topic names
are the only access control on ntfy.sh and are not secret in any strong
sense). Recommendation: `/respond` accepts a **short-lived, single-use
per-gate token** instead of the master key — generated when the REVIEW_GATE
notification is sent, stored in a gitignored
`docs/staging/.gate_tokens/<gate>.token`, and invalidated on first use.
The master `FILE_API_KEY` should never appear in an ntfy action.

## Implementation steps (future session, separate from this writeup)

1. `/respond` endpoint + gate-token helper + tests in
   `tests/background/test_file_api.py`.
2. `session_watchdog.py`: generate a gate token and attach `http` actions
   when sending a REVIEW_GATE notification; poll
   `docs/staging/responses/` each autoloop cycle.
3. Update the NTFY Protocol section of `MASTER_BACKLOG.md` with the
   priority/tag conventions (Part 1) and the action-button format (Part 2).
4. `make check`, commit, push, NTFY.

## Open question for Rich

Confirm `http` action buttons render and work from the ntfy mobile app on
your device before the rest is built — some ntfy action types are
Android-only, but `http` actions are documented as cross-platform.
