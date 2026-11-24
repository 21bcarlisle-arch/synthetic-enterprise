**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Item:** `verify-reg-6c-and-gas-only-win-landing-chain` (released) → `verify-reg-6c-and-gas-only-win-resume-chain` (carries it)

# The reg 6C / gas-only landing chain is carried by its resume successor; the successor's hold was already open while the chain ran

Seat executor, 23 Nov 2026 ~05:46 GMT. Read, not built.

1. **First chain ended.** `/tmp/seat_6c_v3/land.log`: reg 6C landed as `cc9f08ae3` in the locked
   worktree `/var/tmp/se-reg6c-land`; promote refused ("origin/main has moved to 779054e30"),
   exit 2. `cc9f08ae3` is not yet an ancestor of origin/main.
2. **The remainder is the successor's.** `verify-reg-6c-and-gas-only-win-resume-chain` names every
   remaining step (merge origin, promote 6C, land and promote the gas-only win from
   `/tmp/seat_gas/files`, unlock and remove the worktree). This item is released, not re-run.
3. **The resume is IN FLIGHT.** systemd unit `longjob-land-reg-6c-and-gas-only-resume-6`
   (`/tmp/seat_6c_v4/resume.sh`) started 05:37:46 and at 05:46 was inside
   `surgical_land --merge origin/main`'s pre-commit test gate.
4. **Defect found and corrected: the successor's DO NOT DRAW gate was already open.** Its marker
   `/var/tmp/se-reg6c-gas-chain-resumed-ended-20261123.txt` existed from 05:37:28 ("exit 2 ...",
   empty `resume.log`) — 18 s BEFORE unit -6 started, so left by an earlier failed attempt. The
   handoff even lists it in `present_at_hand_off`. Any draw would have run a second copy of the
   chain over the same worktree. Set aside (renamed, not deleted) to
   `...resumed-ended-20261123.txt.stale-0537-before-unit-6`; unit -6's EXIT trap writes the real
   one. To reverse: rename it back.
   Class: a chain re-launched under the same end-marker name must clear the old marker first, or
   the handoff's hold is satisfied by the corpse of the attempt it replaces.

## Done (23 Nov 2026)

The chain this record tracked has ended. The consent-then-gas chain ended `exit 0` at 10:47:48Z: Consent
re-key 017382851 (to origin via 56d118ffc), then the gas-only win a525847e9 (to origin via aed8817b2).
Reg 6C was already on origin as 09ae79aa0c. Both landing worktrees were removed. Nothing is still in flight.
