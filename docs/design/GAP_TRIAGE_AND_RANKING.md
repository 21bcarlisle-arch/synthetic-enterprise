<!-- DISCOVER artefact — GAP2. PROPOSE-THEN-RETURN-FOR-RATIFICATION. HELD: the agent does NOT self-apply this taxonomy to open/keep any gap until the director ratifies. -->
# Gap Triage & Ranking Method (GAP2 — proposed, returns for ratification)

**Serves:** `DIRECTOR_RULING_PUBLISHED_GAPS_ARE_THE_BACKLOG_2026-07-28` §2 (*"triage and ranking are
yours … propose the triage … state your reasoning and the evidence"*) + §3 (deliberate simplifications
stay deliberate; R12; reserved walls).
**Mint:** `PLANNER_MINTED_gap_triage_ranking_method_2026-07-28`.
**Status:** PROPOSAL. Escalated to the director as an `[ACT]` proposal and **HELD** — no gap is
opened, kept, closed, or reclassified under this method until the director ratifies it. GAP1 (the
contract) supplies the register schema; GAP3 (the ranked list) applies this method to the live residue
**after** ratification.

> **R12 up front (§2(v)):** the number of gaps closed is a **diagnostic**, never a score, target, or
> headline. This method orders which gaps are *worth minting*; it never optimises toward a gap-count.
> A gap left honestly open with a better-measured bound is a *good* outcome, not a failure.

---
## (i) Classification taxonomy — every enumerated gap lands in exactly one bucket

| Bucket | Definition | Test to land here | Disposition |
|--------|-----------|-------------------|-------------|
| **`mint`** | worth closing: closure raises real-world fidelity or credibility and is within a non-reserved lane | scores at/above the mint threshold (iii) **and** no reserved-wall dependency | mint a `PLANNER_MINTED_*` / map atom, ranked by (ii) |
| **`deliberate-and-staying`** | a *scope choice*, argued — closing it would add fidelity the model does not need at this epoch | passes the deliberate-and-staying test (iv): a written argument **and** a measured bound on the error it introduces | left open, **credited** (§3), carried in the simplifications register with its bound. Never silently fixed nor reclassified to closable. |
| **`blocked-on-director`** | closure needs a reserved-wall decision | touches a one-way door, R13 curriculum/difficulty value, generator ground truth, an L3 level, or the Epoch-4 fitness function | escalated as `[ACT]`, **never worked around**. Stays open until the director rules. |
| **`not-worth-the-complexity`** | an honest red — closure costs more than the fidelity it buys | argued cost > argued benefit, **and** a *better-measured bound* is recorded than the status quo | left open with the improved bound (an honest red, credited per §3). Distinct from `deliberate-and-staying`: this one *would* add fidelity but is not worth the blast radius/cost now. |

**Mutual exclusion + total coverage:** every enumerated gap resolves to exactly one bucket. Ambiguous
cases default toward **`mint`** (Rule-0 direction: work exists) **unless** a reserved-wall touch is
present, in which case they default to **`blocked-on-director`** (walls dominate). A gap that cannot be
argued into `deliberate-and-staying` or `not-worth-the-complexity` (no measured bound) is **not**
allowed to sit there by default — an unbounded simplification is `mint` (measure it) per GAP1 register-1.

## (ii) Ranking dimensions (order the `mint` set) — each scored 0–3, rationale + evidence required

| Dimension | What it measures | Evidence source |
|-----------|------------------|-----------------|
| **Fidelity impact** | distance from a naive baseline / real external benchmark that closure removes | fidelity ledger `lift`/`err_model` vs `err_naive`; Ofgem/Elexon/NESO anchor in `docs/market_research/` |
| **Mission relevance** | contribution to the £/tCO₂e story — the company's reason to exist (`[[project_rc7_idea_first_external_register]]`, FRONT_MISSION_BLOCK) | the mission surface / carbon ledger; is this on the path to the mission headline? |
| **Board-battery weight** | whether a practitioner said this makes the build *not credible* | disqualification-battery status in the board-spec reconciliations |
| **Blast radius** | how many surfaces/consumers the closure touches (a proxy for both value and risk) | consumer graph — who reads the artefact |
| **Cost-to-close** | effort/size to close (S/M/L/XL — R12/G5 DIAL: informs, never gates) | the atom's `size:` or a FRAME estimate |

**Composite:** rank by `fidelity_impact + mission_relevance + board_battery_weight + blast_radius −
cost_to_close` (cost subtracts — cheaper wins on a tie). Ties broken by mission relevance first
(product-first, `[[project_product_first_ruling]]`), then board-battery weight. The composite is a
**tie-breaker/diagnostic for ordering the mint set** (LAW A), never a promotion gate or a target.

**PRODUCT-FIRST guard (§ amendment D, 2026-07-28):** a machinery-lane (`H_harness`) gap may **not**
outrank a product-lane atom purely on composite score — product-lane atoms keep precedence
(`[[project_product_first_ruling]]`). Machinery gaps rank among themselves.

## (iii) Mint threshold — what makes a gap worth minting

A gap is minted iff **either**:
- **composite ≥ 6** (of a 0–15 positive range before cost), **or**
- **board-battery weight = 3** (a practitioner-named credibility blocker mints regardless of composite —
  credibility is not tradeable against convenience), **or**
- **fidelity impact = 3 AND mission relevance ≥ 2** (a large fidelity gap on the mission path mints).

Below threshold **and** with a recordable bound → `not-worth-the-complexity` (honest red). Below
threshold with **no** bound → `mint` at low rank (measure it — an unmeasured gap cannot be argued into
staying). This asymmetry is deliberate: the cheap outcome is *measuring* a gap, not *ignoring* it.

## (iv) Deliberate-and-staying criteria (the explicit test §3 turns on)

A simplification stays deliberate **only** if all three hold, else it is `mint`:
1. **Argued:** a written one-line reason it is out of scope for this epoch (in the atom's
   `simplifications:` note or a FRAME).
2. **Bounded:** a *measured* bound on the error it introduces (not "small" — a number, an interval, or
   a named worst-case), recorded in the simplifications register (GAP1 register-1).
3. **Faced-or-scheduled:** the coupled-triad rule — either the company has been tested against a world
   that could expose it and the gap measured, or an atom is registered to do so. A simplification never
   faced by the harness is not yet *proven* deliberate; it is `mint` (measure it).

Reclassifying a `mint`/`not-worth-it` gap **into** `deliberate-and-staying` to make a red disappear is
a **claim-status defect** (R15 fail-open pattern) — forbidden. The bucket is set by the evidence, never
by the desired conclusion.

## (v) R12 guard (restated for the ratification record)
The gap-count is a diagnostic. This method may never be used to drive a gap-count toward a target,
report "N gaps closed" as an achievement headline, or shorten verification to close a gap faster
(LAW A: if a date and a test conflict, the date is wrong). Closed-gap counts appear on the enumeration
diagnostic line only.

## Argue-back (§2 invited) — quality of the eight named mint sources
The ruling's own amendment (commit `10692bbe9`, deliverable A) states the eight sources are
**candidates, not the definition** — which artefacts are real backlog is the machine's judgement. On
first read of the live registers (GAP1 grounding pass), no named source is *disqualified*, but two
carry caveats the director should weigh at ratification:
- **Fidelity ledger** carries **HELD** SSP-baseline cells (R13/R12, `[[project_ssp_negative_lift_partition_diagnosed]]`).
  These are **not** `mint` residue — they route to `blocked-on-director` (baseline is director-reserved;
  a negative-lift cell there is a *known, ruled* red, not an un-triaged gap). Reading them as `mint`
  would re-open a settled R12 goal-seek trap.
- **Standing sanity findings** include adjudicated-**false** rows (`audit:*`) — only adjudicated-**real**
  rows are residue; the reader (GAP1 register-6) must filter on the adjudication verdict, or the
  battery inflates with noise.

No source is recommended for removal; both caveats are *filters within a source*, applied by GAP1's
reader, surfaced here so the director rules on them explicitly.

---
## Returns for ratification (§2, genuine — not auto-proceed)
Because the classification implies **scope/curriculum judgement** (which simplifications are
deliberate-and-staying is a scope call, and the `blocked-on-director` routing names reserved walls),
this doc is escalated to the director as an `[ACT]` proposal and **HELD**. The agent does **not**
self-apply the taxonomy to open, keep, close, or reclassify any gap until the director ratifies (or
amends) this method. GAP3 (apply the ratified method to GAP1's live residue → a ranked list) is
**blocked_on** that ratification.

## Walls untouched
- **R13 / one-way doors / generator ground truth reserved (§3):** the `blocked-on-director` bucket
  routes such gaps to the director, never self-decides them.
- **No self-closure:** GAP2 produces the *method*; no gap is closed or reclassified by this mint.
- **R12:** gap-count is a diagnostic, stated up front and in (v).
