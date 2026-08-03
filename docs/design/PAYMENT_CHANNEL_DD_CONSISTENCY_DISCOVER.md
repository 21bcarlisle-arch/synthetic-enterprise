<!-- SUPERVISOR_DRAW: discover-output (design/enumeration only, no production code) -->
# DISCOVER — payment_channel ⇔ dd_failed cross-generator consistency

**finding_key:** `coldwalk:payment_channel_dd_fail_contradiction` (adjudicated-real).
**Mint:** `docs/staging/PLANNER_MINTED_payment_channel_dd_consistency_invariant_2026-07-28.md`.
**Status:** DISCOVER (self-drawable) DONE. BUILD blocked_on front/level (director_level_up, R16).
**Evidence base:** `site/data/customer_sample.json` (meta.generated_at 2026-07-28T09:18:46Z, 19 customers),
`docs/state/billing_ledger.json` (source run `run_output_c84d418ef_20260728T091009Z`, 1587 invoices, 19 customers).

---

## VERDICT + MEASURED CLASS SIZE (top-line)

**Measured inconsistency class = 5 customers** (union across both surfaces): **C1g, C4, C5, C6, C8**,
carrying **12 arrears cases** whose stage stream contains a `DD_FAILED` / "Direct debit returned"
event on a **non-Direct-Debit** payment method. Not just C1g.

**The mint's stated mechanism is WRONG in one important respect, and the real defect is worse.** The two
surfaces do **not** disagree on the channel. Both `tools/generate_customer_sample.py:174`
(`payment_channel_for_customer(cid, _commodity)`) and, via `arrears_engine.payment_method`, the ledger at
`tools/generate_billing_ledger.py:185` call the **same** deterministic function on the **same** key
`(cid, commodity)` — so they AGREE that C1g is `standard_credit`. The contradiction is **internal to the
outcome model**: `simulation/arrears_engine.py::payment_outcome()` (line 249) has **no non-DD branch** — every
non-corporate method (standard_credit, prepayment, standing_order, card) is run through the identical
DD-failure probability model, and `arrears_stages()` (line 268) hardcodes a `"DD_FAILED"` stage with the note
`"Direct debit returned"`. So a `standard_credit` customer draws a "DD failure" it physically cannot have.
`payment_behaviour_source.py` says this out loud (lines 278-285): *"every non-corporate method maps to the same
core 'direct_debit'-style outcome tier; only the METHOD LABEL varies."*

This is therefore an R10 **single-generator category error**, not a two-generator join failure — which is
exactly why an R10 **class invariant** (not a C1g instance patch) is the right fix: the label is decorative,
the mechanic is wrong for the whole non-DD population.

**One-line view (invariant vs time-varying-state):** the **consistency invariant IS the correct first BUILD
step** — it is a WALL that must hold under the current static model AND under any future time-varying-channel
model; the time-varying-state change the 2026-07-13 FRAME wants is a real but SEPARATE, larger, director-gated
fidelity build that the invariant guards rather than replaces. See §5.

---

## §1 — The two (actually three) generators mapped

| # | Surface | Field | Generator | Key | Cross-refs the other? |
|---|---------|-------|-----------|-----|----------------------|
| A | `customer_sample.json` | `payment_channel` (`direct_debit`/`standard_credit`) | `simulation/household_segments.py::payment_channel_for_customer()` L154-162 | `random.Random(f"paychannel_{cid}_{fuel}")`, threshold `DIRECT_DEBIT_SHARE_BY_FUEL` (elec 0.72 / gas 0.75) | — pure hash, no arrears input |
| A' | `customer_sample.json` | `payment_miss_trajectory[].dd_failed`, `payment_behaviour_analytics.metrics.dd_fail_rate` | `run_phase2b` per_customer_behavioral → `simulation/payment_behaviour_source.py::generate_payment_event()` L259-330, which WRAPS `arrears_engine.payment_outcome` | own `_period_substream`, `core_method = "direct_debit"` for all non-corp (L288) | **NO** — method label discarded for outcome |
| B | `billing_ledger.json` | `payments[].method` + `.outcome`, `arrears_history[].stages[].stage` | `tools/generate_billing_ledger.py::generate()` → `arrears_engine.payment_method`/`payment_outcome`/`arrears_stages` | shared `random.Random(42)` over sorted bills | **NO** — `payment_outcome` L249 branches only bacs/chaps vs else |

**Signatures (quoted):**
- `payment_channel_for_customer(customer_id: str, fuel: str = "electricity") -> PaymentChannel` — returns
  `DIRECT_DEBIT` if `rng.random() < share` else `STANDARD_CREDIT`. Pure per-customer hash; **no mechanism to
  ever change** (household_segments.py docstring calls every archetype "stable for the account's whole tenure").
- `payment_method(segment, amount_gbp, customer_id=None, fuel="electricity") -> str` (L162) — corp → bacs/chaps;
  `segment == "sme"` → bacs; else `payment_channel_for_customer(cid, fuel).value`.
- `payment_outcome(method, stress, rng, segment="resi", ...) ` (L214) — **only** `method in ("bacs","chaps")`
  is branched (L239); **all else** (L249+) runs the DD-failure model and can `return ("failed", 0)`.
- `arrears_stages(...)` (L265) — first stage is unconditionally
  `{"stage": "DD_FAILED", ... "note": "Direct debit returned"}`.

**Confirmed no cross-reference / no existing invariant:** `grep -rn` for any channel↔DD-fail consistency check
across `company/`, `saas/`, `tools/`, `simulation/` returns empty. The one nearby control,
`company/compliance/population_sanity.py::check_payment_channel_mix()` (L170), is **aggregate-only** (it senses
the DD *share* vs the DESNZ band) and **fail-open on empty** (`if not payments: return []`) — it cannot and does
not enforce the per-customer invariant, matching the audit's LAW-C rejection of the "known-covered" name-match.

---

## §2 — "non-DD" vs "DD" enumeration (from code)

- `simulation/household_segments.py::PaymentChannel` (L126): exactly two values — `DIRECT_DEBIT="direct_debit"`,
  `STANDARD_CREDIT="standard_credit"`. This is the vocabulary that reaches `customer_sample.payment_channel`.
- `simulation/payment_behaviour_source.py` method labels (L179-192): `direct_debit`, `standard_credit`,
  `standing_order`, `card`, `prepayment` (the latter three are the finer non-DD split).
- Corporate methods: `bacs`, `chaps` (I&C / SME).

**DD set = `{direct_debit}` — the ONLY method for which a `DD_FAILED` / "Direct debit returned" event is real.**
**Non-DD set = `{standard_credit, prepayment, standing_order, card, bacs, chaps}`.** Note bacs/chaps already have
a *dispute* failure path (`INVOICE_DISPUTED`, not `DD_FAILED`), so in practice today's offenders are the
`standard_credit`/`prepayment`/... family routed through the DD outcome model. `prepayment` is the most absurd
case — it has no "returned" event at all (self-disconnect / non-vend); household_segments.py L145-147 already
flags this as backlog.

---

## §3 — Enumerated inconsistency table (real data, cite-able)

**A. `billing_ledger.json` — non-DD method carrying `outcome="failed"` → a `DD_FAILED` arrears stage:**

| customer | ledger segment | method | failed count | DD_FAILED arrears cases |
|----------|---------------|--------|--------------|-------------------------|
| C1g | resi | standard_credit | 1 | ARR-C1g-2017-05-31 |
| C4  | resi | standard_credit | 5 | ARR-C4-2018-05-31, -2018-12-31, -2019-04-30, -2019-05-31, -2023-05-31 |
| C5  | **SME** | standard_credit | 2 | ARR-C5-2017-11-30, -2019-03-31 |
| C6  | **SME** | standard_credit | 1 | ARR-C6-2022-07-31 |
| C8  | resi | standard_credit | 3 | ARR-C8-2019-09-30, -2019-10-31, -2024-11-30 |

**Ledger class = 5 customers, 12 arrears cases.**

**B. `customer_sample.json` — `payment_channel="standard_credit"` carrying `dd_failed>0`:**

| customer | channel | Σ dd_failed (payment_miss_trajectory) | dd_fail_rate |
|----------|---------|---------------------------------------|--------------|
| C1g | standard_credit | 2 (2016, 2017) | 0.0333 |
| C4  | standard_credit | 4 | 0.0417 |
| C8  | standard_credit | 3 | 0.0270 |

**Sample class = 3 customers** (C5/C6 are SME → `payment_channel=None` on the sample surface and carry no
resi behavioural trajectory, so they only surface in the ledger).

**Union class = 5: {C1g, C4, C5, C6, C8}.**

**Join note.** Both files key on the same `account_id` (`C1`, `C1g`, `C4`, …); no fuzzy join needed. Inconsistency
is established *within* a single record: (channel or method) is non-DD **AND** a DD-specific artefact
(`DD_FAILED` stage / "Direct debit returned" note / `dd_failed` count / `dd_failure_reason`) is present on the
same customer.

**Two honest caveats (R12 / non-fabrication):**
1. The mint cited C1g `dd_fail_rate=0.0667`; the **current** data shows **0.0333** — the run was regenerated
   (RNG re-drew), so the exact rate drifts run-to-run. The *class* is stable in kind; this run-to-run drift is
   itself the argument for an R10 class invariant over any instance figure.
2. **A distinct second defect surfaced and widens the class: SME case-sensitivity.** `payment_method` (L175)
   tests `segment == "sme"` but bills store the segment as `"SME"` (uppercase) — verified live:
   `payment_method("SME", 500, "C5", "electricity") == "standard_credit"` while `payment_method("sme", …) == "bacs"`.
   So C5/C6 (SME) are mis-routed through the **resi** channel model and then through the DD-failure model,
   producing `standard_credit` + `DD_FAILED` for an I&C-class account (doubly wrong — an SME should be
   BACS/CHAPS with an `INVOICE_DISPUTED` path). This is a separate bug, but the proposed invariant would CATCH
   it (SME carrying `DD_FAILED`), which is a desirable property, not scope creep.

Live confirmation that the reason field is also mislabelled: `generate_payment_event(..., 'standard_credit', …)`
and `(..., 'prepayment', …)` both return `dd_failure_reason = insufficient_funds` on a failed draw — a
DD-specific reason stamped on a non-DD method.

---

## §4 — BUILD sketch (design only) + R15 shape

### 4a. The R10 class invariant (the check)
A per-record consistency invariant, method-symmetric across both surfaces:

> **INV-PCDD:** for any payment/arrears record, `method != "direct_debit"` (equivalently
> `payment_channel != "direct_debit"`) ⇒ that customer carries **zero** DD-specific artefacts:
> no `arrears stage == "DD_FAILED"`, no `note == "Direct debit returned"`, no non-null `dd_failure_reason`,
> and (sample surface) `payment_miss_trajectory[].dd_failed == 0` / `dd_fail_rate == 0`.

**Home:** a new `check_payment_channel_dd_consistency(payments, arrears)` sibling to `check_payment_channel_mix`
in `company/compliance/population_sanity.py`, wired into `run_all_population_checks`; **plus** a generate-time
guard in `tools/generate_billing_ledger.py`/`generate_customer_sample.py` so a violating record cannot be
published (R10 "whole class fails automatically", not an instance patch). The check must be **per-record and
fail-CLOSED**: distinguish "no records supplied" (skip) from "records present, zero violations" (pass) — do not
let an empty/`None` method silently count as DD (the fail-open trap `check_payment_channel_mix` sits in).

### 4b. The data remediation (so genuine data passes the invariant)
The check alone would just RED every run; the paired fix is to branch the outcome/stage vocabulary by method:
- `payment_outcome()` / `arrears_stages()`: a **non-DD** failure emits a method-appropriate stage, e.g.
  `standard_credit` → `"PAYMENT_MISSED"` / note "Standard credit payment not received"; `DD_FAILED` /
  "Direct debit returned" / `dd_failure_reason` reserved for `direct_debit` only.
- Fix the SME case-normalisation in `payment_method` (`segment.lower()` before the `sme`/`ic` tests) so I&C/SME
  never route through the resi channel model.
- `prepayment`'s genuinely different mechanic (no returned event; self-disconnect / emergency credit) stays
  **registered backlog** (household_segments.py L145-147 already flags it) — the invariant simply forces that
  backlog to be honest by flagging any `prepayment` + `DD_FAILED`.

### 4c. C-S2 RNG-substream discipline
The consistency CHECK is pure/deterministic (no RNG — it reads existing records). Any remediation draw (e.g. a
method-appropriate reason split for a standard-credit miss) MUST use its **own named seeded substream**
(e.g. `random.Random(f"credit_fail_reason_{cid}_{period_index}")`), never advance `arrears_engine`'s shared
`random.Random(42)` — the exact pattern `payment_behaviour_source.py::_period_substream` already follows, so a
new draw cannot shift another customer's/subsystem's sequence.

### 4d. R15 both-ways test shape
- **(a) FIRES (defect present):** fixture customer with `method="standard_credit"` carrying an arrears case whose
  stages include `"DD_FAILED"` (and/or `dd_failed>0` / `dd_failure_reason` set) ⇒ the invariant returns a
  non-empty finding naming that customer. **Mutation:** delete/weaken the DD-specific artefact test ⇒ the fixture
  now passes ⇒ proves the control fires on its own named defect (not a tautology).
- **(b) PASSES (legitimate DD arrears):** `method="direct_debit"` customer with a real DD failure
  (`DD_FAILED` stage, `dd_failure_reason=insufficient_funds`) ⇒ empty findings. Plus an SME `bacs` →
  `INVOICE_DISPUTED` case, and a `standard_credit` customer with only success/late payments — all pass
  (no over-block of legitimate arrears).
- **Fail-open guards to assert:** empty payment list ⇒ skipped, never "clean-for-the-wrong-reason"; a
  `None`/missing/NaN method ⇒ NOT silently treated as DD (reject non-finite / unknown method explicitly, per the
  comparison-guards-are-NaN-blind family).

### 4e. R12 (anti-goal-seek)
The count (5 customers / 12 cases *this run*) is a **diagnostic**, never a target. Forbidden: reclassifying
C4/C8/C1g to `direct_debit`, or lowering `DIRECT_DEBIT_SHARE_BY_FUEL`, to shrink the number. The only sanctioned
fix is making non-DD failures method-correct; the population DD share is a separate R13 baseline decided blind
to this count.

---

## §5 — Reconciliation with the 2026-07-13 time-varying-state FRAME

The FRAME argued the *deeper* root cause is that `payment_channel_for_customer` is a **pure static hash with no
mechanism to ever change**, whereas in reality **failing payers drop OFF direct debit** (a supplier moves a
chronic DD-bouncer onto standard credit / prepayment), so the real fidelity fix is a **time-varying,
event-responsive** payment_channel state, not a data-join.

**Evidence-backed view: the invariant is the correct FIRST build step; the time-varying model is a distinct,
later, director-gated build that the invariant GUARDS rather than competes with. Reasons:**

1. **The finding is an INCORRECT mechanism; the FRAME is a MISSING mechanism.** My measurement shows the two
   surfaces already AGREE on the channel — there is no join to fix. The bug is that the outcome model applies a
   `DD_FAILED`/"Direct debit returned"/`insufficient_funds` event to a customer who is **not on DD at that
   instant**. That is wrong *regardless of whether the channel is static or dynamic*.
2. **The invariant is a WALL that survives the FRAME's fix.** Even a perfect time-varying channel model would,
   at every instant a customer IS on `standard_credit`, still be forbidden from emitting `DD_FAILED` for them.
   So INV-PCDD must hold under both models — and it becomes *more* load-bearing under a dynamic model, where a
   single customer's history spans a DD segment (DD events legal) and a standard-credit segment (DD events
   illegal); the invariant is precisely what checks each segment's events are method-consistent across the
   transition.
3. **Cost asymmetry.** The invariant + stage-vocabulary branch is small, reversible, and closeable now
   (self-drawable DISCOVER already done). The time-varying channel is a genuinely larger mechanism (a
   channel-transition process driven by DD-failure history), touches the R13 baseline, and is director-gated.
   Blocking the cheap correctness wall on the expensive feature would be a Rule-0 dial inversion.
4. **They compose, not conflict.** Recommended sequence: (i) land INV-PCDD + method-correct failure stages now
   (closes the absurdity class); (ii) propose the time-varying channel as a *separate* FRAME/atom, with INV-PCDD
   already in place as its acceptance guard (a customer who transitions DD→standard_credit after N failures must
   show DD events only in the DD segment). The FRAME's insight is real and should be built — but as the second
   step, protected by the first.

**Bottom line:** invariant first (correctness wall, now), time-varying channel second (fidelity feature, gated) —
the mint's "cross-generator consistency invariant" is the right first BUILD, with the one correction that the
defect is a single-generator category error, not a generator disagreement.

---

## CORRECTION (2026-08-03, the BUILD tick) — two errors, both found by measuring rather than reading

Status above is stale: BUILD is no longer blocked (`director_build_open`/`director_level_up` were
abolished 2026-07-29 and swept 2026-08-03), and the atom is now **L0→L2** as
`W2_payment_channel_dd_consistency_invariant`. The verdict and §5's sequencing argument both **stand** —
the defect is a single-generator category error, the invariant is the correct first build, and it was
built. Two substantive claims did not survive contact with the data.

### Error 1 — §3B's sample-surface count is an UNDERCOUNT (3 stated, **8** measured), and its reason is false

§3B says: *"Sample class = 3 customers (C5/C6 are SME → `payment_channel=None` on the sample surface and
carry no resi behavioural trajectory, so they only surface in the ledger)."*

**They all carry a behavioural trajectory.** Measured on `site/data/customer_sample.json` with the
shipped control, the sample class is **8**: C1g, C4, C8 (resi `standard_credit`) **plus** C5, C6 (SME)
**plus C_IC1, C_IC2, C_IC3g (I&C)** — every one of them `payment_channel: null` with `dd_failed > 0`.
The union class is therefore **8**, not 5.

### Error 2 — there are THREE DD-artefact generators, not two; §1's table is missing the one that matters

§1 maps `arrears_engine` (ledger) and `payment_behaviour_source` (sample). The I&C rows above come from
neither. `background/live_payment_triad.py` maps **both `"failed"` AND `"dispute"`** onto the literal
string `DD_FAILED`, under its own explicitly **NAMED SIMPLIFICATION** (*"the legacy analytics vocabulary
has only ON_TIME/LATE/DD_FAILED"*). So every corporate **invoice dispute** — a CHAPS customer, correctly
carrying `INVOICE_DISPUTED` on the ledger surface — is recorded as a returned Direct Debit on the
behavioural surface. A surface this DISCOVER never opened.

Minted as `W2_non_dd_miss_vocabulary`, with the trap recorded: the fix is **not** a rename.
`payment_behaviour_analytics.dd_fail_rate` counts `result == "DD_FAILED"`, and `life_event_detector`,
`affordability_inference` and `sme_credit_risk` all read `late_rate + dd_fail_rate` as their distress
signal — emitting a new label without teaching those four would make a non-DD customer's misses stop
registering as distress at all.

### A third miss, in the method rather than the finding — the caller census

`grep -rn "arrears_stages"` finds **one** production caller (`tools/generate_billing_ledger.py`). There
are **two**. `simulation/arrears_engine.py` dispatches it as
`(arrears_stages if outcome == "failed" else ic_arrears_stages)(...)` in two places, which no name-grep
reaches. It was found only because `method` was made a **required keyword-only** argument instead of a
defaulted one, so the un-migrated call site failed loudly at the call rather than quietly in the data.
That is the same rename/indirection fail-open `SP2_1`'s `_add_wd` census hit, in a different disguise.

### What §4b's remediation list got RIGHT, and the one item deliberately not done

The stage-vocabulary branch landed as specified (`DD_FAILED`/"Direct debit returned" reserved for
`direct_debit`; non-DD opens `PAYMENT_MISSED`). **The SME case-normalisation was deliberately NOT done**,
and §4b's one-line framing of it (*"fix the SME case-normalisation ... so I&C/SME never route through the
resi channel model"*) is a trap. Measured: `payment_outcome("bacs", stress, rng, segment="SME")` returns
`("success", 0)` **unconditionally**, because the dispute branch is gated on `_IC_SEGMENTS = ("ic", "I&C")`
and SME is not in it. Normalising the case alone therefore moves C5/C6 onto a path where they can **never
fail a payment**, deleting 3 failed payments and 3 arrears cases of real SME bad debt. **The case bug has
been masking the absence of any SME payment-outcome model.** Minted separately as
`W2_sme_segment_case_normalisation`, blocked on an anchored SME default-behaviour source rather than a
coefficient invented to fill the gap.

**Carried forward:** this is the fifth consecutive atom whose closed DISCOVER doc contained
build-blocking errors. A closed DISCOVER doc is a hypothesis, not a specification.
