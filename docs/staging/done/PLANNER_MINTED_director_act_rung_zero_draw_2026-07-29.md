<!-- SUPERVISOR_DRAW: self-drawable -->

# [PLANNER-MINTED] Director acts draw at rung-zero — a signed act releases its atom on the NEXT tick, proven by R15 (2026-07-29)

**Source ruling:** `DIRECTOR_RULING_PHONE_SIGNER_NO_CONSOLE_2026-07-29.md`,
WORK-THIS-CREATES **#2** ("A plain answer on director-act draw priority, and the rung-zero fix with
its R15 if the answer is no.").
**Serves:** the ruling's core diagnosis — the three problems are *channel / latency / volume*, and this
atom is **latency**. §2 verbatim: *"A faster channel with the same latency is worthless."* The console
act of 2026-07-28 ~19:40 BST was correct and sat unconsumed for ~ELEVEN HOURS behind cooldown
re-stamps and re-verifies. The phone signer (deliverable #1) fixes *channel*; this fixes *latency*.
**Real-world fidelity gained:** none directly — operational authority latency. Value = a director act
(the only scarce resource, per MAKE_IT_STICK) is honoured immediately, not queued behind agent-internal
cooldown/HARDEN churn.

**Lane:** FRAME → BUILD (a real draw-ordering change in `background/supervisor.py`'s self-refill draw;
draw ORDER is a DIAL, reversible via git, no wall touched — R16/one-way-door/safety walls untouched,
this changes ORDER not AUTHORITY). Self-drawable now.
**Target level:** harness/operational mechanism + R15 proof. No maturity-map level claimed (this is
harness infrastructure, not a company/sim capability).
**Priority:** ahead of deliverable #1 (`phone_signer_setup_doc`). The ruling is explicit: *"Answer this
BEFORE the setup is built ... if not, fix that first."* A signer that lands acts into an 11-hour queue
is worthless, so latency is fixed before the channel doc is written.

## The plain answer this atom must produce FIRST (§2 requires the answer stated, then the fix)
State plainly, from a read of the live draw code (`supervisor.py::_self_refill_draw` /
`_maturity_map_draw_concurrent` / the gate-authorization consumers): **does a signed `BUILD_OPEN` /
`LEVEL_UP_PROPOSED` (console OR phone-native `record_director_ntfy_ruling`) release its atom on the
NEXT tick, ahead of cooldown re-stamps, re-verifies, HARDEN, campaigns, staged rulings and backlog?**
- If **YES** and provable: state it with the code path + a test that already proves it, and the fix is
  a no-op (record the proof, rest — do NOT invent a change to look busy, R12).
- If **NO** (the likely answer, given last night's 11h latency): the atom builds the rung-zero draw —
  director-authored acts are drawn **before every other lane**, and emits the R15 below.

## Exit criteria
- **The plain answer is committed** (a short finding in the atom's report or a `docs/design/` note):
  YES-with-proof, or NO-with-the-11h-repro. No hedge.
- **If NO:** `supervisor.py`'s draw places an unconsumed director-authored gate act (a fresh
  `gate_authorizations.jsonl` / `record_director_ntfy_ruling` entry whose atom is not yet released) at
  **rung zero — drawn ahead of cooldown re-stamp, re-verify, HARDEN, campaign, staged-ruling and
  backlog draws**. The released atom is taken on the very next tick.
- **R15 (the ruling names it exactly):** a test reproducing **last night's state — a director act
  present, cooldown/HARDEN work available — and asserting the director act MUST draw first.** Mutation
  both ways: with the rung-zero rule the director act draws on tick N+1; remove the rule (mutation) and
  it sinks behind cooldown → the test REDS. Fail-open guard: an *absent* or *malformed* director-act
  ledger entry must NOT be treated as "present" (no fail-open into a phantom rung-zero draw); an
  unreadable ledger is a FAILED read, not "no acts" (R15 fail-silent).
- **Isolation (memory `new_draw_rung_needs_fixture_isolation`):** the new rung reads the ledger from a
  test-pinned path, not the live `gate_authorizations.jsonl`, so the test cannot leak real acts.
- **R12:** cooldown/latency is a diagnostic; the fix reorders the draw, it does NOT delete cooldown or
  re-stamps for other lanes — director acts jump the queue, everything else keeps its discipline.

## Deps
- Depends on nothing to START (the answer + fix are self-contained in the harness).
- **Blocks the acceptance of deliverable #1** — the ruling's Acceptance clause requires the live signed
  ruling to *"release its atom on the next tick"*; that guarantee is THIS atom. #1's E2E proof cannot
  pass until this lands.
- Related built machinery (do NOT rebuild): the phone-native authority path
  `background/director_authority_channels.py` + `gate_authorization.py` (RATIFIED+WIRED 2026-07-22,
  HMAC key scrubbed from worker env 2026-07-23) already authenticates the act; this atom only fixes
  WHERE in the draw order an authenticated-but-unconsumed act sits.

## Coverage mapping (doorbell requires it)
- PHONE_SIGNER #2 (draw-priority answer + rung-zero fix + R15) → **this atom.**
- PHONE_SIGNER #1 (the setup document) → sibling `PLANNER_MINTED_phone_signer_setup_doc_2026-07-29.md`.
- PHONE_SIGNER #3 (terminal audit of §1) → sibling
  `PLANNER_MINTED_phone_signer_terminal_audit_2026-07-29.md`.
- NOT covered by the LITERAL_ACTS / LITERAL_ACT_LIST sibling mints (those are the blocked-item ledger +
  self-release sweep, a different ruling).

**Propose-then-proceed window:** proceed by default (ruling tagged *"proceed, after the literal-act
list"*; draw-order change is a DIAL, reversible via git; no authority/safety wall touched).

## Deliverable (verbatim)
> A plain answer on director-act draw priority, and the rung-zero fix with its R15 if the answer is no.
