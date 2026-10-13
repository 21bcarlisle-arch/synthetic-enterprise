**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-fabric-settlement-switch-refuses-the-mover-arms-on-fresh-seeds` (Lane 0 delivery)

# A mover's stale eligibility verdict stopped four fresh-seed arms before the book settled

**Fate (2026-10-13, clear-the-decks):** DONE -- e71d5c1db; db1f3767f Doc's own "Fate (2026-10-13): CLOSED" confirms control built (rebind_fabric_verdict_to_new_home + two test files), both on origin.

**Fate (2026-10-13):** CLOSED -- the standing control the hand-off below asked for is built. The
relocation's verdict-copy is now `simulation.fabric_demand_path.rebind_fabric_verdict_to_new_home`,
called from the relocation block. `tests/simulation/test_fabric_demand_path_mover_verdict.py` holds
the rule in both directions against `settlement_providers_match_eligibility` and holds the guard red on
the pre-fix shape; `tests/simulation/test_run_phase2b_mover_verdict.py` holds the relocation block to
the call by AST. Each is named for the module it guards, so the pre-commit stem selector runs it on
any commit to that module (a first, single-file version reached by neither stem was refused by
`test_the_strict_census_stays_discharged`, rightly). Both run in under a second. Mutations
run before landing, each red: the call site reverted to e71d5c1db's pre-fix inline line; the moved-in
verdict flipped to not-eligible; the old verdict left in place.

**Earlier fate (2026-10-12, clear-the-decks):** PARTIAL -- e71d5c1db, db1f3767f. The fix is on origin and all
eight `on` mover arms on 61109-61112 finish exit 0; the item's third DONE condition, a control that
reproduces on 61110 and reds without the fix, does not exist and is handed off below, not claimed.

## Premise, re-measured at draw time

Three `/var/tmp/longjob-regrade-mv-*.log` runs named in the drawn item (`k1-61110`, `k1-61111`,
`k05-61112`) had already died on the run's own settlement-switch guard ("the fabric settlement switch
did not reach the book it was declared for") before this invocation started. By the time this turn
began reading, the fix was already on `origin/main` (`e71d5c1db`, landed from `/var/tmp/se-seat-executor`
in a prior invocation) and three of the four re-runs (`mv-k1-61110-r2`, `mv-k1-61111-r2`,
`mv-k1-61112-r2`) had already finished exit 0. The fourth, `mv-k05-61112-r2`, was still marked `live`
in the launch register, but its log showed `OUTCOME: SURVIVED` and its systemd unit read
`Result=success, ExecMainStatus=0` — the register entry was stale, not the run. This finding records
the cause for the one that was not yet written down, and binds the landing to this draw's claim.

## The one-variable question the item asked

*Does the mover arm move a premise onto a provider its verdict refuses, or is the verdict taken
before the move?* Neither, precisely — the arm moves the premise's **fabric trace** without moving
its **eligibility verdict**. `SYN-2016-021` (seed 61110) relocated from a legacy-profiled home into a
fabric-traced one; the relocation block in `simulation/run_phase2b.py` copied the destination's
weather, dwelling, trace and annual quantity onto the follower, but left the old home's "not
eligible" `FabricEligibility` record in place. The book then carried a fabric-traced premise with a
non-fabric verdict — exactly the mismatch `W1_11` exists to catch, and the guard is correct to stop
on it. The base seed (68793db33's one-seed grade) never happened to move a follower across that
line, so a single-seed grade could not see the fault; it only showed up once the regrade ran fresh
book seeds.

## The fix

`simulation/run_phase2b.py`'s relocation block now replaces the follower's `FabricEligibility` entry
at the same point it replaces the trace: eligible with the destination's trace if the destination has
one, not eligible with the trace removed if it does not. This mirrors the incoming-occupier path,
which already copies its premise's verdict for the same reason — eligibility is a verdict on the
premise, not on the household's history at a prior address.

## Control

**Correction (this turn, after an advisor review of the first draft of this finding):** the first
draft of this section overstated what "the guard itself is the control" gives. `W1_11` is checked
inside a multi-minute fresh-seed run, not by any commit gate, so a revert of the fix would ship
clean through every fast test — it is not a standing regression control in the sense the drawn item
asked for ("a control that reproduces on 61110 and reds without the fix"). What is true and
evidenced: `W1_11` was red on four of the eight `on` arms before the fix (k1 on 61110, 61111 and
61112, and k05 on 61112) and is green on all eight after (confirmed against the artefacts in
`/var/tmp/regrade/out/mv-{k05,k1}-{61109,61110,61111,61112}.json`, each carrying a `total_net` and
`"arm": "on"`, and the `mv-k05-61112-r2` systemd unit's `ExecMainStatus=0`). The before/after
comparison also spans more than the one hunk: the dying runs were at `ed668c733` and the re-runs at
`e71d5c1db`, with other landings (DD4b, `441994e17`, the renewal typed-record wiring) in between, so
it is not a clean one-variable before/after on this file alone — only the mutation check below
isolates that variable.

**Mutation check (this turn):** in an isolated worktree at `db1f3767f` (origin/main), the
`FabricEligibility`-carrying hunk of `e71d5c1db` was reversed with `git apply -R` and the nearest
test selection (`test_move_destination.py`, `test_move_with_us_answer.py`,
`test_move_with_us_arms.py`, `test_move_with_us_offer.py`, `test_run_phase2b.py`,
`test_run_phase2b_event_log.py`) was re-run against the reverted tree: **32 passed, exit 0.** Nothing
reds. **The control the item asked for does not exist.** The bug shipped past every fast gate once
already (the original commit's own gate selection never reached the relocation block, per its
receipt: "7 passed in 11.42s"), and reverting the fix now ships just as clean. The only thing that
currently catches this class of defect is a fresh-seed run of 5-12 minutes that no commit gate runs.

**This is a named gap, not a built control.** `simulation/run_phase2b.py` is also a contested file
right now (a concurrent landing is mid-`surgical_land` on it for unrelated work), and the relevant
logic is inline in `_main()`'s 2000+-line loop body, over variables (`fabric_series_by_customer`,
`fabric_eligibility_verdicts`, `_new_home`, `cid`) local to that function -- there is no already-
extracted unit worth calling directly. A fast standing control needs either (a) extracting the
relocation block's verdict-copy into a small testable function, or (b) a cheap scripted scenario
that drives `_main()` far enough to force one relocation across the legacy/fabric line without the
full multi-year book. Neither is a turn's worth of safe work on a file another lane is mid-landing
on. Handed off via `seat_continuation` below.

## What this does and does not change

Only runs where a follower relocates across the legacy/fabric line are affected; every run that
finished before today either already matched or stopped at the guard, so no previously-published
figure moves. The mover offer still ships `off` (`move_with_us_activation.json`); this unblocks the
four-principles fresh-seed regrade of the `on` arms, not a policy change.

## Hand-off: the missing standing control

Written as `background.seat_continuation --hand-off` (DONE_MEANS below) rather than built this turn:

**WHAT:** write a fast, standing control for the mover relocation's `FabricEligibility` carry-over in
`simulation/run_phase2b.py` (the hunk in `e71d5c1db`), either by extracting the verdict-copy at the
relocation point into a small callable the test imports directly, or by a scripted minimal scenario
that forces one legacy-to-fabric relocation without the full multi-year book.

**WHY:** the mutation check above shows no existing fast test catches a revert of `e71d5c1db`; the
only thing that caught the real bug was a multi-minute fresh-seed run, so the same class of defect
(a copied record missing one of its fields) can ship again past every commit gate. `run_phase2b.py`
was contested by a concurrent landing this turn, which is why the extraction was not attempted now.

**DONE_MEANS:** a test exists that is red against the reverted hunk (`git show e71d5c1db -- simulation/run_phase2b.py | git apply -R` in a worktree) and green with it applied, runs in commit-gate time (seconds, not minutes), and is on origin.

## Disposition

**Correction:** the first draft of this section claimed `e71d5c1db` was bound to this draw's claim.
It was not: `--landed --commit e71d5c1db` was tried and refused ("e71d5c1db is OLDER than this id was
FIRST drawn ... An older commit here is genuinely somebody else's work"), correctly, since that
commit landed from a different session before this item was ever drawn. Only this finding's own
commits bind to this claim. The fix itself is credited to whichever claim the prior invocation that
made it was working under, not to this one. The claim was released after the exit-0 criterion was
confirmed and before the control gap was found; it is not re-claimed, since the hand-off above is now
the route back to this work, not a re-draw of the same id.
