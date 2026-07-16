# D4_loyalty_incentive_billing — FRAME (canonical per-atom, doc-only)

**Atom:** `D4_loyalty_incentive_billing` · lane `D_billing_metering` · epoch **4**
· `level_current: 0` → `level_target: 2` · `loop_stage: idle` · dial 1
· `depends_on: [C4_adoption_physics, D1_bill_correctness]`.
**Epoch-4-gated:** registered "do not start" per `docs/staging/done/ADOPTION_JOURNEY_REGISTER.md`
— DISCOVER/FRAME thought is available now (EPOCH_GATING_AND_ATOM_AUTHORSHIP); BUILD is not.
**Value stream:** `price_to_bill`. **Real-world twin:** Octopus Octoplus / Saving Sessions,
EDF Sunday Saver, British Gas PeakSave, Scottish Power Power Saver — real bill-visible
loyalty economics, not marketing copy.

**Turn:** H17 Lane-3 FRAME, doc-only / no BUILD code (EPOCH_GATING Rule 1) / no map edit
(F1, level reported via `docs/design/atom_status/D4_loyalty_incentive_billing.yaml`).

---

## Why this doc exists (and why it is NOT churn)

D4 carried only **inline DISCOVER simplifications** — the 2026-07-11 registration (P3,
advisor-staged, director "do not start" — `ADOPTION_JOURNEY_REGISTER.md`) and the
2026-07-12 four-scheme DISCOVER pass (Octoplus, Sunday Saver, PeakSave, Power Saver named
with real, current, quantified figures) — and **no `*_FRAME.md` on disk**. The registration
fixes SCOPE and placement but is explicitly "registration only... do not design"; the
DISCOVER pass confirmed the mechanic set is real and named but stopped short of a
consolidated design. Neither is a canonical FRAME terminus with a single stated
BUILD-unblock gate, so the idle-FRAME draw correctly kept re-offering D4 as genuinely
un-FRAMEd. **This doc is that missing terminus.** It **consolidates** the existing DISCOVER
findings into D4's own design — the mechanic-SHAPE taxonomy (§3), the bill-artefact
integration point on the *existing* bill standard (§4), the coupled gap to C4 (§5), the
epistemic wall (§6), and one gate (§7). It does **not** re-research the four schemes or
re-derive the ~£300/yr Octoplus figure; those are carried forward from DISCOVER, cited.

**Honest finding worth stating plainly, not buried:** unlike C4 (whose only remaining block
was the epoch gate, all its `depends_on` atoms being at/beyond their required levels), D4's
block is **BOTH the epoch gate AND an unmet prerequisite** — verified live against
`docs/design/maturity_map.yaml`, not assumed:

- `D1_bill_correctness` — **3/3, `harden`** — MET. The bill artefact and its correctness
  invariants D4 must land its reward/credit lines on are built and hardened.
- `C4_adoption_physics` — **0/2, `idle`** — **NOT MET**. D4 exists to carry persuasion load
  precisely where C4's bother-threshold is uncleared by objective £ (§5); "who gets offered
  what, when" is C4/C5's output. D4 cannot be *meaningfully* built (its whole point — that
  reward-response is discovered, not assumed) before C4 supplies the adoption-physics traits
  D4's mechanics act on. That is the honest epoch-sequencing intelligence this FRAME states
  once, per §7.

---

## 3. The mechanic-SHAPE taxonomy (the reference the BUILD anchors against)

The four real, concurrent 2026 UK schemes fall into **three distinct mechanic shapes**, not
one generic "loyalty" blob. This shape set is the reference the eventual BUILD anchors
against instead of inventing generic loyalty mechanics. For each: the **real P&L line** it
costs the company (not marketing copy), and **how it manifests as a bill-visible artefact**.

| Mechanic shape | Real schemes | What it costs the company (real P&L line) | Bill-visible artefact |
|---|---|---|---|
| **(a) Automatic discount window** — no opt-in, half-price fixed weekly window | British Gas **PeakSave Sundays**, Scottish Power **Power Saver** (both automatic, half-price electricity weekend 11am–4pm) | Foregone unit-margin on all in-window consumption for the *entire eligible book* (no self-selection filter — everyone eligible gets it), net of any peak-avoidance load-shift benefit to the company's own imbalance/wholesale position. A **tariff-structure cost**, borne whether or not the customer changes behaviour. | A **discounted-window tariff structure** — a time-banded `unit_rate_pence` on the electricity `FuelBillSection` (an existing field on `dual_fuel_bill.FuelBillSection`), not a separate credit line. The half-price window is a *rate*, so it lands as a modified `energy_charge_gbp` on the existing bill leg. |
| **(b) Opt-in points → bill credit** | Octopus **Octoplus Points** (redeemable as bill credit), partner-brand **Perks** | Real cash-equivalent liability accrued as points are earned and crystallised as revenue-reduction (or liability settlement) on redemption. Anchor: Octoplus delivered ~**£300/yr** of rewards on average ≈ **~17% of a typical annual bill** — a material, quantified P&L figure, not a rounding error. Cost is borne only for *engaged* customers (self-selecting), unlike shape (a). | A **reward-balance field** (points accrued, cash-equivalent) plus a **statement credit line** on redemption. The redemption credit is a one-off account credit — structurally the same as an `AccountAdjustmentRecord` with `direction=CREDIT` (see §4), but there is **no reward/loyalty `AdjustmentType` today** (named BUILD gap, §4). |
| **(c) Announced free-power EVENT** — time-boxed, sometimes opt-in | Octopus **Saving Sessions** / **Power-ups** (announced free-electricity windows), EDF **Sunday Saver Challenge** (4–16 hrs/week free electricity for weekday peak-avoidance) | Foregone unit-margin on in-event consumption, PLUS any per-event participation reward paid out; offset (partially) by the flexibility/demand-turn-down value the company captures against a real system-stress window (the *reason* these events exist — they are a DER/flexibility instrument dressed as a reward). Cost is **event-triggered and time-boxed**, not standing. | An **event-scoped statement line** — a credit or zero-rated consumption block for the announced window, referencing the event. Distinct from (a)'s standing tariff structure: (c) is a bounded, dated line tied to a specific announced event; (a) is a permanent rate band. |

**Why the shape distinction is load-bearing:** the three shapes have **different cost
dynamics** (standing tariff cost / self-selecting liability / event-triggered payout),
**different self-selection** (whole-book vs engaged-only vs event-opt-in), and **different
bill artefacts** (rate band / reward balance + credit line / event-scoped line). A BUILD
that models "loyalty mechanics" as one generic construct would get the P&L and the
adoption-response wrong. This taxonomy is the anchor.

---

## 4. Bill-visible artefact integration (one architecture on the existing bill standard)

D4's non-negotiable (register, verbatim): these are **bill-visible artefacts — statement
lines, reward balances, discounted-window tariff structures — NOT marketing copy**, and
their cost is a **real P&L line**. The design rule is therefore **one architecture on the
existing bill standard, not a parallel loyalty ledger**.

The real existing bill artefact model, verified against code:

- **`company/billing/dual_fuel_bill.py`** — `DualFuelBill` (the unified per-period statement,
  one account, up to two fuel legs) composed of `FuelBillSection` per fuel. `FuelBillSection`
  already carries `unit_rate_pence`, `energy_charge_gbp`, `standing_charge_gbp`, `levies_gbp`,
  `subtotal_gbp`, `vat_gbp`, `total_gbp`. **This is where mechanic shape (a)** — the
  discounted-window tariff structure — **lands**: a time-banded unit rate flows through the
  *existing* `energy_charge_gbp`, no new artefact type.
- **`company/billing/account_adjustment_register.py`** — `AccountAdjustmentRegister` /
  `AccountAdjustmentRecord`, the existing one-off credit/debit mechanism, already
  double-entry-ledger-integrated, with an `AdjustmentType` enum
  (`GOODWILL`, `BACK_BILLING_CREDIT`, `MISSED_DISCOUNT`, `COMPLAINT_REMEDY`,
  `REGULATORY_REDRESS`, `DEBT_WRITE_OFF`, …) and `AdjustmentDirection.CREDIT`. **This is the
  natural home for shapes (b) redemption and (c) event payout** — a reward redemption is
  structurally an account credit that must flow through the same ledger.

**Named BUILD gaps (not fabrications, stated honestly):**

1. **No reward/loyalty `AdjustmentType` exists today** — the enum has no
   `LOYALTY_REWARD_CREDIT` / `POINTS_REDEMPTION` / `FLEX_EVENT_PAYOUT` member. BUILD adds the
   member(s); it does **not** build a second ledger. This keeps every reward credit inside
   the existing approval-tier and double-entry discipline (real suppliers must — reward
   credits are redress-adjacent under Consumer Duty, §6).
2. **No reward-balance field on the bill artefact** — `FuelBillSection` / `DualFuelBill`
   carry no accrued-points / cash-equivalent-reward balance. Shape (b) needs an accruing
   balance the customer sees *before* redemption. BUILD adds this to the account/bill
   artefact (simplest construct — a field, not a loyalty platform, §6).
3. **No event-scoped statement line for shape (c)** — a bounded, dated, event-referencing
   line is a new statement-line kind; today the bill leg is a whole-period aggregate. BUILD
   decides whether this is a sub-line on `FuelBillSection` or an adjustment referencing the
   event.

These three gaps ARE D4's L1→L2 BUILD scope. Naming them here makes BUILD a translation
exercise onto a named, hardened bill standard, not a greenfield loyalty design.

---

## 5. The COUPLED-TRIAD gap (A6 — the load-bearing bit)

D4 is a **COMPANY-lane capability** that exists precisely to carry persuasion load **where
C4's bother-threshold `τ_i` is NOT cleared by objective £ alone**. In C4's four-parameter
model (`docs/design/frame/C4_adoption_physics_FRAME.md` §1), **reward responsiveness `ω_i`**
is "what carries the persuasion load... precisely where `τ_i` is uncleared by the objective
£ alone." **D4's mechanics ARE what C4's `ω_i` responds to** — the points, discounted-window
structures, and free-power events of §3 are the concrete stimulus whose perceived value
enters C4's composite decision as the `uplift(ρ_i, ω_i)` multiplier.

**The coupled pair:** `D4_loyalty_incentive_billing` (COMPANY leg — the belief `b`: the
company's fitted model of which mechanic moves which segment) ↔ `C4_adoption_physics` (SIM
leg — the hidden truth `θ`: per-customer `τ_i`, `ω_i`, and the true reward-response shape).

**The belief-vs-truth GAP the harness will eventually measure:** the company must **DISCOVER
reward-response through observed billing/engagement outcomes** — realised redemption rates,
window-participation rates, retention deltas visible in its own book — and is **allowed to
misjudge it**. It **CANNOT read the SIM-side per-customer `ω_i` / `τ_i` directly** (§6). A
naive "everyone loves points" assumption is exactly the belief the coupled test must be able
to defeat: a population whose reward-response is segment-varying and partly negative (reward
fatigue, gamification distrust, Consumer-Duty-relevant vulnerability harm) should make a
naive uniform-uptake belief measurably wrong. Per `COUPLED_TRIAD_DESIGN.md`: **no world/SIM
atom reaches L3 until the company's been tested against it, and D4 is not complete until it
has faced a population whose reward-response defeats the naive assumption.** `gap→0` (perfect
recovery of individual `ω_i` from aggregate billing behaviour) would be structurally
unreachable and a **wall DEFECT if seen**, not a triumph — the same reading convention as
every other coupled pair.

**Registration gap (named, not fixed — F1/no-code):** `background/coupled_triad.py::
_AUTHORITATIVE_COUPLING` today maps only `W2_x → C_x` pairs; it has **no `D4 → C4` entry**
(same class as the `C4 → C5` and `W1_5 → C13` gaps already named in their FRAMEs). Because
D4↔C4 is a **within-arc COMPANY↔SIM coupling that crosses lanes** (`D_billing_metering` ↔
`C_customer_ops`), BUILD must register it explicitly; this FRAME names it as a BUILD-time
task, does not touch the code.

---

## 6. Epistemic wall, portability, scale

**Epistemic wall (explicit).** The company sees its **own bills, payments, reward
redemptions, and engagement events** — never SIM churn/adoption internals.

| Company CAN observe (through the wall) | Company CANNOT observe (SIM-internal) |
|---|---|
| Its own bill-visible reward artefacts and their realised uptake (redemptions, window participation, points accrued/burned) | Any individual customer's `ω_i` reward-responsiveness or `τ_i` bother-threshold (C4 L3 ground truth) |
| Aggregate/segment retention and engagement deltas within its own book after a mechanic is offered | The counterfactual — whether a customer stayed *because of* the reward or would have stayed anyway |
| The real P&L cost of each mechanic (foregone margin, accrued liability, event payout) from its own ledger | The true segment-varying reward-response shape as ground truth — only its own book's realised outcomes |

**Portability (C-S*, SIMPLICITY GUARD).** A reward is a **bill-visible artefact TYPE, not a
bolt-on** — product-as-first-class per the portability constraints: a second product's
rewards fit inside the same bill brain (new artefact type / new `AdjustmentType`, no new
billing engine). **Idempotent reward crediting** (C-S2): applying a redemption twice is
harmless — the adjustment register's apply/reverse discipline already provides this; BUILD
must not add a reward path that bypasses it. **Simplest construct:** a reward-balance field
and an `AdjustmentType` member, NOT a loyalty-platform cathedral — the existing bill/ledger
already provides the seam.

**Consumer Duty two-sidedness** (register, verbatim, carried from C4 §6): gamified incentives
and free-power-event pressure have real mis-selling / vulnerability edges — reward mechanics
must be visible to the compliance organs at BUILD time, not modelled as pure upside. This is
why reward credits must flow through the *existing* approval-tier'd adjustment register (§4),
not a side ledger.

---

## 7. The single BUILD-unblock gate

| Atom | Epoch | Level (held) | BUILD-unblock gate | Gate class |
|------|-------|--------------|--------------------|------------|
| `D4_loyalty_incentive_billing` | 4 | **0 (→2)** | **BOTH** (a) **Epoch-4 BUILD-open** (TWIN, standing approver per EPOCH_GATING §3a) AND director "do not start" lifted, AND (b) **`C4_adoption_physics` reaching the level D4 needs** for it to be meaningfully built — C4 is currently **0/2 `idle`**, an UNMET prerequisite (D1_bill_correctness at 3/3 `harden` is MET). Once both hold, BUILD: (i) adds the reward `AdjustmentType` member(s) and reward-balance field on the *existing* bill artefact (§4 gaps 1–2); (ii) implements the three mechanic shapes (§3) — discounted-window tariff band, points→credit, event-scoped line; (iii) registers the `D4 → C4` coupling in `_AUTHORITATIVE_COUPLING` (§5); (iv) faces a population whose segment-varying reward-response defeats a naive uniform-uptake belief (coupled test, §5). | DIAL (epoch sequencing) **+ real unmet dependency** (C4) |

**Honest distinction from C4's FRAME:** C4's only block was the epoch gate (its deps were all
met). **D4's block is genuinely two-part** — the epoch gate *and* an unmet prerequisite (C4
at 0). This is not a reason to hold at a wall (Rule 0): DISCOVER/FRAME on D4 is available
now and this FRAME completes it; only BUILD is gated.

**Disposition:** level **HELD at 0** (idle atom; FRAME complete ≠ built; epoch-gated +
prerequisite-gated). This FRAME is D4's canonical terminus; the next idle draw reads D4 as
frame-saturated and yields to genuinely-un-FRAMEd work instead. No BUILD code, no map edit
(F1).

---

*Sources consolidated (not re-derived): D4's own inline DISCOVER simplifications
(`docs/design/maturity_map.yaml`, 2026-07-11 registration + 2026-07-12 four-scheme pass —
Octoplus ~£300/yr ≈ 17% of bill, EDF Sunday Saver, British Gas PeakSave, Scottish Power
Power Saver), `docs/staging/done/ADOPTION_JOURNEY_REGISTER.md` (scope, placement, "do not
start"), `docs/design/frame/C4_adoption_physics_FRAME.md` (`τ_i`/`ω_i`/composite decision,
coupled-gap reading convention), `docs/design/COUPLED_TRIAD_DESIGN.md` (gap-formula family).
Bill artefact model named from live code: `company/billing/dual_fuel_bill.py`
(`DualFuelBill`/`FuelBillSection`), `company/billing/account_adjustment_register.py`
(`AccountAdjustmentRegister`/`AdjustmentType`). Coupling table checked live:
`background/coupled_triad.py::_AUTHORITATIVE_COUPLING` (no D4→C4 entry — named BUILD gap).
Levels verified live against the map (C4 0/2 idle, D1 3/3 harden); the ~£300/yr figure is
carried from DISCOVER, not re-verified here; exact per-mechanic P&L numbers remain shapes,
not settled numbers, flagged for BUILD (R10).*
