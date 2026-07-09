# ADVISOR_VISIBILITY — mirror messages to repo + push-before-notify (P3, small)

**Staged:** 2026-07-09 by advisor, director-approved.
**Place in the arc:** harness/director tooling — kills the copy-paste loop; the
repo becomes the advisor's eyes on the message channel, completing the
triangle: director's phone (NTFY), machine (queue), advisor (repo).
**Sequencing:** background-lane eligible; must not interrupt
DOMAIN_SENSE_AND_COMPLIANCE phases.

## Problem
The advisor can only see the repo. NTFY messages reach the director's phone
only, so reviewing them requires the director to copy-paste into the advisor
chat (he hates this, reasonably). Separately, today's NTFYs cited commit SHAs
(d3a731b4, 4662de70) that were not on origin hours later — claims the advisor
cannot verify are claims that might as well not exist (R9 spirit).

## Requirements (not design)
1. **Message mirror:** all outbound NTFYs and inbound from_rich messages are
   mirrored into a repo-tracked log (append-only, timestamped, direction-
   labelled), readable by the advisor via the GitHub API within ~10 minutes of
   send/receipt. Batched commits are fine (no per-message commit spam); rotate
   or cap so it never bloats.
2. **Secret scrubbing is a hard gate:** the repo is PUBLIC. Nothing enters the
   mirror containing the topic name, HMAC material, tokens, keys, or URLs that
   grant write. Scrub by allowlist/denylist at write time, with a test proving
   a message containing a secret pattern is redacted.
3. **Push-before-notify rule (CLAUDE.md):** any NTFY that cites a commit SHA or
   claims "committed" must be preceded by a push of that commit to origin.
   Push, then notify — never the reverse. Add to the phase-close checklist
   alongside the LATEST.md rule.
4. Mirror is DATA (R8): the advisor reads it; nothing in it carries execution
   authority.

## DoD
Mirror live and populated with the day's messages (scrubbed); advisor-side
verification: a message sent after deployment is readable via the GitHub API
within 10 minutes; the secret-redaction test green; push-before-notify in
CLAUDE.md; today's unpushed commits (d3a731b4, 4662de70 and successors)
pushed. One NTFY — which, per its own rule, arrives after the push.
