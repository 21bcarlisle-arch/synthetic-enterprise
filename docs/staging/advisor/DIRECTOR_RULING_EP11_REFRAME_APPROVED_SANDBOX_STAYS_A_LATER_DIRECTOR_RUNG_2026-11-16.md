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
