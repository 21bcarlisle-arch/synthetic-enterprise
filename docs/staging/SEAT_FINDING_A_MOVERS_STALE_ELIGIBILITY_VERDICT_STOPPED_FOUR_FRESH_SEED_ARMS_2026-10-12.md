**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-fabric-settlement-switch-refuses-the-mover-arms-on-fresh-seeds` (Lane 0 delivery)

# A mover's stale eligibility verdict stopped four fresh-seed arms before the book settled

**Fate (2026-10-12, clear-the-decks):** DONE -- e71d5c1db. Fix on origin; all eight `on` mover arms on 61109-61112 now finish exit 0.

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

No new unit test was written; the run's own `W1_11` settlement-switch guard is the control — it was
red on seed 61110/61111/61112 before the fix (three of four `on` arms refusing to settle) and is
green after (all eight `on` arms across 61109-61112 finish exit 0, confirmed against the artefacts in
`/var/tmp/regrade/out/mv-{k05,k1}-{61109,61110,61111,61112}.json`, each carrying a `total_net` and
`"arm": "on"`, and the `mv-k05-61112-r2` systemd unit's `ExecMainStatus=0`). This follows the
project's own instruction to prefer the smallest mechanism that can fail over a register that watches
it: the guard that caught the bug is the same guard that proves the fix.

## What this does and does not change

Only runs where a follower relocates across the legacy/fabric line are affected; every run that
finished before today either already matched or stopped at the guard, so no previously-published
figure moves. The mover offer still ships `off` (`move_with_us_activation.json`); this unblocks the
four-principles fresh-seed regrade of the `on` arms, not a policy change.

## Disposition

`the-fabric-settlement-switch-refuses-the-mover-arms-on-fresh-seeds` is bound to `e71d5c1db` via
`background.delivery_lane --landed --commit e71d5c1db` in this turn (the commit predates this
invocation and had not yet been bound to any claim). No code change was needed from this turn; this
file and the binding are what it lands.
