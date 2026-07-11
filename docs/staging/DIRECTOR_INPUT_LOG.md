# DIRECTOR_INPUT_LOG — unified log of every director input, every channel (P2)

**Staged:** 2026-07-11 by advisor, director-proposed ("a log of everything I
post on every channel, hashed where confidential, that the advisor can see").
**Lane H.** Extends ADVISOR_VISIBILITY (which mirrors ntfy) to close the gap
that caused today's impasse: window pastes are invisible to the advisor, so
an unanswered blocking question sat in a pane for hours while the advisor
drafted answers Rich had already posted.

## Requirement
Capture EVERY input that becomes agent turn-content, at the runtime layer so
nothing can be missed (the user-prompt lifecycle hook from the adoption
sprint is the known-good mechanism — deterministic, unskippable). Each entry:
- timestamp
- **channel tag**: window-live | window-queued-midturn | ntfy | comments-box
  | supervisor-wake | watcher-wake | advisor-staged
- HMAC-verified status for machine-generated injections
- content, SCRUBBED (below)
Appended to a repo log (docs/observability/director_input_log.md or similar),
batched commits per the existing mirror pattern, size-capped/rotating,
advisor-readable within ~10 minutes.

## Scrubbing (public-repo aware — the director has been told everything he
types becomes public once scrubbed)
- Secrets (topic names, PINs, tokens, signatures, keys) → replaced by
  sha256-prefix hashes (8 chars) so correlation survives without disclosure.
- Scrub list maintained in one place, shared with the ntfy mirror's scrubber;
  a test proves a planted secret is redacted before the feature enables
  (same standard as ADVISOR_VISIBILITY).
- Anything matching obvious personal-data shapes (emails, phone numbers not
  already public) → hashed likewise.

## Why (both directions)
- Advisor: full sight of what the director actually sent, on which channel,
  when — no more drafting answers to already-answered questions.
- Agent: provenance becomes self-documenting — a window-queued-midturn entry
  in the log IS the evidence that a suspicious-wrapper message was real
  director input. Kills the injection-confusion class at the root.

## DoD
Hook live; all channels demonstrably captured (one test entry per channel
tag, including a mid-turn queued paste); scrub test passes with a planted
secret; log visible on origin; entry added to CLAUDE.md channel docs. One
digest line. Pixel rule applies.
