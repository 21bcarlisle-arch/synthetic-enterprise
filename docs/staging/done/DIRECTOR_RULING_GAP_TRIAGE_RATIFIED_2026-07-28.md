# [DIRECTOR-RULING] — GAP2 triage method RATIFIED, with one amendment and two questions. GAP1 BUILD half OPENED. (2026-07-28)

**Type:** [DIRECTOR-RULING] via advisor bridge. Answers the held [ACT] on `docs/design/GAP_TRIAGE_AND_RANKING.md` and the `director_build_open` block on GAP1.

## 1. RATIFIED as proposed

The four-bucket taxonomy — **mint / deliberate-and-staying / blocked-on-director / not-worth-the-complexity** — is ratified with its ranking dimensions, its mint threshold, its R12 guard, and its default directions. **Apply it.**

Specifically ratified, because these are the parts carrying the weight:

- **The asymmetric default on bounds.** Below threshold *with* a measured bound → not-worth-the-complexity; below threshold *without* one → mint at low rank, to measure it. "The cheap outcome is measuring a gap, not ignoring it" is exactly right, and it closes the route by which a gap could be dismissed as unimportant without ever being sized.
- **The faced-or-scheduled condition** on deliberate-and-staying. A simplification the harness has never been exposed to is an untested assumption, not a proven scope choice. This is the strongest idea in the proposal.
- **Reclassification to make a red disappear is a claim-status defect.** Held.
- **Board-battery weight = 3 mints regardless of composite.** Credibility is not tradeable against convenience — correct.
- **Both argue-back filters are ratified as filters-within-sources, not source removals:** held SSP-baseline cells route to `blocked-on-director` and are never `mint` residue (reading them as mint would re-open a settled R12 goal-seek trap); standing sanity findings are filtered on adjudication verdict so only adjudicated-real rows are residue.

**Recorded:** the SSP caveat was reached independently from the live registers, and matches the collision the advisor named from the rulings side (amendment E, `10692bbe9`). Two routes, one answer.

## 2. AMENDMENT — asymmetric ratification on bucket moves

The proposal forbids **bad-faith** reclassification. It does not cover **good-faith scope drift**, and the two directions carry very different risk.

- **Moving a gap INTO `deliberate-and-staying` returns for director ratification.** That is a scope call — a claim that the model does not need this fidelity at this epoch — and it is the direction in which honest reds quietly disappear.
- **Moving a gap OUT of `deliberate-and-staying` toward `mint` is autonomous.** No ratification needed; the direction that surfaces more work needs no permission.
- Moves between the other three buckets are autonomous under the ratified method, save the existing `blocked-on-director` escalation rule.

Batch the inbound-ratification requests rather than escalating singly.

## 3. Two QUESTIONS — your judgement, not prescriptions

**(a) Staleness has no disposition.** The taxonomy claims mutual exclusion and total coverage, but a register entry that is simply **no longer true** — superseded, already fixed, or describing a component since removed — fits none of the four buckets. Under total coverage plus the ambiguous-defaults-to-mint rule, it would become work for a gap that does not exist. Is this already handled by GAP1's reader contract (a staleness filter at read time), or does the taxonomy need a fifth disposition with its own evidence test? **Your call — you hold the registers and know how stale they run.**

**(b) Blast radius is scored as positive value**, and it is simultaneously a risk proxy — the proposal says as much. As a diagnostic tie-breaker that may be exactly right. State whether risk is considered separately anywhere in the ordering, or deliberately folded in on the argument that value and risk move together here. If the honest answer is that they were folded for simplicity, say so and leave it; this is not worth a mechanism.

## 4. GAP1 BUILD half — OPENED

The `director_build_open` block on `docs/design/GAP_REGISTER_MINT_SOURCE_CONTRACT.md` is **released**. Build the reader contract: per-register primary-state paths, OPEN-marking fields, and the reader invariants already specified — LAW-C independent read, fail-safe toward work, R12.

Both ratified filters from §1 are part of the reader's contract, not an afterthought: the SSP-held cells and the adjudication-verdict filter must be enforced by the reader, so a downstream consumer cannot mis-read the registers even if it wants to.

## 5. Coherence

- **GAP3** (apply the ratified method to the live residue → the first ranked list) is unblocked by this ruling and proceeds.
- **PRODUCT-FIRST** guard stands as the proposal already honours it: machinery-lane gaps rank among themselves and never outrank a product-lane atom on composite score.
- **Exit-criterion interaction unchanged** (amendment D): only product-content gap closures count toward the harness counter; harness-register closures do not; ambiguous cases do not count and get flagged.
- **R12 unchanged:** the gap-count is a diagnostic. It may appear on the enumeration line and nowhere else.

## WORK THIS CREATES

1. Apply the ratified taxonomy; GAP3's first ranked list, with buckets and rationale.
2. GAP1 reader contract built, with both ratified filters enforced at read time.
3. The inbound-ratification path for moves into `deliberate-and-staying`, batched.
4. Answers to (a) staleness and (b) blast-radius, in one report.

Acceptance: every enumerated gap carries a bucket with its evidence, and the ranked mint set is inspectable from published artifacts.

**Risk & proportionality:** ratification plus one narrow amendment; the reader build is mechanism already specified by the machine. Tag: **proceed.**

— Advisor bridge, carrying the director's ratification, 2026-07-28.
