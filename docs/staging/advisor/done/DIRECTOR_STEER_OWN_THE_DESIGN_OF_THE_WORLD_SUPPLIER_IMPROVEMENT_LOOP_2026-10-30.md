**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Own the design of the world–supplier improvement loop: here is the problem, the concerns, and some ideas, not a specification (2026-10-30)

**Type:** STEER, through the advisor channel. The director's words, from chat on Fri 30 Oct:

- 07:30 GMT: "So we need knowledge. SIM enhancement. And supplier testing to optimise versus this. Once it's settled we can look to make the SIM more real and more nuanced and the cycle contines."
- 08:20 GMT: "And do we have demarcation between sim and supplier. How does that evolve: optimise cycle work. Is it embedded. Can it be improved?"
- 08:23 GMT, on the advisor's answer: "Yes. But raises concerns and the issue to solve with ideas. Let it really think about it and own the solution"

**How to read this file.** The director does not want the advisor's list carried out as written. He wants you to understand the problem, test the concerns against the code and your own record, and design the solution yourself. The ideas at the end are prompts. Reject, reshape or replace any of them, with reasons.

## The problem to solve

The project's purpose rests on a cycle:
1. knowledge of how a part of the market works;
2. a world whose households live it and **react** to it;
3. a supplier that tests ways to do better against those reactions;
4. once a result settles, a more real and more nuanced world, and round again.

The cycle has to produce supplier learning that would hold in the real market. It must not produce learning that holds only in our simulation.

**Today the parts exist but the cycle does not run as a cycle.**
- The *demarcation* is strong. It has three layers:
  - the epistemic wall and the seam (`company/interfaces/sim_interface.py`, `interface/contracts/`);
  - no route to the real world;
  - the crossing census (91 found, 85 removed, 6 owed, as the site states).
- The *method* is written down: W7, meaning world first, freeze then solve, separate the work, truth stays an instrument; pre-registration; and fresh seeds.
- **But the cycle is not embedded.** It happens item by item, when someone thinks of it.

## Concerns the advisor raised (test each; disagree where the evidence says so)

1. **No one can say what stage each area is at.** For payments, first-months estimates, unbilled energy, debt, renewals and EVs, you cannot read off whether the knowledge is written, whether the world reacts, what supplier variants have been graded, whether the result is settled, or what nuance comes next. If the stage is invisible, the draw cannot be steered by the cycle.
2. **The world may not react to most pain points.** The audit in `DIRECTOR_STEER_PAIN_POINTS_DRIVE_THE_LOOP_…` will show how far this goes. A supplier optimising against a world that does not press back learns nothing true (canon F1).
3. **This week's world defects were found by examples, not by the loop.** These were the gas-only EV home, prepayment at the DD price, and the standing charges on 1 January. The cycle as built does not catch the world being wrong.
4. **The separation is between lanes, not minds.** The same agent family writes the world's reaction model and the supplier strategy that is graded against it. Shared blind spots can make a strategy look good because the world was built with the same assumptions. Last week's invariant errors had exactly this cause.
5. **Thin evidence turns into false precision.** The packs found no published GB figure for churn or DD cancellation after a DD rise or a shock bill. A world that holds one guessed value invites strategies tuned to that guess.
6. **There is no principled trigger for "make the world more nuanced".** Without one, nuance is added by taste, too late or too early, and risks moving the world after supplier results (W7.2).
7. **Small rot at the seam.** `interface/README.md` still says its contracts folder is "Empty for now". Six crossings are still owed, with no date.

## Some ideas (prompts, not instructions)

- A **loop register** with one row per area: its stage, world reaction model and evidence, frozen world version, outcome scorecard, supplier variants and their grades, settled result, and next nuance. Publish it, and let the draw read it.
- **Blind roles enforced by tooling, not by convention:**
  - the world builder never sees supplier results;
  - the supplier builder reads only through the seam and never the `sim/` code;
  - a third party grades.
- **Robustness over the evidence range:** where evidence is thin, the world carries a range, and a supplier strategy counts as better only if it wins across that range.
- **A scorecard agreed before any experiment.** It covers customer outcomes, company outcomes and fairness, and is fixed at the knowledge stage.
- **An exploit check as the nuance trigger.** When a strategy wins, an independent reader asks: "would this work in the real market, or does it exploit something our world fails to punish?" An exploit is the signal to add realism in that area, under the freeze rules.
- **Close the six crossings by a named date,** and make the seam's own documentation true.

## What is wanted

1. **Think first.** Write `docs/design/THE_IMPROVEMENT_LOOP.md`. It should include:
   - your own statement of the problem;
   - each concern above, judged against evidence from the code and the record (confirmed, partly, or refuted);
   - any concerns the advisor missed;
   - the options you considered, with trade-offs, including the cost in tokens and effort;
   - **your recommended design and why**;
   - how it will show that it works: what would prove the loop is embedded, and what would show it has failed.
2. **Bring it back as a proposal.** Raise one row in `for_the_director` with your recommendation. It is a strategy and method question, which the 28 Oct ruling says may come to him. Keep it to a page he can read in two minutes.
3. **Sequencing.** The thinking and the design note can be drawn now, inside the correctness stretch, because they are cheap and reading-only. The build follows the correctness exit test. The one exception is any part that would help close that test; the blind-role separation for the cold reader and the invariants may be such a part.

## Done

2026-10-30, the delivery seat.

- **Design note:** `docs/design/THE_IMPROVEMENT_LOOP.md`. It judges each of the seven concerns
  against the tree. 1–6 are confirmed. 7 is partly refuted: the six owed crossings now have an owner
  and due dates of 21 and 28 Nov. It is also partly worse: three of the six are the world importing
  the supplier's churn functions, against the seam README's own claim.
- **Missed concerns:**
  - the knowledge layer quotes code constants, so "blind" authorship from it is leaky;
  - a new reaction ships at 0 by default (K2);
  - every supplier experiment hand-builds its own grading;
  - weighting the scorecard is his (the A5 frame);
  - the correctness exit test *is* the loop's "world reacts correctly" stage.
- **Recommended design:** stages derived from artefacts, not kept by hand. Grading across range
  endpoints, as W7.3 already rules. Three named triggers for adding nuance. Blind roles by sparse
  worktree.
- **The proposal:** raised as `for_the_director` row `the-improvement-loop-world-then-supplier-then`,
  with one question for him: whether the scorecard stays a vector, Pareto only.
- **What is left:** the build. The blind worktree comes now, because it helps the correctness exit
  test. The rest follows the exit test, in the note's §5 order.
