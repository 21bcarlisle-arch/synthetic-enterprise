# ADVISOR_VISIBILITY — message mirror + push-before-notify (P3, small)

**Staged:** 2026-07-09 by advisor, director-approved.
**Place in the arc:** harness / operating contract — removes the director's
copy-paste burden (his explicit ask) and closes an observability gap found
today. **Sequencing:** background-lane eligible; must not interrupt
DOMAIN_SENSE_AND_COMPLIANCE phases.

## Problem
The advisor's only eyes are the GitHub repo (Contents API). Today's three NTFYs
cited commits (d3a731b4, 4662de70) that were NOT on origin — real local work,
invisible outside the terminal, unverifiable by the advisor, and at risk if the
machine dies. Separately, the director currently copy-pastes every NTFY and
console excerpt into the advisor chat by hand, which he hates and which loses
context.

## Requirements (not design)
1. **Message mirror:** all outbound NTFYs and all inbound from_rich messages
   are mirrored into a log under version control, readable by the advisor via
   the repo within ~10 minutes of send/receipt. Secret-scrubbed (topic names,
   tokens, signatures never appear). Batched commits are fine — no per-message
   commit spam; piggyback on existing commit moments where sensible. Rotation/
   size-capping so it never bloats the repo.
2. **Push-before-notify rule (CLAUDE.md):** any NTFY that cites a commit SHA,
   claims work is "committed", or announces a phase close must be preceded by a
   push of that work to origin. If deliberately batching pushes, say
   "committed locally, push pending" instead — never let the message trail get
   ahead of what origin shows. (Extends the existing LATEST.md-before-NTFY
   phase-close discipline.)
3. Mirror entries carry timestamp, direction (out/in), and the message verbatim
   (post-scrub) — enough for the advisor to review the day's traffic without
   the director pasting anything.

## DoD
Mirror live and readable via origin; a test entry visible; rule in CLAUDE.md;
today's so-far-unpushed work (C1 fix, obligations register) pushed as part of
adopting the rule. One NTFY (which itself appears in the mirror — the proof).
