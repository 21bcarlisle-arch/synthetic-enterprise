# SEAT FINDING — three Knowledge pages carry their review class in two homes, and the copy the reader gets is not the copy the author set

**Severity:** LATENT · **Lane:** H_harness

**Date:** 2026-09-10 (delivery seat, lane 0 draw — found while checking the four remaining unchecked pages)

---

## The defect

How long a Knowledge page may go unchecked before the badge says "review due" is set by its
rate-of-change class. That class is written down **twice**, in two files, and nothing compares them:

| home | field | who reads it |
|---|---|---|
| `site/data/knowledge_wholesale.json` → `topics[].rate_of_change` | the index | **`review_state.threshold_days()`** — drives the badge and the threshold |
| `site/data/knowledge_<topic>.json` → `meta.rate_of_change_class` | the page's own body | nothing |

Three of the ten pages that carry both disagree:

| topic | index (read) | body (ignored) | effect |
|---|---|---|---|
| `carbon-price` | `medium` (183d) | `fast` (92d) | author asked for 92 days; reader gets 183 |
| `imbalance-cashout-settlement` | `medium` (183d) | `slow` (365d) | author asked for 365; reader gets 183 |
| `electricity-wholesale` | `medium` (183d) | `slow` (365d) | author asked for 365; reader gets 183 |

Seven agree. The divergence is silent in both directions and has no reader, so neither copy is
ever forced to justify itself.

**Why it is LATENT and not merely untidy.** The body copy is what an author edits when they think
about how fast their subject moves — it sits next to the prose, in the file they are writing. The
index copy is what the reader is actually graded by. Two of the three divergences would have made
the badge *slacker* than the author intended, and `carbon-price`'s would have made it **twice** as
slack. The control that exists here (`review_state.py`) is carefully fail-closed about a *missing*
date and completely blind to a *contradicted threshold*.

This is the project's recurring two-homes shape, in the file whose whole job is to tell a reader
how much to trust a page.

## What this turn did, and what it deliberately did not

**Fixed, because the check settled it:** `imbalance-cashout-settlement` body `slow` → `medium`.
Not by preference — the same check established that MHHS compresses that page's central timetable
from 1 October 2026, three weeks after the check. A subject whose timetable changes in three weeks
is not slow-moving, so the index copy was right and the body copy is now corrected to agree.

**Not fixed, because nothing here settles them:** `carbon-price` (`fast` vs `medium`) and
`electricity-wholesale` (`slow` vs `medium`). Picking a winner to make the numbers match would be
choosing an answer to silence a disagreement, which is how the divergence got here. Both need the
question asked properly: *how fast does this subject actually move?* — `carbon-price` now states a
statutory rate frozen to 31 March 2028, which argues for the slower class its index already has,
and against the `fast` its body asks for.

## The remedy

An equality over data that already exists, in
`site/knowledge/test_a_review_date_describes_the_body_it_serves.py` — which already resolves each
topic's body feed from its own markup, so it has both terms in hand and needs no new machinery:

> if a body declares `meta.rate_of_change_class`, it must equal the index's `rate_of_change`
> for that topic.

Keyed to the property, not to today's answer: silent while the two agree, speaks the moment they
part, whoever writes them. It cannot land until the two remaining divergences are settled — which
is the point, and is why this is filed rather than written today. Writing the control first and
adding `carbon-price` and `electricity-wholesale` to an exceptions list would reproduce the
allowlist-excusing-its-own-subject pattern this project has already paid for.

## How it was found

Not by looking for it. The four-page check needed each page's rate class to know its threshold,
read it from the body file, and got a different answer from the index the badge uses.
