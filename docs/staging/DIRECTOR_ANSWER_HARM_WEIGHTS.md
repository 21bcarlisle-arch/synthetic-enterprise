# DIRECTOR ANSWER — A7_harm_cost_weights_ratio (R13, signed) + a formula defect

**Staged:** 2026-07-13 by advisor, **relaying the DIRECTOR'S DECISION** made in
live conversation after reviewing your decision pack. This answers your
[ACTION NEEDED] A7_harm_cost_weights_ratio. Disposition: **INTERRUPT** (you are
blocked on it; placeholders are shipping).

## 1. THE DIRECTOR'S SIGNATURE (R13 curriculum — his call, recorded)
**R = 8:1 SIGNED. Band 5:1–10:1.**
Rationale on record: the shape is right — heavily harm-averse but **BOUNDED**,
so BOTH real deaths stay possible (regulatory/licence death from harm; insolvency
death from bad debt). Direct costs are roughly comparable (bad-debt write-off is
several hundred pounds a case; the British Gas redress works out around £700 a
case), so **8:1 is pricing the TAIL** — enforcement, mass remediation, licence
risk — which is the honest reason harm dominates. Never tune this toward a gap
number (Law B / R13). It changes only by the director's explicit re-signature.

## 2. FORMULA DEFECT — YOUR FLIP-POINT IS INVERTED (advisor's finding; fix first)
Your ntfy states `R*(p) = (1-p)/p`. **That is inverted.** The correct threshold
is:

  **R* = p / (1-p)**   → pursue iff R < p/(1-p), i.e. iff p > R/(1+R)

Check it against YOUR OWN decision rule: at R=8 you correctly say "pursue only
when >= 89% confident". `p/(1-p)` at p=0.889 gives **8** ✓. `(1-p)/p` gives
0.125 ✗.

**THE TRAP, and why this is a mutation-testing case:** both formulas evaluate to
exactly **1** at p=0.5 — so a test written at the coin-flip case **passes either
way**. An inverted gate would make the company FORBEAR when it should PURSUE and
PURSUE when it should FORBEAR, and the obvious test would never catch it.
**Verify the code, and mutation-test it at p=0.9 and p=0.1, not at p=0.5.** If
the inversion reached the implementation, this is a live Tier-1-class defect in
the decision gate.

## 3. TWO SIMPLIFICATIONS TO REGISTER (do not block on them)
- **Harm is HEAVY-TAILED, not a point estimate.** Most wrongful pursuits cost
  little; a few trigger enforcement, mass remediation and existential licence
  risk. A single scalar collapses that distribution. Register as a named
  simplification; model the tail when the affordability cluster matures.
- **Harm must SCALE WITH VULNERABILITY.** Wrongly pursuing a disorganised but
  comfortable household is not the same as pursuing someone on the PSR who then
  self-disconnects. Real regulation makes that distinction; our scalar does not
  yet. Register it — it couples naturally to W2_8 (self-rationing) and the PSR.

## 4. H1 (the figure you could not source)
Use the **£90m British Gas aggregate as the DIRECT anchor** (~£700/case).
**Treat licence-loss as a SCENARIO, not a probability** — you cannot estimate the
tail of an event that has almost never occurred, and a fabricated probability
would be worse than an honest scenario. Record it that way.

## 5. The finding worth publishing (Proof door + pitch)
**At even odds, ANY harm-aversion at all means forbear. Pursuit must be EARNED by
confidence.** That is what regulation implicitly demands, no supplier can
articulate it, and we can put a number on it. Feature it.

## DoD
R=8:1 in the curriculum (director-signed, versioned); the flip-point formula
verified and mutation-tested at p=0.9/p=0.1 (NOT only p=0.5); both
simplifications registered; H1 recorded as anchor + scenario; the
"pursuit must be earned by confidence" finding published on The Proof door.
