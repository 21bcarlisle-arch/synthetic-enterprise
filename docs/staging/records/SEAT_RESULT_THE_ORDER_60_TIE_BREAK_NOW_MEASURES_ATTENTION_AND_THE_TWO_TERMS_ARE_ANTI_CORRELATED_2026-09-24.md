# RESULT — the ORDER 60 tie-break now measures attention; the two terms are anti-correlated

**Severity: RECORDED** — the repair is landed and controlled. Nothing is owed on this document.

Filed 2026-09-24 by the delivery seat. Answers
`records/SEAT_PREREG_WHAT_AN_ATTENTION_TIE_BREAK_DOES_TO_THE_LIVE_ALARM_BAND_2026-09-24.md`,
which was written before anything was run. The predictions are kept below beside their answers,
including the one that was wrong.

## What was wrong

`staging_rooms.work_queue()` sorted `(rank, mtime, name)` at all four sort sites. For
`KIND_ALARM` (rank 60), mtime is not age: `alarm_repetition` rewrites an alarm document on every
firing (`_note_still_live` appends a dated line, `_refresh_counts` rewrites the header). So the
term measured **how recently the alarm wrote**, ascending — the quietest condition first and the
loudest last. Anti-correlated with neglect, therefore inverted rather than arbitrary, and silent:
the band looked sorted by age because its own docstring said so.

## The predictions, and what happened

| # | Predicted | Measured |
|---|---|---|
| 1 | `DEADMAN_WORKTREE_UNDECLARED` is 10th of 10 under mtime | **REFUTED — 7th of 10.** |
| 2 | …and 2nd of 10 under the attention term | CONFIRMED — 2nd. |
| 3 | `OPERATIONAL_LAYER_SIGNAL` (newest filing) moves to 10th | CONFIRMED — 2nd → 10th. |
| 4 | Spearman(old, new) is negative; ≥7 of 10 documents move | CONFIRMED — **−0.709**, and 10 of 10 move. |
| 5 | A hand edit moves a document under the old term, not the new one | Holds structurally: the new key reads no mtime and no body text. |

**Prediction 1 was wrong and the reason is worth keeping.** `15e61d604` measured 34 of 34 over the
WHOLE queue; I re-read that as "last within its band" and it is not the same claim. The band order
churns continuously — every firing rewrites a document and re-sorts it — so an exact position
measured on Monday is not a fact about Wednesday. The claim that survives is prediction 4, which is
about the RELATION between the two terms and does not depend on where any one document sat.

## What the term is now

`alarm_repetition.unattended_since(path)` — the instant since which nothing has looked at the
document, ascending, so longest-neglected draws first. Three sources, each the honest answer for a
document the one above cannot describe:

1. The newest line under `REASK_HEADING`. The re-ask is somebody asking whether this still
   matters, and the module already keeps that section out of `_observation_dates` so that
   attention cannot masquerade as the condition holding. This is the other side of that same cut,
   and nothing read it until now.
2. Failing that, the FILING DATE in the filename — nobody has ever re-asked, so the last decision
   made about the document is the one that filed it. No firing moves it.
3. Failing that, `0.0`: the top of the band.

**Never `st_mtime`, at any step, including as a last resort** — that is the term this replaced, and
a fallback to it would restore the inversion for exactly the documents the other legs could not
describe.

**Today the population is entirely on leg 2.** Zero of the ten live alarm documents carry a
`## Re-asked` section: the re-ask landed 2026-09-23 and has not been applied. So the band currently
orders by filing date, which is what its docstring always claimed mtime gave it. Leg 1 arms itself
the first time the re-ask runs with `--apply`, and `test_MUTATION_a_reask_is_attention_and_moves_
an_alarm_down_the_band` is what proves it is wired rather than decorative.

## The controls, and the mutation that did not fire

Four in `tests/background/test_staging_rooms.py`, each proven by reverting the thing it names:

- the loudest alarm is not served last → red when the alarm branch returns mtime;
- a re-ask moves an alarm down the band → red when `unattended_since` ignores the re-ask channel;
- the term is scoped to the alarms → red when it leaks to every kind;
- an unpriceable alarm goes to the top of its band → red when the fail-open falls through to mtime.

**The fourth was written because its mutation went GREEN.** Nothing reached the `except Exception`
branch, so the fail-open DIRECTION was uncontrolled while three tests watched the happy path. A
missing test, established rather than assumed to be an equivalence. It now drives the branch by
making the term raise.

`QueueItem.mtime` is renamed `QueueItem.within_band`. The field held three different quantities —
a file's mtime, a class register's position, an alarm's attention staleness — and the name was true
of one of them. It is read at the four sort sites and nowhere else in the tree.

## What was NOT pinned, deliberately

No control asserting that body text does not affect rank. That keys to today's answer and would go
red the day the ranking becomes content-aware, which is the direction the map is going. The
controls above key to the property — the longest-unattended alarm draws first — and each arranges
mtime adversarially so that the old term returns the other answer.
