<!-- SUPERVISOR_DRAW: self-drawable -->

# [PLANNER-MINTED] Terminal-audit of §1 — confirm no step needs a terminal, or name precisely which does and why (2026-07-29)

**Source ruling:** `DIRECTOR_RULING_PHONE_SIGNER_NO_CONSOLE_2026-07-29.md`,
WORK-THIS-CREATES **#3** ("Confirmation that no part of §1 requires a terminal — or precisely which
part does and why.").
**Serves:** §0's standing rule — *the console is the LAST resort, not the first* — applied as an
adversarial check ON the setup document, so the agent's "console-by-default habit" (§13, recorded as the
error it is) cannot silently pad a terminal step back into a phone-only walkthrough. §21 verbatim: do
not pad the console back in by assumption.
**Real-world fidelity gained:** none — this is a truthfulness/anti-regression gate on deliverable #1.
Value = the director's Acceptance test (*"without opening a terminal at any point"*) is honestly met, or
the exact irreducible terminal act is named with its reason instead of being hidden.

**Lane:** DISCOVER (read-only audit of the #1 document + the underlying mechanism; no code change).
Self-drawable now.
**Target level:** doc-only confirmation appended to / committed alongside
`docs/design/PHONE_SIGNER_SETUP.md`. No maturity-map level claimed.

## Why a separate atom (not folded into #1)
The ruling lists it as a distinct deliverable and the director wants it stated plainly — an adversarial
audit performed with fresh eyes (the cold-eyes technique) is stronger than the author self-certifying.
It is the **exit gate** on #1: #1 cannot be marked done until this audit passes or names the exception.

## Exit criteria
- Every numbered step of `docs/design/PHONE_SIGNER_SETUP.md` is walked and classified **phone-doable**
  vs **terminal-required**, checked against the real mechanism (not against the prose of #1 alone —
  quote the function/command each step actually invokes).
- **Output is one of two honest statements, committed:**
  (a) *"No part of §1 requires a terminal"* — with the per-step evidence table backing it, OR
  (b) *"Step N requires a terminal because <precise reason>"* — naming the **minimum irreducible act**
  (e.g. a one-time out-of-tree key placement on the daemon, which is a DAEMON-side act the director
  never performs on his phone anyway, vs a genuine director-phone terminal step). Distinguish
  *director-phone* terminal need (the thing the ruling forbids) from *daemon-side provisioning already
  done* (not a director act at all).
- **Anti-self-flattery (R15 spirit):** the audit must be able to FAIL — if #1 hides a terminal step
  behind vague phrasing, this atom must catch it and force it explicit. A pass that would survive a
  planted terminal step in #1 is theatre; state the specific step that WOULD trip it.

## Deps
- **depends_on:** `phone_signer_setup_doc` (deliverable #1) — there is nothing to audit until the
  document exists. This atom is #1's acceptance gate; run it at #1's phase-close.

## Coverage mapping
- PHONE_SIGNER #3 → **this atom.**
- PHONE_SIGNER #1 → sibling `PLANNER_MINTED_phone_signer_setup_doc_2026-07-29.md`.
- PHONE_SIGNER #2 → sibling `PLANNER_MINTED_director_act_rung_zero_draw_2026-07-29.md`.

**Propose-then-proceed window:** proceed by default (read-only audit, reversible via git).

## Deliverable (verbatim)
> Confirmation that no part of §1 requires a terminal — or precisely which part does and why.
