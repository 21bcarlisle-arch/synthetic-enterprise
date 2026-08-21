**Severity:** LATENT · **Lane:** W2_customer_generator · **Atom:** PB1_population_target_and_its_price

# The population ceiling is about 80 customers, it costs 22.4 MB each, and one seam owns the whole bill

DISCOVER/FRAME output for PB1 (`loop_stage: idle`, so BUILD is parked and this is the work that
is available). Its dependency AO12 is satisfied at L2/2, and AO12 already measured the answer —
this reads that measurement rather than producing a new one.

## The number, and its price

PB1 asks for a population that was **priced before it was bought**. The price is measured, in
`docs/design/scale_probe_10k_report.json` (2026-08-10):

| seam | survived | tore at | outcome | marginal RSS per customer |
|---|---|---|---|---|
| **settlement_build** | 20 | **100** | memory_error | **22,928 KB (~22.4 MB)** |
| run_output_serialize | 1,000 | 10,000 | memory_error | 399 KB |
| population_draw | 1,000 | 10,000 | error | 1.1 KB |
| site_publish | 10,000 | — | — | ~0 (flat) |
| git_transport | 10,000 | — | — | ~0 (flat) |

**One seam owns the bill.** `settlement_build` costs **fifty-seven times** more per customer than
the next seam and **twenty thousand times** more than the population draw. It tore at n=100, at
customer index 80 — so the ceiling is not 100, it is **80**, and the probe recorded exactly where.

The two cheapest-looking seams are flat: `site_publish` and `git_transport` do not grow with the
book at all. Whatever the population becomes, publishing it is free.

## What this makes PB1's answer

Today's book is 14–21 accounts depending on which surface you read: `site/data/customers.json`
says 14, and `LATEST.md` carries 21 and 18. The 21/18 pair is NOT an undiscovered inconsistency
— LATEST.md §137-138 already records it as a known control defect (`site/data/customers/*.json`
reads 21 accounts / 1682 bills / 30 not footing, while the printed-footing control reads
`site/state/billing_ledger.json` at 18 / 1557 / 0). Named here only so nobody reads the ceiling
arithmetic below against the wrong denominator. Either way the book sits far under the wall.

So the honest proposal is a range with a wall at the end of it:

* **Any population up to ~80 is affordable today**, at 22.4 MB of peak settlement RSS each.
  Going from 20 to 80 costs roughly 1.3 GB of peak RSS and nothing else — no other seam moves.
* **80 is a hard wall, not a soft one.** The tear outcome is `memory_error`, not a slowdown.
* **Above 80 is not a bigger machine, it is a different settlement build.** At 22.4 MB/customer,
  1,000 customers needs 22 GB of peak RSS for that stage alone. Buying RAM buys a linear
  extension of a linear problem.

## The part worth arguing about

The atom's framing is that scale "stops being an inherited default and becomes a proposed
number". The measurement says something sharper: **there is no interesting choice of population
size below 80, and no reachable one above it.** Proposing 40 rather than 25 is not a decision
with consequences — both are far under the wall and neither moves any other seam.

So PB1's real content is not the number. It is: **the population question is currently a
settlement-build question wearing a different hat.** Until 22.4 MB/customer comes down, the
population target is dictated by one stage's memory profile, and any figure proposed for it is
that stage's constraint restated.

That is a finding PB1 can close on, and it makes the atom's L2 target reachable without
inventing a target number nobody can act on.

## What I did NOT do, and why

**No new measurement.** AO12 ran this in August and its report is intact and checkable. Re-running
a 10k probe to restate a number already on disk is the seventh-pass shape the director named
today. If the settlement seam is changed, the probe is the thing to re-run — not before.

**No proposal to fix settlement_build.** AO12's own scope note is explicit that probe findings
return to the director before any substrate decision, and a 22.4 MB/customer settlement build is
exactly that class. Naming the cost is this document's job; spending it is not.

## Provenance

Every figure above is read from `docs/design/scale_probe_10k_report.json`, generated
2026-08-10T17:07:43Z, whose `prediction_register_sha256` pins the predictions it was scored
against. The advisor's predicted seam ordering and the observed ordering match
(`ordering_matches_advisor: true`), over the two seams with a measured memory key.
