<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED] — cross-generator invariant: payment_channel ⇔ dd_failed consistency (2026-07-28)

**finding_key:** `coldwalk:payment_channel_dd_fail_contradiction` (adjudicated-real, ledger 2026-07-12).

**Source:** `docs/design/SANITY_FINDING_COVERAGE_MAP.md` row 7. This finding was *listed* in the P2 mint
file's "known-covered" block (→ payment grid SOURCE 1+2), but the audit's **LAW-C independent read
rejected the name-match**: the payment grid SENSES aggregate collection gaps (regime detection +
expected-collection reconciliation, "SENSING ONLY"); it does **not** enforce the per-customer
cross-generator invariant this finding names. `grep` for any channel↔dd-fail consistency check returns
empty. So the honest verdict is `uncovered` → MINT. (This is exactly the audit's purpose: catch a
name-match that isn't a mechanism-match — §3 no-silent-closure.)

**Provenance:** RUNG-7 planner mint (defect fix = `mint`-direction, GAP2 §2, autonomous).

**The defect (root-caused in the finding's own evidence).** `site/data/customer_sample.json` C1g has
`payment_channel="standard_credit"` yet `dd_fail_rate=0.0667` with `dd_failed` counts across multiple
years — a standard-credit customer *cannot* have a Direct-Debit failure. Root cause: `payment_channel` is a
static per-customer classification from `simulation.household_segments.payment_channel_for_customer()`
(via `tools/generate_customer_sample.py`), while `dd_failed`/method labels come from
`simulation.arrears_engine.payment_method()/payment_outcome()` (via `tools/generate_billing_ledger.py`) —
two independently-dispatched generators never cross-referenced at build time. Same recurring "two
duplicated registers never reconciled" class as the M2 payments audit.

**Serves:** DIRECTOR_AXES v1 **#2 Segmentation/customer truth** + **#3 Believability** (a COO reading a
standard-credit account with DD failures fails the 20-year-veteran smell test), and the coupled-triad law
"the gap is the score" (an unmeasured cross-generator inconsistency masquerading as handled).

**Fidelity gained (one sentence):** a customer's payment channel and its arrears-engine payment events can
no longer contradict each other — the two generators are reconciled at the source, closing the whole
class, not this one customer.

## Exit criteria (falsifiable, R11 + R15, R10 class closure)
- **DISCOVER (self-drawable now):** map the two generators' outputs; enumerate every customer whose
  `payment_channel` is inconsistent with its arrears-engine event stream (bound the class size, not just C1g).
- **BUILD (gated):** a **class invariant** (R10 — not a C1g instance patch): a non-DD `payment_channel`
  ⇒ zero `dd_failed`/DD-method events for that customer, enforced where the ledger/sample is generated.
  R15 both-ways — (a) inject a standard-credit customer carrying a `dd_failed` event → the invariant FIRES;
  (b) a genuinely DD customer with a DD failure PASSES (no fail-open, no over-block of legitimate DD arrears).
- **R12:** the count of inconsistent customers is a diagnostic, never a target; no customer reclassified to
  shrink it.

## Lane / rank / walls
- **Lane:** `simulation` generators + a consistency check (`saas`/`company` compliance). **DISCOVER
  self-drawable now; BUILD blocked_on the relevant front/level (director_level_up, R16 — no self-bump).**
- **Rank:** among product-lane atoms per ratified GAP2; PRODUCT-FIRST guard applies.
- **Walls:** R13 untouched. C-S2 RNG-substream discipline — the reconciliation must draw from its own named
  seeded substream, not shift another subsystem's outputs.
