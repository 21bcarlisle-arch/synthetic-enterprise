# Engagement mix — Ofgem-anchored reconciliation + curriculum proposal (Spec 006 finding F3 / battery 6-9)

**Provenance.** proposal · DISCOVER→FRAME · **doc-only** · **NO level claimed** · edits no `sim/`/`simulation/`/`company/`/`saas/`/`site/` code and no `maturity_map.yaml`.
**Trigger.** Director console ruling (2026-07-22): *"Engagement mix (ACTIVE 0.48 vs the board's 'disengaged majority'): do NOT adopt either side blind. Verify the cited 2025 Ofgem series first — which definition of 'active' it measures — and reconcile the board's veteran claim against that anchor. Then propose the curriculum value with both sources cited; the final number is my R13 call."*
**Standing rule.** R13 — the engagement mix is a **curriculum** constant, director-reserved. This doc **verifies, reconciles, and proposes**. It does **not** set the number and changes no share.

---

## 0. The three quantities in play (this is the whole reconciliation)

The word "active" means a **different thing** in each of the three sources. The apparent numerical
agreement (SIM 0.48 ≈ Ofgem 45.1%) is partly **coincidental** — they are not measuring the same object.

| Source | "Active" means | Type of measure |
|---|---|---|
| **SIM** (`simulation/household_segments.py:52-62`) | `ACTIVE` archetype = a household that **shops around ~every renewal** (durable per-tenure propensity; drives `active_renewal_probability = 0.65`) | **Behavioural / flow** — a lifetime switching *disposition* |
| **Ofgem RMI Oct 2025** | Account **currently sits on an actively-chosen (non-default) tariff** at the snapshot date | **Stock / point-in-time** — current tariff *state*, not history |
| **Board veteran claim** (Spec 006 §2 #4) | "Disengaged default-tariff loyalists are **the majority of any real book**" | A *shape* claim about the book |

A household can be on an actively-chosen fixed tariff **right now** (Ofgem-active) yet be a PASSIVE
archetype who switched once two years ago; conversely an ACTIVE archetype sitting between fixes shows up
as Ofgem-default. **Stock ≠ disposition.** Keep this seam in view for the whole proposal.

---

## 1. VERIFY — the cited 2025 Ofgem series and its definition of "active"

**The series the SIM's recalibration flag cites** (`household_segments.py:32-40`, `ASSUMPTIONS.md` line 116):
**Ofgem Retail Market Indicators data portal**, the *"Number of domestic customer accounts by supplier …
on default tariffs"* panel (ofgem.gov.uk/energy-data-and-research/data-portal/retail-market-indicators),
**as of October 2025**, fetched 2026-07-08. Non-prepayment **domestic** accounts.

**Its numbers, verbatim from the register (not re-fetched — no-network run):**

| | Actively-chosen | On default tariff | of which held **3+ yr** (clearly disengaged) | of which held **<3 yr** (recently defaulted / churning middle) |
|---|---|---|---|---|
| **Electricity** | **45.1%** | **54.9%** | **20.3%** | **34.6%** |
| **Gas** | **45.4%** | **54.6%** | **23.1%** | **31.5%** |

**Definition of "active" this series measures:** a **point-in-time stock** — "the account is on an
actively-chosen tariff on the snapshot date." It is **not** "switched more than once" and **not** a
behavioural disposition. Critically, Ofgem **does not equate "default" with "disengaged"**: it splits the
54.9% default majority into a **clearly-disengaged** 3+-year tail (20.3%) and a **churning middle**
(34.6%, <3 yr) that defaulted recently — post-fix rollers, SoLR placements, price-crisis fallbacks.

**Regime caveat (R13-critical).** This is a **post-crisis snapshot**. The active share is strongly
time/regime-dependent (`svt_rates_active_passive_2016_2025.md` §2–3): ~35% actively-renewing in the
steady 2016–20 window → **collapsed to ~10% fixed / ~90% SVT** at the 2023 crisis trough → recovered to
~one-third fixed by Jul 2025 → ~45% chosen by Oct 2025. **A single static engagement constant is itself a
simplification of a swing of 35 points.** Which regime the baseline represents is a director call in its
own right (see §4, Q-B).

---

## 2. RECONCILE — the board's veteran claim against that anchor

**The board's instinct is DIRECTIONALLY CORROBORATED by the hard series** — but its **strong form overshoots.**

- ✅ **"Most of the book is not actively shopping" is TRUE.** Default-tariff share = **54.9%** (elec) /
  **54.6%** (gas) — a genuine majority on the hard Ofgem number. The veteran is right that the median
  customer is a default-tariff sitter, not a shopper.
- ⚠️ **"Disengaged *majority*" overshoots if "disengaged" means the hard core.** Ofgem pins the
  *clearly-disengaged* (3+ yr default) cohort at only **20.3%** (elec) / **23.1%** (gas) — **not** a
  majority. The 54.9% default majority is **mostly the churning middle** (34.6% held <3 yr), not
  hard-core loyalists. The board's rhetorical "majority" conflates *on-default-right-now* with
  *permanently-disengaged*; the data separates them.

**Where the SIM sits vs the Ofgem stock split (mapping the three archetypes onto the three tariff-states):**

| | SIM share | Ofgem RMI (elec) closest analogue | Δ (SIM − Ofgem) |
|---|---|---|---|
| ACTIVE | **0.48** | actively-chosen **0.451** | **+3 pts** (SIM slightly high) |
| PASSIVE | **0.23** | default <3 yr (churning middle) **0.346** | **−12 pts** (SIM under-weights the middle) |
| DISENGAGED | **0.29** | default 3+ yr (clearly disengaged) **0.203** | **+9 pts** (SIM over-weights the hard core) |

So the SIM currently **over-weights both extremes and hollows out the churning middle** — the opposite of
the board's picture in one respect (it has *too many* hard-disengaged, not too few) and consistent with it
in another (default-tariff sitters, PASSIVE+DISENGAGED = 0.52, are already a slim majority).

**Internal-consistency flag (worth the director knowing).** The SIM's ACTIVE proxy ("~48% switched more
than once", `household_segments.py:19`) is in tension with its **own** cited anchor
(`svt_rates_active_passive_2016_2025.md` §2): the 2018 Consumer Engagement Survey is recorded there as
"**60%+ switched once or never**." The 0.48 ACTIVE share looks **inflated even against 2018**, before any
2025 argument. This is a second, independent reason 0.48 is the shakiest of the three shares.

---

## 3. VERDICT — neither side blind

- **Adopt the board's number blind?** No — its strong "disengaged majority" is not supported (hard-core = 20%, not >50%).
- **Adopt the Ofgem 2025 number blind?** No — it is a *stock* snapshot of a *post-crisis recovery* regime, measuring a different object than the SIM's behavioural archetype, and a single static baseline can't be "the" 2025 number without a regime decision.
- **The honest synthesis:** the **default-tariff cohort is a majority (both sources agree), but the hard-disengaged core is ~20%, not a majority.** The SIM's error is not "too few disengaged" — it is **too few in the churning middle (PASSIVE)** and **too many at both poles.**

---

## 4. PROPOSE — curriculum value (director's R13 call; NOT applied)

Two decisions gate the number. Recommendations are flagged; the choice is the director's.

**Q-A — semantics.** Keep the SIM archetype as a **behavioural disposition** (shops ~every renewal — this
is what drives the churn physics), and treat the Ofgem **stock** split as the external **anchor for the
shares**, not as a redefinition of the archetype. *Recommend: yes* — the behavioural archetype is load-bearing
for churn/revenue; don't collapse it into a stock measure just because the two numbers rhyme.

**Q-B — regime.** Is the baseline a **single static mix** or a **curriculum-timed schedule**? The real
active share swung 35 → ~10 → 45 across 2016–25. *Recommend, as the smaller reversible step first:* keep a
**single static behavioural mix representing the pre-crisis steady state** (the regime the baseline mostly
runs), and log "regime-timed engagement schedule" as a **named candidate curriculum scenario** for later —
not a silent parameter.

**Candidate static mix** (electricity, re-anchored to the Ofgem RMI Oct 2025 three-way stock as the closest
external three-cell anchor, honouring **both** sources without collapsing either):

| | current | **candidate** | rationale |
|---|---|---|---|
| ACTIVE | 0.48 | **0.45** | ↓ to Ofgem actively-chosen 45.1%; also below the internally-inconsistent 48% |
| PASSIVE | 0.23 | **0.35** | ↑ to Ofgem default-<3yr 34.6% — fills the hollow churning middle |
| DISENGAGED | 0.29 | **0.20** | ↓ to Ofgem clearly-disengaged 20.3% — the honest hard-core size |

**Why this honours both sides:** DEFAULT-tariff cohort = PASSIVE + DISENGAGED = **0.55**, a **genuine
majority** → the board's veteran instinct is satisfied. Hard-DISENGAGED stays at the honest **0.20** → the
Ofgem number is respected and the "disengaged *majority*" overshoot is not baked in. Neither adopted blind.

**Consequence check — near aggregate-neutral (important).** Re-basing shares would normally break the
module's artificial ~35%-aggregate preservation, which the file flags as "a separate, larger decision." It
does **not**, for this candidate: with the *existing* per-archetype renewal probabilities (0.65 / 0.15 /
0.02),

    0.45×0.65 + 0.35×0.15 + 0.20×0.02 = 0.2925 + 0.0525 + 0.0040 = **0.349**

vs the current **0.352**. The aggregate active-renewal rate barely moves (−0.3 pt). **This candidate fixes
the within-book *shape* (board realism) with negligible churn/revenue disturbance** — it re-distributes
heterogeneity without re-levelling the portfolio. That makes it a low-risk R13 move if the director wants one.

**The separate, larger lever (flagged, not proposed).** If the director also wants the **aggregate
active-renewal rate itself** to rise toward the ~45% recovery regime (not just the within-book shape), that
means re-tuning the per-archetype probabilities upward — a broader churn/revenue recalibration, and a
distinct R13 decision. **Per R12 (anti-goal-seek), this doc does not push the aggregate toward 45%** — the
figure is a diagnostic, not a target; surfaced for his decision only.

---

## 5. Sources (both cited, per the ruling)

1. **Board veteran claim** — `docs/staging/done/BOARD_SPEC_006_SEGMENTATION_2026-07-22.md` §2 segment #4
   ("Disengaged default-tariff loyalists — the majority of any real book"); reconciled in
   `docs/design/BOARD_SPEC_006_RECONCILIATION.md` (coverage #4, F3, battery 6-9).
2. **Ofgem Retail Market Indicators data portal**, "default tariffs" panel, as of **October 2025**
   (non-prepayment domestic): elec 45.1% chosen / 54.9% default (20.3% 3+yr, 34.6% <3yr); gas 45.4% / 54.6%
   (23.1%, 31.5%). Recorded `docs/market_research/ASSUMPTIONS.md` line 116 (fetched 2026-07-08).
3. **Regime context** — `docs/market_research/svt_rates_active_passive_2016_2025.md` §2–3 (35% steady →
   ~10% crisis trough → ~45% Oct-2025 recovery).
4. **SIM current state** — `simulation/household_segments.py:52-73` (shares 0.48/0.23/0.29; per-archetype
   renewal 0.65/0.15/0.02; ~35% aggregate preserved); older-source proxy = Ofgem Consumer Engagement Survey
   2018 (`svt_rates_active_passive_2016_2025.md` §2).

**Handoff:** awaiting the director's R13 number (or "keep static pre-crisis / go regime-timed" on Q-B). On
his word, the share change is a one-line edit to `ENGAGEMENT_POPULATION_SHARE` with the aggregate-neutrality
above holding the per-archetype probabilities fixed — a granted-turn BUILD, not done here.
