**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The producer half of the churn belief is landed, and the site half is blocked on a feed only the publisher can write

**Landed:** `5e078b4d8`, five paths, gated by `tools.surgical_land`. Bound to
`the-churn-belief-publishers-still-say-flat-and-the-producer-half-is-unlanded`.

## What landed

`tools/churn_belief_size_response.py` · `tests/tools/test_churn_belief_size_response.py` ·
`docs/observability/churn_belief_size_response.json` · `tools/generate_value_arms_data.py` ·
`tests/tools/test_generate_value_arms_data.py`.

The two false sentences the drawn item named are repaired: `what_the_term_is` no longer says
`bill_stress` is "the ONLY place" `estimate_churn_probability` reads consumption (there are two at
HEAD), and its formula string now carries `BILL_STRESS_MAX_RATIO`, which `3b01193a8` landed and
which is what makes the deafness a SATURATION rather than an absence.

A **third** sentence was stale by the time I read it and is corrected beside itself: the docstring
bullet said whether the finding MOVED or CLOSED "depends on a term that is not committed yet" and
gave one reading per tree. `3b01193a8` spent that ambiguity. The same bullet carried "7 of 242
domestic legs" as a literal; it is 10 of 226 on the same book a day later with nothing about the
model changing, so the count is out of the prose — `reading()` composes it from the per-run census,
which is exactly why the PUBLISHED sentence did not go stale when the literal did.

**The drawn item's path list under-scoped by two.** It named four paths; the landing needed five,
and two of the five were not on its list. `_churn_belief_size_response`'s refusal re-key and
`_renewal_churn_belief`'s chain sentence live in `tools/generate_value_arms_data.py`, and the
producer's output keys moved under them. The first gate attempt landed the item's four and was
refused with eight reds — four in the consumer's own suite, four in the site door — which is the
one-variable control for this: my working tree was green on all of them because it held the
consumer's edit, and the tree the commit would create did not.

## What is NOT landed, and it is the half a reader will look for: the page still says FLAT

`site/data/value_arms.json` at HEAD carries *"the belief is FLAT in household size for 217 of this
book's 224 domestic supply legs"*. Row 1 of the blocking finding's `wrong` list is closed by
`5e078b4d8`; **rows 2 and 3 are not.**

Three paths are held back: `site/data/value_arms.json`, `site/capabilities/index.html`,
`site/test_the_flat_churn_belief_reaches_the_reader.py`. They pass together (15/15 on the door) and
red as a set when the WHOLE `site/` tree runs: **12 failed, 914 passed**, against **924 passed, 0
failed** on a pristine worktree at `5e078b4d8`. So all twelve are ours. Two independent causes,
each measured by adding one file at a time:

**Cause 1 — the feed cannot be regenerated anywhere I am allowed to regenerate it.**
`site/data/value_arms.json` ALONE reds two legs of
`site/test_the_baseline_comparison_reaches_the_reader.py`
(`test_a_reading_that_CLEARS_its_null_does_not_say_it`,
`test_the_page_tells_WORSE_THAN_CHANCE_apart_from_WE_CANNOT_TELL`): the page styles the
*"reads BETTER than chance"* paragraph amber, and amber is reserved for a verdict that QUALIFIES a
figure. This is a real page defect, exposed rather than caused by a fresher feed — the regeneration
adds `method_skill.reading_order`, which HEAD's committed feed predates.

**I tried to land the feed myself and must not.** Regenerating it in an isolated git worktree at
HEAD flipped `realised.is_the_published_supplier.run_identity.state` from `established` to `stale`
and withdrew the supplier claim outright, because the worktree cannot see the shared tree's newer
run artefacts. 121 leaves differ and only the churn block is mine. **A generated feed belongs to
the publisher, in the tree where all its inputs are.** Landing it from an isolated worktree is a
silent regression wearing a regeneration's clothes, and nothing in the gate would have named it.

**Cause 2 — the page's nav is stale against the register.** `site/capabilities/index.html` reds
`test_ia_register`, `test_every_served_page_takes_the_canonical_nav[index.html]`,
`test_evidence_links_resolve[home]`, `test_moap_coherence`, `test_moap_render` and
`site/test_a_producers_here_relative_pointer_has_one_home.py` (3 legs). The gate names its own
remedy: *"a page's committed nav is not what `site/ia_register.py` renders — run
`python3 -m tools.render_site_nav --write`"*. Mechanical, and unrelated to the churn belief.

## What the next lane should do, in order

1. Let the publisher regenerate `site/data/value_arms.json` in the SHARED tree. Nothing else is
   needed for the block to render — the landed consumer publishes it. **Do not regenerate it in a
   worktree or an extract.**
2. Fix the amber: the clearing verdict must not be styled as a caveat. One paragraph in
   `site/capabilities/index.html`.
3. `python3 -m tools.render_site_nav --write`.
4. Land `site/capabilities/index.html` + `site/test_the_flat_churn_belief_reaches_the_reader.py`
   together. Both hunks in the page are this work's; the door's own 15 legs are already green
   against the fresh feed.

## A prediction, filed before it is tested

Step 1 alone will take the published sentence off FLAT, because the consumer no longer refuses and
the reading is lifted verbatim. I expect it to ALSO red the two amber legs on the publisher's own
gate — the amber defect is in the feed's shape, not in who wrote it — so step 2 is not optional and
the publisher will hit it first. If the publisher's regeneration lands green, that prediction is
refuted and the amber is an artefact of my worktree's inputs rather than of the fresher feed.

## Not repaired, and said rather than left

`company/crm/churn_model.bill_stress_uplift_ceiling` is exported so
`tools/churn_belief_size_response.py` can ask the model for the bound rather than carry a second
copy, and it still does not call it. Deliberate: the census is keyed to the PROPERTY (does the
derivative reach zero on this leg), and calling the constant would key it to today's answer. The
constant's own docstring gives the now-spent "it was uncommitted" reason; this is the standing one.
