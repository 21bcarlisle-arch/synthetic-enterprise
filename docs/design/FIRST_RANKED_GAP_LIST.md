<!-- DISCOVER artefact — GAP3. Applies the DIRECTOR-RATIFIED GAP2 method (docs/design/GAP_TRIAGE_AND_RANKING.md)
to the live 8-register enumeration (per the GAP1 contract, docs/design/GAP_REGISTER_MINT_SOURCE_CONTRACT.md).
The `mint` classifications are AUTONOMOUS (§2 amendment: moves toward mint are autonomous). The
`deliberate-and-staying` PROPOSALS are HELD and RETURN FOR DIRECTOR RATIFICATION (§2: into-moves return,
batched via GAP-M2). This doc PROPOSES; it self-enacts no closure. -->
# First Ranked Gap List (GAP3 — ratified method applied to the live registers, 2026-07-28)

**Serves:** `DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28` §2–§3 + `DIRECTOR_RULING_GAP_TRIAGE_RATIFIED_2026-07-28`
deliverable 1. **Method:** GAP2 (director-ratified §1). **Enumeration:** the live 8-register OPEN residue
(the GAP1 reader BUILD-half is still `blocked_on director_build_open`, so this pass enumerated the
registers directly, read-only).
**Mint:** `PLANNER_MINTED_first_ranked_gap_list_2026-07-28`.

> **R12 — restated and binding on this whole document.** The counts below are a **diagnostic**, never a
> score, target, or headline. No gap was reclassified to move a count. A gap left honestly open with a
> better-measured bound is a *good* outcome. The value of this list is the **order of the mint set** (what
> to work next) and the **honest disposition** of the rest — not "N gaps found/closed".

---
## 0. Two enumeration findings that change the contract (net-new — both are R15 FAIL-OPEN risks)

The register scan surfaced **two ways GAP1's reader contract, as written, would fail-open** — i.e. a
built reader would report an EMPTY residue while open rows demonstrably exist, the exact tautology/fail-open
GAP1's own invariant 1 forbids. These are the highest-value net-new gaps this pass produced:

1. **Register 1 keys on a field that does not exist.** The OPEN rule is "carries no `measured_bound`",
   but `maturity_map.yaml`'s `simplifications:` entries are **plain free-text strings (621 across 146
   atoms), zero structured `measured_bound` fields**. The list has also grown ~4× past the contract's
   stated "157" — it is now an append-only dated FRAME/HARDEN **log**, not a bounded-simplification
   declaration list. A reader keying on `measured_bound` reads **all-open or all-closed** depending on
   impl — never the true residue. → **MINTED** as `PLANNER_MINTED_gap1_reader_contract_failopen_fix_2026-07-28`.
2. **Register 6 keys on the wrong prefix.** The contract keys standing sanity findings on `audit:*`, but
   the **15 adjudicated-real** findings live under `coldwalk:` / `expert_hour:` / `harden_sweep:` /
   `population:` prefixes; the 9 `audit:*` rows are only false-positive or un-adjudicated. A reader keying
   on `audit:*` **misses all 15 real findings** (fail-open). → folded into the same mint (both are the
   GAP1 reader-contract correction).

These are **`mint`** (autonomous — a fix, not a red-retirement). The GAP1 reader BUILD half stays
`blocked_on director_build_open`; correcting the *contract* (doc) is drawable now and is the minted atom's
DISCOVER half.

---
## 1. Classification — every register's residue lands in exactly one bucket

### `blocked-on-director` (walls dominate — escalated as `[ACT]`, never worked around)
| Rows | Why reserved |
|------|--------------|
| **6 fidelity-ledger SSP-baseline cells** (`W1_6_physics_price_signal::ssp_*`, all `commercial_weight=1.0`, lift ≤ 0) | R13 baseline is director-reserved + a **known, ruled** red (`ssp_scarcity_form_calm_low_x_underfit_bounded`, director 2026-07-19 console steer ranks calm-year MAE below spike-tail). Reading these as `mint` re-opens a settled R12 goal-seek trap (GAP2 argue-back). |
| **`SPINE_2_launch_worlds`** (register 8) | R13 — the three launch worlds' ratified parameter VALUES are the director's curriculum. |
| **MODEL_ON_A_PAGE Timeframe-2 roadmap sequencing** (register 7, 6 lines) | Epoch-advance is director-gated. The *lines* are sequenced next-epoch roadmap, not agent scope-choices — deferring them is a director sequencing decision. (Individual sub-capabilities drawable NOW as DISCOVER/FRAME are not blocked — see the mint set.) |
| **Existing idle map atoms behind an epoch/front gate** — `E5_carbon_three_ledger` (L0, the £/tCO₂e mission headline), gas-storage stock-and-flow (`SPEC_004` item 6, = `SPINE_3`), outage/interconnector tail (`SPEC_004` item 11, = `SPINE_5`), retail-gas hedging, collateral→cash death-loop | Already registered atoms; their BUILD is epoch/front-gated. GAP3 **ranks** them (below) but they need a director **front/epoch open**, not a new mint (R16: agent cannot self-open a front). |

### `deliberate-and-staying` — **PROPOSED, HELD, RETURNS FOR RATIFICATION** (§2 into-move, batched via GAP-M2)
Per GAP2(iv) a simplification stays deliberate only if **argued + measured-bound + faced-or-scheduled**.
Because the `simplifications:` register carries **no measured bounds** (finding 0.1), *almost none* of the
621 entries currently satisfy the test — an unmeasured simplification is `mint` (measure it), not
deliberate-and-staying. So this PROPOSED set is deliberately **small** and each carries its own argument;
the director ratifies (or rejects) each move into this bucket:
- **LPG/bottled-gas depth** (`W2` population) — thin by design; argued out-of-scope this epoch (mains
  gas + electricity are the product). *Bound to be measured before ratification.*
- **Single-geography / single-currency** — portability *constraint* honoured, second geography not built
  (PORTABILITY_DESIGN_CONSTRAINTS, director-approved standing constraint). Argued; already director-owned.
- **`payment_observation_consumer` "deliberately not wired"** (register 5) — an honestly-labelled sensing
  organ, not a surface-claim defect; argued deliberate.

> These are **PROPOSALS**. The agent does **not** move any row into `deliberate-and-staying`; GAP-M2's
> batched path returns them to the director. Until ratified, each stays in its prior bucket (`mint` for
> the unmeasured ones).

### `not-worth-the-complexity` — honest reds below threshold, with a better bound
- **`sim_interface.py` abstract `NotImplementedError` seam methods** (register 5) — an abstract base-class
  seam, not a claim defect; the "gap" is by-design abstraction. Bound: zero live-surface claim depends on
  them. Honest red, credited, not minted.
- The bulk of the **~479 dated FRAME/HARDEN log entries** in register 1 that carry an inline numeric note —
  these are progress-log lines, not un-triaged gaps; better bound = they are *records*, not simplifications.
  (This is why finding 0.1's contract fix matters: the register must separate the log from true
  simplifications so the residue is real, not inflated.)

### `mint` — worth closing (autonomous), RANKED in §2

---
## 2. The ranked `mint` set (composite = fidelity + mission + board-battery + blast-radius − cost; PRODUCT-FIRST guard)

**PRODUCT-FIRST (§ amendment D):** product-lane atoms keep precedence; machinery (`H_harness`) gaps rank
among themselves **below** product, never outranking product on composite alone. Board-battery weight = 3
(a practitioner-named "not credible" item) mints **regardless** of composite (credibility is not tradeable).

### Product lane (ranked)
| # | Gap | Bucket evidence | Scoring rationale | Disposition this tick |
|---|-----|-----------------|-------------------|----------------------|
| P1 | **`E5_carbon_three_ledger` → £/tCO₂e on the front page** | register 5 (L0) + register 7 line 5 + RC7 FRONT_MISSION_BLOCK | mission = **3** (the company's reason to exist), fidelity high, blast-radius high | **already an atom, BUILD epoch/front-gated → `blocked-on-director` (needs front open).** Ranked #1 product; no new mint (R16). |
| P2 | **Real customer/billing defects, adjudicated-REAL** — margin-reconciliation portfolio-vs-ledger, cost-to-serve cross-fuel mismatch (same household), bad-debt implausibly low through 2021-22 crisis, payment-channel DD-fail contradiction, ledger double-entry (`E1`), `unit_rate_vs_cap_band` violations (`C1g:2019`,`C4:2024`) | register 6 (15 adjudicated-real) | fidelity + board-battery (credibility), mission ≥ 2 (customer truth) | **existing sanity findings; several already have remediation atoms** (bad-debt bridge, payment grid). Ranked; verify-then-mint only the un-covered ones in a future tick (avoid duplication). |
| P3 | **No privacy-policy page** (customer-facing legibility/credibility) | register 6 `coldwalk:no_privacy_policy_page` (adjudicated-real) + SPEC_005 credibility | cost = **S** (cheap), blast-radius low, credibility real, product/site-lane | **MINTED** `PLANNER_MINTED_privacy_policy_page_2026-07-28` (SITE lane, L2, autonomous). |
| P4 | **Effective-temperature demand blend + warming trend** | SPEC_002 battery `7.3`/`7.7` (ABSENT, "not credible") → **weight 3** | demand fidelity; board-battery 3 ⇒ mints regardless | existing WORLD-lane scope (`SPEC_002` reconciliation); ranked, front-gated. |
| P5 | **Gas-storage stock-and-flow** (`= SPINE_3`) | SPEC_004 item 6 ("the largest gap", ABSENT) → **weight 3** | fidelity = 3, mission ≥ 2, cost = **XL** | existing atom, epoch-gated → `blocked-on-director`. Ranked #high; needs front/epoch open. |
| P6 | **Outage / interconnector tail** (`= SPINE_5`) + **stochastic outage process** | SPEC_004 item 11 (ABSENT, "not credible") → **weight 3** | tail-risk fidelity; cost = L | existing atom, epoch-gated. |
| P7 | **Domestic void / holiday / tenancy state events** | SPEC_003 battery `5.3` (ABSENT) | population fidelity; some covered by `W2_12/W2_13` (authored DISCOVER atoms) | ranked; partly registered. |

### Machinery lane (`H_harness`, ranked among themselves — below product)
| # | Gap | Evidence | Disposition this tick |
|---|-----|----------|----------------------|
| M1 | **GAP1 reader-contract fail-open fix** (register-1 `measured_bound` + register-6 prefix keying) | finding §0 — both are R15 fail-open | **MINTED** `PLANNER_MINTED_gap1_reader_contract_failopen_fix_2026-07-28` (highest machinery value: without it the whole backlog-reader reports empty while open). |
| M2 | **Stop control** ("no stop control at all — material safety gap") | SPEC_005 `7.13` (ABSENT, **material safety**) → weight 3 | safety-adjacent; ranked top of machinery. Existing governance scope — verify against the current run-hold/kill controls before minting (may already be partly covered). |
| M3 | **Public challenge channel** (`7.8`) + **delta view** (`7.10`) | SPEC_005 battery ABSENT | governance/legibility machinery; ranked. |
| M4 | **F3 obligations register + profitable-desk alarm in CODE** (not doc-only) | WHOLESALE `8`/`10` (FAIL) = Director Finding F3 | existing F3 finding; ranked, front-gated. |
| M5 | **BOARD_SPEC_001 reconciliation — publish the missing file** | register 3 (no `001` reconciliation exists) | net-new, cheap (M); ranked, mint in a future tick. |
| M6 | **Simplifications register: add a structured `measured_bound` field** (split the log from true simplifications) | finding §0.1 (data model) | enables the whole coupled-triad bound-tracking; folded into M1's DISCOVER scope. |

---
## 3. Enumeration diagnostic (R12 — diagnostic only, never a score)

| # | Register | OPEN residue | Dominant disposition |
|---|----------|-------------|----------------------|
| 1 | Deliberate-simplifications | 621 strict / ~177 no-bound | mostly log-lines (`not-worth-it` / contract fix M1+M6); true unmeasured simplifications → `mint` (measure) |
| 2 | Fidelity ledger | 6 cells | `blocked-on-director` (all SSP HELD) |
| 3 | Board-spec 001–006 + Wholesale | 152–154 (42 ABSENT/FAIL) | mostly existing WORLD atoms; SPEC_001 file net-new (M5) |
| 4 | Disqualification battery | 51 (15 "not credible" weight-3) | the weight-3 items seed the mint set (P4–P6, M2–M4) |
| 5 | Claim-status placeholders | ~9–10 | E5 (`blocked-on-director`) + honest not-wired sensing organs (`not-worth-it`) |
| 6 | Standing sanity findings | 15 adjudicated-real (8 false-positive excluded) | `mint` (P2/P3), several already remediated |
| 7 | MODEL_ON_A_PAGE Timeframe-2 | 6 | `blocked-on-director` (epoch sequencing) |
| 8 | Registered follow-ons | 5 (SPINE_1–5) | SPINE_1 `mint`/front-gated; SPINE_2 `blocked-on-director`; 3/4/5 map to P5/P6 |

**Saturation is impossible while this residue is open** (the ruling's acceptance test): every register's
residue is non-empty. This list makes the residue *drawable and ordered*; it closes nothing.

---
## 4. What this tick actually enacts (bounded, honest)
- **Minted (autonomous, net-new, non-duplicate):** M1 (GAP1 reader fail-open fix) + P3 (privacy-policy page).
- **Ranked but NOT newly minted:** the existing epoch/front-gated atoms (P1, P4–P6, M4) → they need a
  director **front/epoch open** (R16), surfaced as `blocked-on-director`; the already-remediated sanity
  findings (part of P2) → verify-then-mint only the uncovered ones later (no duplication); M5 → future tick.
- **Returned for ratification (HELD):** the `deliberate-and-staying` PROPOSALS in §1 (batched via GAP-M2).
- **Nothing self-enacted into a closure.** The mint direction is autonomous (§2); the deliberate-and-staying
  direction is not.

## 5. Walls untouched
- **R13 / curriculum / generator ground truth:** SSP cells + launch-world values routed to
  `blocked-on-director`, never self-closed; no baseline or difficulty value moved.
- **R16:** no `level_current` moved; existing atoms needing a front/epoch open are escalated, not self-opened.
- **R12:** counts are diagnostic; no gap reclassified to move a count; no "N closed" headline.
- **§2 asymmetry:** `mint` moves autonomous; `deliberate-and-staying` moves HELD + returned.
