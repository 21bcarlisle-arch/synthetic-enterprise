**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] The control stack also shows meaning, learning, and what it refuses to do (2026-10-23)

**Type:** STEER, through the advisor channel. It extends `DIRECTOR_STEER_SHOW_THE_HARNESS_AS_A_LIVE_CONTROL_STACK_2026-10-23.md` and goes into the same How it's built rework. The director's words, from chat on Fri 23 Oct:

- 09:23 BST: "And what about ontology and some of the other themes we've discussed in the this chat?"

The themes he means come from his advisor chat over recent weeks. He and the advisor compared Poesys with an observability textbook, Anthropic's code-review write-up, Google's self-improving harness work, a knowledge-layer paper and several published agent harnesses. Four of those themes are places where Poesys is distinctive, and the stack should show them. Four are honest gaps, and they belong one click down.

## Show these as part of the stack

1. **Meaning: one concept, one meaning, checked where parts meet.** This is our answer to "ontology". The director chose this on 31 Aug (`DIRECTOR_CANON_END_TO_END_AND_ONTOLOGY_2026-08-31.md`): "a walk EXERCISES the concepts where a census only INVENTORIES them." The evidence today is:
   - the journey walk, where one household is walked end to end with the joins asserted;
   - the domain invariants;
   - canon claims checked against the code;
   - knowledge-page figures stated as claims and tested against the drawn world every week (`tools/world_claims.py`).

   Others draw an ontology as a box of definitions. Ours is a set of tests that go red when two parts disagree about what a word means. The VAT rule with five implementations is the story that explains why.
2. **Learning: experience becomes knowledge, and knowledge becomes a check.** There are three layers: individual findings, the class documents that consolidate them (`docs/staging/reference/CLASS_*`), and the ratchets and rules they produce. Show it as a flow with live counts. Two mechanisms illustrate it: a ratchet freezes old problems and fails only on growth, and a red that keeps refusing becomes work rather than a retry. Anthropic's review team reported the same convergence problem in October, and we had already measured it.
3. **What the machine is not allowed to do to itself.** The industry is moving towards harnesses that rewrite their own prompts to raise a score: GEPA, Google's Harness² and similar. Poesys refuses that by design. Its outputs are diagnostics and never targets, and a check that is pinned to today's answer is itself a defect. Show this as a deliberate choice with its reason. It is the most distinctive position on the page for a tech reader, and almost nobody else states it.
4. **Judging the judges.** AI reviewers are independent, and they are measured on whether they were right (`background/judge_validation.py`). Show the real count, even though it is small.

## Put these one click down, as "what we are building next"

State them plainly, as the next steps of a system that measures itself, and not as failings on the face of the diagram.
- **Asking any question of a run.** There is no wide per-run record yet, so a new question about a past run needs new code. The run ledger exists and nothing calls it.
- **A reviewer that reads every change.** The trial staged on 17 Oct is measuring whether it would have caught our known-bad commits.
- **Batch-then-bisect landing.** The question staged on 15 Oct is still open.
- **The mothball audit** still has no trigger or schedule.

If any of these has moved since, say where it has got to rather than what this file says.

## Requirements

The same as the parent steer: every count is generated at publish, plain words, one click from each box to the real thing, and "not measured yet" rather than a placeholder. Fold these into the one diagram if they fit, or give them a second panel beside it. Do not start a third page.

## Risk

Touches: the How it's built page and its generator only. Reads existing stores.
Blast radius: one public page, which is reversible.
Probable failure mode: showcase language outrunning the evidence, for example calling it an "ontology" in a way an ontology specialist would reject. Name it for what it is: concepts checked where parts meet.
Proportionality: reversible and narrow — just do it.

— Director steer, 23 Oct 2026, his words above; the theme selection and drafting are the advisor's.
