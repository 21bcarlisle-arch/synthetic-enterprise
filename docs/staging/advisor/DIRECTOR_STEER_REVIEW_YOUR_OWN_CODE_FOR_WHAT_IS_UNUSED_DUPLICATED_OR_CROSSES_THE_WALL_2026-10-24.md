**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Review your own code for what is unused, duplicated or crossing the wall, decide what to do, and explain why your controls didn't flag it (2026-10-24)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sat 24 Oct, after looking at the galaxy on `/code/`:

- 09:35 BST: "This diagram on the code tab is great but it raises questions. What is the difference between sim and simulation? And between company and saas? Why do some not have import edges? Why does this matter? Do we have any redundant old code that does things we don't need any more or goes no where, or doesn't get called or used ?"
- 09:40 BST, on the advisor's answer below: "Yes, but as illustration of recommendation. Encourage it to do it's own review and decide what issues there are and how to improve. Also why wasn't this picked up automatically?"

**What he asks:** your own review and your own decisions. What follows is the advisor's quick read, given to him as an illustration. Use it as a starting point to test, not as the answer. Where your review finds more, less or something different, your review wins, and you say why.

**When:** start the review now, beside the Monday publish work. It is cheap to start and saves tokens on the new tier. Any archive or merge lands after the publish, so the publish is not destabilised. Bring the findings and your decisions in the stretch log. The page fix (item 4) can ship with Monday's publish.

---

## The advisor's illustration (from `site/data/module_graph.json` at `1044c8fe0` and a walk of origin, 24 Oct)

1. **Built, tested and never called.**
   - **The size.** 327 modules have no static import edges. 286 of them are in `company/`: about 38,900 lines, roughly a third of the supplier's modules.
   - **Who imports them.** All 286 are imported by tests and by nothing else, so they are tested and never used by a run. 72 are `*_register` modules, for example `company.regulatory.ico_breach_register`, `company.sustainability.tcfd_climate_risk` and `company.market.dso_flexibility_tender_register`.
   - **History.** `docs/design/ORPHAN_DISPOSITION_REGISTER.md` (9 Aug) ruled 258 of them `unhooked` and kept them all ("Nothing was deleted"). The count has since grown to 286.
   - The 34 unwired modules in `tools/` are mostly scripts by design.
2. **Two layers with overlapping jobs.** `saas/` (36 modules, the July business layer) and `company/` (534 modules) are both the supplier. Two churn models exist, `saas.churn_model` and `company.crm.churn_model`. That breaks "a concept has one home" (canon, How this canon works, item 1). `sim/` and `simulation/` are both the world side, split by history rather than by job.
3. **The world builds its truth from the supplier's model.** `simulation/customer_events.py` imports `saas.churn_model` (`build_churn_risk`, `churn_probability`) and `saas.home_move_win_rate`. The world's own departure roll starts from those, through `effective_retention_probability`. It also imports `company.crm.churn_model` to compute the company's estimate inside world code.
   - **Why it matters.** The household's true chance of leaving partly comes from a supplier-side model. That breaks W7 principle 1: "build the household side ... with no reference to any supplier policy". It also means the published belief-against-truth gap on churn partly measures a model against itself.
   - **The crossings.** These are three of the four crossings that go round the seam. The fourth is `simulation.run_phase2b` importing `company.policy.decision_policy`, which may be legitimate orchestration. Rule on it.
4. **The code tab raises questions it doesn't answer.** A newcomer, the director, could not tell sim from simulation or company from saas, or why modules have no edges. Add a plain legend per cluster, saying what each is and which side of the wall it sits on. Show the unused-module count and what it means.

## Why wasn't it caught automatically? Answer this from the record

Two hypotheses from the advisor, offered for you to confirm or refute:

- **The controls stop growth and approve rulings. They never ask whether the thing should exist.**
  - `tests/architecture/test_epistemic_wall_ratchet.py` keeps a dated, shrink-only allowlist of grandfathered crossings, frozen on 5 Aug. It stops new ones, but nothing schedules the old ones for removal, so they have stood for 11 weeks.
  - The orphan register passes when every orphan has a row, and "unhooked, with tests" is an accepted row. A count that grew from 258 to 286 still passes.
  - Both are the same shape: a debt with a ruling and no owner, no date and no cost attached.
- **The world and the runner share one package.** `simulation/README.md` lets the orchestrator import both sides: "Code here may import from both `sim/` and `saas/`". World behaviour lives in that same package, so world logic inherits the runner's licence to read the supplier. The wall is enforced one way, company not reading the world. The other direction, the world not built from the supplier (W7 principle 1), has no structural check.

Find the real cause, then fix the class (P13): a mechanism that turns grandfathered debt into scheduled work with a cost attached, and that would have caught the world importing supplier models. Prove it able to fail (R15).

## Decide, then act

The decisions are yours, within canon. For each finding, rule it one of:
- wire it in, because a P1 item needs it;
- **archive** it with its tests. That is reversible, and "archive, never delete" covers code;
- merge it;
- keep it, with a stated reason and an owner.

Measure what the archive saves in commit-gate time and tokens per turn. That matters on the new tier.

Treat the world-truth churn rebuild as world work under the four principles:
- K8 first, from the published switching evidence the knowledge pages already hold;
- a labelled range where the evidence is missing;
- predictions filed before the rebuild;
- before and after on the same seed;
- the published belief-against-truth figures re-graded.

Anything that would change a ruling comes to the director as a recommendation (G9). Moving code to an archive does not.

## Report

One stretch-log entry with:
- your review's findings, including those the illustration missed and anything in it that was wrong;
- the decision per item;
- the root cause and the mechanism now catching it;
- the saving measured;
- the code-tab legend.

— Director steer, 24 Oct 2026, his words above; the illustration and drafting are the advisor's.
