<!-- DROPPED 2026-07-29 by director ntfy: "The authority seam approval is withdrawn -- we removed signatures entirely. Drop it and carry on." The signature/phone-signer workflow is CLOSED, not parked. Disposition: docs/staging/done/RESPONSE_AUTHORITY_SEAM_WITHDRAWN_2026-07-29.md. Archived, not deleted -- git history restores it if a reserved act ever needs the channel. -->
<!-- PARKED in_progress 2026-07-29: consumed as a MINT SOURCE (§2+§4 WORK_DEFINITION). All three
WORK-THIS-CREATES deliverables are minted as self-drawable atoms (do NOT re-mint):
  #1 PHONE_SIGNER_SETUP.md            -> PLANNER_MINTED_phone_signer_setup_doc_2026-07-29.md
  #2 draw-priority answer + R15 fix   -> PLANNER_MINTED_director_act_rung_zero_draw_2026-07-29.md
  #3 terminal audit of §1            -> PLANNER_MINTED_phone_signer_terminal_audit_2026-07-29.md
OPEN sub-item blocking archival: the ruling's Acceptance (director sends one live signed ruling from his
phone with NO terminal, and it releases its atom on the next tick) is a DIRECTOR-PRESENT step — it
unblocks only after #2 (latency, first) and #1 (channel) are BUILT and the live E2E proof runs.
Sequence per §2: #2 before #1; #3 is #1's exit gate. -->

# [DIRECTOR-RULING] — Phone-signer setup, delivered as a DOCUMENT not a console session. And: console is the last resort. (2026-07-29)

**Type:** [DIRECTOR-RULING] via advisor bridge. Priority immediately after the literal-act list.

## 0. The standing rule, first — because the advisor keeps breaking it

Director: *"Why am I having to paste this? Defeats the point of you. We've been fighting against this since the start."* Correct.

**RULE: the console is the LAST resort, not the first.** Before anything is routed to the director's terminal, it must fail this test: *can this be staged, or written as a document the advisor relays?* Almost always it can — staging is read every tick and the advisor holds that write path.

**Genuinely console-or-device-bound, and nothing else:** one-way doors, safety-control changes, and provisioning a secret onto the director's own device. **Information is never console-bound.** A walkthrough, a set of instructions, a diagnosis, a proposal — all of these are documents.

The advisor's habit of reaching for a console paste when something feels stuck is recorded as the error it is: the console is not more reliable, it is merely more visible to the advisor.

## 1. The phone-signer setup — produce it as a DOCUMENT

Write `docs/design/PHONE_SIGNER_SETUP.md` containing the complete setup, **written for a non-technical reader on a phone, as discrete numbered steps**, each one a single action with an expected result. The advisor will relay it one step at a time; **the director will not open a terminal for any of it.**

It must cover: what to install or configure on the phone; how the director generates or receives the key **without it ever being transmitted through any chat, written to the repo, or logged**; how a signed ruling is composed and sent from the phone (the exact message shape); and how to verify a signature was accepted.

**If any step genuinely cannot be done from a phone**, say so explicitly and name the minimum irreducible act — do not pad the console back in by assumption.

## 2. Answer this BEFORE the setup is built

**Do director acts draw ahead of everything?** The console act of 2026-07-28 ~19:40 BST was correct and sat unconsumed for roughly eleven hours behind cooldown re-stamps and re-verifies. **A faster channel with the same latency is worthless.**

State plainly whether a signed `BUILD_OPEN` / `LEVEL_UP_PROPOSED` releases its atom on the **next tick**, and if not, **fix that first** — director-authored acts are rung-zero, ahead of staged rulings, campaigns, backlog and HARDEN alike, with an R15 reproducing last night's state (a director act present, cooldown work available, the act must draw first).

The three problems are separate and only one is the channel: **channel** (where the director must be — the signer fixes this), **latency** (how long an act takes to land — §2 fixes this), **volume** (how many acts are needed at all — the literal-act list and the block taxonomy attack this). Do not let the signer's completion be read as the whole problem solved.

## 3. Volume — the target, stated

Routine director acts should approach **zero**: blocks self-release on elapsed windows or twin authority wherever the wall permits; genuinely reserved acts are rare; and when one does occur the [ACT] states the exact verb and payload so a single tap clears it. Twenty-two blocked items requiring twenty-two authorisations is a design failure, not a workload.

## WORK THIS CREATES

1. `PHONE_SIGNER_SETUP.md` — phone-only, numbered, one action per step, with the irreducible acts named honestly.
2. A plain answer on director-act draw priority, and the rung-zero fix with its R15 if the answer is no.
3. Confirmation that no part of §1 requires a terminal — or precisely which part does and why.

Acceptance: the director completes phone-signer setup and sends one live signed ruling **without opening a terminal at any point**, and that ruling releases its atom on the next tick.

**Risk & proportionality:** documentation plus a draw-priority fix; the key never leaves the director's device. Tag: **proceed, after the literal-act list.**

— Advisor bridge, recording the advisor's console-by-default habit as the error. 2026-07-29.