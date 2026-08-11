# WORKER FINDING — the KNIFE2 lane is ORPHANED

**Filed:** 2026-08-09, worker seat (systemd restart), on director instruction to classify
the KNIFE2 lane as ACTIVE / DORMANT-BETWEEN-TICKS / ORPHANED.
**Disposition:** FILED, NOT TOUCHED. No atom edited, no level moved, no lane restarted.

## VERDICT

**ORPHANED** — with one distinction that matters and is easy to blur:

- the **LANE** (the executing agent that built KNIFE2) is **ORPHANED**: it is gone, it
  left work stranded, and nothing is scheduled to bring it back;
- the **ATOM** `KNIFE2_customer_straddle` is **not** stranded — it sits at
  `level_current: 2` / `level_target: 2` / `loop_stage: harden`, so it remains drawable
  for HARDEN.

Reporting only the atom's health would read as DORMANT and would be wrong. The lane that
knows *why the seam looks the way it does* is what is missing.

## EVIDENCE (R9 — all observed-with-evidence unless labelled)

**1. No live KNIFE2 draw.** `ps -eo pid,etime,cmd | grep [K]NIFE2` returns only two
kinds of process: this seat's own diagnostic shells, and PID 1735587/1735611 — the
*autonomous worker tick*, whose commit message is `unwedge(publish): land KNIFE2's code`.
That is another lane cleaning up after KNIFE2, not KNIFE2 running.

**2. No branch, no worktree.** `git branch -a --list '*knife*' --list '*KNIFE*'` → empty.

**3. Its builder never recorded its own level.** `gate_authorizations.jsonl`, KNIFE2 entry,
in its own words:

> RECORDED BY THE PW2 WORKER TICK, NOT ITS BUILDER (R9 — who certified this and on what
> basis): the move was found UNRECORDED in the working tree at 2026-08-09T15:0xZ, where it
> refused every commit touching docs/design/maturity_map.yaml (level_promotion_gate exit 1)

Compare the two siblings on the same day — the contrast is the finding:

| atom | L2 recorded at | recorded by |
|---|---|---|
| AO5_hotspot_consolidation | 08:44:19 | its own lane |
| KNIFE1_reporting_cycle | 11:18:45 | its own builder (first-person evidence) |
| **KNIFE2_customer_straddle** | **16:06:53** | **the PW2 worker tick — a third party** |

**4. Its builder never committed its code.** `company/interfaces/supply_book.py` and
`tests/company/interfaces/test_supply_book_seam.py` were found UNTRACKED at ~15:0x and are
being committed at 18:41 by a *second, different* third party — 2h35m after the level was
recorded, and by neither of the two lanes that touched it before.

**5. Nothing will re-draw it as BUILD.** `level_current == level_target == 2`, so the BUILD
draw is satisfied. There is no pending tick, no `blocked_on`, no parked marker that would
return an agent to this work. A lane that will not be resumed is not "between ticks".

## WHAT THE ORPHAN LEFT UNPAID

Two open questions with no owner. Both are recorded by the adopting ticks, neither is answered:

**(a) The seam DESIGN was never reviewed by anyone.** Both the PW2 adoption note inside
`company/interfaces/supply_book.py` and the ledger provenance say the same thing in the same
words — *"the owning lane should confirm the seam DESIGN; the MEASUREMENT is verified."*
Three parties have now handled this seam and all three verified only that the edge counts
moved. No one has asked whether `registered_supply_points()` is the right shape.

**(b) The narrowing debt.** The module docstring records that the seam hands back the full
customer dicts unchanged — contract type and internal segment label included — where a real
MPAN registration publishes identity, supply start, address, profile class, metering
arrangement and EAC. Deliberately deferred to KNIFE3 / the Epoch-3 adapter programme by a
lane that is no longer present to hand that over.

## WHY THIS IS NOT COSMETIC

`KNIFE3_wall_crossing_paydown` carries `depends_on: [AO5, KNIFE1, KNIFE2]`, and AO5's own
ledger entry states the mechanism plainly: *"KNIFE3 stays blocked until both KNIFE1 and
KNIFE2 are L2."*

So KNIFE2 reaching L2 is what **unblocks the next pass** — and that L2 was recorded by a
proxy, from re-measured edge counts, over a seam design nobody has reviewed. KNIFE3 will be
drawn against a foundation whose only verification is arithmetic.

**Inferred, not observed:** this is the same shape as the three instances already logged
today (KNIFE1, KNIFE2, `14fbd32cd`) — *a lane measures the tree, certifies the atom, and
exits without committing.* KNIFE2 is the most advanced case because the residue was adopted
twice by two unrelated lanes, which makes the lane's absence look like completed work.

## RECOMMENDATION (not taken — filed per instruction)

Give the design question an owner before KNIFE3 is drawn: a HARDEN draw on
`KNIFE2_customer_straddle` scoped to *the seam design only*, not its edge counts, answering
(a) and formally handing (b) to KNIFE3. The measurement needs no redoing; it has been
verified twice.
