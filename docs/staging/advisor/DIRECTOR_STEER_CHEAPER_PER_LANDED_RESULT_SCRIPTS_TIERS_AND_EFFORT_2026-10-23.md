**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Make each landed result cheaper with scripts, model tiers and effort levels, piloted and measured; not a local model (2026-10-23)

**Type:** STEER, through the advisor channel. It shapes the cost proposal asked for in `DIRECTOR_READING_THE_NEW_TIER_IS_A_QUARTER_OF_THE_OLD_2026-10-23.md`.

## What the advisor told him

The director asked (09:53 BST): "Should we use ollama and the GPU more or is that marginal with complications and consequences?"

The advisor replied, in short:
- **The local model is marginal.**
  - A 12 GB-class model can't do the work where the tokens go: reading code, landing changes, grading.
  - The mechanical rest is better done by deterministic scripts.
  - It competes with runs for the box's 6 GB memory budget, about 0.5 GB of headroom since the 400-household change.
  - Qwen was retired on 10 Aug.
- **The better levers:**
  - scripts for any mechanical answer;
  - cheaper Claude models and lower effort for routine reading and searching, piloted and measured (R14);
  - fewer parallel lanes, fewer whole-tree re-reads, smaller runs, and less coordination churn.

## The director's words

From chat on Fri 23 Oct:
- 09:56 BST: "I like you "better levers". I find 5.5 versions of the 3 models very good. And medium surprisingly good."

## What it means

1. **No local model on Skynet.** Don't revive ollama or the GPU path. A local model on the director's second PC stays an option for later, for one bounded and measured job, and only if the cost breakdown shows a large mechanical share it would shrink.
2. **Scripts first.** Before any model choice, list the work that has a mechanical answer: census counts, log summaries, staging triage, freshness checks, commit metadata. Convert it to deterministic scripts that cost no tokens. Report the expected share of spend each one removes.
3. **Pilot model tiers and effort levels against what lands, not against spend alone.** The director rates the 5.5 models (Opus, Sonnet and Haiku) as "very good", and medium effort as "surprisingly good".
   - **Routing.** Search, census, log reading, triage and routine edits move to Sonnet 5.5 or Haiku 5.5. Diagnosis, science, weighing evidence and anything canon calls judgement stay on the strongest model (R14).
   - **Effort.** Run medium effort as the default for routine turns, with high or max reserved for diagnosis, design and grading.
   - **The test.** Measure each pilot on the share of turns that land green, rework afterwards and tokens per landed result, against a control on the current setting, for the same kind of work.
   - **Why it must be measured.** The 12–14 Oct Sonnet-with-Opus-advisor trial landed 33% against 74%, at four times the cost per landed run. A cheaper tier that lands less is not cheaper.
   - **Under the 23 Oct ruling,** a pilot that passes its own pre-registered rule is the machine's to switch on. Record each switch-on with a dated exception (G17).
4. **Structural cuts, measured the same way.** Narrower parallel width, landings before experiments, fewer full re-reads of the tree, the smallest run that answers the question (R5), and less churn in the delivery seat and tick loops.
5. **Report by Monday's reset.** Bring one proposal covering:
   - spend by route;
   - each lever's measured or estimated saving per landed result;
   - which pilots are running, with their rules filed before launch;
   - the projected week on the new tier.

   If the conclusion is that the work needs the bigger plan, bring that as a recommendation (G9).

— Director steer, 23 Oct 2026, his words above; the advisor's answer is summarised as he read it; drafting is the advisor's.
