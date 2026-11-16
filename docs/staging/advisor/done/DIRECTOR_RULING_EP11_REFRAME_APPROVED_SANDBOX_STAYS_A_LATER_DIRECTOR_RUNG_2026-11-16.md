**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `EP11`

# [DIRECTOR-RULING] EP11 reframe approved: the bureau counterparty inside the walls, the real sandbox stays a later director-only rung

**Type:** RULING, through the advisor channel. Answers `for_the_director` row `ep11-is-titled-direct-debit-against-a` (raised 16 Nov).

**The director's words,** chat, Mon 16 Nov 09:27 GMT, replying "Yes and yes" to the advisor's line: "The machine wants to change its framing so the unhappy-path work happens inside the simulation, not in a separate sandbox. I recommend approving that."

## What is decided

- The proposal stands as filed. EP11 level 3 is a GoCardless-shaped bureau counterparty over the existing EP6 wire. All four Bacs reports arrive as world events, with AWACS added. A payment confirms only after the ARUDD window. Webhook-style duplicates and reordering are included.
- The live sandbox stays a later, director-only rung (level 4). Nothing here adds `gocardless.com` to the egress allowlist, opens a sandbox account under Poesys's name, or lets `company/` open a socket. Those remain reserved: console for the allowlist, the director personally for the account.

## Risk

- **Touches:** EP11's level definitions and the EP6 wire's consumers.
- **Blast radius:** payments arriving at the company. A reordering or duplicate that the desk mishandles changes balances and dunning, so it is serious under the correctness stretch's rule.
- **Probable failure mode:** duplicates double-post a payment, or a late ARUDD reverses a payment the desk already treated as cleared.
- **Mitigation, inline:** the money invariants judge the desk's handling, not the event's existence. Land behind a default-off switch, and read one book before turning it on.

**Proportionality:** contract-touching. Implement with the named mitigations. It is feature work under the correctness stretch, so it queues within the feature share.

## Done

Actioned 16 Nov by the delivery seat. The `for_the_director` row `ep11-is-titled-direct-debit-against-a`
is answered with his 09:27 words in a follow-up commit, committing `EP11_adapter_gocardless_bacs` to carry the reframe (the direction-seat window refused the row while the 09:23 orientation was writing that file). The
map row is retitled "Direct Debit against a bureau counterparty in the world" (it was "against a real
sandbox"). Its `level_note` in `docs/design/simplifications/EP11_adapter_gocardless_bacs.yaml` states
level 3 as ruled: the four Bacs reports including AWACS as world events, confirmation only after the
ARUDD window, duplicates and reordering, a default-off switch and one book read before it goes on. It
also states level 4, the live sandbox, as director-only. Nothing touched the egress allowlist, any
account, or `company/` sockets. The build itself is feature work under the correctness stretch and
queues in EP11's lane. It was not started in this turn.
