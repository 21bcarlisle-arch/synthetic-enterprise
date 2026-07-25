# Payment-failure detection — narrow sensing carve-out BUILD (2026-07-25)

Actions the director ruling `DIRECTOR_RULING_PAYMENT_DETECTION_CARVE_OUT_2026-07-25.md`
(§2) authorized: build the expected-collection reconciliation detector, sensing only.
Built this worker tick.

## What was built (§2, IN SCOPE)

**`company/billing/payment_observation_consumer.py`**
- `ExpectedCollectionMiss` dataclass + `expected_collection_misses(account_id, as_of,
  grace_days, ...)` + `PaymentBeliefSnapshot.detected_collection_misses`.
- Mechanism: reconcile the company's OWN issued bills (`BILL_DEBIT`) against its OWN
  observed cash (`PAYMENT_CREDIT`), via the existing `arrears_engine.age_open_items`.
  An invoice `grace_days` past due with a positive outstanding balance is a **detected
  missed collection** — the through-the-wall way a real supplier notices a missed
  *customer-initiated push payment* (standing order / card / prepayment) that emits **no
  rail failure event at all**. Reads no `PaymentEvent`/generator internal — epistemic
  verifier PASS.
- **Sensing only**: deliberately NOT wired into `arrears_risk_belief` or any action.

## Detection latency, not a permanent gap (§1)

The detector is silent within a `grace_days` (default 5) window and fires only past it —
so the residual is a **detection LATENCY**, registered with its measured distribution
(`stats["detection_latency_days"]` = n / min / median / max), never compressed to zero
(R12). DD failures remain observable fast (rail return); push-channel misses at due+grace.

## R15 both-ways (control can FAIL)

- **Fires**: `test_reconciliation_fires_and_narrows_the_detection_gap` — the reconciliation
  path strictly lowers the recall gap vs a DD-event-only belief on the same population.
- **Can still miss / can't fail-open**: `test_reconciliation_cannot_fail_open` — because
  the detection metric is pure **recall**, flagging every overdue invoice would drive the
  gap to zero by flagging everyone. The detector keys on the ledger's **actual outstanding
  cash**, so a paid-late invoice is NOT flagged; a cash-blind mutant (flag any overdue
  bill) is proven to wrongly flag it while the real detector does not.
- **Latency registered**: `test_detection_latency_is_registered_not_zero`.
- Witness split in the harness: `n_flagged_non_dd_failures` (a non-DD case reaching belief
  via the DD-failure-event channel = a **wall leak**) stays **0**;
  `n_flagged_non_dd_via_reconciliation` (the carve-out working) is **> 0**.

## Measured effect

Offline harness (`tools/couple_w2_11_d5`, 4000 customers, seed 0): detection gap
**0.278 → 0.095**. Live `live_payment_triad` + per-cell `detection_cell_measurements`
re-measure automatically on the next run (same `score_triad` scorer — no second metric).
Residual (never zero, R12): late-but-eventual payments (latency), ambiguous-remittance
mis-allocation (oldest-first), and partial payments.

## Explicitly NOT built — RESERVED (§3)

Dunning / collections actions, vulnerability/PSR flagging, SoLR machinery, arrears-driven
pricing, bad-debt provisioning method and write-off rules — all reserved to the director's
forthcoming dunning/debt/provisioning session. The detection organ is the substrate that
session designs on top of; building actions first would foreclose its choices.

Levels untouched (director-reserved). Change is additive and git-revertible.
