**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] A decision reserved to him still arrives with a considered recommendation (2026-10-19)

**Type:** STEER, standing, through the advisor channel. The director's words, from chat on Mon 19 Oct:

- 16:38 BST: "Ps. Even items that are reserved for me I'd prefer it to make a considered recommendation"

## What it means

When something reaches him because it is his (G5, G9, P11, C14, a curriculum value, a ruling), it arrives with these parts:
- **The question, in one line.**
- **A recommendation**, said plainly: "I recommend X". A neutral list of options doesn't meet this.
- **The evidence and reasoning**, with sources and numbers where they exist (K-rules).
- **The trade-off**: what X costs, and what the main alternative would buy instead.
- **The holding position until he rules**, and why it is the safe default. Work does not stop for it (P7, P8).
- **What would change the recommendation.**

**The 400 example (19 Oct).** The 17 Oct finding proposed holding 400 supply points as the safe default. That was a holding position, not a recommendation on the question itself. He ruled "Households, as long as it doesn't create a memory problem". The better shape would have recommended households or supply points on the evidence, as suppliers count customers, priced the memory and run-time cost, and named the holding position separately.

**Not changed.** What is reserved stays reserved, and the recommendation does not act on itself. It only tells him what the machine would do and why.

## Where this lands

- `docs/design/DIRECTOR_CANON.md`: add one line to G9, quoting the director's words above verbatim (canon "How this canon works", items 2–3, marked as his words of 19 Oct).
- `CLAUDE.md`: point to G9, without rewording it.
- The `director_concerns` / `for_the_director` row format: give it a required `recommendation` field. The staging watcher flags a row that lacks one. That is the mechanism. Make it mutation-proven, and keep it small.
- Open rows already waiting for him: add a recommendation to each in the next pass, and report how many.

— Director steer, 19 Oct 2026, his words above; the drafting is the advisor's.
