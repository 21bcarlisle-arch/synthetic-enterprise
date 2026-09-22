# A window that closed before its own subject existed now says so, and the drawn remedy was refuted

**Severity:** RECORDED · **Lane:** H_harness

*Worker, 2026-09-18 05:15. Lane 0 delivery claim
`the-lanes-new-evidence-path-has-never-fired-against-a-real-sweep`.*

---

## What the item asked, and what was already true

The item asked to prove that `69d5f071c`'s new evidence path (`_landed_by_sibling`, which derives
`LANDED_ELSEWHERE` from the join `_bound_by` already computes) fires on a **live** sweep rather than
only in its own tests. Its stated premise was that the repair "is written; what is unproven is that
it fires", because the only row swept this stretch was swept before the commit landed.

**The premise is refuted, and the path was already firing.** Asked of the live draw ledger (396
rows) this turn:

| disposition | rows | route |
|---|---:|---|
| `delivered` | 334 | own name |
| `not_done` | 50 | the residual |
| `landed_elsewhere` | 8 | **6 hand-stated `--landed-under`, 2 DERIVED by `_landed_by_sibling`** |
| `premise_spent` | 3 | hand-stated |

The two derived rows are `establish-what-drops-fourteen-of-the-twenty-priced-decisions` (credited to
`attribute-the-churn-auc-move-from-0-4653-to-0-13`, `158da2878`) and
`execute-the-reconcile-the-refusal-now-prints-instead-of-labelling-it-a-ninth-time` (credited to
`the-two-arms-have-never-priced-the-same-population-and-the-page-says-they-have`, `b329e702b`). Both
carry non-empty evidence naming their sibling. Neither was the row the item named.

Two corrections to the item's own account, recorded beside it rather than over it: `69d5f071c`
landed at **03:04**, not 02:04; and the row it named is not the only thing the sweep had to say.

## The row the item named, and why both offered remedies are wrong

`read-the-next12-twelve-alone-once-the-0358-run-settles`, written 2026-09-17 23:52, drawn
2026-09-18 00:07:03. Its own prose:

> The run exec'd 20:11:48, 13.0 min per arm-leg, **ETA near 03:58; do not draw this before then, the
> file will not exist.**

Its window — 100 minutes plus the landing grace — closed at **02:47**, an hour and eleven minutes
before the artefact could exist. Measured at 05:15 today, `/var/tmp/value_cycle_ab_s1_noise_floor_
next12_20260917.json` **still does not exist** and its producing run (PID 3819244) is ten hours in.

The item offered `--premise-spent` or `--landed-under`. **Both are refuted by the evidence:**

- `--premise-spent` asserts a commit had *already consumed* the premise, and requires that commit to
  be an ancestor of `origin/main`. There is no such commit. The premise had not *arrived*; it is the
  mirror of spent, and recording it as spent states the opposite of what was measured.
- `--landed-under` asserts a sibling delivered the subject. The three later re-issues of this
  subject landed ETA instrumentation, not the next12 reading. Crediting them would claim a reading
  nobody has taken.

Writing either would have put a false sentence in the store to make a dial read explained. The item
was right that the row's cause is *premise-not-yet-ripe*; it was wrong that the lane had a command
that could say so.

## What landed

`PREMISE_NOT_YET_RIPE` — a **fifth disposition value**, derived, asked **last** of all four existing
readings, so it can only ever replace an empty string and never a populated one.

It fires when the item's own prose states an instant and `drawn + CLAIM_STALE_SECONDS +
_landing_grace_seconds() <= that instant` — the *whole* window, grace included. A row drawn five
minutes before its subject appears had ninety-five usable minutes and is an ordinary miss; including
the grace makes the condition stricter, which is the direction a reading that excuses a miss must
err in.

**A third live spelling of the embargo was the reason nothing could read it.** `_EMBARGO`'s own
docstring warns that a grammar accepting only the phrasings in front of it is "a guard with a silent
off-switch". This is that off-switch found in the wild: the dated forms (`DO NOT DRAW BEFORE 10:45
on 2026-09-18`) are read, and the back-referenced form (`ETA near 03:58; do not draw this before
then`) is not. `_back_referenced_start` reads it, anchored on the **draw instant** so a row's
disposition cannot drift day to day.

**It is deliberately NOT wired into the draw, and that boundary is the point.** `_embargoed` asks
the same question of the same prose to decide whether to *hand work out*; a stamp invented there
from a loose grammar costs every invocation in the window — the empty lane visible to nobody that
`draw`'s six-day walkover already paid for. This reading can only explain a window that has already
closed. Same regex, same resolver, different anchor, and only one of the two can cost the lane a
tick. **Wiring the back-referenced spelling into the draw is the next item and needs its own care.**

## Done means the live store says it

```
$ python3 -c "...disposition_of('read-the-next12-twelve-alone-once-the-0358-run-settles')"
{"disposition": "premise_not_yet_ripe",
 "evidence": "the item's own prose puts its subject at 2026-09-18 03:58 -- 1.2h after this
              window closed, so no turn under this claim could read it"}
```

**One row in 396.** No false positives; the 50 genuine misses stay loud with an empty string. The
orientation brief carries it through automatically, and gained the one clause a reader needs: a
`premise_not_yet_ripe` row is the *opposite* instruction to the others — do not go looking in the
tree, and do not draw it again until the stated instant has passed.

## The control, and the mutation that did not fire

`tests/background/test_a_window_that_closed_before_its_own_subject_existed_says_so.py`, eight legs,
opening with a partition control over all six readings from one ledger. Ten mutations applied
**in-process** (never to the shared tree — two sibling pytest runs were live on it); the unmutated
control is green and all ten fire.

**One did not, at first, and it was a missing test rather than an equivalence — established, not
assumed.** Dropping *both* digit guards from `_CLOCK_TIME` left the answer unchanged: on the live
sentence the timestamp sits *before* the ETA, so the nearest-antecedent rule discards it anyway and
the guards never had to do anything. Each guard needs its own ordering to be graded —
`(?<![:\d])` only by timestamp-first, `(?![:\d])` only by timestamp-last — so the control now
asserts both, and the two mutations fire separately. Recorded in the control's own header.

The first draft also combined the time and the instruction into one regex. `Ignore the 22:30
checkpoint. ETA near 03:58; do not draw this before then` matched **once, at 22:30**: a left-to-right
scan anchors on the earliest time that can reach the instruction and consumes everything between, so
the real antecedent was never offered as a candidate. Scanning for the instruction and looking
*backward* is the only order in which "the last instant named before `then`" is askable.

## Still owed

1. **The draw does not honour the back-referenced spelling.** This row was drawn four times, each
   time hours early, each time burning an invocation. That is the defect that *cost* the window;
   this turn made the cost legible, it did not stop it. It is a withholding decision and wants the
   care the fail-open direction in `embargoed_until`'s docstring argues for.
2. **The 50 `not_done` rows are unexamined** — that is the genuine residual and it is still the
   largest group after `delivered`.
