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

## What is next

1. **Six Knowledge pages now honestly say they have never been checked, and that is a real debt,
   not a formatting change.** `gb-electricity-market`, `merit-order-residual-demand`,
   `gas-wholesale`, `carbon-price`, `imbalance-cashout-settlement`, `hedging-forward-market` —
   written 2026-08-24 from established mechanism, never checked against a published source. The
   2026-08-19 review of their predecessors found **two of six materially wrong**, which is the
   best available prior for what a real check of these six would turn up. This is the largest
   thing this turn leaves open and it is now visible on the pages themselves rather than hidden
   behind a badge that said otherwise.
2. **`electricity-wholesale` is ungraded and should not stay that way.** Its body IS the topic
   graph, which carries no `written` date, so the comparison has no second term — and that file
   is edited constantly, including by this commit. Its 2026-07-25 review date is the one
   remaining place where a check could drift from its body unnoticed. Giving that record a
   `written` date would bring it into grading; deciding what that date should be is a judgement
   about a note that deliberately holds its review date still, and I did not make it here.
3. **The `checked_by: "worker"` shape deserves a sweep beyond Knowledge.** A write stamping
   itself verified survived five days after the control against it shipped, because it lived in
   an unrendered, ungraded home. Nothing here establishes whether other feeds carry the same
   self-certification; the question has not been asked.
