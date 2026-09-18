**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# Both reds were one class at opposite ends, and repairing the fixture did NOT fix the second

**Filed:** 2026-09-18 · **Claim id:** `repair-the-stratified-fixture-then-land-the-09-18-republish`
**Pre-registration:** `docs/staging/PREREG_WHAT_REPAIRING_THE_STRATIFIED_FIXTURE_MOVES_ON_THE_TWO_REDS_2026-09-18.md`
**Discharges:** `docs/staging/done/SEAT_FINDING_THE_STRATIFIED_FIXTURE_CONSTRUCTS_ONE_OF_THE_TWO_FIGURES_ITS_ASSERTION_NEEDS_AND_INHERITS_THE_OTHER_2026-09-18.md`
**Subject:** `site/test_the_stratified_concordance_reaches_the_reader.py`, the 09-18 book promoted

---

## The predictions against the results

| | predicted before | measured |
|---|---|---|
| P1 fixture repair works, both books | yes | **held** — 22 passed 1 skipped on the 09-18 book AND on the 09-10 book |
| P2 it does NOT fix the second red | still red | **held** — 1 failed 21 passed 1 skipped after P1 alone |
| P3 second red is a two-state control over a four-state producer | yes | **held** |
| P4 final count | "23 passed, 0 failed" | **wrong as phrased** — 22 passed, **1 skipped**, 0 failed. 23 is the collected count, and I wrote the skip into the same sentence that denied it. No consequence; recorded because a prediction corrected after the answer is not a prediction. |

## What the finding got right, and the one thing it got wrong

The mechanism is confirmed exactly. Two corrections to its claims about the tree, kept beside it:

1. **The book on HEAD is `..._20260910.json`, not the 09-08 book the finding names** (md5 `bd0936be`).
2. **"`..._DECLARES` fails from the same cause and should be re-measured after the fixture is
   repaired rather than diagnosed separately" is wrong.** Same CLASS, different instance. That test
   takes the **live** feed as its subject and never calls the fixture, so no change to
   `rank_within_year` could reach it — and none did. It needed its own diagnosis, which is P3.

## The class, stated once, because both instances are it

> **A control that builds half its precondition and inherits the other half from whichever artefact
> is canonical is keyed to today's answer, however property-shaped its assertion reads.**

- `..._keeps_its_household_reading` constructed the **stratified** figure and inherited the
  **unstratified** one. `_auc_reading` gates on the unstratified bound FIRST.
- `..._DECLARES` derived the **household** gate independently and inherited the **reachability of
  any claim at all**. Neither constant is written unless the unstratified figure clears its null
  upward — past four refusals in `_auc_reading` — and on a run inside its null the producer writes
  neither, while the control demanded one be on the page.

Both passed for two months only because every book promoted in that time happened to clear that
null. The 09-18 book — 104 decisions, AUC 0.5566 against a null of 0.3871–0.6129 — does not, and
**the page is right to withhold**. The controls reported "the gate is refusing everything" about a
gate refusing exactly one thing, correctly.

## The repair, and the draft of it that was wrong

The fixture now recomputes `discrimination_auc` from the same mutated rows through the producer's
own `_pooled_within_year_auc`, so both figures are built and neither is borrowed, and asserts the
unstratified bound clears BEFORE asserting anything about the page.

`..._DECLARES` gains the gate above the gate — bound available, direction resolved, outside the
null, not below it — and a third branch asserting **neither** constant reaches a reader when the
producer declares neither.

**A first draft of that second repair was a fail-open and the mutation caught it.** It asked the
producer which constant its own reading contained and checked the reader met that one. That agrees
with the producer by construction: M2 below **passed** against it. The independent derivation of
`earned` from the stratified block is the whole grip of this leg, and reading the answer back off
the producer gives it away while looking more principled. Recorded because the draft was more
elegant than the thing that works.

## R15 — the mutations, each fired at its own named defect

| mutation | fires | on |
|---|---|---|
| **M1** drop the fixture's `discrimination_auc` recompute | `..._keeps_its_household_reading` | the new precondition assertion — it names the fixture's defect, not the page's |
| **M2** producer appends `_UNEARNED_CLAIM_SENTENCE` to the inside-the-null branch | `..._DECLARES` | the new third-state leg. **Passed against the first draft of the repair** — this is what refuted it |
| **M3** reword the earned claim to *"...who stays, household by household."* — still contains `HOUSEHOLD_CLAIM`, is not the constant | `..._keeps_its_household_reading` | the new pinning leg ALONE; the pre-existing `HOUSEHOLD_CLAIM` leg stays green, which is what proves the new leg is not a duplicate |

M3 is also why the pinning leg moved onto the null control: on a book inside its null the live
pinning is unreachable by construction, so without a constructed run that earns the claim, the
constant-vs-page comparison would go quiet on exactly the promotion that needed it.

## Evidence for the republish

Promoted `docs/observability/value_cycle_ab_s1_three_arm_20260918.json` → `THREE_ARM_PATH`,
regenerated `site/data/value_arms.json`. On that feed:

- `site/test_the_stratified_concordance_reaches_the_reader.py` — 22 passed, 1 skipped
- the same file on the 09-10 book — 22 passed, 1 skipped (the repair is book-independent)
- `tests/tools/test_generate_value_arms_data.py` + `tests/tools/test_the_renewal_funnel.py` — 274 passed
- the whole `site/` tree **with the feed STAGED**, which is the gate's own subject — **862 passed, 37 skipped**
- the same tree UNSTAGED read 861 passed 38 skipped and was blind to the eleventh control; the difference is the whole lesson below

## THE ELEVENTH, found by the gate after this file claimed the tree was green

The first landing attempt was REFUSED on a third control, in a file nothing had pointed at:
`site/test_the_baseline_comparison_reaches_the_reader.py::test_the_error_bar_says_the_instrument
_cannot_resolve_it`. It is the same class again, and two things about how it was found matter more
than the repair.

**My own whole-`site/` run could not see it, and said 861 passed.** That directory's doors take the
**published** feed as their subject — `published_blob` reads `git show :<path>`, the INDEX — so a
regenerated `site/data/value_arms.json` sitting unstaged in the working tree is invisible to them.
I ran the suite, read green, and was measuring HEAD's 09-10 feed against my repair. The gate stages
the paths first, which is the whole point of it. **Staging the feed before running reproduces the
gate's subject exactly** — that is the step that was missing, and it is a general one for any
`site/` door.

**The producer had already been repaired for this and the control was not.** `_error_bar` splits
the withheld sign two ways, and its own comment, dated 2026-09-18, ends:

> *"Caught by printing the block at real inputs before the test was written, which is the only
> thing that would have caught it: every assertion in the suite was about the verdict, and the
> verdict was right."*

That suite is this control. It kept one `else` for both reasons and demanded the precision
sentence. The tell was printed in its own failure message: *"the estimate sits 2.50 standard errors
from zero, **short of** the 2.1098..."* — 2.50 is not short of 2.11. A message whose own numbers
refute it.

One variable, HEAD's published feed against mine: `sems_from_zero` is **identical** (2.4954) and so
is the bar (2.1098). The only thing that moved is *why* the sign is withheld — promoting the 09-18
book makes the error bar **older than the figure it bounds** (spread measured 09-17T21:39:28Z,
estimate 09-18T05:43:40Z), so the producer withholds for a CLOCK reason rather than a precision
one, and says so at length. The page is right for the third time in this turn.

The control now branches on `sign_withheld_because` and pins the reason to the **payload**,
lower-cased at the seam exactly as the producer embeds it — so a reason the producer states and the
door drops is caught, rather than a sentence this file happens to know the words of today.

| mutation | fires |
|---|---|
| **M4** producer keeps `sign_withheld_because` in the feed and stops rendering it | the reason-reaches-no-reader leg |
| **M5** restore the pre-2026-09-18 producer (one reason for both states) | same leg — recorded as what fired, not as what I expected |
| **M6** render the reason AND the precision refusal beside it | the precision leg, which M5 left unproven |

**M6's first attempt passed, and it was a broken mutation, not an equivalence.** The patch dropped a
closing paren, the regenerate failed into `/dev/null`, and the stale feed stayed staged — so the
control was re-measured against unchanged bytes and read green. Establishing which of the three it
was (missing test / equivalence / broken simulation) is the rule, and it was the third. The
generator's output is no longer swallowed in these probes.

## One red this promotion does NOT move, measured rather than assumed

`tools.promoted_artefact_claim_census --check` refuses, and the instinct was to read that as this
promotion's doing — it is the one control written for exactly this move. One variable says
otherwise: it refuses **identically on HEAD's own 09-10 book**, same single STALE, same line.

    STALE tools/generate_value_arms_data.py:9854 (comment) token='2026-08-31'

Pre-existing, not mine, and left alone rather than folded into this landing. It also looks like a
false positive worth someone's half hour: that comment is *narrating the retired defect* — "this
sentence read 'published beside the 2026-08-31 run' until 2026-09-09" — so the census is firing on
a date inside the account of a bug that was fixed, not on a live claim. A census that cannot tell a
claim from a comment recounting a withdrawn claim will refuse every tree that documents its own
repairs, which is the behaviour this project keeps asking for. Filed here rather than fixed,
because it is a different subject and a contested file.

## What a reader now meets, and it is the honest answer

The page withdraws the household claim on this book and says why: the figure is inside its own null
on 104 decisions. "We cannot tell" is a result, it is on the surface, and no control now asks the
page to say otherwise.
