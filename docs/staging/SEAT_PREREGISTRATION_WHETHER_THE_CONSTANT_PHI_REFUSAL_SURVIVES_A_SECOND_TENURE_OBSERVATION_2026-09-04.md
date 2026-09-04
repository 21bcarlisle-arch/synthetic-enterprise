**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — whether the constant-φ refusal survives a second SVT tenure observation

A pre-registration, not a finding. The finding it serves is
`SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_COMPRESSED_NOT_MISDIRECTED_2026-09-03.md`,
which stays **BLOCKING**.

Filed 2026-09-04, before `tools/published_route_split.py` carries a second tenure observation and
before any verdict at a second mix has been computed by the module.

---

## Why this question, and why it is the one §13 named

§13 closed by naming its own binding weak input:

> *"the binding weak INPUT is now the single Ofgem CES 2018 tenure split, which is carried across
> nine years and is what separates a record that refuses constancy from one that admits it."*

and asked for exactly one thing:

> *"**a second tenure split for the SVT segment in any year other than 2018.** One more observation
> of that one quantity decides whether the record refuses a constant φ or admits 0.62–0.85 of one,
> and it is the highest-leverage sourcing question this chain has produced."*

**It is in the tree, and it was in the tree when §13 asked for it.** `docs/market_research/
ASSUMPTIONS.md` L176 and `docs/market_research/continuous_behavioural_engagement_w2_14.md` §1a both
carry Ofgem's Retail Market Indicators October-2025 stock split, cited, dated and fetched
2026-07-08, and the R13 ruling of 2026-07-22 turns on it. This is the fourth instance in this chain
of the shape §10 recorded — *"the sourcing's own first result: it was already in the tree, three
times"* — and this pre-registration is filed before the reading, not after it.

**The second observation is a better instrument than the first, not merely another one.** CES 2018
is a consumer survey and reports self-declared tariff type and tenure; RMI is supplier-returned
administrative stock. They disagree, and the disagreement is large.

---

## The three quantities, and what is hand-derived versus what is open

**HAND-DERIVED BEFORE FILING, AND DECLARED AS SUCH.** The two composed bands and the 2017/2018 and
2017/2019 crossings on `all_domestic` were computed with a calculator while designing the change. A
prediction filed after its answer is not a prediction, so they are recorded here as *derivations*
and only the module's agreement with them is being tested. Everything under "OPEN" below was not
computed in any form before filing.

| observation | instrument | within-SVT long-stayer share | composed band |
|---|---|---|---|
| Ofgem CES 2018 | consumer survey, self-report, all domestic | 29/(29+23) = **0.5577** | [0.09423, 0.14423] |
| Ofgem RMI Oct-2025, electricity | supplier stock returns, **non-prepayment** | 20.3/(20.3+34.6) = **0.3698** | [0.11302, 0.16302] |
| Ofgem RMI Oct-2025, gas (companion) | as above | 23.1/(23.1+31.5) = **0.4231** | not carried — `R` is electricity |

Observed-mix hull = [0.09423, **0.16302**]. Mix-free envelope, unchanged = [0.05, 0.20].

**A directional caveat that is part of the reading and not a footnote.** RMI Oct-2025 excludes
prepayment. `tools/published_tariff_mix` already establishes that >90% of prepayment customers are
on a default tariff, and prepayment is the segment least likely to have moved tariff recently, so
restoring it can only move the 2025 long-stayer share **up** — i.e. toward 2018's. **0.3698 is a
lower bound on the 2025 within-SVT long-stayer share**, and the composed band's upward shift is
therefore an upper bound on the shift. The hull is the wider of the two claims and is what the
verdict should be read at.

---

## The predictions

### P1 — the 2025-mix band REFUSES, and refuses harder *(direction hand-derived; the module's
### agreement, the as-published basis, and the minimal pairs are open)*

The band translates **up** by 0.018793 with its width unchanged, so each year's φ interval
translates **down** by `s(y)·0.018793 / ((1−s(y))·0.35)` — larger where the default share is larger.
2017's share (0.6195–0.6365 all-domestic) is above 2018's (0.5855), so 2017's interval falls further
than 2018's and the gap between them widens.

- **Predicted:** REFUSES on both bases over `fitted_years`. Hand-derived on `all_domestic`: 2017's
  high end 0.6290 → **0.5389**, 2018's low end 0.7620 → **0.6862**, crossing −0.133 → **−0.147**.
- **OPEN:** whether `as_published` also refuses; whether the minimal refusing pairs are still
  exactly {2017,2018} and {2017,2019}; whether any *new* pair joins them.

### P2 — the observed-mix HULL also REFUSES *(hand-derived on one pair; the binding pair is open)*

- **Predicted:** REFUSES on `all_domestic` over `fitted_years`. Hand-derived: at the hull 2017's
  high end is 0.6290 (the hull's low end is 2018's) and 2018's low end is **0.6862**, so the
  2017/2018 crossing is **−0.057** — narrowed by the widening, and still a refusal.
- **OPEN, and this is the substantive one:** whether 2017/2018 is the *binding* pair at the hull or
  whether 2017/2019 binds harder, what the overall crossing is, and whether `as_published` agrees.
  I have not computed 2019's low end at the hull.

### P3 — the mix-free envelope is UNCHANGED, byte for byte

Neither `SVT_CHURN_RECENT` nor `SVT_CHURN_LONG_STAYER` moves, so `mix_free_envelope` must still
ADMIT φ ∈ **[0.6178, 0.8503]** on `all_domestic` and **[0.6122, 0.7700]** on `as_published`. A
change here is a defect in the change, not a result.

### P4 — the constant-PAIR sweep is band-free and must not move

`_whether_any_constant_pair_admits_a_common_phi` sweeps `H` over [0, 0.40] and never reads a segment
band. **Predicted: identical** — 0 of 4,001 on both bases, widest slack −0.3093 (as_published,
H = 0.0685) and −0.3374 (all_domestic, H = 0.0542). This is the control on the change: if it moves,
the new bands have leaked somewhere they do not belong.

### P5 — the share series still cannot carry the record's steps at either new band *(OPEN)*

`dV = (s₂ − s₁)·(H_svt − 0.35φ)`, so the reachable interval scales with the band's span. The 2025
band has the **same** span as 2018's (0.05); the hull's is **38% wider** (0.0688).

- **Predicted:** 0 of 4 judged pairs carried at `tenure_composed_2025` and 0 of 4 at
  `observed_mix_hull`, on both bases — i.e. §13's headline result survives the widening.
- **Predicted, and the narrowest margin:** 2018→2019 — the step §12's disjoint intervals turn on —
  reached at most 0.44pp against a required 0.70pp at the 2018 mix. At the hull I predict its
  maximum reach lands in **0.55–0.70pp** and stays **short**. If it exceeds 0.70pp this prediction
  is refuted and the "the movement is behavioural, not composition" claim needs qualifying at the
  hull.
- **Predicted:** the two pairs flagged `record_requires_a_move: false` (2023→2024, 2024→2025) are
  still flagged and still excluded from the denominator at the new bands.

### P6 — 2022's φ stays negative at both new bands

2022's interval is [−2.880, −0.463] at the 2018 mix. The hull shares that band's **low** end, so
2022's φ **high** end at the hull must be exactly −0.46264 again; the 2025 mix's low end is higher
still, so its high end must be **below** −0.46264. **Predicted: entirely negative at both**, and the
structural-break exclusion keeps its stated reason unchanged.

### P7 — §13's own handover sentence is REFUTED as posed

§13 said one more observation *"decides whether the record refuses a constant φ or admits
0.62–0.85 of one"*. **Predicted: it decides neither.** The record refuses at *both* observed mixes
and at every mix between them, and admits only at mixes **outside** the range anything has observed
— which relocates the admission from "the record might allow it" to "the record allows it only at a
tenure mix no instrument supports". If that holds, the interval [0.618, 0.850] is weaker evidence
after this reading than before it, and `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` has one more reason to
stay `None`.

### P8 — nothing in the world moves, and the diff proves it

`EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` stays `None`; `YEAR_LEVEL_ANCHOR` untouched; no solver aim point
moved; `emergent_level_verdict` still six of seven outside their bands. New band keys are appended
**after** existing ones so that every world-derived section of `docs/reports/
published_route_split.json` stays byte-identical and the artefact's diff is **insertions only** —
§4's constraint 4, a tenth time.

---

## What would make me wrong in an interesting way

If the hull ADMITS, then the refusal really was an artefact of one survey year, §13's sentence
stands, and the next question is a third observation rather than φ. I do not expect it and I have
written the reading so that outcome is reportable without editing anything: both branches of the
verdict are live in the same run today (the composed bands refuse, the mix-free envelope admits), so
a control cannot pass by freezing either polarity.

— Delivery seat, 2026-09-04, before the measurement.
