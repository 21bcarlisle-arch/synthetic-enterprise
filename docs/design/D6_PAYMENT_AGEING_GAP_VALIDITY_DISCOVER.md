# D6 — Is the payment AGEING gap real, or a metric artefact?

**Atom:** `D6_payment_ageing_gap_validity` (lane D_billing_metering, epoch 3, dial 3)
**Stage:** DISCOVER — closed 2026-08-08
**Couples with:** `H27_payment_belief_gap`, `W2_11_payment_behaviour_source`
**Question as filed:** the live coupled-triad reports an ageing gap of **1.1538** — above 1.0,
i.e. the company's debt-ageing belief scores *worse than the baseline the metric norms against*.
Genuine company failure mode, or metric-shape defect?

---

## VERDICT — **BOTH, and they must be separated**

1. **The number 1.1538 is a metric-shape defect. It is not evidence of anything and must not be
   cited as fidelity.** Proven three ways below against the *unchanged* criterion.
2. **Underneath it there IS a genuine, real-world-recognisable failure mode** — oldest-first
   (Clayton's Case) appropriation of unreferenced payments misdates debt while leaving the
   account *balance* exactly right. It is demonstrable **without** the broken metric, so it
   survives the metric's replacement.

The two are independent findings. Fixing the metric does not make the failure mode go away;
citing the metric does not evidence the failure mode.

A framing correction first: the atom (and the ledger note) describe the ageing dimension as
normed against a **"flag-nobody" baseline**. It is not. `misapplication_gap` norms against the
**majority-class** baseline — `g0 = mean(truth[i] != majority_class(truth))`. On this label
space the majority class happens to be `current`, which *looks* like flag-nobody but is a
**class-prevalence quantity**, and that is the whole problem. "Flag nobody → gap = 1" is the
`detection_gap` baseline text, reused by eye on a metric that does not have that shape.

---

## Evidence A — the criterion on trial with an oracle

Known-good and known-bad ageing beliefs, run through the **unchanged**
`background.gap_metric.misapplication_gap` exactly as `tools/couple_w2_11_d5.score_triad` calls
it. The right answer for each row is known *independently of the metric*. Reproduce with
`PYTHONPATH=. python3 tools/d6_ageing_metric_oracle.py`.

| Case | Company behaviour | Independently | **GAP** |
|---|---|---|---|
| A | perfect ageing (0 miss, 0 false positive) | best possible → 0 | 0.0000 ✅ |
| B | the no-skill baseline itself (call everything current) | exactly 1 | 1.0000 ✅ |
| C | **finds 100% of real arrears**, 1.5% false-positive rate | strictly better than B | **1.5000 ❌** |
| E | off by ONE bucket on every overdue invoice | much better than B | 1.0000 ❌ |
| E' | totally blind on every overdue invoice | = B | 1.0000 ❌ |

**Defect 1 — above-1 does not mean "worse than no-skill" (row C).** A company that finds *every*
real arrears case with a 1.5% false-positive rate scores 1.50 — nominally worse than a company
that reports no arrears at all. No supplier, regulator or auditor would agree. The measured
1.1538 is in exactly this régime.

**Defect 2 — the score is dominated by class prevalence, not by the company (row D).** Hold the
company's behaviour *literally fixed* (same belief vector, same 15 false positives, all real
arrears found) and move only the arrears base rate:

| true arrears prevalence | 0.50% | 0.99% | 1.96% | 4.76% | 9.09% |
|---|---|---|---|---|---|
| **GAP** | **3.0000** | **1.5000** | **0.7500** | **0.3000** | **0.1500** |

A twentyfold swing from a property of the *world*, with the *company* unchanged. The number is
not a measurement of the company. This alone disqualifies it as a fidelity statement.

**Defect 3 — ordinal blindness (rows E vs E').** The buckets `current < 30-60 < 60-90 < 90+` are
**ordered**; Hamming error rate is not. Believing a 90+ debt is 60-90 scores identically to not
seeing it at all. This is the "detection-style normalisation misapplied to a bucket-distance
dimension" the atom hypothesised — and it is confirmed *as a property of the metric*, though see
the honest caveat under Evidence B: in the live-path populations probed, adjacent-bucket errors
numbered **zero**, so Defect 3 is currently latent rather than active. Defects 1 and 2 are active.

## Evidence B — the live code path, decomposed

`background.live_payment_triad.LivePaymentTriad` (the LIVE module, not a re-implementation) run
over synthetic multi-year populations, scored by the same `score_triad`, with the truth/belief
label pairs re-derived and given provenance. 60 customers × 24 monthly periods, resi:

```
n=1440  n_wrong=58  n_truly_overdue=205   gap=0.2829
  MISSES        (truly overdue, believed current):  19
  FALSE AGEING  (truly current,  believed overdue): 39
  WRONG BUCKET  (both overdue, different bucket):    0   <- Defect 3 latent, not active
  misses by payment method: card 10, prepayment 8, standing_order 1, direct_debit 0
  false ageing by true result: success 42/42
```

Two things fall straight out:

* **Every miss is non-DD. Zero of 19 land on Direct Debit.** DD payments carry
  `correlation_id == invoice_ref` (remittance-directed) and settle their own invoice; non-DD
  payments cross the seam with the correlation id **stripped to `None`**, forcing
  `AccountLedger.allocate`'s oldest-first fallback. That is the mechanism, isolated.
* **Every false ageing is on an invoice that was truly paid.** Not noise — the mirror image of
  the same misallocation.

## Evidence C — the genuine failure mode, shown without the metric

Account `ACC-D6C0038`, prepayment (unreferenced credits), 24 monthly bills of £95:

* Truth: successes and failures **scattered** across the 24 periods.
* Company belief: the **12 oldest** invoices settled, the **12 newest** open — 10 at `90+`, one
  at `60-90`, one at `30-60`.
* Company balance: `balance_gbp = 1140.00`, `open_sum = 1140.00`, `total_outstanding_gbp = 1140.00`,
  `unallocated_credit_gbp = 0.00`.

**The money is exactly right and the dates are exactly wrong.** That is Clayton's Case as a real
supplier meets it: unreferenced cash appropriated to the oldest debt produces a correct ledger
balance and a materially misdated ageing report — which is what drives wrongful dunning, wrong
statutory-interest accrual, and misstated bad-debt provisioning. A real supplier *would*
recognise this, so it belongs in the gap; it simply cannot be reported by the current metric.

**A hypothesis I ran and refuted, recorded so it is not re-run:** I suspected the open-item view
over-stated arrears relative to the account's own balance (an internal D5 inconsistency). A
population check said 44/60 accounts diverged — but the checker read a **dict** with `getattr`,
so its "outstanding" was silently 0.0 on every account: a fail-open control of exactly the R15
kind, in my own probe. Corrected (dict access + a vacuity guard on non-zero balances), the answer
is **0/60 diverge**. There is no ledger inconsistency. The claim is withdrawn.

Also refuted en route, each by measurement rather than argument: a day-origin mismatch between
the two sides (both age from `issue_date + payment_terms_days` — aligned); variable invoice
amounts as the driver (gap 0.2829 → 0.2976, not the cause); failure base rate alone within the
live path (0.35–0.57 across stress mixes, never above 1). The exact live population composition
that yields 1.1538 was **not** reproduced — see Limits.

---

## What must change

**Do not report a single "ageing gap".** The dimension has two error directions with opposite
real-world consequences, and collapsing them into one prevalence-normalised scalar is what
produced an uninterpretable number. Report instead:

1. `understated_arrears_rate = misses / n_truly_overdue` — debt the company believes settled.
   Scale-free, denominator is the population it is about.
2. `overstated_arrears_rate = false_ageings / n_truly_current` — the **wrongful-dunning
   exposure**. This is the one the current metric hides inside a ratio normed on the *other*
   class.
3. `mean_bucket_displacement` among truly-overdue invoices — an **ordinal** severity that
   distinguishes off-by-one from blind. Reported **absolute**, NOT as a ratio to a no-skill
   baseline.

**A trap in (3), caught by mutation-testing this very doc's proposal — do not walk into it.**
My first draft of (3) was `mean_bucket_displacement / no-skill mean_bucket_displacement`. That
ratio **inherits Defect 2 exactly**: the no-skill displacement is itself a prevalence quantity,
so with the company held fixed it reproduces the same twentyfold swing (3.0000, 1.5000, 0.7500,
0.3000, 0.1500 — identical to the Hamming column). Measured, company literally unchanged:

| arrears prevalence | 0.50% | 0.99% | 1.96% | 4.76% | 9.09% |
|---|---|---|---|---|---|
| ordinal ÷ no-skill (**rejected**) | 3.0000 | 1.5000 | 0.7500 | 0.3000 | 0.1500 |
| `overstated_arrears_rate` ✅ | 0.0150 | 0.0150 | 0.0150 | 0.0150 | 0.0150 |
| `understated_arrears_rate` ✅ | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `mean_bucket_displacement` ✅ | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

**Any normaliser whose denominator counts the truth's class balance re-imports Defect 2**,
whatever the numerator's shape. The rule for D7_ageing_gap_metric_reshape: each measure's denominator must be the
population that measure is *about*, and the ordinal severity carries no denominator at all.

The headline for a *dating* dimension should be **date displacement of debt**, not a
classification error rate. Per R12 all three stay diagnostics, never targets.

Immediate honesty action taken now (not deferred): the published note in
`background/live_payment_triad.py` — which reaches `docs/observability/coupled_gap_ledger.json`
and from there `site/data/proof.json`, a live public surface — now labels the ageing figure
NOT-EVIDENCE and points here. The figure is not deleted (it is a real output of a real run); it
is disclaimed, which is what R14/R11 require of a published number whose basis has been refuted.

## Limits of this DISCOVER — read before building on it

* **The live 1.1538 was not reproduced.** From `n_wrong / n_non_majority = 45/39` the live
  population is inferable (39 truly-overdue invoices, 45 bucket errors, consistent with the
  ledger's own `truth_size = 39`), but the run's customer/term composition was not reconstructed.
  The oracle results are exact and population-independent, so the verdict does not rest on the
  reproduction — but nobody should claim the live figure has been explained *in detail*.
* Defect 3 (ordinal blindness) is proven as a metric property and observed **inactive** in every
  population probed. It should be fixed on shape grounds, not because it is currently biting.
* This doc is a **hypothesis until its build lands** — the project's DISCOVER docs have been
  wrong before. The falsifier is committed alongside it:
  `tests/tools/test_d6_ageing_metric_shape.py` pins Defects 1–3 as **characterization** tests of
  the current metric, so they fail loudly when the metric is replaced (which is the point).
* **R15 — the characterization tests were mutation-proven to fire, both ways.** Under a
  prevalence-safe reshape (`gap = overstated_arrears_rate`) 4 of 5 fail, including all three
  defect tests; under an ordinal-but-still-prevalence-normalised reshape only the Defect 3 test
  fails — which is how the trap above was caught. The 5th test (`..._still_routes_through_this_metric`)
  correctly stays green in both: `score_triad` is untouched by a mutation of the metric alone.

---

## D7 LANDED — 2026-08-08 (this doc is no longer a hypothesis)

`background.gap_metric.ageing_gap` replaced the ageing dimension in `score_triad`.
`misapplication_gap` is UNCHANGED and still scores W2_9↔C11; only the ageing caller left.

The same oracle rows, both criteria (`PYTHONPATH=. python3 tools/d6_ageing_metric_oracle.py`
now prints the old table above the new one):

| Case | retired scalar | understated | overstated | displacement |
|---|---|---|---|---|
| A perfect | 0.0000 ✅ | 0.0000 | 0.0000 | 0.0000 |
| B no-skill | 1.0000 ✅ | 1.0000 | 0.0000 | 3.0000 |
| C finds all, 1.5% FP | **1.5000 ❌** | 0.0000 | 0.0150 | 0.0000 |
| E off by ONE bucket | **1.0000 ❌** | 0.0000 | 0.0000 | **1.0000** |
| E' totally blind | 1.0000 | 1.0000 | 0.0000 | **3.0000** |
| D prevalence 0.50%→9.09%, company FIXED | **3.00→0.15 ❌** | 0.0000 flat | 0.0150 flat | 0.0000 flat |

All three defects answered: C now beats B on every axis it is better on and pays for its false
alarms only on the axis they belong to (D1); the sweep is exactly flat (D2); off-by-one is 1
bucket and blind is 3 (D3).

**On the live population** (`tools/couple_w2_11_d5.py --customers 400 --seed 7`): the retired
scalar reads **0.8043** on this population; the reshape reads **understated 0.0725** (10 misses
of 138 truly-overdue), **overstated 0.0951** (101 false ageings of 1062 truly-current),
**displacement 0.123 buckets**. The decomposition immediately says something the scalar could
not: this company's *wrongful-dunning* exposure is larger than its miss rate — 101 truly-settled
invoices believed in arrears against 10 real arrears believed settled. That is the direction a
real supplier gets complained about and fined for, and the old single number had it buried
inside a denominator normed on the other class.

**R15, four mutants, `tests/tools/test_d7_ageing_measures.py`.** Each property is asserted
against the real measures AND against a named mutant that breaks exactly it, with the assertion
*required* to fail on the mutant: `_MUTANT_ordinal_over_no_skill` (the trap this doc caught in
its own draft), `_MUTANT_displacement_over_whole_population` (milder same mistake — denominator
is n), `_MUTANT_understated_over_population` (`misses/n`), `_MUTANT_hamming_not_ordinal`
(Defect 3 restored). Plus fail-loud on an unrankable bucket label, and vacuity reported as
`None` rather than 0.0 when a population has no truly-overdue invoices.

**Not claimed.** The live 1.1538 is still not reproduced in detail (see Limits above) — the
reshape did not need it and does not explain it. Defect 3 remains latent in live populations
(`wrong_bucket == 0` on the 400-customer run): it is fixed on shape grounds, and the
displacement measure now *would* show it if it started.

## Follow-on work

* ~~`D7_ageing_gap_metric_reshape` (BUILD)~~ — **DONE 2026-08-08**, see above.
* **Open, unbuilt:** whether W2_9↔C11 should also leave `misapplication_gap`. The ordered-space
  fix does NOT transfer — obligation classes are unordered, so there is no displacement to
  report there. Defects 1 and 2 still apply to that pair and are carried openly by the stamped
  caveat; that is a real remaining exposure, not a closed one.
* `D8_ambiguous_remittance_misdating` (BUILD, couples W2_11 ↔ D5) — report the Clayton's-Case
  date displacement as the company-failure finding in its own right, once D7_ageing_gap_metric_reshape gives it a shape.

Both are minted rather than fixed on sight, per SELF-INTERRUPT DISCIPLINE: the machine is not
blocked, and the metric replacement is a design change that deserves its own build, not a patch
appended to a DISCOVER.
