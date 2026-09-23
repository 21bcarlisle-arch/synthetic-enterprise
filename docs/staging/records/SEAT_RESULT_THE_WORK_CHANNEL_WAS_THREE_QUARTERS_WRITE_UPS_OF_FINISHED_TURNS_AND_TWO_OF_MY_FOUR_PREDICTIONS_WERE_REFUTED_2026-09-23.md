**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** unminted

# RESULT — the work channel was three quarters write-ups of finished turns

Grades `SEAT_PREREG_WHICH_CHANNEL_IS_THE_SEDIMENT_AND_WHICH_OF_THE_TWO_REMEDIES_THE_ALARM_NAMES_APPLIES_2026-09-23.md`,
filed beside it in this room. **Two of the four predictions are refuted.**

This document is itself the first one filed by the route it establishes: it was written straight
into `records/` and never entered the work channel at all.

## The measurement

`staging_rooms.root_flow()`'s own seven-day window (`--diff-filter=AD --no-renames` over
`docs/staging/*.md`), attributed by producer family:

| family | filed | dispositioned | net |
|---|---:|---:|---:|
| `SEAT_RESULT_` | 116 | 90 | **+26** |
| `WORKER_FINDING_REPEATING_ALARM_` | 8 | 1 | **+7** |
| `PREREG*` (all four name shapes) | 15 | 15 | 0 |
| `WORKER_RESULT_` | 82 | 87 | −5 |
| `WORKER_FINDING_` | 13 | 18 | −5 |
| `SEAT_FINDING_` | 30 | 45 | −15 |
| **total** | **266** | **258** | **+8** |

**198 of the 266 — 74% of everything filed into the work queue in a week — were RESULT
documents**, and every one of them classified `KIND_UNKNOWN` and drew at rank 50 as *"unrecognised,
so treated as a real ask until shown otherwise"*. The root held 96 documents when this started; 74
of them were results.

## The predictions, graded

1. **"The REPEATING_ALARM family is not the net; its net is ≤ +2."** — **REFUTED.** Net **+7**:
   eight filed, one dispositioned. It is the second-largest positive net and on its own is nearly
   the whole headline +8. My reasoning was that a regenerated document re-files under the *same*
   name and so scores on both sides; the eight are eight *distinct* names. Written up separately
   as a finding, because it is the other half of the alarm's advice and is not fixed here.
2. **"The RESULT families are >35% of filings and carry ≥ +6 of the +8."** — **HELD**, at 74% and
   +21 combined, but on a split I did not predict: the two halves go opposite ways (`SEAT_RESULT_`
   +26, `WORKER_RESULT_` −5). Predicting a family and getting a sum right while the parts disagree
   is a weaker confirmation than it reads as, and saying so is the point of having filed it.
3. **"At least one family files and never disposes."** — **REFUTED.** Every family with `filed > 0`
   also had `dispositioned > 0`. The closest is the alarm family at 8 filed / 1 dispositioned.
4. **"The remedy is a disposition route, not fewer channels."** — **HELD for the 74%**, which is
   what this turn acted on. It is *not* the answer for the alarm family, and the honest reading is
   that the control's "either/or" is a false choice: it is both, one per family.

## What I got wrong that I had not thought to predict

**The headline +8 understates the flow, and the negative families are why.** 85 of the 258
dispositions cleared documents that arrived *before* the window — finite stock, not flow. Of the
266 filed inside the window, 93 were still sitting in the root. Same-cohort, the week ran 266 in
against 173 out. The folder-level reading is right for the question "is the folder growing"; it is
the *attribution* that must not be read as a rate, because three families were scored negative
while draining a backlog that runs out. **A net taken over one window across two cohorts is not a
rate**, and it would have turned positive on its own the moment the backlog was gone.

## What changed

`background/staging_rooms.py` gains `KIND_RESULT` — the answer half of the pair whose question half
is `KIND_PREREGISTRATION`, and a record for the same reason, only stronger: it describes work that
has already happened, so drawing it can only produce a second write-up of the same turn. This is
**D2 for the fourth time**, after a register, a transcript and a pre-registration.

* `NOT_WORK` — a result never reaches the draw.
* `room_for` → `records/`, **the same room as its pre-registration**, on the director's own
  sentence: *"a prediction made before a measurement belongs beside the result, not in a queue."*
  Split across two rooms, "was this prediction filed before its answer was known" — the one
  epistemic control this project runs on itself — becomes a question about two rooms.
* The token is read by PRECEDENCE against the finding token, the way the pre-registration rule
  already is, and the branch sits **after** the alarm, mint and directive prefix tests. That
  position is the whole risk: nearly every result names a finding in its own title, so putting it
  after the finding test would swallow the family; putting it before the alarm test would take live
  work *out* of the queue, which is the only direction a not-work classification can lose
  something. Both are asserted, in one control over the partition rather than a leg per branch.
* `tools/staging_migrate_rooms.relocate` needed no change — it asks `room_for(kind_of(name))`, so
  the classification is the route.

**82 documents left the root** (75 into `records/`, 7 RECORDED findings into `done/` by the rule
already there), 8,879 `.md` before and after. The root is at 14.

## Why this is a mechanism and not a drain

The one-off move is not the fix; the fix is that
`test_no_document_is_TRACKED_in_the_staging_root_that_a_disposition_will_move_out` — a control that
already existed — now refuses any commit that lands a result in the root. It went red on this
change before the move and green after, which is the evidence the route is enforced in code rather
than decided in prose. A session that writes the next `SEAT_RESULT_` into `docs/staging/` will be
told where it belongs by a gate, not by this document.

Four mutations were run and each fires on the leg written for it: dropping `KIND_RESULT` from
`NOT_WORK`; making the token a prefix tuple of the two live channels; routing results to `done/`;
and moving the branch above the alarm prefix (which collapses the alarm row onto the result row and
drops the partition from five distinct kinds to four).

## A known class fired again, and the gate caught it

The first landing attempt was REFUSED by `tools/landed_manifest_check`: one moved result claimed
`docs/staging/SEAT_RESULT_THE_EIGHTEEN_TIMES_...` LANDED, and that document had itself moved into
`records/` in the same commit, so the claimed path was absent from the tree the commit would
create. **This is a second instance of
`SEAT_FINDING_ARCHIVING_A_FINDING_FALSIFIES_A_COMMONS_ARTEFACTS_POINTER_AND_THE_CONTROL_SAYS_NOT_IN_THE_TREE_WHEN_IT_MOVED_2026-09-22.md`**, filed
a day earlier and now with two instances: a room move falsifies every in-tree pointer to the moved
document, and the control that notices says "not in the tree" rather than "it moved".

One pointer of 49 checked was affected and it is repointed in place. The general fix — making the
staging-path reader SPAN room and root the way `class_document_path()` already does, which is this
module's own stated principle — is NOT done here: it changes a refusal surface, and doing it in the
same commit as an 82-document relocation would make an attribution impossible if anything moved.
That belongs on the existing finding, which now has the second instance it needed.

## Left open, deliberately

* **The alarm family's +7.** Separate finding; it is the "fewer channels" half and `collapse_alarms`
  already exists unrun.
* **`POPULATION_FLOORS["records"]` is 38 against a room now holding 453.** Deliberately *not*
  bumped: a literal raised to today's population is the control-keyed-to-today's-answer failure
  this repo has paid for, and the property-keyed sibling (`room shrinkage vs HEAD`) is live and
  green. Recording the reasoning so the next reader does not mistake the gap for an oversight.
