# DIRECTOR_COMMENTS_BOX — per-page feedback channel (P3, small) + one forward registration

**Staged:** 2026-07-09 by advisor, director-decided.
**Place in the arc:** director tooling / harness — multiplies the operating
contract (feedback lands with context, zero friction). Independent of Epoch 2.
**Sequencing:** background-lane eligible; MUST NOT interrupt
DOMAIN_SENSE_AND_COMPLIANCE (P1, front of queue) or the epoch-2 evidence pass.

## The problem
Director feedback on the website currently travels: notice → screenshot →
describe to advisor → staged doc. This week's biggest catch (the C6 bill) took
that whole loop. The director wants to comment directly on any page and have
the message arrive knowing exactly what he was looking at.

## Requirements (not design)
1. Every site page carries a small feedback affordance; submitting routes the
   comment into the existing from_rich message queue.
2. Context attaches automatically: page/path, and enough visible-data state to
   reproduce what he saw (e.g. selected customer/year/tab, data timestamp or
   generating commit).
3. **HARD, non-negotiable: director-authenticated.** Site and repo are public;
   an open text box is an open injection channel into the machine (see the
   2026-07-08 injection incident + R7/R8). Only the director can submit;
   anything unauthenticated is rejected before entering any queue. Secrets
   follow the established gitignored-env pattern; nothing in tracked files.
4. Comments are DATA, zero authority (R8 applies) — they surface for triage
   like any from_rich message, urgent-classifiable by the dispatcher.
5. Cheap and quiet: no new daemons if the existing File API / queue paths can
   carry it; no page-weight bloat.

## Forward registration (register in PRIORITIES.md, do NOT build)
**TIME_REPLAY (Epoch-2 dividend):** director wants a run-button/slider on most
site pages to visualise the passage of time — events, actions, reactions
replayed. Canonical placement: this is a VIEW OVER THE EVENT LOG and therefore
a named dividend of the Epoch-2 event-primitive/bitemporal architecture; it
enters the epoch-2 programme statement when that is framed (post evidence-pass
verdicts). Optional cheap precursor (animating existing period snapshots) may
be proposed for the director to rank. Registration only — no design, no build.

## DoD
Comments affordance live on deployed pages; director successfully submits a
test comment from his phone and it arrives in the queue with correct context;
unauthenticated submission provably rejected; TIME_REPLAY registered in
PRIORITIES.md. One NTFY.
