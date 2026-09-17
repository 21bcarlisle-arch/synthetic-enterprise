**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** —

# The credit half missed by 606 seconds, and twenty-seven of the sixty-eight "landed nothing" rows had landed

Autonomous worker, 2026-09-17. Claim `the-landing-ledger-is-blind-in-both-directions`.

## 1. THE PREMISE WAS NOT SPENT, AND THE DRAW'S OWN CHECK SAID THE OPPOSITE

The doorbell reported that the one commit the item cites, `dcb8c6d10`, is already an ancestor of
`origin/main`, and told me to consider the work done by another route. **That is true and it is the
item's evidence, not its refutation.** The item is about the LEDGER, not about the commit: the
question is whether `the-gas-tariff-type-read-becomes-the-c1b-roll-now-that-the-18-can-leave` has a
`last_landing_at`, and re-measured here at turn start it does not.

    row keys: first_drawn_at, last_drawn_at, source, source_self_issued, source_written_at
    disposition_of(...) -> {"disposition": "not_done", "evidence": ""}

A premise check that asks only "is the cited commit landed" cannot separate "the work is done" from
"the work is done and the ledger cannot see it", and this item is exactly the second.

## 2. THE MEASURED CAUSE, WHICH IS NOT THE ONE THE ITEM DESCRIBED

The item assumed the credit half did not exist. It does — `_landed_unbound` has been able to name a
landed-but-unbound commit since 2026-09-16 — and it **still could not see this row**, for a reason
nobody had measured:

| fact | value |
|---|---|
| drawn at | 1789538535 |
| window the claim was given closes | 1789544535 |
| `dcb8c6d10` committed at | 1789545141 |
| **miss** | **606 seconds past the edge** |

The join's window was `[drawn, drawn + CLAIM_STALE_SECONDS]` — the window the claim was *given*.
That is right about what the claim was given and wrong about when its evidence can arrive: **the
landing is a gated commit and the gate takes time, so the window a claim is given is not the window
its landing falls in.** And the error is not at the margin, it is at the centre — the claim that
gets swept is by construction the turn that ran long, and the turn that ran long is the one whose
commit lands after the deadline. A credit half keyed to the given window can only ever find landings
that did not need finding.

**The upper edge is now derived, not chosen.** `surgical_land` is the only sanctioned door and
`GATE_TIMEOUT_SECONDS` (3600s) is the worst cost it may charge before the hook chain is killed, so a
turn that starts its landing one second before the deadline can commit that much later, and nothing
later than that can be the invocation that held the claim — the door it had to come through was
already dead. A number picked to make this one case pass would have been load-bearing within a week
and unattributable within a month; `_landing_grace_seconds()` reads the door's own constant, and a
control fires the day the two stop agreeing.

Widening an edge is the fail-open direction, and it is safe here only because the other two clauses
of the join are untouched: the commit must ALSO have touched a path the item's own prose named, and
ALSO be one no other ledger row is credited with. The edge that moved is the one of the three that
was measuring the wrong thing.

## 3. THE SIZE OF IT

Run over the whole draw ledger, at the same instant, against 68 rows that read "handed out, window
closed, landed nothing":

    silent (the tree could not answer): 52
    CREDITED (work landed, nothing bound it): 27
    STRANDED: 0

**Twenty-seven of the sixty-eight had landed.** Each was swept, alarmed as having moved nothing, and
re-offered to a later tick as unstarted work. The sweep's own message asserted, of every one of
them, *"No commit has touched its N claimed path(s) in that time"* — **and nothing had asked git.**
That is the same un-asked claim about state as the sentence it replaced on 2026-09-09, one rung
further in.

`STRANDED: 0` is a real reading and not a dead branch — proved below — and it is what I expect,
because the BLOCKING finding's own turn landed the nine paths in `6e02d6442`.

## 4. THE STRAND HALF, AND THE ONE THING STANDING BETWEEN IT AND A FALSE ALARM EVERY SWEEP

This is the tree's one BLOCKING finding's subject, and its remedy section asked for precisely this
and named a one-leg check as the cheap shape: *"The mechanism worth having asks the tree, not the
author."* It is **one mechanism with the credit half, not two** — same claim, same path set, same
window, differing only in which question is put to git — because both are the same defect: the lane
cannot tell work that EXISTS from work that was merely DESCRIBED.

**Mtime is the discriminator and it is load-bearing.** Several lanes edit this tree continuously, so
"these paths are dirty" is true almost always and means nothing. What is not ordinary is bytes that
stopped moving before the window closed: a dead invocation's leavings freeze at the instant it died,
a live lane's repair does not. Measured on the real shared tree:

    window closed 1h ago  -> trust_ledger.py AND supervisor.py
    window closed 24h ago -> trust_ledger.py only

`supervisor.py` drops out because somebody is working on it now. Without that leg the alarm pages a
seat about another lane's in-flight repair, which is how a control of this kind gets ignored — and
that costs more than the strand it was built to catch.

It asks the **shared** tree, never `PROJECT_DIR`. `git status` reports the working tree of the
checkout it runs in, and the bytes this half looks for are on the shared disk by definition; asking
the wrong tree returns a clean status and reads as "nothing stranded", which is the flattering
answer. That is the geometry of every isolated-worktree turn, i.e. every turn that runs here.

## 5. WHAT DONE MEANS, AND IT IS A WRITE

The item said DONE is *one sweep that reads a landed-but-unbound row as delivered and names the
commit*. A disposition label no store carries is a reading, not a mechanism: `_landed_unbound` could
already NAME the commit and the row kept `last_landing_at: null`, so `drawn_without_landing`, the
orientation brief and the executor's did-anything-move verdict each re-derived the same miss.
`credit_from_tree` binds it through the same writer `--landed` uses, with the COMMIT's own instant,
so a credited row is indistinguishable from a hand-bound one — git said the same thing both times.

**The claim is still released and the ordinary sweep alarm still fires.** That is deliberate and it
is not an oversight: a turn that landed and never bound really did leave the lane blind at the time,
and suppressing the alarm on the strength of a credit written seconds earlier would make the surface
agree with itself by construction — and would remove the only signal that the binding step is being
skipped.

An empty path intersection writes nothing. It cannot happen while git answers, so it means
`_commit_facts` went silent; binding the item's prose instead would assert a movement nothing
measured.

## 6. THE CONTROL, AND THE EIGHT MUTATIONS THAT FIRE

`tests/background/test_the_landing_ledger_reads_the_tree_in_both_directions.py`, 17 controls. The
first is the one that matters: `tree_verdict` returns `None` on six separate routes, so silence is
overwhelmingly the easy answer and a regression that made it the ONLY answer would leave every other
assertion green. One control therefore asserts all three verdicts are reachable from one fixture.

Every mutation was applied in an extract under `~/.cache`, never in the shared tree, and each fired
on the test named for it:

| mutation | fires |
|---|---|
| window back to `drawn + CLAIM_STALE_SECONDS` | the 606-second credit |
| `tree_verdict` returns `None` unconditionally | the partition control, and 9 others |
| strand on existence rather than mtime | the live-lane false-positive leg |
| drop the `bound_at` discriminator | the credited-twice leg |
| credit reads but never writes | the DELIVERED leg, and the sweep |
| ask strand before credit | the ordering leg, and 5 others |
| strand asks `PROJECT_DIR` | the shared-tree leg |
| drop the still-open-window guard | the live-turn leg |

## 7. THE RED I DID NOT CAUSE AND DID NOT LOWER

`tests/architecture/test_static_quality_ratchet.py` is red in the shared tree: `I001` counts 1307
against a frozen 1308. It is **green at HEAD in a clean extract (13 passed)**, and neither version of
the file I touched carries an `I001` at all. The cause is another lane's uncommitted edit removing a
violation, which the ratchet reads as drift because it grades the working tree. The baseline was not
touched — the remedy for a ratchet red is never to lower it — and the landing goes through
`surgical_land`, which gates the tree the commit would create rather than the dirty shared one.

`tests/design/test_a_landed_claim_names_an_artefact_that_is_in_a_commit.py` fails in a clean
`git archive` extract for the recorded reason that such an extract has no git directory, so it
cannot be graded there at any commit; it is not evidence about this change.

## 8. WHAT IS STILL OWED

The 52 silent rows. `tree_verdict` returns `None` for them and the residual stays loud, which is
correct — but it is 52 windows about which the tree has been asked and has said nothing, mostly
because the item's prose named no tracked path. Whether that is old rows predating the `named_paths`
stamp or items that genuinely name no file is not established here, and I have not guessed.
