# JUDGING THE JUDGES — and the harm-cost weights (P1)

**Staged:** 2026-07-13 by advisor, director-requested. Disposition: QUEUE.
Two items, both about scoring things honestly.

## PART 1 — the un-mutation-testable judge (your honest residual)
You reported: *"the LLM-judge verdict QUALITY is structurally
un-mutation-testable."* **That is true, and naming it was the most valuable
sentence in the digest.** You cannot inject a defect that proves a JUDGMENT was
bad. But it is not un-attackable. Four approaches; adopt what survives contact:

1. **CONSISTENCY** — same input, repeated: does the judge return the same
   verdict? A judge that flips on identical evidence is noise, and its verdicts
   cannot support a promotion. Measure and publish the flip rate.
2. **INDEPENDENCE** — does a differently-primed judge (different persona, seed,
   or context) reach the same verdict? Systematic disagreement between
   independent judges is a finding about the JUDGE, not the artefact.
3. **GOLD SET** — you already have one: **the director's own Expert Hours are
   human-adjudicated cases.** Build the gold set from them (the C1 bill, the
   thesis chart, the bad-debt smell test, the meter-read mismatch) and score
   judges against it. A judge that misses what the director caught is a weak
   judge, and now you can say so with a number.
4. **OUTCOME CORRELATION (the strongest, and nearly free)** — **a judge whose
   PASSES later FAIL is a bad judge.** The trust ledger ALREADY tracks
   defects-found-post-close. That IS the judge's error rate, sitting there
   uncomputed. Wire it: per judge, per task class, track (verdicts passed) vs
   (defects later found in that work). Publish it. This validates judgment by
   CONSEQUENCE when it cannot be validated by construction.

**Standing rule to consider:** where a control cannot be mutation-tested, it must
be OUTCOME-tested. No verdict-producing organ escapes measurement entirely —
if we cannot test how it decides, we test whether it was right.

## PART 2 — the harm-cost weights (R13, director's call — this doc frames it)
The weights that turn the belief-vs-truth gap into a SCORE. Correctly withheld
from the agent (Law B: never tune the weights toward a gap number).

**What is being weighted (the can't-pay / won't-pay 2x2):**
- True can't-pay, classified WON'T-pay -> **HARM**: aggressive collections
  against someone who genuinely cannot pay. Ability-to-pay rule breach, Consumer
  Duty breach, vulnerability harm, complaints, redress, Ofgem enforcement,
  licence risk.
- True won't-pay, classified CAN'T-pay -> **LOSS**: soft treatment of a
  strategic non-payer. Bad debt, moral hazard, revenue leakage.

**Anchor the weights to REAL consequences, in BOTH directions — do not pluck
them:**
- HARM side: actual Ofgem enforcement and redress outcomes (wrongful PPM
  installation, ability-to-pay failures) — these have run to millions and carry
  licence-threatening tail risk.
- LOSS side: real supplier insolvency (~30 UK suppliers failed in 2021-22; bad
  debt and unhedged exposure were central).

**The essential shape (advisor's recommendation, director decides the numbers):**
Heavily asymmetric toward harm-avoidance — **but NOT infinite.** If harm is
weighted infinitely, the optimal policy becomes "never pursue anyone", bad debt
explodes, and the company dies of the other cause. **BOTH failure modes must
remain lethal**, because both are lethal in reality. A weighting that makes one
of the two real deaths impossible is a weighting that has removed a truth from
the world.

**Present the director with:** the two anchor sets above (with sources), a
recommended ratio, the policy each ratio implies at the extremes, and the
sensitivity — i.e. at what ratio does the optimal policy flip from "pursue" to
"forbear"? That last number is the interesting one, and it belongs in the pitch.

## DoD
Judge-validation: consistency + independence + gold set (seeded from the
director's Expert Hours) + outcome correlation (from the trust ledger) live and
published; the "outcome-test what you cannot mutation-test" rule in CLAUDE.md.
Harm weights: the framing pack above put to the director as a single decision
with anchors, implied policies and the flip-point; placeholders stay until he
signs. Never tune the weights toward a gap number.
