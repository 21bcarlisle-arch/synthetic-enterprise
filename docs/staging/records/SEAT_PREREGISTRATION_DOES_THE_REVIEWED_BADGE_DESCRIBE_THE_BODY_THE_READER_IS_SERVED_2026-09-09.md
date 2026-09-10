**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `six-knowledge-topics-have-two-homes-and-all-six-have-already-drifted`) · **Class:** `controls_that_cannot_fail`

# Pre-registration: does the "Reviewed <date>" badge describe the body the reader is served?

**Written 2026-09-09, BEFORE measuring.** The drawn Lane 0 item has two halves. The first —
delete the losing copy of the six two-homed topics — landed at `2a33bfa4f`. This registers the
second: *record the re-check obligation the surviving copy inherits.*

## The mechanism, established before predicting

Every Knowledge page renders a review badge. Its state comes from
`site/data/knowledge_wholesale.json` → `topics[].reviewed.last_verified`, through the rule in
`site/knowledge/review_state.py` (mirrored into each page's JS). That rule is fail-closed on a
*missing* date: no date ⇒ DUE, never fresh.

The **body** the reader is served is somewhere else. For the six survivors it is
`site/data/knowledge_<topic>.json` → `rungs`. For the other five it is
`site/data/knowledge_topics.json` → `pages[<slug>].rungs`.

So the badge and the body have different homes, and `review_state.py` answers exactly one
question — *when was this last checked against the world* — and deliberately not *is the page
good*. Nothing in that rule can see whether the body changed after the date it advertises.

**The hazard being tested:** a page can be rewritten after its `last_verified` date and keep
advertising "Reviewed <date>" — a fresh badge over text nobody checked. That is fail-OPEN in the
one direction the rule's own docstring does not cover, and it is the obligation the surviving
copy inherits: it is now the *only* copy, so if its badge is untied, nothing anywhere holds it.

## Method, fixed now so it cannot be fitted to the answer

For each topic, take `D = reviewed.last_verified`. Take `C = git rev-list -1 --until="D
23:59:59" HEAD` — the tree as it stood on the day the review was recorded. Compare the topic's
`rungs` in `git show C:<body file>` against `rungs` at HEAD.

- unchanged ⇒ the badge describes what the reader is served.
- changed ⇒ the badge is a claim about superseded text.
- body file absent at `C` ⇒ the entire body postdates the review.

The comparison is on `rungs` only, not the whole file: a citation or a title edit is not the
body, and counting it would inflate the result in the direction I am predicting.

## Predictions

- **P1.** For **at least 3 of the 6** survivors, `rungs` at HEAD differs from `rungs` at `C`.
- **P2.** `gb-electricity-market` and `gas-wholesale` are both among them. These are the two
  whose `meta.title` differed between the two homes when measured at `2a33bfa4f` — a title
  divergence is the tell that the live body was rewritten late.
- **P3.** No control in the tree reds when a body changes after its `last_verified`. Operational
  test: nothing under `site/` or `tests/` reads a body file *and* `reviewed.last_verified` in a
  way that could compare them.
- **P4 — the discriminating leg, and the one I expect to be told I got wrong.** This is either
  an obligation the *six* inherit, or a property of the whole Knowledge layer. If **at least one
  of the five `knowledge_topics.json` consumers** also has `rungs` changed since its
  `last_verified`, then the two-homes framing is not the cause and the finding is layer-wide.
  **I predict at least one does** — the mechanism has nothing to do with how many homes a topic
  had, so a defect that stopped at the six would need a reason, and I have none.

  P4 is what makes P1–P2 falsifiable as an *explanation* rather than just true. If P4 fails and
  only the six are affected, my account of the mechanism is wrong and I must find the real one.

## What would make me drop this rather than file it

If every one of the sixteen topics is unchanged since its review date, there is no live
instance, and the untied badge is a latent shape — worth one sentence in the record, not a
finding, and certainly not a new control. **A control built for a hazard with no instance is the
"file made of rules" CLAUDE.md refuses.** I will say so plainly if that is the result.
