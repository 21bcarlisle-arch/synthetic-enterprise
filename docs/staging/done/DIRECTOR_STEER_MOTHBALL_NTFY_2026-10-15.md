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

## Done (2026-10-15, console seat)

1. **Push stopped, record kept** (`565bd6303`). Every message now goes to `ntfy-mirror.md` (direction `out-mothballed`) and the director input log. Nothing reaches the phone except item 4.
2. **Inbound route retired by construction.** `ntfy_responder` and `dispatcher` have permanent no-op entry points and `retired` manifest rows, and their units are removed from the repo. On the box they are stopped, disabled and masked. The dead library is handed off as `retire-the-inbound-ntfy-library`.
3. **Escalations moved.** They go to `for_the_director` and the stretch log.
4. **Dead-man's push kept.** One `[DEAD-MAN]` message per episode, when nothing has landed for 6h and no lane is alive. It is rare by measurement: 0 fires of the hard rest cap in 47 days. A box that is wholly down cannot send it.
5. **Canon D5, D7, G8 and CLAUDE.md amended**, marked as his words.
6. **Reported** in the stretch log entry of 15 Oct: "The director's phone goes quiet".
