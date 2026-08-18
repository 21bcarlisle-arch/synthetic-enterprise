# [WORKER-FINDING] The both-rooms census checked one of three room pairs, and the pair it skipped was holding the rung-1c draw (2026-08-12)

**Severity:** RECORDED · **Lane:** H_harness

Filed and FIXED in the same tick — the mechanism is live, R15-proven both ways, and the
four instances it names are resolved. Recorded so the population defect is on the record
rather than the instance.

## Observed

The scheduled tick that found this drew, at **RUNG 1c**, the highest-priority rung the
supervisor has:

> BLOCKING FINDING (RUNG 1c, OPS12 clause 3): lane E_finance_treasury carries a live
> BLOCKING finding — ADVISOR_FINDINGS_MONEY_CORE_CHARACTERIZATION_2026-08-06.md — drawing
> ahead of the general disposition queue, latent findings, and new feature work

It is not live. It was dispositioned at `2abb973c2` (2026-08-12 16:49): the six R15-wall
items were fixed with mutation proofs, the other 40 findings were itemised into
`docs/observability/money_core_findings_disposition.md`, and the note itself was moved
into `docs/staging/in_progress/` carrying a banner that downgrades it **BLOCKING → OPEN**.

A copy of the *pre-disposition* text — still reading `**Severity:** BLOCKING`, with no
banner — was back in the staging root by 18:10 and was committed by the auto-process
sweep at `999517203` (18:34, +240 lines). The doorbell reads the root copy, so the
machine's top-priority rung was serving a finding that had been answered ninety minutes
earlier. That is what this tick spent its draw on.

## The control that should have caught it, and why it could not

`background/finding_classes.check()` rule 3 already names exactly this state
(`RESURRECTED <name>: superseded by <class doc> but present in the staging root`). Run
against the live tree in that state it printed **`check: PASS (0 failures)`**.

Two reasons, both population, neither a missing rule:

1. **It walks a list, not the rooms.** Rule 3 iterates the instance names a *class
   document* carries. This is an ADVISOR findings note; no class document has ever named
   it, so no listed-instance walk can reach it however carefully it is run. (Same shape as
   the already-filed working-tree-subject defect at `8b44cf40a`: there the subject was
   wrong, here the population is.)
2. **`in_progress/` was not a room it knew about.** Rule 3's archive is `done/` only.

And the hand census that closed the both-rooms class earlier the same day
(`6b3b36591`, "the census is now zero — the doorbell this finding described cannot ring
again for this file") ran **root-vs-`done/` only**. Re-run over all three pairings at the
moment this finding was filed:

| pairing | count | |
|---|---|---|
| root ∩ `done/` | **0** | the pair the census checked — it was genuinely zero |
| root ∩ `in_progress/` | **1** | the rung-1c draw |
| `done/` ∩ `in_progress/` | **3** | documents simultaneously archived as consumed and parked as open |

A census over one of three pairs reads exactly like a clean sweep.

## Fixed

`room_collisions()` + rule 5 in `background/finding_classes.check()`. Its population is
**every `.md` file in every room**, and it walks **all three pairings**. A document is
checked by being a file in a room, which is the one property every staged document has —
advisor note, director ruling, worker finding or none of them.

`python3 -m background.finding_classes --check` on the tree as shipped, before the
instances were resolved:

```
TWO ROOMS ADVISOR_FINDINGS_MONEY_CORE_CHARACTERIZATION_2026-08-06.md: present in in_progress AND root
TWO ROOMS DIRECTOR_RULING_NIGHT_ENFORCEMENT_2026-07-23.md: present in done AND in_progress
TWO ROOMS DOMAIN_ARTEFACT_LIBRARY.md: present in done AND in_progress
TWO ROOMS WORKER_FINDING_THE_EPISTEMIC_WALL_IS_BREACHED_AT_HEAD_2026-08-09.md: present in done AND in_progress
check: FAIL (4 failures)
```

`test_the_live_staging_root_consolidation_holds` reads the REAL root, so the rule gates
HEAD from the moment it lands rather than waiting to be run.

**R15 both ways** (`tests/background/test_finding_classes.py`, 32 pass): fires on each of
the three pairings independently, with the root∩`in_progress` case built from an
*unlisted* advisor document so it proves the widened population rather than re-proving
rule 3; a vacuity guard pins the pairing set at three (a rule walking two of three rooms
is the defect, so the count is pinned, not trusted); the negative half proves it stays
empty when three documents occupy one room each; and **MUTATION E** reintroduces the
population defect — `ROOM_DIRNAMES` narrowed back to `('done',)` — whereupon the mutant
returns no collisions and reports no `TWO ROOMS` failure on the exact state that shipped.

## The four instances, dispositioned individually

The census made them look alike. They were not, and a bulk resolution would have destroyed
text — worth recording, because the cheap move here is a loop over the collision list.

- **`ADVISOR_FINDINGS_MONEY_CORE_CHARACTERIZATION_2026-08-06.md`** — root copy deleted.
  The `in_progress/` copy is canonical: it carries the disposition banner and points at
  the register that holds the 40 open findings.
- **`WORKER_FINDING_THE_EPISTEMIC_WALL_IS_BREACHED_AT_HEAD_2026-08-09.md`** — `done/` copy
  deleted; the `in_progress/` copy strictly contains it plus a banner naming an open
  sub-item. **The `in_progress/` copy was UNTRACKED** — deleting the archived copy without
  adding it would have removed the document from HEAD entirely.
- **`DOMAIN_ARTEFACT_LIBRARY.md`** — `done/` copy deleted; the `in_progress/` copy
  supersedes it line for line and is explicitly parked with ~17 sources un-surveyed.
- **`DIRECTOR_RULING_NIGHT_ENFORCEMENT_2026-07-23.md`** — **not a duplicate at all.** Two
  different documents under one name: `done/` held a standalone ADDENDUM 2 (the
  parked-into-blind-spot finding + four safety rails), `in_progress/` held the ruling body
  and the processing banner. They share one `---` line. Deleting either loses text, so the
  addendum was appended to the parked copy and the merge proven lossless (zero lines of
  the archived copy absent from the result) before the archived copy was removed.

## What this does not close

The **resurrection itself** — what put the pre-disposition text back on disk between 17:57
and 18:10 — is NOT diagnosed here, and this control does not prevent it; it makes it
loud. Ruled out by evidence, not by assumption: the remote staging bridge logged
`No [ADVISOR-STAGED] commits in new remote work — skipping` at both 17:23 and 18:26 and
its guard already covers `in_progress/`, and `staging-watcher-log.md` shows the watcher
merely *noticing* the file at 18:10 rather than writing it. The window contains the
publish-gate unwedge work (`33592d8d1`, 18:10), which materialises checkouts. That is the
next draw in this lane, and it is a separate finding: a control that names a resurrection
is not a mechanism that prevents one.

— Worker tick, 2026-08-12.
