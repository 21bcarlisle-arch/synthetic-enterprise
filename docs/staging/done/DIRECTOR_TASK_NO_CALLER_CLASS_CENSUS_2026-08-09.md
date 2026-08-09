# [DIRECTOR-TASK] — The no-caller class: count it, name it, one page (2026-08-09)

**Type:** [DIRECTOR TASK — REPORT ONLY, NO BUILD]. [DIRECTOR-PRIORITY]: a report about a class that keeps getting outranked should not itself be outranked; draw ahead of the general plate.

## CONTEXT / STATE ANCHOR
I reviewed an external autonomous-build harness (loki-mode) with the advisor to see what we could learn. The one idea worth taking was a per-commit evidence record: hard facts (change is non-empty, tests ran, each gate's verdict) separated from AI judgement, with a headline computed from the facts alone and every unproven thing named.

Before deciding whether to build anything, we tested it against our own history. It would have caught the case where a build's cell claimed done and the code had never been committed. It would NOT have caught our two most expensive recurring failures, because both sit downstream of a green commit: mechanisms wired to nothing, and published figures going stale.

That second one is the reason for this task. The no-caller failure has now appeared repeatedly in different disguises — including in a finding dated today. Each instance has been filed separately, as its own incident, because each looked different. Nothing on the board states the cumulative cost, which is why the class fix keeps getting outranked. The class fix for it is currently parked and, in the machine's own words, prose-only and therefore likely to evaporate.

## DECISIONS ALREADY MADE
- The per-commit evidence record is DEFERRED pending this page. Do not design or build it.
- This is a counting and naming task. Its output is one page.
- Report only. Fix nothing on sight, even if an instance is trivial.

## RESERVED — DO NOT TOUCH THIS TURN
- No new gate, hook, or mechanism.
- No change to any existing commit-time gate.
- No level move, no map edit beyond what the task itself requires.
- Do not archive or close the parked class-fix items.

## THE TASK
Produce ONE page that answers two questions with evidence:

1. Every instance of the no-caller class to date. I believe there are at least five, spanning: a mechanism with no production caller, a live mechanism with a permanently dead input, a tool wrongly recorded as its own caller, complete green work dying uncommitted in the tree, and a regeneration step that nothing ever runs. Confirm, correct or extend that list — cite the evidence for each, and state the date each was found and how it was found (deliberately, or by accident).

2. What ONE mechanism, had it existed at the first instance, would have caught all of them. If no single mechanism covers the set, say so plainly and state the smallest number that does, and why they cannot be one.

If the honest answer to either question contradicts my framing above, say so — an accurate count that shows this is two classes, or fewer instances than I think, is more useful to me than a tidy confirmation.

## WORK THIS CREATES (canonical, in-document)
One page, filed as a worker report; nothing else. Any fix it motivates is a future draw under its own priority, informed by the page.

— Directed 2026-08-09; staged by the advisor with the director's two additions (priority tag, this block); body verbatim the director's.
