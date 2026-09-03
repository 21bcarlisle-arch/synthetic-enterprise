**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** `the-company-estimator-learns-from-its-own-book`

# The fail-closed guard the director made his priority reached no reader — checked from origin, and repaired

**2026-08-31, Lane 0.** The direction asked for a reader-side check of the standing rule's verdict,
named three possible outcomes, and said not to assume the first. **The third one held.** This is the
check, read off `origin/main`, and the repair that followed it.

---

## 0. Two premises in the direction were already stale, and one changed what "origin" means

The direction said four commits (`6168ae6bf`, `27a646701`, `2b9fb79d9`, `ae12a334e`) were local-only
and `origin/main` was `c9d0dab6d`. Not at the time of the check:

    git ls-remote origin main -> 44d99a62e5206226107de146f67a10e10b5c4c9c
    git rev-parse HEAD        -> 44d99a62e5206226107de146f67a10e10b5c4c9c

All four are ancestors of `44d99a62e`. `git ls-remote` rather than `git rev-parse origin/main`,
because the remote-tracking ref is a local cache and reading it would have reproduced exactly the
class the direction was warning about. **HEAD and origin were identical**, so every reader-side
reading below is a reading of the published site.

---

## 1. What a reader could see, before this landed

Every JSON under `site/data/` at `44d99a62e` was walked for the strings the verdict is made of
(`two sides`, `cannot tell`, `measuring our own reflection`, `evidence of skill`, `own inference`)
and for its keys (`belief_vs_truth`, `inference_claim`, `sides_are_independent`, `co_calibrated`,
`publishable_as_evidence_of_inference`, `belief_error_pp`). Three results:

**(a) LEG TWO reaches a reader.** `site/data/value_arms.json` carries
`method_skill.cannot_tell` — *"On whether this method carries any information, we cannot tell:
0.333 sits inside the 0.133–0.867 a signal carrying no information reaches on 6 decisions."* —
and `site/capabilities/index.html` renders it in amber. That half works, exactly as designed.

**(b) LEG ONE, AND THE COMPOSED VERDICT, REACH NOBODY.** `site/data/value_arms.json` has **no
`belief_vs_truth` key at all** — top-level keys are `generated_at … method_skill, household,
decisions, headline` and nothing else. `tools/couple_value_based_pricing` composes
`sides_are_independent`, `the_method_clears_its_null`, `publishable_as_evidence_of_skill`, the
derived `sentence` and the `refusal` into `docs/observability/value_based_pricing_arms.json`, and
the only things that read that file are `tools/run_value_cycle_ab.py` and the module itself. It is
not under `site/`. `value_cycle_ab_s1_three_arm.json`, which *is* read by the site producer,
carries **zero** occurrences of the sentence. So the page could say *"we cannot tell whether the
method works"* while saying nothing whatever about whether the two sides were even arrived at
independently — which is the leg the director's own instance of the rule was written about.

**(c) AND THE COMMITTED ARTEFACT PREDATED THE MODULE.** `git show
HEAD:docs/observability/value_based_pricing_arms.json` → `belief_vs_truth` has keys
`available … publishable_as_evidence_of_inference, shared_calibration, refusal, what_it_means` and
**no `inference_claim` at all**. So even the one file that holds the verdict held a version from
before `tools/inference_claim` existed. Anything that had started reading that artefact would have
published a verdict the module no longer holds.

**Outcome three, then: the honest finding is that a fail-closed guard the director made his
priority publishes nothing.** Not the flattering outcome (a self-correcting sentence needing only a
push) and not the alarming one (a live wrong claim). The design *is* good — `_sentence` derives its
prose from the flags and the reversal did self-correct where it was computed — but a verdict that
self-corrects into a file nothing renders has not failed closed on any surface. CLAUDE.md:
*"'we cannot tell' is a result, it belongs on the page, not in a footnote."*

## 1a. The near-miss that is worth more than the finding

`site/data/delivery.json` — a **published** page — carries, in the seat's own direction prose:

> *"We now have neither, measured: `co_calibrated: true`, `indistinguishable: true`, max divergence
> 1.80pp in 2023, zero years further apart than the band is wide."*

That is a **hand-authored copy of the verdict, in the present tense, on a live page**, and it is the
only place a reader meets these figures. It is consistent with origin's code *today* — and
`tools/couple_value_based_pricing.py` is sitting **staged and uncommitted** in this tree with the
company leg repointed from the prior to the posterior, which moves `co_calibrated` to `false` and
`sides_are_independent` to `true`. The moment that lands, the published sentence is false and
nothing anywhere will notice, because it is prose and its machine-readable form is a different
artefact. The derived sentence now published beside it cannot rot the same way; the hand-authored
one still can. Filed rather than fixed here: the delivery page republishes the direction verbatim
and rewriting a director-facing record to match a later measurement is not this lane's call.

---

## 2. The repair, and why it is computed and not read

`site/data/value_arms.json` now carries a top-level `inference_claim` block and
`site/capabilities/index.html` renders it into its own `arms-inference` element. The live reading
on this tree:

> *"The two sides are independent, which removes the objection that we were measuring our own
> reflection — it does not establish that the company knows anything. The gap is published as a
> measurement only: the method's ranking sits INSIDE the interval a random signal produces, so on
> whether the method works we cannot tell (0.333 against 0.133–0.867 for a signal carrying no
> information, on 6 decisions). The company's estimator is outside the published band in 4 of 6
> years, by up to 16.5pp — so this is independence and inaccuracy at once."*

**COMPUTED LIVE, NOT READ FROM THE RUN ARTEFACT, and finding (c) is why.** Every other figure on
that page is read from a run, correctly, because it is a measurement *of that run* and recomputing
it would mint a second source. This is not that: it is a **rule applied to today's code**, and the
committed artefact was the worked example of what reading one costs. `_inference_claim` imports
`shared_calibration_holds` lazily inside the function and fails closed on any exception — to
`available: False` plus the reason **and the words anyway**, because an unavailable check is a
failed check and the page says so rather than falling silent.

**ITS OWN ELEMENT, NOT A PARAGRAPH ON `arms-method`.** Both `method_skill` branches assign
`arms-method.innerHTML` and a run carrying neither assigns nothing. Sharing that element would
delete the verdict exactly on the runs where "we cannot tell whether this is evidence of anything"
matters most.

## 3. The three controls, and what each one actually catches

`site/test_the_baseline_comparison_reaches_the_reader.py`, mutation-proven **off-tree** (the door
copied to a throwaway file and the module's `DOOR` repointed in-process, so no concurrent lane's
pytest ever saw a mutated page):

| mutation | reds |
|---|---|
| drop the render | 3 of 3 |
| compose the prose from `ic.sides_are_independent` instead of rendering `ic.sentence` | 3 of 3 |
| render into `arms-method` instead of `arms-inference` | 3 of 3 |
| **nest the render inside `if (msk.available)`** | **1 of 3 — only `..._SURVIVES_a_run_that_carries_no_method_skill_reading`** |

The fourth row is the one that earns the third control its place: it is the only mutation the
other two cannot see, and it is the fail-open the obvious placement would have created.

The whole-sentence comparison was **wrong on the first pass and is recorded because it was**: the
door's `prose()` rewrites `" -- "` to an em dash before assigning, so an `in` test against the feed
string reports a correct page red. The controls now split the sentence on that same separator and
check every clause — which is the render-checker class already in the memory index
(*"a render checker that skips unescaping reads a string no reader ever sees"*), met from the other
direction.

---

## 4. What is still owed

* **The `belief_vs_truth` GAP itself still reaches no reader** — `median_belief_error_pp`,
  `scored_beyond_the_world_calibration`, the composed `refusal`. Only the verdict *about* the gap
  is published. That is the right order (a refusal without its subject is publishable; a subject
  without its refusal is not), but it is half a surface.
* **`site/data/delivery.json`'s hand-authored `co_calibrated: true`** — §1a. It goes stale the
  moment the staged repointing in `tools/couple_value_based_pricing.py` lands.
* **The staged repointing is not committed.** Another lane holds it in the index. Nothing here
  depends on it: the block is computed from whatever the tree holds, which is the point.
