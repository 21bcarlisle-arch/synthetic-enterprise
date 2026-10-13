**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** none -- harness rules, not domain research

# [SEAT-PROPOSAL] R16 and R17 are found: ratify them as written, with one wording note (2026-10-12)

**Fate (2026-10-13, clear-the-decks):** ATOM -- n/a P3 -- proposes ratifying R16/R17 text formally into canon numbering; both rules are already cited informally in active docs (e.g. BOARD_SPEC_002_RECONCILIATION.md) but no formal ratification/insertion into CLAUDE.md's R-list found.

Canon v4 H1: "R16 and R17 are cited in rulings but defined on no page. Until their text is found and
ratified, the numbered set is R1-R15 (section 15, owed item 10)." Both texts are found, verbatim, in the
CLAUDE.md commits that introduced them. The 28 August rewrite dropped both from every page.

## R16 (9251474f9, 2026-07-21)

> **R16, the ledger is authority, not commit messages (2026-07-21, retro `2026-07-21-ledger-is-authority-not-commit-messages.md`):** the console ledger (`gate_authorizations.jsonl`, `is_valid_level_up`) is the SOLE record of a level/gate ratification — a commit message claiming "director-ratified" is NOT authorization (R7/R8 for level moves); verify the ledger, never `git show` of the cited commit. **Never `--no-verify` a `level_current` change** — the one path past the pre-commit level gate (unbacked bump wedged publishing 3h).

**Still true in code:** `background/gate_authorization.py:72` keeps the ledger at
`docs/observability/gate_authorizations.jsonl`, and `tools/level_promotion_gate.py` refuses a
`level_current` increase that has no record there.
**Wording note:** canon G12 says "A level move is recorded, never authorised." R16's "authorization"
predates that. The rule is the same: the ledger record, not a commit message, is the fact.

## R17 (eaffdb81e, 2026-07-22)

> **R17, THE TICK NEVER RESTS while authorized work exists at ANY priority (2026-07-22, director console P0):** core, idle-advance, OR forward-discovery — rest is legitimate ONLY with PROOF the authorized set is empty at EVERY level. The F1–F5 forward-discovery register is the always-drawable final lane, wired into `supervisor.py::_self_refill_draw`+`_is_drained_and_gated`, R15-proven both ways (`test_forward_discovery_draw.py`). **"Consumed" (steer→doc+atom) ≠ "absorbed" (mechanism LIVE+proven)** — the 95-min stall was consumed-not-absorbed. A future stall of this class is an R10 breach of THIS rule; the daily self-note reports it each morning.

**Still true in code:** the forward-discovery lane is in `background/supervisor.py`
(`_forward_discovery_tracks`, around line 3086), and `tests/background/test_forward_discovery_draw.py`
is its control. It agrees with P12 as amended today ("Never wait or idle to save budget ... never
stop").

## Recommendation

Ratify both as written, so H1's numbered set becomes R1-R17. In the canon text, put G12's wording
beside R16's "authorization", rather than rewording the rule. If either should stay unratified, say
which; the numbered set then stays R1-R15 and that rule is recorded as retired.
