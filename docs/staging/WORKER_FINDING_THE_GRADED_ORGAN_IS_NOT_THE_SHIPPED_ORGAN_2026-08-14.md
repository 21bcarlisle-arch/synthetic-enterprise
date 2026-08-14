# [WORKER-FINDING] The graded organ is not the shipped organ — the harness builds the company with 4.4× its own production memory, and that is what puts both belief figures off scale (2026-08-14)

**Severity:** LATENT · **Lane:** D_billing_metering · **Status:** measured, not repaired — the
repair is atom `D30_the_belief_band_is_this_books_length`'s own reshape and BUILD is gated on it
(`loop_stage: idle`). Full frame:
`docs/design/simplifications/D30_the_belief_band_is_this_books_length.yaml`.

Found on a DISCOVER/FRAME draw of D30 (worker tick, LANE 3), not fixed on sight
(SELF-INTERRUPT DISCIPLINE).

## The measurement, `observed-with-evidence`

Detached worktree at HEAD `401fa828e`; n=300, seeds 7/11/23; shipped `build_scenario` /
`score_triad`; company memory perturbed through the declared `organ_failure_window_drift_days`
parameter, never a monkeypatch.

```
company/billing/payment_observation_consumer.py:386   dd_failure_window_days: int = 90
tools/couple_w2_11_d5.py                              DD_FAILURE_WINDOW_DAYS = 400
                                                      -> PaymentObservationConsumer(
                                                           dd_failure_window_days=400 + k)
```

The two BELIEF dimensions read exactly one company parameter, and the harness constructs it at
**4.4× the value the company itself ships**. Scored on the **shipped** book at W around the
organ's own default:

| seed | saturated at W=90 | headroom | distinct `belief` over W=85..95 | distinct `mix` |
|---|---|---|---|---|
| 7 | False | −1 | 4 | 4 |
| 11 | False | −2 | 3 | 3 |
| 23 | False | −2 | 7 | 4 |

Every value differs at 4dp, so they survive D34's reader-precision floor. **The instrument that
"cannot resolve the company it scores" already resolves the company it ships** — same book, no
reshape, all three seeds.

Blast radius of restoring the shipped default, measured (shipped book, W 400 → 90):

| dimension | moved? |
|---|---|
| `belief` | MOVED 3/3 |
| `belief_population_mix` | MOVED 2/3 — seed 23 bit-identical, seed 11 by 1.4e-17 only (D33's predicate), so **1 of 3** at the precision a reader gets |
| `ageing`, `detection`, `detection_latency` | bit-identical 3/3 |

## Why it is not a fix on sight

The 400 is deliberate and its reason is still in the constant's comment: generous on purpose, so
the belief's own recency-decay window does not confound the CHANNEL blind spot this scenario
exists to measure (atom D27 owns it). But the parameter it holds inert **is the only parameter
these two dimensions read** — `_arrears_risk_belief` counts observed failures inside that window
and reads no dating at all. On this pair, confounder-removal and resolution are the same mechanism
seen from two sides: the isolation was bought by publishing the figure at a setting where the
thing it isolates cannot move. Restoring the shipped default buys resolution and re-admits the
confound in the same edit.

**Recommendation (taken forward into D30's frame, not asked bare):** publish **both** companies —
the channel-isolated reading (W=400, declared saturated and labelled as such) and the
shipped-company reading — rather than choosing between them. Two scorings of one book: no world
change, and no re-derivation of any other dimension's declared band.

## What this corrects in the record

- D30's own `name` offers three reshapes and all three change the **book**. The cheapest candidate
  changes the **company back to the shipped one** and was never on the list.
- D30's `name` says the reshape "moves every published belief figure on this pair". True of the
  book candidate (which moves **five of five** published figures); false of the cheap one.
- `belief`'s own `own_why` in `DIMENSION_DRIFT_RESOLUTION` already records that the organ's
  shipped 90d default "sits just BELOW the edge, publishing a different number (0.1519 → 0.1709 at
  seed 7)". The fact was in the register; nobody asked what it made the 400. Hour #11's *a lead is
  not a control*, one register field over — ninth sighting in this module's line.

**R12:** no published number was tuned and none was written to any artefact. Every figure above was
scored inside a throwaway worktree to find out which of them each candidate reshape reaches.
