**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The drawn repair was already landed under the rival claim, and the one red it filed survived the merge

**Filed:** 2026-09-18 · **Claim id:** `repair-the-stratified-fixture-then-land-the-09-18-republish`
**Disposition:** `--landed-under` → `republish-the-arms-decomposition-over-one-priced-book`
**Subject:** `site/test_the_stratified_concordance_reaches_the_reader.py`, `site/data/value_arms.json`,
`docs/observability/value_cycle_ab_s1_three_arm.json`

---

## The premise, re-measured rather than assumed

The draw-time check said the one commit the item cites (`5167f1281`) was already an ancestor of
`origin/main` and told me to re-measure before starting. It is spent, and so is the rest of the item.

| what the item asked for | measured on this tree |
|---|---|
| repair the fixture so it builds BOTH figures | **landed** — `site/test_the_stratified_concordance_reaches_the_reader.py:691` recomputes `discrimination_auc` through the producer's own `_pooled_within_year_auc`, and `:701` asserts the unstratified bound BEFORE anything about the page |
| re-promote the 09-18 book to `THREE_ARM_PATH` | **landed** — `THREE_ARM_PATH` and `..._20260918.json` are md5-identical (`e87d3fc4…`); HEAD's previous book `..._20260910.json` is `bd0936be…` |
| regenerate `site/data/value_arms.json` | **landed** — committed, clean working tree |
| land it | **landed** — worktree HEAD `7bbf247ad` **equals** `origin/main`; nothing local is unpushed |

Both doors run green here: **189 passed, 2 skipped**
(`test_the_stratified_concordance_reaches_the_reader.py` + `test_the_baseline_comparison_reaches_the_reader.py`).

## Why it was drawn twice, and which id owns it

The draw-time duplicate-work note was right. The rival claim
`republish-the-arms-decomposition-over-one-priced-book` has **bound every path this item names**, and
this item's own claim row has `paths: []`:

    republish-…-one-priced-book   →  docs/observability/value_cycle_ab_s1_three_arm.json
                                     site/data/value_arms.json
                                     site/test_the_stratified_concordance_reaches_the_reader.py
                                     site/test_the_baseline_comparison_reaches_the_reader.py
                                     + the finding, the prereg and the result doc
    repair-the-stratified-fixture-…  →  (none)

So this is not two pieces of work on one subject — it is one piece of work drawn under two names, and
the one that did it is the one holding the paths. Taking `--landed-under` rather than `--release`,
because the work exists and is on `origin/main`; a release would put a finished repair back in the pool.

**The note that made this cheap was in the item itself.** The duplicate-work check named the rival
claim and named two of the exact paths. Reading the rival's bound path list before building is what
turned a full re-derivation into three measurements — the check earns its place.

## The red this promotion did NOT move, re-measured because its symptom had changed

`docs/staging/SEAT_RESULT_BOTH_STRATIFIED_REDS_…_2026-09-18.md` filed one refusal rather than fixing
it: `tools.promoted_artefact_claim_census --check`, one `STALE`, called a probable false positive and
left alone as "a different subject and a contested file". It is **still live after the merge**, and
two things about it have moved:

1. **The line moved, `9854` → `9883`.** The finding's own line number was an un-re-asked prediction
   and it went stale inside a day. The token and the file are unchanged.
2. **The refusal now prints alongside 90 `UNSUPPORTED`, 8 `ORDERING` and 2 `UNCHECKABLE` rows**, which
   is a different-looking output than the finding describes. Those are not new defects and not this
   promotion's doing — the `REFUSED` line is keyed to the single `STALE`, and the `UNSUPPORTED` rows
   are payload dates in `value_arms.json` the census does not treat as claims about which run sits at
   a path. Recorded so the next reader does not diagnose the volume instead of the refusal.

**The false-positive call holds, and the code is right.** At `:9883` the live expression is a
`{when}` placeholder resolved from the other panel's own payload — the comment directly above it says
so in capitals. The date the census flags is inside the comment's *account of the retired defect*:

> *"This sentence read 'published beside the 2026-08-31 run' until 2026-09-09, which was true for as
> long as `THREE_ARM_PATH` resolved to that run and became false the moment the 21:01Z re-take was
> promoted…"*

That is a withdrawn claim being narrated beside its repair, not a live claim.

## The class, and why it costs more than one refusal

> **A census that reads a date in a comment as a claim cannot tell a live assertion from a
> retraction, and will refuse every tree that records its own corrections.**

This one bites harder here than it would elsewhere, because "correct yourself plainly, in the record,
**beside the claim**" is a standing instruction in `CLAUDE.md`. A control that reds the tree for
obeying it pushes the next session toward deleting the account of the defect to clear the red — which
destroys the attribution and leaves the census green. That is the failure mode worth naming, and it is
the reason this is worth a repair rather than an allowlist entry.

**The remedy belongs at the census, not at `generate_value_arms_data.py`.** Fixing the instance means
editing a contested file to please a control that is wrong; fixing the class means teaching
`tools/promoted_artefact_claim_census.py` that a past-tense retraction is not an assertion. Left for
the next turn rather than half-done in this one, and handed off with that scope — **not** as a
narrowing that silences this one comment, which is the asymmetric-fix trap: the false positive gets a
comment and the weakened predicate gets none.

## What a reader meets

Unchanged by this turn, and correct: the arms page withdraws the household claim on the 09-18 book and
says why — the figure sits inside its own null on 104 decisions. No control now asks it to say
otherwise.
