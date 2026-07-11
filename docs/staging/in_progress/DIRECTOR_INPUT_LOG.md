> **STATUS (2026-07-11):** Private repo created, V1 BUILT (commit 70f1d239).
> Core mechanism live: background/director_input_log.py (channel-tagged,
> HMAC-verified, correlatable secret scrubbing), .claude/hooks/
> log_director_input.py wired for "window", ntfy_utils.py/ntfy_responder.py
> wired for "ntfy" both directions. ntfy mirror relocated off the public
> repo. Log genuinely visible on origin (synthetic-enterprise-ops).
>
> HONEST SCOPE LIMITS, not silently claimed as done:
> 1. window-live/window-queued-midturn collapse into one "window" tag --
>    researched via claude-code-guide before building: Claude Code's
>    UserPromptSubmit hook has no field distinguishing them, and no other
>    documented hook covers a mid-turn-queued message either. A real gap
>    in the harness, not this repo's to close (would need an `origin`
>    field on the hook payload).
> 2. comments-box / supervisor-wake / watcher-wake / advisor-staged are
>    classify-able (classify_channel() recognises their bracket tags,
>    tested) but have NO live automatic call site yet -- staging_watcher.py,
>    dispatcher.py, director_comments.py, and advisor-commit detection
>    would each need their own wiring. Registered as V2, next real step if
>    this is prioritised further.
> Move to done/ once V2 lands or the director judges V1 sufficient.

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
Appended to a log in the PRIVATE ops repo (see below), batched commits per
the existing mirror pattern, size-capped/rotating, advisor-readable within
~10 minutes via the same Contents API.

## PRIVACY AMENDMENT (director, 2026-07-11)
The log lives in a separate PRIVATE repository, `synthetic-enterprise-ops`
(director is creating it and extending the PAT's access — BLOCKED on those
two director clicks; prepare everything else meanwhile: remote config, push
path, log format). RELOCATE the existing ntfy/from_rich mirror there too —
its public placement was a compromise, now unnecessary. Public repo keeps
zero message-traffic mirrors. Scrubbing of genuine secrets still applies
(raw secrets belong in NO repo, private included); personal/operational
content may flow unredacted in the private log.

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
