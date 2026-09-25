**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** `W2_30` (couples `W2_18`)

# Three electrically heated homes hold a gas contract, and the book settles ~9.5 MWh of gas a year that their physics says they never burn

**Found 2026-09-25 while grading the fresh gas-shape run** (`SEAT_PREREG_HOW_MANY_GAS_HOUSEHOLDS_...`).

## The reading

Of the 98 resi gas customers, 13 keep the population 70/30 split. Ten of those have no fabric trace
(their electricity twin has no weather cell; pre-registered, and it held exactly). **The other three
refuse for a different reason: "the household consumed no gas over the window".** They are the only
three homes on the gas book whose drawn heating is not a gas boiler:

| customer | drawn heating | gas AQ on the contract |
|---|---|---|
| SYN-2016-012 | electric_storage | 9,468 kWh |
| SYN-2016-037 | electric_storage | 9,198 kWh |
| SYN-2016-056 | electric_direct | 9,825 kWh |

(Census over the gas book: 67 combi, 28 system boiler, 2 storage, 1 direct.)

## Why this is odd against how the trade works

A home heated by storage heaters or direct electric usually has **no mains gas at all**, or a gas
supply for cooking only (a few hundred kWh a year). It does not carry a 9.5 MWh space-heating AQ.
The AQ is the industry's own forecast of a meter's consumption. Settling it against a house whose
physics burns nothing bills gas the world never consumed. That is value transferred, not created,
and invisible to the company because it reads the AQ, not the physics.

## Where the incoherence is

The world draws `heating_system` for the dwelling **independently of the fact that the customer is
on the gas book**, and `has_mains_gas_supply` is `None` on the record. The per-household shape
correctly refuses (physics gives zero). The fallback then settles the gas term on the population
split of the full AQ. The refusal and the settlement disagree about whether the house uses gas, and
nothing reconciles them.

## Not done here, and why

This is not fixed in this turn. There are two candidate remedies with opposite effects on the book:
(a) the draw conditions heating on the fuel the supplier holds; (b) the gas contract is only minted
for a home the world says has mains gas and a gas heating system. Which one is right is a question
about how the synthetic book is constructed, so it gets asked before building. **Question for the
director, with a recommendation:** (b). The world owns the house, and the supplier's contract
should follow what is plumbed in, which is the epistemic direction every other B12 repair has taken.
The three homes' gas legs would disappear from the book.

## Resolved — 2026-09-25, `6dcdd0339` (on origin via `7099cc486`)

The paragraph above said this would be asked before building. It was not asked: I recommended (b)
on NTFY, said I would proceed unless told otherwise, and then measured the cause, which turned out
narrower than either remedy. **Neither the draw's heating nor the contract rule was wrong. The
founder path read the account's fuel from the draw record's `commodity`, a second draw, instead of
the premise's.** The campaign path already used the premise (`_gas_leg_for`). The founder path now
applies the same predicate and skips the candidate, as it already skips an unpriceable band. Control:
`tests/simulation/test_a_drawn_gas_founder_sits_on_a_gas_heated_home.py`, with a reachability leg
and a property leg; disabling the guard reds it on exactly these three homes. Gate: 1,026 passed.
