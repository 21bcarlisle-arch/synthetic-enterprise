**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Show the harness as one live control stack, end to end (2026-10-23)

**Type:** STEER, through the advisor channel. It adds to `DIRECTOR_STEER_THE_OTHER_PAGES_MATCH_THE_FRONT_DOOR_2026-10-23.md` §4 (How it's built) and should land in the same rework, before the Monday 26 Oct publish. The director's words, from chat on Fri 23 Oct:

- 09:20 BST: "Whenever I share someone else's impressive looking harness list or diagram you always say we do this already or are ahead. But on the website our harness is not a neat or impressive summary list or diagram. How could you show our harness and e2e control mechanism, is very advanced"

## The problem

Other teams publish a neat diagram of their agent harness: a set of layers, a few labels, often no evidence. When the advisor compares them with Poesys, the honest answer is usually that we have the same idea or a stricter one. A reader of poesys.net cannot see that. Our controls are spread across a delivery record, war stories, CLAUDE.md, the hooks and the code. Nowhere shows them as one system you can take in at a glance.

## The outcome wanted

Near the top of How it's built, a newcomer in tech should see **the whole control system on one screen**. It runs from the director's intent to the published page, and every layer is backed by live evidence that it works. A comparison should be possible at a glance: here is everything that stands between an AI's idea and a published claim.

The thing that makes ours different, and the reason it should be shown this way: **every box carries its own proof, generated at publish.** That proof is:
- how often the layer refused or caught something in the last 30 days;
- when it last fired;
- whether it has been shown able to fail.

Other diagrams are claims about a design. This one would be a measurement of a running system. A layer that rarely fires shows that plainly in its own box, with its number. That honesty is part of what makes the stack credible, and it does not need to be the headline.

## What the stack covers (the advisor's reading; check it against the code, and the repo wins)

Roughly in order, from intent to published page. Group and name the layers however reads best.

1. **Direction.** The director sets purpose. Canon is held in his words. The delivery seat writes direction and never code. The advisor channel only accepts files signed with a pinned key. Some decisions stay with a human (the one-way-door categories).
2. **Knowledge before build.** A domain number must declare where it came from. A cited constant must actually be used. A knowledge page comes before a capability.
3. **The walls.** The company can only know what a real supplier could know. It cannot open a network connection. Ground truth never crosses the seam. These are refused by construction, not by approval.
4. **The commit gate.** About 21 pre-commit checks and 5 commit-message checks, measured today from the hook files. Ratchets freeze the existing backlog and fail on any growth. Bypassing the hooks is a wall.
5. **Proof the checks work.** Each control is shown failing on its own defect by reintroducing that defect. About 654 test files cite this rule today.
6. **Independent judgement.** Fresh-context reviewers: the phase-close evaluator, cold-eyes walks and the naive organ. A ledger records whether their passes later proved wrong.
7. **The published state.** The deploy byte check. Door tests run the page's own JavaScript against the real feed. Every financial figure carries its clock. Canon is checked against the code. Knowledge pages test the simulated world every week.
8. **Learning.** A finding becomes a class, and a class becomes a rule or a ratchet. A red that keeps refusing becomes work, not a retry. The weekly end-to-end check reads canon, logic, work and findings together.

## Requirements

- Every number in the stack is generated at publish from the stores that already exist. No figure is hand-typed, including the 21, the 5 and the 654 above.
- Each box links one click down to the real thing: the rule's enforcing file, the ledger, or the latest refusal.
- Plain words for a newcomer, so no atom, rung or lane vocabulary on the face of the diagram.
- It renders static in the HTML, readable on a phone, and is consistent with the home page and the code galaxy.
- If a layer's evidence cannot be computed, the box says so ("not measured yet"). It never shows a plausible placeholder.

## Checks

Use the same cold tech reader as the main steer and ask one extra question: "Compared with other AI agent harness diagrams you have seen, what does this one show that they do not?" If the reader cannot answer, the diagram has not met this steer.

## Risk

Touches: the How it's built page and its publish-time generator only. It reads existing stores and writes none.
Blast radius: one public page, which is reversible.
Probable failure mode: a count that reads a store with the wrong population, for example refusals counted per cycle on one layer and per commit on another, then shown side by side as if comparable. Say what each number counts, in the box.
Proportionality: reversible and narrow — just do it.

— Director steer, 23 Oct 2026, his words above; the stack reading and drafting are the advisor's.
