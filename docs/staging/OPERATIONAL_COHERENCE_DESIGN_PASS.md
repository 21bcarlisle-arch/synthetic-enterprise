# DESIGN THE OPERATIONAL LAYER AS ONE SYSTEM — stop patching, understand why, design the whole (P0 mandate, director-decided)

**Staged:** 2026-07-16 by advisor, **director-decided** — the most important
insight of a long failure night. Disposition: MANDATE (governs operational work
going forward; ranks ABOVE more features and ABOVE more operational patches).

## The diagnosis (director's, verbatim intent)
Tonight was not caused by any single bug. It was caused by the OPERATIONAL LAYER
being built by ACCRETION, not DESIGN. Every mechanism exists as a PATCH reacting
to the previous patch's symptom:
- cron auto-restart = patch for "things keep stopping" -> masked that the stack
  couldn't stay up, and resurrected a BROKEN stack every 30 min.
- session-watchdog = patch for "sessions die" -> started KILLING sessions
  (detected "MULTIPLE interactive sessions" and reaped the director's console,
  exit 143).
- deadman = patch for "silent stalls".
- transition-only / predicate / escalation-routing = patches for the previous
  notification patches' side effects.
**Each fix created or masked the next problem. We were fixing fixes.** The result
is a pile of individually-sensible ideas that interact in ways NOBODY DESIGNED,
so when two parts conflict there is no principle to resolve it — only another
patch.

Director: *"The issue isn't what we tried to do — it's the tinkering to get
there, each fix creating or masking another problem. What we need is to
understand WHY we did things. Create the goal, then design as a single system.
Not a patchwork of ideas and fixes."*

## The mandate
**Before any more operational patches: design the operational layer as ONE
COHERENT SYSTEM, from its PURPOSE.** For each part, state (a) its PURPOSE, (b) the
GUARANTEES it provides, (c) WHY it exists — traced to the goal, not to the last
symptom. Resolve the conflicts between the accreted mechanisms BY DESIGN, then
rebuild to that design, ABSORBING or DELETING the patches.

Every mechanism must have a reason that traces to the goal, so that when two
parts interact, the DESIGN says how they should — rather than the interaction
being discovered by breakage.

## The parts that must be designed as one (not patched separately)
1. **Process / session lifecycle** — what runs, who owns each process, how it
   starts, stops, restarts, recovers. Designed — NOT "cron + watchdog + deadman"
   patched together. Must answer: how is the director's console session
   distinguished from managed daemons so it is NEVER reaped? What restarts what,
   under what authority, with what health gate?
2. **Deployment model** — how COMMITTED code becomes RUNNING code. Designed so
   "committed ≠ deployed" (tonight's recurring lie) CANNOT happen — a fix is not
   live until the running process is on current HEAD, by construction.
3. **Notification model** — ONE designed contract for what pages the director and
   why (transition-only, self-contained, typed by source: real-alarm vs
   test-fixture vs director-echo). NOT four paths each independently patched for
   spam.
4. **Test / isolation boundary** — designed so test code CANNOT touch production
   (pytest can never send a real NTFY, spawn a real session, or write real
   state). Designed, not discovered when pytest spammed the director.
5. **Recovery model** — designed crash/reboot/restart recovery to a KNOWN-SAFE
   state (fail-closed, deterministic), replacing the accreted
   cron-resurrects-whatever-was-there.

## Method (this is an architecture pass, a different kind of work)
- Start from PURPOSE and GOAL, top-down — not from the current mechanisms
  bottom-up. Ask "what should this system do and why," then design, then map the
  existing patches onto the design (absorb the good, delete the redundant, fix
  the conflicting).
- This is the operational twin of what ARCH1 does for the domain: turn an
  accreted tangle into a designed system with clear seams and stated reasons.
- Consider a KNOWN-GOOD baseline: identify when the operational layer last worked
  cleanly (git history of start_worker.sh, the watchdog, the executor, conftest);
  a recent harness change may be a regression worth reverting rather than
  patching over. Design forward FROM a known-good point, not from the current
  broken accretion.
- Output: a written operational DESIGN (purpose/guarantees/why per part + how the
  parts relate + conflict resolutions), THEN an implementation that rebuilds to
  it. The design is the deliverable first; code follows the design.

## The spine (record in CLAUDE.md as an operating principle)
**Understand WHY. Design the WHOLE. Do not accrete.** A mechanism added to patch
a symptom, without a designed reason that traces to the goal and without
consideration of how it interacts with the whole, is forbidden — it is exactly
how tonight happened. New operational mechanisms must state their purpose and
their fit to the system design before being built.

## Ranking
This ranks ABOVE new features and ABOVE further operational patches. Tonight's
headless fix job stops the bleeding; it is still patching. THIS is the actual fix
for the class of failure tonight represents. Do it deliberately, when the stack
is stable and with a clear head — it is design work, not firefighting.

## DoD
A written operational-system design covering process/session lifecycle,
deployment, notifications, test isolation, and recovery — each with purpose,
guarantees, and why-it-exists, plus how the parts relate and how the current
accreted mechanisms' conflicts are resolved by design; identification of a
known-good baseline and an explicit keep/revert/rebuild decision per mechanism;
then an implementation that rebuilds the operational layer to that design,
deleting or absorbing the patches; the "understand why / design the whole / don't
accrete" principle recorded in CLAUDE.md as a gate on future operational work.
