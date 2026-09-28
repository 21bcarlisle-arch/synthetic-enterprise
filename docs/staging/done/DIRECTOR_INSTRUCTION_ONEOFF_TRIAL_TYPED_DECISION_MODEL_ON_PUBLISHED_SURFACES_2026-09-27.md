# DIRECTOR INSTRUCTION — ONE-OFF TRIAL: a typed-decision model on published surfaces

Staged by the advisor on the director's behalf, 2026-09-27.
A single bounded experiment. Not a lane, not an adoption, not a dependency.
Report-only. When it is done, report and stop.

## Why

Every control this project owns is a binary assertion that blocks a
commit. That instrument has caught a great deal. It cannot catch the
class of defect the director keeps finding by eye:

- a published page with no route into it from the main nav
- chart stamps reading a year older than their own page's data date
- a figure on a page that its cited source does not support

The mothball ruling's third addendum already names this as a gap: an
error the project keeps finding by eye, which no control catches because
no deterministic expression exists. This trial tests one candidate
mechanism for closing it.

## The candidate

Jev, from TypeSafe AI. A "System One" model: it does not generate text,
it returns a typed decision — a choice, a score, or a yes/no with a
calibrated probability — in roughly 70-500ms at roughly $0.001 per
decision. Out of stealth 2026-09-15, version 1.13. Reachable via the
TypeSafe API directly, or via Vercel AI Gateway, OpenRouter or
Cloudflare. There is an MCP server and a LangChain integration.

The advisor could not test it: the sandbox network allowlist does not
include the endpoint, and no key exists. Obtaining a key is part of the
trial.

## The question this trial answers

Can a typed-decision model catch published-surface defects that no
deterministic control catches, at a cost that permits running it across
every surface on every publish?

Not "is it good". Whether it earns a place.

## Step one — research it before designing anything

Read TypeSafe's own documentation for Jev: its primitives, what shape of
question it answers, how it is called, how it integrates with Claude Code
specifically (there is an MCP server, an agent skill, and a LangChain
middleware), and what its stated limitations are. Then decide what the
best first trial is.

The method below is the director's advisor sketching one possibility from
the outside, having never called the thing. Treat it as an illustration
of the standard, not as the design. If the research shows a different
experiment would answer the question better — a different subject, a
different corpus, a different primitive entirely — run that one instead
and say why. The governance below is not negotiable; the method is.

## Method — a suggestion only, replace it if research says better

We already have a labelled corpus. It may be the right one to use.

**Known positives** — published surfaces at commits where a defect we
have since confirmed was present. The nav-route absence and the
stamp-vintage disagreement are two. The class documents in
`docs/staging/reference/` will yield more.

**Known negatives** — surfaces from the same period with no known defect.
Without these the trial measures nothing: a judge that flags everything
scores perfect recall and is useless.

**Questions to ask it** — bounded, answerable, one subject each. For
example: given this page and the site's link list, is this page reachable
from the main nav? Does this page's stated data date agree with its chart
stamps? Does this page assert a figure its cited source does not support?

**Score it** against what we already know. Report precision and recall
separately. A single accuracy figure hides the failure mode that matters.

## Two breaks that must be run

This is not optional and the trial does not count without them.

1. **Deliberate corruption.** Take a surface known to be clean, break it
   in the way the check is meant to catch, and confirm the verdict goes
   red. A judge that never says no has told us nothing.

2. **Adversarial content.** Put a page through it whose own text instructs
   the judge to pass it. Prompt injection influencing this model's
   verdicts is a reported weakness, and TypeSafe's own limitations note
   adversarial content as a known edge. LangChain's integration
   deliberately withholds fetched content from the classifier input so
   that material the agent retrieved cannot authorise its own execution.

   If the verdict flips, that is fail-open, and it disqualifies this
   mechanism from anything beyond report-only — permanently, not pending
   a workaround.

## Stated in advance — what would make this a no

Record these before running, and hold to them:

- If it misses the defects we already found by eye, it does not close the
  gap it was brought in for.
- If it flags surfaces we know are clean at a rate that would need a
  human to triage every publish, it has moved the work rather than done
  it.
- If the adversarial case flips the verdict, report-only is the ceiling.
- If the cost of running it across every surface on every publish is not
  materially below a full model judging the same surfaces, its single
  advantage is gone.

## Reserved — not authorised by this trial

- Nothing inside the wall. This looks at published surfaces only.
- It authorises nothing, gates nothing, and blocks no commit.
- No standing dependency, no service, no scheduled job.
- No second use case until this one has reported.

## Cost

Set a hard ceiling before starting and stop at it. If the trial cannot be
run inside a small, bounded spend, say so and stop rather than raising
the ceiling.

## What I want back

One page. Precision and recall against the labelled corpus, the result of
both breaks, the observed cost, and a plain verdict: does this close the
by-eye gap, or not.

If the honest answer is that the trial cannot be run as specified —
no key, endpoint unreachable, corpus too thin — say that instead of
substituting a different experiment.

## Epoch arc

Epoch 1 — governance and the published evidence surface. Not company
machinery. No model goes near the wall on the strength of this.

---

## Disposition — actioned 2026-09-27, archived 2026-09-28

Run once on the director's prepaid key (GitHub Actions run 36316887264, $0.0031). Verdict: **no**. It
does not close the by-eye gap. False alarms on clean pairs were 40%, recall on corruptions 0.64, and
there were 2 adversarial flips, so report-only is the permanent ceiling. Workflow deleted in
`a9da50c49`. The record is
`docs/staging/records/SEAT_PREREG_THE_JEV_TRIAL_IS_AIMED_AT_CLAIM_VERSUS_SOURCE_BECAUSE_THE_OTHER_TWO_CLASSES_ARE_CODE_2026-09-27.md`
and the corpus is `docs/trials/jev_2026-09-27/`. The stamp-vs-date class became the door
`site/test_a_chart_stamp_is_never_older_than_its_page.py` (`b2d2de01f`, which also made an unlinked
published file fail in code). Nav reachability was already held by
`tools/site_reachability.py`.
