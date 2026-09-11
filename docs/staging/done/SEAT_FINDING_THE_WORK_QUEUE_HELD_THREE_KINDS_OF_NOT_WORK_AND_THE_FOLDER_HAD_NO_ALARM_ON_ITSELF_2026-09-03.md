**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# The work queue held three kinds of not-work, half the pile was already dispositioned, and nothing in the tree had ever read the folder

*Delivery seat, 2026-09-03. Answers the director's staging instruction of the same morning.*

---

## 1. The ask, and the measurement taken before anything moved

> *"Staging is at 168 in the root and 120 in progress — up from 15 on 28 August, eleven-fold in six
> days. 153 of the 168 are your own documents: 85 findings, 51 pre-registrations, 17 seat findings.
> The prioritising works. The clearing doesn't, and the reason is that filing is free and
> dispositioning isn't. Fix the class, not the pile."*

His count is exact and it is `git ls-files`: **168** tracked documents in the root — 85 findings, 55
pre-registrations, 17 seat findings, 7 director documents, 4 other. The pile turned out to be
**four different problems**, and only two of them are what "the clearing doesn't work" describes.

| | count | what it actually was |
|---|---|---|
| already dispositioned, never committed | **89** | a LANDING failure |
| pre-registrations in the work channel | **55** | records with no exit |
| findings drawing at the wrong rank | **16** | a classifier keyed to one channel |
| findings graded RECORDED | **11** | landed, nothing owed |

## 2. Half the pile had already been decided and the commit never happened

**89 of the 168 were not in the root at all.** Deleted from `docs/staging/`, deletion never
committed, dispositioned copy untracked in `done/`. Checked one by one rather than sampled: **89 of
89** had a copy in `done/`, 75 byte-identical to the root version at HEAD, 14 carrying an appended
result or disposition (+1 to +127 lines, no rewrites). Nothing had been lost and nothing was
sediment; the work of deciding them was done days ago.

**This is not only a counting error.** The same shape armed a red that morning:
`tests/architecture/test_switching_rate_commons.py` was green at HEAD and red in the shared tree
because three of these very documents had been deleted without being committed and a citation
resolved nowhere. An archive move started and not landed arms a red for every lane, and the lane
that trips it reads it as its own breakage. Landed at `04ba0e387`, 178 paths.

## 3. A pre-registration has no exit, so it cannot sit in a queue

This is **D2 one kind further on**. D2's argument — a document that can never be actioned-and-
archived keeps the queue from ever reaching zero, so it cannot signal "drained" — was made about
class registers and console transcripts on 2026-08-28. A pre-registration is the same shape and for
a stronger reason: it is a prediction filed **before** its measurement, so acting on it would mean
running the measurement (a different document's work) and revising it would destroy the only thing
it is for. All it can do is be **graded beside a result**.

`records/` and not `done/`, deliberately: `done/` means dispositioned and out of the way, and
`staging_archive_policy` may fold an archived document once it is old and unreferenced. A
pre-registration must stay readable for as long as the claim it graded is published, because it is
the only evidence the experiment was designed before its answer was known. Filing it as done would
put the machine's own falsifiability record on an archive path. **38 moved; floor set at 38.**

**A token, not a prefix.** The 55 carried four different name shapes — `SEAT_PREREGISTRATION_`,
`WORKER_PREREGISTRATION_`, `PREREG_`, and `SEAT_PREREGISTRATION_WHETHER_`. A prefix tuple would have
caught whichever ones its author had in front of them and left the rest in the work channel, reading
as "pre-registrations are handled".

## 4. The seat's own findings had never been classified

`_FINDING_PREFIXES` was `("WORKER_FINDING_", "WORKER_ALARM_")`, written when the worker turn was the
only channel filing findings. The seat then started writing `SEAT_FINDING_`, and **all 16 of them in
the root classified as `KIND_UNKNOWN`** and drew at rank 50 — below every finding, above every alarm
— under the comment *"unrecognised, so treated as a real ask until shown otherwise"*.

Nothing was lost, because UNKNOWN fails safe toward work. What was lost was the **order**, silently,
for as long as the seat has been filing. A new channel adopting an existing document kind must not
have to remember to edit a tuple; the kind is what a document IS and its name says so.

## 5. Eleven were reports of things already fixed

**11 of the 36 findings in the root were graded RECORDED** — `finding_severity`'s own word for a
landed record with nothing owed. `finding_classes.derive_memberships` already drops RECORDED from
consolidation on exactly that reasoning (*"a landed record with nothing owed has no repair to argue
and no cost to add"*); the work channel was the last place in the pipeline still offering them.

Read in `work_queue` and not in `kind_of`, and that split is the same one the class registers take:
the KIND is what a document is and comes from its name; the SEVERITY is what is owed and can only
come from its body. `_is_recorded` fails toward WORK on anything it cannot parse — the harmful
mistake is dropping a live finding because its file could not be read.

## 6. The register could not take the instances, and the reason is worth more than the move

The director: *"Findings that share a class go to the class register as instances, not to the root
as documents; the register already exists for exactly that."*

**It exists, and the step that moves the member was never written.** `derive_memberships` picks the
members, the lane guard refuses what it may not supersede, `render_class_document` writes them into
the register as an instance list, `archived_instances` reads them back out of `done/`,
`instance_paths` spans both rooms, and `check()` verifies the whole thing holds. The register's own
printed text says the members are *"archived, not deleted, in `docs/staging/done/`"*. **Nothing
moved them.** So every classed finding was named as an instance in a register AND left in the root
as a document, and the register — built so one argument can win a draw instead of twenty siblings
losing separately — became a second copy of the pile rather than a replacement for it.
`consolidate()` is the missing step, added here.

**And it moves nothing today, for a reason that is a finding in itself.** Of the 13 classed
documents in the root:

| | count | why not consolidated |
|---|---|---|
| refused out of lane | **9** | the register's lane is `H_harness`; the document's is `W2_customer_generator` (6) or `D_billing_metering` (3) |
| RECORDED | **4** | landed, nothing owed — correctly dropped upstream |
| live members | **0** | |

**All six class registers are declared in `H_harness`, and a class is by definition cross-lane.**
`measurements_that_mirror` is an H_harness register and every live instance of it is in W2. So the
register can only ever hold instances from its own lane, and the cross-lane majority stays in the
root as documents indefinitely — which is a large part of the pile the director is reading.

The lane guard is **not** widened here. Its reason is stated and correct: archiving a document under
another lane's register would remove that lane's blocker while filing the cost under someone else's.
Fixing this properly means a register that spans lanes and reports per-lane blockers, which changes
what `_blocking_lane_draw` freezes. That is a design change with a live control on the other end of
it, and it is filed rather than bolted on.

## 7. Nothing had ever read the folder

Every control in `staging_rooms` reads the **documents**. None read the **root**, so it could go
from 15 to 168 in six days without a single thing in the tree having an opinion.

`root_flow()` measures **flow, not size**: how many documents entered the root against how many left
it, over the seven days the director's own measurement spans. A size cap is a threshold and a
threshold gets raised the first time it is inconvenient — this repository has watched that happen to
a settlement ceiling. Flow needs no number picked: *"filing is free and dispositioning isn't"* is the
mechanism, and the comparison is against **one**, which is an identity and not a target.

**Read from git, not from disk**, because the 89 stranded moves were dispositioned on disk days
earlier: a disk reading would have scored them as drained while every count taken from the record
still saw them. Whether a document has left the queue is a fact about the committed record.

**`--no-renames` is load-bearing and the first draft did not have it.** An archive move IS a rename,
so with rename detection on, git reports `R100` and `--diff-filter=AD` drops it entirely. The first
run scored the 89 moves landed minutes earlier as **6** dispositions — reporting the queue as barely
draining at the exact moment it had drained by half.

Reading today: **193 filed, 152 dispositioned, net +41 over 7 days.** Dispositioning is happening at
scale; it runs about 21% behind filing. That is a materially different story from "nothing is being
cleared", and it is the story only because the rename bug was found.

**An alarm and not a wall.** `--check` exits non-zero on sediment and the reading is carried in the
delivery seat's brief, but it is deliberately NOT in `is_material` and nothing in the commit path
gates on it. A queue that is growing is the normal state of a machine that files as it works; a
control that blocked landings on it would stop the very work that drains it, which is the cure-
becomes-the-next-cause shape this seat was shown on 2026-08-20 and again on 2026-09-02.

## 8. What the root looks like now, and what is left in it

**168 tracked → 36 documents**, and every one of them is work:

| kind | count |
|---|---|
| directive | 1 — the bill-validation brief, items 4 and 5 outstanding |
| finding | 25 — 24 LATENT, 1 BLOCKING |
| repeating alarm | 10 |

The work queue is **43 items**: those 35 drawable documents plus the 7 standing registers and the
HEAD-red register, which are spliced in by state and never drain by being consumed.

**What is still in it that arguably should not be:** the 10 repeating alarms. They are
self-clearing by contract — `alarm_repetition` mutes the pager until the underlying state changes —
so consolidating one archives an unconverged condition while its own pager stays muted. They drain
when their condition clears, and four of them have been open since 22–26 August, which is a
statement about those four conditions rather than about the folder.

## 9. One thing this broke and repaired on the way

`tools/staging_migrate_rooms._git_mv` **overwrote its destination silently**. `Path.rename` clobbers
on POSIX, so a move onto an existing document destroyed it and reported `MOVED`. It happened on this
run — the alarm collapse renamed a survivor onto a same-family document already in the root — and the
only trace was the tool's own file-count arithmetic coming out short. **A count that notices a
deletion after it has happened is a receipt, not a control.** An occupied destination is now a
refusal that names both paths; a byte-identical one is deduped, so a half-finished migration stays
re-runnable.

## 10. Tests

`tests/background/test_only_work_is_in_the_work_channel.py`, 21 legs, each naming the mutation that
must fire. The two that matter most are the null controls: a repeating alarm still classifies as an
alarm and not a finding (the finding token is in its name), and an unreadable severity leaves the
finding IN the queue.

Two pre-existing legs in `test_staging_rooms.py` asserted `len(violations) == 2` and went red when
`records/` became the third floored room — they failed because the control got **wider**, which is
the pinned-to-today's-answer shape that file's own subject exists to catch. Re-keyed to
`len(POPULATION_FLOORS)`.
