**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `six-knowledge-topics-have-two-homes-and-all-six-have-already-drifted`) · **Class:** `controls_that_cannot_fail`

# Six pages advertised a check that covered a body the reader cannot reach

**2026-09-09.** The drawn item had two halves: delete the losing copy of the six two-homed
Knowledge topics, and *record the re-check obligation the surviving copy inherits*. The first
half was already done and landed at `2a33bfa4f` earlier today. This is the second half, and the
obligation turned out to be larger than a note: **all six survivors were rendering a review date
that was earned by the copy that was deleted.**

Pre-registered before measuring:
`docs/staging/records/SEAT_PREREGISTRATION_DOES_THE_REVIEWED_BADGE_DESCRIBE_THE_BODY_THE_READER_IS_SERVED_2026-09-09.md`.

---

## 1. The defect

Every Knowledge page renders a review badge from `site/data/knowledge_wholesale.json` →
`topics[].reviewed.last_verified`, through `site/knowledge/review_state.py`. The **body** the
reader is served lives elsewhere — `site/data/knowledge_<topic>.json` for these six. The review
record is keyed to the **topic**; the body is keyed to a **file**. Nothing tied them, so a body
could move house and leave its review record behind.

| when | what happened |
|---|---|
| 2026-08-19 `bedb08ea4` | six pages **checked against source**, two corrected. The bodies checked were the entries in `knowledge_topics.json`. `last_verified` → 2026-08-19. |
| 2026-08-24 `0aa1c6d22` | six **new** files written "to replace a stub"; the pages were repointed at them. The graph was not touched. |
| 2026-09-09 `2a33bfa4f` | the reviewed bodies deleted as unread second copies — correctly, and that removed the last artefact this was discoverable from. |

The 08-24 bodies are not edits of the reviewed ones. Headline word overlap **10–39%**, and two
have a different title (`gb-electricity-market`: *"How Great Britain's electricity market is
arranged"* → *"How the GB electricity market fits together"*). They are different pages.

So for **sixteen days**, six public pages read *"Reviewed 2026-08-19"* over text nobody had ever
checked, citing sources fetched for a page that no longer existed. The two corrections that
review was proudest of — the Pool was abolished in 2001 and GB self-dispatches; Carbon Price
Support is levied per unit of fuel, not per tonne — do not appear in the live bodies, because
the live bodies are not about those things at all.

**Nothing went red.** The full `site/knowledge/` suite passed on 2026-09-09 with all six badges
false, and passed again, 106 green, after they were corrected. A suite that cannot tell those
two trees apart is not grading this.

### The seed of the recurrence, one level down

Each of the six bodies also stamped **itself** `"last_verified": "2026-08-24", "checked_by":
"worker"` — on the same day, in the same commit, that it was written. A write claiming to be a
check is the exact thing `review_state.py`'s own comment refuses (*"WRITTEN is not CHECKED"*) and
that `test_MUTATION_writing_a_page_does_not_reduce_the_risk_count` was created to pin **five days
earlier**. It survived because it sat in the home nothing renders and nothing grades.

## 2. What was measured

Instrument: for each topic, the body's own `meta.claim_freshness.written` against the graph's
`reviewed.last_verified`. Both already exist; no new bookkeeping.

| | |
|---|---|
| topics graded | 14 of 16 |
| **checks predating the body they cover** | **6 — exactly the six** |
| review tally, as advertised | `{fresh 16, unchecked 0}` |
| review tally, honest | `{fresh 10, unchecked 6}` |
| rendered value changed | **yes** — badge now reads *"Written, awaiting check · Written 2026-08-24. The explanation below has not been checked against the published source."* |

## 3. A prediction I got wrong, kept beside the right answer

**P4 predicted the defect was layer-wide** — that the badge/body split had nothing to do with how
many homes a topic had, so at least one of the five consolidated pages would show it too. My
first pass appeared to confirm it: `how-many-synthetic-households` flagged.

It was an artefact of my instrument. I was diffing bodies by **git commit date**, and that page
was written and verified on 2026-09-07 and landed on 09-08 — a one-day lag between doing the work
and committing it, not an untied badge. Re-measured against each body's own `written` date, it is
clean, and **the defect stops at exactly the six**.

P4 is refuted, and the refutation sharpens the finding rather than damaging it. The cause is not
the general badge/body split, which every page has and only these six suffered from. It is
narrower and more useful: **when a body changes FILE, the review record follows the topic and not
the body.** The five consolidated pages never moved house, so their record and body stayed
together. The two-homes framing in the drawn item was right, and my generalisation of it was not.

Recording the instrument error too: commit date is a weaker proxy for "when was this written"
than the field the author fills in saying when they wrote it, and it produces false positives in
exactly the benign case where work is committed the day after it is done.

## 4. What was done

1. **The six review records now tell the truth.** `last_verified: null`, `written: "2026-08-24"`,
   and the void check preserved under `superseded_check` with its reason — not erased, because
   the check did happen, it just does not cover this text. `review_state.py` already had the
   right state for this and needed no change: **UNCHECKED, "Written, awaiting check"**, which is
   fail-closed by construction.
2. **The six bodies no longer stamp themselves as checked.** `claim_freshness.last_verified` →
   `null` with a note naming the rule it broke; `checked_by: "worker"` removed. `written` stands.
   The rungs are byte-identical — asserted in the edit, and no reader loses a word.
3. **The class is closed, not the instance.** New control
   `site/knowledge/test_a_review_date_describes_the_body_it_serves.py`:

   > if a topic advertises `reviewed.last_verified`, the body that page serves must not say it
   > was `written` after that date.

   Keyed to the property, not to today's answer: silent while a check covers its body, loud the
   moment a body outruns its check.

**Proven against the real historical instance, not a fixture.** In a clean `git archive HEAD`
extract with only the new file added, it reds on **exactly the six** and names each one and both
dates; on the fixed tree, 18 green.

| poison | result |
|---|---|
| the unfixed tree at HEAD | **RED on all six**, no others |
| push one body's `written` to 2099 | RED |
| would the comparison run at all? | ≥8 pages reach the assertion (`test_MUTATION_the_rule_is_not_vacuous_on_the_real_record`) |
| drop a body's `written` to dodge grading | RED — the ungraded set is an **equality**, not a skip |

The first poison round I wrote **did not fire**, and that is worth keeping: it picked
`_gradeable()[0]` = `carbon-price`, one of the six whose date this same commit had just cleared,
so the comparison returned early and a live rule read exactly like a dead one. The poison round
found the defect in the poison round. The reason is written into the test.

## 5. Increment 2: the seventh page, and two more defects under it

Landed separately after `6ad1aa5d3`. "What is next" item 2 said `electricity-wholesale` was
ungraded and should not stay that way. Following it produced **a live instance, not a tidy-up.**

Its `claim_freshness` carried a field named `written_sections_2026_08_24` listing **five of its
seven rungs**, beside a note that was exactly right — *"That is authorship, not verification …
`last_verified` stays where it was"* — and correctly refused to move the date. But the badge went
on rendering **"Claims verified: 2026-07-25"** over a body five-sevenths written a month later.
**The note was honest and what it rendered was not**, and my new control could not see it purely
because the date was spelled in a *field name* instead of a field.

So the same correction was applied: `last_verified: null`, `written: 2026-08-24`,
`superseded_check` holding the void date. Honest tally is now **`{fresh 9, unchecked 7}`**.
`electricity-wholesale` leaves the ungraded set — only `weather-cells` remains, and it is not a
written Knowledge record at all.

Two further defects fell out, and both are the same shape as the finding itself:

1. **A control that went red when the page became more honest.**
   `test_both_staleness_dimensions_present` asserted `claim_freshness["last_verified"]` was
   *truthy* — it demanded the page claim a check, and fired on the day it admitted it had none.
   That is CLAUDE.md's *"key a control to the property, not to today's answer"*, with a live
   instance. Rekeyed: the dimension must be **answered** — a date, or a null **with what it
   supersedes**. A missing key and a bare unexplained null are both still red, poison-checked.

2. **The honest state reached the reader as the literal word `null`.** The stamp did
   `'Claims verified: '+esc(cf.last_verified)` with no branch, so the first render after the
   correction served **"Claims verified: null"**. Caught by driving the real markup against the
   real feed rather than by reading the diff. The page now branches, and
   `test_the_unchecked_state_reaches_the_reader_as_words_and_never_as_null` grades the sentence a
   reader actually gets: **"Claims: written 2026-08-24, awaiting check"**.

The poison round for that last one was run before the fix, not after: the unbranched page was
driven through the live harness and did serve the word `null`. 126 green in `site/knowledge/`.

**The general lesson, which is the finding's own shape one turn later:** telling the truth in a
record is not enough on its own. Three separate things — a control, a template, and a badge —
were each built assuming the answer would always be a date, and every one of them broke or lied
when the answer became *"we have not checked"*. **A system that cannot render "we cannot tell"
will quietly pressure every record into claiming it can.**

## What is next

1. **Seven Knowledge pages now honestly say they have never been checked, and that is a real
   debt, not a formatting change.** `gb-electricity-market`, `merit-order-residual-demand`,
   `gas-wholesale`, `carbon-price`, `imbalance-cashout-settlement`, `hedging-forward-market` —
   written 2026-08-24 from established mechanism, never checked against a published source. The
   2026-08-19 review of their predecessors found **two of six materially wrong**, which is the
   best available prior for what a real check of these six would turn up. This is the largest
   thing this turn leaves open and it is now visible on the pages themselves rather than hidden
   behind a badge that said otherwise.
2. ~~`electricity-wholesale` is ungraded and should not stay that way.~~ **Done in increment 2
   (§5)** — and it was a live instance, not the tidy-up this line expected. Every one of the
   sixteen topics is now either graded or, in the single remaining case, not a written Knowledge
   record.
3. **The `checked_by: "worker"` shape deserves a sweep beyond Knowledge.** A write stamping
   itself verified survived five days after the control against it shipped, because it lived in
   an unrendered, ungraded home. Nothing here establishes whether other feeds carry the same
   self-certification; the question has not been asked.
