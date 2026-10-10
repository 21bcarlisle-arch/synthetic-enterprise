**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

# SEAT PROPOSAL — home-mover retention as a supplier lever (2026-10-10)

*Delivery seat. The director, 2026-10-10: "Next supplier items, unless you see better: make the reactive
save on the loss notice a live supplier capability in the run, then home-mover retention now that moves
are on, then debt management as a next best action." Filed before any code, with its predictions.*

## What the lever is

When **our** household moves out, it tells us at least two Working Days before the move (SLC 24.1(a);
`docs/market_research/home_moves.md` §8.1). That notice is the one moment a retention offer can be made
before the household is gone (§8.4). A **move-with-us offer** supplies the household at its new home,
usually by carrying its tariff across and waiving the exit fee closing the old contract would trigger
(§8.3). At the new home another supplier is the incumbent, so taking us with them is a switch gained
at the destination, through the ordinary registration route.

## What exists today, and what does not

- **The world draws the destination and nothing reads it.** `sim/customer_state_layer.draw_home_move`
  returns `mover_arrives` (a derived destination premise, the same occupancy, starting on the move date).
  No caller consumes it, so every mover simply leaves our book.
- **The company receives no move-out notice.** §8.2 defines the honest observable (meter point, move-out
  date, date the notice arrived; destination absent unless the household says so), and nothing carries it.
- **No take-up rate is published** (§8.5 G8.4, re-confirmed by Ofgem OFG1164, June 2026).

## Proposed build, smallest first

1. **The notice (seam).** A move-out notice wire, dated two Working Days before the move: the latest notice
   consistent with the world's own decision that every mover notified in time (§8.1). Company side: a
   register that files it.
2. **The offer (company).** On the notice, the company decides per household whether to offer to carry the
   tariff to the new home with the exit fee waived. The decision reads only what it holds: its own
   forward value of the household (its CLV belief), the tariff in force, and the notice. A household the
   company knows to be vulnerable is never offered less than its twin (director, 2026-10-08).
3. **The world's answer.** No take-up rate exists, so none is invented. The household answers on **the same
   renewal roll** it would face at its next renewal, at the carried tariff (as the save does on the loss
   notice), and a labelled sensitivity `k` scales that response between 0 (no mover ever takes us) and 1
   (a mover stays as often as a renewing household at that price). The two ends are run and reported. A
   result that turns on `k` is reported to the director as turning on an unpublished number.
4. **The destination supply.** A household that takes us is supplied at the destination premise
   (`mover_arrives`) under a new account on the carried tariff, with the destination's demand drawn by the
   world's existing premise draw. This is the world work the lever needs, and it is admitted because it
   blocks this supplier result.

## Measurement and predictions (written before any code)

Arms on the production book: `off` (no offer, today) and `on` at k = 0 and k = 1. Same base seed.

- **P1, byte-identity.** `off` equals today's run on every account-term; `on` at k = 0 equals `off`.
- **P2, the stayers.** No stayer's price moves between `on` and `off` at either end: a retained mover is
  supplied at its carried tariff, and its margin must not enter the feed the portfolio premium reads (the
  save's lesson, `_held_on_a_save`).
- **P3, vulnerability.** Zero twin shortfalls; no known-vulnerable mover left unoffered while others are.
- **P4, the size.** The 400-founder run settles ~3,100 account-years; the world's move hazard runs from
  0.073/yr (all tenures) to 0.175/yr (private rent; EHS 2023-24, `home_moves.md`). So I expect
  **roughly 230-540 move-out notices** over the window, nearer the low end for an owner-heavy book; the
  run's own `home_move_outs` count is the check. At k = 1 I expect most offered movers to be
  retained (renewal stay share ~0.60), and `on` minus `off` total net positive, of the order of the
  retained accounts' remaining margin; at k = 0, exactly zero. I cannot predict the size better than that,
  and the result **will** turn on `k`.

## What this needs from the director

Nothing to start. The take-up gap is carried as `k` with both ends reported, exactly as the save's
response scale was. If the result turns on `k` (P4 says it will), the director is told so with both ends,
and a practitioner's view of how often a mover takes their supplier is the one number that would settle it.
