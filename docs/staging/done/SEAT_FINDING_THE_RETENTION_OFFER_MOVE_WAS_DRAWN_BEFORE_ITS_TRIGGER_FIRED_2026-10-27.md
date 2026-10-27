**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** unassigned · **Atom:** `unminted` — Lane 0 delivery

# The retention-offer move was drawn before its trigger fired, so it is released without code

**Fate (2026-10-27, seat-executor):** DONE -- released, no build. The continuation is dropped; the
trigger stays where 361ddb90a5 put it, on W2_39 and the tariffs page.

Item: `the-retention-offer-moves-with-the-statement-when-households-decide-in-the-window`, handed off
as a LIVE continuation minutes after 361ddb90a5 landed.

## The premise, re-measured

The item's own WHY makes it conditional: "*Once* W2_39 gives households a decision inside the 42-49
day window, an end-day offer arrives after they decide and is a defect." 361ddb90a5 ruled the
same thing: moving only the offer is a relabelling, not a fix, until the world answers inside the
window. On origin/main at this draw, the world does not:

- `simulation/run_phase2b.py`, where the SLC 22C statement is sent: "The act only: no household reads
  it (GAP, tariffs_and_the_default_tariff page)."
- W2_39 in the maturity map, at L2: "NOT L3: the fixed-term roll is unwired". The only stay-or-go
  answer a fixed-term household gives is still the roll on the end day.

So the condition is false. If the offer moved to day 42 now, it would be priced against a market 42
days older than the one the household compares it with. That is the defect 361ddb90a5 declined to
ship.

## What done means, and where it now lives

The offer moves with the statement, priced against day 42's market, in the same change that gives
fixed-term households a decision inside the window. That is W2_39's L3 work: wiring the fixed-term
roll to read what the company sent. It is step-4 world work, so the correctness stretch does not hold
it. It is not drawn here. The trigger is already written on
`docs/market_research/tariffs_and_the_default_tariff_2026-10-25.md` ("When the retention offer is
made"), so no new row is needed.

## Why it was drawn at all

The previous turn's commit said `NEXT: none` because the work waits on W2_39. The hand-off then wrote
the same work down as a LIVE continuation without that condition. A continuation is offered as soon
as it is written, so a conditional piece handed off this way gets drawn before its condition holds.
The cheap correction is the one taken here: re-measure at the draw, then drop it. A gate on
`--hand-off` would be another ceremony, and it is not proposed.
