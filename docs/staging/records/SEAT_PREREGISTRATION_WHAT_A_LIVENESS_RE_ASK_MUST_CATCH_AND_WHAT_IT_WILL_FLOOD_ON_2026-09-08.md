**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the level/selection re-take died in silence and its preregistration says it is in flight)

# PREREGISTRATION — what a liveness re-ask must catch, and what it will flood on

Written **before** the census is run and before the module exists. Beside
`SEAT_FINDING_THE_RETAKE_DIED_A_THIRD_TIME_AND_THE_KILLER_WAS_NEVER_THE_SESSION_IT_IS_THE_TICKS_CGROUP_2026-09-08.md`,
whose third owed item is *"no mechanism anywhere can notice a detached run has died"*. This is that
mechanism, and this file is what it must do stated before it can do anything.

## The defect, stated so it can be refuted

Three launches of the current-book re-take died. Each death was invisible until a person looked at
a pid. The 09-07 correction asserted its relaunch was live for **six hours after its subject was a
corpse**, and nothing in the repository disagreed with it — not a test, not a gate, not a daemon.
The document was the only record, and a document cannot re-ask.

**A pid is not the discriminator and never was.** All three dead launches had a live pid at every
moment a waiter looked; the 22:31 launch was watched for a full 300s and recorded live at 300s. The
verdict has to come from outside the killed cgroup, which is systemd, and it has to be re-asked at
a time nobody chose in advance.

## What I am building

`background/launch_liveness.py`. A detached run's launch record is a machine-readable block; the
control re-asks systemd and the filesystem for every block it finds, and refuses when a document's
in-flight claim is contradicted.

## Predictions, made before the census runs

I do not know these answers. They are recorded here so the census cannot be fitted to them.

| # | prediction | why I might be wrong |
|---|---|---|
| 1 | A prose scan for in-flight assertions over `docs/staging/**` returns **between 3 and 25** documents. Under 3 means my pattern is too narrow to catch the instance it exists for; over 25 means it floods and the second leg cannot ship as a hard gate. | I have not looked. The staging tree is 267 files and this project writes narrative records. |
| 2 | The 09-07 correction (`SEAT_CORRECTION_THE_FIRST_RETAKE_LEFT_NO_EVIDENCE...`) **is** in the returned set. If it is not, the pattern does not catch the one instance the mechanism was built for and is worthless whatever else it finds. | Its exact wording is unread by me at the time of writing. |
| 3 | Most hits will be **honest historical narration** — "the run was alive when this was written" — not live claims. I predict the majority of hits are past-tense and must NOT be refused. | If the majority are present-tense live claims, the tree has more stale liveness than this lane knows about, which is a bigger finding than the mechanism. |
| 4 | Exactly **one** `--user` unit on this box is currently active for a value-cycle run: `value-cycle-floor-current-book`. `value-cycle-ab-current-book` will read inactive with `Result=success`. | Another lane may have launched something. |

## What the mechanism must NOT be

Recorded in advance because each is a way this ships as a control that cannot fail:

- **Not a pid check.** A live pid is what all three deaths had. If the module reads `/proc` for its
  verdict it has rebuilt the thing that already failed three times.
- **Not fail-open on an unknown unit.** A unit systemd has never heard of, with no artefact, is
  precisely the 09-07 state. Passing that is passing the instance. It must refuse and say
  `UNVERIFIABLE`, not `finished`.
- **Not fail-open on a broken probe.** If `systemctl` cannot be run at all, that is an unreadable
  probe and not a dead subject — `wait_for.py` already learned this distinction and paid for it.
  These two must be separate verdicts, because reporting "gone" when we could not look is how a
  control tells a caller a run completed when it had not.
- **Not vacuous.** A control that only re-asks blocks nobody writes passes for ever. The second leg
  — a document asserting in-flight must carry a block — is what stops that, and prediction 1 is
  what decides whether it can ship as a gate or only as a report.

## The one that would make this a control that cannot fail

If every verdict the module can return is reachable only when a run is *already* known dead, it is
a diagnosis and not a control. The poison round is: **take the currently-live floor unit, assert it
reads IN_FLIGHT, then re-ask a fabricated unit name and assert it reads UNVERIFIABLE.** Both legs
over one partition, in one control, so a module that returns a single constant fails. Asserted
before written, so it cannot be written to fit.

## What this preregistration does not claim

Anything about level versus selection. That question's artefact exists
(`value_cycle_ab_current_book_2026-09-08.json`) and its floor leg is running; both are the subject
of the record beside this one. This file is about the launcher only.
