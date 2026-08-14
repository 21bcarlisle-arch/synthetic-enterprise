# PB2 DISCOVER — the opening book, its size, and the path that has to win it

**Atom:** `PB2_opening_book_won_not_assigned` (`docs/design/maturity_map.yaml`, lane
`W2_customer_generator`, epoch 2, `loop_stage: idle`, `provenance: director_ruling`).
**Source ruling:** `docs/staging/in_progress/DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11.md`
(deliverable 2). **Mint receipt:** `docs/staging/done/PLANNER_MINTED_population_and_book_growth_2026-08-11.md`.

**This is a LANE-3 DISCOVER/FRAME pass. No BUILD.** The atom is `idle`, which parks it for BUILD
only (`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` rule 1). `level_current` stays **0**, `loop_stage` stays
`idle`, nothing in any `file_scope` was touched, no curriculum value moved (R13 — the population
draw's activation and profile are the director's, and this document proposes, it does not flip).

Every figure below is either read from a committed artefact (path and commit named) or computed in
this document from figures that are. Nothing is asserted from memory; the two places where the
evidence runs out are labelled UNMEASURED and are treated as unknown, not as zero.

---

## 0. The answer, up front

| | |
|---|---|
| **Proposed opening book (target)** | **3,217 accounts** — derived, §1 |
| **What it is anchored to** | Ofgem's Capital Target of **£130 per dual-fuel-equivalent domestic customer** (26 July 2023 decision) and the company's own published opening treasury of **£2,467,568.06** |
| **Affordability verdict** | **NOT affordable today.** The AO12 probe measured the settlement build dying at **465 customer-years** under its 3,072 MB ceiling; 3,217 is 6.9× that. Cost governs, per the ruling. |
| **Recommended interim** | The largest N that completes a **green full shipped run**, established by bisection. Until that measurement exists, **465 is the fail-closed cap** — itself ~36× today's book, so the director's "materially larger than 13" is satisfied by the interim alone. |
| **Population floor this implies for PB1** | **N_pop ≥ 18,756 premises** — derived from the funnel's own quotes-per-win, §4 |
| **Structural blocker found** | Exit (d) is **unsatisfiable by construction today**: the seam makes the book and the population the *same set*, so there is no unwon remainder for the book to be a subset of. §5 |

I am not asking which of these to do. Recommendation: adopt the derivation and the interim, and let
PB1 carry the bisection, because the measurement it needs is the one PB1 already owes.

---

## 1. The proposed size, and why it is not a round number

The ruling's requirement is "materially larger than 13 and defensible as a plausible small
supplier". A defensible number is one that **falls out of a constraint**, so here is the constraint.

A supplier that starts with N accounts must, out of its own opening capital, do two things:

1. **Win** them — the acquisition path costs real money per account won (§3), and
2. **Capitalise** them — Ofgem's Minimum Capital Requirement decision (26 July 2023) sets a
   **Capital Floor of £0 and a Capital Target of £130 per dual-fuel-equivalent domestic customer**,
   phased in by milestone assessment. Source: `docs/market_research/ofgem_licence_readiness.md` §2,
   with the Ofgem decision-document URLs quoted there. The figure is **already load-bearing in this
   repo**, not imported for this argument: `company/finance/treasury.py::MCR_PER_ACCOUNT = 130.0`
   and `saas/capital/solvency.py::MCR_FLOOR_GBP_PER_CUSTOMER`.

So the largest book the company could have *bought and still lawfully held* is

```
N* = opening_capital / (MCR_per_account + cost_per_account_won)
```

**Opening capital** = `£2,467,568.06`, read from `site/data/dashboard.json`
(`portfolio.treasury_start_gbp`), read at `meta.git_commit = dfc233094` and RE-READ at the current
published stamp `1cf30581b` — the same £2,467,568.06 both times, so the derivation does not rest on
a stale snapshot (the stamp moved under it during this pass; the figure did not). It is a company-layer figure —
the company's own treasury at window open — so quoting it crosses no wall.

**Cost per account won** = `£637.02` for a book won in the 2016 window; `£553.93` post-REC. Both are
computed in §3 from the shipped funnel's own constants, which themselves trace to
`docs/market_research/findings/acquisition_funnel_benchmarks.md`.

```
N*(2016 window, pre-REC)  = 2,467,568.06 / (130 + 637.02) = 3,217
N*(post-REC 2022 onwards) = 2,467,568.06 / (130 + 553.93) = 3,607
```

**The opening book is won in 2016, so the number is 3,217.** The arithmetic closes on itself: at
N = 3,217 the company spends **£2,049,295.20** winning the book and holds **£418,210** against the
Ofgem target — **£2,467,505.20**, which is its entire opening treasury less **£62.86**: the residual
is there because 3,217 is the floor of the unrounded 3,217.08, and one more account costs £767.02
the balance sheet does not have. So it closes to within a pound *of one account*, not to the pound
on the total — the honest version, and the one that still makes it a ceiling. That is the *ceiling*, not a
plan: any working capital reserved for wholesale purchase comes straight off it. It is exactly the
right shape for a plausibility anchor, because it says what "small real supplier" means in this
company's own numbers — **the book its balance sheet could have paid for** — and it is 247× today's
13 and 292× the 11 supply points the published book actually carries in 2025
(`site/data/dashboard.json` → `customers.book_annual`, 9 electricity + 2 gas).

**The tell that today's book is a fixture, in the regulator's own units.** At 11 accounts the
company holds £2.47m against an MCR requirement of £1,430 — **1,725× the Capital Target**. An MCR
headroom control against that book cannot ever bind, in either direction; it is a control whose
subject cannot move it (R15's "cannot fail" family, seen from the other side). Sizing the book to
the balance sheet is what gives that instrument a live subject for the first time.

**Sanity check against the real market, with its denominator caveat.** `f5_simulated_competitor_field.md`
§8 records (Ofgem *State of the Market*, Jan 2026) that Octopus holds ~12.9m household accounts at
~23.7% of the available market, implying a market of ~54.4m accounts, and that ~8% of the domestic
market sits outside the top six. 3,217 accounts is ~0.006% of that — deep in the long tail, which is
precisely where a plausible small supplier sits. Treat this as an order-of-magnitude check only:
that same section warns that two "market" denominators coexist and are not interchangeable.

---

## 2. The affordability verdict — the probe governs, and it says no

The ruling makes cost the governor: *"if the probe says the scale is unaffordable on current
storage, that is the answer."* `AO12_scale_probe_10k` (level 2, run `20260812T013154Z`) reports in
`docs/observability/scale_probe_10k/report.json`:

| stage | status | what it measured |
|---|---|---|
| `population_draw` | measured | 10,258 customers in 0.20 s, **860 bytes RSS/customer** — the world is cheap |
| `settlement_build` | **ceiling_death** | **MemoryError at 465 customers**, 17,517 records/customer-year, projecting **63.9 GB** at 10k |
| `run_output_serialization` | measured | 248.46 output bytes/record → **4.35 MB per customer-year** of raw settlement |
| `site_publish`, `git_transport` | measured | both carry their own UNMEASURED notes |

Three things follow, and the third is the one that matters for PB2.

**(i) The expensive object is the BOOK, not the world.** ⚠ **CORRECTED 2026-08-14** by the FRAME
pass (`docs/design/PB2_UNWON_REMAINDER_FRAME.md` §5), on a finding PB1 §(g) queued against this
record. The paragraph originally read the 860 B/**customer** figure above as 860 B/**premise** and
concluded a premise the company never won is "nearly free", ~7,400× cheaper than a won one. That is
R15's wrong-subject shape: AO12's `population_draw` stage declares `"unit": "customer"` and its
subject is `simulation/population_draw.py`; `simulation/premise_population.py` has **no stage in the
report at all**, so the per-premise cost is UNMEASURED and therefore UNKNOWN, never zero (PB1 exit
(d) governs). **The ~7,400× multiplier is withdrawn.**

What survives is the structural half, which never needed the byte figure: the two objects reach
different *stages*. A won premise enters `settlement_build` — the stage AO12 measured dying at 465
customer-years — and an unwon one never does. So **PB1's affordability question is still mostly
PB2's question**, and the book target is what the probe kills. The measurement that would restore a
number is PB1 §(f) prerequisite (1), an AO12 stage whose subject is
`premise_population.draw_premise_population`. Still owed; not taken here.

**(ii) The cap is 465, fail-closed.** The projection at the box's full 8.58 GB RSS budget is 1,343
customers, but the probe's own `detail` field says the per-unit cost is *under-stated* (its baseline
was taken at the first checkpoint) and the stage did not survive to be measured properly. PB1's exit
(d) — a stage the probe never reached is an UNKNOWN cost, not a zero — applies to a stage it reached
and died in, too. **Use the measured 465, not the projected 1,343.**

**(iii) 3,217 is 6.9× the measured cap. Verdict: NOT AFFORDABLE on current storage.** That is the
answer, not a problem to route around, and the ruling names the prerequisite:
`DIRECTOR_INSTRUCTION_QUERYABLE_PROJECTIONS_2026-08-10.md` (still an unminted mint source in the
staging root). At 3,217 accounts the raw settlement working set alone is 3,217 × 4.35 MB/yr × 10
years ≈ **140 GB** before the reduction — and the reduction's cost is explicitly UNMEASURED in the
probe's own report, so no smaller number may be claimed for the persisted artefact.

**What the interim costs.** 465 accounts × (£130 + £637.02) = **£356,664**, 14.5% of opening
treasury. The interim is comfortably capitalised; it is bounded by RAM, not by money.

---

## 3. The acquisition path (exit b) — how the book is won, and what must never happen

Cost per account won, computed from shipped constants (`simulation/acquisition_funnel.py`,
`saas/growth_mandate.py::COST_PER_ACQUISITION["resi"] = 150.0`):

```
p(win | quote)  = 0.24 (quote→application) × 0.94 (creditworthy) × 0.95 (credit→onboarding)
                  × 0.80 (survives cooling-off, pre-REC)      = 0.171456   → 5.83 quotes per win
E[cost | quote] = 150 × (0.65 + 0.24×0.10 + 0.2256×0.05 + 0.2143×0.20) = £109.22
cost per won    = 109.22 / 0.171456 = £637.02        (post-REC survival 0.92 → £553.93)
```

**The organs already exist; the path is a wiring, not a build.** In order:

1. `saas.growth_mandate.should_attempt_acquisition()` — the company's own awareness/consideration
   gate. A **company-side decision**, made blind.
2. `simulation.acquisition_funnel` — the **world's** response: quote → application → credit_check →
   onboarding → cooling_off, each stage with real calendar spacing and per-stage cost. The company
   proposes; the world disposes.
3. `company.crm.onboarding_journey` — the company's own record of the customer arriving, built from
   the SLC-dated events it can actually see (SLC 14.2 welcome pack, 22.1 first bill, 7.5 smart-meter
   offer).
4. `company.interfaces.supply_book.register_acquired_point()` — the book grows by **one won account
   at a time**, at the moment it is won.

**The forbidden shape, stated so a future build can be checked against it.** A "second cast" is any
path where a roster of N customers is materialised and handed to the company as a starting state.
Today's seam is exactly that shape (`simulation/live_population.py::live_population()` appends the
whole drawn cohort to `CUSTOMERS` and registers it) — which is safe *only* because the activated
draw is the director-signed **Profile B trickle, λ=1.0, realising as two customers**
(`docs/design/curriculum/population_draw_activation.json`). Two won customers appended is a trickle.
**Three thousand appended would be a grant**, and the same file already says so in the director's own
term: *earned, never granted*. Scaling the opening book by raising λ on the existing seam is
therefore the one implementation that must not be chosen, however easy it looks.

**What a build must do instead:** the opening book arrives as ~18,756 quotes issued into a drawn
population over the opening period, of which ~3,217 (17.1%) survive to supply, each one costing the
P&L its funnel stages and each one traceable to a `FunnelStageEvent` chain. The book size then is not
a parameter anywhere in the tree — it is a **measurement of what the campaign won**, which is what
makes PB3's "growth curve that can be lost" possible at all.

**Governance seam for the size:** the acquisition *profile* is curriculum (R13). Proposing a Profile
C ("opening campaign") means one versioned edit to `docs/design/curriculum/population_draw_activation.json`
by the director, not a code change — the mechanism is already the right shape and needs no new gate.

---

## 4. What this hands PB1 — a derived population floor

Every quote must be issued to a real premise in the world. At 1/0.171456 = **5.8324** quotes per win,
and rounding UP because it is a floor:

```
N_pop ≥ ⌈5.8324 × N_book⌉       (distinct premises quoted, one quote each)
      = 18,756 premises at the 3,217 target      (5.8324 × 3,217 = 18,755.13)
      =  2,712 premises at the 465 interim       (5.8324 ×   465 =  2,711.06)
```

This is the first floor PB1 has that is *derived* rather than proposed: the population must be big
enough for the funnel to have somewhere to lose. It also fixes the subset ratio as a consequence
rather than a choice — **book/population ≤ 17.1%**, because that is the funnel's win rate.

⚠ **CORRECTED 2026-08-14** (FRAME pass §5): this paragraph originally continued "and at 860 bytes
RSS/premise, 18,756 premises cost ~16 MB to draw — the world is affordable at the target book's
floor even though the book is not." **That verdict is withdrawn.** The 860 B figure's measured
subject is a drawn *customer*, not a drawn premise, and AO12 has no stage for
`premise_population`; an unmeasured stage is an unknown cost, not a zero. The world's affordability
at this floor is **UNDECIDED** pending that stage. The count floor above is unaffected — it is
funnel arithmetic and never used the byte figure.

---

## 5. The wall (exit c) and the subset (exit d) — one exists, one cannot yet be true

### (c) The wall control PB2 needs is already built and already R15-proven

`tests/architecture/test_epistemic_wall_ratchet.py` is a static import ratchet over the
company↔sim perimeter, with **mutation tests both ways**
(`test_mutation_injected_company_reads_sim_reds_only_new_crossing`,
`..._sim_reads_company_...`, plus walker/exemption mutations). `tests/simulation/test_live_population_seam.py`
adds the **runtime** half for the hidden ground truth: `test_wall_drawn_book_never_exposes_ground_truth_cohort`,
`test_runtime_wall_covers_every_forbidden_cohort_field`,
`test_to_customer_dict_never_emits_a_hidden_cohort_field`, and the guard's own falsifier
`test_the_company_import_guard_can_fail`.

**Do not build a third wall control for PB2.** The instrument exists; a new one would be a second
way to do one thing, and the failure mode this repo actually suffers is an orphaned control, not an
absent one. What PB2 must do is **name its subject inside the existing instrument**.

### The subject that does not exist yet — and it is the whole atom

Exit (d) says the opening book must be *measured to be a genuine subset of the drawn population*.
Read `simulation/live_population.py:161-177` directly: every drawn `SyntheticCustomer` is rendered
and appended, then registered. **The drawn population IS the book.** There is no remainder. The
subset test would today assert `|book| == |population|` and pass, which is the tautology R15 names
first — the checked value derived from the same source it checks.

So the third wall subject PB2 introduces, for the first time in this codebase, is **the unwon
remainder**: the premises the world has drawn and the company has *not* acquired. That set does not
exist today, which is why no control covers it. Once it exists, the wall statement becomes testable
and non-trivial:

* **positive:** the company's book contains only ids it has an onboarding-event chain for;
* **negative (the mutation that must RED):** a company-side read of the unwon remainder — enumerating
  drawn-but-not-acquired premises, or resolving one by id — fails. Because the remainder is data
  rather than an import, the static ratchet alone will not catch a value passed through a dict; this
  needs the **runtime** guard pattern (`test_runtime_wall_covers_every_forbidden_cohort_field`)
  extended to roster membership, not a new mechanism.
* **subset, non-tautologically:** `book_ids ⊂ population_ids` **and** `|remainder| > 0` **and** every
  book id carries a funnel chain. The third clause is what makes the first non-derivable from the
  producer, which is the independence R15 demands.

---

## 6. Blockers a future build will hit, found in this pass

1. **The draw saturates at λ ≈ 745** (`WORKER_FINDING_THE_POPULATION_DRAW_SATURATES_ABOVE_LAMBDA_745_2026-08-12.md`).
   A single call asking for thousands returns ~733 silently. Any opening-book build **must** batch
   below saturation with per-batch seeds and id prefixes, exactly as `tools/scale_probe_10k.py` does,
   or fix the generator in log space — the owning lane's call, and byte-identity below saturation is
   the constraint.
2. **The SYN key set diverges from the static roster.** `live_population.py`'s own docstring flags it
   and it has already cost seven consecutive failed runs on 2026-08-13 (`KeyError: 'epc_rating'`,
   `KeyError: 'SYN-2021-001'`). At two drawn customers this is a nuisance; at 465 it is the run.
   Hardening the entrypoints is a **precondition** of any book increase, not a follow-up.
3. **The activation-half asymmetry** (`WORKER_FINDING_THE_POPULATION_DRAW_IS_LIVE_ON_DISK_WHILE_ITS_ROSTER_FIX_IS_UNCOMMITTED_2026-08-13.md`):
   a curriculum JSON arms from the working tree while its code path arms only at HEAD, so the two
   halves cannot land atomically. A Profile C edit inherits that hole intact.
4. **The sim's cost per won account (£637) is ~11× the sourced PCS commission** of £25–30 per fuel
   switched (`B2_CATEGORY6_CAC_ANCHORS.md`, CMA-era). The £150-per-attempt constant is documented as
   quote/application *processing* cost rather than channel commission, so the two are not the same
   line — but at 3,217 accounts the difference is £1.9m of opening capital and it deserves a
   deliberate answer before it silently sets the book size. **QUEUED as a finding, not fixed here**
   (SELF_INTERRUPT_DISCIPLINE — the atom that owns CAC owns this).

---

## 7. What this pass deliberately did not do

* **No BUILD.** No code, no test, no `file_scope` path touched; the atom is `idle`.
* **No level move.** DISCOVER does not move levels (`MATURITY_MAP.md` §3); `level_current` stays 0.
* **No curriculum change.** λ, the profile, the activation flag and the population target are all
  director-reserved (R13). This document proposes 3,217 and an interim; it flips nothing.
* **No re-derivation of the probe's numbers.** Every cost figure is read from
  `docs/observability/scale_probe_10k/report.json`, and the two stages carrying UNMEASURED notes are
  reported as unknown rather than absorbed into a total.
* **No claim that the interim is 465.** 465 is a *ceiling-death artefact under a 3,072 MB
  address-space limit the probe chose*, so it is a fail-closed cap, not a proposal. The interim
  number is whatever a bisection of full shipped runs measures, and that measurement does not exist
  yet.

— Worker tick, 2026-08-13. LANE 3 DISCOVER draw on `PB2_opening_book_won_not_assigned`.
