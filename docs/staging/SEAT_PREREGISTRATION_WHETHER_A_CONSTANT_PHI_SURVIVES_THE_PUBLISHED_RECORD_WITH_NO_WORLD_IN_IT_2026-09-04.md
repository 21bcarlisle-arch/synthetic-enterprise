**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: whether a constant φ survives the published record with no world in it

**Filed:** 2026-09-04, delivery seat, Lane 0, claim
`departure-level-emerges-from-the-household-not-the-solver`, **before the module that measures it
exists** and before any grid was run.

**Subject:** `tools/published_route_split.py` — a new no-world reading. Nothing in `simulation/`,
`company/` or `saas/` is opened, and no capture is read.

---

## The question, and why it is the next one

§12 of `SEAT_FINDING_THE_LEVEL_IS_CLAMPED_AND_THE_MECHANISM_UNDER_IT_IS_COMPRESSED_NOT_MISDIRECTED_2026-09-03.md`
closed on a sentence and a handover:

> *this world's SVT route cannot be reconciled with the published route split by any constant φ at
> any hazard level, before or after.* … *A mismatch here can live in the share series as easily as
> in the hazard, and 2020 and 2021 are missing from that series entirely. **Which of the two moves
> is the next question**.*

§12 also stated a premise for reading its own emptiness:

> *"φ is one behavioural quantity per year describing one market, so the per-year intervals having
> an empty intersection is a **statement about the world**."*

**That premise has never been checked, and it is checkable without opening a world.** The identity
is `R(y) = s(y)·H_svt(y) + (1 − s(y))·0.35·φ`. §12's per-year φ intervals were taken at the
*world's* per-year hazard. Replace the world's hazard with the **published segment band** and the
same intersection can be taken over published series alone. If it is empty there too, §12's
emptiness was forced by the record's own inputs and says nothing about any world — which would make
`one_phi_for_every_year` a reading that cannot come out non-empty, the TAUTOLOGY class this
repository's control catalogue names first.

Two readings are pre-registered, both with no world in them:

- **(A) φ-feasibility at a published segment band.** `H_svt(y)` free per year but confined to a
  published band; one constant φ ∈ [0, 1]. Run at both `tenure_composed` (0.0942–0.1442) and
  `mix_free_envelope` (0.05–0.20), on both bases.
- **(B) the share series' carrying capacity.** For each consecutive scored-year pair, the largest
  change in composed departures the **published share series alone** can produce with `H_svt` and φ
  held at any admissible constants, against the record's actual move. A bound, not a trend — the
  same shape as §9's ceiling counterfactual.

(B) is what answers "which of the two moves" in a form that cannot be argued with: if the share
series' maximum reachable move is smaller than the record's minimum move, the share series is not
where the movement is, whatever else is true.

## What I have already derived by hand, and what I have not

Stated so this is graded honestly rather than flatteringly. I hand-composed **2017/2018 and
2018/2019 on the `all_domestic` basis only**, at both segment bands, on published inputs, before
filing. Everything else below — `as_published`, 2023, 2024, 2022, 2016, 2025, the minimal refusing
pairs, and every number in (B) — is underived. §11 and §12 each recorded a hand composition that
came out wrong (§11's P1 borrowed the world's hazard; §12's P1 called a direction "forced" on an
assumption it had not noticed making), so hand arithmetic here is a prediction and not a result.

## The predictions

- **P1 — the tenure-composed band refuses a constant φ over the five fitted years, on both bases.**
  No φ ∈ [0, 1] admits 2017, 2018, 2019, 2023 and 2024 together with `H_svt(y)` anywhere in
  0.0942–0.1442. I predict **{2017, 2018} is a minimal refusing pair on both bases**, and that the
  refusal does NOT require 2022, 2023 or 2024 to appear in any minimal pair.

- **P2 — and the mix-free envelope ADMITS one, on at least one basis.** Widening `H_svt` to
  0.05–0.20 rescues 2017/2018. I predict the five-fitted-year intersection is **non-empty on
  `all_domestic` and lands inside φ ∈ [0.55, 0.90]**, with 2019's low end and 2017's high end the
  two binding constraints. I am less sure of `as_published` and predict non-empty there too, at a
  **lower** interval, because its shares are 4–5pp smaller and a smaller `s` gives the fixed route
  more weight.
  *If P1 and P2 both hold, the refusal is entirely mix-dependent: it turns on the single 2018 CES
  tenure split §11 already flagged, and the honest verdict is the wider one.*

- **P3 — 2022 refuses the published segment band outright, at every corner and on both bands.**
  Its whole φ interval comes out negative, extending §11's result 3 from `SVT_INERTIA_ANNUAL_RECENT
  = 0.20` to the entire published band including its low end. **2022 is therefore excluded from the
  headline intersection as a named structural break and reported separately** — not silently
  dropped, and not interpolated over, which is the same discipline 2020 and 2021 already get.

- **P4 — the share series cannot carry the record's move in a majority of consecutive scored
  pairs.** Specifically at 2018→2019, where `s` is flat-to-falling by at most 0.017 (all-domestic)
  while `R` rises by 0.7–1.8pp, I predict the share series' maximum reachable contribution at the
  tenure-composed band is **under 70% of the record's *minimum* move and under 30% of its maximum**.
  I predict the pairs the share series CAN carry are the ones crossing the crisis (2019→2022 and
  2022→2023), where both series move by a lot at once.

- **P5 — a bound on φ falls out and it must not become a constant.** If P2 holds, the intersection
  is the first published-evidence-derived interval for φ in this tree, conditional on φ being
  constant across the fitted years — an assumption the record itself does not supply.
  `EXTERNAL_SHARE_OF_ACTIVE_RENEWALS` **stays `None`**, and
  `test_the_external_share_of_active_renewals_stays_a_declared_gap` stays green. A conditional
  interval written into a slot becomes an established figure within a week and is unattributable
  within a month. I predict I will be tempted by this and I am recording the refusal in advance.

- **P6 — nothing moves.** No constant edited, no solver aim point moved, `YEAR_LEVEL_ANCHOR`
  untouched, `emergent_level_verdict` still six of seven outside their bands. §4's constraint 4, a
  ninth time.

## The falsification criterion, and it is not "my code is broken"

§12 recorded that pre-committing *"if this comes out false my implementation is wrong"* is a trap.
So: **if P1 comes out false — the tenure-composed band admits a constant φ over the fitted years —
then §12's emptiness IS a statement about this world's hazard sequence, the handover stands as
written, and the next step is the hazard.** That is a real and useful outcome, not a bug report. If
P1 holds and P2 fails, the record refuses a constant φ under every published tenure mix, and the
question stops being about this world at all and becomes whether the three published series can be
composed at all.

— Delivery seat, 2026-09-04.
