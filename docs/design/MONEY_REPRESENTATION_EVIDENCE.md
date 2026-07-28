# Money-representation evidence for the director — float vs Decimal (DISCOVER, 2026-07-28)

**Status:** DISCOVER-ONLY. No code changed. No money type migrated. This document answers the two
evidence items named in `DIRECTOR_RULING_SHARED_PRIMITIVES_AND_CODE_STANDARDS_2026-07-28.md` §6 /
Acceptance item 7 (mint: `docs/staging/in_progress/PLANNER_MINTED_money_representation_evidence_2026-07-28.md`).
**The decision is director-reserved** (one-way-door #5-adjacent, Tier-1 "bills accurate above all").
This atom recommends; it does not act.

Evidence basis: read of the live repo tree at commit range up to `bf106fbc6` (2026-07-28), plus a
real, already-generated full billing run persisted on disk — `docs/reports/run_output_6c9fa672b_20260728T083004Z.json`,
**basis clock: generated 2026-07-28T08:30:04Z**, `1,588` bills, `19` customers, billing periods
`2016-01-01` .. `2025-06-01` (settled/billed basis — these are the company's own billed amounts, not
banked/collected). All figures below are **observed-with-evidence** unless explicitly marked
**inferred**, per R9.

---

## 1. Money representation census

**Claim in the mint: zero `Decimal` usage across `saas/`+`company/`. Confirmed.**

```
grep -rn "Decimal" saas/   → 0 matches
grep -rn "Decimal" company/ → 0 matches
```

Money is `float` everywhere it is computed, from generation through to storage and publication:

- **`saas/bill_generator.py::generate_bill()`** (the root of the money call graph — see §3) — every
  money field (`commodity_amount_gbp`, `non_commodity_amount_gbp`, `standing_charge_gbp`, `vat_gbp`,
  `total_amount_gbp`) is a plain Python `float`, built from `sum()` of dict values and `*`/`/`
  arithmetic (`saas/bill_generator.py:109-163`). No rounding/quantization inside the function at all
  — full IEEE-754 double precision leaves `generate_bill()` unrounded.
- **`saas/ledger.py`** — every event constructor is typed `amount_gbp: float` / `provision_gbp: float`
  / `cost_gbp: float` (e.g. `saas/ledger.py:66`, `118`, `152`, `172`). `unbilled_revenue_accrual()`
  applies `round(..., 2)` only at the point a figure is exposed (`saas/ledger.py:338,342`) — an ad hoc
  display rounding, not a declared quantization policy.
- **`saas/reporting/annual_report.py`** (9,276 lines — the single largest money-handling module) — the
  same pattern throughout: `float` accumulation via `sum()`/`+=` over `_gbp`-suffixed dict keys, with
  `round(x, N)` scattered at individual call sites when a figure is about to be displayed (e.g.
  `saas/reporting/annual_report.py:135`, and the wider corpus below).
- **`tools/generate_billing_ledger.py`** — the module that turns `generate_bill()`'s unrounded float
  output into the persisted customer-facing invoice: `round(bill.get("commodity_amount_gbp", 0), 2)`,
  `round(bill.get("non_commodity_amount_gbp", 0), 2)`, `round(bill.get("standing_charge_gbp", 0), 2)`,
  `round(bill.get("vat_gbp", 0), 2)` (lines 236-241) — **each component rounded independently** — and
  separately `"total_amount_gbp": round(amount, 2)` (line 242) where `amount` is the **unrounded**
  float total, not a re-sum of the just-rounded components. This independent-rounding pattern is the
  direct cause of the drift measured in §2.
- **`company/billing/invoice.py`** — money persists to SQLite as `REAL NOT NULL` columns (lines 46-47,
  239) — `REAL` in SQLite is an IEEE-754 double, i.e. **float at rest**, not just float in memory. This
  is the one place the census found money leaving the Python process boundary, and it is still float.
- Scale of the ad hoc rounding pattern: `round(..., 2)` (the informal "2dp money" idiom) appears
  **1,006 times** across `saas/`, `company/`, `tools/`, `simulation/` combined. `round(` calls
  co-occurring with a `_gbp` identifier on the same line: **26** in `saas/`, **548** in `company/**`
  (company/'s much higher count reflects its far larger file count, not a different pattern).

**Conclusion on item 1: the mint's claim holds exactly.** There is no declared money type. The system
is not "using float as a deliberate choice" and not "using Decimal" — it is applying `round(x, 2)` at
whichever point in the pipeline a developer happened to remember to, independently at each of dozens
of call sites, with no shared quantization primitive. This is the "undeclared, worst of the three"
state the ruling names.

---

## 2. Worst observed rounding drift across a full billing run

**Method (read-only, no live-path change):** `docs/reports/run_output_6c9fa672b_20260728T083004Z.json`
carries the `bills` array — `generate_bill()`'s real, **unrounded** float output for a full historical
billing run (1,588 bills / 19 customers / 2016-2025), i.e. the actual live-path numbers before
`tools/generate_billing_ledger.py` rounds them for the customer-facing invoice. This is real production
output, not synthetic test data. Two independent measurements were run against it, in-memory, via a
throwaway script (not committed, not part of the live path):

- **(A) Live-float-path internal consistency** — for each bill, round each of the four line-item
  components (`commodity_amount_gbp`, `non_commodity_amount_gbp`, `standing_charge_gbp`, `vat_gbp`) to
  2dp exactly as `tools/generate_billing_ledger.py` does, sum them, and compare to the independently
  `round()`-ed `total_amount_gbp` that is actually billed to the customer.
- **(B) Shadow Decimal cross-check** — the same comparison, but the four components are quantized via
  `Decimal(str(x)).quantize(Decimal("0.01"), ROUND_HALF_UP)` (a proper penny-accurate decimal
  computation) instead of Python `round()`, to confirm (A) is a real quantization phenomenon and not an
  artefact of `round()`'s banker's-rounding-on-binary-floats behaviour specifically. **This shadow
  computation ran in parallel for comparison only — it never touched or replaced the live float path.**

`147` of the 1,588 bills carry a back-billing `catchup_adjustment_gbp` line (a real additional charge
not among the four base components); these were excluded from (A)/(B) to avoid a false positive (an
initial unfiltered pass showed a spurious "£10,361.26 worst drift" that was entirely this — catchup
bills were checked separately in (C) below and are fine).

**Results, ordinary (non-catchup) bills, n = 1,441, basis: billed, run generated 2026-07-28T08:30:04Z:**

| Measurement | Worst per-bill drift | Aggregate signed drift | Bills affected |
|---|---|---|---|
| (A) live-float: Σ(rounded components) vs rounded total | **£0.02** | **-£0.22** | 533 / 1,441 (37.0%) |
| (B) shadow-Decimal quantize-then-sum vs live float total | **£0.02** | **+£0.01** | 532 / 1,441 (36.9%) |
| (C) catchup bills (n=147): components+catchup line vs total | £0.01 | £0.01 | sanity-check only |

(A) and (B) agree to the penny on the worst case and land within a few pence of each other in
aggregate, confirming this is a genuine rounding-quantization effect of independently rounding parts
of a whole, not a measurement bug.

**Reading of the figure:** the *aggregate* magnitude is small at this run's scale (19 customers,
£0.22 net over the run) — this is **not** a story about cumulative pounds draining away. The material
finding is the **defect rate**: on **37% of ordinary bills**, the four line items printed on the
invoice do not sum, to the penny, to the total printed on the same invoice. That is a customer-facing
"the maths doesn't add up" surface (the director's own prior comment on `/customers/`, referenced in
`saas/bill_generator.py:190-194`, was literally "we need to be able to explain the maths properly") —
present on more than a third of bills, at production scale (19 customers × ~10yr history). It would
scale proportionally in *incidence* (still ~37% of bills) as the customer book grows, even though the
aggregate £ figure stays small per bill.

Worst-case single-bill drift observed: **£0.02** (2 pence). No drift over 2p was observed in this run.
**This figure is observed-with-evidence from one real run; it is not a proof of a hard upper bound** —
a different billing-period/tariff/segment mix could in principle produce a larger single-bill drift
(inferred, not measured: the mechanism is bounded by the number of independently-rounded components
summed, currently 4, so the theoretical worst case per bill is bounded near `4 × 0.005 = £0.02`, which
matches what was actually observed).

---

## 3. Blast radius of a boundary conversion

**Call graph, root to publish (traced via `grep`/import inspection, not assumed):**

```
simulation/run_phase4c_on_phase2b.py  (orchestrator; calls generate_bill() twice per period:
      │                                 true_bill + estimated_bill, lines 352 & 441)
      ▼
saas/bill_generator.py::generate_bill()   <- ROOT of all money computation, unrounded float
      │
      ├─▶ saas/contact_model.py            (clarity_score / bill_shock_pct-driven complaint modelling)
      ├─▶ saas/payment_behaviour.py        (payment lifecycle, bad-debt provisioning)
      ├─▶ saas/ledger.py::build_ledger()   (9 event types, P&L, cash position)
      ├─▶ tools/generate_billing_ledger.py (persisted customer invoice JSON — docs/state/billing_ledger.json;
      │                                      first rounding boundary, independent per-component)
      ├─▶ company/billing/invoice.py       (SQLite persistence — REAL columns, i.e. float AT REST)
      ├─▶ company/billing/pre_bill_validation.py
      └─▶ saas/reporting/annual_report.py  (9,276 lines — portfolio P&L, dashboards, segment reports)
              │
              ├─▶ saas/reporting/segment_report.py
              ├─▶ tools/generate_margin_bridge.py
              ├─▶ tools/generate_dashboard_data.py   -> site/data/*.json (public site, 10 files touch
              │                                          _gbp fields directly)
              ├─▶ tools/contact_centre_port.py
              ├─▶ tools/acquisition_funnel_port.py
              ├─▶ tools/tournament_runner.py
              └─▶ tools/publish_report_gist.py       -> docs/reports/ANNUAL_REPORT.md (public report)
```

**Surfaces a float→Decimal boundary conversion would have to cross:**

1. **Computation core** — `saas/bill_generator.py`, `saas/ledger.py`, `saas/reporting/annual_report.py`
   (9,276 lines alone), `saas/payment_behaviour.py`, `saas/contact_model.py`. All arithmetic (`sum()`,
   `+`, `*`, `/`, `min`/`max` over money) would need Decimal-safe rewrites; Decimal does not silently
   interoperate with float (`Decimal(1) + 0.1` raises `TypeError`), so this is not a type-annotation
   change, it is a rewrite of every arithmetic call site.
2. **Persistence** — `company/billing/invoice.py`'s SQLite schema uses `REAL` columns. Decimal-accurate
   storage needs a schema change (`NUMERIC`/`TEXT` affinity or integer-pence columns) plus a migration
   of any existing rows.
3. **Serialization / JSON boundary** — `docs/state/billing_ledger.json`, `docs/reports/run_output_*.json`,
   and `site/data/*.json` all currently carry money as JSON numbers. `Decimal` is not natively
   JSON-serializable (needs a custom encoder, typically to a string) — every downstream JSON consumer,
   including the **front end**, would need to change how it parses money. Confirmed **10** `site/data/*.json`
   files carry `_gbp`-suffixed fields directly, and **10** front-end files use `toFixed`/
   `Intl.NumberFormat` for money display — both assume a JS `number`, not a string. A Decimal-as-string
   JSON boundary breaks these silently (`toFixed` on a string throws) unless every one is touched.
4. **Test surface** — **567 test files** reference `_gbp` fields. Many money assertions use
   `pytest.approx()` (float-tolerant); those would need re-auditing under Decimal (some become exact
   equality, some still need tolerance for rate-derived quantities), which is itself a non-trivial
   review pass, not just a search-and-replace.
5. **The ad hoc rounding idiom** — 1,006 existing `round(x, 2)` call sites would each need inspection:
   is this a boundary rounding point (correct place to quantize) or an internal one (should be removed
   in favour of carrying full Decimal precision until the real boundary)?

**Cost/risk estimate (inferred, not measured — no work was done to migrate anything):**
- A **full core migration** (float→Decimal everywhere money is computed) touches the single largest
  file in the money graph (`annual_report.py`, 9,276 lines) plus 5-6 other core modules, the SQLite
  schema, and every JSON/front-end consumer. This is a multi-phase, weeks-scale (inferred) effort with
  meaningful regression risk against 567 existing tests, squarely in "don't do lightly under a Tier-1
  bills-accuracy rule" territory.
- A **boundary-only conversion** (keep float internally, introduce one shared Decimal-quantization
  helper used consistently at the *existing* rounding points — replacing the 1,006 ad hoc `round(x,2)`
  call sites with one declared, tested primitive, with correct component/total reconciliation so §2's
  37%-of-bills defect can't recur) is materially smaller: it does not touch the SQLite schema or the
  JSON/front-end boundary at all (output is still a float, just correctly quantized and internally
  consistent), and the surface is the ~1,006 call sites rather than the full arithmetic core. This is
  the option that most directly answers the actual observed defect in §2 (parts not summing to the
  whole) without opening the higher-risk full-migration surface.

---

## 4. Recommendation

**Both a full float→Decimal migration and a declared, quantization-consistent float boundary are
defensible per the ruling ("either answer can be right") — the choice is the director's.** This atom
recommends, it does not act.

**Recommendation: adopt a declared boundary-conversion policy, not a full core migration, as the
first move.** Reasoning from the evidence above:
- The measured defect (§2) is a **reconciliation** bug — line items don't sum to the printed total on
  37% of bills — not a **magnitude** bug (worst drift observed: 2p; aggregate: pennies over a
  10-year/19-customer run). A single shared quantize-and-reconcile helper at the existing invoice
  boundary (`tools/generate_billing_ledger.py`, `saas/ledger.py`'s display points) fixes exactly this,
  cheaply, without the schema/JSON/front-end blast radius in §3.
- A full core Decimal migration is the more *rigorous* long-term answer (it removes the class of bug
  entirely, not just the currently-observed instance — R10 would favour it) but costs materially more
  (9,276-line core file, SQLite schema, 10 JSON/front-end surfaces, 567 tests) for a defect whose
  measured financial magnitude is currently small. **If/when a real customer or real money is at
  stake** (per the one-way-door list item 7, "anything touching a real customer or real market") the
  calculus shifts and the full migration becomes the safer choice pre-emptively, not reactively.
- Recommend the director treat this as **two separable decisions**: (a) authorize the small
  boundary-reconciliation fix now (closes the observed 37%-of-bills defect, narrow blast radius, low
  risk) — this is arguably still Tier-1-adjacent since it changes bill arithmetic, so it stays gated
  behind the director's own word regardless; and (b) rule separately, on his own timeline, on whether
  the full core migration is warranted before real money is involved.

**Evidence summary for the [ACT]:**
- Decimal usage confirmed: **0** across `saas/`+`company/`.
- Worst observed single-bill rounding drift: **£0.02** (2p), aggregate **-£0.22** over 1,441 ordinary
  bills in the measured run (basis: billed, run `6c9fa672b` generated 2026-07-28T08:30:04Z, periods
  2016-01-01..2025-06-01) — observed-with-evidence, not inferred.
- Defect rate: **37.0%** of ordinary bills have line items that don't sum to the penny to the printed
  total — the material finding, not the £ magnitude.
- Blast radius of a full core conversion: 9,276-line core reporting module + SQLite schema (`REAL`
  columns) + 10 JSON/front-end surfaces + 567 referencing tests. Blast radius of a boundary-only fix:
  ~1,006 existing `round(x,2)` call sites, no schema/JSON/front-end change.
- **No code was changed to produce this evidence.** No money type was migrated. The decision remains
  the director's.
