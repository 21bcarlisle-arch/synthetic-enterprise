**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The naive organ is silent because 104 of its questions are still open, not because it is broken (2026-11-03)

Delivery item `the-naive-organ-is-seen-to-ask`. The log had no entry after 2026-11-02T11:30:23Z, with
`naive-organ.service` running (pid 3640449, up since 03:30).

## Which of the four it was

None of the four named. One in-process cycle on 2026-11-03 at 05:29Z, through `python3 -m background.naive_organ cycle`:

| | count |
|---|---|
| triggers fired (T2 ×1, T3 ×10; T1, T4–T8 none) | 11 |
| asked | 0 |
| refused: same (trigger, claim) already `open` in the log | 11 |
| refused: purpose decline already on record | 0 |
| open backlog | 104, asked 2026-07-13 → 2026-08-10 |

The triggers fire and reach `ask_organ`. The debounce refuses each one because the same question is already open.
That debounce is correct: re-asking an open question is how the log filled with 27,663 identical declines. **The
organ has no new claim to ask about that it has not already asked, and nobody has answered 104 of its questions
in 85 days.** Only 7 questions have ever been answered.

## The change

Each cycle now overwrites a runtime tally file beside the log (.naive_organ_last_cycle.json, gitignored, never committed) with that tally. A
quiet log can then be read: "11 fired, 11 already open, backlog 104". Before, it could not be told apart from
the twelve-week fault. Test: `tests/background/test_a_silent_naive_organ_says_why_it_asked_nothing.py`. It first
shows that a cycle on today's LATEST.md with an empty log asks at least one question. It then shows that the re-run
asks nothing, and that the tally accounts for every fired trigger. Mutation-proven: disabling the debounce reddens
it, and so does dropping the refusal count.

## What is owed (recommendation)

Somebody has to work the 104 open questions down, or the organ stays silent by design. The work goes in bulk
through `answer_question` (with evidence) or `mark_verdict(entry_id, "miss")`. Most were raised on LATEST.md prose
from July and August that no longer exists. Those are misses by staleness, and marking them so releases the debounce.
I recommend one seat pass: answer the questions whose claim still appears in today's LATEST.md, and mark the rest
as misses. This needs no decision from the director.
