**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Mothball NTFY to the director's phone; the advisor channel replaces it (2026-10-15)

**The director's words, to his advisor, 15 Oct 14:08 BST:** "Should we not mothball the ntfy alerts? I don't ever read them. And you can stage so it's redundant."

Do this after the advisor channel (`DIRECTOR_STEER_ADVISOR_CHANNEL_NO_PASTE_2026-10-15.md`) is working. Until then, NTFY is how that channel is acknowledged.

## WORK THIS CREATES (canonical, in-document)

1. **Stop pushing to his phone, but keep the record.** Every alert the machine would have pushed still lands as a line in the ops repo's `ntfy-mirror.md`, or its successor. That is the advisor's reading surface. Only the phone push stops. "Remember to mothball properly": stop what feeds the push, retire alerts nothing reads, and record which alerts went and why.
2. **Retire the inbound route.** The NTFY responder is retired: it last acknowledged a message on 6 October. Director input now arrives through the console and the advisor folder. Remove the inbound topic's listener and anything that only existed to serve it. Do this by construction, so no inbound text can reach a lane by that route again.
3. **Escalations move to what he and his advisor read.** Escalations go to `for_the_director` and the stretch log, which the advisor reads and relays. Concerns, proposals and "this needs you" items belong there.
4. **One exception, only if it fires rarely: the dead-man's alert.** If the machine is down or wedged for more than six hours, with nothing landing and no lane alive, a single push still goes to his phone. If the dead-man switch can't say that reliably in one message, drop it too and say so.
5. **Canon and CLAUDE.md, marked as his words.** In canon D5, D7 and G8 and in CLAUDE.md's operating model, the channels become the console and the advisor folder in, and the stretch log and `for_the_director` out. "Escalate on NTFY, never in the window" becomes "escalate in for_the_director, never in the window".
6. **Report** in the stretch log: what was retired, what stays, and the dead-man's decision.

Keep going between pieces.
