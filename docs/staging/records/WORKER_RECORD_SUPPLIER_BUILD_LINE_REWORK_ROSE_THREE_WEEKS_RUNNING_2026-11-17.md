**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Record: supplier_build's line rework rose three weeks running, 5% to 11% (2026-11-17)

This is one reading for the Friday review's rework line (the director's steer of 17 Nov, which the
seat executor is landing as E-r). It belongs to the machine and is not relayed to the director.

**Where it came from.** An autonomous worker drew the same steer at the same time as the executor and
built a parallel version. When the executor's landing was found in its gate, the worker stood its
version down unlanded. Its patch is kept outside the repo at `/var/tmp/cpr-worker/mine.patch`.

**The measure.** A behaviour commit (code under sim/, simulation/, company/, saas/, background/,
tools/ or site/, with test files left out) is counted at its lines. A line counts as reworked if it
was changed or removed within 14 days. The test is `git blame -M -w` at origin's first-parent state
14 days after the commit. Lines are not independent draws, so this share has no binomial bound.
Read its trend, not its decimals.

| week ending | all classes, commits reworked | all classes, lines | supplier_build, commits | supplier_build, lines |
|---|---|---|---|---|
| 13 Oct | 145/219 (60–72%) | 7% | 13/26 (32–68%) | **5%** |
| 20 Oct | 82/123 (58–74%) | 8% | 24/30 (63–90%) | **9%** |
| 27 Oct | 146/227 (58–70%) | 7% | 27/39 (54–81%) | **10%** |
| 3 Nov | 72/119 (52–69%) | 9% | 20/34 (42–74%) | **11%** |

Commit shares carry their Wilson 95% bounds. The weeks ending 13 Oct and 20 Oct also had no other
class above 9%.

**What the commit share cannot show.** Every class reworks 50–80% of its commits, and the bounds
overlap, so a "worst class" by commit share does not pick supplier_build. The line share does: it
is the only class that rose every week.

**Proposed action, for the Friday review to take or refuse.** Apply "trust gates autonomy" to
supplier_build. Read the week ending 10 Nov when it matures, on 24 Nov. If it rises a fourth time,
pre-register one added verification step on company/ landings, such as a mutation pass or a cold
read on billing and collections. Do that before any cheaper tier or wider autonomy for that work.
Change one variable only. Without a fourth rise, this record closes as noise.
