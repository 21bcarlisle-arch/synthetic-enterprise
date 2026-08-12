# WORKER REPORT — the belief headline now knows which account it is talking about

**Severity:** RECORDED · **Lane:** D_billing_metering · **Status:** repaired — this report IS
the repair (D19 L0 → L2); the wrong measure it describes no longer runs.

**Date:** 2026-08-10 · **Atom:** `D19_belief_gap_is_distribution_only` **L0 → L2**
**Drawn as:** `H27_payment_belief_gap` 2→3 (HARDEN). **H27 stays at L2** — see the last section.
**R12:** the reshape was designed from the defect, never fitted to a value. Every number below moved
because the measure was wrong, not because it looked wrong.

## What was wrong

Expert Hour #3 (2026-08-10, `0470e50f9`) measured it and declined to fix it on sight, because the fix
moves a published number on three pairs. The W2_11↔D5 triad's belief headline was a total-variation
distance between two **population** severity distributions, so it could not see which account held
which belief:

| | per-case agreement | published belief gap |
|---|---|---|
| the real company | 0.9300 | 0.0700 |
| every belief permuted | 0.6333 | **0.0700** |

The degenerate that scored exactly what the real company scored was *"get the population MIX right and
every INDIVIDUAL wrong"* — a collections report whose portfolio risk mix matches the auditor's while
naming the wrong customers in every bucket.

## What landed

`background.gap_metric.belief_measures` — the D11 shape, applied to an ordinal scale:

```
undercall_rate = |{belief < truth}| / |{truth > bottom of scale}|
overcall_rate  = |{belief > truth}| / |{truth < top of scale}|
gap (headline) = (undercall_rate + overcall_rate) / 2      # g0 = 0.5
```

**Each denominator is the population on which that error is POSSIBLE** (D7's rule). An account already
at the bottom of the scale cannot be under-called; counting it would move the rate with the shape of
the book rather than the company's judgement — the prevalence dependence D6 measured and D7 removed one
dimension over. `order` is a **required argument**, never inferred from the labels a run produced: an
inferred scale would let a run where nobody reached the top silently redefine what over-calling means.

### Measured, 600 customers, seeds 7 / 11 / 23

| seed | headline (was → is) | undercall | overcall | permuted degenerate |
|---|---|---|---|---|
| 7 | 0.0700 → **0.1338** | 0.2675 (42/157) | 0.0000 (0/564) | 0.1338 → **0.5007** |
| 11 | 0.1033 → **0.1950** | 0.3899 (62/159) | 0.0000 (0/575) | 0.1950 → **0.4934** |
| 23 | 0.0733 → **0.1325** | 0.2651 (44/166) | 0.0000 (0/566) | 0.1325 → **0.5003** |

The headline roughly doubles because the denominator is the ~26% of accounts that *could* be
under-called, not the whole book. The degenerate now lands on the no-skill baseline **0.5** instead of
the real company's own number — that is the acceptance criterion the atom wrote for itself, met and
measured. Calling every account `normal` and calling every account `high` both score 0.5 too.

### The TV figure is renamed, not deleted

It is published as its own dimension, `belief_population_mix`. "Does the company have the right MIX?"
is a real question — a credit committee reads exactly that. What was wrong was publishing it under a
name that reads as a per-case error rate, which on a one-directional book it even numerically *equals*.
Keeping it also keeps `AGGREGATE_SCORING_CONTRACT` **differential**: after the reshape every other
dimension is per-case, and a register whose entries all land on one side is a blanket rule wearing a
register's clothes. It carries its own `as_of` declaration rather than inheriting `belief`'s — a
dimension that shares another's inputs is exactly the one an author assumes is covered.

## One direction reads 0.0000, and is proven able to fire

This company only ever under-calls, so `overcall_rate` is `0.0` on every seed — over a **non-empty**
denominator of 564/575/566 accounts, which is the difference between a measurement and vacuity. That is
the shape that lets a dead measure pass for a clean one (D11's `missed_failure_rate` is the same shape
one dimension over). It is declared as a property of the population, never banked as precision, and
mutation-proven: escalate one account a step it did not earn and the rate moves and the headline
worsens. Where a direction's *population* is empty the rate is `None` and the headline is `None` —
never `0.0`, never the surviving direction alone.

## R15, mutating the SOURCE

- Revert `score_triad`'s headline to `belief_gap` → **5 tests fire**, including the acceptance criterion
  (`test_the_belief_headline_moves_under_a_permutation_since_d19`).
- The existing lying-declaration mutation now covers four dimensions, including the new one.
- Both mutated files were restored and verified byte-identical by checksum.

### A fail-silent hole closed on the way

`_rendered_dimension_text` — the helper the D16 phrase sweep runs over, whose whole purpose is that no
phrase reaches a reader from a dimension nobody compared — was a **hand-maintained** map of published
dimensions. A newly published dimension simply would not appear in it, so the sweep would skip it and
still pass. The set is now **derived** from the scored result and asserted against it. Proven by
deleting a dimension from the map: **3 tests fire**.

## Open and registered, not fixed here (SELF_INTERRUPT_DISCIPLINE)

The D8 remittance counterfactual's `_ATTRIBUTED_MEASURES` covers ageing and detection components only.
Before this reshape the belief dimension had no per-case direction rate to attribute; it does now, and
none of them is attributed — so this instrument's ledger note explains less of itself than it appears
to. That is a D8 question and this build declined to answer it on its owner's behalf.

## Tests

76 in `tests/tools/test_couple_w2_11_d5.py` (9 new); **696 green** across every file touching
`gap_metric` and the three pairs that call `belief_gap` (`test_couple_w2_11_d5`, `test_gap_metric`,
`test_live_payment_triad`, `test_couple_w2_4_c6`, `test_couple_cohort`, and the four other coupled
pairs). Ledger: `LEVEL_UP_SELF_CERTIFIED` D19 → 2 in `docs/observability/gate_authorizations.jsonl`.

## Why H27 is still at L2

The draw was H27 2→3. It is not taken, and this tick has the least right of any to take it: **this is
the tick that changed the instrument**, which is the reputation-of-the-old-instrument problem in its
purest form and the reason every previous release gave. No `depends_on` is added and none is needed —
there is no unbuilt blocker to aim one at, and pointing a block at a satisfied atom is the
dead-mechanism class H27's note has already fallen into twice. **The next HARDEN draw of H27 is Expert
Hour #4**, on the corrected instrument, and it should start where this build declined to go:

1. Two of this instrument's four dimensions now publish a **structurally-zero error direction**
   (detection's `missed_failure_rate`, belief's `overcall_rate`). Each is honestly declared and
   mutation-proven able to fire, and each makes its balanced headline half a measurement. Whether that
   is acceptable at L3 is one judgement, now owed on two dimensions at once.
2. The unattributed belief directions above.
