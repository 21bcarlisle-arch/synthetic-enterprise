# ONE RULE: EVERY NOTIFICATION AND ESCALATION IS TRANSITION-ONLY / FIRE-ONCE (P1 class fix, director-decided)

**Staged:** 2026-07-16 by advisor, **director-decided**. Disposition: INTERRUPT
(the channel is actively spamming the director right now). This is a CLASS fix —
enforce ONE rule across ALL notification/escalation paths, not per-path patches.

## The evidence (from the ntfy mirror, verified)
- **Staging spam:** "New staged instruction — pending review" fired 3x in 2 min
  for SCHEDULED_HOUSEKEEPING.md (16:33/16:34/16:35) plus a `.bak` variant.
- **Answer re-dispatch:** every director reply is re-flagged "[DISPATCHER:
  URGENT] Message from Rich" and re-queued as a fresh urgent command.
- **Escalation re-ask:** the atom-X open-build escalation recurs (director report;
  same class).
- Earlier: the retro-cadence alarm spammed every cycle (fixed 8b7401af as an
  instance).

**These are ONE bug in four places: notifications fire EVERY CYCLE instead of
ONCE ON TRANSITION.** R5 (transition-only alerting) exists but was applied
per-path, so each new notification type re-derives the same spam independently.

## THE RULE (enforce as ONE mechanism, all paths inherit it)
**Every notification and every escalation is TRANSITION-ONLY and FIRE-ONCE:**
1. **Emit on STATE-CHANGE only.** A condition that is still true on the next
   cycle does NOT re-emit. Silence on unchanged repeats.
2. **An open escalation NEVER re-asks** until its state changes (i.e. until the
   director answers). Record per-item "escalated, awaiting answer"; suppress
   re-escalation of the same item while open.
3. **State resets on change**, so a genuine FUTURE occurrence still alerts
   (stale->fresh->stale must be able to fire again).
4. **Director replies CLOSE the escalation they answer** — matched to the open
   item — and are NEVER re-ingested as new commands or re-flagged urgent inbound.
   An answer is bound to its question, not free-floating re-parsable text.
5. Applies to: staging-doc announcements, escalations, cadence/staleness alarms,
   health checks, the dispatcher's urgent-flagging — and any path added later.
   A single shared "notify-if-changed / fire-once" primitive that ALL paths call,
   not a flag re-implemented per site.

## Root of WHY this keeps recurring (record it)
R5 was a rule, applied by hand, per notification. Every new notification type
missed it and had to be caught spamming and fixed individually (retro-cadence,
staging, escalation, dispatcher — four times). The fix is a MECHANISM every path
must route through, so transition-only is structural, not remembered. (This is
the make-it-stick lesson: a rule applied by hand decays; a shared mechanism
holds.)

## Belongs to the maintenance lane
This is the maintenance lane's notification-hygiene workload, elevated to a hard
rule. Fold the archive-on-consumption `.bak` defect in with it (droppings are the
same hygiene class).

## DoD
A single shared transition-only/fire-once primitive that ALL notification and
escalation paths route through; no notification re-emits on an unchanged repeat;
no open escalation re-asks while awaiting an answer; director replies close their
escalation and are never re-ingested/re-flagged; state resets on change so future
genuine occurrences still fire; `.bak` staging droppings eliminated. A check:
hold a condition true across N cycles — it emits ONCE; change it and back — it
emits again; answer an escalation — it closes and does not re-ask.
