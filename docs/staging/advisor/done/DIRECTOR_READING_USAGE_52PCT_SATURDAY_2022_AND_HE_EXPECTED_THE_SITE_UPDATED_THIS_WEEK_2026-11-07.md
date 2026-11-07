**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage at 52% on Sat 7 Nov, 20:22 GMT, and he expected the site updated this week

**Type:** READING, through the advisor channel. The director's words, from chat:

- Sat 7 Nov, 20:22 GMT: "52% I thought we were going to get the website updated this week to use spare credits ?"

## The reading

- Plan usage was **52%** at 20:22. It was 49% at 16:15, so the burn is about **0.75 points an hour** [derived].
- The reset is Mon 9 Nov 03:00 GMT, about 30.6 hours away. Keeping about 10 points for Monday leaves about **38 points**, or about **1.2 points an hour** [derived]. There is spare. Spend it.

## What he is telling you

- The site's figures still show run 0a6391d186, verified on 3 Nov. That run is four days old, and two of those days were lost to the outage.
- He expected the spare tokens this week to show on the site. A Monday publish that cannot happen, because the shared tree is pinned (see the 20:20 chase), would mean a second week with nothing new to show.

## What is asked

1. Unpin the shared tree tonight (the 20:20 chase). Every later step depends on it.
2. **Publish as soon as a book passes the full gate. Do not wait for Monday because that is the usual day.** If a director ruling fixes the publish to Monday, cite it in the next commit, and the advisor will put the question to him. If only habit or the schedule holds it, publish early.
3. If no book can pass the gate by Monday, say on the site's status line which gate is refusing and why. "Not updated" should never be silent.
4. Spend the spare points on the gate's refusing rows and on the cold-read gaps that block a publish. Do not spend them on new features.

## Done (delivery seat, 2026-11-07 21:10 GMT)

1. **Unpinned.** The shared tree fast-forwarded 20 commits, fa915ac0d7 to f248d5ffa, at 21:00 UTC
   (reconcile-watch: `FAST_FORWARDED [settled]`). The N15/N16 rows were not stranded work: they had reached origin
   in f7f0a8ca43. Every refusing copy was superseded by origin. Each was preserved, then refreshed or set to
   origin's bytes. The only unlanded writing was three orientation entries in the stretch log, and those landed in
   f248d5ffa. Preserved bytes: `refs/preserved/unpin-2026-11-07/*` and `refs/preserved/refresh-to-head/unpin-2026-11-07*`
   in the shared repo, with copies and a MANIFEST in `/var/tmp/shared-tree-unpin-evidence-2026-11-07/`. sim-runner's next
   run starts about 21:34 UTC from the new HEAD. That run is the first book that can carry 8b6316995.
2. **The Monday publish is held by a director ruling, not by habit.** His words, 26 Sep 09:29 UTC: "Make it real,
   and anchor it to Monday rather than a rolling seven days: publish on Monday after the reset"
   (`docs/design/canon_review_2026-10/inputs/director_words_filtered.md:35`, enforced by
   `background/publish_freshness.content_publish_window`). So the window was not overridden. The question went to
   him as `the-publish-window-is-anchored-to-monday` in `for_the_director`, recommending one early publish this week
   as soon as a book passes the full gate.
3. **Not done, handed on.** If no book passes the gate by Monday, the site's status line must name the refusing
   gate. That step depends on the 21:34 book's grade, so it was handed on as a continuation.
4. Spend: this turn went on the unpin only. No new feature work was drawn.
