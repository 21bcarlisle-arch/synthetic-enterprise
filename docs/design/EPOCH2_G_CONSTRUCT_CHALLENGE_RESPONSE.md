# Atom G — construct challenge-response (fidelity-evidence measures)

**Provenance:** advisor rider `ADVISOR_RIDER_FIDELITY_CHALLENGE_CLAUSE_2026-07-19.md`, at the director's
prompting — *"the intent is the wall; the constructs are yours to improve. Think it through; do not merely
implement the translation."* The director's **intent** (unchanged, the wall): value = what you add over what a
basic outfit would model; edges/coincidences, never the population average; integration proven real, not
diagrammatic. The three constructs in atom G (`EPOCH2_G_FIDELITY_EVIDENCE_MACHINERY_DISCOVER.md`) — lift over a
frozen naive baseline, worst-cell grid, ablation-with-CRN — are the advisor's **translations**. Below is my
genuine critical pass: two I propose to **sharpen**, one I propose to **augment**, one construct **endorsed as-is**.

This is DISCOVER/FRAME — proposals with reasoning, to be tested at BUILD, not silent spec changes.

---

## Measure 1 — lift over a frozen naive baseline → **sharpen: lift over the best-of-a-naive-FAMILY**

**What serves the intent well:** hash-pinning the baseline on an independent code path (so you can't inflate lift
by quietly weakening the strawman) is exactly right and stays.

**The weakness:** a *single* frozen baseline is a single strawman. "A basic outfit" is not one model — and the
honest question is not "do we beat *a* crude model" but "do we beat the **best thing a competent-but-basic outfit
would cheaply do**." If the frozen baseline is even slightly too weak, lift is systematically inflated, and the
weakness is invisible (the baseline is frozen, so no one re-examines it). Goodhart moves from "weaken the baseline"
(guarded) to "the baseline was born weak" (unguarded).

**Proposal:** define lift as improvement over the **best of a small, fixed FAMILY of naive baselines** —
`err_naive(cell) = min over b in NAIVE_FAMILY of err_b(cell)`. For each driver the family is the 2–3 genuinely
cheap alternatives a basic supplier actually uses (e.g. for price: gas-floor-alone, persistence, and the
3-feature OLS regression; for weather: climatology + persistence). Lift is then value over the *best* cheap
option, which cannot be cherry-picked and rises automatically if any cheap method is strong in a cell. Each family
member is hash-pinned exactly as the single baseline was. **Coherence check:** this is already implicitly the bar
on task 1 — the SSP recal's "beat MAE £34" target IS "beat the OLS regression," i.e. beat the strongest cheap
alternative, not gas-floor-alone (MAE ~£90). The recal validates the construct: the honest baseline was the
competitive naive, not the first strawman. Adopting best-of-family makes that principle general.

## Measure 2 — worst-cell MAX → **sharpen: worst-q% tail mean (CVaR), with q→0 recovering MAX**

**What serves the intent well:** refusing to let good cells average away bad ones is the whole point and stays.
MAX is the honest anti-average.

**The weakness:** pure MAX has two problems. (a) **Noise-fragility** — the single worst cell is often the
*data-poorest* cell, so MAX can lock onto a noise artifact rather than a real edge (atom A's top-k smoother is a
partial patch, but it's a patch). (b) **Distribution-blindness** — two models with an identical worst cell but
very different second/third-worst cells score identically; MAX throws away the shape of the tail, which is exactly
where a risk business lives.

**Proposal:** aggregate the cell scores as the **mean of the worst `q`% of cells** — a CVaR / expected-shortfall
statistic — instead of the single maximum. This (i) is far less noise-sensitive (averages over the worst *band*,
not one point), (ii) still structurally refuses population-averaging (only the bad tail counts; good cells never
dilute it), (iii) reads the *shape* of the tail, and (iv) **aligns the fidelity measure with the campaign's own
frame** — atom F makes value-at-risk the arbiter, and CVaR is the coherent tail-risk measure; measuring fidelity
by the same tail statistic the company uses to price risk is more honest than an ad-hoc MAX. `q` is a single dial;
**`q → 0 recovers pure MAX**, so this strictly generalises the advisor's construct rather than replacing it — the
director can set q=0 to get exactly the sketch, or a small q (e.g. worst 5–10%) for the noise-robust version.
The map-of-ignorance (unmeasured cells = top severity) is untouched and still sits on top.

## Measure 3 — ablation-with-CRN → **endorse as the confirmatory test; augment with a cheap screen**

**What serves the intent well:** ablation (sever a coupling `L→1`, measure Δ under common random numbers) is the
**gold-standard causal proof** that a coupling is load-bearing not decorative — CRN/substream isolation is what
makes Δ causal rather than noise. This is correct and I would not weaken it. It is the right bar for the
*load-bearing claim*.

**The weakness the advisor already flagged:** it is expensive (a full re-run per coupling) and low-powered on thin
runs (Δ can sit inside noise even under CRN — G's own doc points at importance sampling).

**Proposal (augment, don't replace):** add a **cheap observational-sensitivity SCREEN** upstream of ablation — from
the *already-computed* run, measure whether the downstream belief's response to real upstream variation is
consistent with the wired coupling's `L` (a conditional-sensitivity / partial-correlation check, near-zero extra
cost). This is only *correlational* (confounded), so it can **never** promote a coupling to load-bearing — but it
**triages**: couplings whose observational sensitivity is flat are unlikely to survive ablation, so ablation
compute goes first to the couplings that might matter. Ablation stays the sole confirmatory test; the screen just
spends the expensive test where it pays. Combined with CRN + importance sampling (for power), this keeps the
causal bar intact while making the measure affordable at scale (C-S constraints).

---

## Net
- **Intent honoured in full** — none of these relaxes "value over a basic outfit / edges not averages / integration
  proven real." Two proposals make the constructs *harder* to game (best-of-family) and *sounder* (CVaR); one makes
  the causal test *affordable* without weakening it (screen-then-ablate).
- **All three are generalisations** — best-of-family with a 1-member family = the frozen baseline; CVaR with q→0 =
  MAX; screen-then-ablate with an empty screen = plain ablation. So the director can dial back to the exact sketch
  at any point; nothing is lost, only headroom added.
- **Status:** FRAME proposals, to be tested when atom G's G1–G3 machinery is BUILT (this campaign, gate-after).
  The SSP recal (task 1) already exercises measure-1's best-of-family principle live. Batched for director review
  alongside the values-calls; override any construct back to the sketch at the console.
- **The rider is absorbed into the campaign's standing discovery clause** — advisor sketches are hypotheses to
  test, never specs to build; the intent is the wall.
